## Why

El manejo actual de excepciones en `LLMFactory.get_provider()` captura todas las excepciones y las re-lanza como un `RuntimeError` genérico, perdiendo el traceback original y la información de debugging. Esto dificulta diagnosticar problemas de inicialización del LLM, especialmente cuando faltan dependencias o API keys.

## What Changes

- Mejorar el manejo de excepciones en `src/llm_provider.py` para preservar la cadena de excepciones
- Usar `raise ... from e` para mantener el contexto original
- Opcionalmente, ser más selectivo capturando solo `ImportError` para lazy imports mientras se dejan propagar las `RuntimeError` específicas

## Capabilities

### New Capabilities
<!-- No new capabilities - this is a bug fix/improvement -->

### Modified Capabilities
- `llm-provider-initialization`: El manejo de errores ahora preserva información completa de debugging cuando la inicialización falla

## Impact

- `src/llm_provider.py`: Modificar el bloque try/except en `LLMFactory.get_provider()` (líneas 54-138)
