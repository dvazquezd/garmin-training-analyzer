# Notes: implement-agent-specs

## Decisiones iniciales
- Priorizar cambios que mejoren testability y seguridad (Config, LLM abstraction, Garmin adapter).
- Mantener compatibilidad hacia atrás durante refactors; usar feature branches por módulo.
- Evitar añadir nuevas dependencias salvo justificación clara. Para validations consideraremos `pydantic` o `dataclasses + custom validators`.

## Comunicación
- Cada PR debe referenciar esta change (`openspec/changes/implement-agent-specs`) y el ticket correspondiente.
- Incluir en cada PR: descripción corta, checklist de tests, comandos para ejecutar localmente y un changelog resumido.

## Estimaciones
- Audit: 1-2 días (completado: draft)  
- Config refactor: 1-2 días  
- LLM provider refactor: 2-4 días  
- Garmin adapter: 2-4 días  
- Cache & visualizations: 1-3 días  
- CI & Docs: 1-2 días

## Siguientes acciones recomendadas (hoy)
1. Abrir la rama `refactor/config-dataclass` y añadir `tests/test_config_refactor.py` con escenarios básicos (defaults, load from .env, validation fails).  
2. Implementar clase `Config` dataclass en `src/config.py` con minimal API and `Config.load()` used by tests.  
3. Run tests and iterate until green.
