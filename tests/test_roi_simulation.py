"""
Unit tests for ROI Simulation Module
Tests for StakeOptimizer and OutcomeChecker
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from analysis.stake_optimizer import StakeOptimizer
from analysis.outcome_checker import OutcomeChecker


class TestRoiSimulation(unittest.TestCase):
    """Test suite for ROI simulation components"""
    
    def test_kelly_stake_calculation(self):
        """Test Kelly Criterion stake calculation with specific inputs"""
        value_bets = [
            {
                "market": "OVER/UNDER",
                "selection": "Over 2.5",
                "probability": 0.6,
                "suggested_odd": 2.0,
            }
        ]
        total_investment = 100.0
        fractional_kelly = 0.5
        
        optimizer = StakeOptimizer()
        bets_with_stakes = optimizer.calculate_kelly_stakes(
            value_bets, total_investment, fractional_kelly
        )
        
        self.assertEqual(len(bets_with_stakes), 1)
        self.assertIn("stake", bets_with_stakes[0])
        
        expected_stake = 50.0
        self.assertAlmostEqual(bets_with_stakes[0]["stake"], expected_stake, places=1)
    
    def test_outcome_checker_over_win(self):
        """Test outcome checker for Over 2.5 with 3 goals (win)"""
        bet = {
            "market": "OVER/UNDER",
            "selection": "Over 2.5",
            "probability": 0.6,
            "suggested_odd": 2.0,
        }
        match_details = {
            "status": "FINISHED",
            "score": {
                "fullTime": {
                    "home": 2,
                    "away": 1
                }
            }
        }
        
        result = OutcomeChecker.check_bet_outcome(bet, match_details)
        self.assertTrue(result, "Over 2.5 should win with 3 total goals")
    
    def test_outcome_checker_over_loss(self):
        """Test outcome checker for Over 2.5 with 2 goals (loss)"""
        bet = {
            "market": "OVER/UNDER",
            "selection": "Over 2.5",
            "probability": 0.6,
            "suggested_odd": 2.0,
        }
        match_details = {
            "status": "FINISHED",
            "score": {
                "fullTime": {
                    "home": 1,
                    "away": 1
                }
            }
        }
        
        result = OutcomeChecker.check_bet_outcome(bet, match_details)
        self.assertFalse(result, "Over 2.5 should lose with 2 total goals")
    
    def test_outcome_checker_1x2_home_win(self):
        """Test outcome checker for 1X2 market - home win"""
        bet = {
            "market": "1X2",
            "selection": "1",
            "probability": 0.5,
            "suggested_odd": 2.0,
        }
        match_details = {
            "status": "FINISHED",
            "score": {
                "fullTime": {
                    "home": 2,
                    "away": 1
                }
            }
        }
        
        result = OutcomeChecker.check_bet_outcome(bet, match_details)
        self.assertTrue(result, "Home win (1) should win when home score > away score")
    
    def test_outcome_checker_btts_yes(self):
        """Test outcome checker for BTTS Yes"""
        bet = {
            "market": "BTTS",
            "selection": "Yes",
            "probability": 0.55,
            "suggested_odd": 1.8,
        }
        match_details = {
            "status": "FINISHED",
            "score": {
                "fullTime": {
                    "home": 2,
                    "away": 1
                }
            }
        }
        
        result = OutcomeChecker.check_bet_outcome(bet, match_details)
        self.assertTrue(result, "BTTS Yes should win when both teams score")
    
    def test_multiple_bets_stake_distribution(self):
        """Test stake distribution across multiple value bets"""
        value_bets = [
            {
                "market": "OVER/UNDER",
                "selection": "Over 2.5",
                "probability": 0.6,
                "suggested_odd": 2.0,
            },
            {
                "market": "BTTS",
                "selection": "Yes",
                "probability": 0.55,
                "suggested_odd": 1.9,
            },
            {
                "market": "1X2",
                "selection": "1",
                "probability": 0.5,
                "suggested_odd": 2.2,
            }
        ]
        total_investment = 100.0
        
        optimizer = StakeOptimizer()
        bets_with_stakes = optimizer.calculate_kelly_stakes(value_bets, total_investment)
        
        self.assertEqual(len(bets_with_stakes), 3)
        for bet in bets_with_stakes:
            self.assertIn("stake", bet)
            self.assertGreater(bet["stake"], 0)
        
        total_stakes = sum(bet["stake"] for bet in bets_with_stakes)
        self.assertLessEqual(total_stakes, total_investment)


if __name__ == "__main__":
    unittest.main()
