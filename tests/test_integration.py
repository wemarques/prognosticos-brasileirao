"""
Testes de integração completos
Testa fluxo completo de processamento multi-liga
"""
import pytest
import time
from data.multi_league_processor import MultiLeagueProcessor
from analysis.batch_processor import BatchMatchProcessor
from utils.cache_manager import CacheManager, get_cache_manager
from utils.timezone_utils import TimezoneConverter


class TestIntegrationFullFlow:
    """Testes de integração do fluxo completo"""
    
    @pytest.fixture
    def setup(self):
        """Setup para testes de integração"""
        processor = MultiLeagueProcessor()
        cache = CacheManager(use_redis=False)
        timezone_converter = TimezoneConverter()
        
        return {
            'processor': processor,
            'cache': cache,
            'timezone_converter': timezone_converter
        }
    
    def test_full_flow_brasileirao(self, setup):
        """Testa fluxo completo para Brasileirão"""
        processor = setup['processor']
        cache = setup['cache']
        
        # Dados de entrada
        matches = [
            {
                'home_team': 'Flamengo',
                'away_team': 'Vasco',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400,
            },
            {
                'home_team': 'Botafogo',
                'away_team': 'Palmeiras',
                'home_stats': {'cards_for': 12, 'cards_against': 14},
                'away_stats': {'cards_for': 16, 'cards_against': 11},
                'h2h_data': {},
                'referee_key': 'raphael_claus',
                'utc_timestamp': int(time.time()) + 86400,
            }
        ]
        
        # Processar rodada
        results = processor.process_round('brasileirao', matches, show_progress=False)
        
        # Validações
        assert results['total'] == 2
        assert results['league'] == 'brasileirao'
        assert results['successful'] >= 1
        
        # Armazenar em cache
        cache.set('brasileirao_round', results, ttl_seconds=3600)
        
        # Recuperar do cache
        cached_results = cache.get('brasileirao_round')
        assert cached_results is not None
        assert cached_results['total'] == 2
    
    def test_full_flow_premier_league(self, setup):
        """Testa fluxo completo para Premier League"""
        processor = setup['processor']
        cache = setup['cache']
        
        # Dados de entrada
        matches = [
            {
                'home_team': 'Manchester United',
                'away_team': 'Liverpool',
                'home_stats': {'cards_for': 16, 'cards_against': 11},
                'away_stats': {'cards_for': 13, 'cards_against': 14},
                'h2h_data': {},
                'referee_key': 'anthony_taylor',
                'utc_timestamp': int(time.time()) + 86400,
            },
            {
                'home_team': 'Arsenal',
                'away_team': 'Chelsea',
                'home_stats': {'cards_for': 14, 'cards_against': 13},
                'away_stats': {'cards_for': 15, 'cards_against': 12},
                'h2h_data': {},
                'referee_key': 'michael_oliver',
                'utc_timestamp': int(time.time()) + 86400,
            }
        ]
        
        # Processar rodada
        results = processor.process_round('premier_league', matches, show_progress=False)
        
        # Validações
        assert results['total'] == 2
        assert results['league'] == 'premier_league'
        assert results['successful'] >= 1
        
        # Armazenar em cache
        cache.set('premier_league_round', results, ttl_seconds=3600)
        
        # Recuperar do cache
        cached_results = cache.get('premier_league_round')
        assert cached_results is not None
        assert cached_results['total'] == 2
    
    def test_full_flow_multiple_leagues(self, setup):
        """Testa fluxo completo com múltiplas ligas"""
        processor = setup['processor']
        
        matches = {
            'brasileirao': [
                {
                    'home_team': 'Flamengo',
                    'away_team': 'Vasco',
                    'home_stats': {'cards_for': 15, 'cards_against': 12},
                    'away_stats': {'cards_for': 14, 'cards_against': 13},
                    'h2h_data': {},
                    'referee_key': 'anderson_daronco',
                    'utc_timestamp': int(time.time()) + 86400,
                }
            ],
            'premier_league': [
                {
                    'home_team': 'Manchester United',
                    'away_team': 'Liverpool',
                    'home_stats': {'cards_for': 16, 'cards_against': 11},
                    'away_stats': {'cards_for': 13, 'cards_against': 14},
                    'h2h_data': {},
                    'referee_key': 'anthony_taylor',
                    'utc_timestamp': int(time.time()) + 86400,
                }
            ]
        }
        
        # Processar múltiplas ligas
        results = processor.process_multiple_leagues(matches, show_progress=False)
        
        # Validações
        assert 'brasileirao' in results
        assert 'premier_league' in results
        assert results['brasileirao']['total'] == 1
        assert results['premier_league']['total'] == 1
    
    def test_timezone_conversion_integration(self, setup):
        """Testa integração de conversão de timezone"""
        processor = setup['processor']
        timezone_converter = setup['timezone_converter']
        
        utc_timestamp = int(time.time()) + 86400
        
        # Converter para Brasília
        brasilia_time = processor.convert_time_to_league_timezone(
            'brasileirao',
            utc_timestamp
        )
        
        # Converter para Londres
        london_time = processor.convert_time_to_league_timezone(
            'premier_league',
            utc_timestamp
        )
        
        # Ambos devem ser válidos
        assert brasilia_time is not None
        assert london_time is not None
        
        # Devem ser diferentes (timezones diferentes)
        assert brasilia_time != london_time
    
    def test_cache_integration_with_processing(self, setup):
        """Testa integração de cache com processamento"""
        processor = setup['processor']
        cache = setup['cache']
        
        matches = [
            {
                'home_team': 'Flamengo',
                'away_team': 'Vasco',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400,
            }
        ]
        
        # Primeira execução (sem cache)
        start_time = time.time()
        results1 = processor.process_round('brasileirao', matches, show_progress=False)
        time1 = time.time() - start_time
        
        # Armazenar em cache
        cache.set('test_round', results1, ttl_seconds=3600)
        
        # Segunda execução (com cache)
        start_time = time.time()
        results2 = cache.get('test_round')
        time2 = time.time() - start_time
        
        # Cache deve ser mais rápido
        assert time2 < time1
        assert results1 == results2


class TestIntegrationErrorHandling:
    """Testes de integração com tratamento de erros"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar um processador"""
        return MultiLeagueProcessor()
    
    def test_invalid_league_error(self, processor):
        """Testa erro com liga inválida"""
        with pytest.raises(ValueError):
            processor.process_round('invalid_league', [])
    
    def test_invalid_referee_handling(self, processor):
        """Testa tratamento de árbitro inválido"""
        matches = [
            {
                'home_team': 'Flamengo',
                'away_team': 'Vasco',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'invalid_referee',
                'utc_timestamp': int(time.time()) + 86400,
            }
        ]
        
        # Deve processar mesmo com árbitro inválido (fallback)
        results = processor.process_round('brasileirao', matches, show_progress=False)
        assert results['total'] == 1
    
    def test_empty_matches_handling(self, processor):
        """Testa tratamento de lista vazia de matches"""
        results = processor.process_round('brasileirao', [], show_progress=False)
        
        assert results['total'] == 0
        assert results['successful'] == 0


class TestIntegrationPerformance:
    """Testes de performance de integração"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar um processador"""
        return MultiLeagueProcessor()
    
    def test_performance_20_matches_brasileirao(self, processor):
        """Testa performance com 20 matches do Brasileirão"""
        matches = [
            {
                'home_team': f'Time{i}A',
                'away_team': f'Time{i}B',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400 + (i * 3600),
            }
            for i in range(20)
        ]
        
        start_time = time.time()
        results = processor.process_round('brasileirao', matches, show_progress=False)
        elapsed_time = time.time() - start_time
        
        # Deve processar 20 matches em menos de 10 segundos
        assert elapsed_time < 10.0
        assert results['total'] == 20
    
    def test_performance_20_matches_premier_league(self, processor):
        """Testa performance com 20 matches da Premier League"""
        matches = [
            {
                'home_team': f'Team{i}A',
                'away_team': f'Team{i}B',
                'home_stats': {'cards_for': 16, 'cards_against': 11},
                'away_stats': {'cards_for': 13, 'cards_against': 14},
                'h2h_data': {},
                'referee_key': 'anthony_taylor',
                'utc_timestamp': int(time.time()) + 86400 + (i * 3600),
            }
            for i in range(20)
        ]
        
        start_time = time.time()
        results = processor.process_round('premier_league', matches, show_progress=False)
        elapsed_time = time.time() - start_time
        
        # Deve processar 20 matches em menos de 10 segundos
        assert elapsed_time < 10.0
        assert results['total'] == 20
    
    def test_performance_multiple_leagues_simultaneous(self, processor):
        """Testa performance processando múltiplas ligas simultaneamente"""
        matches = {
            'brasileirao': [
                {
                    'home_team': f'Time{i}A',
                    'away_team': f'Time{i}B',
                    'home_stats': {'cards_for': 15, 'cards_against': 12},
                    'away_stats': {'cards_for': 14, 'cards_against': 13},
                    'h2h_data': {},
                    'referee_key': 'anderson_daronco',
                    'utc_timestamp': int(time.time()) + 86400 + (i * 3600),
                }
                for i in range(10)
            ],
            'premier_league': [
                {
                    'home_team': f'Team{i}A',
                    'away_team': f'Team{i}B',
                    'home_stats': {'cards_for': 16, 'cards_against': 11},
                    'away_stats': {'cards_for': 13, 'cards_against': 14},
                    'h2h_data': {},
                    'referee_key': 'anthony_taylor',
                    'utc_timestamp': int(time.time()) + 86400 + (i * 3600),
                }
                for i in range(10)
            ]
        }
        
        start_time = time.time()
        results = processor.process_multiple_leagues(matches, show_progress=False)
        elapsed_time = time.time() - start_time
        
        # Deve processar 20 matches (10 de cada liga) em menos de 15 segundos
        assert elapsed_time < 15.0
        assert results['brasileirao']['total'] == 10
        assert results['premier_league']['total'] == 10


class TestIntegrationDataConsistency:
    """Testes de consistência de dados"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar um processador"""
        return MultiLeagueProcessor()
    
    def test_data_consistency_across_processing(self, processor):
        """Testa consistência de dados entre processamentos"""
        matches = [
            {
                'home_team': 'Flamengo',
                'away_team': 'Vasco',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400,
            }
        ]
        
        # Processar duas vezes
        results1 = processor.process_round('brasileirao', matches, show_progress=False)
        results2 = processor.process_round('brasileirao', matches, show_progress=False)
        
        # Resultados devem ser consistentes
        assert results1['total'] == results2['total']
        assert results1['league'] == results2['league']
    
    def test_league_config_consistency(self, processor):
        """Testa consistência de configuração de ligas"""
        comparison1 = processor.get_league_comparison()
        comparison2 = processor.get_league_comparison()
        
        # Configurações devem ser idênticas
        assert comparison1 == comparison2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])