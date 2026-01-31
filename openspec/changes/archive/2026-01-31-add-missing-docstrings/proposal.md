## Why

Varios métodos públicos en `src/` carecen de docstrings, lo que dificulta la comprensión del código, el mantenimiento y la generación de documentación automática. Los docstrings son esenciales para que otros desarrolladores (y herramientas como IDEs) entiendan rápidamente qué hace cada método, sus parámetros y valores de retorno.

## What Changes

- Agregar docstrings faltantes a métodos públicos en archivos de `src/`
- Seguir el formato Google/NumPy docstring con secciones Args, Returns, Raises cuando aplique
- Priorizar métodos en las clases principales: `Config`, `VisualizationManager`, `GarminClient`, `PromptManager`, `CacheManager`
- Asegurar que todos los métodos públicos (que no empiezan con `_`) tengan documentación descriptiva

## Capabilities

### New Capabilities
<!-- No new capabilities - this is a documentation improvement -->

### Modified Capabilities
- `code-documentation`: Los métodos públicos ahora tienen documentación completa y consistente que describe su propósito, parámetros y valores de retorno

## Impact

- `src/config.py`: Agregar docstrings a métodos públicos de la clase `Config`
- `src/visualizations.py`: Completar docstrings faltantes en `VisualizationManager`
- `src/garmin_client.py`: Revisar y completar docstrings en `GarminClient`
- `src/prompt_manager.py`: Agregar docstrings a métodos de `PromptManager`
- `src/cache_manager.py`: Documentar métodos públicos de `CacheManager`
- `src/html_reporter.py`: Agregar docstrings a métodos de reporting
