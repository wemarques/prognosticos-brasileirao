"""
Extensão do DataProcessor com suporte a análise de árbitros
"""
from typing import Dict, Any
from data.processor import DataProcessor
from analysis.referee_adjusted_calculator import RefereeAdjustedCalculator
from utils.timezone_utils import TimezoneConverter


class DataProcessorWithReferee(DataProcessor):
    """DataProcessor estendido com análise de árbitros"""
    
    def __init__(self):
        super().__init__()
        self.referee_calculator = RefereeAdjustedCalculator()
    
    def process_match_with_referee_and_timezone(
        self,
        home_stats: Dict,
        away_stats: Dict,
        h2h_data: Dict,
        home_team_name: str,
        away_team_name: str,
        referee_key: str = None,
        utc_timestamp: int = None,
        competition: str = 'brasileirao'
    ) -> Dict[str, Any]:
        """
        Processa dados completos de um match incluindo árbitro e timezone
        
        Args:
            home_stats: Estatísticas do time mandante
            away_stats: Estatísticas do time visitante
            h2h_data: Dados de confrontos diretos
            home_team_name: Nome do time mandante
            away_team_name: Nome do time visitante
            referee_key: Chave do árbitro (ex: 'anderson_daronco')
            utc_timestamp: Timestamp UTC do match
            competition: Competição
            
        Returns:
            Dict com dados processados incluindo análise de árbitro e horário
        """
        # 1. Processar dados básicos
        basic_data = self.process_match_data(
            home_stats,
            away_stats,
            h2h_data,
            home_team_name,
            away_team_name
        )
        
        # 2. Adicionar análise de árbitro se disponível
        if referee_key:
            referee_analysis = self.referee_calculator.calculate_cards_with_referee(
                home_stats,
                away_stats,
                referee_key,
                competition
            )
            basic_data['referee_analysis'] = referee_analysis
        
        # 3. Adicionar informações de timezone se disponível
        if utc_timestamp:
            basic_data['match_time'] = {
                'utc_timestamp': utc_timestamp,
                'brasilia_time': TimezoneConverter.format_brasilia_full(utc_timestamp),
                'brasilia_time_short': TimezoneConverter.format_brasilia_time_short(utc_timestamp),
                'status': TimezoneConverter.get_match_status(utc_timestamp),
                'time_until': TimezoneConverter.get_time_until_match(utc_timestamp),
                'weekday': TimezoneConverter.get_weekday_name(utc_timestamp),
                'is_today': TimezoneConverter.is_match_today(utc_timestamp),
                'is_tomorrow': TimezoneConverter.is_match_tomorrow(utc_timestamp)
            }
        
        return basic_data
    
    def process_round_with_referees(
        self,
        matches: list,
        competition: str = 'brasileirao'
    ) -> Dict[str, Any]:
        """
        Processa todos os matches de uma rodada com análise de árbitros
        
        Args:
            matches: Lista de matches com dados completos
            competition: Competição
            
        Returns:
            Dict com resultados processados
        """
        results = {
            'successful': 0,
            'failed': 0,
            'matches': [],
            'errors': []
        }
        
        for match in matches:
            try:
                # Extrair dados do match
                home_stats = match.get('home_stats', {})
                away_stats = match.get('away_stats', {})
                h2h_data = match.get('h2h_data', {})
                home_team = match.get('home_team', '')
                away_team = match.get('away_team', '')
                referee_key = match.get('referee_key')
                utc_timestamp = match.get('utc_timestamp')
                
                # Processar match
                processed = self.process_match_with_referee_and_timezone(
                    home_stats,
                    away_stats,
                    h2h_data,
                    home_team,
                    away_team,
                    referee_key,
                    utc_timestamp,
                    competition
                )
                
                results['matches'].append(processed)
                results['successful'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'match': f"{match.get('home_team')} vs {match.get('away_team')}",
                    'error': str(e)
                })
                results['failed'] += 1
        
        return results
    
    def compare_referees_for_match(
        self,
        home_stats: Dict,
        away_stats: Dict,
        referee_keys: list,
        competition: str = 'brasileirao'
    ) -> Dict[str, Any]:
        """
        Compara prognósticos de cartões para diferentes árbitros
        
        Args:
            home_stats: Estatísticas do time mandante
            away_stats: Estatísticas do time visitante
            referee_keys: Lista de chaves de árbitros
            competition: Competição
            
        Returns:
            Comparação de prognósticos
        """
        return self.referee_calculator.compare_referees(
            home_stats,
            away_stats,
            referee_keys,
            competition
        )


# Exemplo de uso
if __name__ == "__main__":
    import time
    
    # Dados de exemplo
    home_stats = {
        'cards_for': 15,
        'cards_against': 12,
        'goals_for': 25,
        'goals_against': 18
    }
    
    away_stats = {
        'cards_for': 14,
        'cards_against': 13,
        'goals_for': 22,
        'goals_against': 20
    }
    
    h2h_data = {}
    
    # Timestamp de exemplo (próximo dia)
    utc_timestamp = int(time.time()) + 86400
    
    # Processar match com árbitro e timezone
    processor = DataProcessorWithReferee()
    
    result = processor.process_match_with_referee_and_timezone(
        home_stats,
        away_stats,
        h2h_data,
        'Flamengo',
        'Vasco',
        referee_key='anderson_daronco',
        utc_timestamp=utc_timestamp,
        competition='brasileirao'
    )
    
    print("Match Processado com Árbitro e Timezone:")
    print(f"  Times: {result.get('home_team')} vs {result.get('away_team')}")
    print(f"  Horário Brasília: {result['match_time']['brasilia_time']}")
    print(f"  Status: {result['match_time']['status']}")
    print(f"  Tempo até o match: {result['match_time']['time_until']}")
    print()
    
    if 'referee_analysis' in result:
        ref_info = result['referee_analysis']['referee_info']
        print(f"  Árbitro: {ref_info['key']}")
        print(f"  Estilo: {ref_info['style']}")
        print(f"  Cartões esperados: {result['referee_analysis']['adjusted_cards']}")
        print(f"  Over 4.5: {result['referee_analysis']['over_4_5']:.1%}")