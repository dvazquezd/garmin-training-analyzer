# Audit Report: implement-agent-specs

Fecha: 2026-01-31
Auditor: GitHub Copilot (as agent)

## Resumen ejecutivo
Realicé una revisión rápida del código para identificar violaciones a `openspec/agents.md` y puntos de mejora prioritarios. Este informe contiene hallazgos iniciales (P0/P1/P2), evidencia y acciones recomendadas para la primera iteración.

---

## Hallazgos prioritarios (P0)

1) `src/config.py` — Configuración leída en import time, sin dataclass ni validación robusta.
   - Evidencia: variables de clase que usan `os.getenv()` y `load_dotenv()` en import.
   - Riesgo: Imposible reconstruir config en tests, falta de validación de tipos/rangos, no soporta overrides CLI fácil.
   - Acción recomendada: Implementar `Config` como dataclass Pydantic-like (o usar `pydantic`/`dataclasses` + validación), añadir `Config.load(env_file, cli_args)` y tests.

2) `src/llm_analizer.py` — Dependencia fuerte de proveedores (branching), uso de `print()` en utilidades y lógica de formateo acoplada.
   - Evidencia: `if provider == 'anthropic': return ChatAnthropic(...)` y `print()` en verify/utility.
   - Riesgo: Difícil de testear y de intercambiar providers; impresiones de consola en librería.
   - Acción recomendada: Introducir `LLMProvider` interface + factory, inyectar cliente en `LLMAnalyzer`, mover formateo a pequeñas funciones y usar logging.

3) Uso de `print()` en módulos utilitarios (`llm_analizer.verify_*`, `prompt_manager.verify_prompts_setup`, `config.py __main__`).
   - Evidencia: llamadas explícitas `print(...)` en tres módulos.
   - Riesgo: Código no usable en librería; tests impuros.
   - Acción recomendada: Reemplazar por logging y proporcionar CLI/console entrypoints para human-friendly output.

---

## Hallazgos importantes (P1)

4) `src/prompt_manager.py` — Validación básica pero placeholders y templates inconsistentes (`{...}` vs `{{...}}`). No parseo YAML frontmatter ni snippets.
   - Acción: Añadir soporte Jinja2, YAML frontmatter parsing, snippet expansion, sanitización y tests.

5) `src/garmin_client.py` — Tight coupling con `garminconnect.Garmin`; falta de interfaz/adapter, manejo de 2FA detectado en specs (need explicit detection), y algunas estructuras ad-hoc para body composition.
   - Acción: Crear `GarminAdapter` interface y inyectarla; añadir tests que simulen 2FA/rate-limit errors; centralizar parsing de composición.

6) `src/cache_manager.py` — Buen nivel, pero falta WAL mode, `busy_timeout` y manejo de corrupción explícito.
   - Acción: Activar PRAGMAs (WAL), busy_timeout, tests para recuperación y concurrency.

7) `src/html_reporter.py` y `src/visualizations.py` — Templating y conversiones funcionan, pero dependen de objetos con atributos (rather than dicts). Tests should assert responsive and accessible outputs.
   - Acción: Harden input contracts (accept both dicts and dataclasses), add tests for mobile/responsive rendering and accessibility checks.

---

## Observaciones (P2)

- Algunos scripts/demo usan `__main__` con prints; convertirlos en small CLI entrypoints (argparse) that call library functions.
- Add static analysis tools to CI (Black, Flake8, isort) if missing; this is quick win.
- Tests: run existing tests and capture failures to prioritize further.

---

## Prioridad inicial recomendada
1. P0 items (Config, LLM analyzer prints/DI) — bloqueantes para testability.  
2. P1 items (Prompts, Garmin adapter, Cache hardening) — important for correctness and resilience.  
3. P2 items (CLI tidy, CI infra) — low friction, merge early.

---

## Próximos pasos concretos (short-term)
- Crear la tarea `refactor/config-dataclass` (PR #1) y asignar tests (TDD).  
- Crear la tarea `refactor/llm-provider-abstraction` (PR #2) con tests que muevan la lógica de provider a una fábrica y permitan mocking.  
- Añadir `audit_report.md` a `openspec/changes/implement-agent-specs/` y priorizar elementos en `tasks.md`.

---

Si quieres, empiezo ahora mismo con la primera PR: `refactor/config-dataclass` (creo tests y la implementación mínima para pasar pruebas de validación). ¿Procedo?