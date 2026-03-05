const socket = io();

let mySid = null;
let isPlaying = false;

// Initialize joining
document.addEventListener("DOMContentLoaded", () => {
  const inviteUrl =
    window.location.origin + "/multiplayer/setup?room=" + ROOM_ID;
  document.getElementById("inviteLink").value = inviteUrl;

  const username = localStorage.getItem("mp_username");
  const avatar = localStorage.getItem("mp_avatar");

  if (!username || !avatar) {
    // Redirect to setup if no info
    window.location.href = `/multiplayer/setup?room=${ROOM_ID}`;
    return;
  }

  socket.on("connect", () => {
    mySid = socket.id;
    socket.emit("join_game", {
      room_id: ROOM_ID,
      username: username,
      avatar: avatar,
    });
  });
});

// Socket Event Implementations

socket.on("room_update", (roomData) => {
  updatePlayersUI(roomData);

  const pCount = Object.keys(roomData.players).length;
  if (pCount === 2 && roomData.status === "waiting") {
    document.getElementById("readyBtn").style.display = "block";
    document.getElementById("waitingText").textContent =
      "Waiting for both players to mark Ready...";
  } else if (pCount < 2) {
    document.getElementById("readyBtn").style.display = "none";
    document.getElementById("waitingText").textContent =
      "Waiting for opponent...";

    // Reset Opponent View
    document.getElementById("oppPanel").style.opacity = "0.5";
    document.getElementById("oppName").textContent = "Waiting for P2...";
    document.getElementById("oppAvatar").src =
      "https://api.dicebear.com/7.x/bottts/svg?seed=waiting";
    document.getElementById("oppAvatar").className =
      `player-avatar color-bg-primary`;
    document.getElementById("oppScore").textContent = `Wins: 0`;
    document.getElementById("oppStatus").textContent = "---";
  }
});

socket.on("round_start", (data) => {
  isPlaying = true;
  document.getElementById("lobbyView").style.display = "none";
  document.getElementById("gameView").style.display = "block";
  document.getElementById("rematchBtn").style.display = "none";
  document.getElementById("guessBtn").disabled = false;
  document.getElementById("guessInput").disabled = false;
  document.getElementById("guessInput").value = "";
  document.getElementById("guessInput").focus();

  document.getElementById("rangeTop").textContent = data.range_top;

  const feedbackMsg = document.getElementById("feedback");
  feedbackMsg.innerHTML = `<h3>Match Started!</h3><p>First to crack it wins!</p>`;
  feedbackMsg.className = "feedback-box display-default";

  // Reset all bars
  let myBar = document.getElementById("myProximityBar");
  myBar.style.width = "0%";
  myBar.className = "mini-bar-fill fill-bg-primary";
  let oppBar = document.getElementById("oppProximityBar");
  oppBar.style.width = "0%";
  oppBar.className = "mini-bar-fill fill-bg-primary";

  addSystemChat("The match has begun! Good luck.");
});

socket.on("guess_result", (data) => {
  const feedbackMsg = document.getElementById("feedback");
  feedbackMsg.innerHTML = `<h3>${data.message}</h3><p>Your guess: <b>${data.guess}</b></p>`;
  feedbackMsg.className = `feedback-box ${data.bar_color}`;

  const myBar = document.getElementById("myProximityBar");
  myBar.style.width = `${data.proximity}%`;
  myBar.className = `mini-bar-fill fill-${data.bar_color}`;

  document.getElementById("guessInput").value = "";
  document.getElementById("guessInput").focus();
});

socket.on("opponent_proximity", (data) => {
  if (data.sid !== mySid) {
    // Update opponent's color aura and bar
    document.getElementById("oppAvatar").className =
      `player-avatar color-${data.color}`;
    const oppBar = document.getElementById("oppProximityBar");
    oppBar.style.width = `${data.proximity}%`;
    oppBar.className = `mini-bar-fill fill-${data.color}`;
  } else {
    document.getElementById("myAvatar").className =
      `player-avatar color-${data.color}`;
  }
});

socket.on("game_over", (data) => {
  isPlaying = false;
  updatePlayersUI(data.state);

  const isWinner = data.winner_sid === mySid;

  document.getElementById("guessBtn").disabled = true;
  document.getElementById("guessInput").disabled = true;

  const feedbackMsg = document.getElementById("feedback");
  if (isWinner) {
    feedbackMsg.innerHTML = `<h2>🏆 YOU WIN! 🏆</h2><p>You guessed <b>${data.secret_number}</b>!</p>`;
    feedbackMsg.className = "feedback-box bg-hot"; // Turn red hot winner
    addSystemChat("You won the round! 🎉");
    triggerWinEffects();
  } else {
    feedbackMsg.innerHTML = `<h2>💀 DEFEATED! 💀</h2><p>${data.winner} guessed <b>${data.secret_number}</b>!</p>`;
    feedbackMsg.className = "feedback-box bg-very-cold"; // Turn cold loser
    addSystemChat(`${data.winner} won the round!`);
  }

  if (isWinner) {
    document.getElementById("myProximityBar").style.width = "100%";
  } else {
    document.getElementById("oppProximityBar").style.width = "100%";
  }

  document.getElementById("rematchBtn").style.display = "block";
});

socket.on("chat_broadcast", (data) => {
  const chatBox = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = "chat-message";
  div.innerHTML = `<strong style="color:var(--neon-pink)">${data.sender}:</strong> ${data.message}`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
});

// Core Functions

function updatePlayersUI(state) {
  const players = state.players;

  // Find me and opp
  for (let sid in players) {
    let p = players[sid];
    if (sid === mySid) {
      document.getElementById("myName").textContent = p.name;
      document.getElementById("myAvatar").src = p.avatar;
      document.getElementById("myAvatar").className =
        `player-avatar color-${p.color}`;
      document.getElementById("myScore").textContent = `Wins: ${p.score}`;

      if (state.status === "playing")
        document.getElementById("myStatus").textContent = "GUESSING...";
      else
        document.getElementById("myStatus").textContent = p.ready
          ? "READY"
          : "WAITING";
    } else {
      document.getElementById("oppPanel").style.opacity = "1";
      document.getElementById("oppName").textContent = p.name;
      document.getElementById("oppAvatar").src = p.avatar;
      document.getElementById("oppAvatar").className =
        `player-avatar color-${p.color}`;
      document.getElementById("oppScore").textContent = `Wins: ${p.score}`;

      if (state.status === "playing")
        document.getElementById("oppStatus").textContent = "GUESSING...";
      else
        document.getElementById("oppStatus").textContent = p.ready
          ? "READY"
          : "WAITING";
    }
  }
}

function copyInvite() {
  const copyText = document.getElementById("inviteLink");
  copyText.select();
  copyText.setSelectionRange(0, 99999);
  navigator.clipboard.writeText(copyText.value);
  addSystemChat("Invite link copied to clipboard.");
}

function markReady() {
  socket.emit("player_ready", { room_id: ROOM_ID });
  document.getElementById("readyBtn").style.display = "none";
  document.getElementById("waitingText").textContent =
    "Waiting for Opponent...";
  document.getElementById("rematchBtn").style.display = "none";
}

function submitGuess() {
  if (!isPlaying) return;
  const input = document.getElementById("guessInput");
  const val = input.value;
  if (!val) return;

  socket.emit("make_guess", { room_id: ROOM_ID, guess: val });
}

function handleEnter(e) {
  if (e.key === "Enter") submitGuess();
}

function handleChatEnter(e) {
  if (e.key === "Enter") sendChat();
}

function sendChat() {
  const input = document.getElementById("chatInput");
  const val = input.value.trim();
  if (!val) return;

  socket.emit("chat_message", { room_id: ROOM_ID, message: val });
  input.value = "";
}

function sendQuickChat(code) {
  const msgs = {
    gg: "Good Game! 🎉",
    gl: "Good Luck! 🍀",
    close: "I am getting so close! 🥵",
    wow: "Wow! 🤯",
  };
  socket.emit("chat_message", { room_id: ROOM_ID, message: msgs[code] });
  document.getElementById("emojiDropup").style.display = "none";
}

function toggleEmojiDropup() {
  const dropup = document.getElementById("emojiDropup");
  if (dropup.style.display === "none" || dropup.style.display === "") {
    dropup.style.display = "flex";
  } else {
    dropup.style.display = "none";
  }
}

// Close dropup if clicked outside
document.addEventListener("click", function (event) {
  const dropup = document.getElementById("emojiDropup");
  if (!dropup) return;
  const isClickInside =
    dropup.contains(event.target) || event.target.closest(".emoji-btn");
  if (!isClickInside && dropup.style.display === "flex") {
    dropup.style.display = "none";
  }
});

function addSystemChat(msg) {
  const chatBox = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = "chat-message system";
  div.textContent = msg;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
