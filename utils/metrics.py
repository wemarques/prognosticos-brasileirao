"""
Sistema de métricas de performance
Coleta e análise de métricas do sistema
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import time
import psutil
import os


class MetricsCollector:
    """Coletor de métricas de performance"""
    
    def __init__(self):
        """Inicializa o coletor de métricas"""
        self.metrics = defaultdict(list)
        self.start_time = datetime.now()
        self.process = psutil.Process(os.getpid())
    
    def record_operation(self, operation: str, duration: float, success: bool = True, details: str = ""):
        """
        Registrar métrica de operação
        
        Args:
            operation: Nome da operação
            duration: Duração em segundos
            success: Se a operação foi bem-sucedida
            details: Detalhes adicionais
        """
        metric = {
            'timestamp': datetime.now(),
            'operation': operation,
            'duration': duration,
            'success': success,
            'details': details
        }
        self.metrics[operation].append(metric)
    
    def record_api_call(self, api: str, endpoint: str, status_code: int, duration: float):
        """
        Registrar chamada de API
        
        Args:
            api: Nome da API
            endpoint: Endpoint chamado
            status_code: Código de status HTTP
            duration: Duração em segundos
        """
        metric = {
            'timestamp': datetime.now(),
            'api': api,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            'success': 200 <= status_code < 300
        }
        self.metrics[f'api_{api}'].append(metric)
    
    def record_cache_hit(self, cache_type: str, hit: bool):
        """
        Registrar acerto/erro de cache
        
        Args:
            cache_type: Tipo de cache
            hit: Se foi um acerto
        """
        metric = {
            'timestamp': datetime.now(),
            'cache_type': cache_type,
            'hit': hit
        }
        self.metrics[f'cache_{cache_type}'].append(metric)
    
    def get_operation_stats(self, operation: str, minutes: int = 60) -> Dict[str, Any]:
        """
        Obter estatísticas de uma operação
        
        Args:
            operation: Nome da operação
            minutes: Últimos N minutos
            
        Returns:
            Dict com estatísticas
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        metrics = [m for m in self.metrics[operation] if m['timestamp'] > cutoff_time]
        
        if not metrics:
            return {
                'operation': operation,
                'count': 0,
                'success_rate': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0
            }
        
        durations = [m['duration'] for m in metrics]
        successes = sum(1 for m in metrics if m['success'])
        
        return {
            'operation': operation,
            'count': len(metrics),
            'success_rate': (successes / len(metrics)) * 100,
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_duration': sum(durations)
        }
    
    def get_api_stats(self, api: str, minutes: int = 60) -> Dict[str, Any]:
        """
        Obter estatísticas de API
        
        Args:
            api: Nome da API
            minutes: Últimos N minutos
            
        Returns:
            Dict com estatísticas
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        metrics = [m for m in self.metrics[f'api_{api}'] if m['timestamp'] > cutoff_time]
        
        if not metrics:
            return {
                'api': api,
                'total_calls': 0,
                'success_rate': 0,
                'avg_duration': 0,
                'error_count': 0
            }
        
        durations = [m['duration'] for m in metrics]
        successes = sum(1 for m in metrics if m['success'])
        errors = len(metrics) - successes
        
        return {
            'api': api,
            'total_calls': len(metrics),
            'success_rate': (successes / len(metrics)) * 100,
            'avg_duration': sum(durations) / len(durations),
            'error_count': errors,
            'status_codes': self._get_status_code_distribution(metrics)
        }
    
    def get_cache_stats(self, cache_type: str, minutes: int = 60) -> Dict[str, Any]:
        """
        Obter estatísticas de cache
        
        Args:
            cache_type: Tipo de cache
            minutes: Últimos N minutos
            
        Returns:
            Dict com estatísticas
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        metrics = [m for m in self.metrics[f'cache_{cache_type}'] if m['timestamp'] > cutoff_time]
        
        if not metrics:
            return {
                'cache_type': cache_type,
                'total_accesses': 0,
                'hit_rate': 0,
                'hits': 0,
                'misses': 0
            }
        
        hits = sum(1 for m in metrics if m['hit'])
        misses = len(metrics) - hits
        
        return {
            'cache_type': cache_type,
            'total_accesses': len(metrics),
            'hit_rate': (hits / len(metrics)) * 100,
            'hits': hits,
            'misses': misses
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas do sistema
        
        Returns:
            Dict com estatísticas do sistema
        """
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': memory_percent,
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def get_all_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Obter todas as estatísticas
        
        Args:
            minutes: Últimos N minutos
            
        Returns:
            Dict com todas as estatísticas
        """
        operations = {}
        for op in set(k for k in self.metrics.keys() if not k.startswith('api_') and not k.startswith('cache_')):
            operations[op] = self.get_operation_stats(op, minutes)
        
        apis = {}
        for api_key in set(k for k in self.metrics.keys() if k.startswith('api_')):
            api_name = api_key.replace('api_', '')
            apis[api_name] = self.get_api_stats(api_name, minutes)
        
        caches = {}
        for cache_key in set(k for k in self.metrics.keys() if k.startswith('cache_')):
            cache_name = cache_key.replace('cache_', '')
            caches[cache_name] = self.get_cache_stats(cache_name, minutes)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_stats(),
            'operations': operations,
            'apis': apis,
            'caches': caches
        }
    
    def _get_status_code_distribution(self, metrics: List[Dict]) -> Dict[int, int]:
        """Obter distribuição de códigos de status"""
        distribution = defaultdict(int)
        for m in metrics:
            distribution[m['status_code']] += 1
        return dict(distribution)
    
    def clear_old_metrics(self, minutes: int = 1440):
        """
        Limpar métricas antigas
        
        Args:
            minutes: Remover métricas mais antigas que N minutos
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        for key in self.metrics:
            self.metrics[key] = [m for m in self.metrics[key] if m['timestamp'] > cutoff_time]


# Instância global
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Obter instância global do coletor de métricas"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Decorators para facilitar uso
def track_performance(operation_name: str):
    """Decorator para rastrear performance de uma função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                get_metrics_collector().record_operation(
                    operation_name,
                    duration,
                    success=True
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                get_metrics_collector().record_operation(
                    operation_name,
                    duration,
                    success=False,
                    details=str(e)
                )
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    # Teste de métricas
    collector = get_metrics_collector()
    
    # Simular operações
    collector.record_operation("test_operation", 0.5, True)
    collector.record_operation("test_operation", 0.3, True)
    collector.record_operation("test_operation", 0.7, False)
    
    # Simular chamadas de API
    collector.record_api_call("football_data", "/matches", 200, 0.2)
    collector.record_api_call("football_data", "/matches", 200, 0.25)
    collector.record_api_call("football_data", "/matches", 500, 0.1)
    
    # Simular cache
    collector.record_cache_hit("referee_data", True)
    collector.record_cache_hit("referee_data", True)
    collector.record_cache_hit("referee_data", False)
    
    # Obter estatísticas
    print("📊 Estatísticas de Operações:")
    print(collector.get_operation_stats("test_operation"))
    
    print("\n📊 Estatísticas de API:")
    print(collector.get_api_stats("football_data"))
    
    print("\n📊 Estatísticas de Cache:")
    print(collector.get_cache_stats("referee_data"))
    
    print("\n📊 Estatísticas do Sistema:")
    print(collector.get_system_stats())
    
    print("\n✅ Métricas configuradas com sucesso!")