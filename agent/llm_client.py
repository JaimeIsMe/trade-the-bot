"""
LLM Client for AI decision making
"""
from typing import Optional
from loguru import logger
from config.config import config


class LLMClient:
    """Client for interacting with LLM providers"""
    
    def __init__(self):
        self.provider = config.llm.provider
        self.model = config.llm.model
        
        if self.provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=config.llm.openai_api_key)
        elif self.provider == "deepseek":
            from openai import AsyncOpenAI
            # DeepSeek uses OpenAI-compatible API
            self.client = AsyncOpenAI(
                api_key=config.llm.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
        elif self.provider == "qwen":
            from openai import AsyncOpenAI
            # Qwen uses OpenAI-compatible API (DashScope International)
            self.client = AsyncOpenAI(
                api_key=config.llm.qwen_api_key,
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            )
        elif self.provider == "anthropic":
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=config.llm.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        logger.info(f"LLM Client initialized with {self.provider} using model {self.model}")
    
    async def get_completion(
        self, 
        prompt: str, 
        system_message: Optional[str] = None
    ) -> str:
        """
        Get completion from LLM
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            LLM response text
        """
        try:
            if self.provider in ["openai", "deepseek", "qwen"]:
                # DeepSeek and Qwen use OpenAI-compatible API
                return await self._get_openai_completion(prompt, system_message)
            elif self.provider == "anthropic":
                return await self._get_anthropic_completion(prompt, system_message)
        except Exception as e:
            logger.error(f"Error getting LLM completion: {e}")
            raise
    
    async def _get_openai_completion(
        self, 
        prompt: str, 
        system_message: Optional[str]
    ) -> str:
        """Get completion from OpenAI"""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def _get_anthropic_completion(
        self, 
        prompt: str, 
        system_message: Optional[str]
    ) -> str:
        """Get completion from Anthropic"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=config.llm.max_tokens,
            temperature=config.llm.temperature,
            system=system_message or "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text

