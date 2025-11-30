// --- GLOBAL VARIABLES ---
let startTime = Date.now();
let timerInterval;
let chaosTimeLeft = 30; // 30 Seconds for Chaos Mode
let isChaosMode = false;
let isMuted = false;

// --- THEME INITIALIZATION ---
(function initTheme() {
    const savedTheme = localStorage.getItem('appTheme');
    if (savedTheme === 'stealth') {
        document.body.classList.add('theme-stealth');
    }
})();

// --- INITIALIZATION ---
window.onload = function() {
    
    // 1. GAME PAGE LOGIC (Timer & Mode)
    if (document.getElementById('level-indicator')) {
        checkMode();
        
        // Clear any existing interval just to be safe, then start
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(updateTimer, 1000);
    }

    // 2. THEME BUTTON LOGIC (Runs on Landing & Game Page)
    const themeBtn = document.getElementById('theme-btn');
    if (themeBtn) {
        if (document.body.classList.contains('theme-stealth')) {
            themeBtn.innerText = "🔮 MODE: STEALTH";
        } else {
            themeBtn.innerText = "🕹️ MODE: ARCADE";
        }
    }
};

function checkMode() {
    const levelEl = document.getElementById('level-indicator');
    // Safety check: only run if element exists
    if (levelEl) {
        const levelText = levelEl.innerText;
        if (levelText.includes('CHAOS')) {
            isChaosMode = true;
        }
    }
}

// --- TIMER LOGIC (Dual Mode) ---
function updateTimer() {
    if (isChaosMode) {
        // COUNTDOWN
        chaosTimeLeft--;
        
        // Handle Time Over
        if (chaosTimeLeft <= 0) {
            chaosTimeLeft = 0;
            clearInterval(timerInterval);
            alert("TIME EXPIRED! MISSION FAILED.");
            window.location.href = "/result";
        }

        // Update Display
        document.getElementById('timer-display').innerText = `00:${pad(chaosTimeLeft)}`;
        
        // Visual Panic (Red text if < 10s)
        const timerElement = document.getElementById('timer-display');
        if (chaosTimeLeft < 10) {
            timerElement.style.color = "#ff4757"; // Red
            timerElement.style.textShadow = "0 0 10px #ff4757";
        } else {
            timerElement.style.color = "white";
            timerElement.style.textShadow = "none";
        }

    } else {
        // STANDARD COUNT UP
        const now = Date.now();
        const diff = Math.floor((now - startTime) / 1000);
        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;
        document.getElementById('timer-display').innerText = `${pad(minutes)}:${pad(seconds)}`;
    }
}

function pad(val) {
    return val > 9 ? val : "0" + val;
}

// --- MAIN GAMEPLAY FUNCTION ---
async function submitGuess() {
    const inputField = document.getElementById('user-guess');
    const guess = inputField.value;

    // 1. Basic Validation
    if (guess === "") return;

    // 2. Send Data to Python
    const response = await fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guess: guess })
    });

    const data = await response.json();

    // 3. Handle Errors
    if (data.status === "error") {
        alert(data.message);
        return;
    }

    // --- UI UPDATES ---
    
    // Update Lives (if element exists/visible)
    const livesEl = document.getElementById('lives-display');
    if (livesEl && livesEl.style.display !== 'none') {
        livesEl.innerText = data.lives_left;
    }

    // Update Proximity Bar
    const bar = document.getElementById('proximity-bar');
    bar.style.width = data.proximity + "%";
    updateBarColor(bar, data.bar_color);

    // Update Feedback Text
    const feedback = document.getElementById('feedback-text');
    feedback.innerText = data.message;
    feedback.style.color = getColorFromClass(data.bar_color);

    // Update History
    updateHistory(guess);


    // --- STATUS HANDLING ---

    if (data.status === "correct") {
        // STANDARD WIN
        triggerWinEffects();
    } 
    else if (data.status === "chaos_next") {
        // CHAOS MODE CONTINUES
        triggerWinEffects();
        playSound('win');
        
        // Bonus Time
        chaosTimeLeft += 10;
        
        // Update Streak Display
        const streakDisplay = document.getElementById('streak-display');
        if (streakDisplay) {
            streakDisplay.innerText = data.streak;
            // Pulse Animation
            streakDisplay.style.transform = "scale(1.5)";
            setTimeout(() => streakDisplay.style.transform = "scale(1)", 200);
        }

        // Reset History Visually (New Round)
        document.getElementById('history-list').innerHTML = "";
    }
    else if (data.status === "wrong") {
        // WRONG GUESS
        triggerShake();
        playSound('wrong'); 
    }
    else if (data.status === "info") {
        // GOD MODE / CHEAT
        playSound('win'); // Satisfying sound for cheats
    }

    // --- GAME OVER ---
    if (data.game_over) {
        clearInterval(timerInterval);
        setTimeout(() => {
            window.location.href = "/result";
        }, 2000);
    }

    // Reset Input
    inputField.value = "";
    inputField.focus();
}

// --- HINT SYSTEM ---
async function getHint() {
    const hintDisplay = document.getElementById('hint-display');
    hintDisplay.innerText = "Analyzing Quantum Data...";

    const response = await fetch('/hint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });

    const data = await response.json();

    if (data.status === "success") {
        hintDisplay.innerText = "💡 " + data.hint;
        hintDisplay.style.opacity = 0;
        setTimeout(() => hintDisplay.style.opacity = 1, 100);
    } else {
        hintDisplay.innerText = "Error retrieving hint.";
    }
}

// --- AUDIO SYSTEM ---
function toggleMute() {
    isMuted = !isMuted;
    const btn = document.getElementById('mute-btn');
    
    if (isMuted) {
        btn.innerText = "🔇 MUTED";
        btn.style.opacity = "0.5";
    } else {
        btn.innerText = "🔊 SOUND ON";
        btn.style.opacity = "1";
    }
}

function playSound(type) {
    if (isMuted) return;

    let audioFile = "";
    if (type === 'win') audioFile = "/static/sounds/win.mp3";
    if (type === 'wrong') audioFile = "/static/sounds/wrong.mp3";
    
    if (audioFile) {
        const audio = new Audio(audioFile);
        audio.play().catch(e => console.log("Audio play failed"));
    }
}

// --- VISUAL HELPERS ---
function triggerShake() {
    const card = document.querySelector('.game-card');
    card.classList.add('shake');
    setTimeout(() => {
        card.classList.remove('shake');
    }, 500);
}

function triggerWinEffects() {
    confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 }
    });
    playSound('win');
}

function updateHistory(num) {
    const list = document.getElementById('history-list');
    const chip = document.createElement('div');
    chip.classList.add('chip');
    chip.innerText = num;
    list.prepend(chip);
}

// Helper to map class names to hex colors for the "Glow" effect
function updateBarColor(element, colorClass) {
    let color = "#1e90ff"; // Default

    // THE NEW PALETTE
    if (colorClass === 'bg-very-hot')  color = "#ff0000"; // Pure Red
    if (colorClass === 'bg-hot')       color = "#ff4757"; // Soft Red
    if (colorClass === 'bg-warm')      color = "#ffa502"; // Orange
    if (colorClass === 'bg-cool')      color = "#eccc68"; // Gold/Yellow
    if (colorClass === 'bg-cold')      color = "#1e90ff"; // Blue
    if (colorClass === 'bg-very-cold') color = "#a29bfe"; // Icy Purple
    
    // Win State
    if (colorClass === 'bg-success')   color = "#2ed573"; // Green

    element.style.backgroundColor = color;
    element.style.boxShadow = `0 0 15px ${color}`;
}

function getColorFromClass(colorClass) {
    // We can reuse the logic, essentially
    if (colorClass === 'bg-very-hot')  return "#ff0000";
    if (colorClass === 'bg-hot')       return "#ff4757";
    if (colorClass === 'bg-warm')      return "#ffa502";
    if (colorClass === 'bg-cool')      return "#eccc68";
    if (colorClass === 'bg-cold')      return "#1e90ff";
    if (colorClass === 'bg-very-cold') return "#a29bfe";
    if (colorClass === 'bg-success')   return "#2ed573";
    return "#ffffff";
}

// --- MODAL LOGIC ---
function openRules() {
    const modal = document.getElementById('rulesModal');
    if (modal) {
        modal.style.display = 'flex';
        // Optional: Reset animation
        modal.querySelector('.modal-content').classList.remove('fade-in');
        void modal.offsetWidth; // Trigger reflow
        modal.querySelector('.modal-content').classList.add('fade-in');
    } else {
        console.error("Error: rulesModal ID not found in HTML");
    }
}

function closeRules() {
    const modal = document.getElementById('rulesModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close if clicking outside the box
window.onclick = function(event) {
    const modal = document.getElementById('rulesModal');
    if (event.target == modal) {
        closeRules();
    }
}

function toggleTheme() {
    const body = document.body;
    body.classList.toggle('theme-stealth');
    
    // Save preference
    if (body.classList.contains('theme-stealth')) {
        localStorage.setItem('appTheme', 'stealth');
        // Update button text if needed
        document.getElementById('theme-btn').innerText = "🔮 MODE: STEALTH";
    } else {
        localStorage.setItem('appTheme', 'arcade');
        document.getElementById('theme-btn').innerText = "🕹️ MODE: ARCADE";
    }
}