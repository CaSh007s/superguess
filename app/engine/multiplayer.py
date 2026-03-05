from app import socketio
from flask_socketio import join_room, leave_room, emit, disconnect
from flask import request
import random
import time
import json
import os
import redis

# ----- REDIS CONFIGURATION -----
redis_url = os.environ.get("REDIS_URL", "")
redis_client = redis.from_url(redis_url) if redis_url else None

_memory_rooms = {}        # Fallback for local development
ROOM_TTL = 15 * 60        # 15 minutes TTL for rooms in Seconds
sid_to_room = {}          # Local Worker scope: map socket id -> room_id to handle fast disconnects

def get_room(room_id):
    if redis_client:
        data = redis_client.get(f"room:{room_id}")
        return json.loads(data) if data else None
    return _memory_rooms.get(room_id)

def save_room(room_id, room_data):
    if redis_client:
        redis_client.set(f"room:{room_id}", json.dumps(room_data), ex=ROOM_TTL)
    else:
        _memory_rooms[room_id] = room_data

def delete_room(room_id):
    if redis_client:
        redis_client.delete(f"room:{room_id}")
    else:
        _memory_rooms.pop(room_id, None)

def room_exists(room_id):
    if redis_client:
        return redis_client.exists(f"room:{room_id}") > 0
    return room_id in _memory_rooms

# -------------------------------

def get_range_top(difficulty):
    if difficulty == 'easy': return 50
    elif difficulty == 'medium': return 200
    elif difficulty == 'hard': return 1000
    elif difficulty == 'chaos': return 100
    return 50

def get_feedback_components(diff):
    if diff <= 3: return "🔥 BURNING HOT! 🔥", "bg-very-hot"
    elif diff <= 10: return "Hot", "bg-hot"
    elif diff <= 25: return "Warm", "bg-warm"
    elif diff <= 50: return "Cool", "bg-cool"
    elif diff <= 100: return "Cold", "bg-cold"
    else: return "🥶 Freezing 🥶", "bg-very-cold"

@socketio.on('join_game')
def on_join_game(data):
    room_id = data.get('room_id')
    username = data.get('username')
    avatar = data.get('avatar')
    player_id = data.get('player_id')
    
    if not room_id or not username or not player_id:
        return {'status': 'error', 'message': 'Missing room, username, or player ID'}

    room = get_room(room_id)
    if not room:
        return {'status': 'error', 'message': 'Room not found'}
        
    # Check if this player is already in the room (Reconnection)
    if player_id in room['players']:
        # They are rejoining! Just update their active socket ID
        room['players'][player_id]['sid'] = request.sid
        room['players'][player_id]['connected'] = True
    else:
        # Check if full (max 2 players)
        if len(room['players']) >= 2:
            return {'status': 'error', 'message': 'Room is full'}

        # Add new player
        room['players'][player_id] = {
            'sid': request.sid,
            'name': username,
            'avatar': avatar,
            'ready': False,
            'score': 0,
            'color': 'bg-primary',
            'connected': True
        }
    
    save_room(room_id, room)
    
    # We map their socket to both room and player_id for quick disconnect handling
    sid_to_room[request.sid] = {'room_id': room_id, 'player_id': player_id}
    join_room(room_id)
    
    # Broadcast updated player list
    emit('room_update', get_room_state(room_id), to=room_id)
    return {'status': 'success'}

@socketio.on('player_ready')
def on_player_ready(data):
    room_id = data.get('room_id')
    player_id = data.get('player_id')
    room = get_room(room_id)
    
    if room and player_id in room['players']:
        room['players'][player_id]['ready'] = True
        save_room(room_id, room)
        emit('room_update', get_room_state(room_id), to=room_id)
        
        # Check if both players are ready
        players = room['players']
        if len(players) == 2 and all(p['ready'] for p in players.values()):
            start_round(room_id)

@socketio.on('chat_message')
def on_chat_message(data):
    room_id = data.get('room_id')
    message = data.get('message')
    player_id = data.get('player_id')
    room = get_room(room_id)
    
    if room and player_id in room['players']:
        # Update TTL via re-save so chat keeps room alive
        save_room(room_id, room) 
        player_name = room['players'][player_id]['name']
        emit('chat_broadcast', {'sender_id': player_id, 'sender': player_name, 'message': message}, to=room_id)

@socketio.on('make_guess')
def on_make_guess(data):
    room_id = data.get('room_id')
    guess_str = data.get('guess')
    player_id = data.get('player_id')
    sid = request.sid
    
    room = get_room(room_id)
    if not room or player_id not in room['players'] or room['status'] != 'playing':
        return

    try:
        guess = int(guess_str)
    except ValueError:
        return

    secret = room['secret_number']
    
    if guess == secret:
        # We have a winner!
        room['status'] = 'finished'
        winner_name = room['players'][player_id]['name']
        room['players'][player_id]['score'] += 1
        
        # Reset ready states
        for p in room['players'].values():
            p['ready'] = False
            p['color'] = 'bg-primary'
            
        save_room(room_id, room)
        emit('game_over', {
            'winner': winner_name,
            'winner_id': player_id,
            'secret_number': secret,
            'state': get_room_state(room_id)
        }, to=room_id)
    else:
        # Provide proximity feedback without revealing guess
        diff = abs(secret - guess)
        text, color = get_feedback_components(diff)
        
        if diff >= 100: percent = 5
        else: percent = 100 - diff
        
        room['players'][player_id]['color'] = color
        save_room(room_id, room)
        
        # Send exact response to the guesser
        emit('guess_result', {
            'status': 'wrong',
            'message': text,
            'proximity': percent,
            'bar_color': color,
            'guess': guess
        }, to=sid)
        
        # Broadcast the color change logic to the room
        emit('opponent_proximity', {
            'player_id': player_id,
            'color': color,
            'proximity': percent
        }, to=room_id)

@socketio.on('disconnect')
def on_disconnect():
    session_data = sid_to_room.pop(request.sid, None)
    if session_data:
        room_id = session_data['room_id']
        player_id = session_data['player_id']
        room = get_room(room_id)
        
        if room and player_id in room['players']:
            # We don't delete them immediately, just mark as disconnected
            room['players'][player_id]['connected'] = False
            save_room(room_id, room)
            emit('room_update', get_room_state(room_id), to=room_id)
            
            # Note: We let the Redis TTL handle deleting abandoned rooms (15 mins)

def start_round(room_id):
    room = get_room(room_id)
    if not room: return
    room['secret_number'] = random.randint(1, room['range_top'])
    room['status'] = 'playing'
    room['start_time'] = time.time()
    save_room(room_id, room)
    
    # Notify players the game starts
    emit('round_start', {'range_top': room['range_top']}, to=room_id)

def get_room_state(room_id):
    room = get_room(room_id)
    if not room: return {}
    # Strip sensitive info (like secret_number and socket IDs)
    return {
        'id': room_id,
        'difficulty': room['difficulty'],
        'status': room['status'],
        'players': {
            pid: {
                'name': p['name'], 
                'avatar': p['avatar'], 
                'ready': p['ready'], 
                'score': p['score'], 
                'color': p['color'],
                'connected': p.get('connected', True)
            }
            for pid, p in room['players'].items()
        }
    }
