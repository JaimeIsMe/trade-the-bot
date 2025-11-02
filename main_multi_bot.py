"""
Multi-Bot Launcher - Run multiple trading bots with different strategies
Each bot can use different:
- LLM providers (OpenAI, DeepSeek, Claude)
- Trading strategies
- Wallet credentials
- Symbols
"""
import asyncio
import threading
import os
from loguru import logger
from dotenv import load_dotenv

from api.aster_client import AsterClient
from agent.trader import VibeTrader
from agent.llm_client import LLMClient
from utils.logger import setup_logger
from config.config import config

# Load environment variables
load_dotenv()


class BotConfig:
    """Configuration for a single bot instance"""
    def __init__(
        self,
        name: str,
        user_address: str,
        signer_address: str,
        private_key: str,
        llm_provider: str,
        llm_model: str,
        llm_api_key: str,
        symbol: str = "ASTERUSDT",
        strategy_name: str = "aggressive"
    ):
        self.name = name
        self.user_address = user_address
        self.signer_address = signer_address
        self.private_key = private_key
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_api_key = llm_api_key
        self.symbol = symbol
        self.strategy_name = strategy_name


def create_llm_client(bot_config: BotConfig) -> LLMClient:
    """Create a custom LLM client for a bot"""
    from openai import AsyncOpenAI
    from config.config import Config, LLMConfig
    
    # Create custom config for this bot
    if bot_config.llm_provider == "openai":
        client = AsyncOpenAI(api_key=bot_config.llm_api_key)
    elif bot_config.llm_provider == "deepseek":
        client = AsyncOpenAI(
            api_key=bot_config.llm_api_key,
            base_url="https://api.deepseek.com"
        )
    elif bot_config.llm_provider == "qwen":
        client = AsyncOpenAI(
            api_key=bot_config.llm_api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
    elif bot_config.llm_provider == "anthropic":
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=bot_config.llm_api_key)
    else:
        raise ValueError(f"Unsupported provider: {bot_config.llm_provider}")
    
    # Create LLM client wrapper
    llm = LLMClient.__new__(LLMClient)
    llm.provider = bot_config.llm_provider
    llm.model = bot_config.llm_model
    llm.client = client
    
    logger.info(f"[{bot_config.name}] LLM initialized: {bot_config.llm_provider} - {bot_config.llm_model}")
    return llm


def create_aster_client(bot_config: BotConfig) -> AsterClient:
    """Create Aster client with custom credentials"""
    # Create client with custom credentials
    client = AsterClient.__new__(AsterClient)
    client.user_address = bot_config.user_address
    client.signer_address = bot_config.signer_address
    client.private_key = bot_config.private_key
    client.api_url = config.aster.api_url
    client.base_url = config.aster.api_url  # Fix: add base_url attribute
    client.ws_url = config.aster.ws_url
    client.session = None
    
    logger.info(f"[{bot_config.name}] Aster client created for {bot_config.user_address[:10]}...")
    return client


def run_dashboard_api(bots: list):
    """Run the dashboard API server"""
    import uvicorn
    from dashboard_api.server import app, set_trader_instances
    
    # Set all bots for multi-bot dashboard support
    if bots:
        set_trader_instances(bots)
    
    logger.info(f"Starting Dashboard API on http://localhost:{config.dashboard.api_port}")
    uvicorn.run(app, host="0.0.0.0", port=config.dashboard.api_port, log_level="warning")


async def initialize_bot(bot_config: BotConfig, traders_list: list):
    """Initialize a bot instance and add to traders list"""
    logger.info(f"=" * 70)
    logger.info(f"[{bot_config.name}] Initializing Bot")
    logger.info(f"[{bot_config.name}] Symbol: {bot_config.symbol}")
    logger.info(f"[{bot_config.name}] LLM: {bot_config.llm_provider} ({bot_config.llm_model})")
    logger.info(f"[{bot_config.name}] Strategy: {bot_config.strategy_name}")
    logger.info(f"=" * 70)
    
    # Create Aster client
    aster_client = create_aster_client(bot_config)
    await aster_client.__aenter__()
    
    # Create LLM client
    llm_client = create_llm_client(bot_config)
    
    # Create trader
    trader = VibeTrader(
        aster_client=aster_client,
        llm_client=llm_client,
        bot_name=bot_config.name,
        symbol=bot_config.symbol
    )
    
    # Add trader to list for dashboard
    traders_list.append(trader)
    
    # Register with dashboard API directly
    try:
        from dashboard_api.server import register_trader_instance
        register_trader_instance(trader)
    except Exception as e:
        logger.warning(f"[{bot_config.name}] Could not register with dashboard: {e}")
    
    logger.info(f"[{bot_config.name}] Bot initialized and registered with dashboard")


async def main():
    """Main function to run multiple bots"""
    setup_logger()
    
    # Initialize shared account cache to reduce API calls
    from utils.shared_account_cache import SharedAccountCache
    shared_cache = SharedAccountCache()
    logger.info("✅ Shared account cache initialized - all bots will share account data")
    
    # ═══════════════════════════════════════════════════════════════
    # BOT CONFIGURATIONS - 5 ASSETS WITH QWEN-FLASH
    # All bots use same wallet, same LLM model, different assets
    # ═══════════════════════════════════════════════════════════════
    
    bots_config = []
    
    # Common config for all bots
    user_address = os.getenv("ASTER_USER_ADDRESS", "")
    signer_address = os.getenv("ASTER_SIGNER_ADDRESS", "")
    private_key = os.getenv("ASTER_PRIVATE_KEY", "")
    llm_provider = os.getenv("LLM_PROVIDER", "qwen")
    llm_model = os.getenv("LLM_MODEL", "qwen-flash")
    llm_api_key = os.getenv("QWEN_API_KEY", "")
    
    # BOT 1: ASTERUSDT
    bot1 = BotConfig(
        name="ASTER-BOT",
        user_address=user_address,
        signer_address=signer_address,
        private_key=private_key,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        symbol="ASTERUSDT",
        strategy_name="aggressive"
    )
    bots_config.append(bot1)
    
    # BOT 2: BTCUSDT
    bot2 = BotConfig(
        name="BTC-BOT",
        user_address=user_address,
        signer_address=signer_address,
        private_key=private_key,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        symbol="BTCUSDT",
        strategy_name="aggressive"
    )
    bots_config.append(bot2)
    
    # BOT 3: SOLUSDT
    bot3 = BotConfig(
        name="SOL-BOT",
        user_address=user_address,
        signer_address=signer_address,
        private_key=private_key,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        symbol="SOLUSDT",
        strategy_name="aggressive"
    )
    bots_config.append(bot3)
    
    # BOT 4: BNBUSDT
    bot4 = BotConfig(
        name="BNB-BOT",
        user_address=user_address,
        signer_address=signer_address,
        private_key=private_key,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        symbol="BNBUSDT",
        strategy_name="aggressive"
    )
    bots_config.append(bot4)
    
    # BOT 5: ETHUSDT
    bot5 = BotConfig(
        name="ETH-BOT",
        user_address=user_address,
        signer_address=signer_address,
        private_key=private_key,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        symbol="ETHUSDT",
        strategy_name="aggressive"
    )
    bots_config.append(bot5)
    
    # ═══════════════════════════════════════════════════════════════
    
    if not bots_config:
        logger.error("No bots configured!")
        return
    
    logger.info("=" * 70)
    logger.info(f"MULTI-BOT TRADING SYSTEM - {len(bots_config)} Bots Active")
    logger.info("=" * 70)
    for bot in bots_config:
        logger.info(f"  • {bot.name}: {bot.symbol} via {bot.llm_provider} ({bot.strategy_name})")
    logger.info("=" * 70)
    
    try:
        # Create traders list for dashboard
        traders = []
        
        # Start dashboard API in background
        api_thread = threading.Thread(
            target=run_dashboard_api,
            args=(traders,),
            daemon=True
        )
        api_thread.start()
        logger.info("Dashboard API started in background")
        
        # Wait a moment for dashboard to initialize
        await asyncio.sleep(2)
        
        # Initialize all bots first (without starting trading)
        logger.info("Initializing all bots...")
        trader_tasks = []
        for bot_config in bots_config:
            trader_tasks.append(initialize_bot(bot_config, traders))
        
        # Wait for all bots to initialize
        await asyncio.gather(*trader_tasks)
        
        # Set the Aster client in shared cache (use first trader's client since they all share wallet)
        if traders:
            shared_cache.set_client(traders[0].aster)
            logger.info("✅ Shared cache configured with Aster client")
        
        # Now start trading for all bots - STAGGERED to spread API load
        logger.success(f"🚀 Starting {len(traders)} trading bots (staggered 1 min apart)...")
        
        async def start_bot_with_delay(trader, delay_seconds):
            """Start a bot after a delay to stagger API calls"""
            if delay_seconds > 0:
                logger.info(f"⏱️ {trader.bot_name} will start in {delay_seconds} seconds...")
                await asyncio.sleep(delay_seconds)
            logger.info(f"🚀 Starting {trader.bot_name}")
            await trader.start()
        
        # Stagger bot starts by 60 seconds each
        staggered_tasks = [
            start_bot_with_delay(trader, index * 60) 
            for index, trader in enumerate(traders)
        ]
        
        await asyncio.gather(*staggered_tasks)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("Shutting down all trading bots")


if __name__ == "__main__":
    asyncio.run(main())

