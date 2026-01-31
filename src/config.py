"""Configuracion centralizada del sistema con validación y carga controlada.

Se provee una implementación mínima de `Config` basada en dataclass para mejorar
la testabilidad y permitir validaciones más estrictas. Mantiene compatibilidad
con la API previa mediante métodos de clase que actualizan atributos de clase
al cargar la configuración.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Error relacionado con la configuración."""


def _parse_bool(value: str | bool | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "on")


@dataclass
class ConfigSchema:
    garmin_email: str = ""
    garmin_password: str = ""

    # LLM
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"
    google_model: str = "gemini-2.0-flash-exp"
    max_tokens: int = 3000
    temperature: float = 0.7

    # Analysis
    analysis_days: int = 30

    # Cache
    use_cache: bool = True
    cache_ttl_hours: int = 24

    # Logging
    log_level: str = "INFO"

    def __post_init__(self):
        # Normalize provider string
        self.llm_provider = (self.llm_provider or "anthropic").lower()

        # Validate ranges
        if not (0.0 <= float(self.temperature) <= 1.0):
            raise ValueError("TEMPERATURE must be between 0.0 and 1.0")

        if not (1 <= int(self.max_tokens) <= 8000):
            raise ValueError("MAX_TOKENS out of expected range")

        if not (1 <= int(self.analysis_days) <= 365):
            raise ValueError("ANALYSIS_DAYS out of range 1-365")

    def ensure_valid(self) -> None:
        """Raise ConfigError if this schema is invalid."""
        errors = []
        if not self.garmin_email:
            errors.append('GARMIN_EMAIL: missing')
        if not self.garmin_password:
            errors.append('GARMIN_PASSWORD: missing')

        if self.llm_provider == 'anthropic' and not self.anthropic_api_key:
            errors.append('ANTHROPIC_API_KEY missing')
        if self.llm_provider == 'openai' and not self.openai_api_key:
            errors.append('OPENAI_API_KEY missing')
        if self.llm_provider == 'google' and not self.google_api_key:
            errors.append('GOOGLE_API_KEY missing')

        if errors:
            raise ConfigError('Configuration invalid: ' + '; '.join(errors))


class Config:
    """Compatible facade for configuration used across the codebase.

    Use `Config.load()` to create and validate a configuration instance.
    Accessors like `Config.get_llm_config()` continue to work and will read
    from the loaded instance when present.
    """

    # Backwards-compatible class attributes (defaults)
    GARMIN_EMAIL: str = ""
    GARMIN_PASSWORD: str = ""

    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    OPENAI_MODEL: str = "gpt-4o"
    GOOGLE_MODEL: str = "gemini-2.0-flash-exp"
    MAX_TOKENS: int = 3000
    TEMPERATURE: float = 0.7

    ANALYSIS_DAYS: int = 30

    BASE_DIR: Path = Path(__file__).parent
    OUTPUT_DIR: Path = BASE_DIR / os.getenv('OUTPUT_DIR', 'analysis_reports')
    TRAINING_PLAN_PATH: str = os.getenv('TRAINING_PLAN_PATH', 'plan_trainingpeaks.txt')

    LOG_LEVEL: str = 'INFO'
    LOG_FILE: Path = BASE_DIR / 'training_analyzer.log'

    # Internal loaded instance
    _instance: Optional[ConfigSchema] = None

    @classmethod
    def load(cls, env_file: Optional[str] = None, cli_args: Optional[dict] = None) -> ConfigSchema:
        """Carga la configuración desde entorno o un archivo `.env`.

        Args:
            env_file: ruta opcional a un archivo .env
            cli_args: dict de overrides desde CLI (opcional)

        Returns:
            ConfigSchema: instancia cargada y validada
        """
        # Only load a specific .env file when explicitly provided to avoid
        # importing environment from repository-level files during tests.
        if env_file:
            load_dotenv(env_file)

        # Helper to read env with fallback to CLI args
        def _get(key: str, default=None):
            if cli_args and key in cli_args:
                return cli_args[key]
            return os.getenv(key, default)

        # Parse values
        garmin_email = _get('GARMIN_EMAIL', '')
        garmin_password = _get('GARMIN_PASSWORD', '')
        llm_provider = _get('LLM_PROVIDER', 'anthropic')
        anthropic_api_key = _get('ANTHROPIC_API_KEY', '')
        openai_api_key = _get('OPENAI_API_KEY', '')
        google_api_key = _get('GOOGLE_API_KEY', '')
        anthropic_model = _get('ANTHROPIC_MODEL', cls.ANTHROPIC_MODEL)
        openai_model = _get('OPENAI_MODEL', cls.OPENAI_MODEL)
        google_model = _get('GOOGLE_MODEL', cls.GOOGLE_MODEL)

        max_tokens = int(_get('MAX_TOKENS', cls.MAX_TOKENS))
        temperature = float(_get('TEMPERATURE', cls.TEMPERATURE))
        analysis_days = int(_get('ANALYSIS_DAYS', cls.ANALYSIS_DAYS))

        use_cache = _parse_bool(_get('USE_CACHE', str(True)))
        cache_ttl_hours = int(_get('CACHE_TTL_HOURS', cls._default_cache_ttl()))

        log_level = _get('LOG_LEVEL', cls.LOG_LEVEL)

        instance = ConfigSchema(
            garmin_email=garmin_email,
            garmin_password=garmin_password,
            llm_provider=llm_provider,
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key,
            google_api_key=google_api_key,
            anthropic_model=anthropic_model,
            openai_model=openai_model,
            google_model=google_model,
            max_tokens=max_tokens,
            temperature=temperature,
            analysis_days=analysis_days,
            use_cache=use_cache,
            cache_ttl_hours=cache_ttl_hours,
            log_level=log_level
        )

        # Store instance and update class attrs for backwards compatibility
        cls._instance = instance
        cls._sync_class_attrs(instance)

        return instance

    @classmethod
    def _default_cache_ttl(cls) -> int:
        return 24

    @classmethod
    def _sync_class_attrs(cls, instance: ConfigSchema) -> None:
        """Update legacy class attributes from the loaded instance."""
        cls.GARMIN_EMAIL = instance.garmin_email
        cls.GARMIN_PASSWORD = instance.garmin_password

        cls.LLM_PROVIDER = instance.llm_provider
        cls.ANTHROPIC_API_KEY = instance.anthropic_api_key
        cls.OPENAI_API_KEY = instance.openai_api_key
        cls.GOOGLE_API_KEY = instance.google_api_key
        cls.ANTHROPIC_MODEL = instance.anthropic_model
        cls.OPENAI_MODEL = instance.openai_model
        cls.GOOGLE_MODEL = instance.google_model
        cls.MAX_TOKENS = instance.max_tokens
        cls.TEMPERATURE = instance.temperature

        cls.ANALYSIS_DAYS = instance.analysis_days
        cls.LOG_LEVEL = instance.log_level

    @classmethod
    def get_llm_config(cls) -> dict:
        """Return a dict with provider/model/api_key for the current configuration."""
        if cls._instance:
            provider = cls._instance.llm_provider
            models = {
                'anthropic': (cls._instance.anthropic_api_key, cls._instance.anthropic_model),
                'openai': (cls._instance.openai_api_key, cls._instance.openai_model),
                'google': (cls._instance.google_api_key, cls._instance.google_model),
            }
            api_key, model = models.get(provider, models['anthropic'])
            return {'api_key': api_key, 'model': model, 'provider': provider}

        # Fallback to legacy class attrs
        provider = cls.LLM_PROVIDER
        configs = {
            'anthropic': {'api_key': cls.ANTHROPIC_API_KEY, 'model': cls.ANTHROPIC_MODEL, 'provider': 'anthropic'},
            'openai': {'api_key': cls.OPENAI_API_KEY, 'model': cls.OPENAI_MODEL, 'provider': 'openai'},
            'google': {'api_key': cls.GOOGLE_API_KEY, 'model': cls.GOOGLE_MODEL, 'provider': 'google'},
        }
        return configs.get(provider, configs['anthropic'])

    @classmethod
    def validate(cls) -> Tuple[bool, list[str]]:
        """Validate the current configuration and return (ok, errors)."""
        instance = cls._instance or cls.load()
        errors = []

        if not instance.garmin_email:
            errors.append('GARMIN_EMAIL: missing')
        if not instance.garmin_password:
            errors.append('GARMIN_PASSWORD: missing')

        # Ensure provider has API key
        if instance.llm_provider == 'anthropic' and not instance.anthropic_api_key:
            errors.append('ANTHROPIC_API_KEY missing')
        if instance.llm_provider == 'openai' and not instance.openai_api_key:
            errors.append('OPENAI_API_KEY missing')
        if instance.llm_provider == 'google' and not instance.google_api_key:
            errors.append('GOOGLE_API_KEY missing')

        return (len(errors) == 0, errors)

    @classmethod
    def ensure_valid(cls) -> None:
        """Raise ConfigError if config is invalid."""
        ok, errors = cls.validate()
        if not ok:
            raise ConfigError("Configuration invalid: " + "; ".join(errors))


if __name__ == '__main__':
    # Simple CLI-like verification (kept minimal for library use)
    import logging

    logging.basicConfig(level=logging.INFO)
    cfg = Config.load()

    try:
        cfg_obj = cfg
        ok, errs = Config.validate()
        if ok:
            logging.info('Config valid')
        else:
            logging.error('Config invalid: %s', errs)
    except Exception as e:
        logging.exception('Error validating configuration: %s', e)

