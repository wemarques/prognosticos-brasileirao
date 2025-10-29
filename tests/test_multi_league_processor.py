"""
Testes para MultiLeagueProcessor
"""
import pytest
import time
from data.multi_league_processor import MultiLeagueProcessor
from utils.multi_league_config import (
    get_league_config,
    get_available_leagues,
    compare_leagues
)


class TestMultiLeagueProcessor:
    """Testes para o processador multi-liga"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar um processador multi-liga"""
        return MultiLeagueProcessor()
    
    def test_processor_initialization(self, processor):
        """Testa inicialização do processador"""
        assert processor is not None
        assert len(processor.processors) == 2
        assert len(processor.batch_processors) == 2
    
    def test_processor_has_both_leagues(self, processor):
        """Testa se processador tem ambas as ligas"""
        assert 'brasileirao' in processor.processors
        assert 'premier_league' in processor.processors
    
    def test_process_match_brasileirao(self, processor):
        """Testa processar match do Brasileirão"""
        result = processor.process_match(
            league='brasileirao',
            home_stats={'cards_for': 15, 'cards_against': 12},
            away_stats={'cards_for': 14, 'cards_against': 13},
            h2h_data={},
            home_team_name='Flamengo',
            away_team_name='Vasco',
            referee_key='anderson_daronco',
            utc_timestamp=int(time.time()) + 86400
        )
        
        assert result is not None
        assert result['league'] == 'brasileirao'
        assert 'league_config' in result
    
    def test_process_match_premier_league(self, processor):
        """Testa processar match da Premier League"""
        result = processor.process_match(
            league='premier_league',
            home_stats={'cards_for': 16, 'cards_against': 11},
            away_stats={'cards_for': 13, 'cards_against': 14},
            h2h_data={},
            home_team_name='Manchester United',
            away_team_name='Liverpool',
            referee_key='anthony_taylor',
            utc_timestamp=int(time.time()) + 86400
        )
        
        assert result is not None
        assert result['league'] == 'premier_league'
        assert 'league_config' in result
    
    def test_process_match_invalid_league(self, processor):
        """Testa processar match com liga inválida"""
        with pytest.raises(ValueError):
            processor.process_match(
                league='invalid_league',
                home_stats={},
                away_stats={},
                h2h_data={},
                home_team_name='Team A',
                away_team_name='Team B'
            )
    
    def test_get_league_comparison(self, processor):
        """Testa obter comparação de ligas"""
        comparison = processor.get_league_comparison()
        
        assert 'brasileirao' in comparison
        assert 'premier_league' in comparison
        assert comparison['brasileirao']['name'] == 'Brasileirão Série A'
        assert comparison['premier_league']['name'] == 'Premier League'
    
    def test_convert_time_to_league_timezone_brasilia(self, processor):
        """Testa conversão de timezone para Brasília"""
        utc_timestamp = int(time.time())
        brasilia_time = processor.convert_time_to_league_timezone(
            'brasileirao',
            utc_timestamp
        )
        
        assert brasilia_time is not None
        assert '/' in brasilia_time  # Formato DD/MM/YYYY
        assert ':' in brasilia_time  # Formato HH:MM
    
    def test_convert_time_to_league_timezone_london(self, processor):
        """Testa conversão de timezone para Londres"""
        utc_timestamp = int(time.time())
        london_time = processor.convert_time_to_league_timezone(
            'premier_league',
            utc_timestamp
        )
        
        assert london_time is not None
        assert '/' in london_time
        assert ':' in london_time
    
    def test_get_league_stats_summary_brasileirao(self, processor):
        """Testa obter resumo de estatísticas do Brasileirão"""
        summary = processor.get_league_stats_summary('brasileirao')
        
        assert 'BRASILEIRÃO' in summary
        assert 'Gols/Jogo' in summary
        assert 'Cartões/Jogo' in summary
    
    def test_get_league_stats_summary_premier_league(self, processor):
        """Testa obter resumo de estatísticas da Premier League"""
        summary = processor.get_league_stats_summary('premier_league')
        
        assert 'PREMIER LEAGUE' in summary
        assert 'Gols/Jogo' in summary
        assert 'Cartões/Jogo' in summary


class TestLeagueConfiguration:
    """Testes para configuração de ligas"""
    
    def test_get_league_config_brasileirao(self):
        """Testa obter configuração do Brasileirão"""
        config = get_league_config('brasileirao')
        
        assert config['name'] == 'Brasileirão Série A'
        assert config['code'] == 'BSA'
        assert config['timezone'] == 'America/Sao_Paulo'
    
    def test_get_league_config_premier_league(self):
        """Testa obter configuração da Premier League"""
        config = get_league_config('premier_league')
        
        assert config['name'] == 'Premier League'
        assert config['code'] == 'PL'
        assert config['timezone'] == 'Europe/London'
    
    def test_get_available_leagues(self):
        """Testa obter ligas disponíveis"""
        leagues = get_available_leagues()
        
        assert len(leagues) == 2
        assert 'brasileirao' in leagues
        assert 'premier_league' in leagues
    
    def test_compare_leagues(self):
        """Testa comparação de ligas"""
        comparison = compare_leagues()
        
        assert 'brasileirao' in comparison
        assert 'premier_league' in comparison
        
        br = comparison['brasileirao']
        pl = comparison['premier_league']
        
        assert br['avg_goals'] < pl['avg_goals']  # PL tem mais gols
        assert br['avg_cards'] < pl['avg_cards']  # PL tem mais cartões


class TestMultiLeagueProcessing:
    """Testes para processamento multi-liga"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar um processador"""
        return MultiLeagueProcessor()
    
    @pytest.fixture
    def sample_matches(self):
        """Fixture com matches de exemplo"""
        return {
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
    
    def test_process_multiple_leagues(self, processor, sample_matches):
        """Testa processar múltiplas ligas"""
        results = processor.process_multiple_leagues(sample_matches, show_progress=False)
        
        assert 'brasileirao' in results
        assert 'premier_league' in results
        assert results['brasileirao']['total'] == 1
        assert results['premier_league']['total'] == 1
    
    def test_process_round_brasileirao(self, processor):
        """Testa processar rodada do Brasileirão"""
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
            for i in range(5)
        ]
        
        results = processor.process_round('brasileirao', matches, show_progress=False)
        
        assert results['total'] == 5
        assert results['league'] == 'brasileirao'
    
    def test_process_round_premier_league(self, processor):
        """Testa processar rodada da Premier League"""
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
            for i in range(5)
        ]
        
        results = processor.process_round('premier_league', matches, show_progress=False)
        
        assert results['total'] == 5
        assert results['league'] == 'premier_league'


class TestLeagueStatistics:
    """Testes para estatísticas de ligas"""
    
    def test_brasileirao_stats(self):
        """Testa estatísticas do Brasileirão"""
        config = get_league_config('brasileirao')
        stats = config['stats']
        
        assert stats['league_avg_goals'] == 1.82
        assert stats['league_avg_xg'] == 1.40
        assert stats['home_advantage'] == 1.53
        assert stats['avg_cards_per_match'] == 4.2
    
    def test_premier_league_stats(self):
        """Testa estatísticas da Premier League"""
        config = get_league_config('premier_league')
        stats = config['stats']
        
        assert stats['league_avg_goals'] == 2.69
        assert stats['league_avg_xg'] == 1.65
        assert stats['home_advantage'] == 1.38
        assert stats['avg_cards_per_match'] == 4.4
    
    def test_stats_comparison(self):
        """Testa comparação de estatísticas"""
        br_config = get_league_config('brasileirao')
        pl_config = get_league_config('premier_league')
        
        br_stats = br_config['stats']
        pl_stats = pl_config['stats']
        
        # Premier League tem mais gols
        assert pl_stats['league_avg_goals'] > br_stats['league_avg_goals']
        
        # Premier League tem mais cartões
        assert pl_stats['avg_cards_per_match'] > br_stats['avg_cards_per_match']
        
        # Brasileirão tem maior vantagem de casa
        assert br_stats['home_advantage'] > pl_stats['home_advantage']


class TestProcessorPerformance:
    """Testes de performance do processador"""
    
    def test_processor_initialization_performance(self):
        """Testa performance de inicialização"""
        start_time = time.time()
        processor = MultiLeagueProcessor()
        init_time = time.time() - start_time
        
        # Inicialização deve ser rápida
        assert init_time < 1.0
    
    def test_league_comparison_performance(self):
        """Testa performance de comparação de ligas"""
        processor = MultiLeagueProcessor()
        
        start_time = time.time()
        comparison = processor.get_league_comparison()
        comparison_time = time.time() - start_time
        
        # Comparação deve ser rápida
        assert comparison_time < 0.1
        assert len(comparison) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])