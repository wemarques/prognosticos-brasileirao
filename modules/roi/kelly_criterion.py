"""
Kelly Criterion Module - Optimal Stake Calculation
Implements the Kelly Criterion formula for optimal bet sizing
"""
from utils.logger import setup_logger

logger = setup_logger(__name__)


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
            bankroll: Total bankroll amount
            kelly_fraction: Fraction of Kelly to use (default 0.25 = quarter Kelly)
                           Conservative approach to reduce variance
        """
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.max_stake_percentage = 0.05  # Maximum 5% of bankroll per bet
        
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
    
    def update_bankroll(self, new_bankroll: float):
        """
        Update bankroll amount.
        
        Args:
            new_bankroll: New bankroll amount
        """
        old_bankroll = self.bankroll
        self.bankroll = new_bankroll
        logger.info(f"💰 Bankroll updated: R${old_bankroll:.2f} → R${new_bankroll:.2f}")
