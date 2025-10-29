"""
Sistema de logging centralizado
Configuração de logging para toda a aplicação
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class LoggerConfig:
    """Configuração centralizada de logging"""
    
    # Criar diretório de logs
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)
    
    # Níveis de log
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # Formato de log
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @staticmethod
    def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
        """
        Configurar logger para um módulo
        
        Args:
            name: Nome do logger (geralmente __name__)
            level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Logger configurado
        """
        logger = logging.getLogger(name)
        logger.setLevel(LoggerConfig.LEVELS.get(level, logging.INFO))
        
        # Evitar duplicação de handlers
        if logger.handlers:
            return logger
        
        # Formatter
        formatter = logging.Formatter(
            LoggerConfig.LOG_FORMAT,
            datefmt=LoggerConfig.DATE_FORMAT
        )
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LoggerConfig.LEVELS.get(level, logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para arquivo
        log_file = LoggerConfig.LOG_DIR / f"{name.replace('.', '_')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(LoggerConfig.LEVELS.get(level, logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def setup_performance_logger() -> logging.Logger:
        """Configurar logger para métricas de performance"""
        logger = logging.getLogger('performance')
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt=LoggerConfig.DATE_FORMAT
        )
        
        # Handler para arquivo de performance
        perf_file = LoggerConfig.LOG_DIR / "performance.log"
        file_handler = logging.handlers.RotatingFileHandler(
            perf_file,
            maxBytes=10485760,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def setup_error_logger() -> logging.Logger:
        """Configurar logger para erros"""
        logger = logging.getLogger('errors')
        logger.setLevel(logging.ERROR)
        
        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n%(exc_info)s',
            datefmt=LoggerConfig.DATE_FORMAT
        )
        
        # Handler para arquivo de erros
        error_file = LoggerConfig.LOG_DIR / "errors.log"
        file_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10485760,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def setup_api_logger() -> logging.Logger:
        """Configurar logger para requisições de API"""
        logger = logging.getLogger('api')
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt=LoggerConfig.DATE_FORMAT
        )
        
        # Handler para arquivo de API
        api_file = LoggerConfig.LOG_DIR / "api.log"
        file_handler = logging.handlers.RotatingFileHandler(
            api_file,
            maxBytes=10485760,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger


# Instâncias globais de loggers
logger = LoggerConfig.setup_logger(__name__)
performance_logger = LoggerConfig.setup_performance_logger()
error_logger = LoggerConfig.setup_error_logger()
api_logger = LoggerConfig.setup_api_logger()


# Funções de conveniência
def log_info(message: str, logger_name: str = 'main'):
    """Log de informação"""
    LoggerConfig.setup_logger(logger_name).info(message)


def log_warning(message: str, logger_name: str = 'main'):
    """Log de aviso"""
    LoggerConfig.setup_logger(logger_name).warning(message)


def log_error(message: str, exception: Exception = None, logger_name: str = 'main'):
    """Log de erro"""
    error_logger.error(message, exc_info=exception)


def log_performance(operation: str, duration: float, details: str = ""):
    """Log de performance"""
    message = f"{operation}: {duration:.2f}s"
    if details:
        message += f" - {details}"
    performance_logger.info(message)


def log_api_call(method: str, url: str, status_code: int = None, duration: float = None):
    """Log de chamada de API"""
    message = f"{method} {url}"
    if status_code:
        message += f" - Status: {status_code}"
    if duration:
        message += f" - Duration: {duration:.2f}s"
    api_logger.info(message)


if __name__ == "__main__":
    # Teste de logging
    log_info("Teste de informação")
    log_warning("Teste de aviso")
    log_performance("Operação de teste", 1.234, "Detalhes do teste")
    log_api_call("GET", "https://api.example.com/data", 200, 0.5)
    
    print("✅ Logging configurado com sucesso!")
    print(f"📁 Logs salvos em: {LoggerConfig.LOG_DIR}")