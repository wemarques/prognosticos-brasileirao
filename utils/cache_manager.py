"""
Gerenciador de cache inteligente com TTL
Suporta cache em memória e Redis
"""
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib
import logging


logger = logging.getLogger(__name__)


class CacheManager:
    """Gerenciador de cache com TTL"""
    
    def __init__(self, use_redis: bool = False):
        """
        Inicializa o gerenciador de cache
        
        Args:
            use_redis: Usar Redis (True) ou memória (False)
        """
        self.use_redis = use_redis
        self.memory_cache = {}
        self.cache_timestamps = {}
        
        if use_redis:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Redis conectado com sucesso")
            except Exception as e:
                logger.warning(f"Redis não disponível: {e}. Usando cache em memória.")
                self.use_redis = False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Gera chave de cache única
        
        Args:
            prefix: Prefixo da chave
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Chave de cache
        """
        # Criar string com todos os argumentos
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        key_string = "|".join(key_parts)
        
        # Hash para chaves muito longas
        if len(key_string) > 100:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_string
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obter valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor em cache ou None
        """
        try:
            if self.use_redis:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Verificar TTL em memória
                if key in self.memory_cache:
                    timestamp = self.cache_timestamps.get(key)
                    if timestamp and datetime.now() < timestamp:
                        return self.memory_cache[key]
                    else:
                        # Cache expirado
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]
            
            return None
        except Exception as e:
            logger.error(f"Erro ao obter cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Armazenar valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl_seconds: Tempo de vida em segundos
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if self.use_redis:
                self.redis_client.setex(
                    key,
                    ttl_seconds,
                    json.dumps(value, default=str)
                )
            else:
                self.memory_cache[key] = value
                self.cache_timestamps[key] = datetime.now() + timedelta(seconds=ttl_seconds)
            
            logger.debug(f"Cache armazenado: {key} (TTL: {ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Erro ao armazenar cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Deletar valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se sucesso
        """
        try:
            if self.use_redis:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
            
            logger.debug(f"Cache deletado: {key}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Limpar todo o cache
        
        Returns:
            True se sucesso
        """
        try:
            if self.use_redis:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
                self.cache_timestamps.clear()
            
            logger.info("Cache limpo")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def cached(self, ttl_seconds: int = 3600, prefix: str = "cache"):
        """
        Decorator para cachear resultado de função
        
        Args:
            ttl_seconds: Tempo de vida em segundos
            prefix: Prefixo da chave
            
        Returns:
            Função decorada
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Gerar chave
                key = self._generate_key(prefix, func.__name__, *args, **kwargs)
                
                # Tentar obter do cache
                cached_value = self.get(key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {key}")
                    return cached_value
                
                # Executar função
                result = func(*args, **kwargs)
                
                # Armazenar no cache
                self.set(key, result, ttl_seconds)
                
                return result
            
            return wrapper
        return decorator
    
    def get_stats(self) -> dict:
        """
        Obter estatísticas do cache
        
        Returns:
            Dict com estatísticas
        """
        if self.use_redis:
            try:
                info = self.redis_client.info()
                return {
                    'type': 'redis',
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands': info.get('total_commands_processed', 0)
                }
            except Exception as e:
                logger.error(f"Erro ao obter stats Redis: {e}")
        
        # Stats de memória
        return {
            'type': 'memory',
            'cached_items': len(self.memory_cache),
            'memory_usage': f"{len(str(self.memory_cache)) / 1024:.2f} KB"
        }


# Instância global
_cache_manager = None


def get_cache_manager(use_redis: bool = False) -> CacheManager:
    """
    Obter instância global do gerenciador de cache
    
    Args:
        use_redis: Usar Redis
        
    Returns:
        Instância do CacheManager
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(use_redis=use_redis)
    return _cache_manager


# Configurações de cache por tipo
CACHE_CONFIG = {
    'referee_data': {
        'ttl': 86400,  # 24 horas
        'prefix': 'referee'
    },
    'league_stats': {
        'ttl': 43200,  # 12 horas
        'prefix': 'league_stats'
    },
    'match_processed': {
        'ttl': 3600,   # 1 hora
        'prefix': 'match'
    },
    'api_results': {
        'ttl': 1800,   # 30 minutos
        'prefix': 'api'
    },
    'round_results': {
        'ttl': 3600,   # 1 hora
        'prefix': 'round'
    }
}


def cache_referee_data(func: Callable) -> Callable:
    """Decorator para cachear dados de árbitros"""
    cache = get_cache_manager()
    config = CACHE_CONFIG['referee_data']
    return cache.cached(ttl_seconds=config['ttl'], prefix=config['prefix'])(func)


def cache_league_stats(func: Callable) -> Callable:
    """Decorator para cachear estatísticas de liga"""
    cache = get_cache_manager()
    config = CACHE_CONFIG['league_stats']
    return cache.cached(ttl_seconds=config['ttl'], prefix=config['prefix'])(func)


def cache_match_processed(func: Callable) -> Callable:
    """Decorator para cachear matches processados"""
    cache = get_cache_manager()
    config = CACHE_CONFIG['match_processed']
    return cache.cached(ttl_seconds=config['ttl'], prefix=config['prefix'])(func)


def cache_api_results(func: Callable) -> Callable:
    """Decorator para cachear resultados de API"""
    cache = get_cache_manager()
    config = CACHE_CONFIG['api_results']
    return cache.cached(ttl_seconds=config['ttl'], prefix=config['prefix'])(func)


# Exemplo de uso
if __name__ == "__main__":
    # Criar gerenciador
    cache = CacheManager(use_redis=False)
    
    # Armazenar dados
    cache.set('test_key', {'data': 'value'}, ttl_seconds=60)
    
    # Recuperar dados
    value = cache.get('test_key')
    print(f"Valor recuperado: {value}")
    
    # Usar decorator
    @cache.cached(ttl_seconds=60, prefix='example')
    def expensive_function(x, y):
        print(f"Calculando {x} + {y}...")
        return x + y
    
    # Primeira chamada (calcula)
    result1 = expensive_function(5, 3)
    print(f"Resultado 1: {result1}")
    
    # Segunda chamada (do cache)
    result2 = expensive_function(5, 3)
    print(f"Resultado 2: {result2}")
    
    # Stats
    print(f"Stats: {cache.get_stats()}")