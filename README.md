# ⚡ ScorePulse - Live Sport Score App

A high-performance, real-time sports scoreboard and match centre built with **Python**, **Flask**, **Tailwind CSS**, and modern web technologies. Sourced from free live public sports APIs with an automatic fallback simulation engine.

---

## ✨ Features

- 🟢 **Live Scores & Real-Time Tracking**: Auto-refreshes every 15 seconds with an animated countdown timer and manual sync button.
- ⚽ **Multiple Football Leagues & Sports**:
  - Premier League (England)
  - UEFA Champions League
  - La Liga (Spain)
  - Serie A (Italy)
  - Bundesliga (Germany)
  - Ligue 1 (France)
  - MLS (USA)
  - NBA Basketball
- 🔔 **Instant Goal Chime**: Audio chime sounds automatically when a live score changes in any monitored match.
- 📊 **Interactive Match Centre**:
  - Click on any fixture to view **Match Events & Goals** timeline (goals, cards, substitutions).
  - Head-to-head **In-Game Statistics** (Possession %, Total Shots, Shots on Target, Corners, Fouls) with dynamic comparison bars.
- 🏆 **League Table & Standings**: Real-time standings showing rank, team crests, games played, wins, draws, losses, goal differences, and points.
- ⭐ **Pinned / Favorites**: Pin key matches to the top of the feed with one click (persisted across sessions in `localStorage`).
- ⚡ **Seamless Simulation / Demo Engine**: Switch between live real-world ESPN feeds and dynamic live match simulation at any time with a single toggle.

---

## 🚀 Quick Start

### 1. One-Click Launch (Windows)
Simply double-click the included:
```bash
run.bat
```
This automatically starts the server and opens `http://127.0.0.1:5000` in your default browser.

### 2. Manual Command Line Launch
```powershell
# 1. Install dependencies (if not already installed)
pip install -r requirements.txt

# 2. Run the application
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 📁 Project Architecture

```
Sport Score App/
├── app.py                     # Flask web server & REST endpoints
├── sports_service.py          # ESPN public API client + caching & response parsers
├── simulation_service.py      # Real-time ticking match simulation engine
├── requirements.txt           # Python dependencies (Flask, requests)
├── run.bat                    # Windows one-click launcher
├── templates/
│   └── index.html             # Responsive sports dashboard UI (Tailwind CSS)
├── static/
│   ├── css/
│   │   └── style.css          # Digital scoreboard and pulse animations
│   └── js/
│       └── app.js             # Client-side state, filters, auto-refresh & modal logic
└── README.md                  # Documentation
```

---

## 🌐 API Endpoints

- `GET /` — Serves the interactive web scoreboard dashboard.
- `GET /api/leagues` — Returns all supported sports leagues and metadata.
- `GET /api/scores?league=eng.1&mode=auto` — Returns current scoreboard fixtures for the specified league (`auto`, `sim`).
- `GET /api/match/<league_id>/<event_id>` — Returns match timeline events, statistics, and lineups.
- `GET /api/standings/<league_id>` — Returns current league table and points rankings.

---

## 🛠️ Built With

- **Python 3.12**
- **Flask**
- **Requests**
- **Tailwind CSS & Phosphor Icons**
