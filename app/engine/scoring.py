def calculate_final_score(time_taken, attempts, hints_used, difficulty_level, unlimited=False):
    """
    Calculates the score based on efficiency and difficulty.
    """
    base_scores = {
        'easy': 1000,
        'medium': 2000,
        'hard': 5000,
        'chaos': 3000
    }
    
    # If playing unlimited, we halve the base score (Practice Mode)
    base = base_scores.get(difficulty_level, 1000)
    if unlimited:
        base = base // 2
    
    # The Penalties
    time_penalty = int(time_taken) * 2
    hint_penalty = hints_used * 150        

    # CHANGE: If unlimited lives, attempts shouldn't reduce score
    # Otherwise score would drain instantly after 20 guesses
    if unlimited:
        attempt_penalty = 0
    else:
        attempt_penalty = (attempts - 1) * 50 

    final_score = base - time_penalty - attempt_penalty - hint_penalty
    
    return max(0, final_score)