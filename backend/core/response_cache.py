"""
Simple in-memory cache for AI responses
"""
from functools import lru_cache
import hashlib
from core.logger import logger


class ResponseCache:
    """Simple LRU cache for AI responses"""

    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size

    def get_key(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate cache key from parameters"""
        cache_str = f"{prompt}|{max_tokens}|{temperature}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def get(self, prompt: str, max_tokens: int, temperature: float) -> str | None:
        """Get cached response if available"""
        key = self.get_key(prompt, max_tokens, temperature)
        if key in self.cache:
            logger.info(f"Cache HIT for prompt: {prompt[:50]}...")
            return self.cache[key]
        logger.info(f"Cache MISS for prompt: {prompt[:50]}...")
        return None

    def set(self, prompt: str, max_tokens: int, temperature: float, response: str):
        """Cache a response"""
        # Simple LRU: if full, remove oldest (first) item
        if len(self.cache) >= self.max_size:
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        key = self.get_key(prompt, max_tokens, temperature)
        self.cache[key] = response
        logger.info(f"Cached response for: {prompt[:50]}...")


# Global cache instance
response_cache = ResponseCache(max_size=200)
