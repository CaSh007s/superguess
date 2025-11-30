from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for
from app.engine.game import GameSession
import time
import json
import os
from flask import current_app

main = Blueprint('main', __name__)

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
def make_guess():
    data = request.get_json()
    user_guess = data.get('guess')

    if not user_guess:
        return jsonify({"status": "error", "message": "No guess provided"})

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
    
    json_path = os.path.join(current_app.root_path, 'highscores.json')
    
    try:
        with open(json_path, 'r') as f:
            highscores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        highscores = {"easy": 0, "medium": 0, "hard": 0}

    is_new_record = False
    
    # CHANGE: Only save high score if this was a Normal (Limited) game
    if not session.get('unlimited'):
        # Only save if they actually beat the score
        if score > highscores.get(difficulty, 0):
            highscores[difficulty] = score
            is_new_record = True
            with open(json_path, 'w') as f:
                json.dump(highscores, f)

    return render_template('result.html', 
                           score=score, 
                           highscore=highscores.get(difficulty, 0),
                           is_new_record=is_new_record,
                           difficulty=difficulty)

@main.route('/hint', methods=['POST'])
def buy_hint():
    # 1. Reconstruct State
    if 'secret_number' not in session:
        return jsonify({"status": "error", "message": "No active game"})

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
    json_path = os.path.join(current_app.root_path, 'highscores.json')
    
    default_scores = {"easy": 0, "medium": 0, "hard": 0, "chaos": 0}

    try:
        with open(json_path, 'r') as f:
            saved_scores = json.load(f)
            highscores = {**default_scores, **saved_scores}
    except (FileNotFoundError, json.JSONDecodeError):
        highscores = default_scores

    return render_template('leaderboard.html', scores=highscores)