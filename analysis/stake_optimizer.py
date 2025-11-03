
from typing import List, Dict

class StakeOptimizer:
    @staticmethod
    def calculate_kelly_stakes(value_bets: List[Dict], total_investment: float, fractional_kelly: float = 0.5) -> List[Dict]:
        kelly_fractions = []
        for bet in value_bets:
            prob = bet.get("probability", 0)
            odd = bet.get("suggested_odd", 0)
            if odd > 1 and prob > 0:
                fraction = ((odd * prob) - 1) / (odd - 1)
                if fraction > 0:
                    kelly_fractions.append({"bet": bet, "fraction": fraction})

        total_fraction = sum(item["fraction"] for item in kelly_fractions)
        bets_with_stakes = []
        if total_fraction > 0:
            for item in kelly_fractions:
                normalized_fraction = item["fraction"] / total_fraction
                stake = total_investment * normalized_fraction * fractional_kelly
                item["bet"]["stake"] = round(stake, 2)
                bets_with_stakes.append(item["bet"])
        return bets_with_stakes
