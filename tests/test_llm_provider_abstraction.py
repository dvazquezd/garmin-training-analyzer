import pytest
from unittest.mock import MagicMock

from src.llm_analizer import LLMAnalyzer


def make_fake_activity():
    class A:
        name = 'Morning Run'
        activity_type = 'running'
        date = '2025-01-30'
        distance_km = 10.5
        duration_minutes = 54
        avg_heart_rate = 145
        max_heart_rate = 178
        calories = 650
        avg_speed = 3.22
        elevation_gain = 120
    return A()


def test_llm_analyzer_uses_injected_provider():
    """When a provider is injected, LLMAnalyzer should call provider.generate and return its result."""
    # Arrange
    fake_provider = MagicMock()
    fake_provider.generate.return_value = "## Análisis simulado"

    analyzer = LLMAnalyzer(provider=fake_provider)

    activities = [make_fake_activity()]
    details = [{}]
    profile = {'name': 'Test User'}
    body_comp = []

    # Act
    result = analyzer.analyze_training(activities, details, profile, body_comp)

    # Assert
    assert result == "## Análisis simulado"
    assert fake_provider.generate.called
    args, kwargs = fake_provider.generate.call_args
    assert 'ACTIVIDADES' in args[0] or 'ACTIVIDADES' in args[0].upper()


def test_llm_analyzer_with_provider_error_returns_none():
    """If provider.generate raises, analyzer should catch and return None."""
    fake_provider = MagicMock()
    fake_provider.generate.side_effect = Exception("Provider error")

    analyzer = LLMAnalyzer(provider=fake_provider)

    activities = [make_fake_activity()]
    details = [{}]
    profile = {'name': 'Test User'}
    body_comp = []

    result = analyzer.analyze_training(activities, details, profile, body_comp)

    assert result is None
