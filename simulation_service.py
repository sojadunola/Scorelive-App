"""
Simulation Service
Provides a realistic, interactive live match engine for demo mode
or when off-season / no live real-world matches are playing.
"""
import random
import time

DEMO_MATCHES = [
    {
        "id": "sim_1",
        "league_id": "eng.1",
        "league_name": "Premier League",
        "league_icon": "⚽",
        "state": "in",
        "is_live": True,
        "is_finished": False,
        "minute": 68,
        "period": 2,
        "home": {
            "name": "Arsenal",
            "short_name": "ARS",
            "score": 2,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
            "color": "EF0107"
        },
        "away": {
            "name": "Chelsea",
            "short_name": "CHE",
            "score": 1,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
            "color": "034694"
        },
        "venue": "Emirates Stadium, London",
        "broadcast": "Sky Sports, NBC Sports",
        "headline": "London Derby thriller under the floodlights",
        "events": [
            {"clock": "12'", "type": "goal", "text": "GOAL! Bukayo Saka curls it into the top corner! (1-0)", "team": "home"},
            {"clock": "34'", "type": "yellow", "text": "Yellow Card: Enzo Fernández for a late tackle.", "team": "away"},
            {"clock": "51'", "type": "goal", "text": "GOAL! Cole Palmer levels with a cool penalty finish! (1-1)", "team": "away"},
            {"clock": "62'", "type": "goal", "text": "GOAL! Kai Havertz heads home from Martin Ødegaard's corner! (2-1)", "team": "home"}
        ],
        "stats": {
            "possession": [54, 46],
            "shots": [13, 9],
            "shots_on_target": [6, 4],
            "corners": [7, 3],
            "fouls": [8, 11]
        }
    },
    {
        "id": "sim_2",
        "league_id": "esp.1",
        "league_name": "La Liga",
        "league_icon": "🇪🇸",
        "state": "in",
        "is_live": True,
        "is_finished": False,
        "minute": 38,
        "period": 1,
        "home": {
            "name": "Real Madrid",
            "short_name": "RMA",
            "score": 1,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/86.png",
            "color": "FFFFFF"
        },
        "away": {
            "name": "Barcelona",
            "short_name": "BAR",
            "score": 1,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/83.png",
            "color": "004D98"
        },
        "venue": "Santiago Bernabéu, Madrid",
        "broadcast": "DAZN, ESPN+",
        "headline": "El Clásico intensity at peak fever pitch",
        "events": [
            {"clock": "19'", "type": "goal", "text": "GOAL! Vinicius Jr explodes down the wing and slots it past the keeper! (1-0)", "team": "home"},
            {"clock": "31'", "type": "goal", "text": "GOAL! Lamine Yamal dazzles outside the box with a stunner! (1-1)", "team": "away"}
        ],
        "stats": {
            "possession": [49, 51],
            "shots": [7, 8],
            "shots_on_target": [3, 4],
            "corners": [4, 5],
            "fouls": [6, 7]
        }
    },
    {
        "id": "sim_3",
        "league_id": "uefa.champions",
        "league_name": "UEFA Champions League",
        "league_icon": "🏆",
        "state": "in",
        "is_live": True,
        "is_finished": False,
        "minute": 82,
        "period": 2,
        "home": {
            "name": "Manchester City",
            "short_name": "MCI",
            "score": 3,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
            "color": "6CABDD"
        },
        "away": {
            "name": "Bayern Munich",
            "short_name": "BAY",
            "score": 2,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/132.png",
            "color": "DC052D"
        },
        "venue": "Etihad Stadium, Manchester",
        "broadcast": "TNT Sports, Paramount+",
        "headline": "High-octane European clash with relentless tempo",
        "events": [
            {"clock": "8'", "type": "goal", "text": "GOAL! Erling Haaland hammers home an early opener! (1-0)", "team": "home"},
            {"clock": "22'", "type": "goal", "text": "GOAL! Harry Kane strikes a pinpoint equalizer! (1-1)", "team": "away"},
            {"clock": "44'", "type": "goal", "text": "GOAL! Kevin De Bruyne masterclass free kick! (2-1)", "team": "home"},
            {"clock": "58'", "type": "goal", "text": "GOAL! Jamal Musiala weaves through three defenders! (2-2)", "team": "away"},
            {"clock": "76'", "type": "goal", "text": "GOAL! Phil Foden rocket into the top corner! (3-2)", "team": "home"}
        ],
        "stats": {
            "possession": [58, 42],
            "shots": [16, 11],
            "shots_on_target": [8, 5],
            "corners": [9, 4],
            "fouls": [9, 12]
        }
    },
    {
        "id": "sim_4",
        "league_id": "eng.1",
        "league_name": "Premier League",
        "league_icon": "⚽",
        "state": "post",
        "is_live": False,
        "is_finished": True,
        "minute": 90,
        "period": 2,
        "home": {
            "name": "Liverpool",
            "short_name": "LIV",
            "score": 3,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png",
            "color": "C8102E"
        },
        "away": {
            "name": "Aston Villa",
            "short_name": "AVL",
            "score": 1,
            "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/362.png",
            "color": "670E36"
        },
        "venue": "Anfield, Liverpool",
        "broadcast": "Full Time",
        "headline": "Liverpool secure decisive victory at Anfield",
        "events": [
            {"clock": "20'", "type": "goal", "text": "GOAL! Mohamed Salah clinical counter-attack! (1-0)", "team": "home"},
            {"clock": "45+2'", "type": "goal", "text": "GOAL! Ollie Watkins header off set piece! (1-1)", "team": "away"},
            {"clock": "67'", "type": "goal", "text": "GOAL! Darwin Núñez powered strike! (2-1)", "team": "home"},
            {"clock": "88'", "type": "goal", "text": "GOAL! Dominik Szoboszlai long range belter! (3-1)", "team": "home"}
        ],
        "stats": {
            "possession": [62, 38],
            "shots": [18, 7],
            "shots_on_target": [9, 2],
            "corners": [8, 2],
            "fouls": [10, 13]
        }
    },
    {
        "id": "sim_5",
        "league_id": "nba",
        "league_name": "NBA Basketball",
        "league_icon": "🏀",
        "state": "in",
        "is_live": True,
        "is_finished": False,
        "minute": 10,
        "period": 4,
        "home": {
            "name": "Los Angeles Lakers",
            "short_name": "LAL",
            "score": 108,
            "logo": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
            "color": "552583"
        },
        "away": {
            "name": "Golden State Warriors",
            "short_name": "GSW",
            "score": 105,
            "logo": "https://a.espncdn.com/i/teamlogos/nba/500/gsw.png",
            "color": "1D428A"
        },
        "venue": "Crypto.com Arena, Los Angeles",
        "broadcast": "ESPN, ABC",
        "headline": "Clutch 4th quarter showdown in LA",
        "events": [
            {"clock": "4Q 2:15", "type": "basket", "text": "LeBron James driving slam dunk plus the foul!", "team": "home"},
            {"clock": "4Q 1:40", "type": "basket", "text": "Stephen Curry responds with step-back 3-pointer!", "team": "away"}
        ],
        "stats": {
            "possession": [50, 50],
            "field_goals": ["42/85 (49.4%)", "39/84 (46.4%)"],
            "three_pointers": ["12/32 (37.5%)", "17/41 (41.5%)"],
            "free_throws": ["12/15 (80.0%)", "10/12 (83.3%)"],
            "rebounds": ["46", "39"],
            "assists": ["27", "29"]
        }
    }
]

DEMO_STANDINGS = {
    "eng.1": [
        {"rank": 1, "team_name": "Arsenal", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png", "played": "10", "wins": "7", "draws": "2", "losses": "1", "goal_diff": "+14", "points": "23"},
        {"rank": 2, "team_name": "Manchester City", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png", "played": "10", "wins": "7", "draws": "2", "losses": "1", "goal_diff": "+12", "points": "23"},
        {"rank": 3, "team_name": "Liverpool", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png", "played": "10", "wins": "7", "draws": "1", "losses": "2", "goal_diff": "+11", "points": "22"},
        {"rank": 4, "team_name": "Chelsea", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png", "played": "10", "wins": "5", "draws": "3", "losses": "2", "goal_diff": "+8", "points": "18"},
        {"rank": 5, "team_name": "Aston Villa", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/362.png", "played": "10", "wins": "5", "draws": "3", "losses": "2", "goal_diff": "+5", "points": "18"},
        {"rank": 6, "team_name": "Tottenham Hotspur", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png", "played": "10", "wins": "5", "draws": "1", "losses": "4", "goal_diff": "+6", "points": "16"},
        {"rank": 7, "team_name": "Brighton", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/331.png", "played": "10", "wins": "4", "draws": "4", "losses": "2", "goal_diff": "+3", "points": "16"},
        {"rank": 8, "team_name": "Newcastle United", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/361.png", "played": "10", "wins": "4", "draws": "3", "losses": "3", "goal_diff": "+2", "points": "15"}
    ]
}

class SimulationEngine:
    def __init__(self):
        self.matches = [m.copy() for m in DEMO_MATCHES]
        self.last_update = time.time()

    def tick(self):
        """Simulate real-time progression of matches"""
        now = time.time()
        elapsed = now - self.last_update
        if elapsed < 2.0:
            return

        self.last_update = now

        for m in self.matches:
            if not m["is_live"]:
                continue

            if m["league_id"] == "nba":
                # NBA clock & point simulation
                if random.random() < 0.4:
                    scorer = "home" if random.random() < 0.52 else "away"
                    pts = random.choice([2, 3])
                    m[scorer]["score"] += pts
                    time_str = f"4Q {random.randint(1, 3)}:{random.randint(10, 59):02d}"
                    player = "LeBron James" if scorer == "home" else "Stephen Curry"
                    m["events"].insert(0, {
                        "clock": time_str,
                        "type": "basket",
                        "text": f"{pts}-pointer scored by {player}!",
                        "team": scorer
                    })
                continue

            # Football / Soccer minute progression
            m["minute"] += 1
            if m["minute"] >= 90:
                m["minute"] = 90
                m["is_live"] = False
                m["is_finished"] = True
                m["state"] = "post"
                m["status_detail"] = "FT - Final"
                continue

            m["status_detail"] = f"{m['minute']}'"

            # Chance of goal (~4% per tick)
            if random.random() < 0.04:
                scoring_team = "home" if random.random() < 0.55 else "away"
                m[scoring_team]["score"] += 1
                curr_min = f"{m['minute']}'"
                team_name = m[scoring_team]["name"]
                event_text = f"GOAL! {team_name} score! Current score: {m['home']['score']}-{m['away']['score']}"
                m["events"].insert(0, {
                    "clock": curr_min,
                    "type": "goal",
                    "text": event_text,
                    "team": scoring_team
                })
                m["stats"]["shots"][0 if scoring_team == "home" else 1] += 1
                m["stats"]["shots_on_target"][0 if scoring_team == "home" else 1] += 1

            # Chance of yellow card
            elif random.random() < 0.05:
                card_team = "home" if random.random() < 0.5 else "away"
                curr_min = f"{m['minute']}'"
                m["events"].insert(0, {
                    "clock": curr_min,
                    "type": "yellow",
                    "text": f"Yellow card shown to {m[card_team]['name']} player.",
                    "team": card_team
                })
                m["stats"]["fouls"][0 if card_team == "home" else 1] += 1

    def get_scoreboard(self, league_id=None):
        self.tick()
        filtered = self.matches
        if league_id:
            filtered = [m for m in self.matches if m["league_id"] == league_id]

        # Format matches
        res_matches = []
        for m in filtered:
            clock_display = m["status_detail"] if not m["is_live"] else f"{m['minute']}'"
            if m["league_id"] == "nba" and m["is_live"]:
                clock_display = "4Q Live"

            res_matches.append({
                "id": m["id"],
                "league_id": m["league_id"],
                "league_name": m["league_name"],
                "league_icon": m["league_icon"],
                "date": "2026-10-31T20:00:00Z",
                "state": m["state"],
                "is_live": m["is_live"],
                "is_finished": m["is_finished"],
                "clock": clock_display,
                "period": m["period"],
                "status_detail": clock_display,
                "home": {
                    "id": f"h_{m['id']}",
                    "name": m["home"]["name"],
                    "short_name": m["home"]["short_name"],
                    "logo": m["home"]["logo"],
                    "score": str(m["home"]["score"]),
                    "color": m["home"]["color"]
                },
                "away": {
                    "id": f"a_{m['id']}",
                    "name": m["away"]["name"],
                    "short_name": m["away"]["short_name"],
                    "logo": m["away"]["logo"],
                    "score": str(m["away"]["score"]),
                    "color": m["away"]["color"]
                },
                "venue": m["venue"],
                "broadcast": m["broadcast"],
                "headline": m["headline"]
            })

        return {
            "league_id": league_id or "all",
            "league_name": "All Simulated Leagues" if not league_id else filtered[0]["league_name"] if filtered else league_id,
            "league_icon": "⚡",
            "matches": res_matches,
            "count": len(res_matches),
            "live_count": sum(1 for m in res_matches if m["is_live"]),
            "source": "simulation"
        }

    def get_match_summary(self, event_id):
        self.tick()
        match = next((m for m in self.matches if m["id"] == event_id), None)
        if not match:
            return None

        # Build stats array
        raw_stats = match.get("stats", {})
        stats = []
        if "possession" in raw_stats:
            stats.append({"label": "Possession %", "home": f"{raw_stats['possession'][0]}%", "away": f"{raw_stats['possession'][1]}%"})
        if "shots" in raw_stats:
            stats.append({"label": "Total Shots", "home": str(raw_stats['shots'][0]), "away": str(raw_stats['shots'][1])})
        if "shots_on_target" in raw_stats:
            stats.append({"label": "Shots on Target", "home": str(raw_stats['shots_on_target'][0]), "away": str(raw_stats['shots_on_target'][1])})
        if "corners" in raw_stats:
            stats.append({"label": "Corners", "home": str(raw_stats['corners'][0]), "away": str(raw_stats['corners'][1])})
        if "fouls" in raw_stats:
            stats.append({"label": "Fouls", "home": str(raw_stats['fouls'][0]), "away": str(raw_stats['fouls'][1])})

        if "field_goals" in raw_stats:
            for k, label in [("field_goals", "Field Goals"), ("three_pointers", "3-Pointers"), ("free_throws", "Free Throws"), ("rebounds", "Rebounds"), ("assists", "Assists")]:
                stats.append({"label": label, "home": str(raw_stats[k][0]), "away": str(raw_stats[k][1])})

        return {
            "events": match.get("events", [])[:10],
            "stats": stats,
            "rosters": []
        }

    def get_standings(self, league_id="eng.1"):
        return DEMO_STANDINGS.get(league_id, DEMO_STANDINGS.get("eng.1", []))
