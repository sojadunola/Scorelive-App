"""
Sport Score App - Main Application Server
"""
import os
import logging
from flask import Flask, render_template, jsonify, request
from sports_service import SportsService, LEAGUES
from simulation_service import SimulationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SportScoreApp")

app = Flask(__name__)

sports_service = SportsService()
sim_engine = SimulationEngine()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/leagues")
def get_leagues():
    return jsonify({
        "success": True,
        "leagues": sports_service.get_leagues()
    })

@app.route("/api/scores")
def get_scores():
    league_id = request.args.get("league", "eng.1")
    mode = request.args.get("mode", "auto")  # 'auto', 'live', 'sim'
    date_str = request.args.get("date", None)

    if mode == "sim":
        data = sim_engine.get_scoreboard(league_id if league_id != "all" else None)
        return jsonify({"success": True, "data": data})

    # Try live ESPN API
    data = sports_service.get_scoreboard(league_id, date_str=date_str)

    # In 'auto' mode, if live ESPN has 0 matches for today, fallback to simulation for demo satisfaction
    if mode == "auto":
        if not data or not data.get("matches") or len(data["matches"]) == 0:
            sim_data = sim_engine.get_scoreboard(league_id)
            sim_data["note"] = "Showing live simulation demo (no real-world matches currently active today)."
            return jsonify({"success": True, "data": sim_data})

    if not data:
        return jsonify({
            "success": False,
            "message": "Unable to fetch live data from provider.",
            "data": sim_engine.get_scoreboard(league_id)
        }), 200

    return jsonify({"success": True, "data": data})

@app.route("/api/match/<league_id>/<event_id>")
def get_match_detail(league_id, event_id):
    if event_id.startswith("sim_"):
        summary = sim_engine.get_match_summary(event_id)
    else:
        summary = sports_service.get_match_summary(league_id, event_id)
        if not summary:
            # Fallback to empty structure
            summary = {"events": [], "stats": [], "rosters": []}

    return jsonify({"success": True, "data": summary})

@app.route("/api/standings/<league_id>")
def get_standings(league_id):
    standings = sports_service.get_standings(league_id)
    if not standings:
        standings = sim_engine.get_standings(league_id)

    return jsonify({
        "success": True,
        "league_id": league_id,
        "standings": standings
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Sport Score App running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
