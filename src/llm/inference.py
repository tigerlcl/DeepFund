import os
from typing import Type, TypeVar, Dict, Any
from dataclasses import dataclass

from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel

from util.logger import logger
from .provider import Provider

@dataclass
class LLMConfig:
    """Configuration for LLM inference"""
    provider: str
    model: str = ""  # If empty, will use provider's default model
    temperature: float = 0.5
    max_retries: int = 3

T = TypeVar('T', bound=BaseModel)

def get_model(config: LLMConfig) -> BaseChatModel:
    """Get a model instance based on configuration."""
    provider = Provider(config.provider)
    model_config = provider.config
    
    # Use default model if not specified
    model_name = config.model or model_config.default_model

    if model_config.requires_api_key:
        api_key = os.getenv(model_config.env_key)
        if not api_key:
            logger.error(f"API Key Error: Please make sure {model_config.env_key} is set in your .env file.")
            raise ValueError(f"{provider} API key not found. Please set {model_config.env_key} in .env file.")
    
    kwargs = {
        "model": model_name,
        **({"api_key": api_key} if model_config.requires_api_key else {}),
        **({"base_url": model_config.base_url} if model_config.base_url else {}),
        **({"temperature": config.temperature} if config.temperature is not None else {})
    }
    
    try:
        return model_config.model_class(**kwargs)
    except Exception as e:
        logger.error(f"{provider} Chat Error: {e}")
        raise ValueError(f"{provider} Chat Error: {e}")

def agent_call(prompt: str, config: Dict[str, Any], pydantic_model: Type[T]) -> T:
    """
    Makes an agent call with retry logic and structured output.
    
    Args:
        prompt: The prompt to send to the LLM
        config: Configuration for the LLM
        output_model: The Pydantic model to use for structured output
    Returns:
        An instance of output_model (with defaults if error occurs)
    """

    llm_config = LLMConfig(**config)
    llm = get_model(llm_config)
    llm = llm.with_structured_output(pydantic_model)
    
    for attempt in range(llm_config.max_retries):
        try:
            result = llm.invoke(prompt)
            return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{llm_config.max_retries} failed: {e}")
            if attempt == llm_config.max_retries - 1:
                logger.error(f"All {llm_config.max_retries} attempts failed")
                return pydantic_model()
    
    return pydantic_model() 