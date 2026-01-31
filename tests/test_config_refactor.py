import os
import pytest
from pathlib import Path

from src.config import Config, ConfigError


def test_default_values_when_no_env(monkeypatch):
    """Scenario: Defaults when no env file."""
    # Clear potentially present env vars
    for k in [
        'GARMIN_EMAIL', 'GARMIN_PASSWORD', 'ANALYSIS_DAYS', 'MAX_TOKENS',
        'TEMPERATURE', 'USE_CACHE', 'CACHE_TTL_HOURS'
    ]:
        monkeypatch.delenv(k, raising=False)

    cfg = Config.load()

    assert cfg.analysis_days == 30
    assert cfg.max_tokens == 3000
    assert abs(cfg.temperature - 0.7) < 1e-6
    assert cfg.use_cache is True
    assert cfg.cache_ttl_hours == 24


def test_load_config_from_env_file(tmp_path):
    """Scenario: Load from .env file"""
    env = tmp_path / ".env"
    env.write_text("""
GARMIN_EMAIL=user@example.com
GARMIN_PASSWORD=mypass
ANALYSIS_DAYS=60
MAX_TOKENS=4000
USE_CACHE=false
CACHE_TTL_HOURS=12
""")

    cfg = Config.load(env_file=str(env))

    assert cfg.garmin_email == 'user@example.com'
    assert cfg.garmin_password == 'mypass'
    assert cfg.analysis_days == 60
    assert cfg.max_tokens == 4000
    assert cfg.use_cache is False
    assert cfg.cache_ttl_hours == 12


def test_missing_required_fields_raises_error(monkeypatch):
    """Scenario: Missing required fields should raise ConfigError on ensure_valid"""
    monkeypatch.delenv('GARMIN_EMAIL', raising=False)
    monkeypatch.setenv('GARMIN_PASSWORD', 'pass')

    cfg = Config.load()

    with pytest.raises(ConfigError):
        cfg.ensure_valid()


def test_invalid_type_raises_error(monkeypatch):
    """Scenario: Invalid type for ANALYSIS_DAYS should raise ValueError during load"""
    monkeypatch.setenv('ANALYSIS_DAYS', 'abc')

    with pytest.raises(ValueError):
        Config.load()
