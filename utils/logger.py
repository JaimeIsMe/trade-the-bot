"""
Logging configuration
"""
import sys
from loguru import logger
from pathlib import Path


def setup_logger():
    """Configure logger for the application"""
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # File handler for all logs
    logger.add(
        log_dir / "vibe_trader.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )
    
    # Separate file for errors
    logger.add(
        log_dir / "errors.log",
        rotation="100 MB",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Separate file for trades
    logger.add(
        log_dir / "trades.log",
        rotation="100 MB",
        retention="90 days",
        level="INFO",
        filter=lambda record: "trade" in record["message"].lower() or "position" in record["message"].lower(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}"
    )

