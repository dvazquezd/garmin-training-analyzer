import os
import types
import sys
from types import SimpleNamespace

from src.llm_provider import LLMFactory


def test_factory_reads_api_key_from_env_for_anthropic(monkeypatch):
    """If llm_config lacks api_key, factory should read ANTHROPIC_API_KEY env var."""
    # Ensure no api_key in config
    cfg = {'provider': 'anthropic', 'model': 'claude-2'}

    # Provide fake module
    class FakeChatAnthropic:
        def __init__(self, model, anthropic_api_key):
            self.model = model
            self.key = anthropic_api_key

        def create(self, prompt):
            return SimpleNamespace(text=f"CLAUDE_OK: {self.key}:{prompt}")

    fake_module = types.SimpleNamespace(ChatAnthropic=FakeChatAnthropic)
    monkeypatch.setitem(sys.modules, 'langchain_anthropic', fake_module)

    monkeypatch.setenv('ANTHROPIC_API_KEY', 'env-key-123')

    provider = LLMFactory.get_provider(cfg)
    assert provider.generate('hola') == 'CLAUDE_OK: env-key-123:hola'


def test_factory_reads_api_key_from_env_for_openai(monkeypatch):
    cfg = {'provider': 'openai', 'model': 'gpt-4o'}

    class FakeOpenAI:
        def __init__(self, model, openai_api_key):
            self.model = model
            self.key = openai_api_key

        def create(self, prompt):
            return SimpleNamespace(text=f"OPENAI_OK: {self.key}:{prompt}")

    fake_module = types.SimpleNamespace(ChatOpenAI=FakeOpenAI)
    monkeypatch.setitem(sys.modules, 'langchain_openai', fake_module)

    monkeypatch.setenv('OPENAI_API_KEY', 'open-env-456')

    provider = LLMFactory.get_provider(cfg)
    assert provider.generate('hola') == 'OPENAI_OK: open-env-456:hola'
