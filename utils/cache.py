"""
Sistema de Cache com TTL (Time To Live)
Reduz requisições à API armazenando dados temporariamente
"""

import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class CacheManager:
    """Gerenciador de cache com expiração automática"""
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Inicializa o cache
        
        Args:
            ttl_seconds: Tempo de vida do cache em segundos (padrão: 1 hora)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'expirations': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Busca valor no cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não existir/expirado
        """
        if key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        entry = self._cache[key]
        
        # Verificar se expirou
        if time.time() > entry['expires_at']:
            del self._cache[key]
            self._stats['expirations'] += 1
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        return entry['value']
    
    def set(self, key: str, value: Any) -> None:
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
        """
        self._cache[key] = {
            'value': value,
            'created_at': time.time(),
            'expires_at': time.time() + self.ttl_seconds
        }
        self._stats['sets'] += 1
    
    def has(self, key: str) -> bool:
        """
        Verifica se chave existe e não expirou
        
        Args:
            key: Chave do cache
            
        Returns:
            True se existe e válido, False caso contrário
        """
        return self.get(key) is not None
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self._cache.clear()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'expirations': 0
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dict com hits, misses, hit_rate, etc.
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'expirations': self._stats['expirations'],
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'cached_items': len(self._cache)
        }
    
    def get_ttl_remaining(self, key: str) -> Optional[int]:
        """
        Retorna tempo restante até expiração
        
        Args:
            key: Chave do cache
            
        Returns:
            Segundos restantes ou None se não existe
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        remaining = int(entry['expires_at'] - time.time())
        
        return max(0, remaining)
    
    def cleanup_expired(self) -> int:
        """
        Remove entradas expiradas
        
        Returns:
            Número de entradas removidas
        """
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self._cache.items():
            if current_time > entry['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        self._stats['expirations'] += len(expired_keys)
        
        return len(expired_keys)


# Cache global para partidas (1 hora)
matches_cache = CacheManager(ttl_seconds=3600)

# Cache global para times (24 horas)
teams_cache = CacheManager(ttl_seconds=86400)


def get_cache_key_matches(team_id: int, status: str = "FINISHED", limit: int = 10) -> str:
    """Gera chave de cache para partidas"""
    return f"matches_{team_id}_{status}_{limit}"


def get_cache_key_team_stats(team_id: int, venue: str = "HOME") -> str:
    """Gera chave de cache para estatísticas de time"""
    return f"stats_{team_id}_{venue}"


def get_cache_key_h2h(team1_id: int, team2_id: int, limit: int = 5) -> str:
    """Gera chave de cache para H2H"""
    # Ordenar IDs para garantir mesma chave independente da ordem
    id1, id2 = sorted([team1_id, team2_id])
    return f"h2h_{id1}_{id2}_{limit}"


def format_cache_stats(stats: Dict) -> str:
    """Formata estatísticas do cache para exibição"""
    return (
        f"📊 Cache Stats:\n"
        f"  Hits: {stats['hits']}\n"
        f"  Misses: {stats['misses']}\n"
        f"  Hit Rate: {stats['hit_rate']:.1f}%\n"
        f"  Cached Items: {stats['cached_items']}\n"
        f"  Expirations: {stats['expirations']}"
    )

