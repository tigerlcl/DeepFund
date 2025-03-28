from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

@dataclass
class ModelConfig:
    """Configuration for a model provider"""
    model_class: Type[BaseChatModel]
    env_key: Optional[str] = None
    base_url: Optional[str] = None
    requires_api_key: bool = True

class Provider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"
    OLLAMA = "Ollama"

    @property
    def config(self) -> ModelConfig:
        """Get the configuration for this provider"""
        PROVIDER_CONFIGS = {
            Provider.OPENAI: ModelConfig(
                model_class=ChatOpenAI,
                env_key="OPENAI_API_KEY",
            ),
            Provider.ANTHROPIC: ModelConfig(
                model_class=ChatAnthropic,
                env_key="ANTHROPIC_API_KEY",
            ),
            Provider.DEEPSEEK: ModelConfig(
                model_class=ChatDeepSeek,
                env_key="DEEPSEEK_API_KEY",
            ),
            Provider.OLLAMA: ModelConfig(
                model_class=ChatOllama,
                requires_api_key=False,
            ),
        }
        return PROVIDER_CONFIGS[self]