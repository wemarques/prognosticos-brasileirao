"""
Comprehensive test suite for ROI module (Kelly Criterion + ROI Simulator)
Tests all functionality including validation, calculations, and integrations
"""
import unittest
import numpy as np
from modules.roi.kelly_criterion import KellyCriterion, find_value_bets
from modules.roi.roi_simulator import ROISimulator


class TestKellyCriterionBasic(unittest.TestCase):
    """Test 1: Basic Kelly Criterion instantiation"""
    
    def test_kelly_basic_instantiation(self):
        """Test that KellyCriterion can be instantiated with valid parameters"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        self.assertEqual(kelly.bankroll, 1000)
        self.assertEqual(kelly.kelly_fraction, 0.25)
        self.assertEqual(kelly.max_stake_percentage, 0.05)
    
    def test_kelly_default_fraction(self):
        """Test default kelly_fraction is 0.25"""
        kelly = KellyCriterion(bankroll=1000)
        self.assertEqual(kelly.kelly_fraction, 0.25)


class TestKellyCriterionValueBet(unittest.TestCase):
    """Test 2: Kelly Criterion value bet calculation"""
    
    def test_kelly_value_bet_calculation(self):
        """Test correct stake calculation for a value bet"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        result = kelly.calculate_stake(probability=0.55, odds=2.0)
        
        self.assertTrue(result['is_value_bet'])
        self.assertGreater(result['stake'], 0)
        self.assertGreater(result['edge'], 0)
        self.assertGreater(result['expected_value'], 0)
        self.assertGreater(result['kelly_percentage'], 0)
    
    def test_kelly_high_edge_value_bet(self):
        """Test value bet with high edge"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        result = kelly.calculate_stake(probability=0.60, odds=2.0)
        
        self.assertTrue(result['is_value_bet'])
        self.assertAlmostEqual(result['edge'], 10.0, places=1)


class TestKellyCriterionNoValue(unittest.TestCase):
    """Test 3: Kelly Criterion no-value bet detection"""
    
    def test_kelly_no_value_bet(self):
        """Test that non-value bets return stake=0"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        result = kelly.calculate_stake(probability=0.45, odds=2.0)
        
        self.assertFalse(result['is_value_bet'])
        self.assertEqual(result['stake'], 0.0)
        self.assertLess(result['edge'], 0)
        self.assertIn('reason', result)
    
    def test_kelly_zero_edge(self):
        """Test bet with exactly zero edge"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        result = kelly.calculate_stake(probability=0.50, odds=2.0)
        
        self.assertFalse(result['is_value_bet'])
        self.assertEqual(result['stake'], 0.0)


class TestKellyCriterionValidation(unittest.TestCase):
    """Test 4: Kelly Criterion input validation"""
    
    def test_kelly_invalid_bankroll_low(self):
        """Test that bankroll below 100 raises ValueError"""
        with self.assertRaises(ValueError):
            KellyCriterion(bankroll=50, kelly_fraction=0.25)
    
    def test_kelly_invalid_bankroll_high(self):
        """Test that bankroll above 100000 raises ValueError"""
        with self.assertRaises(ValueError):
            KellyCriterion(bankroll=150000, kelly_fraction=0.25)
    
    def test_kelly_invalid_fraction_low(self):
        """Test that kelly_fraction below 0.1 raises ValueError"""
        with self.assertRaises(ValueError):
            KellyCriterion(bankroll=1000, kelly_fraction=0.05)
    
    def test_kelly_invalid_fraction_high(self):
        """Test that kelly_fraction above 0.5 raises ValueError"""
        with self.assertRaises(ValueError):
            KellyCriterion(bankroll=1000, kelly_fraction=0.6)
    
    def test_kelly_invalid_probability(self):
        """Test that invalid probability returns no-bet result"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        result = kelly.calculate_stake(probability=1.5, odds=2.0)
        self.assertEqual(result['stake'], 0.0)
        self.assertIn('reason', result)
        
        result = kelly.calculate_stake(probability=-0.1, odds=2.0)
        self.assertEqual(result['stake'], 0.0)
    
    def test_kelly_invalid_odds(self):
        """Test that invalid odds returns no-bet result"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        result = kelly.calculate_stake(probability=0.55, odds=0.5)
        self.assertEqual(result['stake'], 0.0)
        self.assertIn('reason', result)


class TestFindValueBets(unittest.TestCase):
    """Test 5: find_value_bets function"""
    
    def test_find_value_bets_basic(self):
        """Test basic value bet identification"""
        probs = {
            'home_win': 0.55,
            'draw': 0.25,
            'away_win': 0.20
        }
        odds = {
            'home_win': 2.0,   # Implied: 0.50, Edge: +0.05
            'draw': 3.5,       # Implied: 0.286, Edge: -0.036
            'away_win': 6.0    # Implied: 0.167, Edge: +0.033
        }
        
        value_bets = find_value_bets(probs, odds, min_edge=0.03)
        
        self.assertEqual(len(value_bets), 2)
        self.assertEqual(value_bets[0]['market'], 'home_win')
        self.assertGreater(value_bets[0]['edge'], 0.03)
    
    def test_find_value_bets_sorted(self):
        """Test that value bets are sorted by edge (descending)"""
        probs = {
            'market_a': 0.60,
            'market_b': 0.55,
            'market_c': 0.50
        }
        odds = {
            'market_a': 2.0,   # Edge: 0.10
            'market_b': 2.0,   # Edge: 0.05
            'market_c': 2.0    # Edge: 0.00
        }
        
        value_bets = find_value_bets(probs, odds, min_edge=0.01)
        
        self.assertEqual(len(value_bets), 2)
        self.assertGreater(value_bets[0]['edge'], value_bets[1]['edge'])
    
    def test_find_value_bets_no_matches(self):
        """Test when no value bets are found"""
        probs = {'market_a': 0.40}
        odds = {'market_a': 2.0}  # Edge: -0.10
        
        value_bets = find_value_bets(probs, odds, min_edge=0.05)
        
        self.assertEqual(len(value_bets), 0)


class TestROISimulatorBasic(unittest.TestCase):
    """Test 6: ROI Simulator basic instantiation"""
    
    def test_roi_simulator_instantiation(self):
        """Test that ROISimulator can be instantiated"""
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        
        self.assertEqual(simulator.initial_bankroll, 1000)
        self.assertEqual(simulator.kelly_fraction, 0.25)
        self.assertEqual(simulator.num_simulations, 1000)
    
    def test_roi_simulator_default_fraction(self):
        """Test default kelly_fraction is 0.25"""
        simulator = ROISimulator(initial_bankroll=1000)
        self.assertEqual(simulator.kelly_fraction, 0.25)


class TestROISimulatePeriod(unittest.TestCase):
    """Test 7: ROI Simulator period simulation"""
    
    def test_roi_simulate_period_structure(self):
        """Test that simulate_period returns correct structure"""
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        
        result = simulator.simulate_period(
            avg_bets_per_week=5,
            avg_edge=0.08,
            win_rate=0.55,
            weeks=4
        )
        
        self.assertIn('days', result)
        self.assertIn('scenarios', result)
        self.assertIn('statistics', result)
        
        self.assertEqual(result['days'], 28)
        
        self.assertIn('pessimistic', result['scenarios'])
        self.assertIn('realistic', result['scenarios'])
        self.assertIn('optimistic', result['scenarios'])
        
        for scenario in ['pessimistic', 'realistic', 'optimistic']:
            self.assertIn('final_bankroll', result['scenarios'][scenario])
            self.assertIn('profit', result['scenarios'][scenario])
            self.assertIn('roi_percent', result['scenarios'][scenario])
    
    def test_roi_simulate_period_positive_edge(self):
        """Test that positive edge generally produces profit"""
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        
        result = simulator.simulate_period(
            avg_bets_per_week=5,
            avg_edge=0.10,
            win_rate=0.60,
            weeks=4
        )
        
        self.assertGreater(result['scenarios']['realistic']['final_bankroll'], 900)
    
    def test_roi_simulate_period_percentiles(self):
        """Test that percentiles are ordered correctly"""
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        
        result = simulator.simulate_period(
            avg_bets_per_week=5,
            avg_edge=0.08,
            win_rate=0.55,
            weeks=4
        )
        
        pessimistic = result['scenarios']['pessimistic']['final_bankroll']
        realistic = result['scenarios']['realistic']['final_bankroll']
        optimistic = result['scenarios']['optimistic']['final_bankroll']
        
        self.assertLessEqual(pessimistic, realistic)
        self.assertLessEqual(realistic, optimistic)


class TestROIMultiplePeriods(unittest.TestCase):
    """Test 8: ROI Simulator multiple periods (30/60/90 days)"""
    
    def test_roi_multiple_periods_structure(self):
        """Test that simulate_multiple_periods returns correct structure"""
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        
        results = simulator.simulate_multiple_periods(
            avg_bets_per_week=5,
            avg_edge=0.08,
            win_rate=0.55
        )
        
        self.assertIn('4_weeks', results)
        self.assertIn('8_weeks', results)
        self.assertIn('12_weeks', results)
        
        for period in ['4_weeks', '8_weeks', '12_weeks']:
            self.assertIn('days', results[period])
            self.assertIn('scenarios', results[period])
            self.assertIn('statistics', results[period])
    
    def test_roi_multiple_periods_days(self):
        """Test that days are calculated correctly"""
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        
        results = simulator.simulate_multiple_periods(
            avg_bets_per_week=5,
            avg_edge=0.08,
            win_rate=0.55
        )
        
        self.assertEqual(results['4_weeks']['days'], 28)
        self.assertEqual(results['8_weeks']['days'], 56)
        self.assertEqual(results['12_weeks']['days'], 84)


class TestIntegration(unittest.TestCase):
    """Test 9: Integration test - Kelly + ROI together"""
    
    def test_kelly_and_roi_integration(self):
        """Test Kelly Criterion and ROI Simulator working together"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        stake_result = kelly.calculate_stake(probability=0.55, odds=2.0)
        
        self.assertTrue(stake_result['is_value_bet'])
        self.assertGreater(stake_result['stake'], 0)
        
        simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
        roi_result = simulator.simulate_period(
            avg_bets_per_week=5,
            avg_edge=0.05,  # 5% edge similar to Kelly result
            win_rate=0.55,
            weeks=4
        )
        
        self.assertIn('scenarios', roi_result)
        self.assertGreater(roi_result['scenarios']['realistic']['final_bankroll'], 0)
    
    def test_multiple_stakes_and_roi(self):
        """Test calculating multiple stakes and simulating ROI"""
        kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
        
        bets = [
            {'probability': 0.55, 'odds': 2.0},
            {'probability': 0.60, 'odds': 1.8},
            {'probability': 0.45, 'odds': 2.5}
        ]
        
        results = kelly.calculate_multiple_stakes(bets)
        
        self.assertEqual(len(results), 3)
        
        value_bets = [r for r in results if r['is_value_bet']]
        self.assertGreater(len(value_bets), 0)
        
        if value_bets:
            avg_edge = sum(r['edge'] for r in value_bets) / len(value_bets) / 100
            
            simulator = ROISimulator(initial_bankroll=1000, kelly_fraction=0.25)
            roi_result = simulator.simulate_multiple_periods(
                avg_bets_per_week=5,
                avg_edge=avg_edge,
                win_rate=0.55
            )
            
            self.assertIn('4_weeks', roi_result)
            self.assertIn('8_weeks', roi_result)
            self.assertIn('12_weeks', roi_result)


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
