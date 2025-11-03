import numpy as np
from scipy.stats import poisson
from typing import Tuple, Dict

class DixonColesModel:
    """Modelo Dixon-Coles calibrado para Brasileirão"""
    
    def __init__(self, brasileirao_mode=True):
        """
        Args:
            brasileirao_mode: Se True, usa calibrações específicas do BR
        """
        if brasileirao_mode:
            self.hfa = 1.38  # Home Field Advantage (reduzido de 1.53)
            self.ava = 0.88  # Away disadvantage (ajustado de 0.85)
            self.league_avg_goals = 1.82
            self.league_avg_xg = 1.40
            self.correlation_k = 0.15  # Correlação positiva (era rho=-0.11, agora k positivo)
            self.home_advantage = 0.45  # Vantagem de casa adicional
            self.attack_strength = 1.15  # Força de ataque média calibrada
            self.defense_strength = 0.95  # Força de defesa média calibrada
        else:
            # Valores Premier League
            self.hfa = 1.18
            self.ava = 0.95
            self.league_avg_goals = 2.74
            self.league_avg_xg = 1.40
            self.correlation_k = 0.12  # Correlação positiva para PL
            self.home_advantage = 0.35
            self.attack_strength = 1.10
            self.defense_strength = 0.98
    
    def calculate_lambda(
        self,
        xg_for: float,
        xgc_against: float,
        is_home: bool,
        adjustments: Dict = None
    ) -> float:
        """
        Calcula lambda (taxa esperada de gols) com calibração integrada
        
        Args:
            xg_for: xG do time atacante
            xgc_against: xGC do time defensor
            is_home: Se o time é mandante
            adjustments: Ajustes contextuais (viagem, altitude, etc)
            
        Returns:
            Lambda calibrado
        """
        # Cálculo base com parâmetros de calibração integrados
        attack_strength = (xg_for / self.league_avg_xg) * self.attack_strength
        defense_weakness = (xgc_against / self.league_avg_xg) * self.defense_strength
        
        lambda_base = attack_strength * defense_weakness * self.league_avg_goals
        
        # Aplicar HFA/AVA com vantagem de casa adicional
        if is_home:
            lambda_adj = lambda_base * self.hfa
            lambda_adj += self.home_advantage
        else:
            lambda_adj = lambda_base * self.ava
        
        # Aplicar ajustes contextuais
        if adjustments:
            if 'travel_factor' in adjustments and not is_home:
                lambda_adj *= adjustments['travel_factor']
            
            if 'altitude_factor' in adjustments and not is_home:
                lambda_adj *= adjustments['altitude_factor']
            
            if 'classic_bonus' in adjustments and is_home:
                lambda_adj += adjustments['classic_bonus']
            
            if 'absences_impact' in adjustments:
                lambda_adj += adjustments['absences_impact']
        
        # Floor e cap
        lambda_adj = max(0.25, min(3.5, lambda_adj))
        
        return lambda_adj
    
    def bivariate_poisson(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula matriz de probabilidades de placares
        usando Poisson bivariada
        
        Returns:
            prob_matrix: Matriz 10x10 com P(i,j) para cada placar
            home_goals: Array de gols do mandante
            away_goals: Array de gols do visitante
        """
        max_goals = 10
        prob_matrix = np.zeros((max_goals, max_goals))
        
        # Componente comum (correlação positiva)
        # Usa correlation_k positivo para capturar dependência entre gols
        lambda_0 = self.correlation_k * min(lambda_home, lambda_away)
        lambda_1 = lambda_home - lambda_0
        lambda_2 = lambda_away - lambda_0
        
        for i in range(max_goals):
            for j in range(max_goals):
                # P(gols_home=i, gols_away=j)
                prob = (
                    poisson.pmf(i, lambda_1) *
                    poisson.pmf(j, lambda_2) *
                    poisson.pmf(min(i, j), lambda_0)
                )
                prob_matrix[i, j] = prob
        
        # Normalizar
        prob_matrix /= prob_matrix.sum()
        
        home_goals = np.arange(max_goals)
        away_goals = np.arange(max_goals)
        
        return prob_matrix, home_goals, away_goals
    
    def calculate_match_probabilities(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> Dict[str, float]:
        """
        Calcula probabilidades de vitória, empate, derrota
        
        Returns:
            Dict com probabilidades 1X2 e outros mercados
        """
        prob_matrix, _, _ = self.bivariate_poisson(lambda_home, lambda_away)
        
        # 1X2
        p_home_win = prob_matrix[np.triu_indices_from(prob_matrix, k=1)].sum()
        p_draw = np.diag(prob_matrix).sum()
        p_away_win = prob_matrix[np.tril_indices_from(prob_matrix, k=-1)].sum()
        
        # Total de gols
        total_goals_dist = np.zeros(20)
        for i in range(10):
            for j in range(10):
                if i + j < 20:
                    total_goals_dist[i + j] += prob_matrix[i, j]
        
        # Over/Under
        p_over_15 = total_goals_dist[2:].sum()
        p_over_25 = total_goals_dist[3:].sum()
        p_over_35 = total_goals_dist[4:].sum()
        
        # BTTS
        p_btts = 1 - prob_matrix[0, :].sum() - prob_matrix[:, 0].sum() + prob_matrix[0, 0]
        
        # Placar mais provável
        most_likely_score = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
        
        return {
            'p_home_win': p_home_win,
            'p_draw': p_draw,
            'p_away_win': p_away_win,
            'p_over_15': p_over_15,
            'p_over_25': p_over_25,
            'p_over_35': p_over_35,
            'p_btts': p_btts,
            'most_likely_score': most_likely_score,
            'expected_goals_home': lambda_home,
            'expected_goals_away': lambda_away,
        }
