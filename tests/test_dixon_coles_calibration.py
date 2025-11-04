"""
Test Dixon-Coles calibration for Brasileirão
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from models.dixon_coles import DixonColesModel


def test_parameters():
    """Test that Brasileirão parameters are correctly set"""
    model = DixonColesModel(brasileirao_mode=True)
    
    assert model.hfa == 1.35, "HFA deve ser 1.35"
    assert model.ava == 0.92, "AVA deve ser 0.92"
    assert model.league_avg_goals == 1.65, "Média deve ser 1.65"
    
    print("✅ Parameters test passed")


def test_lambda_range():
    """Test that lambdas generate realistic goal expectations"""
    model = DixonColesModel(brasileirao_mode=True)
    
    lh, la = model.calculate_lambdas(1.5, 1.2, 1.4, 1.3, "HOME")
    total = lh + la
    
    assert 2.0 <= total <= 3.0, f"Total de gols fora do esperado: {total}"
    assert 0.8 <= lh <= 2.0, f"Lambda home fora do esperado: {lh}"
    assert 0.8 <= la <= 2.0, f"Lambda away fora do esperado: {la}"
    
    print(f"✅ Lambda range test passed (Total: {total:.2f})")


def test_realistic_predictions():
    """Test that model generates realistic match predictions"""
    model = DixonColesModel(brasileirao_mode=True)
    
    test_cases = [
        {"home_attack": 1.6, "home_defense": 1.2, "away_attack": 1.4, "away_defense": 1.3, "expected_total": (2.3, 2.7)},
        {"home_attack": 1.8, "home_defense": 1.1, "away_attack": 1.2, "away_defense": 1.5, "expected_total": (2.4, 3.0)},
        {"home_attack": 1.3, "home_defense": 1.4, "away_attack": 1.3, "away_defense": 1.4, "expected_total": (2.0, 2.6)},
    ]
    
    for i, case in enumerate(test_cases):
        lh, la = model.calculate_lambdas(
            case["home_attack"], case["home_defense"],
            case["away_attack"], case["away_defense"],
            "HOME"
        )
        total = lh + la
        min_exp, max_exp = case["expected_total"]
        
        assert min_exp <= total <= max_exp, f"Caso {i+1}: Total {total:.2f} fora do esperado [{min_exp}, {max_exp}]"
        print(f"  Caso {i+1}: Total={total:.2f} gols ✅")
    
    print("✅ Realistic predictions test passed")


def test_over_2_5_probability():
    """Test that Over 2.5 probability is realistic (~40-45%)"""
    model = DixonColesModel(brasileirao_mode=True)
    
    from scipy.stats import poisson
    
    lh, la = model.calculate_lambdas(1.5, 1.2, 1.4, 1.3, "HOME")
    
    prob_over_2_5 = 0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            if home_goals + away_goals > 2.5:
                prob_over_2_5 += poisson.pmf(home_goals, lh) * poisson.pmf(away_goals, la)
    
    prob_over_2_5_pct = prob_over_2_5 * 100
    
    assert 35 <= prob_over_2_5_pct <= 50, f"Over 2.5 = {prob_over_2_5_pct:.1f}% (esperado 40-45%)"
    
    print(f"✅ Over 2.5 test passed: {prob_over_2_5_pct:.1f}%")


if __name__ == "__main__":
    print("🔍 Running Dixon-Coles calibration tests...\n")
    
    try:
        test_parameters()
        test_lambda_range()
        test_realistic_predictions()
        test_over_2_5_probability()
        
        print("\n🎉 ALL CALIBRATION TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
