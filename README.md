<div align = "center">
  
# 🔮 SuperGuess: The Ultimate Arcade Challenge

<img src="screenshots/desktop-stealth.png" alt="SuperGuess Stealth Mode" width="800">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-white?style=for-the-badge&logo=flask&logoColor=black)
![Redis](https://img.shields.io/badge/Redis-Upstash-red?style=for-the-badge&logo=redis&logoColor=white)
![Socket.IO](https://img.shields.io/badge/Socket.IO-Realtime-black?style=for-the-badge&logo=socket.io&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Deployed-purple?style=for-the-badge)

> **Can you crack the code before time runs out?**
> SuperGuess is a modern, full-stack web application that reinvents the classic "Guess the Number" game with arcade mechanics, dynamic visuals, and high-stakes gameplay.

---

## [![Play SuperGuess Online](https://img.shields.io/badge/PLAY_SUPERGUESS_ONLINE-ff007f?style=for-the-badge)](https://superguess.onrender.com)

</div>

## ✨ Key Features

### 🎮 Gameplay Mechanics

- **4 Distinct Difficulty Levels:**
  - **Rookie (1-50):** Standard gameplay.
  - **Agent (1-200):** Expanded range.
  - **Grandmaster (1-1000):** The ultimate test of logic.
  - **⚠️ CHAOS MODE:** A time-attack frenzy. 30 seconds on the clock. Every win adds +10s. How high can your streak go?
- **♾️ Unlimited Practice Mode:** Toggle "Unlimited Lives" to practice without the pressure of a Game Over.
- **🧠 Intelligent Hint System:** Spend points to analyze the target (Prime checks, Divisibility rules, Digit sums).

### 🆚 Real-Time Multiplayer (PvP)

- **Instant Matchmaking:** Create a room, grab your invite link, and battle a friend in under 10 seconds. No accounts required.
- **Live Proximity Radar:** Watch your opponent's "closeness bar" fill up with physics-based CSS animations in real-time as they narrow down the answer.
- **Stealth Comm & Emojis:** Send aggressive trash-talk or quick emoji macros directly to your opponent's console while playing.
- **Mobile Optimized:** Full CSS Grid rewriting allows seamless cross-play, placing the game engine cleanly alongside a floating chat modal on mobile devices.

### 🎨 UI & Experience

- **Dynamic Proximity Bar:** A visual "Hot/Cold" meter that fills up based on absolute distance to the target.
- **Dual Theme System:**
  - 🕹️ **Arcade Mode:** Neon, glowing text, retro-futuristic vibes (Default).
  - 🔮 **Stealth Mode:** Matte black, high-contrast green/white, minimalist interface.
- **Responsive Design:** Fully optimized for Mobile, Tablet, and Desktop.
- **Juice & Polish:** Screen shake on errors, confetti on wins, CRT flicker effects, and immersive sound effects (with Mute toggle).

---

## 🌡️ The Logic System

The game features a sophisticated feedback engine that guides players using color-coded tiers:

| Distance  | Status              | Color Indicator |
| :-------- | :------------------ | :-------------- |
| **0**     | **TARGET ACQUIRED** | 🟢 Green        |
| **< 3**   | **BURNING HOT**     | 🔴 Bright Red   |
| **< 10**  | **HOT**             | 🔴 Soft Red     |
| **< 25**  | **WARM**            | 🟠 Orange       |
| **< 50**  | **COOL**            | 🟡 Gold         |
| **< 100** | **COLD**            | 🔵 Blue         |
| **> 100** | **FREEZING**        | 🟣 Purple       |

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask), Socket.IO, Gunicorn/Gevent
- **State Management:** Upstash Redis (Handles high-velocity WebSocket events and Rate Limiting)
- **Frontend:** HTML5, CSS3 (Variables & Animations), JavaScript (Fetch API & WebSockets)
- **Architecture:**
  - **Server-Side Sessions:** Securely stores game state in signed cookies.
  - **Real-time Engine:** Uses `Flask-SocketIO` alongside Redis Pub/Sub for sub-millisecond game state broadcasting.

---

## 📸 Screenshots

|                           **Arcade Theme**                            |                          **How To Play (Stealth)**                          |
| :-------------------------------------------------------------------: | :-------------------------------------------------------------------------: |
| <img src="screenshots/hero_arcade.png" alt="Arcade Mode" width="400"> | <img src="screenshots/howtoplay-stealth.png" alt="How to Play" width="400"> |

|                              **Mobile View**                              |                           **Chaos Mode**                            |
| :-----------------------------------------------------------------------: | :-----------------------------------------------------------------: |
| <img src="screenshots/mobile_responsive.png" alt="Mobile UI" width="400"> | <img src="screenshots/chaos_mode.png" alt="Chaos Mode" width="400"> |

|                         **PvP Gameplay (Desktop)**                         |                         **PvP Battle Chat (Mobile)**                         |
| :------------------------------------------------------------------------: | :--------------------------------------------------------------------------: |
| <img src="screenshots/pvp-desktop.png" alt="PvP Mode Desktop" width="400"> | <img src="screenshots/pvpchat-mobile.png" alt="PvP Mode Mobile" width="400"> |

---

## 💻 Local Installation

Want to run this on your own machine?

1.  **Clone the repository**

    ```bash
    git clone https://github.com/CaSh007s/superguess.git
    cd superguess
    ```

2.  **Create a Virtual Environment**

    ```bash
    python -m venv venv
    # Windows: venv\Scripts\activate
    # Mac/Linux: source venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the App**
    ```bash
    python run.py
    ```
    Visit `http://127.0.0.1:5000` in your browser.

---

## 🤝 Contributing

Got an idea for **Level 5**? Pull requests are welcome!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 👨‍💻 Author

**Kalash Pratap Gaur**

<ul style="list-style-type: none; padding-left: 0; margin-left: 20px;">
  <li style="display: flex; align-items: center; margin-bottom: 5px;">
    <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #fff; margin-right: 15px;"></span>
    GitHub: <a href="https://github.com/CaSh007s">@CaSh007s</a>
  </li>
  <!-- <li style="display: flex; align-items: center;"> -->
    <!-- <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #fff; margin-right: 15px;"></span> -->
    <!-- Portfolio: <a href="https://yourportfolio.com">YourPortfolioLink</a> -->
  <!-- </li> -->
</ul>

---

<blockquote style="border-left: 4px solid var(--border-color); padding-left: 15px; margin-left: 0; font-style: italic; color: #a0a0a0;">
  Built with 💻 and ☕ by Kalash.
</blockquote>
