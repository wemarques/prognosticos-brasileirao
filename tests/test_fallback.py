"""
Test fallback statistics for corners and cards
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from analysis.calculator import _calculate_corners_fallback, _calculate_cards_fallback


def test_corners_fallback():
    """Test that corner fallback returns realistic probabilities"""
    result = _calculate_corners_fallback()
    
    assert 'p_over_95' in result, "Missing p_over_95 key"
    
    over_95_pct = result['p_over_95'] * 100
    assert 50 <= over_95_pct <= 60, f"Over 9.5 = {over_95_pct}% (esperado ~55%)"
    
    assert 'p_over_85' in result
    assert 'p_over_105' in result
    assert 'p_over_115' in result
    
    print(f"✅ Corner fallback test passed - Over 9.5 = {over_95_pct:.1f}%")


def test_cards_fallback():
    """Test that card fallback returns realistic probabilities"""
    result = _calculate_cards_fallback()
    
    assert 'p_over_45' in result, "Missing p_over_45 key"
    
    over_45_pct = result['p_over_45'] * 100
    assert 48 <= over_45_pct <= 56, f"Over 4.5 = {over_45_pct}% (esperado ~52%)"
    
    assert 'p_over_35' in result
    assert 'p_over_55' in result
    assert 'p_over_65' in result
    
    print(f"✅ Card fallback test passed - Over 4.5 = {over_45_pct:.1f}%")


def test_fallback_values_are_realistic():
    """Test that fallback values are within realistic ranges"""
    corners = _calculate_corners_fallback()
    cards = _calculate_cards_fallback()
    
    assert corners['p_over_85'] > corners['p_over_95']
    assert corners['p_over_95'] > corners['p_over_105']
    assert corners['p_over_105'] > corners['p_over_115']
    
    assert cards['p_over_35'] > cards['p_over_45']
    assert cards['p_over_45'] > cards['p_over_55']
    assert cards['p_over_55'] > cards['p_over_65']
    
    assert 8 <= corners['avg_corners'] <= 12, f"Average corners = {corners['avg_corners']}"
    assert 4 <= cards['avg_cards'] <= 6, f"Average cards = {cards['avg_cards']}"
    
    print("✅ Fallback values are realistic and properly ordered")


def test_fallback_returns_dict():
    """Test that fallback functions return dictionaries"""
    corners = _calculate_corners_fallback()
    cards = _calculate_cards_fallback()
    
    assert isinstance(corners, dict), "Corners fallback should return dict"
    assert isinstance(cards, dict), "Cards fallback should return dict"
    
    print("✅ Fallback functions return proper data types")


if __name__ == "__main__":
    print("🔍 Running fallback tests...\n")
    
    try:
        test_corners_fallback()
        test_cards_fallback()
        test_fallback_values_are_realistic()
        test_fallback_returns_dict()
        
        print("\n🎉 ALL TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
