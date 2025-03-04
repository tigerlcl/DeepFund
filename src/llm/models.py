import os
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Tuple
import requests
import json
from core.logger import logger


class ModelProvider(str, Enum):
    """Enum for supported LLM providers"""
    OPENAI = "OpenAI"
    GROQ = "Groq"
    ANTHROPIC = "Anthropic"
    OLLAMA = "Ollama"
    CUSTOM = "Custom"


class LLMModel(BaseModel):
    """Represents an LLM model configuration"""
    display_name: str
    model_name: str
    provider: ModelProvider
    
    def is_deepseek(self) -> bool:
        """Check if the model is a DeepSeek model"""
        return self.model_name.startswith("deepseek")


class CustomChatModel(BaseChatModel):
    """Custom chat model for external API endpoints"""
    
    def __init__(
        self, 
        url: str, 
        api_key: str, 
        model: str = "default", 
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """Initialize the custom chat model.
        
        Args:
            url: API endpoint URL
            api_key: API key
            model: Model name to use
            headers: Additional headers to include in the request
        """
        super().__init__(**kwargs)
        self.url = url
        self.api_key = api_key
        self.model = model
        self.headers = headers or {}
        
        # Add API key to headers
        self.headers["Authorization"] = f"Bearer {self.api_key}"
        
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Generate a response from the model."""
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": m.type, "content": m.content} for m in messages],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
            }
            
            if stop:
                payload["stop"] = stop
                
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the response content
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return {"generations": [{"text": content}]}
            else:
                raise ValueError(f"Unexpected response format: {result}")
                
        except Exception as e:
            logger.error(f"Error calling custom LLM API: {str(e)}")
            return {"generations": [{"text": f"Error: {str(e)}"}]}
            
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        """Async version of _generate."""
        # For simplicity, we're using the sync version
        return self._generate(messages, stop, run_manager, **kwargs)
        
    def _llm_type(self):
        """Return the type of LLM."""
        return "custom_chat_model"


def get_model(config: Dict[str, Any]) -> BaseChatModel:
    """Get a model instance based on configuration.
    
    Args:
        config: LLM configuration from config manager
        
    Returns:
        A chat model instance
    """
    provider = config.get("provider", "OpenAI")
    model_name = config.get("model", "gpt-4o")
    
    if provider == ModelProvider.GROQ.value:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("API Key Error: Please make sure GROQ_API_KEY is set in your .env file.")
            raise ValueError("Groq API key not found. Please make sure GROQ_API_KEY is set in your .env file.")
        return ChatGroq(model=model_name, api_key=api_key)
    
    elif provider == ModelProvider.OPENAI.value:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("API Key Error: Please make sure OPENAI_API_KEY is set in your .env file.")
            raise ValueError("OpenAI API key not found. Please make sure OPENAI_API_KEY is set in your .env file.")
        return ChatOpenAI(model=model_name, api_key=api_key)
    
    elif provider == ModelProvider.ANTHROPIC.value:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("API Key Error: Please make sure ANTHROPIC_API_KEY is set in your .env file.")
            raise ValueError("Anthropic API key not found. Please make sure ANTHROPIC_API_KEY is set in your .env file.")
        return ChatAnthropic(model=model_name, api_key=api_key)
    
    elif provider == ModelProvider.OLLAMA.value:
        try:
            return ChatOllama(model=model_name)
        except Exception as e:
            logger.error(f"Ollama Chat Error: {e}")
            raise ValueError(f"Ollama Chat Error: {e}")
    
    elif provider == ModelProvider.CUSTOM.value:
        custom_config = config.get("custom_endpoint", {})
        url = custom_config.get("url")
        api_key_env_var = custom_config.get("api_key_env_var")
        headers = custom_config.get("headers", {})
        
        if not url:
            logger.error("Custom API URL not provided in configuration.")
            raise ValueError("Custom API URL not provided in configuration.")
            
        if not api_key_env_var:
            logger.error("Custom API key environment variable not provided in configuration.")
            raise ValueError("Custom API key environment variable not provided in configuration.")
            
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            logger.error(f"API Key Error: Please make sure {api_key_env_var} is set in your .env file.")
            raise ValueError(f"Custom API key not found. Please make sure {api_key_env_var} is set in your .env file.")
            
        return CustomChatModel(url=url, api_key=api_key, model=model_name, headers=headers)
    
    else:
        logger.error(f"Unsupported model provider: {provider}")
        raise ValueError(f"Unsupported model provider: {provider}")