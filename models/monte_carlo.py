import numpy as np
from typing import Dict, List, Tuple

class MonteCarloSimulator:
    """Simula 50.000 jogos para gerar distribuições de probabilidade"""
    
    def __init__(self, n_simulations: int = 50000):
        self.n_simulations = n_simulations
    
    def simulate_match(
        self,
        lambda_home: float,
        lambda_away: float,
        correlation_k: float = 0.15
    ) -> Dict:
        """
        Simula N jogos usando Poisson bivariada com correlação positiva
        
        Args:
            lambda_home: Taxa esperada de gols do mandante
            lambda_away: Taxa esperada de gols do visitante
            correlation_k: Coeficiente de correlação positivo (padrão 0.15)
        
        Returns:
            Dict com estatísticas das simulações
        """
        # Componente comum (correlação positiva)
        lambda_0 = correlation_k * min(lambda_home, lambda_away)
        lambda_h = lambda_home - lambda_0
        lambda_a = lambda_away - lambda_0
        
        # Gerar gols
        goals_home_ind = np.random.poisson(lambda_h, self.n_simulations)
        goals_away_ind = np.random.poisson(lambda_a, self.n_simulations)
        goals_common = np.random.poisson(lambda_0, self.n_simulations)
        
        goals_home = goals_home_ind + goals_common
        goals_away = goals_away_ind + goals_common
        
        # Calcular estatísticas
        total_goals = goals_home + goals_away
        
        results = {
            'home_wins': (goals_home > goals_away).sum(),
            'draws': (goals_home == goals_away).sum(),
            'away_wins': (goals_home < goals_away).sum(),
            'btts': ((goals_home > 0) & (goals_away > 0)).sum(),
            'over_15': (total_goals > 1.5).sum(),
            'over_25': (total_goals > 2.5).sum(),
            'over_35': (total_goals > 3.5).sum(),
            'over_45': (total_goals > 4.5).sum(),
            'avg_goals_home': goals_home.mean(),
            'avg_goals_away': goals_away.mean(),
        }
        
        # Converter para probabilidades
        for key in ['home_wins', 'draws', 'away_wins', 'btts', 
                    'over_15', 'over_25', 'over_35', 'over_45']:
            results[f'p_{key}'] = results[key] / self.n_simulations
        
        # Top 5 placares
        scores = list(zip(goals_home, goals_away))
        from collections import Counter
        score_counts = Counter(scores)
        top_scores = score_counts.most_common(5)
        results['top_5_scores'] = [
            {'score': f"{s[0]}-{s[1]}", 'probability': count / self.n_simulations}
            for s, count in top_scores
        ]
        
        return results
    
    def simulate_cards(
        self,
        lambda_cards_home: float,
        lambda_cards_away: float
    ) -> Dict:
        """Simula cartões"""
        cards_home = np.random.poisson(lambda_cards_home, self.n_simulations)
        cards_away = np.random.poisson(lambda_cards_away, self.n_simulations)
        total_cards = cards_home + cards_away
        
        return {
            'p_over_25': (total_cards > 2.5).sum() / self.n_simulations,
            'p_over_35': (total_cards > 3.5).sum() / self.n_simulations,
            'p_over_45': (total_cards > 4.5).sum() / self.n_simulations,
            'p_over_55': (total_cards > 5.5).sum() / self.n_simulations,
            'avg_cards': total_cards.mean(),
        }
    
    def simulate_corners(
        self,
        lambda_corners: float
    ) -> Dict:
        """Simula escanteios"""
        corners = np.random.poisson(lambda_corners, self.n_simulations)
        
        return {
            'p_over_65': (corners > 6.5).sum() / self.n_simulations,
            'p_over_75': (corners > 7.5).sum() / self.n_simulations,
            'p_over_85': (corners > 8.5).sum() / self.n_simulations,
            'p_over_95': (corners > 9.5).sum() / self.n_simulations,
            'p_over_105': (corners > 10.5).sum() / self.n_simulations,
            'avg_corners': corners.mean(),
        }
