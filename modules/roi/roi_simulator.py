"""
ROI Simulator Module - Simulate betting performance over time
Implements Monte Carlo simulation with numpy for statistical analysis
"""
import numpy as np
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ROISimulator:
    """
    Simulate ROI (Return on Investment) for betting strategies over time.
    
    Uses Monte Carlo simulation with 1000 iterations to estimate bankroll growth
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
        self.max_stake_percentage = 0.05
        self.num_simulations = 1000
        
        logger.info(f"📈 ROI Simulator initialized: Bankroll=R${initial_bankroll:.2f}, Kelly Fraction={kelly_fraction}, Simulations={self.num_simulations}")
    
    def simulate_period(
        self,
        avg_bets_per_week: int,
        avg_edge: float,
        win_rate: float,
        weeks: int
    ) -> dict:
        """
        Simulate betting performance over a period using Monte Carlo method.
        
        Runs 1000 simulations with variation in bets/week and edge to generate
        statistical distribution of outcomes (pessimistic, realistic, optimistic).
        
        Args:
            avg_bets_per_week: Average number of bets per week
            avg_edge: Average edge over bookmaker (e.g., 0.08 = 8%)
            win_rate: Win rate (e.g., 0.55 = 55%)
            weeks: Number of weeks to simulate
        
        Returns:
            dict: {
                'days': Number of days simulated,
                'scenarios': {
                    'pessimistic': 10th percentile result,
                    'realistic': 50th percentile (median) result,
                    'optimistic': 90th percentile result
                },
                'statistics': {
                    'mean_final_bankroll': Average final bankroll,
                    'std_final_bankroll': Standard deviation,
                    'mean_roi': Average ROI percentage
                }
            }
        """
        logger.info(f"🎲 Starting Monte Carlo simulation: {self.num_simulations} iterations, {weeks} weeks, {avg_bets_per_week} bets/week, edge={avg_edge:.2%}, win_rate={win_rate:.2%}")
        
        final_bankrolls = np.zeros(self.num_simulations)
        
        for sim in range(self.num_simulations):
            bankroll = self.initial_bankroll
            
            for week in range(weeks):
                bets_this_week = max(1, int(np.random.normal(avg_bets_per_week, avg_bets_per_week * 0.2)))
                
                for bet in range(bets_this_week):
                    edge_variation = np.random.normal(avg_edge, avg_edge * 0.3)
                    edge_variation = max(0.01, min(edge_variation, 0.25))
                    
                    stake_pct = min(edge_variation * self.kelly_fraction, self.max_stake_percentage)
                    stake = bankroll * stake_pct
                    
                    won = np.random.random() < win_rate
                    
                    if won:
                        odds = 1 / (1 - edge_variation)
                        profit = stake * (odds - 1)
                        bankroll += profit
                    else:
                        bankroll -= stake
                    
                    if bankroll <= 0:
                        bankroll = 0
                        break
                
                if bankroll <= 0:
                    break
            
            final_bankrolls[sim] = bankroll
        
        p10 = np.percentile(final_bankrolls, 10)
        p50 = np.percentile(final_bankrolls, 50)
        p90 = np.percentile(final_bankrolls, 90)
        mean_bankroll = np.mean(final_bankrolls)
        std_bankroll = np.std(final_bankrolls)
        
        days = weeks * 7
        
        result = {
            'days': days,
            'scenarios': {
                'pessimistic': {
                    'final_bankroll': round(p10, 2),
                    'profit': round(p10 - self.initial_bankroll, 2),
                    'roi_percent': round((p10 - self.initial_bankroll) / self.initial_bankroll * 100, 2)
                },
                'realistic': {
                    'final_bankroll': round(p50, 2),
                    'profit': round(p50 - self.initial_bankroll, 2),
                    'roi_percent': round((p50 - self.initial_bankroll) / self.initial_bankroll * 100, 2)
                },
                'optimistic': {
                    'final_bankroll': round(p90, 2),
                    'profit': round(p90 - self.initial_bankroll, 2),
                    'roi_percent': round((p90 - self.initial_bankroll) / self.initial_bankroll * 100, 2)
                }
            },
            'statistics': {
                'mean_final_bankroll': round(mean_bankroll, 2),
                'std_final_bankroll': round(std_bankroll, 2),
                'mean_roi': round((mean_bankroll - self.initial_bankroll) / self.initial_bankroll * 100, 2)
            }
        }
        
        logger.info(f"✅ Monte Carlo simulation complete ({self.num_simulations} iterations)")
        logger.info(f"   Pessimistic (10%): R${result['scenarios']['pessimistic']['final_bankroll']:.2f} ({result['scenarios']['pessimistic']['roi_percent']:+.2f}%)")
        logger.info(f"   Realistic (50%): R${result['scenarios']['realistic']['final_bankroll']:.2f} ({result['scenarios']['realistic']['roi_percent']:+.2f}%)")
        logger.info(f"   Optimistic (90%): R${result['scenarios']['optimistic']['final_bankroll']:.2f} ({result['scenarios']['optimistic']['roi_percent']:+.2f}%)")
        
        return result
    
    def simulate_multiple_periods(
        self,
        avg_bets_per_week: int,
        avg_edge: float,
        win_rate: float
    ) -> dict:
        """
        Simulate betting performance over multiple time periods (4, 8, 12 weeks).
        
        Returns results for 30, 60, and 90 day periods with Monte Carlo simulations.
        
        Args:
            avg_bets_per_week: Average number of bets per week
            avg_edge: Average edge over bookmaker (e.g., 0.08 = 8%)
            win_rate: Win rate (e.g., 0.55 = 55%)
        
        Returns:
            dict: Results for each time period (4_weeks, 8_weeks, 12_weeks)
        """
        logger.info(f"📊 Running multi-period Monte Carlo simulation: {avg_bets_per_week} bets/week, edge={avg_edge:.2%}, win_rate={win_rate:.2%}")
        
        periods = [4, 8, 12]
        results = {}
        
        for weeks in periods:
            logger.info(f"\n--- Simulating {weeks} weeks ({weeks * 7} days) ---")
            result = self.simulate_period(avg_bets_per_week, avg_edge, win_rate, weeks)
            results[f'{weeks}_weeks'] = result
        
        logger.info(f"\n✅ Multi-period simulation complete")
        
        return results
    
    def reset_bankroll(self):
        """Reset bankroll to initial value for new simulation."""
        logger.info(f"🔄 Bankroll reset to R${self.initial_bankroll:.2f}")
