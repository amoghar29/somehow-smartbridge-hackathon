"""
Claude API Service for AI-powered financial advice
Replaces the slow local Granite model with fast Claude API
"""
import os
from typing import Optional
from anthropic import Anthropic
from core.logger import logger
from core.response_cache import response_cache
import time
# Initialize Claude API client
# Set your API key in environment variable: ANTHROPIC_API_KEY
# Or hardcode it here (not recommended for production)
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

class ClaudeService:
    """
    Service for generating AI responses using Claude API
    """
    _instance = None
    _client = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClaudeService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Claude API client"""
        if not ClaudeService._initialized:
            try:
                if CLAUDE_API_KEY:
                    ClaudeService._client = Anthropic(api_key=CLAUDE_API_KEY)
                    ClaudeService._initialized = True
                    logger.info("Claude API client initialized successfully")
                else:
                    logger.warning("ANTHROPIC_API_KEY not set - AI responses will use fallbacks")
            except Exception as e:
                logger.error(f"Failed to initialize Claude API: {str(e)}")
                ClaudeService._client = None

    def generate(
        self,
        prompt: str,
        max_tokens: int = 300,
        temperature: float = 0.7,
        use_cache: bool = True
    ) -> str:
        """
        Generate text using Claude API

        Args:
            prompt: Input prompt for Claude
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            use_cache: Whether to use response cache

        Returns:
            str: Generated text response

        Raises:
            Exception: If API call fails and no fallback available
        """
        # Check cache first
        if use_cache:
            cached_response = response_cache.get(prompt, max_tokens, temperature)
            if cached_response:
                logger.info("Using cached Claude response")
                return cached_response

        # Check if Claude API is available
        if not ClaudeService._client:
            error_msg = "Claude API not initialized - check ANTHROPIC_API_KEY"
            logger.error(error_msg)
            raise Exception(error_msg)
        time.sleep(7)
        try:
            logger.info(f"Calling Claude API with prompt: {prompt[:100]}...")
            # Call Claude API
            message = ClaudeService._client.messages.create(
                model="claude-haiku-4-5-20251001",  # Latest Claude model
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract response text
            response_text = message.content[0].text

            # Log response with safe encoding
            try:
                logger.info(f"Claude API response received: {response_text[:100]}...")
            except (UnicodeEncodeError, UnicodeDecodeError):
                logger.info("Claude API response received: [Response contains special characters]")

            # Cache the response
            if use_cache:
                response_cache.set(prompt, max_tokens, temperature, response_text)

            return response_text

        except Exception as e:
            error_msg = f"Claude API call failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def is_ready(self) -> bool:
        """
        Check if Claude API is ready to use

        Returns:
            bool: True if API client is initialized, False otherwise
        """
        return ClaudeService._client is not None


# Create global instance
claude_service = ClaudeService()


def generate(prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
    """
    Convenience function to generate text using Claude API

    Args:
        prompt: Input text prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        str: Generated text response

    Raises:
        Exception: If API call fails
    """
    return claude_service.generate(prompt, max_tokens, temperature)


def is_api_available() -> bool:
    """
    Check if Claude API is available

    Returns:
        bool: True if API is ready, False otherwise
    """
    return claude_service.is_ready()
