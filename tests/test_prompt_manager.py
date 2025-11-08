"""
Tests para el gestor de prompts (src/prompt_manager.py).
"""

import pytest
from pathlib import Path
from src.prompt_manager import PromptManager


class TestPromptManager:
    """Tests para la clase PromptManager."""

    def test_prompts_dir_exists(self):
        """Test que el directorio de prompts existe."""
        assert PromptManager.PROMPTS_DIR.exists()
        assert PromptManager.PROMPTS_DIR.is_dir()

    def test_get_system_prompt(self):
        """Test que get_system_prompt retorna contenido válido."""
        system_prompt = PromptManager.get_system_prompt()

        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        # Verificar que contiene texto esperado del prompt
        assert 'análisis' in system_prompt.lower() or 'entrenamientos' in system_prompt.lower()

    def test_get_user_prompt_template(self):
        """Test que get_user_prompt_template retorna contenido válido."""
        user_template = PromptManager.get_user_prompt_template()

        assert isinstance(user_template, str)
        assert len(user_template) > 0

    def test_prompt_caching(self):
        """Test que los prompts se cachean correctamente."""
        # Primera llamada
        prompt1 = PromptManager.get_system_prompt()
        # Segunda llamada (debería usar cache)
        prompt2 = PromptManager.get_system_prompt()

        assert prompt1 == prompt2
        assert PromptManager._system_prompt_cache is not None

    def test_force_reload(self):
        """Test que force_reload recarga el prompt desde archivo."""
        # Cargar con cache
        prompt1 = PromptManager.get_system_prompt()

        # Forzar recarga
        prompt2 = PromptManager.get_system_prompt(force_reload=True)

        assert prompt1 == prompt2  # Contenido debería ser el mismo
        assert PromptManager._system_prompt_cache is not None

    def test_reload_prompts(self):
        """Test que reload_prompts recarga todos los prompts."""
        # Asegurar que hay cache
        PromptManager.get_system_prompt()
        PromptManager.get_user_prompt_template()

        assert PromptManager._system_prompt_cache is not None
        assert PromptManager._user_template_cache is not None

        # Limpiar cache
        PromptManager._system_prompt_cache = None
        PromptManager._user_template_cache = None

        # Recargar
        PromptManager.reload_prompts()

        assert PromptManager._system_prompt_cache is not None
        assert PromptManager._user_template_cache is not None

    def test_validate_prompts_success(self):
        """Test que validate_prompts retorna True para configuración válida."""
        is_valid, errors = PromptManager.validate_prompts()

        assert is_valid is True
        assert len(errors) == 0

    def test_get_prompts_info(self):
        """Test que get_prompts_info retorna información correcta."""
        info = PromptManager.get_prompts_info()

        assert 'system_prompt' in info
        assert 'user_template' in info

        # Verificar estructura de system_prompt
        assert 'file' in info['system_prompt']
        assert 'length' in info['system_prompt']
        assert 'lines' in info['system_prompt']

        # Verificar estructura de user_template
        assert 'file' in info['user_template']
        assert 'length' in info['user_template']
        assert 'lines' in info['user_template']
        assert 'placeholders' in info['user_template']

        # Verificar valores
        assert info['system_prompt']['length'] > 0
        assert info['user_template']['length'] > 0

    def test_system_prompt_file_exists(self):
        """Test que el archivo de system prompt existe."""
        file_path = PromptManager.PROMPTS_DIR / PromptManager.SYSTEM_PROMPT_FILE
        assert file_path.exists()
        assert file_path.is_file()

    def test_user_prompt_file_exists(self):
        """Test que el archivo de user prompt existe."""
        file_path = PromptManager.PROMPTS_DIR / PromptManager.USER_PROMPT_FILE
        assert file_path.exists()
        assert file_path.is_file()

    def test_load_nonexistent_file(self):
        """Test que _load_prompt_file lanza FileNotFoundError para archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            PromptManager._load_prompt_file('nonexistent_file.txt')
