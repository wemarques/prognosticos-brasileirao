"""
Test Kelly Criterion Module
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.roi.kelly_criterion import KellyCriterion


def test_basic_kelly_calculation():
    """Test basic Kelly Criterion calculation"""
    k = KellyCriterion(1000, 0.25)
    r = k.calculate_stake(0.58, 2.0)
    
    assert r['is_value_bet'], "Should be a value bet"
    assert r['stake'] > 0, "Stake should be positive"
    assert r['stake'] <= 50, f"Stake should be <= 5% of R$1000 (R$50), got R${r['stake']:.2f}"
    assert r['edge'] > 0, "Edge should be positive for value bet"
    assert r['expected_value'] > 0, "Expected value should be positive"
    
    print(f"✅ Basic Kelly calculation test passed")
    print(f"   Stake: R${r['stake']:.2f}, Edge: {r['edge']:.2f}%, EV: R${r['expected_value']:.2f}")


def test_no_value_bet():
    """Test that no bet is recommended when there's no value"""
    k = KellyCriterion(1000, 0.25)
    r = k.calculate_stake(0.40, 2.0)  # Probability < implied probability (0.5)
    
    assert not r['is_value_bet'], "Should not be a value bet"
    assert r['stake'] == 0, "Stake should be zero for no value bet"
    assert r['edge'] <= 0, "Edge should be negative or zero"
    
    print(f"✅ No value bet test passed")
    print(f"   Stake: R${r['stake']:.2f}, Edge: {r['edge']:.2f}%")


def test_max_stake_limit():
    """Test that stake is capped at 5% of bankroll"""
    k = KellyCriterion(1000, 1.0)  # Full Kelly (no fraction)
    r = k.calculate_stake(0.70, 2.0)  # High probability
    
    assert r['stake'] <= 50, f"Stake should be capped at R$50, got R${r['stake']:.2f}"
    assert r['kelly_percentage'] <= 5.0, "Kelly percentage should be capped at 5%"
    
    print(f"✅ Max stake limit test passed")
    print(f"   Stake: R${r['stake']:.2f} (capped at 5%)")


def test_kelly_fraction():
    """Test that Kelly fraction is applied correctly"""
    k1 = KellyCriterion(1000, 1.0)  # Full Kelly
    k2 = KellyCriterion(1000, 0.25)  # Quarter Kelly
    
    r1 = k1.calculate_stake(0.58, 2.0)
    r2 = k2.calculate_stake(0.58, 2.0)
    
    if r1['stake'] < 50:  # If not capped
        assert abs(r2['stake'] - r1['stake'] * 0.25) < 0.1, "Quarter Kelly should be ~1/4 of full Kelly"
    
    print(f"✅ Kelly fraction test passed")
    print(f"   Full Kelly: R${r1['stake']:.2f}, Quarter Kelly: R${r2['stake']:.2f}")


def test_invalid_inputs():
    """Test handling of invalid inputs"""
    k = KellyCriterion(1000, 0.25)
    
    r1 = k.calculate_stake(1.5, 2.0)
    assert r1['stake'] == 0, "Should return zero stake for invalid probability"
    
    r2 = k.calculate_stake(-0.1, 2.0)
    assert r2['stake'] == 0, "Should return zero stake for negative probability"
    
    r3 = k.calculate_stake(0.58, 0.5)
    assert r3['stake'] == 0, "Should return zero stake for invalid odds"
    
    print(f"✅ Invalid inputs test passed")


def test_bankroll_update():
    """Test bankroll update functionality"""
    k = KellyCriterion(1000, 0.25)
    
    r1 = k.calculate_stake(0.58, 2.0)
    stake1 = r1['stake']
    
    k.update_bankroll(2000)
    
    r2 = k.calculate_stake(0.58, 2.0)
    stake2 = r2['stake']
    
    assert abs(stake2 - stake1 * 2) < 0.1, "Stake should scale with bankroll"
    
    print(f"✅ Bankroll update test passed")
    print(f"   R$1000 stake: R${stake1:.2f}, R$2000 stake: R${stake2:.2f}")


def test_edge_calculation():
    """Test edge calculation accuracy"""
    k = KellyCriterion(1000, 0.25)
    
    r = k.calculate_stake(0.58, 2.0)
    
    assert abs(r['edge'] - 8.0) < 0.01, f"Edge should be 8%, got {r['edge']:.2f}%"
    
    print(f"✅ Edge calculation test passed")
    print(f"   Edge: {r['edge']:.2f}%")


def test_expected_value():
    """Test expected value calculation"""
    k = KellyCriterion(1000, 0.25)
    r = k.calculate_stake(0.58, 2.0)
    
    expected_ev = r['stake'] * (2.0 * 0.58 - 1)
    
    assert abs(r['expected_value'] - expected_ev) < 0.01, "Expected value calculation incorrect"
    
    print(f"✅ Expected value test passed")
    print(f"   EV: R${r['expected_value']:.2f}")


if __name__ == "__main__":
    print("🔍 Running Kelly Criterion tests...\n")
    
    try:
        test_basic_kelly_calculation()
        test_no_value_bet()
        test_max_stake_limit()
        test_kelly_fraction()
        test_invalid_inputs()
        test_bankroll_update()
        test_edge_calculation()
        test_expected_value()
        
        print("\n🎉 ALL KELLY CRITERION TESTS PASSED!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
