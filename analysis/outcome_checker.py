
from typing import Dict

class OutcomeChecker:
    @staticmethod
    def check_bet_outcome(bet: Dict, match_details: Dict) -> bool:
        market = bet.get("market", "").upper()
        selection = str(bet.get("selection", "")).replace(" ", "").upper()
        score = match_details.get("score", {}).get("fullTime", {})
        home_score = score.get("home", 0)
        away_score = score.get("away", 0)
        total_goals = home_score + away_score

        if market == "1X2":
            if selection == "1" and home_score > away_score: return True
            if selection == "X" and home_score == away_score: return True
            if selection == "2" and away_score > home_score: return True
            return False
        if market == "OVER/UNDER":
            try:
                value = float(selection.replace("OVER", "").replace("UNDER", ""))
                if "OVER" in selection and total_goals > value: return True
                if "UNDER" in selection and total_goals < value: return True
                return False
            except ValueError:
                return False
        if market == "BTTS":
            if selection == "YES" and home_score > 0 and away_score > 0: return True
            if selection == "NO" and (home_score == 0 or away_score == 0): return True
            return False
        return False
