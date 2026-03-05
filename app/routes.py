from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for
from app.engine.game import GameSession
import time
import json
import os
import uuid
from flask import current_app
from app.engine.multiplayer import get_room, save_room, room_exists, get_range_top
from app import limiter

main = Blueprint('main', __name__)

@main.route('/multiplayer/setup')
def multiplayer_setup():
    return render_template('multiplayer_setup.html')

@main.route('/multiplayer/create', methods=['POST'])
@limiter.limit("10 per minute")
def multiplayer_create():
    difficulty = request.form.get('difficulty', 'easy')
    room_id = str(uuid.uuid4())[:8] # Short UUID
    
    # Initialize room in Redis (or memory fallback)
    room_data = {
        'id': room_id,
        'difficulty': difficulty,
        'range_top': get_range_top(difficulty),
        'secret_number': None,
        'players': {},
        'status': 'waiting',
        'start_time': None
    }
    save_room(room_id, room_data)
    
    return redirect(url_for('main.multiplayer_room', room_id=room_id))

@main.route('/room/<room_id>')
def multiplayer_room(room_id):
    room = get_room(room_id)
    if not room:
        return "Room not found or has expired.", 404
        
    return render_template('multiplayer_room.html', room_id=room_id, difficulty=room['difficulty'], range_top=room['range_top'])


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/start', methods=['POST'])
def start_game():
    difficulty = request.form.get('difficulty', 'easy')
    
    # Checkbox returns 'on' if checked, None if not
    unlimited_mode = request.form.get('unlimited') == 'on' 

    # Initialize Engine with new flag
    new_game = GameSession(difficulty, unlimited=unlimited_mode)
    
    # Save to Session
    session['secret_number'] = new_game.secret_number
    session['range_top'] = new_game.range_top
    session['max_lives'] = new_game.max_lives
    session['difficulty'] = difficulty
    session['unlimited'] = unlimited_mode
    session['attempts'] = 0
    session['hints_used'] = 0
    session['history'] = []
    session['start_time'] = time.time()
    session['score'] = 0
    session['streak'] = 0
    
    return redirect(url_for('main.game_board'))

@main.route('/game')
def game_board():
    """Renders the actual game page."""
    # Security check: If they haven't started a game, send them back to start
    if 'secret_number' not in session:
        return redirect(url_for('main.index'))
        
    return render_template('game.html', 
                           difficulty=session.get('difficulty'),
                           lives=session.get('max_lives'),
                           unlimited=session.get('unlimited'),
                           range_top=session.get('range_top'))

@main.route('/guess', methods=['POST'])
@limiter.limit("5 per second")
def make_guess():
    data = request.get_json()
    user_guess = data.get('guess')

    if not user_guess:
        return jsonify({"status": "error", "message": "No guess provided"})

    # --- SESSION GUARD ---
    if 'secret_number' not in session:
        return jsonify({"status": "error", "message": "No active game session found. Please refresh."})

    # 1. RECONSTRUCT STATE
    game = GameSession(session['difficulty'], unlimited=session.get('unlimited', False))
    game.secret_number = session['secret_number']
    game.attempts = session['attempts']
    game.hints_used = session['hints_used']
    game.history = session['history']
    game.range_top = session['range_top']
    game.max_lives = session['max_lives']
    
    game.streak = session.get('streak', 0) 

    # 2. RUN LOGIC
    elapsed = time.time() - session['start_time']
    result = game.make_guess(user_guess, time_elapsed=elapsed)

    # 3. SAVE STATE
    session['attempts'] = game.attempts
    session['history'] = game.history
    session['score'] = result['score']
    session['won'] = game.won
    
    session['streak'] = game.streak
    session['secret_number'] = game.secret_number 

    session.modified = True

    return jsonify(result)

@main.route('/result')
def result_page():
    score = session.get('score', 0)
    difficulty = session.get('difficulty', 'easy')
    unlimited = session.get('unlimited', False)

    return render_template('result.html', 
                           score=score, 
                           difficulty=difficulty,
                           unlimited=unlimited)

@main.route('/hint', methods=['POST'])
def buy_hint():
    # 1. Reconstruct State
    if 'secret_number' not in session:
        return jsonify({"status": "error", "message": "No active game session found. Please refresh."})

    game = GameSession(session['difficulty'])
    game.secret_number = session['secret_number']
    game.hints_used = session['hints_used']
    game.range_top = session['range_top']
    
    # 2. Get Hint
    hint_text = game.get_hint()
    
    # 3. Save State (Important: We incremented hints_used)
    session['hints_used'] = game.hints_used
    session.modified = True
    
    return jsonify({
        "status": "success", 
        "hint": hint_text,
        "hints_used": game.hints_used
    })

@main.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')