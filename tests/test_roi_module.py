"""
Consolidated tests for ROI modules (Kelly Criterion and ROI Simulator)
"""
import sys
from pathlib import Path
import random

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.roi.kelly_criterion import KellyCriterion
from modules.roi.roi_simulator import ROISimulator


def test_kelly_value_bet():
    """Test Kelly Criterion with value bet scenario"""
    kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
    result = kelly.calculate_stake(probability=0.58, odds=2.0)
    
    assert result['is_value_bet'] == True, f"Expected value bet, got {result['is_value_bet']}"
    assert result['stake'] > 0, f"Expected stake > 0, got {result['stake']}"
    
    print(f"✅ Kelly value bet test passed")
    print(f"   Stake: R${result['stake']:.2f}, Edge: {result['edge']:.2f}%, EV: R${result['expected_value']:.2f}")


def test_kelly_no_value():
    """Test Kelly Criterion with no value bet scenario"""
    kelly = KellyCriterion(bankroll=1000, kelly_fraction=0.25)
    result = kelly.calculate_stake(probability=0.45, odds=2.0)
    
    assert result['stake'] == 0, f"Expected stake = 0, got {result['stake']}"
    
    print(f"✅ Kelly no value test passed")
    print(f"   Stake: R${result['stake']:.2f} (no value bet)")


def test_roi_simulation():
    """Test ROI Simulator basic simulation"""
    random.seed(42)
    
    simulator = ROISimulator(initial_bankroll=1000)
    result = simulator.simulate_period(
        avg_bets_per_week=5,
        avg_edge=0.08,
        win_rate=0.55,
        weeks=4
    )
    
    assert 'final_bankroll' in result, "Result should have 'final_bankroll' key"
    assert result['final_bankroll'] > 0, f"Expected final_bankroll > 0, got {result['final_bankroll']}"
    assert 'profit' in result, "Result should have 'profit' key"
    assert 'roi_percent' in result, "Result should have 'roi_percent' key"
    
    print(f"✅ ROI simulation test passed")
    print(f"   Final Bankroll: R${result['final_bankroll']:.2f}, ROI: {result['roi_percent']:+.2f}%")


def test_integration():
    """Test integration of KellyCriterion and ROISimulator together"""
    random.seed(123)
    
    bankroll = 1000
    kelly_fraction = 0.25
    
    kelly = KellyCriterion(bankroll=bankroll, kelly_fraction=kelly_fraction)
    simulator = ROISimulator(initial_bankroll=bankroll, kelly_fraction=kelly_fraction)
    
    kelly_result = kelly.calculate_stake(probability=0.58, odds=2.0)
    assert kelly_result['is_value_bet'], "Should identify value bet"
    
    sim_result = simulator.simulate_period(
        avg_bets_per_week=5,
        avg_edge=0.08,
        win_rate=0.55,
        weeks=4
    )
    assert sim_result['final_bankroll'] > 0, "Simulation should return positive bankroll"
    
    kelly.update_bankroll(sim_result['final_bankroll'])
    new_stake_result = kelly.calculate_stake(probability=0.58, odds=2.0)
    
    if kelly_result['stake'] > 0 and new_stake_result['stake'] > 0:
        stake_ratio = new_stake_result['stake'] / kelly_result['stake']
        bankroll_ratio = sim_result['final_bankroll'] / bankroll
        assert abs(stake_ratio - bankroll_ratio) < 0.01, "Stake should scale with bankroll"
    
    print(f"✅ Integration test passed")
    print(f"   Initial stake: R${kelly_result['stake']:.2f}")
    print(f"   After simulation: R${sim_result['final_bankroll']:.2f}")
    print(f"   New stake: R${new_stake_result['stake']:.2f}")


if __name__ == "__main__":
    print("🔍 Running ROI module tests...\n")
    
    try:
        test_kelly_value_bet()
        print()
        
        test_kelly_no_value()
        print()
        
        test_roi_simulation()
        print()
        
        test_integration()
        print()
        
        print("🎉 ALL ROI TESTS PASSED!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
