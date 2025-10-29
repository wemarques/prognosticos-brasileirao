"""
Testes para validar a arquitetura multi-API
"""
import pytest
from data.multi_league_collector import DataCollector
from data.api_factory import APIFactory
from utils.leagues_config import get_league_config, get_api_config, get_league_names


class TestLeaguesConfig:
    """Testes para configuração de ligas"""
    
    def test_get_league_config_brasileirao(self):
        """Testa obtenção de configuração do Brasileirão"""
        config = get_league_config('brasileirao')
        assert config['id'] == 2013
        assert config['code'] == 'BSA'
        assert config['name'] == 'Brasileirão Série A'
    
    def test_get_league_config_premier_league(self):
        """Testa obtenção de configuração da Premier League"""
        config = get_league_config('premier_league')
        assert config['id'] == 2021
        assert config['code'] == 'PL'
        assert config['name'] == 'Premier League'
    
    def test_get_api_config_brasileirao(self):
        """Testa obtenção de configuração da API para Brasileirão"""
        api_config = get_api_config('brasileirao')
        assert api_config['provider'] == 'football_data'
        assert api_config['league_id'] == 2013
    
    def test_get_api_config_premier_league(self):
        """Testa obtenção de configuração da API para Premier League"""
        api_config = get_api_config('premier_league')
        assert api_config['provider'] == 'footystats'
        assert api_config['league_id'] == 1626
        assert api_config['api_key'] == 'test85g57'
    
    def test_get_league_names(self):
        """Testa obtenção de nomes de ligas para exibição"""
        names = get_league_names()
        assert 'brasileirao' in names
        assert 'premier_league' in names
        assert '🇧🇷' in names['brasileirao']
        assert '🏴' in names['premier_league']
    
    def test_invalid_league_raises_error(self):
        """Testa que liga inválida levanta erro"""
        with pytest.raises(ValueError):
            get_league_config('liga_inexistente')


class TestAPIFactory:
    """Testes para APIFactory"""
    
    def test_create_collector_brasileirao(self):
        """Testa criação de collector para Brasileirão"""
        collector = APIFactory.create_collector('brasileirao')
        assert collector is not None
        assert hasattr(collector, 'get_matches')
        assert hasattr(collector, 'get_teams')
        assert hasattr(collector, 'get_standings')
    
    def test_create_collector_premier_league(self):
        """Testa criação de collector para Premier League"""
        collector = APIFactory.create_collector('premier_league')
        assert collector is not None
        assert hasattr(collector, 'get_matches')
        assert hasattr(collector, 'get_teams')
        assert hasattr(collector, 'get_standings')
    
    def test_get_supported_providers(self):
        """Testa obtenção de providers suportados"""
        providers = APIFactory.get_supported_providers()
        assert 'football_data' in providers
        assert 'footystats' in providers


class TestDataCollector:
    """Testes para DataCollector unificado"""
    
    def test_data_collector_brasileirao_initialization(self):
        """Testa inicialização do collector para Brasileirão"""
        collector = DataCollector('brasileirao')
        assert collector.league_key == 'brasileirao'
        assert collector.api_collector is not None
    
    def test_data_collector_premier_league_initialization(self):
        """Testa inicialização do collector para Premier League"""
        collector = DataCollector('premier_league')
        assert collector.league_key == 'premier_league'
        assert collector.api_collector is not None
    
    def test_data_collector_default_league(self):
        """Testa que collector usa Brasileirão por padrão"""
        collector = DataCollector()
        assert collector.league_key == 'brasileirao'
    
    def test_data_collector_has_methods(self):
        """Testa que collector tem todos os métodos necessários"""
        collector = DataCollector('brasileirao')
        assert callable(collector.get_matches)
        assert callable(collector.get_teams)
        assert callable(collector.get_standings)


class TestDataNormalization:
    """Testes para normalização de dados"""
    
    def test_normalized_match_structure(self):
        """Testa que matches normalizados têm estrutura consistente"""
        br_collector = DataCollector('brasileirao')
        pl_collector = DataCollector('premier_league')
        
        # Ambos devem ter os mesmos campos normalizados
        expected_fields = {'id', 'date', 'home_team', 'away_team', 'home_goals', 'away_goals', 'status', 'odds'}
        
        # Verificar que os adaptadores normalizam corretamente
        from data.adapters.data_adapter import FootballDataAdapter, FootyStatsAdapter
        
        br_adapter = FootballDataAdapter()
        pl_adapter = FootyStatsAdapter()
        
        # Dados de exemplo
        br_match = {
            'id': 1,
            'utcDate': '2025-01-01',
            'homeTeam': {'name': 'Team A'},
            'awayTeam': {'name': 'Team B'},
            'score': {'fullTime': {'home': 1, 'away': 0}},
            'status': 'FINISHED'
        }
        
        pl_match = {
            'id': 1,
            'date': '2025-01-01',
            'home_team': 'Team A',
            'away_team': 'Team B',
            'goals': {'home': 1, 'away': 0},
            'status': 'FINISHED'
        }
        
        br_normalized = br_adapter.normalize_match(br_match)
        pl_normalized = pl_adapter.normalize_match(pl_match)
        
        # Ambos devem ter os mesmos campos
        assert set(br_normalized.keys()) == set(pl_normalized.keys())
        assert set(br_normalized.keys()) == expected_fields


if __name__ == '__main__':
    pytest.main([__file__, '-v'])