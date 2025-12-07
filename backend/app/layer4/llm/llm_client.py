"""
llm_client.py - Unified client for OpenAI and Anthropic
"""

import asyncio
from typing import Dict, Optional, Any
import time
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str  # 'openai' or 'anthropic'
    model: str
    api_key: str
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 2


class UnifiedLLMClient:
    """
    Unified client supporting OpenAI and Anthropic
    Handles retries, timeouts, and error handling
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None

        if config.provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Run: pip install openai")
            self.client = openai.OpenAI(api_key=config.api_key)
        elif config.provider == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=config.api_key)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion from LLM

        Returns:
        {
            'content': 'LLM response text',
            'usage': {'prompt_tokens': X, 'completion_tokens': Y, 'total_tokens': Z},
            'model': 'model-name',
            'provider': 'openai|anthropic',
            'latency_ms': milliseconds,
            'finish_reason': 'stop|length|...'
        }
        """

        start_time = time.time()

        # Override config with kwargs
        temperature = kwargs.get('temperature', self.config.temperature)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                if self.config.provider == 'openai':
                    result = await self._call_openai(
                        prompt, system_prompt, temperature, max_tokens
                    )
                else:
                    result = await self._call_anthropic(
                        prompt, system_prompt, temperature, max_tokens
                    )

                # Add metadata
                result['latency_ms'] = int((time.time() - start_time) * 1000)
                result['provider'] = self.config.provider
                result['model'] = self.config.model
                result['attempt'] = attempt + 1

                logger.info(f"LLM call successful: {result['usage']['total_tokens']} tokens, "
                           f"{result['latency_ms']}ms")

                return result

            except Exception as e:
                last_error = e
                logger.warning(f"LLM call attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.config.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"All LLM call attempts failed: {str(e)}")

        if last_error:
            raise last_error
        raise Exception("LLM call failed with unknown error")

    async def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call OpenAI API"""

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Use asyncio.to_thread for blocking IO calls
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.config.timeout
        )

        return {
            'content': response.choices[0].message.content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'finish_reason': response.choices[0].finish_reason
        }

    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Anthropic API"""

        # Use asyncio.to_thread for blocking IO calls
        response = await asyncio.to_thread(
            self.client.messages.create,
            model=self.config.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            timeout=self.config.timeout
        )

        return {
            'content': response.content[0].text,
            'usage': {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            },
            'finish_reason': response.stop_reason
        }


# Initialize clients (singleton pattern)
# These will be None if API keys are not configured
openai_client: Optional[UnifiedLLMClient] = None
anthropic_client: Optional[UnifiedLLMClient] = None

def _initialize_clients():
    """Initialize LLM clients if API keys are available"""
    global openai_client, anthropic_client
    
    try:
        from app.core.config import settings
        
        # Try OpenAI
        openai_key = getattr(settings, 'OPENAI_API_KEY', None) or getattr(settings, 'OPENAI_KEY', '')
        if openai_key and OPENAI_AVAILABLE:
            try:
                openai_client = UnifiedLLMClient(LLMConfig(
                    provider='openai',
                    model='gpt-4',
                    api_key=openai_key,
                    temperature=0.3,
                    max_tokens=2000
                ))
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        # Try Anthropic
        anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', None) or getattr(settings, 'ANTHROPIC_KEY', '')
        if anthropic_key and ANTHROPIC_AVAILABLE:
            try:
                anthropic_client = UnifiedLLMClient(LLMConfig(
                    provider='anthropic',
                    model='claude-3-5-sonnet-20241022',
                    api_key=anthropic_key,
                    temperature=0.3,
                    max_tokens=2000
                ))
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
                
    except Exception as e:
        logger.warning(f"Could not initialize LLM clients: {e}")


# Lazy initialization - clients will be initialized on first import
_initialize_clients()
