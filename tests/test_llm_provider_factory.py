import sys
import types
from types import SimpleNamespace

from src.llm_provider import LLMFactory


def test_factory_returns_claude_provider(monkeypatch):
    """LLMFactory should return a provider wrapping the langchain_anthropic ChatAnthropic (claude)."""

    class FakeChatAnthropic:
        def __init__(self, model, anthropic_api_key):
            self.model = model
            self.key = anthropic_api_key

        def invoke(self, messages):
            # Extract content from HumanMessage
            prompt = messages[0].content if messages else ""
            return SimpleNamespace(content=f"CLAUDE_OK: {prompt}")

    fake_module = types.SimpleNamespace(ChatAnthropic=FakeChatAnthropic)
    monkeypatch.setitem(sys.modules, 'langchain_anthropic', fake_module)

    cfg = {
        'provider': 'claude',
        'model': 'claude-2',
        'api_key': 'fake-key',
        'max_tokens': 128,
        'temperature': 0.2,
    }

    provider = LLMFactory.get_provider(cfg)
    assert hasattr(provider, 'generate')
    assert provider.generate('hola') == 'CLAUDE_OK: hola'
