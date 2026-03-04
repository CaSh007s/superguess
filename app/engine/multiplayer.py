from app import socketio
from flask_socketio import join_room, leave_room, emit, disconnect
from flask import request
import random
import time

# Memory storage for active rooms
rooms = {}

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
    
    if not room_id or not username:
        return {'status': 'error', 'message': 'Missing room or username'}

    # If room doesn't exist, we can't join it unless it was created via the route.
    # The route will initialize the room structure.
    if room_id not in rooms:
        return {'status': 'error', 'message': 'Room not found'}
        
    room = rooms[room_id]
    
    # Check if full (max 2 players)
    if len(room['players']) >= 2 and request.sid not in room['players']:
        return {'status': 'error', 'message': 'Room is full'}

    # Add player
    room['players'][request.sid] = {
        'name': username,
        'avatar': avatar,
        'ready': False,
        'score': 0,
        'color': 'bg-primary'
    }
    
    join_room(room_id)
    
    # Broadcast updated player list
    emit('room_update', get_room_state(room_id), to=room_id)
    return {'status': 'success'}

@socketio.on('player_ready')
def on_player_ready(data):
    room_id = data.get('room_id')
    if room_id in rooms and request.sid in rooms[room_id]['players']:
        rooms[room_id]['players'][request.sid]['ready'] = True
        emit('room_update', get_room_state(room_id), to=room_id)
        
        # Check if both players are ready
        players = rooms[room_id]['players']
        if len(players) == 2 and all(p['ready'] for p in players.values()):
            start_round(room_id)

@socketio.on('chat_message')
def on_chat_message(data):
    room_id = data.get('room_id')
    message = data.get('message')
    if room_id in rooms and request.sid in rooms[room_id]['players']:
        player_name = rooms[room_id]['players'][request.sid]['name']
        emit('chat_broadcast', {'sender': player_name, 'message': message}, to=room_id)

@socketio.on('make_guess')
def on_make_guess(data):
    room_id = data.get('room_id')
    guess_str = data.get('guess')
    sid = request.sid
    
    if room_id not in rooms or sid not in rooms[room_id]['players']:
        return

    room = rooms[room_id]
    if room['status'] != 'playing':
        return
        
    try:
        guess = int(guess_str)
    except ValueError:
        return

    secret = room['secret_number']
    
    if guess == secret:
        # We have a winner!
        room['status'] = 'finished'
        winner_name = room['players'][sid]['name']
        room['players'][sid]['score'] += 1
        
        # Reset ready states
        for p in room['players'].values():
            p['ready'] = False
            p['color'] = 'bg-primary'
            
        emit('game_over', {
            'winner': winner_name,
            'winner_sid': sid,
            'secret_number': secret,
            'state': get_room_state(room_id)
        }, to=room_id)
    else:
        # Provide proximity feedback without revealing guess
        diff = abs(secret - guess)
        text, color = get_feedback_components(diff)
        
        # Calculate percent for the guesser
        if diff >= 100: percent = 5
        else: percent = 100 - diff
        
        room['players'][sid]['color'] = color
        
        # Send exact response to the guesser
        emit('guess_result', {
            'status': 'wrong',
            'message': text,
            'proximity': percent,
            'bar_color': color,
            'guess': guess
        }, to=sid)
        
        # Broadcast the color change logic to the room (opponent sees you heated up)
        emit('opponent_proximity', {
            'sid': sid,
            'color': color
        }, to=room_id)

@socketio.on('disconnect')
def on_disconnect():
    # Find which room this player was in and remove them
    for room_id, room in list(rooms.items()):
        if request.sid in room['players']:
            del room['players'][request.sid]
            emit('room_update', get_room_state(room_id), to=room_id)
            if len(room['players']) == 0:
                # Clean up empty rooms
                del rooms[room_id]
            break

def start_round(room_id):
    room = rooms[room_id]
    room['secret_number'] = random.randint(1, room['range_top'])
    room['status'] = 'playing'
    room['start_time'] = time.time()
    
    # Notify players the game starts
    emit('round_start', {'range_top': room['range_top']}, to=room_id)

def get_room_state(room_id):
    room = rooms[room_id]
    # Strip sensitive info
    return {
        'id': room_id,
        'difficulty': room['difficulty'],
        'status': room['status'],
        'players': {
            sid: {'name': p['name'], 'avatar': p['avatar'], 'ready': p['ready'], 'score': p['score'], 'color': p['color']}
            for sid, p in room['players'].items()
        }
    }
