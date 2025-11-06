"""
ROI Simulator Module - Simulate betting performance over time
Implements deterministic simulation without numpy
"""
import random
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ROISimulator:
    """
    Simulate ROI (Return on Investment) for betting strategies over time.
    
    Uses a deterministic single-scenario approach to estimate bankroll growth
    based on average edge, win rate, and betting frequency.
    """
    
    def __init__(self, initial_bankroll: float, kelly_fraction: float = 0.25):
        """
        Initialize ROI Simulator.
        
        Args:
            initial_bankroll: Starting bankroll amount
            kelly_fraction: Fraction of Kelly to use (default 0.25 = quarter Kelly)
        """
        self.initial_bankroll = initial_bankroll
        self.kelly_fraction = kelly_fraction
        self.max_stake_percentage = 0.05  # Maximum 5% of bankroll per bet
        
        logger.info(f"📈 ROI Simulator initialized: Bankroll=R${initial_bankroll:.2f}, Kelly Fraction={kelly_fraction}")
    
    def simulate_period(
        self,
        avg_bets_per_week: int,
        avg_edge: float,
        win_rate: float,
        weeks: int
    ) -> dict:
        """
        Simulate betting performance over a period.
        
        Args:
            avg_bets_per_week: Average number of bets per week
            avg_edge: Average edge over bookmaker (e.g., 0.08 = 8%)
            win_rate: Win rate (e.g., 0.55 = 55%)
            weeks: Number of weeks to simulate
        
        Returns:
            dict: {
                'final_bankroll': Final bankroll amount,
                'profit': Total profit/loss,
                'roi_percent': ROI percentage
            }
        """
        logger.info(f"🎲 Starting simulation: {weeks} weeks, {avg_bets_per_week} bets/week, edge={avg_edge:.2%}, win_rate={win_rate:.2%}")
        
        bankroll = self.initial_bankroll
        total_bets = 0
        wins = 0
        losses = 0
        
        for week in range(1, weeks + 1):
            week_start_bankroll = bankroll
            
            for bet_num in range(avg_bets_per_week):
                stake_pct = min(avg_edge * self.kelly_fraction, self.max_stake_percentage)
                stake = bankroll * stake_pct
                
                won = random.random() < win_rate
                
                if won:
                    odds = 1 / (1 - avg_edge)
                    profit = stake * (odds - 1)
                    bankroll += profit
                    wins += 1
                else:
                    bankroll -= stake
                    losses += 1
                
                total_bets += 1
            
            week_profit = bankroll - week_start_bankroll
            logger.info(f"  Week {week}: Bankroll=R${bankroll:.2f} (Δ R${week_profit:+.2f})")
        
        profit = bankroll - self.initial_bankroll
        roi_percent = (profit / self.initial_bankroll) * 100
        
        result = {
            'final_bankroll': round(bankroll, 2),
            'profit': round(profit, 2),
            'roi_percent': round(roi_percent, 2),
            'total_bets': total_bets,
            'wins': wins,
            'losses': losses,
            'actual_win_rate': round(wins / total_bets, 4) if total_bets > 0 else 0
        }
        
        logger.info(f"✅ Simulation complete: Final=R${result['final_bankroll']:.2f}, Profit=R${result['profit']:+.2f}, ROI={result['roi_percent']:+.2f}%")
        logger.info(f"   Stats: {wins}W-{losses}L ({result['actual_win_rate']:.2%} win rate)")
        
        return result
    
    def simulate_multiple_periods(
        self,
        avg_bets_per_week: int,
        avg_edge: float,
        win_rate: float
    ) -> dict:
        """
        Simulate betting performance over multiple time periods (4, 8, 12 weeks).
        
        Args:
            avg_bets_per_week: Average number of bets per week
            avg_edge: Average edge over bookmaker (e.g., 0.08 = 8%)
            win_rate: Win rate (e.g., 0.55 = 55%)
        
        Returns:
            dict: Results for each time period
        """
        logger.info(f"📊 Running multi-period simulation: {avg_bets_per_week} bets/week, edge={avg_edge:.2%}, win_rate={win_rate:.2%}")
        
        periods = [4, 8, 12]
        results = {}
        
        for weeks in periods:
            logger.info(f"\n--- Simulating {weeks} weeks ---")
            result = self.simulate_period(avg_bets_per_week, avg_edge, win_rate, weeks)
            results[f'{weeks}_weeks'] = result
        
        logger.info(f"\n✅ Multi-period simulation complete")
        
        return results
    
    def reset_bankroll(self):
        """Reset bankroll to initial value for new simulation."""
        logger.info(f"🔄 Bankroll reset to R${self.initial_bankroll:.2f}")
