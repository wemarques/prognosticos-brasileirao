import sys
import os
import logging

# Garantir que conseguimos importar os módulos
try:
    from models.dixon_coles import DixonColesModel
    from models.monte_carlo import MonteCarloSimulator
    from analysis.calibration import BrasileiraoCalibrator
except ModuleNotFoundError:
    # Fallback: adicionar diretório pai ao path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.dixon_coles import DixonColesModel
    from models.monte_carlo import MonteCarloSimulator
    from analysis.calibration import BrasileiraoCalibrator

from typing import Dict

# Configurar logging
logger = logging.getLogger(__name__)


def normalize_expected_goals(home_xg: float, away_xg: float) -> tuple:
    """
    Normaliza gols esperados com calibração melhorada para Brasileirão 2025
    
    Usa scaling + offset baseado em análise de dados históricos:
    - Scaling: 0.72 (redução de 28% em vez de 35% fixo)
    - Offset: -0.15 (ajuste para jogos defensivos)
    - Cap máximo: 3.2 (mais realista que 3.5)
    
    Args:
        home_xg: Expected goals do mandante
        away_xg: Expected goals do visitante
        
    Returns:
        Tupla (home_xg_normalized, away_xg_normalized)
    """
    scaling_factor = 0.72  # Reduz em 28% (mais conservador que 0.65)
    offset = -0.15  # Ajuste para baixo em jogos defensivos
    
    home_xg_normalized = (home_xg * scaling_factor) + offset
    away_xg_normalized = (away_xg * scaling_factor) + offset
    
    # Garantir valores mínimos e máximos realistas
    home_xg_normalized = max(0.3, min(home_xg_normalized, 3.2))
    away_xg_normalized = max(0.3, min(away_xg_normalized, 3.2))
    
    logger.debug(f"Normalized xG: {home_xg:.2f} -> {home_xg_normalized:.2f}, {away_xg:.2f} -> {away_xg_normalized:.2f}")
    
    return home_xg_normalized, away_xg_normalized


def adjust_probabilities_for_defensive_games(home_xg: float, away_xg: float, home_win: float, draw: float, away_win: float) -> tuple:
    """
    Ajusta probabilidades para jogos defensivos (baixo xG)
    
    Com correlação positiva no Dixon-Coles, o ajuste de empates é menor.
    Anteriormente era +35%, agora é +20% pois a correlação já captura parte do efeito.
    
    Args:
        home_xg: Expected goals do mandante
        away_xg: Expected goals do visitante
        home_win: Probabilidade de vitória do mandante
        draw: Probabilidade de empate
        away_win: Probabilidade de vitória do visitante
        
    Returns:
        Tupla (home_win_adj, draw_adj, away_win_adj) normalizada
    """
    if home_xg < 1.0 and away_xg < 1.0:
        logger.debug(f"Defensive game detected (xG < 1.0). Adjusting draw probability.")
        
        draw_adj = draw * 1.20
        
        home_win_adj = home_win * 0.90
        away_win_adj = away_win * 0.90
    else:
        home_win_adj = home_win
        draw_adj = draw
        away_win_adj = away_win
    
    total = home_win_adj + draw_adj + away_win_adj
    home_win_adj = home_win_adj / total
    draw_adj = draw_adj / total
    away_win_adj = away_win_adj / total
    
    logger.debug(f"Adjusted probabilities: H={home_win_adj:.1%} D={draw_adj:.1%} A={away_win_adj:.1%}")
    
    return home_win_adj, draw_adj, away_win_adj


def get_corners_prediction(lambda_corners: float, simulator) -> Dict:
    """
    Prediz escanteios com fallback robusto
    
    Args:
        lambda_corners: Lambda para simulação de escanteios
        simulator: Instância do MonteCarloSimulator
        
    Returns:
        Dict com probabilidades de escanteios
    """
    try:
        corners = simulator.simulate_corners(lambda_corners)
        
        if corners is None or corners.get('p_over_85', 0) == 0:
            logger.warning("Corners prediction returned invalid values, using fallback")
            corners = {
                'p_over_65': 0.65,
                'p_over_75': 0.55,
                'p_over_85': 0.45,
                'p_over_95': 0.25,
                'avg_corners': 8.5,
            }
    except Exception as e:
        logger.error(f"Error predicting corners: {e}, using fallback")
        # Fallback em caso de erro
        corners = {
            'p_over_65': 0.65,
            'p_over_75': 0.55,
            'p_over_85': 0.45,
            'p_over_95': 0.25,
            'avg_corners': 8.5,
        }
    
    return corners


def get_cards_prediction(lambda_cards_home: float, lambda_cards_away: float, simulator) -> Dict:
    """
    Prediz cartões com fallback robusto
    
    Args:
        lambda_cards_home: Lambda de cartões do mandante
        lambda_cards_away: Lambda de cartões do visitante
        simulator: Instância do MonteCarloSimulator
        
    Returns:
        Dict com probabilidades de cartões
    """
    try:
        cards = simulator.simulate_cards(lambda_cards_home, lambda_cards_away)
        
        if cards is None or cards.get('p_over_25', 0) == 0:
            logger.warning("Cards prediction returned invalid values, using fallback")
            cards = {
                'p_over_25': 0.55,
                'p_over_35': 0.35,
                'p_over_45': 0.15,
                'p_over_55': 0.05,
                'avg_cards': 3.5,
            }
    except Exception as e:
        logger.error(f"Error predicting cards: {e}, using fallback")
        # Fallback em caso de erro
        cards = {
            'p_over_25': 0.55,
            'p_over_35': 0.35,
            'p_over_45': 0.15,
            'p_over_55': 0.05,
            'avg_cards': 3.5,
        }
    
    return cards


class PrognosisCalculator:
    """Classe principal que calcula prognósticos completos"""
    
    def __init__(self, brasileirao_mode=True):
        self.model = DixonColesModel(brasileirao_mode=brasileirao_mode)
        self.simulator = MonteCarloSimulator(n_simulations=50000)
        self.calibrator = BrasileiraoCalibrator()
        self.brasileirao_mode = brasileirao_mode
    
    def calculate_full_prognosis(
        self,
        home_stats: Dict,
        away_stats: Dict,
        context: Dict
    ) -> Dict:
        """
        Calcula prognóstico completo de uma partida
        
        Args:
            home_stats: Estatísticas do mandante
            away_stats: Estatísticas do visitante
            context: Contexto (distância, altitude, tipo de jogo, etc)
            
        Returns:
            Dict completo com todas análises e probabilidades
        """
        logger.info(f"Iniciando cálculo de prognóstico")
        
        # 1. Calcular lambdas de gols
        adjustments_home = {
            'classic_bonus': self.calibrator.get_classic_bonus(
                context.get('match_type', 'normal')
            ),
            'absences_impact': context.get('home_absences_impact', 0),
        }
        
        adjustments_away = {
            'travel_factor': self.calibrator.get_travel_factor(
                context.get('distance_km', 0)
            ),
            'altitude_factor': self.calibrator.get_altitude_factor(
                context.get('altitude_m', 0)
            ),
            'absences_impact': context.get('away_absences_impact', 0),
        }
        
        lambda_home = self.model.calculate_lambda(
            xg_for=home_stats['xg_for_home'],
            xgc_against=away_stats['xgc_against_away'],
            is_home=True,
            adjustments=adjustments_home
        )
        
        lambda_away = self.model.calculate_lambda(
            xg_for=away_stats['xg_for_away'],
            xgc_against=home_stats['xgc_against_home'],
            is_home=False,
            adjustments=adjustments_away
        )
        
        logger.debug(f"Initial lambdas: home={lambda_home:.2f}, away={lambda_away:.2f}")
        
        lambda_home_normalized, lambda_away_normalized = normalize_expected_goals(lambda_home, lambda_away)
        
        # 3. Calcular probabilidades (Dixon-Coles)
        probs = self.model.calculate_match_probabilities(lambda_home_normalized, lambda_away_normalized)
        
        # 4. Simular com Monte Carlo usando mesma correlação do modelo
        mc_results = self.simulator.simulate_match(
            lambda_home_normalized, 
            lambda_away_normalized,
            correlation_k=self.model.correlation_k
        )
        
        logger.debug(f"Initial probabilities: H={mc_results['p_home_wins']:.1%} D={mc_results['p_draws']:.1%} A={mc_results['p_away_wins']:.1%}")
        
        home_win_adj, draw_adj, away_win_adj = adjust_probabilities_for_defensive_games(
            lambda_home_normalized,
            lambda_away_normalized,
            mc_results['p_home_wins'],
            mc_results['p_draws'],
            mc_results['p_away_wins']
        )
        
        # 6. Calibrar para Brasileirão
        probs['p_btts_calibrated'] = self.calibrator.calibrate_btts(
            mc_results['p_btts']
        )
        probs['p_over_25_calibrated'] = self.calibrator.calibrate_over25(
            mc_results['p_over_25']
        )
        
        lambda_cards_home = context.get('lambda_cards_home', 1.5)
        lambda_cards_away = context.get('lambda_cards_away', 1.5)
        
        cards_results = get_cards_prediction(lambda_cards_home, lambda_cards_away, self.simulator)
        cards_results = self.calibrator.calibrate_cards(cards_results)
        
        lambda_corners = context.get('lambda_corners', 6.76)
        corners_results = get_corners_prediction(lambda_corners, self.simulator)
        corners_results = self.calibrator.calibrate_corners(corners_results)
        
        logger.info(f"Prognóstico calculado com sucesso")
        
        # 9. Compilar resultado final
        return {
            'lambdas': {
                'home': lambda_home_normalized,
                'away': lambda_away_normalized,
            },
            'probabilities': {
                'home_win': home_win_adj,
                'draw': draw_adj,
                'away_win': away_win_adj,
                'btts': probs['p_btts_calibrated'],
                'over_15': mc_results['p_over_15'],
                'over_25': probs['p_over_25_calibrated'],
                'over_35': mc_results['p_over_35'],
            },
            'cards': cards_results,
            'corners': corners_results,
            'top_scores': mc_results['top_5_scores'],
            'expected_goals': {
                'home': mc_results['avg_goals_home'],
                'away': mc_results['avg_goals_away'],
                'total': mc_results['avg_goals_home'] + mc_results['avg_goals_away'],
            },
        }
