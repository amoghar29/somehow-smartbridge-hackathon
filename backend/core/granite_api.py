"""
IBM Granite Model API Integration
Handles model loading and text generation using Hugging Face Transformers
"""
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from config.settings import MODEL_ID, DEVICE, CACHE_DIR, MAX_NEW_TOKENS, DEFAULT_TEMPERATURE
from core.logger import logger
from core.response_cache import response_cache

class GraniteAPI:
    """
    Singleton class for managing IBM Granite model instance
    """
    _instance = None
    _pipeline = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraniteAPI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Granite model pipeline (lazy loading)"""
        # Don't load model on init - load on first use instead
        pass

    def _load_model(self):
        """
        Load the IBM Granite model and create a text generation pipeline
        """
        try:
            logger.info(f"Loading IBM Granite model: {MODEL_ID}")
            logger.info(f"Using device: {DEVICE}")
            logger.info(f"Cache directory: {CACHE_DIR}")

            # Load tokenizer from cache only (no internet check)
            logger.info("Loading tokenizer from cache...")
            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_ID,
                cache_dir=CACHE_DIR,
                trust_remote_code=True,
                local_files_only=True  # Force using cache, don't check for updates
            )

            # Load model from cache only (no internet check)
            logger.info("Loading model from cache (this may take 10-30 seconds)...")

            # Try to use quantization for faster CPU inference
            try:
                # Use bitsandbytes 8-bit quantization if available
                model = AutoModelForCausalLM.from_pretrained(
                    MODEL_ID,
                    cache_dir=CACHE_DIR,
                    load_in_8bit=True,  # 8-bit quantization for faster inference
                    trust_remote_code=True,
                    device_map="auto",
                    local_files_only=True
                )
                logger.info("Model loaded with 8-bit quantization")
            except Exception as quant_error:
                # Fallback to regular loading if quantization fails
                logger.warning(f"Quantization failed ({quant_error}), loading with float32")
                model = AutoModelForCausalLM.from_pretrained(
                    MODEL_ID,
                    cache_dir=CACHE_DIR,
                    torch_dtype=torch.float32,  # Use float32 for CPU
                    trust_remote_code=True,
                    device_map="auto",  # Let accelerate handle device placement
                    local_files_only=True  # Force using cache, don't check for updates
                )

            # Create text generation pipeline
            # Don't specify device when using device_map with accelerate
            GraniteAPI._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer
            )

            logger.info("Model loaded successfully!")

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            GraniteAPI._pipeline = None
            raise

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> str:
        """
        Generate text using the Granite model

        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            str: Generated text response

        Raises:
            Exception: If model is not loaded or generation fails
        """
        # Check cache first
        cached_response = response_cache.get(prompt, max_new_tokens, temperature)
        if cached_response:
            return cached_response

        # Lazy load model on first use
        if GraniteAPI._pipeline is None and not GraniteAPI._initialized:
            logger.info("Model not loaded yet. Loading now...")
            self._load_model()
            GraniteAPI._initialized = True

        if GraniteAPI._pipeline is None:
            error_msg = "Model failed to load. Cannot generate text."
            logger.error(error_msg)
            raise Exception(error_msg)

        try:
            logger.info(f"Generating response for prompt: {prompt[:100]}...")

            # Generate text with optimized parameters for CPU speed
            # Use greedy decoding when temperature is 0 for faster generation
            if temperature == 0.0:
                result = GraniteAPI._pipeline(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,  # Greedy decoding - much faster
                    num_return_sequences=1,
                    pad_token_id=GraniteAPI._pipeline.tokenizer.eos_token_id,
                    eos_token_id=GraniteAPI._pipeline.tokenizer.eos_token_id
                )
            else:
                # Sampling mode - slower but more diverse
                result = GraniteAPI._pipeline(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.95,
                    top_k=50,
                    repetition_penalty=1.2,
                    num_return_sequences=1,
                    pad_token_id=GraniteAPI._pipeline.tokenizer.eos_token_id,
                    eos_token_id=GraniteAPI._pipeline.tokenizer.eos_token_id
                )

            # Extract generated text
            generated_text = result[0]['generated_text']

            # Remove the prompt from the output
            response = generated_text[len(prompt):].strip()

            # Clean up the response
            # Remove incomplete sentences at the end
            if response:
                # Split into sentences and take complete ones
                sentences = response.split('.')
                # Keep sentences that are reasonably complete
                complete_sentences = []
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 10:  # Minimum sentence length
                        complete_sentences.append(sent)
                    if len(complete_sentences) >= 3:  # Max 3 sentences for concise answers
                        break

                if complete_sentences:
                    response = '. '.join(complete_sentences) + '.'
                else:
                    response = response[:200]  # Fallback: first 200 chars

            logger.info(f"Generated response: {response[:100]}...")

            # Cache the response
            response_cache.set(prompt, max_new_tokens, temperature, response)

            return response

        except Exception as e:
            error_msg = f"Text generation failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def is_ready(self) -> bool:
        """
        Check if the model is loaded and ready

        Returns:
            bool: True if model is ready, False otherwise
        """
        return GraniteAPI._pipeline is not None


# Create global instance
granite_api = GraniteAPI()


def generate(prompt: str, max_new_tokens: int = MAX_NEW_TOKENS, temperature: float = DEFAULT_TEMPERATURE) -> str:
    """
    Convenience function to generate text using the global Granite API instance

    Args:
        prompt: Input text prompt
        max_new_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature

    Returns:
        str: Generated text response
    """
    return granite_api.generate(prompt, max_new_tokens, temperature)
