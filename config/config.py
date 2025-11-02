"""
Configuration management for Aster Vibe Trader
"""
import os
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class AsterConfig(BaseModel):
    """Aster API configuration - Wallet-based authentication"""
    user_address: str = Field(default_factory=lambda: os.getenv("ASTER_USER_ADDRESS", ""))
    signer_address: str = Field(default_factory=lambda: os.getenv("ASTER_SIGNER_ADDRESS", ""))
    private_key: str = Field(default_factory=lambda: os.getenv("ASTER_PRIVATE_KEY", ""))
    api_url: str = Field(default_factory=lambda: os.getenv("ASTER_API_URL", "https://fapi.asterdex.com"))
    ws_url: str = Field(default_factory=lambda: os.getenv("ASTER_WS_URL", "wss://fapi.asterdex.com"))


class LLMConfig(BaseModel):
    """LLM configuration"""
    provider: Literal["openai", "anthropic", "deepseek", "qwen"] = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "openai")
    )
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    deepseek_api_key: str = Field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    qwen_api_key: str = Field(default_factory=lambda: os.getenv("QWEN_API_KEY", ""))
    model: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini")  # Options: gpt-4o-mini, deepseek-chat, qwen-max, claude-3-haiku
    )
    temperature: float = 0.7
    max_tokens: int = 4000


class TradingConfig(BaseModel):
    """Trading strategy configuration - AGGRESSIVE SETTINGS"""
    mode: Literal["testnet", "live"] = Field(
        default_factory=lambda: os.getenv("TRADING_MODE", "testnet")
    )
    symbol: str = Field(
        default_factory=lambda: os.getenv("TRADING_SYMBOL", "BTCUSDT")
    )
    max_position_size: float = Field(
        default_factory=lambda: float(os.getenv("MAX_POSITION_SIZE", "1200"))  # Increased to $1,200 for better capital utilization ($2k account)
    )
    risk_per_trade: float = Field(
        default_factory=lambda: float(os.getenv("RISK_PER_TRADE", "0.03"))  # 3% per trade (more aggressive)
    )
    max_open_positions: int = Field(
        default_factory=lambda: int(os.getenv("MAX_OPEN_POSITIONS", "5"))  # Allow 5 simultaneous positions for multi-asset
    )
    leverage: int = Field(
        default_factory=lambda: int(os.getenv("LEVERAGE", "5"))  # 5x leverage (aggressive but manageable)
    )
    update_interval: int = 300  # 5 minutes (300 seconds) - reduced to prevent API bans
    
    # Advanced risk parameters
    max_portfolio_heat: float = 0.15  # Max 15% total portfolio at risk
    trailing_stop_activation: float = 0.015  # Activate trailing stop after 1.5% profit
    trailing_stop_distance: float = 0.01  # Trail at 1% distance
    confidence_threshold: int = 60  # Minimum confidence to trade (lowered for more opportunities)


class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    port: int = Field(default_factory=lambda: int(os.getenv("DASHBOARD_PORT", "3000")))
    api_port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))


class Config(BaseModel):
    """Master configuration"""
    aster: AsterConfig = Field(default_factory=AsterConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)


# Global config instance
config = Config()

