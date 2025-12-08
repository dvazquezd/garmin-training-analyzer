"""
Gestor de prompts para el sistema de análisis de entrenamiento.
Permite cargar y gestionar prompts desde archivos externos.
"""

import logging
from pathlib import Path
from typing import Optional


class PromptManager:
    """Gestor centralizado de prompts del sistema."""

    # ========================================
    # CONFIGURACIÓN
    # ========================================

    # Buscar prompts en la raíz del proyecto (un nivel arriba de src/)
    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    USER_PROMPT_FILE = "user_prompt_template.txt"

    # Cache de prompts para evitar lecturas repetidas
    _system_prompt_cache: Optional[str] = None
    _user_template_cache: Optional[str] = None

    # ========================================
    # MÉTODOS PÚBLICOS
    # ========================================

    @classmethod
    def get_system_prompt(cls, force_reload: bool = False) -> str:
        """
        Obtiene el system prompt desde el archivo.

        Args:
            force_reload: Si True, recarga el prompt desde el archivo
                         ignorando el cache

        Returns:
            str: Contenido del system prompt

        Raises:
            FileNotFoundError: Si el archivo de prompt no existe
            Exception: Si hay error al leer el archivo
        """
        if cls._system_prompt_cache is None or force_reload:
            cls._system_prompt_cache = cls._load_prompt_file(cls.SYSTEM_PROMPT_FILE)

        return cls._system_prompt_cache

    @classmethod
    def get_user_prompt_template(cls, force_reload: bool = False) -> str:
        """
        Obtiene el user prompt template desde el archivo.

        Args:
            force_reload: Si True, recarga el prompt desde el archivo
                         ignorando el cache

        Returns:
            str: Contenido del user prompt template

        Raises:
            FileNotFoundError: Si el archivo de prompt no existe
            Exception: Si hay error al leer el archivo
        """
        if cls._user_template_cache is None or force_reload:
            cls._user_template_cache = cls._load_prompt_file(cls.USER_PROMPT_FILE)

        return cls._user_template_cache

    @classmethod
    def reload_prompts(cls) -> None:
        """
        Recarga todos los prompts desde los archivos.
        Útil después de modificar los archivos de prompts.
        """
        cls._system_prompt_cache = None
        cls._user_template_cache = None

        # Forzar recarga
        cls.get_system_prompt(force_reload=True)
        cls.get_user_prompt_template(force_reload=True)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Prompts recargados desde archivos")

    @classmethod
    def validate_prompts(cls) -> tuple[bool, list[str]]:
        """
        Valida que los archivos de prompts existan y sean legibles.

        Returns:
            tuple: (es_valido, lista_de_errores)
        """
        errors = []

        # Verificar directorio
        if not cls.PROMPTS_DIR.exists():
            errors.append(f"Directorio de prompts no existe: {cls.PROMPTS_DIR}")
            return False, errors

        # Verificar archivo de system prompt
        system_path = cls.PROMPTS_DIR / cls.SYSTEM_PROMPT_FILE
        if not system_path.exists():
            errors.append(f"System prompt no existe: {system_path}")
        elif not system_path.is_file():
            errors.append(f"System prompt no es un archivo: {system_path}")
        else:
            try:
                content = system_path.read_text(encoding='utf-8')
                if not content.strip():
                    errors.append("System prompt está vacío")
            except Exception as e:
                errors.append(f"Error leyendo system prompt: {e}")

        # Verificar archivo de user template
        user_path = cls.PROMPTS_DIR / cls.USER_PROMPT_FILE
        if not user_path.exists():
            errors.append(f"User prompt template no existe: {user_path}")
        elif not user_path.is_file():
            errors.append(f"User prompt template no es un archivo: {user_path}")
        else:
            try:
                content = user_path.read_text(encoding='utf-8')
                if not content.strip():
                    errors.append("User prompt template está vacío")

                # Verificar placeholders esperados
                required_placeholders = ['{athlete_name}', '{activities_text}', '{training_plan_section}']
                missing = [ph for ph in required_placeholders if ph not in content]
                if missing:
                    errors.append(f"Faltan placeholders en user template: {', '.join(missing)}")

            except Exception as e:
                errors.append(f"Error leyendo user prompt template: {e}")

        return len(errors) == 0, errors

    @classmethod
    def get_prompts_info(cls) -> dict:
        """
        Obtiene información sobre los prompts cargados.

        Returns:
            dict: Información de los prompts (longitud, archivos, etc.)
        """
        try:
            system_prompt = cls.get_system_prompt()
            user_template = cls.get_user_prompt_template()

            return {
                "system_prompt": {
                    "file": str(cls.PROMPTS_DIR / cls.SYSTEM_PROMPT_FILE),
                    "length": len(system_prompt),
                    "lines": system_prompt.count('\n') + 1,
                    "cached": cls._system_prompt_cache is not None
                },
                "user_template": {
                    "file": str(cls.PROMPTS_DIR / cls.USER_PROMPT_FILE),
                    "length": len(user_template),
                    "lines": user_template.count('\n') + 1,
                    "placeholders": user_template.count('{'),
                    "cached": cls._user_template_cache is not None
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # ========================================
    # MÉTODOS PRIVADOS
    # ========================================

    @classmethod
    def _load_prompt_file(cls, filename: str) -> str:
        """
        Carga un archivo de prompt.

        Args:
            filename: Nombre del archivo a cargar

        Returns:
            str: Contenido del archivo

        Raises:
            FileNotFoundError: Si el archivo no existe
            Exception: Si hay error al leer
        """
        logger = logging.getLogger(__name__)
        file_path = cls.PROMPTS_DIR / filename

        if not file_path.exists():
            error_msg = f"Archivo de prompt no encontrado: {file_path}"
            logger.error(f"❌ {error_msg}")
            raise FileNotFoundError(error_msg)

        try:
            content = file_path.read_text(encoding='utf-8')
            logger.debug(f"✅ Prompt cargado: {filename} ({len(content)} caracteres)")
            return content
        except Exception as e:
            error_msg = f"Error leyendo archivo de prompt {filename}: {e}"
            logger.error(f"❌ {error_msg}")
            raise


# ========================================
# FUNCIÓN DE UTILIDAD
# ========================================

def verify_prompts_setup() -> None:
    """
    Verifica y muestra la configuración de prompts.
    Útil para debugging y setup inicial.
    """
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DE PROMPTS")
    print("=" * 60)

    # Validar prompts
    is_valid, errors = PromptManager.validate_prompts()

    if is_valid:
        print("\n✅ Configuración válida\n")

        # Mostrar información
        info = PromptManager.get_prompts_info()

        print("📄 System Prompt:")
        print(f"   Archivo: {info['system_prompt']['file']}")
        print(f"   Longitud: {info['system_prompt']['length']} caracteres")
        print(f"   Líneas: {info['system_prompt']['lines']}")

        print("\n📝 User Prompt Template:")
        print(f"   Archivo: {info['user_template']['file']}")
        print(f"   Longitud: {info['user_template']['length']} caracteres")
        print(f"   Líneas: {info['user_template']['lines']}")
        print(f"   Placeholders: {info['user_template']['placeholders']}")

        # Mostrar preview
        print("\n👀 Preview del System Prompt (primeras 200 caracteres):")
        system_prompt = PromptManager.get_system_prompt()
        if system_prompt:  # pylint: disable=unsubscriptable-object
            print(f"   {system_prompt[:200]}...")
        else:
            print("   (No disponible)")
    else:
        print("\n❌ Errores encontrados:")
        for error in errors:
            print(f"   - {error}")


if __name__ == "__main__":
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Ejecutar verificación
    verify_prompts_setup()