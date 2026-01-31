## Context

El proyecto tiene código Python en `src/` con cobertura inconsistente de docstrings. Algunos métodos públicos tienen documentación completa, otros tienen documentación parcial, y algunos carecen completamente de ella. Esto afecta la mantenibilidad y la experiencia del desarrollador.

El codebase ya usa type hints en varios lugares, lo cual complementará bien los docstrings. El proyecto parece seguir el estilo Google para los docstrings existentes.

## Goals / Non-Goals

**Goals:**
- Agregar docstrings completos a todos los métodos públicos en los 6 archivos prioritarios
- Seguir el formato Google docstring de manera consistente
- Documentar parámetros, valores de retorno y excepciones donde aplique
- Mejorar la documentación de clases públicas

**Non-Goals:**
- No documentar métodos privados (que empiezan con `_`) - solo si son especialmente complejos
- No generar documentación automática con herramientas externas (Sphinx, etc.) en este cambio
- No refactorizar código - solo agregar documentación
- No modificar type hints existentes - solo agregar docstrings

## Decisions

### Decision 1: Usar formato Google docstring

**Enfoque elegido**: Google docstring format (no NumPy style)

**Rationale**:
- El código existente que tiene docstrings ya usa estilo Google
- Es más conciso que NumPy style
- Ampliamente soportado por IDEs (VSCode, PyCharm)
- Fácil de leer en código fuente sin procesar

**Formato ejemplo**:
```python
def method_name(param1: str, param2: int) -> bool:
    """Brief one-line description.

    Optional longer description if needed to explain
    the method's behavior in more detail.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
```

### Decision 2: Priorizar archivos core

**Enfoque elegido**: Documentar completamente 6 archivos prioritarios primero

**Rationale**:
- Estos archivos son las interfaces públicas principales del proyecto
- Mayor ROI en términos de comprensibilidad
- Permite completar el cambio de manera incremental

**Orden de prioridad**:
1. `config.py` - Configuración es punto de entrada
2. `garmin_client.py` - Cliente principal de API externa
3. `llm_analizer.py` - Lógica core de análisis
4. `prompt_manager.py` - Gestión de prompts
5. `cache_manager.py` - Infraestructura de caching
6. `html_reporter.py` - Generación de reportes

### Decision 3: Documentar solo métodos públicos

**Enfoque elegido**: Enfocarse en métodos públicos (no empiezan con `_`)

**Rationale**:
- Los métodos públicos forman la API que otros desarrolladores usarán
- Los métodos privados son detalles de implementación
- Reduce el scope y hace el cambio más manejable

**Excepciones**: Documentar métodos privados solo si:
- Son especialmente complejos
- Son llamados desde múltiples lugares
- Tienen lógica no obvia

### Decision 4: No modificar code existente

**Enfoque elegido**: Solo agregar docstrings, no refactorizar

**Rationale**:
- Mantiene el cambio enfocado y de bajo riesgo
- Evita introducir bugs
- Facilita code review
- Los docstrings pueden agregarse sin afectar tests existentes

## Risks / Trade-offs

**[Riesgo]** Docstrings pueden quedar desactualizados si el código cambia → **Mitigación**: Agregar nota en CONTRIBUTING.md sobre mantener docstrings actualizados. Considerar agregar lint rules que verifiquen presencia de docstrings.

**[Riesgo]** Formato inconsistente si diferentes personas contribuyen → **Mitigación**: Documentar el formato en este design doc y referenciar en PRs futuros. Considerar agregar `pydocstyle` al CI.

**[Trade-off]** Tiempo invertido en documentación vs nuevas features → **Aceptable**: La documentación es inversión en mantenibilidad a largo plazo. Los 6 archivos prioritarios son scope razonable.

**[Trade-off]** Docstrings agregan líneas de código → **Aceptable**: El beneficio en comprensibilidad supera el incremento en LOC. Los docstrings no afectan performance en runtime.
