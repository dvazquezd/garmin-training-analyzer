"""
Configuracion del sistema con soporte multi-LLM.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuracion centralizada de la aplicacion."""

    # Credenciales Garmin
    GARMIN_EMAIL: str = os.getenv('GARMIN_EMAIL', '')
    GARMIN_PASSWORD: str = os.getenv('GARMIN_PASSWORD', '')

    # ========================================
    # CONFIGURACIÓN DE LLM
    # ========================================
    LLM_PROVIDER: str = os.getenv('LLM_PROVIDER', 'anthropic').lower()

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')

    # Modelos por defecto
    ANTHROPIC_MODEL: str = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o')
    GOOGLE_MODEL: str = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')

    # Parametros de LLM
    MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', '3000'))
    TEMPERATURE: float = float(os.getenv('TEMPERATURE', '0.7'))

    # Parametros de analisis
    ANALYSIS_DAYS: int = int(os.getenv('ANALYSIS_DAYS', '30'))

    # Rutas
    BASE_DIR: Path = Path(__file__).parent
    OUTPUT_DIR: Path = BASE_DIR / os.getenv('OUTPUT_DIR', 'analysis_reports')
    TRAINING_PLAN_PATH: str = os.getenv('TRAINING_PLAN_PATH', 'plan_trainingpeaks.txt')

    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: Path = BASE_DIR / 'training_analyzer.log'

    @classmethod
    def get_llm_config(cls) -> dict:
        """Obtiene configuracion del LLM actual."""
        provider = cls.LLM_PROVIDER

        configs = {
            'anthropic': {
                'api_key': cls.ANTHROPIC_API_KEY,
                'model': cls.ANTHROPIC_MODEL,
                'provider': 'anthropic'
            },
            'openai': {
                'api_key': cls.OPENAI_API_KEY,
                'model': cls.OPENAI_MODEL,
                'provider': 'openai'
            },
            'google': {
                'api_key': cls.GOOGLE_API_KEY,
                'model': cls.GOOGLE_MODEL,
                'provider': 'google'
            }
        }

        return configs.get(provider, configs['anthropic'])

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """Valida la configuracion."""
        errors = []

        if not cls.GARMIN_EMAIL:
            errors.append("GARMIN_EMAIL no configurado")
        if not cls.GARMIN_PASSWORD:
            errors.append("GARMIN_PASSWORD no configurado")

        # Validar que el proveedor de LLM tenga API key
        llm_config = cls.get_llm_config()
        if not llm_config.get('api_key'):
            errors.append(f"{cls.LLM_PROVIDER.upper()}_API_KEY no configurado")

        return len(errors) == 0, errors


if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 60)

    is_valid, errors = Config.validate()

    if is_valid:
        print(" Configuracion valida")
        print(f"\nGarmin:")
        print(f"  Email: {Config.GARMIN_EMAIL}")
        print(f"\nLLM:")
        print(f"  Proveedor: {Config.LLM_PROVIDER}")
        llm_config = Config.get_llm_config()
        print(f"  Modelo: {llm_config['model']}")
        print(f"  API Key configurada: Si")

        print(f"\nAnalisis:")
        print(f"  Dias: {Config.ANALYSIS_DAYS}")
        print(f"  Max tokens: {Config.MAX_TOKENS}")
        print(f"  Temperature: {Config.TEMPERATURE}")
    else:
        print(" Errores en configuracion:")
        for error in errors:
            print(f"   - {error}")
