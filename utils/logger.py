"""
Centralized logging configuration for the application
Wrapper around existing logger_config for simplified usage
"""
import logging
import os
from utils.logger_config import LoggerConfig


def setup_logger(name, level=logging.INFO):
    """
    Setup logger with file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
    
    Returns:
        logging.Logger: Configured logger
    """
    level_name = logging.getLevelName(level)
    return LoggerConfig.setup_logger(name, level_name)


logger = setup_logger(__name__)
