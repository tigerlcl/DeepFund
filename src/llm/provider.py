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
    default_model: str = "gpt-4"

class Provider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"
    OLLAMA = "Ollama"
    YIZHAN = "YiZhan"

    @property
    def config(self) -> ModelConfig:
        """Get the configuration for this provider"""
        PROVIDER_CONFIGS = {
            Provider.OPENAI: ModelConfig(
                model_class=ChatOpenAI,
                env_key="OPENAI_API_KEY",
                default_model="gpt-4"
            ),
            Provider.ANTHROPIC: ModelConfig(
                model_class=ChatAnthropic,
                env_key="ANTHROPIC_API_KEY",
                default_model="claude-3-opus-20240229"
            ),
            Provider.DEEPSEEK: ModelConfig(
                model_class=ChatDeepSeek,
                env_key="DEEPSEEK_API_KEY",
                default_model="deepseek-chat"
            ),
            Provider.OLLAMA: ModelConfig(
                model_class=ChatOllama,
                requires_api_key=False,
                default_model="llama2"
            ),
            Provider.YIZHAN: ModelConfig(
                model_class=ChatOpenAI,
                env_key="YIZHAN_API_KEY",
                base_url="https://vip.yi-zhan.top/v1",
                default_model="gpt-4"
            )
        }
        return PROVIDER_CONFIGS[self]

    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get the default model for a provider"""
        return cls(provider).config.default_model 