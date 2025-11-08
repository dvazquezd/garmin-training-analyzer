# Tests

Este directorio contiene los tests unitarios para el proyecto Garmin Training Analyzer.

## Estructura

```
tests/
├── __init__.py              # Inicialización del módulo de tests
├── conftest.py              # Fixtures comunes y configuración de pytest
├── test_config.py           # Tests para src/config.py
├── test_garmin_client.py    # Tests para src/garmin_client.py
├── test_prompt_manager.py   # Tests para src/prompt_manager.py
└── README.md                # Este archivo
```

## Ejecutar los tests

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con verbosidad

```bash
pytest -v
```

### Ejecutar tests con coverage

```bash
pytest --cov=src --cov-report=html
```

### Ejecutar un archivo específico

```bash
pytest tests/test_config.py
```

### Ejecutar un test específico

```bash
pytest tests/test_config.py::TestConfig::test_config_loads_from_env
```

## Dependencias

Asegúrate de tener instaladas las dependencias de testing:

```bash
pip install pytest pytest-cov pytest-mock
```

## Convenciones

- Cada módulo de código en `src/` debe tener su correspondiente archivo `test_*.py`
- Los tests se organizan en clases con el prefijo `Test`
- Cada método de test debe tener el prefijo `test_`
- Usar fixtures de `conftest.py` para datos de prueba comunes
- Usar `pytest-mock` para mockear dependencias externas (APIs, etc.)

## Fixtures Disponibles

Ver `conftest.py` para la lista completa de fixtures. Principales:

- `mock_env_vars`: Variables de entorno mockeadas
- `sample_activity_data`: Datos de actividad de ejemplo
- `sample_body_composition`: Datos de composición corporal
- `sample_user_profile`: Perfil de usuario de ejemplo
- `temp_output_dir`: Directorio temporal para outputs de test

## Cobertura de Tests

Objetivo: >80% de cobertura de código

Actualmente cubierto:
- ✅ src/config.py
- ✅ src/garmin_client.py
- ✅ src/prompt_manager.py
- ⏳ src/llm_analizer.py (pendiente)
- ⏳ training_analyzer.py (pendiente)
