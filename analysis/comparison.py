"""
Sistema de Comparação: Prognóstico vs Realidade
Analisa discrepâncias e sugere ajustes no modelo
"""

from typing import Dict, List, Tuple
import json
from datetime import datetime

class PrognosisComparator:
    """Compara prognósticos com resultados reais"""
    
    def __init__(self):
        self.discrepancies = []
        self.accuracy_stats = {
            'total_matches': 0,
            'correct_1x2': 0,
            'correct_over_under': 0,
            'correct_btts': 0,
            'avg_prob_error': 0
        }
    
    def compare_match(
        self,
        prognosis: Dict,
        real_result: Dict,
        match_info: Dict
    ) -> Dict:
        """
        Compara prognóstico com resultado real de um jogo
        
        Args:
            prognosis: Prognóstico gerado pelo modelo
            real_result: Resultado real do jogo
            match_info: Informações do jogo (times, data, etc)
            
        Returns:
            Dict com análise de comparação
        """
        comparison = {
            'match': match_info,
            'prognosis': prognosis,
            'real_result': real_result,
            'accuracy': {},
            'discrepancies': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. Comparar Resultado Final (1X2)
        predicted_result = self._get_predicted_result(prognosis['probabilities'])
        actual_result = self._get_actual_result(real_result)
        
        comparison['accuracy']['1x2'] = {
            'predicted': predicted_result,
            'actual': actual_result,
            'correct': predicted_result == actual_result,
            'probability': prognosis['probabilities'].get(f'{predicted_result}_win' if predicted_result != 'draw' else 'draw', 0)
        }
        
        if not comparison['accuracy']['1x2']['correct']:
            comparison['discrepancies'].append({
                'market': '1X2',
                'predicted': predicted_result,
                'actual': actual_result,
                'confidence': comparison['accuracy']['1x2']['probability'],
                'severity': 'HIGH' if comparison['accuracy']['1x2']['probability'] > 0.6 else 'MEDIUM'
            })
        
        # 2. Comparar Total de Gols
        predicted_goals = prognosis['expected_goals']['total']
        actual_goals = real_result['home_score'] + real_result['away_score']
        
        goals_error = abs(predicted_goals - actual_goals)
        
        comparison['accuracy']['goals'] = {
            'predicted': round(predicted_goals, 2),
            'actual': actual_goals,
            'error': round(goals_error, 2),
            'error_pct': round((goals_error / max(actual_goals, 0.1)) * 100, 1)
        }
        
        if goals_error > 1.5:  # Erro > 1.5 gols
            comparison['discrepancies'].append({
                'market': 'Total Gols',
                'predicted': predicted_goals,
                'actual': actual_goals,
                'error': goals_error,
                'severity': 'HIGH' if goals_error > 2.5 else 'MEDIUM'
            })
        
        # 3. Comparar Over/Under 2.5
        predicted_over_25 = prognosis['probabilities'].get('over_25', 0) > 0.5
        actual_over_25 = actual_goals > 2.5
        
        comparison['accuracy']['over_under_25'] = {
            'predicted': 'Over 2.5' if predicted_over_25 else 'Under 2.5',
            'actual': 'Over 2.5' if actual_over_25 else 'Under 2.5',
            'correct': predicted_over_25 == actual_over_25,
            'probability': prognosis['probabilities'].get('over_25', 0) if predicted_over_25 else (1 - prognosis['probabilities'].get('over_25', 0.5))
        }
        
        if not comparison['accuracy']['over_under_25']['correct']:
            comparison['discrepancies'].append({
                'market': 'Over/Under 2.5',
                'predicted': comparison['accuracy']['over_under_25']['predicted'],
                'actual': comparison['accuracy']['over_under_25']['actual'],
                'confidence': comparison['accuracy']['over_under_25']['probability'],
                'severity': 'MEDIUM' if comparison['accuracy']['over_under_25']['probability'] > 0.6 else 'LOW'
            })
        
        # 4. Comparar BTTS (Ambos Marcam)
        predicted_btts = prognosis['probabilities'].get('btts', 0) > 0.5
        actual_btts = real_result['home_score'] > 0 and real_result['away_score'] > 0
        
        comparison['accuracy']['btts'] = {
            'predicted': 'Sim' if predicted_btts else 'Não',
            'actual': 'Sim' if actual_btts else 'Não',
            'correct': predicted_btts == actual_btts,
            'probability': prognosis['probabilities'].get('btts', 0) if predicted_btts else (1 - prognosis['probabilities'].get('btts', 0.5))
        }
        
        if not comparison['accuracy']['btts']['correct']:
            comparison['discrepancies'].append({
                'market': 'BTTS',
                'predicted': comparison['accuracy']['btts']['predicted'],
                'actual': comparison['accuracy']['btts']['actual'],
                'confidence': comparison['accuracy']['btts']['probability'],
                'severity': 'LOW'
            })
        
        # 5. Comparar Gols por Time
        comparison['accuracy']['home_goals'] = {
            'predicted': round(prognosis['expected_goals']['home'], 2),
            'actual': real_result['home_score'],
            'error': round(abs(prognosis['expected_goals']['home'] - real_result['home_score']), 2)
        }
        
        comparison['accuracy']['away_goals'] = {
            'predicted': round(prognosis['expected_goals']['away'], 2),
            'actual': real_result['away_score'],
            'error': round(abs(prognosis['expected_goals']['away'] - real_result['away_score']), 2)
        }
        
        # Atualizar estatísticas globais
        self._update_stats(comparison)
        
        return comparison
    
    def _get_predicted_result(self, probabilities: Dict) -> str:
        """Determina resultado previsto baseado em probabilidades"""
        max_prob = max(
            probabilities.get('home_win', 0),
            probabilities.get('draw', 0),
            probabilities.get('away_win', 0)
        )
        
        if probabilities.get('home_win', 0) == max_prob:
            return 'home'
        elif probabilities.get('away_win', 0) == max_prob:
            return 'away'
        else:
            return 'draw'
    
    def _get_actual_result(self, real_result: Dict) -> str:
        """Determina resultado real"""
        if real_result['home_score'] > real_result['away_score']:
            return 'home'
        elif real_result['away_score'] > real_result['home_score']:
            return 'away'
        else:
            return 'draw'
    
    def _update_stats(self, comparison: Dict):
        """Atualiza estatísticas globais de acurácia"""
        self.accuracy_stats['total_matches'] += 1
        
        if comparison['accuracy']['1x2']['correct']:
            self.accuracy_stats['correct_1x2'] += 1
        
        if comparison['accuracy']['over_under_25']['correct']:
            self.accuracy_stats['correct_over_under'] += 1
        
        if comparison['accuracy']['btts']['correct']:
            self.accuracy_stats['correct_btts'] += 1
    
    def get_accuracy_report(self) -> Dict:
        """
        Gera relatório de acurácia do modelo
        
        Returns:
            Dict com estatísticas de acurácia
        """
        total = self.accuracy_stats['total_matches']
        
        if total == 0:
            return {
                'total_matches': 0,
                'accuracy_1x2': 0,
                'accuracy_over_under': 0,
                'accuracy_btts': 0,
                'overall_accuracy': 0
            }
        
        return {
            'total_matches': total,
            'accuracy_1x2': round((self.accuracy_stats['correct_1x2'] / total) * 100, 1),
            'accuracy_over_under': round((self.accuracy_stats['correct_over_under'] / total) * 100, 1),
            'accuracy_btts': round((self.accuracy_stats['correct_btts'] / total) * 100, 1),
            'overall_accuracy': round(
                ((self.accuracy_stats['correct_1x2'] + 
                  self.accuracy_stats['correct_over_under'] + 
                  self.accuracy_stats['correct_btts']) / (total * 3)) * 100, 
                1
            )
        }
    
    def suggest_model_adjustments(self, comparisons: List[Dict]) -> List[Dict]:
        """
        Analisa discrepâncias e sugere ajustes no modelo
        
        Args:
            comparisons: Lista de comparações
            
        Returns:
            Lista de sugestões de ajuste
        """
        suggestions = []
        
        # Analisar padrões de erro
        total_home_goal_error = 0
        total_away_goal_error = 0
        high_discrepancies = []
        
        for comp in comparisons:
            total_home_goal_error += comp['accuracy']['home_goals']['error']
            total_away_goal_error += comp['accuracy']['away_goals']['error']
            
            # Coletar discrepâncias de alta severidade
            for disc in comp['discrepancies']:
                if disc['severity'] == 'HIGH':
                    high_discrepancies.append(disc)
        
        total_matches = len(comparisons)
        
        if total_matches == 0:
            return suggestions
        
        # Sugestão 1: Ajuste de xG (Expected Goals)
        avg_home_error = total_home_goal_error / total_matches
        avg_away_error = total_away_goal_error / total_matches
        
        if avg_home_error > 0.5:
            suggestions.append({
                'parameter': 'xG_home',
                'current_multiplier': 1.0,
                'suggested_multiplier': 1.0 - (avg_home_error * 0.1),
                'reason': f'Modelo superestima gols do mandante em média {avg_home_error:.2f} gols',
                'priority': 'MEDIUM'
            })
        
        if avg_away_error > 0.5:
            suggestions.append({
                'parameter': 'xG_away',
                'current_multiplier': 1.0,
                'suggested_multiplier': 1.0 - (avg_away_error * 0.1),
                'reason': f'Modelo superestima gols do visitante em média {avg_away_error:.2f} gols',
                'priority': 'MEDIUM'
            })
        
        # Sugestão 2: Ajuste de HFA (Home Field Advantage)
        home_wins_predicted = sum(1 for c in comparisons if c['accuracy']['1x2']['predicted'] == 'home')
        home_wins_actual = sum(1 for c in comparisons if c['accuracy']['1x2']['actual'] == 'home')
        
        if abs(home_wins_predicted - home_wins_actual) > total_matches * 0.2:
            current_hfa = 1.53  # Valor padrão
            if home_wins_predicted > home_wins_actual:
                suggested_hfa = current_hfa * 0.95
                reason = f'Modelo superestima vantagem do mandante ({home_wins_predicted} vs {home_wins_actual} vitórias)'
            else:
                suggested_hfa = current_hfa * 1.05
                reason = f'Modelo subestima vantagem do mandante ({home_wins_predicted} vs {home_wins_actual} vitórias)'
            
            suggestions.append({
                'parameter': 'HFA',
                'current_value': current_hfa,
                'suggested_value': round(suggested_hfa, 2),
                'reason': reason,
                'priority': 'HIGH'
            })
        
        # Sugestão 3: Calibração de probabilidades
        if len(high_discrepancies) > total_matches * 0.3:
            suggestions.append({
                'parameter': 'calibration',
                'action': 'increase_uncertainty',
                'reason': f'{len(high_discrepancies)} discrepâncias de alta confiança detectadas. Modelo pode estar overconfident.',
                'priority': 'HIGH'
            })
        
        return suggestions


# Exemplo de uso
if __name__ == "__main__":
    comparator = PrognosisComparator()
    
    # Exemplo de comparação
    prognosis = {
        'probabilities': {
            'home_win': 0.52,
            'draw': 0.28,
            'away_win': 0.20,
            'over_25': 0.58,
            'btts': 0.65
        },
        'expected_goals': {
            'home': 1.85,
            'away': 1.42,
            'total': 3.27
        }
    }
    
    real_result = {
        'home_score': 2,
        'away_score': 1
    }
    
    match_info = {
        'home_team': 'Flamengo',
        'away_team': 'Palmeiras',
        'date': '2025-10-15',
        'round': 30
    }
    
    comparison = comparator.compare_match(prognosis, real_result, match_info)
    
    print("📊 Comparação:")
    print(f"  1X2: {comparison['accuracy']['1x2']['correct']} ✅" if comparison['accuracy']['1x2']['correct'] else f"  1X2: {comparison['accuracy']['1x2']['correct']} ❌")
    print(f"  Gols: Previsto {comparison['accuracy']['goals']['predicted']}, Real {comparison['accuracy']['goals']['actual']}")
    print(f"  Erro: {comparison['accuracy']['goals']['error']} gols")
    
    if comparison['discrepancies']:
        print(f"\n⚠️ {len(comparison['discrepancies'])} discrepâncias detectadas")

