"""
Tests para el módulo de configuración (src/config.py).
"""

import pytest
from src.config import Config


class TestConfig:
    """Tests para la clase Config."""

    def test_config_loads_from_env(self, mock_env_vars):
        """Test que Config carga correctamente desde variables de entorno."""
        # Recargar Config para que tome las variables mockeadas
        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        assert Config.GARMIN_EMAIL == 'test@example.com'
        assert Config.GARMIN_PASSWORD == 'test_password'
        assert Config.LLM_PROVIDER == 'anthropic'
        assert Config.ANTHROPIC_API_KEY == 'test-api-key-123'
        assert Config.ANALYSIS_DAYS == 30
        assert Config.MAX_TOKENS == 3000
        assert Config.TEMPERATURE == 0.7

    def test_get_llm_config_anthropic(self, mock_env_vars, monkeypatch):
        """Test que get_llm_config retorna configuración de Anthropic."""
        monkeypatch.setenv('LLM_PROVIDER', 'anthropic')

        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        llm_config = Config.get_llm_config()

        assert llm_config['provider'] == 'anthropic'
        assert llm_config['api_key'] == 'test-api-key-123'
        assert llm_config['model'] == Config.ANTHROPIC_MODEL

    def test_get_llm_config_openai(self, mock_env_vars, monkeypatch):
        """Test que get_llm_config retorna configuración de OpenAI."""
        monkeypatch.setenv('LLM_PROVIDER', 'openai')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-openai-key')

        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        llm_config = Config.get_llm_config()

        assert llm_config['provider'] == 'openai'
        assert llm_config['api_key'] == 'test-openai-key'
        assert llm_config['model'] == Config.OPENAI_MODEL

    def test_get_llm_config_google(self, mock_env_vars, monkeypatch):
        """Test que get_llm_config retorna configuración de Google."""
        monkeypatch.setenv('LLM_PROVIDER', 'google')
        monkeypatch.setenv('GOOGLE_API_KEY', 'test-google-key')

        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        llm_config = Config.get_llm_config()

        assert llm_config['provider'] == 'google'
        assert llm_config['api_key'] == 'test-google-key'
        assert llm_config['model'] == Config.GOOGLE_MODEL

    def test_validate_success(self, mock_env_vars):
        """Test que validate retorna True con configuración válida."""
        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        is_valid, errors = Config.validate()

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_garmin_email(self, mock_env_vars, monkeypatch):
        """Test que validate detecta falta de email de Garmin."""
        monkeypatch.setenv('GARMIN_EMAIL', '')

        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        is_valid, errors = Config.validate()

        assert is_valid is False
        assert any('GARMIN_EMAIL' in error for error in errors)

    def test_validate_missing_api_key(self, mock_env_vars, monkeypatch):
        """Test que validate detecta falta de API key del proveedor activo."""
        monkeypatch.setenv('ANTHROPIC_API_KEY', '')

        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        is_valid, errors = Config.validate()

        assert is_valid is False
        assert any('API_KEY' in error for error in errors)

    def test_default_values(self, monkeypatch):
        """Test que Config tiene valores por defecto apropiados."""
        # Limpiar variables de entorno
        for key in ['ANALYSIS_DAYS', 'MAX_TOKENS', 'TEMPERATURE', 'LLM_PROVIDER']:
            monkeypatch.delenv(key, raising=False)

        from importlib import reload
        from src import config
        reload(config)
        from src.config import Config

        assert Config.ANALYSIS_DAYS == 30
        assert Config.MAX_TOKENS == 3000
        assert Config.TEMPERATURE == 0.7
        assert Config.LLM_PROVIDER == 'anthropic'
