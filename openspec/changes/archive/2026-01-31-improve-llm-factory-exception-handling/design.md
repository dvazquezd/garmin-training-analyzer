## Context

El método `LLMFactory.get_provider()` en `src/llm_provider.py` actualmente usa un bloque try/except genérico (líneas 54-138) que captura todas las excepciones y las re-lanza como `RuntimeError` genéricos. Esto pierde el traceback original, dificultando el debugging cuando fallan las importaciones de LangChain o cuando faltan API keys.

## Goals / Non-Goals

**Goals:**
- Preservar información completa de debugging cuando falla la inicialización del provider
- Mantener la compatibilidad con código existente (la interfaz pública no cambia)
- Seguir las best practices de Python 3 para exception chaining

**Non-Goals:**
- Cambiar la lógica de selección de providers o configuración
- Modificar el comportamiento de las clases LangChainWrapper
- Agregar retry logic o fallback mechanisms

## Decisions

### Decision 1: Usar exception chaining con `raise ... from e`

**Enfoque elegido**: Cambiar `raise RuntimeError("...") % e` por `raise RuntimeError("...") from e`

**Rationale**:
- Python 3+ recomienda exception chaining para preservar contexto
- El traceback completo se mantiene automáticamente
- Compatible con herramientas de logging y debugging

**Alternativas consideradas**:
- **Opción A**: Capturar solo `ImportError` y dejar propagar las `RuntimeError` específicas
  - Pros: Más limpio, errores específicos se ven directamente
  - Contras: Requiere más cambios en la estructura del código
- **Opción B**: Mantener el código actual pero agregar `traceback.format_exc()` al mensaje
  - Pros: Mínimo cambio
  - Contras: No sigue Python idioms, más difícil para tools que parsean excepciones

**Decisión final**: Implementar `raise ... from e` primero (cambio mínimo). Si se identifica necesidad, refactorizar posteriormente para capturar solo ImportError.

### Decision 2: Mantener el mensaje de error actual

El mensaje "Could not initialize LLM provider: %s" es suficientemente claro. Con el exception chaining, el contexto adicional se preserva automáticamente.

## Risks / Trade-offs

**[Riesgo]** Tests que verifican el texto exacto del mensaje de error podrían fallar → **Mitigación**: Revisar y actualizar tests que usen `pytest.raises` con `match=` para verificar solo la parte clave del mensaje

**[Trade-off]** Exception chaining agrega contexto pero hace los tracebacks más largos → **Aceptable**: La información adicional vale la pena para debugging
