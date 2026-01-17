"""
Logging utilities for BDD Automation Framework
"""
import logging
import sys


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with standard configuration
    
    Args:
        name: Logger name (defaults to root logger)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger








