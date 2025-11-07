"""
Kelly Criterion Module - Optimal Stake Calculation
Implements the Kelly Criterion formula for optimal bet sizing
"""
from utils.logger import setup_logger

logger = setup_logger(__name__)


def find_value_bets(probs_dict: dict, odds_dict: dict, min_edge: float = 0.05) -> list:
    """
    Identify value bets where calculated probability exceeds implied probability.
    
    Args:
        probs_dict: Dictionary of market probabilities (e.g., {'home_win': 0.55, 'draw': 0.25})
        odds_dict: Dictionary of bookmaker odds (e.g., {'home_win': 2.0, 'draw': 3.5})
        min_edge: Minimum edge required to consider a value bet (default 0.05 = 5%)
    
    Returns:
        list: List of value bets sorted by edge (descending), each containing:
            {
                'market': Market name,
                'probability': Calculated probability,
                'odds': Bookmaker odds,
                'implied_probability': Implied probability from odds,
                'edge': Edge percentage
            }
    
    Example:
        >>> probs = {'home_win': 0.55, 'draw': 0.25, 'away_win': 0.20}
        >>> odds = {'home_win': 2.0, 'draw': 3.5, 'away_win': 6.0}
        >>> value_bets = find_value_bets(probs, odds, min_edge=0.05)
    """
    logger.info(f"🔍 Finding value bets with min edge {min_edge:.1%}")
    
    value_bets = []
    
    for market in probs_dict.keys():
        if market not in odds_dict:
            logger.warning(f"⚠️ Market '{market}' not found in odds_dict, skipping")
            continue
        
        try:
            probability = float(probs_dict[market])
            odds = float(odds_dict[market])
            
            if odds <= 1:
                logger.warning(f"⚠️ Invalid odds for {market}: {odds}")
                continue
            
            implied_probability = 1 / odds
            edge = probability - implied_probability
            
            if edge >= min_edge:
                value_bet = {
                    'market': market,
                    'probability': round(probability, 4),
                    'odds': round(odds, 2),
                    'implied_probability': round(implied_probability, 4),
                    'edge': round(edge, 4)
                }
                value_bets.append(value_bet)
                logger.info(f"💎 Value bet found: {market} - Edge: {edge:.2%}")
        
        except (ValueError, TypeError) as e:
            logger.warning(f"⚠️ Error processing market '{market}': {e}")
            continue
    
    value_bets.sort(key=lambda x: x['edge'], reverse=True)
    
    logger.info(f"✅ Found {len(value_bets)} value bets")
    
    return value_bets


class KellyCriterion:
    """
    Calculate optimal stake size using Kelly Criterion formula.
    
    The Kelly Criterion determines the optimal fraction of bankroll to bet
    based on the probability of winning and the odds offered.
    
    Formula: f* = (b * p - q) / b
    where:
        b = odds - 1 (net odds)
        p = probability of winning
        q = 1 - p (probability of losing)
        f* = optimal fraction of bankroll to bet
    """
    
    def __init__(self, bankroll: float, kelly_fraction: float = 0.25):
        """
        Initialize Kelly Criterion calculator.
        
        Args:
            bankroll: Total bankroll amount (100-100000)
            kelly_fraction: Fraction of Kelly to use (0.1-0.5, default 0.25 = quarter Kelly)
                           Conservative approach to reduce variance
        
        Raises:
            ValueError: If bankroll or kelly_fraction are out of valid range
        """
        if not (100 <= bankroll <= 100000):
            raise ValueError(f"Bankroll must be between R$100 and R$100,000. Got: R${bankroll:.2f}")
        
        if not (0.1 <= kelly_fraction <= 0.5):
            raise ValueError(f"Kelly fraction must be between 0.1 and 0.5. Got: {kelly_fraction}")
        
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.max_stake_percentage = 0.05
        
        logger.info(f"💰 Kelly Criterion initialized: Bankroll=R${bankroll:.2f}, Fraction={kelly_fraction}")
    
    def calculate_stake(self, probability: float, odds: float) -> dict:
        """
        Calculate optimal stake using Kelly Criterion.
        
        Args:
            probability: Probability of winning (0 to 1)
            odds: Decimal odds offered by bookmaker
        
        Returns:
            dict: {
                'stake': Recommended stake amount,
                'kelly_percentage': Kelly percentage (before fraction applied),
                'is_value_bet': Whether this is a value bet,
                'edge': Edge over bookmaker (%),
                'expected_value': Expected value of the bet
            }
        """
        logger.info(f"📊 Calculating Kelly stake: probability={probability:.2%}, odds={odds:.2f}")
        
        if probability <= 0 or probability >= 1:
            logger.warning(f"⚠️ Invalid probability: {probability}")
            return self._no_bet_result("Invalid probability")
        
        if odds <= 1:
            logger.warning(f"⚠️ Invalid odds: {odds}")
            return self._no_bet_result("Invalid odds")
        
        b = odds - 1  # Net odds (profit per unit staked)
        p = probability  # Probability of winning
        q = 1 - p  # Probability of losing
        
        implied_probability = 1 / odds
        
        edge = (probability - implied_probability) * 100
        
        is_value_bet = edge > 0
        
        if not is_value_bet:
            logger.info(f"❌ No value bet: edge={edge:.2f}%")
            return self._no_bet_result(f"Negative edge: {edge:.2f}%")
        
        kelly_percentage = (b * p - q) / b
        
        adjusted_kelly = kelly_percentage * self.kelly_fraction
        
        max_stake_fraction = self.max_stake_percentage
        if adjusted_kelly > max_stake_fraction:
            logger.warning(f"⚠️ Kelly stake {adjusted_kelly:.2%} exceeds max {max_stake_fraction:.2%}, capping")
            adjusted_kelly = max_stake_fraction
        
        if adjusted_kelly <= 0:
            logger.info(f"❌ Kelly suggests no bet: kelly={kelly_percentage:.2%}")
            return self._no_bet_result(f"Kelly suggests no bet")
        
        stake = round(self.bankroll * adjusted_kelly, 2)
        
        expected_value = round(stake * (odds * probability - 1), 2)
        
        result = {
            'stake': stake,
            'kelly_percentage': round(adjusted_kelly * 100, 2),
            'is_value_bet': is_value_bet,
            'edge': round(edge, 2),
            'expected_value': expected_value
        }
        
        logger.info(f"✅ Kelly stake calculated: R${stake:.2f} ({adjusted_kelly:.2%}), EV=R${expected_value:.2f}, Edge={edge:.2f}%")
        
        return result
    
    def _no_bet_result(self, reason: str) -> dict:
        """
        Return a no-bet result.
        
        Args:
            reason: Reason for not betting
        
        Returns:
            dict: Result indicating no bet should be placed
        """
        return {
            'stake': 0.0,
            'kelly_percentage': 0.0,
            'is_value_bet': False,
            'edge': 0.0,
            'expected_value': 0.0,
            'reason': reason
        }
    
    def calculate_multiple_stakes(self, bets_list: list) -> list:
        """
        Calculate stakes for multiple bets.
        
        Args:
            bets_list: List of dicts with 'probability' and 'odds' keys
        
        Returns:
            list: List of stake calculation results
        
        Example:
            >>> kelly = KellyCriterion(1000, 0.25)
            >>> bets = [
            ...     {'probability': 0.55, 'odds': 2.0},
            ...     {'probability': 0.60, 'odds': 1.8}
            ... ]
            >>> results = kelly.calculate_multiple_stakes(bets)
        """
        logger.info(f"📊 Calculating stakes for {len(bets_list)} bets")
        
        results = []
        for i, bet in enumerate(bets_list):
            try:
                probability = bet.get('probability')
                odds = bet.get('odds')
                
                if probability is None or odds is None:
                    logger.warning(f"⚠️ Bet {i+1}: Missing probability or odds")
                    results.append(self._no_bet_result("Missing probability or odds"))
                    continue
                
                result = self.calculate_stake(probability, odds)
                results.append(result)
            except Exception as e:
                logger.warning(f"⚠️ Bet {i+1}: Error calculating stake: {e}")
                results.append(self._no_bet_result(f"Error: {e}"))
        
        value_bets_count = sum(1 for r in results if r.get('is_value_bet', False))
        logger.info(f"✅ Calculated {len(results)} stakes, {value_bets_count} value bets found")
        
        return results
    
    def update_bankroll(self, new_bankroll: float):
        """
        Update bankroll amount.
        
        Args:
            new_bankroll: New bankroll amount
        """
        old_bankroll = self.bankroll
        self.bankroll = new_bankroll
        logger.info(f"💰 Bankroll updated: R${old_bankroll:.2f} → R${new_bankroll:.2f}")
