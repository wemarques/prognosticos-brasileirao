"""
Test draw probability adjustment for defensive games
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from models.dixon_coles import DixonColesModel


def test_defensive_game_draw_boost():
    """Test that defensive games get draw boost"""
    model = DixonColesModel(brasileirao_mode=True)
    
    lambda_home = 1.0
    lambda_away = 1.1
    
    probs = model.calculate_match_probabilities(lambda_home, lambda_away)
    
    assert 28 <= probs['p_draw'] * 100 <= 38, f"Empate = {probs['p_draw']*100:.1f}% (esperado 30-35%)"
    
    total = probs['p_home_win'] + probs['p_draw'] + probs['p_away_win']
    assert 0.999 <= total <= 1.001, f"Soma = {total*100}%"
    
    print(f"✅ Defensive game: Draw = {probs['p_draw']*100:.1f}%")


def test_offensive_game_no_boost():
    """Test that offensive games don't get draw boost"""
    model = DixonColesModel(brasileirao_mode=True)
    
    lambda_home = 1.6
    lambda_away = 1.5
    
    probs = model.calculate_match_probabilities(lambda_home, lambda_away)
    
    assert 15 <= probs['p_draw'] * 100 <= 25, f"Empate = {probs['p_draw']*100:.1f}% (esperado 15-25%)"
    
    total = probs['p_home_win'] + probs['p_draw'] + probs['p_away_win']
    assert 0.999 <= total <= 1.001, f"Soma = {total*100}%"
    
    print(f"✅ Offensive game: Draw = {probs['p_draw']*100:.1f}%")


def test_probability_sum():
    """Test that probabilities always sum to 100%"""
    model = DixonColesModel(brasileirao_mode=True)
    
    test_cases = [
        (0.8, 0.9),
        (1.1, 1.0),
        (1.5, 1.4),
        (1.8, 1.9),
        (2.2, 2.0),
    ]
    
    for lh, la in test_cases:
        probs = model.calculate_match_probabilities(lh, la)
        total = probs['p_home_win'] + probs['p_draw'] + probs['p_away_win']
        
        assert 0.999 <= total <= 1.001, f"Lambda ({lh},{la}): Soma = {total*100}%"
        print(f"  ({lh:.1f}, {la:.1f}): Draw={probs['p_draw']*100:.1f}%, Total={total*100:.1f}% ✅")
    
    print("✅ All probability sums OK")


if __name__ == "__main__":
    print("🔍 Running draw adjustment tests...\n")
    
    try:
        test_defensive_game_draw_boost()
        test_offensive_game_no_boost()
        test_probability_sum()
        
        print("\n🎉 ALL DRAW ADJUSTMENT TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
