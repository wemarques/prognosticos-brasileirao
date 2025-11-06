"""
Test ROI Simulator Module
"""
import sys
from pathlib import Path
import random

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.roi.roi_simulator import ROISimulator


def test_basic_simulation():
    """Test basic ROI simulation"""
    random.seed(42)  # Set seed for reproducibility
    
    sim = ROISimulator(1000, 0.25)
    res = sim.simulate_period(5, 0.08, 0.55, 4)
    
    assert 'final_bankroll' in res, "Should have final_bankroll key"
    assert res['final_bankroll'] > 0, "Final bankroll should be positive"
    assert 'profit' in res, "Should have profit key"
    assert 'roi_percent' in res, "Should have roi_percent key"
    assert 'total_bets' in res, "Should have total_bets key"
    assert res['total_bets'] == 20, f"Should have 20 total bets (5 bets/week * 4 weeks), got {res['total_bets']}"
    
    print(f"✅ Basic simulation test passed")
    print(f"   Final: R${res['final_bankroll']:.2f}, Profit: R${res['profit']:+.2f}, ROI: {res['roi_percent']:+.2f}%")


def test_multiple_periods():
    """Test multi-period simulation"""
    random.seed(42)  # Set seed for reproducibility
    
    sim = ROISimulator(1000, 0.25)
    results = sim.simulate_multiple_periods(5, 0.08, 0.55)
    
    assert '4_weeks' in results, "Should have 4_weeks results"
    assert '8_weeks' in results, "Should have 8_weeks results"
    assert '12_weeks' in results, "Should have 12_weeks results"
    
    for period, res in results.items():
        assert 'final_bankroll' in res, f"{period} should have final_bankroll"
        assert 'profit' in res, f"{period} should have profit"
        assert 'roi_percent' in res, f"{period} should have roi_percent"
    
    print(f"✅ Multiple periods test passed")
    print(f"   4 weeks: R${results['4_weeks']['final_bankroll']:.2f} ({results['4_weeks']['roi_percent']:+.2f}%)")
    print(f"   8 weeks: R${results['8_weeks']['final_bankroll']:.2f} ({results['8_weeks']['roi_percent']:+.2f}%)")
    print(f"   12 weeks: R${results['12_weeks']['final_bankroll']:.2f} ({results['12_weeks']['roi_percent']:+.2f}%)")


def test_positive_edge_scenario():
    """Test simulation with positive edge and good win rate"""
    random.seed(123)  # Different seed
    
    sim = ROISimulator(1000, 0.25)
    res = sim.simulate_period(10, 0.10, 0.60, 8)  # Higher edge and win rate
    
    assert res['final_bankroll'] > 0, "Final bankroll should be positive"
    assert res['total_bets'] == 80, f"Should have 80 total bets (10 bets/week * 8 weeks), got {res['total_bets']}"
    
    print(f"✅ Positive edge scenario test passed")
    print(f"   Final: R${res['final_bankroll']:.2f}, ROI: {res['roi_percent']:+.2f}%")


def test_low_edge_scenario():
    """Test simulation with low edge"""
    random.seed(456)  # Different seed
    
    sim = ROISimulator(1000, 0.25)
    res = sim.simulate_period(5, 0.03, 0.52, 4)  # Low edge and win rate
    
    assert res['final_bankroll'] > 0, "Final bankroll should be positive"
    
    print(f"✅ Low edge scenario test passed")
    print(f"   Final: R${res['final_bankroll']:.2f}, ROI: {res['roi_percent']:+.2f}%")


def test_stake_calculation():
    """Test that stake is calculated correctly"""
    random.seed(42)
    
    sim = ROISimulator(1000, 0.25)
    
    
    res = sim.simulate_period(1, 0.08, 0.55, 1)
    
    change = abs(res['final_bankroll'] - 1000)
    assert change > 0, "Bankroll should have changed"
    assert change < 50, f"Change should be reasonable for 2% stake, got {change}"
    
    print(f"✅ Stake calculation test passed")
    print(f"   Bankroll change: R${res['final_bankroll'] - 1000:+.2f}")


def test_max_stake_limit():
    """Test that stake is capped at 5% of bankroll"""
    random.seed(42)
    
    sim = ROISimulator(1000, 1.0)  # Full Kelly
    res = sim.simulate_period(1, 0.30, 0.70, 1)  # Very high edge
    
    
    change = abs(res['final_bankroll'] - 1000)
    assert change <= 60, f"Change should be capped at ~5% stake (R$50), got R${change:.2f}"
    
    print(f"✅ Max stake limit test passed")
    print(f"   Bankroll change: R${res['final_bankroll'] - 1000:+.2f}")


def test_win_loss_tracking():
    """Test that wins and losses are tracked correctly"""
    random.seed(42)
    
    sim = ROISimulator(1000, 0.25)
    res = sim.simulate_period(10, 0.08, 0.55, 2)
    
    assert res['wins'] + res['losses'] == res['total_bets'], "Wins + losses should equal total bets"
    assert res['wins'] > 0, "Should have some wins"
    assert res['losses'] >= 0, "Should have zero or more losses"
    assert 'actual_win_rate' in res, "Should track actual win rate"
    
    print(f"✅ Win/loss tracking test passed")
    print(f"   {res['wins']}W-{res['losses']}L ({res['actual_win_rate']:.2%} win rate)")


def test_different_kelly_fractions():
    """Test simulation with different Kelly fractions"""
    random.seed(42)
    
    sim1 = ROISimulator(1000, 0.25)  # Quarter Kelly
    sim2 = ROISimulator(1000, 0.50)  # Half Kelly
    
    res1 = sim1.simulate_period(5, 0.08, 0.55, 4)
    
    random.seed(42)  # Reset seed for fair comparison
    res2 = sim2.simulate_period(5, 0.08, 0.55, 4)
    
    assert res1['final_bankroll'] != res2['final_bankroll'], "Different Kelly fractions should produce different results"
    
    print(f"✅ Different Kelly fractions test passed")
    print(f"   Quarter Kelly: R${res1['final_bankroll']:.2f}")
    print(f"   Half Kelly: R${res2['final_bankroll']:.2f}")


if __name__ == "__main__":
    print("🔍 Running ROI Simulator tests...\n")
    
    try:
        test_basic_simulation()
        test_multiple_periods()
        test_positive_edge_scenario()
        test_low_edge_scenario()
        test_stake_calculation()
        test_max_stake_limit()
        test_win_loss_tracking()
        test_different_kelly_fractions()
        
        print("\n🎉 ALL ROI SIMULATOR TESTS PASSED!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
