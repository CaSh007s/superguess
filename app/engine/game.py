import random
from app.engine.scoring import calculate_final_score
from app.engine.hints import generate_hint

class GameSession:
    # CHANGE 1: Added 'unlimited=False' to the inputs here
    def __init__(self, difficulty='easy', unlimited=False):
        self.difficulty = difficulty
        self.unlimited = unlimited 
        self.attempts = 0
        self.hints_used = 0
        self.history = []
        self.game_over = False
        self.won = False
        self.score = 0
        self.streak = 0
        
        # Configure Level Settings
        if difficulty == 'easy':
            self.range_top = 50
            self.max_lives = 10
        elif difficulty == 'medium':
            self.range_top = 200
            self.max_lives = 7
        elif difficulty == 'hard':
            self.range_top = 1000
            self.max_lives = 5
        else: 
            self.range_top = 100
            self.max_lives = 5

        self.secret_number = random.randint(1, self.range_top)

    def get_hint(self):
        """Uses a hint credit and returns the hint text."""
        self.hints_used += 1
        return generate_hint(self.secret_number, self.range_top)

    def make_guess(self, guess, time_elapsed=0):
        if self.game_over:
            return {"status": "error", "message": "Game is already over."}

        # --- GOD MODE: CHEAT CODE ---
        if str(guess) == "7777":
            guess = self.secret_number
        
        try:
            guess = int(guess)
        except ValueError:
            return {"status": "error", "message": "Invalid input. Numbers only."}

        self.attempts += 1
        self.history.append(guess)
        
        # --- CHECK WIN ---
        if guess == self.secret_number:
            
            # CHAOS MODE LOGIC: The game does NOT end.
            if self.difficulty == 'chaos':
                # 1. Increment Streak (Initialize if not exists)
                if not hasattr(self, 'streak'): self.streak = 0
                self.streak += 1
                
                # 2. Add Score Bonus
                self.score += 500 

                # 3. GENERATE NEW NUMBER (The Loop)
                self.secret_number = random.randint(1, self.range_top)
                self.history = [] # Clear history for the new round
                
                return self._build_response("chaos_next", "TARGET DESTROYED! NEXT NUMBER GENERATED.", 0)

            # STANDARD MODE LOGIC
            self.game_over = True
            self.won = True
            self.score = calculate_final_score(
                time_elapsed, self.attempts, self.hints_used, self.difficulty, unlimited=self.unlimited
            )
            return self._build_response("correct", "You got it!", 100)
        
        # --- CHECK LOSS ---
        if not self.unlimited:
            if self.attempts >= self.max_lives:
                self.game_over = True
                return self._build_response("game_over", f"Game Over! The number was {self.secret_number}", 0)

    
        # Proximity Logic
        diff = abs(self.secret_number - guess)
        if diff >= 100:
            proximity_percent = 5
        else:
            proximity_percent = 100 - diff

        feedback, color = self._get_feedback_text(diff)
        
        response = self._build_response("wrong", feedback, proximity_percent)
        response['bar_color'] = color
        return response

    def _get_feedback_text(self, diff):
        if diff <= 3:
            return "🔥 BURNING HOT! 🔥", "bg-very-hot"
        elif diff <= 10:
            return "Hot", "bg-hot"
        elif diff <= 25:
            return "Warm", "bg-warm"
        elif diff <= 50:
            return "Cool", "bg-cool"
        elif diff <= 100:
            return "Cold", "bg-cold"
        else:
            return "🥶 Freezing 🥶", "bg-very-cold"

    def _build_response(self, status, message, proximity):
        lives_display = "∞" if self.unlimited else (self.max_lives - self.attempts)
        streak_count = getattr(self, 'streak', 0)

        return {
            "status": status,
            "message": message,
            "proximity": int(proximity),
            "lives_left": lives_display, 
            "streak": streak_count,
            "history": self.history,
            "game_over": self.game_over,
            "score": self.score,
            "bar_color": "bg-primary"
        }