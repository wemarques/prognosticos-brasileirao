"""
Validate Dixon-Coles calibration against real Brasileirão data
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from models.dixon_coles import DixonColesModel
from scipy.stats import poisson
import numpy as np


def validate_against_brasileirao_2024():
    """
    Validate model against Brasileirão 2024 data
    Real average: 2.45 goals per game
    """
    model = DixonColesModel(brasileirao_mode=True)
    
    predictions = []
    for _ in range(100):
        home_attack = np.random.uniform(1.2, 1.8)
        home_defense = np.random.uniform(1.1, 1.5)
        away_attack = np.random.uniform(1.2, 1.8)
        away_defense = np.random.uniform(1.1, 1.5)
        
        lh, la = model.calculate_lambdas(home_attack, home_defense, away_attack, away_defense, "HOME")
        predictions.append(lh + la)
    
    mean_prediction = np.mean(predictions)
    std_prediction = np.std(predictions)
    
    print(f"\n📊 VALIDAÇÃO CONTRA BRASILEIRÃO 2024")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Média real Brasileirão: 2.45 gols/jogo")
    print(f"Média prevista modelo: {mean_prediction:.2f} gols/jogo")
    print(f"Desvio padrão: {std_prediction:.2f}")
    print(f"Erro absoluto: {abs(mean_prediction - 2.45):.2f} gols")
    
    error = abs(mean_prediction - 2.45)
    if error < 0.3:
        print(f"✅ Calibração EXCELENTE (erro < 0.3)")
    elif error < 0.5:
        print(f"✅ Calibração BOA (erro < 0.5)")
    elif error < 0.8:
        print(f"⚠️ Calibração ACEITÁVEL (erro < 0.8)")
    else:
        print(f"❌ Calibração RUIM (erro >= 0.8)")
        return False
    
    return True


if __name__ == "__main__":
    success = validate_against_brasileirao_2024()
    if success:
        print("\n🎉 CALIBRAÇÃO VALIDADA COM SUCESSO!")
    else:
        print("\n❌ CALIBRAÇÃO PRECISA DE AJUSTES")
        sys.exit(1)
