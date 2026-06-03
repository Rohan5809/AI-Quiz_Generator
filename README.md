# ⚡ AI Multiplayer Quiz Generator

A real-time, full-stack multiplayer quiz application powered by **Google Gemini AI**. Generate custom quizzes on any topic instantly, host them in real-time, and compete with friends using a live WebSocket-based leaderboard.

## 🚀 Live Demo
* **Host Dashboard (Create Quiz):** [https://rohan5809.github.io/AI-Quiz_Generator/]
* **Contestant Page (Join Game):** [https://rohan5809.github.io/AI-Quiz_Generator/contestant.html]

---

## ✨ Features

* **🧠 AI-Powered Generation:** Enter any topic (e.g., "World War 2", "Python Basics") and Google Gemini AI instantly generates a highly relevant MCQ quiz.
* **⚡ Real-Time Multiplayer:** Built with WebSockets for a seamless real-time experience. 
* **🏆 Live Leaderboard:** The host screen updates scores instantly as players submit their answers.
* **⏱️ Gamified UI:** Features a sticky, smoothly animating progress bar timer, modern Tailwind CSS glass-morphism effects, and custom interactive components.
* **📱 Fully Responsive:** Works perfectly on both desktop browsers and mobile devices.

---

## 🛠️ Tech Stack

**Frontend:**
* HTML5, Vanilla JavaScript
* Tailwind CSS (via CDN) for modern, minimal styling
* Google Fonts (Inter)

**Backend:**
* Python, FastAPI
* WebSockets (for real-time communication)
* Google Gemini API (for AI content generation)

**Database & Deployment:**
* MongoDB (for storing quiz data and PINs)
* Render (Backend Hosting)
* GitHub Pages (Frontend Hosting)

---

## 🎮 How It Works

1. **Host Creates a Room:** The host visits the dashboard, enters a topic and timer duration, and clicks "Generate".
2. **AI Generates Content:** The backend calls the Gemini API, processes the JSON response, stores it in MongoDB, and generates a unique 4-digit PIN.
3. **Players Join:** Players visit the Contestant page, enter their Name and the 4-digit PIN.
4. **Gameplay:** Players answer the quiz against a depleting, animated timer.
5. **Real-time Scoring:** Upon submission (or when the timer runs out), scores are calculated and sent via WebSockets to update the Host's live leaderboard instantly.

---
