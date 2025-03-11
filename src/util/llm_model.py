import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Type, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

from util.logger import logger

@dataclass
class ModelConfig:
    """Configuration for a model provider"""
    model_class: Type[BaseChatModel]
    env_key: Optional[str] = None
    base_url: Optional[str] = None
    requires_api_key: bool = True

class ModelProvider(str, Enum):
    """Enum for supported LLM providers with their configurations"""
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"
    OLLAMA = "Ollama"
    YIZHAN = "YiZhan"

    @property
    def config(self) -> ModelConfig:
        """Get the configuration for this provider"""
        PROVIDER_CONFIGS = {
            ModelProvider.OPENAI: ModelConfig(
                model_class=ChatOpenAI,
                env_key="OPENAI_API_KEY"
            ),
            ModelProvider.ANTHROPIC: ModelConfig(
                model_class=ChatAnthropic,
                env_key="ANTHROPIC_API_KEY"
            ),
            ModelProvider.DEEPSEEK: ModelConfig(
                model_class=ChatDeepSeek,
                env_key="DEEPSEEK_API_KEY"
            ),
            ModelProvider.OLLAMA: ModelConfig(
                model_class=ChatOllama,
                requires_api_key=False
            ),
            # YiZhan is compatible with OpenAI 
            ModelProvider.YIZHAN: ModelConfig(
                model_class=ChatOpenAI,
                env_key="YIZHAN_API_KEY",
                base_url="https://vip.yi-zhan.top/v1"
            )
        }
        return PROVIDER_CONFIGS[self]

def get_model(config: Dict[str, Any]) -> BaseChatModel:
    """Get a model instance based on configuration."""
    provider = ModelProvider(config.get("provider", ModelProvider.OPENAI))
    model_name = config.get("model", "gpt-4o-mini")
    model_config = provider.config

    if model_config.requires_api_key:
        api_key = os.getenv(model_config.env_key)
        if not api_key:
            logger.error(f"API Key Error: Please make sure {model_config.env_key} is set in your .env file.")
            raise ValueError(f"{provider} API key not found. Please make sure {model_config.env_key} is set in your .env file.")
    
    kwargs = {
        "model": model_name,
        **({"api_key": api_key} if model_config.requires_api_key else {}),
        **({"base_url": model_config.base_url} if model_config.base_url else {})
    }
    
    try:
        return model_config.model_class(**kwargs)
    except Exception as e:
        logger.error(f"{provider} Chat Error: {e}")
        raise ValueError(f"{provider} Chat Error: {e}")

