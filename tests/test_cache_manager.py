"""
Testes para CacheManager
"""
import pytest
import time
from utils.cache_manager import (
    CacheManager,
    get_cache_manager,
    cache_referee_data,
    cache_league_stats,
    CACHE_CONFIG
)


class TestCacheManager:
    """Testes para o gerenciador de cache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture para criar um cache manager"""
        return CacheManager(use_redis=False)
    
    def test_cache_initialization(self, cache):
        """Testa inicialização do cache"""
        assert cache is not None
        assert cache.memory_cache == {}
        assert cache.cache_timestamps == {}
    
    def test_cache_set_and_get(self, cache):
        """Testa armazenar e recuperar do cache"""
        cache.set('test_key', {'data': 'value'}, ttl_seconds=60)
        value = cache.get('test_key')
        
        assert value is not None
        assert value['data'] == 'value'
    
    def test_cache_get_nonexistent(self, cache):
        """Testa recuperar chave inexistente"""
        value = cache.get('nonexistent_key')
        assert value is None
    
    def test_cache_delete(self, cache):
        """Testa deletar do cache"""
        cache.set('test_key', {'data': 'value'}, ttl_seconds=60)
        cache.delete('test_key')
        value = cache.get('test_key')
        
        assert value is None
    
    def test_cache_clear(self, cache):
        """Testa limpar todo o cache"""
        cache.set('key1', 'value1', ttl_seconds=60)
        cache.set('key2', 'value2', ttl_seconds=60)
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
    
    def test_cache_ttl_expiration(self, cache):
        """Testa expiração de TTL"""
        cache.set('test_key', {'data': 'value'}, ttl_seconds=1)
        
        # Valor deve estar disponível imediatamente
        assert cache.get('test_key') is not None
        
        # Aguardar expiração
        time.sleep(1.1)
        
        # Valor deve ter expirado
        assert cache.get('test_key') is None
    
    def test_cache_decorator(self, cache):
        """Testa decorator de cache"""
        call_count = 0
        
        @cache.cached(ttl_seconds=60, prefix='test')
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # Primeira chamada (calcula)
        result1 = expensive_function(5, 3)
        assert result1 == 8
        assert call_count == 1
        
        # Segunda chamada (do cache)
        result2 = expensive_function(5, 3)
        assert result2 == 8
        assert call_count == 1  # Não deve incrementar
    
    def test_cache_key_generation(self, cache):
        """Testa geração de chaves de cache"""
        key1 = cache._generate_key('prefix', 'arg1', 'arg2')
        key2 = cache._generate_key('prefix', 'arg1', 'arg2')
        
        # Mesmos argumentos devem gerar mesma chave
        assert key1 == key2
    
    def test_cache_stats(self, cache):
        """Testa obtenção de estatísticas"""
        cache.set('key1', 'value1', ttl_seconds=60)
        cache.set('key2', 'value2', ttl_seconds=60)
        
        stats = cache.get_stats()
        
        assert stats['type'] == 'memory'
        assert stats['cached_items'] == 2
    
    def test_cache_with_complex_data(self, cache):
        """Testa cache com dados complexos"""
        complex_data = {
            'nested': {
                'data': [1, 2, 3],
                'info': 'test'
            },
            'list': [{'id': 1}, {'id': 2}]
        }
        
        cache.set('complex', complex_data, ttl_seconds=60)
        retrieved = cache.get('complex')
        
        assert retrieved == complex_data
    
    def test_cache_multiple_keys(self, cache):
        """Testa múltiplas chaves no cache"""
        for i in range(10):
            cache.set(f'key_{i}', f'value_{i}', ttl_seconds=60)
        
        for i in range(10):
            assert cache.get(f'key_{i}') == f'value_{i}'
    
    def test_cache_overwrite(self, cache):
        """Testa sobrescrever valor no cache"""
        cache.set('key', 'value1', ttl_seconds=60)
        assert cache.get('key') == 'value1'
        
        cache.set('key', 'value2', ttl_seconds=60)
        assert cache.get('key') == 'value2'


class TestCacheDecorators:
    """Testes para decorators de cache"""
    
    def test_cache_referee_data_decorator(self):
        """Testa decorator para dados de árbitros"""
        call_count = 0
        
        @cache_referee_data
        def get_referee_data(referee_key):
            nonlocal call_count
            call_count += 1
            return {'name': 'Test Referee', 'key': referee_key}
        
        # Primeira chamada
        result1 = get_referee_data('anderson_daronco')
        assert call_count == 1
        
        # Segunda chamada (do cache)
        result2 = get_referee_data('anderson_daronco')
        assert call_count == 1
        
        assert result1 == result2
    
    def test_cache_league_stats_decorator(self):
        """Testa decorator para estatísticas de liga"""
        call_count = 0
        
        @cache_league_stats
        def get_league_stats(league):
            nonlocal call_count
            call_count += 1
            return {'league': league, 'avg_goals': 2.5}
        
        # Primeira chamada
        result1 = get_league_stats('brasileirao')
        assert call_count == 1
        
        # Segunda chamada (do cache)
        result2 = get_league_stats('brasileirao')
        assert call_count == 1
        
        assert result1 == result2


class TestCacheConfig:
    """Testes para configuração de cache"""
    
    def test_cache_config_exists(self):
        """Testa se configurações de cache existem"""
        assert 'referee_data' in CACHE_CONFIG
        assert 'league_stats' in CACHE_CONFIG
        assert 'match_processed' in CACHE_CONFIG
        assert 'api_results' in CACHE_CONFIG
        assert 'round_results' in CACHE_CONFIG
    
    def test_cache_config_ttl_values(self):
        """Testa valores de TTL nas configurações"""
        assert CACHE_CONFIG['referee_data']['ttl'] == 86400  # 24h
        assert CACHE_CONFIG['league_stats']['ttl'] == 43200  # 12h
        assert CACHE_CONFIG['match_processed']['ttl'] == 3600  # 1h
        assert CACHE_CONFIG['api_results']['ttl'] == 1800  # 30min
        assert CACHE_CONFIG['round_results']['ttl'] == 3600  # 1h
    
    def test_cache_config_prefixes(self):
        """Testa prefixos nas configurações"""
        assert CACHE_CONFIG['referee_data']['prefix'] == 'referee'
        assert CACHE_CONFIG['league_stats']['prefix'] == 'league_stats'
        assert CACHE_CONFIG['match_processed']['prefix'] == 'match'
        assert CACHE_CONFIG['api_results']['prefix'] == 'api'
        assert CACHE_CONFIG['round_results']['prefix'] == 'round'


class TestCachePerformance:
    """Testes de performance do cache"""
    
    def test_cache_performance_with_many_items(self):
        """Testa performance com muitos itens"""
        cache = CacheManager(use_redis=False)
        
        # Armazenar 1000 itens
        start_time = time.time()
        for i in range(1000):
            cache.set(f'key_{i}', f'value_{i}', ttl_seconds=60)
        store_time = time.time() - start_time
        
        # Recuperar 1000 itens
        start_time = time.time()
        for i in range(1000):
            cache.get(f'key_{i}')
        retrieve_time = time.time() - start_time
        
        # Ambas operações devem ser rápidas
        assert store_time < 1.0  # Menos de 1 segundo
        assert retrieve_time < 1.0  # Menos de 1 segundo
    
    def test_cache_hit_rate(self):
        """Testa taxa de acerto do cache"""
        cache = CacheManager(use_redis=False)
        
        # Armazenar dados
        for i in range(100):
            cache.set(f'key_{i}', f'value_{i}', ttl_seconds=60)
        
        # Recuperar dados
        hits = 0
        for i in range(100):
            if cache.get(f'key_{i}') is not None:
                hits += 1
        
        hit_rate = hits / 100
        assert hit_rate == 1.0  # 100% de acerto


if __name__ == "__main__":
    pytest.main([__file__, "-v"])