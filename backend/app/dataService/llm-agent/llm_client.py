"""
LLM Client Initialization Module

This module provides a unified way to initialize LLM clients (OpenAI/DeepSeek)
across different components of the system.
"""

import os
import logging
from openai import OpenAI
from typing import Tuple, Optional

# Configure logger
logger = logging.getLogger(__name__)

# --- LLM Client Configuration ---
def initialize_llm_client(provider: Optional[str] = None) -> Tuple[OpenAI, str]:
    """
    Initialize LLM client with support for multiple providers.
    
    Args:
        provider: Optional provider override ('openai' or 'deepseek')
        
    Returns: 
        Tuple of (client, model_name)
        
    Raises:
        SystemExit: If no valid configuration is found
    """
    
    # Get API keys and model preferences from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    # Model name preferences (can be overridden via env vars)
    openai_model = os.getenv("OPENAI_EVAL_MODEL", "gpt-4o")
    deepseek_model = os.getenv("DEEPSEEK_EVAL_MODEL", "deepseek-chat")

    # Allow override of provider preference
    preferred_provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
    custom_model = os.getenv("LLM_MODEL")
    
    logger.info("Initializing LLM client...")
    
    # Try the preferred provider first
    if preferred_provider == "openai" and openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            model = custom_model or openai_model
            logger.info(f"✅ OpenAI client initialized with model: {model}")
            print(f"✅ Using OpenAI API with model: {model}")
            return client, model
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            print(f"❌ OpenAI initialization failed: {e}")
    
    elif preferred_provider == "deepseek" and deepseek_api_key:
        try:
            client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            model = custom_model or deepseek_model
            logger.info(f"✅ DeepSeek client initialized with model: {model}")
            print(f"✅ Using DeepSeek API with model: {model}")
            return client, model
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            print(f"❌ DeepSeek initialization failed: {e}")
    
    # Fallback to any available provider
    logger.info("Trying fallback providers...")
    
    # Try OpenAI as fallback if not already attempted
    if preferred_provider != "openai" and openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            model = custom_model or openai_model
            logger.info(f"✅ OpenAI client initialized (fallback) with model: {model}")
            print(f"✅ Using OpenAI API (fallback) with model: {model}")
            return client, model
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client (fallback): {e}")
    
    # Try DeepSeek as fallback if not already attempted
    if preferred_provider != "deepseek" and deepseek_api_key:
        try:
            client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            model = custom_model or deepseek_model
            logger.info(f"✅ DeepSeek client initialized (fallback) with model: {model}")
            print(f"✅ Using DeepSeek API (fallback) with model: {model}")
            return client, model
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client (fallback): {e}")
    
    # Error: No valid configuration found
    error_msg = "❌ No valid LLM configuration found. Please set OPENAI_API_KEY or DEEPSEEK_API_KEY environment variable."
    logger.error(error_msg)
    print(error_msg)
    exit(1)