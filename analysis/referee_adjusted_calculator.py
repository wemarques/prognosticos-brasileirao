"""
Calculador de prognósticos de cartões ajustado por árbitro
"""
from typing import Dict, Any
import math
from utils.referee_data import (
    get_leniency_factor,
    get_avg_cards,
    classify_referee_style,
    LEAGUE_REFEREE_STATS
)


class RefereeAdjustedCalculator:
    """Calcula prognósticos de cartões considerando o árbitro"""
    
    def __init__(self, league: str = 'brasileirao'):
        self.league = league
        self.league_avg_cards = LEAGUE_REFEREE_STATS[league]['avg_cards_per_match']
        self.league_avg_yellow = LEAGUE_REFEREE_STATS[league]['avg_yellow_cards']
        self.league_avg_red = LEAGUE_REFEREE_STATS[league]['avg_red_cards']
    
    def calculate_cards_with_referee(
        self,
        home_team_stats: Dict,
        away_team_stats: Dict,
        referee_key: str,
        competition: str = 'brasileirao',
        season: int = 2024
    ) -> Dict[str, Any]:
        """
        Calcula prognóstico de cartões ajustado pelo árbitro
        
        Args:
            home_team_stats: Estatísticas do time mandante
            away_team_stats: Estatísticas do time visitante
            referee_key: Chave do árbitro (ex: 'anderson_daronco')
            competition: Competição (brasileirao, copa_do_brasil, etc)
            season: Temporada
            
        Returns:
            Dict com prognósticos ajustados
        """
        # 1. Calcular base de cartões (sem árbitro)
        base_cards = self._calculate_base_cards(home_team_stats, away_team_stats)
        
        # 2. Obter fator de leniência do árbitro
        leniency_factor = get_leniency_factor(referee_key, competition, season)
        
        # 3. Ajustar prognóstico
        adjusted_cards = base_cards * leniency_factor
        
        # 4. Calcular probabilidades
        probs = self._calculate_probabilities(adjusted_cards)
        
        # 5. Classificar estilo do árbitro
        referee_style = classify_referee_style(leniency_factor)
        
        # 6. Obter média de cartões do árbitro
        referee_avg_cards = get_avg_cards(referee_key, competition, season)
        
        return {
            'base_cards': round(base_cards, 2),
            'leniency_factor': round(leniency_factor, 3),
            'adjusted_cards': round(adjusted_cards, 2),
            'over_4_5': round(probs['over_4_5'], 3),
            'over_3_5': round(probs['over_3_5'], 3),
            'over_2_5': round(probs['over_2_5'], 3),
            'under_4_5': round(1 - probs['over_4_5'], 3),
            'under_3_5': round(1 - probs['over_3_5'], 3),
            'under_2_5': round(1 - probs['over_2_5'], 3),
            'referee_info': {
                'key': referee_key,
                'avg_cards': round(referee_avg_cards, 2),
                'leniency': round(leniency_factor, 3),
                'style': referee_style,
                'matches_total': self._get_referee_matches(referee_key)
            },
            'confidence': self._calculate_confidence(leniency_factor)
        }
    
    def _calculate_base_cards(self, home_stats: Dict, away_stats: Dict) -> float:
        """Calcula base de cartões sem considerar árbitro"""
        # Cartões do time mandante
        home_cards_for = home_stats.get('cards_for', 0)
        home_cards_against = home_stats.get('cards_against', 0)
        home_avg = (home_cards_for + home_cards_against) / 2 if (home_cards_for + home_cards_against) > 0 else 0
        
        # Cartões do time visitante
        away_cards_for = away_stats.get('cards_for', 0)
        away_cards_against = away_stats.get('cards_against', 0)
        away_avg = (away_cards_for + away_cards_against) / 2 if (away_cards_for + away_cards_against) > 0 else 0
        
        # Média dos dois times
        avg_cards = (home_avg + away_avg) / 2
        
        # Se não houver dados, usar média da liga
        return avg_cards if avg_cards > 0 else self.league_avg_cards
    
    def _calculate_probabilities(self, expected_cards: float) -> Dict[str, float]:
        """
        Calcula probabilidades usando distribuição de Poisson
        
        Args:
            expected_cards: Número esperado de cartões
            
        Returns:
            Dict com probabilidades de over/under
        """
        # Usar distribuição de Poisson
        # P(X > k) = 1 - P(X <= k)
        
        over_4_5 = 1 - self._poisson_cdf(4, expected_cards)
        over_3_5 = 1 - self._poisson_cdf(3, expected_cards)
        over_2_5 = 1 - self._poisson_cdf(2, expected_cards)
        
        return {
            'over_4_5': over_4_5,
            'over_3_5': over_3_5,
            'over_2_5': over_2_5
        }
    
    def _poisson_cdf(self, k: int, lambda_param: float) -> float:
        """
        Calcula CDF da distribuição de Poisson
        P(X <= k) onde X ~ Poisson(lambda)
        
        Args:
            k: Número de eventos
            lambda_param: Parâmetro lambda (média)
            
        Returns:
            Probabilidade acumulada
        """
        cdf = 0
        for i in range(k + 1):
            cdf += (lambda_param ** i * math.exp(-lambda_param)) / math.factorial(i)
        return cdf
    
    def _calculate_confidence(self, leniency_factor: float) -> str:
        """
        Calcula nível de confiança baseado no fator de leniência
        
        Args:
            leniency_factor: Fator de leniência do árbitro
            
        Returns:
            Nível de confiança (Alta, Média, Baixa)
        """
        # Quanto mais próximo de 1.0, maior a confiança
        deviation = abs(leniency_factor - 1.0)
        
        if deviation < 0.05:
            return "🟢 Alta"
        elif deviation < 0.12:
            return "🟡 Média"
        else:
            return "🔴 Baixa"
    
    def _get_referee_matches(self, referee_key: str) -> int:
        """Obtém número de matches do árbitro"""
        from utils.referee_data import REFEREE_STATS
        referee = REFEREE_STATS.get(referee_key, {})
        return referee.get('matches_total', 0)
    
    def compare_referees(
        self,
        home_team_stats: Dict,
        away_team_stats: Dict,
        referee_keys: list,
        competition: str = 'brasileirao'
    ) -> Dict[str, Any]:
        """
        Compara prognósticos de cartões para diferentes árbitros
        
        Args:
            home_team_stats: Estatísticas do time mandante
            away_team_stats: Estatísticas do time visitante
            referee_keys: Lista de chaves de árbitros
            competition: Competição
            
        Returns:
            Dict com comparação de prognósticos
        """
        comparisons = {}
        
        for referee_key in referee_keys:
            result = self.calculate_cards_with_referee(
                home_team_stats,
                away_team_stats,
                referee_key,
                competition
            )
            comparisons[referee_key] = result
        
        # Encontrar árbitro com maior e menor expectativa de cartões
        min_referee = min(comparisons.items(), key=lambda x: x[1]['adjusted_cards'])
        max_referee = max(comparisons.items(), key=lambda x: x[1]['adjusted_cards'])
        
        return {
            'comparisons': comparisons,
            'min_referee': {
                'key': min_referee[0],
                'cards': min_referee[1]['adjusted_cards'],
                'style': min_referee[1]['referee_info']['style']
            },
            'max_referee': {
                'key': max_referee[0],
                'cards': max_referee[1]['adjusted_cards'],
                'style': max_referee[1]['referee_info']['style']
            },
            'difference': round(max_referee[1]['adjusted_cards'] - min_referee[1]['adjusted_cards'], 2)
        }


# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
    home_stats = {
        'cards_for': 15,
        'cards_against': 12
    }
    
    away_stats = {
        'cards_for': 14,
        'cards_against': 13
    }
    
    # Calcular com árbitro rigoroso
    calculator = RefereeAdjustedCalculator()
    
    result_rigoroso = calculator.calculate_cards_with_referee(
        home_stats,
        away_stats,
        'anderson_daronco',
        'brasileirao'
    )
    
    print("Árbitro Rigoroso (Anderson Daronco):")
    print(f"  Cartões esperados: {result_rigoroso['adjusted_cards']}")
    print(f"  Over 4.5: {result_rigoroso['over_4_5']:.1%}")
    print(f"  Over 3.5: {result_rigoroso['over_3_5']:.1%}")
    print()
    
    # Calcular com árbitro leniente
    result_leniente = calculator.calculate_cards_with_referee(
        home_stats,
        away_stats,
        'raphael_claus',
        'brasileirao'
    )
    
    print("Árbitro Leniente (Raphael Claus):")
    print(f"  Cartões esperados: {result_leniente['adjusted_cards']}")
    print(f"  Over 4.5: {result_leniente['over_4_5']:.1%}")
    print(f"  Over 3.5: {result_leniente['over_3_5']:.1%}")
    print()
    
    # Comparar árbitros
    comparison = calculator.compare_referees(
        home_stats,
        away_stats,
        ['anderson_daronco', 'raphael_claus', 'wilton_pereira_sampaio']
    )
    
    print("Comparação de Árbitros:")
    print(f"  Menor expectativa: {comparison['min_referee']['key']} ({comparison['min_referee']['cards']} cartões)")
    print(f"  Maior expectativa: {comparison['max_referee']['key']} ({comparison['max_referee']['cards']} cartões)")
    print(f"  Diferença: {comparison['difference']} cartões")