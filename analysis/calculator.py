from models.dixon_coles import DixonColesModel
from models.monte_carlo import MonteCarloSimulator
from analysis.calibration import BrasileiraoCalibrator
from typing import Dict

class PrognosisCalculator:
    """Classe principal que calcula prognósticos completos"""
    
    def __init__(self, brasileirao_mode=True):
        self.model = DixonColesModel(brasileirao_mode=brasileirao_mode)
        self.simulator = MonteCarloSimulator(n_simulations=50000)
        self.calibrator = BrasileiraoCalibrator()
    
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
        
        # 2. Calcular probabilidades (Dixon-Coles)
        probs = self.model.calculate_match_probabilities(lambda_home, lambda_away)
        
        # 3. Simular com Monte Carlo
        mc_results = self.simulator.simulate_match(lambda_home, lambda_away)
        
        # 4. Calibrar para Brasileirão
        probs['p_btts_calibrated'] = self.calibrator.calibrate_btts(
            mc_results['p_btts']
        )
        probs['p_over_25_calibrated'] = self.calibrator.calibrate_over25(
            mc_results['p_over_25']
        )
        
        # 5. Cartões
        lambda_cards_home = context.get('lambda_cards_home', 1.5)
        lambda_cards_away = context.get('lambda_cards_away', 1.5)
        
        cards_results = self.simulator.simulate_cards(
            lambda_cards_home, lambda_cards_away
        )
        cards_results = self.calibrator.calibrate_cards(cards_results)
        
        # 6. Escanteios
        lambda_corners = context.get('lambda_corners', 6.76)
        corners_results = self.simulator.simulate_corners(lambda_corners)
        corners_results = self.calibrator.calibrate_corners(corners_results)
        
        # 7. Compilar resultado final
        return {
            'lambdas': {
                'home': lambda_home,
                'away': lambda_away,
            },
            'probabilities': {
                'home_win': mc_results['p_home_wins'],
                'draw': mc_results['p_draws'],
                'away_win': mc_results['p_away_wins'],
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
