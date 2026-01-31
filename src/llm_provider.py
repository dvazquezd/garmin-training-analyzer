"""Abstracción mínima para proveedores LLM.

Provee una interfaz `LLMProvider` y una fábrica `LLMFactory.get_provider()`.
La implementación por defecto intenta crear un wrapper sobre las librerías de
LangChain si están disponibles. Para tests y DI, los providers pueden inyectarse
fácilmente en `LLMAnalyzer`.
"""
from __future__ import annotations

import os
from typing import Protocol
from src.config import Config


class LLMProvider(Protocol):
    """Protocolo que define la interfaz mínima requerida por el analizador."""

    def generate(self, prompt_text: str) -> str:
        """Genera texto a partir del prompt dado."""
        ...


class LLMFactory:
    @staticmethod
    def get_provider(llm_config: dict) -> LLMProvider:
        """Return a provider instance for the given config.

        By default, this will attempt to build a LangChain-backed provider.
        In environments without the relevant external libraries, this method
        will raise a RuntimeError. Tests should inject a mock provider.
        """
        provider = llm_config.get('provider', 'anthropic')

        # Normalize provider name
        provider = (provider or 'anthropic').lower()

        # Resolve API key and model from config -> env -> Config defaults
        api_key = llm_config.get('api_key') or os.getenv('ANTHROPIC_API_KEY') if provider in ('anthropic', 'claude') else llm_config.get('api_key')
        if provider == 'openai' and not api_key:
            api_key = llm_config.get('api_key') or os.getenv('OPENAI_API_KEY')
        if provider == 'google' and not api_key:
            api_key = llm_config.get('api_key') or os.getenv('GOOGLE_API_KEY')

        # Fallback to Config class values if still missing
        if not api_key:
            if provider in ('anthropic', 'claude'):
                api_key = getattr(Config, 'ANTHROPIC_API_KEY', None)
            elif provider == 'openai':
                api_key = getattr(Config, 'OPENAI_API_KEY', None)
            elif provider == 'google':
                api_key = getattr(Config, 'GOOGLE_API_KEY', None)

        # Lazy import to avoid hard dependency during tests
        try:
            if provider in ('anthropic', 'claude'):
                # Support both 'anthropic' and explicit 'claude' provider names.
                from langchain_anthropic import ChatAnthropic  # type: ignore
                # This is a very small wrapper around the Chat* classes. In a
                # later PR we can provide a full-featured adapter.

                class LangChainWrapper:
                    def __init__(self, model, api_key, max_tokens, temperature):
                        if not api_key:
                            raise RuntimeError('Missing API key for Anthropic/Claude provider')
                        self._client = ChatAnthropic(model=model, anthropic_api_key=api_key)
                        # Store params for possible future use
                        self._max_tokens = max_tokens
                        self._temperature = temperature

                    def generate(self, prompt_text: str) -> str:
                        # Minimal call pattern; real implementation should map
                        # messages/roles and use appropriate client API.
                        resp = self._client.create(prompt=prompt_text)
                        return getattr(resp, 'text', str(resp))

                return LangChainWrapper(
                    model=llm_config.get('model') or Config.ANTHROPIC_MODEL,
                    api_key=api_key,
                    max_tokens=llm_config.get('max_tokens', Config.MAX_TOKENS),
                    temperature=llm_config.get('temperature', Config.TEMPERATURE),
                )

            elif provider == 'openai':
                from langchain_openai import ChatOpenAI  # type: ignore

                class LangChainWrapper:
                    def __init__(self, model, api_key, max_tokens, temperature):
                        if not api_key:
                            raise RuntimeError('Missing API key for OpenAI provider')
                        self._client = ChatOpenAI(model=model, openai_api_key=api_key)
                        self._max_tokens = max_tokens
                        self._temperature = temperature

                    def generate(self, prompt_text: str) -> str:
                        resp = self._client.create(prompt=prompt_text)
                        return getattr(resp, 'text', str(resp))

                return LangChainWrapper(
                    model=llm_config.get('model') or Config.OPENAI_MODEL,
                    api_key=api_key,
                    max_tokens=llm_config.get('max_tokens', Config.MAX_TOKENS),
                    temperature=llm_config.get('temperature', Config.TEMPERATURE),
                )

            elif provider == 'google':
                from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore

                class LangChainWrapper:
                    def __init__(self, model, api_key, max_tokens, temperature):
                        if not api_key:
                            raise RuntimeError('Missing API key for Google provider')
                        self._client = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
                        self._max_tokens = max_tokens
                        self._temperature = temperature

                    def generate(self, prompt_text: str) -> str:
                        resp = self._client.create(prompt=prompt_text)
                        return getattr(resp, 'text', str(resp))

                return LangChainWrapper(
                    model=llm_config.get('model') or Config.GOOGLE_MODEL,
                    api_key=api_key,
                    max_tokens=llm_config.get('max_tokens', Config.MAX_TOKENS),
                    temperature=llm_config.get('temperature', Config.TEMPERATURE),
                )

            else:
                raise RuntimeError(f"LLM provider not supported: {provider}")

        except Exception as e:
            raise RuntimeError("Could not initialize LLM provider: %s" % e)
