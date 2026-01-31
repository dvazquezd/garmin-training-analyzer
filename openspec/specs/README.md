# Specifications Guide

## ¿Qué son las Specs?

Las **Specifications** (specs) son documentos vivos que describen **comportamiento esperado** del sistema usando ejemplos concretos. No son documentación técnica tradicional.

### Formato: Given-When-Then

```gherkin
Given [contexto inicial]
When [acción]
Then [resultado esperado]
And [condiciones adicionales]
```

---

## Estructura de una Spec

```markdown
# Feature: [Título descriptivo]

## Context
Por qué existe / Valor que aporta

## User Story
Como [rol]
Quiero [acción]
Para [beneficio]

## Acceptance Criteria
### Scenario 1: [Caso feliz]
Given...
When...
Then...

### Scenario 2: [Caso de error]
...

## Technical Notes
[Detalles de implementación opcionales]

## Out of Scope
[Qué NO cubre]

## Testing Strategy
[Código pytest ejemplo]
```

---

## Catálogo de Specs

### 0. Configuration (`00-configuration/`)
- ✅ `config-management.spec.md` - Gestión de configuración, validación, multi-env

### 1. Authentication (`01-authentication/`)
- ✅ `garmin-auth.spec.md` - Login, retry, rate limits, 2FA

### 2. Data Extraction (`02-data-extraction/`)
- ✅ `activities.spec.md` - Extracción de actividades, cache, tipos
- ✅ `body-composition.spec.md` - Peso, grasa corporal, tendencias

### 3. Caching (`03-caching/`)
- ✅ `sqlite-cache.spec.md` - Cache local con TTL, limpieza, stats

### 4. LLM Analysis (`04-llm-analysis/`)
- ✅ `multi-provider.spec.md` - Claude, GPT-4, Gemini, fallback, rate limits
- ✅ `prompt-management.spec.md` - Prompts externos, templates, A/B testing

### 5. Reporting (`05-reporting/`)
- ✅ `html-reports.spec.md` - Reportes HTML con charts embebidos
- ✅ `visualizations.spec.md` - Gráficos matplotlib (peso, HR, volumen)
- ✅ `multi-format-reports.spec.md` - TXT, Markdown, JSON, CSV

### 6. CLI (`06-cli/`)
- ✅ `command-line-interface.spec.md` - Argumentos CLI, flags, validación

---

## Workflow SDD

```
┌─────────────┐
│   SPECIFY   │ Escribir spec con escenarios Given-When-Then
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    PLAN     │ Diseñar arquitectura técnica (opcional)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  IMPLEMENT  │ Escribir tests → Implementar → Refactorizar
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    TEST     │ Validar todos los escenarios pasan
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ITERATE   │ Actualizar spec si descubres casos nuevos
└─────────────┘
```

---

## Comandos Útiles

```bash
# Ver todas las specs
ls -R specs/

# Crear nueva spec desde template
cp specs/templates/spec-template.md specs/XX-nueva-feature/feature.spec.md

# Ejecutar tests de una spec específica
pytest tests/test_auth.py -v

# Ver cobertura de specs
pytest --cov=src --cov-report=html

# Validar que cada escenario tiene su test
python scripts/validate_spec_coverage.py
```

---

## Reglas de Oro

1. **Specs = Source of Truth**: Si no está en la spec, no existe
2. **Un escenario = Un test**: Cada `Given-When-Then` debe tener test pytest
3. **Specs vivas**: Actualiza si descubres casos edge
4. **Lenguaje simple**: Escribe para humanos, no solo devs
5. **Ejemplos concretos**: Usa datos reales (IDs, fechas, valores)

---

## Contribuir

Para añadir nueva spec:

1. Copia `templates/spec-template.md`
2. Completa todas las secciones
3. Escribe mínimo 3 escenarios (happy path + 2 errores)
4. Añade a este README en la sección "Catálogo de Specs"
5. Crea tests correspondientes en `tests/`
6. Verifica que todos los tests pasan
7. Crea PR con spec + tests

---

## Recursos

- [Specification by Example (Gojko Adzic)](https://gojko.net/books/specification-by-example/)
- [Behavior Driven Development](https://cucumber.io/docs/bdd/)
- [Given-When-Then Guide](https://martinfowler.com/bliki/GivenWhenThen.html)
