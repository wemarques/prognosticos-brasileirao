import numpy as np
from scipy.stats import poisson
from typing import Tuple, Dict

class DixonColesModel:
    """Modelo Dixon-Coles calibrado para Brasileirão"""
    
    def __init__(self, brasileirao_mode=True):
        """
        Initialize Dixon-Coles model with calibrated parameters.
        
        Args:
            brasileirao_mode: If True, use parameters calibrated for Brasileirão Série A
        """
        if brasileirao_mode:
            self.hfa = 1.35
            self.ava = 0.92
            self.league_avg_goals = 1.65
            self.rho = -0.12
            self.league_avg_xg = 1.40
            self.correlation_k = 0.15
            self.home_advantage = 0.30
            self.attack_strength = 1.10
            self.defense_strength = 0.95
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info("🎯 Dixon-Coles initialized for Brasileirão with calibrated parameters")
            logger.info(f"  HFA: {self.hfa}, AVA: {self.ava}, Avg Goals: {self.league_avg_goals}")
        else:
            self.hfa = 1.18
            self.ava = 0.95
            self.league_avg_goals = 2.74
            self.rho = -0.15
            self.league_avg_xg = 1.40
            self.correlation_k = 0.12
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
        Calculate expected goals (lambda) for a team.
        Calibrated for realistic Brasileirão predictions.
        
        Args:
            xg_for: xG do time atacante
            xgc_against: xGC do time defensor
            is_home: Se o time é mandante
            adjustments: Ajustes contextuais (viagem, altitude, etc)
            
        Returns:
            Lambda calibrado
        """
        attack_strength = (xg_for / self.league_avg_xg) * self.attack_strength
        defense_weakness = (xgc_against / self.league_avg_xg) * self.defense_strength
        
        lambda_base = attack_strength * defense_weakness * self.league_avg_goals
        
        if is_home:
            lambda_adj = lambda_base * self.hfa
            lambda_adj += self.home_advantage
        else:
            lambda_adj = lambda_base * self.ava
        
        if adjustments:
            if 'travel_factor' in adjustments and not is_home:
                lambda_adj *= adjustments['travel_factor']
            
            if 'altitude_factor' in adjustments and not is_home:
                lambda_adj *= adjustments['altitude_factor']
            
            if 'classic_bonus' in adjustments and is_home:
                lambda_adj += adjustments['classic_bonus']
            
            if 'absences_impact' in adjustments:
                lambda_adj += adjustments['absences_impact']
        
        lambda_adj = max(0.3, min(lambda_adj, 3.5))
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Lambda calculated: {lambda_adj:.2f} (is_home={is_home})")
        
        return lambda_adj
    
    def calculate_lambdas(self, home_attack, home_defense, away_attack, away_defense, venue="HOME"):
        """
        Calculate expected goals (lambda) for home and away teams.
        Calibrated for realistic Brasileirão predictions.
        """
        home_attack_norm = home_attack / self.league_avg_goals
        home_defense_norm = home_defense / self.league_avg_goals
        away_attack_norm = away_attack / self.league_avg_goals
        away_defense_norm = away_defense / self.league_avg_goals
        
        if venue == "HOME":
            lambda_home = self.league_avg_goals * home_attack_norm * away_defense_norm * self.hfa
            lambda_away = self.league_avg_goals * away_attack_norm * home_defense_norm * self.ava
        else:
            lambda_home = self.league_avg_goals * home_attack_norm * away_defense_norm
            lambda_away = self.league_avg_goals * away_attack_norm * home_defense_norm
        
        lambda_home = max(0.3, min(lambda_home, 3.5))
        lambda_away = max(0.3, min(lambda_away, 3.5))
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Lambdas calculados: Home={lambda_home:.2f}, Away={lambda_away:.2f}, Total={lambda_home+lambda_away:.2f}")
        
        return lambda_home, lambda_away
    
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
    
    def adjust_draw_probability(self, prob_home, prob_draw, prob_away, lambda_home, lambda_away):
        """
        Adjust draw probability for defensive games.
        
        Args:
            prob_home: Home win probability
            prob_draw: Draw probability
            prob_away: Away win probability
            lambda_home: Home expected goals
            lambda_away: Away expected goals
        
        Returns:
            tuple: Adjusted (prob_home, prob_draw, prob_away) that sum to 1.0
        """
        import logging
        logger = logging.getLogger(__name__)
        
        is_defensive = lambda_home < 1.2 and lambda_away < 1.2
        
        if is_defensive:
            draw_boost = 0.10
            
            logger.info(f"🛡️ Jogo defensivo detectado (λH={lambda_home:.2f}, λA={lambda_away:.2f})")
            logger.info(f"   Empate antes: {prob_draw:.1%}")
            
            new_draw = min(prob_draw + draw_boost, 0.40)
            
            diff = new_draw - prob_draw
            if diff > 0:
                total_win_prob = prob_home + prob_away
                if total_win_prob > 0:
                    ratio_home = prob_home / total_win_prob
                    ratio_away = prob_away / total_win_prob
                    
                    new_home = prob_home - (diff * ratio_home)
                    new_away = prob_away - (diff * ratio_away)
                else:
                    new_home = prob_home
                    new_away = prob_away
            else:
                new_home = prob_home
                new_away = prob_away
            
            logger.info(f"   Empate depois: {new_draw:.1%} (+{diff:.1%})")
            
            total = new_home + new_draw + new_away
            new_home /= total
            new_draw /= total
            new_away /= total
            
            return new_home, new_draw, new_away
        else:
            logger.info(f"⚔️ Jogo ofensivo (λH={lambda_home:.2f}, λA={lambda_away:.2f}) - sem ajuste de empate")
            return prob_home, prob_draw, prob_away
    
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
        
        p_home_win, p_draw, p_away_win = self.adjust_draw_probability(
            p_home_win, p_draw, p_away_win, lambda_home, lambda_away
        )
        
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
