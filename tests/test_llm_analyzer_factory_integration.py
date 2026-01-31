from unittest.mock import MagicMock

from src.llm_analizer import LLMAnalyzer
from src import llm_provider


def test_llm_analyzer_uses_factory_provider_by_default(monkeypatch):
    fake_provider = MagicMock()
    fake_provider.generate.return_value = '## Resultado simulado'

    # Replace factory to return our fake provider
    monkeypatch.setattr(llm_provider.LLMFactory, 'get_provider', staticmethod(lambda cfg: fake_provider))

    analyzer = LLMAnalyzer()

    # Build minimal activity set
    class A:
        name = 'Run'
        activity_type = 'running'
        date = '2026-01-01'
        distance_km = 5.0
        duration_minutes = 30
        avg_heart_rate = None
        max_heart_rate = None
        calories = None
        avg_speed = None
        elevation_gain = None

    result = analyzer.analyze_training([A()], [{}], {'name': 'Test'}, [])

    assert result == '## Resultado simulado'
    assert fake_provider.generate.called
