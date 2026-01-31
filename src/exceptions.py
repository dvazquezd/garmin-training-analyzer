"""Módulo de excepciones compartidas para evitar problemas de identidad en tests."""


class ConfigError(RuntimeError):
    """Error relacionado con la configuración."""
    pass
