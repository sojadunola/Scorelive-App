"""
Sports Data Service
Fetches live scores, schedules, match details, and standings from ESPN's free public APIs,
with automatic fallback and cache support.
"""
import time
import logging
import requests

logger = logging.getLogger(__name__)

LEAGUES = {
    "eng.1": {"name": "Premier League", "sport": "soccer", "country": "England", "icon": "⚽"},
    "uefa.champions": {"name": "UEFA Champions League", "sport": "soccer", "country": "Europe", "icon": "🏆"},
    "esp.1": {"name": "La Liga", "sport": "soccer", "country": "Spain", "icon": "🇪🇸"},
    "ger.1": {"name": "Bundesliga", "sport": "soccer", "country": "Germany", "icon": "🇩🇪"},
    "ita.1": {"name": "Serie A", "sport": "soccer", "country": "Italy", "icon": "🇮🇹"},
    "fra.1": {"name": "Ligue 1", "sport": "soccer", "country": "France", "icon": "🇫🇷"},
    "usa.1": {"name": "MLS", "sport": "soccer", "country": "USA", "icon": "🇺🇸"},
    "nba": {"name": "NBA Basketball", "sport": "basketball", "country": "USA", "icon": "🏀"}
}

# Simple in-memory cache to prevent excessive requests
_cache = {}
CACHE_TTL_LIVE = 15      # 15 seconds for live scores
CACHE_TTL_STANDINGS = 300 # 5 minutes for standings

def _get_cached(key):
    entry = _cache.get(key)
    if entry:
        val, ts, ttl = entry
        if time.time() - ts < ttl:
            return val
    return None

def _set_cached(key, val, ttl):
    _cache[key] = (val, time.time(), ttl)


class SportsService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SportScoreApp/1.0"
        })

    def get_leagues(self):
        """Returns list of supported leagues"""
        return [{"id": k, **v} for k, v in LEAGUES.items()]

    def get_scoreboard(self, league_id="eng.1", date_str=None):
        """
        Fetch matches for a league.
        date_str: optional YYYYMMDD string
        """
        cache_key = f"scoreboard_{league_id}_{date_str or 'today'}"
        cached = _get_cached(cache_key)
        if cached:
            return cached

        league_meta = LEAGUES.get(league_id, {"sport": "soccer", "name": league_id})
        sport = league_meta.get("sport", "soccer")

        if sport == "basketball":
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        else:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/scoreboard"

        params = {}
        if date_str:
            params["dates"] = date_str

        try:
            resp = self.session.get(url, params=params, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                parsed = self._parse_scoreboard(data, league_id, league_meta)
                _set_cached(cache_key, parsed, CACHE_TTL_LIVE)
                return parsed
        except Exception as e:
            logger.warning(f"Error fetching scoreboard from ESPN for {league_id}: {e}")

        return None

    def _parse_scoreboard(self, data, league_id, league_meta):
        matches = []
        events = data.get("events", [])

        for event in events:
            competition = event.get("competitions", [{}])[0]
            status_obj = competition.get("status", {})
            status_type = status_obj.get("type", {})

            state = status_type.get("state", "pre")  # 'pre', 'in', 'post'
            display_clock = status_obj.get("displayClock", "")
            period = status_obj.get("period", 0)
            status_detail = status_type.get("shortDetail", status_type.get("description", "Scheduled"))

            competitors = competition.get("competitors", [])
            home_team = None
            away_team = None

            for comp in competitors:
                team_data = {
                    "id": comp.get("id"),
                    "name": comp.get("team", {}).get("displayName", "Team"),
                    "short_name": comp.get("team", {}).get("shortDisplayName", comp.get("team", {}).get("abbreviation", "")),
                    "logo": comp.get("team", {}).get("logo", ""),
                    "score": comp.get("score", "0"),
                    "color": comp.get("team", {}).get("color", "333333"),
                    "record": comp.get("records", [{}])[0].get("summary", "") if comp.get("records") else ""
                }
                if comp.get("homeAway") == "home":
                    home_team = team_data
                else:
                    away_team = team_data

            if not home_team or not away_team:
                if len(competitors) >= 2:
                    home_team = home_team or competitors[0]
                    away_team = away_team or competitors[1]
                else:
                    continue

            # Format kickoff time
            date_raw = event.get("date", "")

            # Extract venue & broadcast
            venue = competition.get("venue", {}).get("fullName", "")
            broadcasts = [b.get("names", [""])[0] for b in competition.get("broadcasts", []) if b.get("names")]

            # Headline notes or key details
            headline = competition.get("notes", [{}])[0].get("headline", "") if competition.get("notes") else ""

            matches.append({
                "id": event.get("id"),
                "league_id": league_id,
                "league_name": league_meta.get("name", league_id),
                "league_icon": league_meta.get("icon", "⚽"),
                "date": date_raw,
                "state": state,                      # 'pre', 'in', 'post'
                "is_live": state == "in",
                "is_finished": state == "post",
                "clock": display_clock,
                "period": period,
                "status_detail": status_detail,
                "home": home_team,
                "away": away_team,
                "venue": venue,
                "broadcast": ", ".join(broadcasts) if broadcasts else None,
                "headline": headline
            })

        return {
            "league_id": league_id,
            "league_name": league_meta.get("name", league_id),
            "league_icon": league_meta.get("icon", "⚽"),
            "matches": matches,
            "count": len(matches),
            "live_count": sum(1 for m in matches if m["is_live"]),
            "source": "espn"
        }

    def get_match_summary(self, league_id, event_id):
        """Fetch match details: timeline, events, stats, lineups"""
        cache_key = f"summary_{league_id}_{event_id}"
        cached = _get_cached(cache_key)
        if cached:
            return cached

        league_meta = LEAGUES.get(league_id, {"sport": "soccer"})
        sport = league_meta.get("sport", "soccer")

        if sport == "basketball":
            url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={event_id}"
        else:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_id}/summary?event={event_id}"

        try:
            resp = self.session.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                parsed = self._parse_summary(data)
                _set_cached(cache_key, parsed, CACHE_TTL_LIVE)
                return parsed
        except Exception as e:
            logger.warning(f"Error fetching match summary for {event_id}: {e}")

        return None

    def _parse_summary(self, data):
        # Extract commentary or key events
        key_events = []
        for play in data.get("keyEvents", []):
            key_events.append({
                "clock": play.get("clock", {}).get("displayValue", ""),
                "type": play.get("type", {}).get("text", ""),
                "text": play.get("text", ""),
                "team_id": play.get("team", {}).get("id")
            })

        # Extract team stats
        stats = []
        boxscore = data.get("boxscore", {})
        team_stats = boxscore.get("teams", [])
        if len(team_stats) == 2:
            team1 = team_stats[0]
            team2 = team_stats[1]
            stats1_map = {s.get("name"): s.get("displayValue") for s in team1.get("statistics", [])}
            stats2_map = {s.get("name"): s.get("displayValue") for s in team2.get("statistics", [])}

            for stat_name, label in [
                ("possessionPct", "Possession"),
                ("totalShots", "Shots"),
                ("shotsOnTarget", "Shots on Target"),
                ("corners", "Corner Kicks"),
                ("foulsCommitted", "Fouls"),
                ("yellowCards", "Yellow Cards"),
                ("redCards", "Red Cards"),
                ("offsides", "Offsides"),
                ("wonCorners", "Corners Won"),
                ("saves", "Goalkeeper Saves")
            ]:
                val1 = stats1_map.get(stat_name)
                val2 = stats2_map.get(stat_name)
                if val1 is not None or val2 is not None:
                    stats.append({
                        "label": label,
                        "home": val1 or "0",
                        "away": val2 or "0"
                    })

        # Rosters / Lineups if available
        rosters = []
        for r in boxscore.get("players", []):
            team_info = r.get("team", {})
            player_list = []
            for athlete in r.get("statistics", [{}])[0].get("athletes", [])[:11]:
                p = athlete.get("athlete", {})
                player_list.append({
                    "name": p.get("displayName", ""),
                    "jersey": p.get("jersey", ""),
                    "position": p.get("position", {}).get("abbreviation", "")
                })
            rosters.append({
                "team_name": team_info.get("displayName", ""),
                "players": player_list
            })

        return {
            "events": key_events,
            "stats": stats,
            "rosters": rosters
        }

    def get_standings(self, league_id="eng.1"):
        """Fetch league standings/table"""
        cache_key = f"standings_{league_id}"
        cached = _get_cached(cache_key)
        if cached:
            return cached

        league_meta = LEAGUES.get(league_id, {"sport": "soccer"})
        if league_meta.get("sport") == "basketball":
            url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
        else:
            url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league_id}/standings"

        try:
            resp = self.session.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                table = self._parse_standings(data)
                _set_cached(cache_key, table, CACHE_TTL_STANDINGS)
                return table
        except Exception as e:
            logger.warning(f"Error fetching standings: {e}")

        return None

    def _parse_standings(self, data):
        rows = []
        children = data.get("children", [])
        if not children:
            standings_list = data.get("standings", {}).get("entries", [])
        else:
            standings_list = children[0].get("standings", {}).get("entries", [])

        for idx, entry in enumerate(standings_list):
            team = entry.get("team", {})
            stats_dict = {s.get("name"): s.get("displayValue") for s in entry.get("stats", [])}

            rows.append({
                "rank": idx + 1,
                "team_name": team.get("displayName", ""),
                "logo": team.get("logos", [{}])[0].get("href", "") if team.get("logos") else "",
                "played": stats_dict.get("gamesPlayed", "0"),
                "wins": stats_dict.get("wins", "0"),
                "draws": stats_dict.get("ties", stats_dict.get("draws", "0")),
                "losses": stats_dict.get("losses", "0"),
                "goal_diff": stats_dict.get("pointDifferential", stats_dict.get("goalDifference", "0")),
                "points": stats_dict.get("points", stats_dict.get("winPercent", "0"))
            })
        return rows
