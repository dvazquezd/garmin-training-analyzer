# Feature: Sistema de Gestión de Configuración

## Context
**Por qué existe**: La aplicación tiene múltiples parámetros configurables (credenciales, proveedores LLM, cache, análisis). Hardcodear configuración es inflexible. Un sistema robusto de configuración permite personalización, entornos múltiples (dev/prod), validación y defaults sensatos.

**Valor que aporta**:
- Configuración centralizada en `.env`
- Validación automática de parámetros
- Defaults razonables (funciona out-of-the-box)
- Soporte para múltiples entornos
- Documentación auto-generada de config
- Type-safe configuration con dataclasses

---

## User Story
**Como** desarrollador o usuario del sistema  
**Quiero** configurar todos los parámetros de forma clara y validada  
**Para** adaptar el sistema a mis necesidades sin tocar código

---

## Acceptance Criteria

### Scenario 1: Cargar configuración desde .env
**Given** existe archivo `.env` con configuración completa:
```env
# Garmin Credentials
GARMIN_EMAIL=user@example.com
GARMIN_PASSWORD=mypassword

# LLM Configuration
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=3000
TEMPERATURE=0.7

# Analysis Parameters
ANALYSIS_DAYS=30

# Cache Settings
USE_CACHE=true
CACHE_TTL_HOURS=24

# Logging
LOG_LEVEL=INFO
```
**When** el sistema inicializa `Config.load()`  
**Then** carga todos los valores en objeto Config:
```python
config = Config.load()
assert config.garmin_email == "user@example.com"
assert config.llm_provider == "anthropic"
assert config.analysis_days == 30
assert config.use_cache is True
```
**And** registra: `"⚙️  Configuración cargada desde .env"`

---

### Scenario 2: Valores por defecto si no existe .env
**Given** NO existe archivo `.env`  
**When** inicializa Config  
**Then** usa valores por defecto:
```python
{
    'analysis_days': 30,
    'max_tokens': 3000,
    'temperature': 0.7,
    'use_cache': True,
    'cache_ttl_hours': 24,
    'log_level': 'INFO'
}
```
**And** registra warning:
```
⚠️  Archivo .env no encontrado. Usando configuración por defecto.
   
   Para configurar:
   1. Copia .env.example a .env
   2. Completa tus credenciales
```

---

### Scenario 3: Validación de configuración obligatoria
**Given** el `.env` NO tiene `GARMIN_EMAIL`  
**When** valida la configuración  
**Then** lanza error descriptivo:
```
❌ Configuración incompleta

Parámetros obligatorios faltantes:
  - GARMIN_EMAIL: Email de Garmin Connect
  - GARMIN_PASSWORD: Password de Garmin Connect

Pasos para corregir:
  1. Abre .env en un editor
  2. Añade las líneas:
     GARMIN_EMAIL=tu_email@garmin.com
     GARMIN_PASSWORD=tu_password
  3. Guarda el archivo
```
**And** termina con exit code `1`

---

### Scenario 4: Validación de tipos de datos
**Given** el `.env` tiene `ANALYSIS_DAYS=abc` (no numérico)  
**When** valida la configuración  
**Then** detecta tipo inválido:
```
❌ Error de configuración: ANALYSIS_DAYS
   Valor actual: 'abc'
   Tipo esperado: Entero positivo (int)
   Rango válido: 1-365
   
   Ejemplo correcto:
     ANALYSIS_DAYS=30
```
**And** termina con exit code `2`

---

### Scenario 5: Validación de rangos
**Given** el `.env` tiene `TEMPERATURE=2.5` (fuera de rango)  
**When** valida la configuración  
**Then** rechaza el valor:
```
❌ Error de configuración: TEMPERATURE
   Valor actual: 2.5
   Rango válido: 0.0 - 1.0
   
   Descripción:
   La temperatura controla la aleatoriedad del LLM.
   - 0.0: Más determinístico
   - 1.0: Más creativo
   
   Valores recomendados:
   - Análisis factual: 0.3-0.5
   - Análisis creativo: 0.7-0.9
```

---

### Scenario 6: Override de configuración con CLI
**Given** el `.env` tiene `ANALYSIS_DAYS=30`  
**And** se ejecuta con `--days 60`  
**When** carga configuración con CLI args  
**Then** CLI tiene precedencia:
```python
config = Config.load(cli_args={'days': 60})
assert config.analysis_days == 60  # No 30 del .env
```
**And** registra: `"⚙️  ANALYSIS_DAYS: 60 (override CLI, default: 30)"`

---

### Scenario 7: Múltiples entornos (dev/prod)
**Given** existen múltiples archivos de configuración:
```
.env.development
.env.production
.env.test
```
**And** configuración `ENVIRONMENT=production`  
**When** carga configuración  
**Then** prioriza `.env.production`:
```python
config = Config.load(env='production')
```
**And** registra: `"⚙️  Entorno: production"`  
**And** fallback a `.env` si el archivo específico no existe

---

### Scenario 8: Validación de API Keys
**Given** el `.env` tiene `ANTHROPIC_API_KEY=invalid_key`  
**When** valida formato de API key  
**Then** detecta formato inválido:
```
❌ API Key inválida: ANTHROPIC_API_KEY
   Formato esperado: sk-ant-[alphanumeric]
   Formato actual: invalid_key
   
   Obtén tu API key en: https://console.anthropic.com
```
**And** NO hace llamadas API con key inválida

---

### Scenario 9: Documentación auto-generada
**Given** el usuario ejecuta:
```bash
python -m src.config --docs
```
**When** genera documentación  
**Then** imprime tabla completa:
```
⚙️  CONFIGURACIÓN DISPONIBLE

┌────────────────────┬──────────────┬─────────────┬──────────────────────┐
│ Parámetro          │ Tipo         │ Default     │ Descripción          │
├────────────────────┼──────────────┼─────────────┼──────────────────────┤
│ GARMIN_EMAIL       │ str          │ (requerido) │ Email de Garmin      │
│ GARMIN_PASSWORD    │ str          │ (requerido) │ Password de Garmin   │
│ ANALYSIS_DAYS      │ int          │ 30          │ Días a analizar      │
│ LLM_PROVIDER       │ str (enum)   │ anthropic   │ anthropic|openai|... │
│ MAX_TOKENS         │ int          │ 3000        │ Max tokens (500-8000)│
│ TEMPERATURE        │ float        │ 0.7         │ LLM temp (0.0-1.0)   │
│ USE_CACHE          │ bool         │ true        │ Habilitar cache      │
│ CACHE_TTL_HOURS    │ int          │ 24          │ Expiración cache (h) │
│ LOG_LEVEL          │ str (enum)   │ INFO        │ DEBUG|INFO|WARN|ERROR│
└────────────────────┴──────────────┴─────────────┴──────────────────────┘

Para más detalles: https://github.com/.../docs/configuration.md
```

---

### Scenario 10: Configuración tipo-segura con dataclasses
**Given** la configuración usa Python dataclasses  
**When** accede a propiedades  
**Then** tiene type hints y validación automática:
```python
@dataclass
class Config:
    garmin_email: str
    analysis_days: int = 30
    temperature: float = 0.7
    use_cache: bool = True
    llm_provider: Literal['anthropic', 'openai', 'google'] = 'anthropic'
    
    def __post_init__(self):
        # Validación automática
        if not (0 <= self.temperature <= 1):
            raise ValueError(f"Temperature must be 0-1, got {self.temperature}")
```
**And** IDEs tienen autocomplete y type checking

---

### Scenario 11: Export de configuración actual
**Given** el usuario ejecuta:
```bash
python training_analyzer.py --export-config
```
**When** exporta configuración  
**Then** crea archivo `config_20250130.json`:
```json
{
  "timestamp": "2025-01-30T14:30:22Z",
  "environment": "production",
  "config": {
    "garmin_email": "user@example.com",
    "garmin_password": "***HIDDEN***",
    "analysis_days": 60,
    "llm_provider": "anthropic",
    "anthropic_model": "claude-sonnet-4-20250514",
    "anthropic_api_key": "sk-ant-***HIDDEN***",
    "use_cache": true,
    "cache_ttl_hours": 24
  },
  "sources": {
    "analysis_days": "cli_override",
    "llm_provider": "env_file",
    "use_cache": "default"
  }
}
```
**And** oculta valores sensibles (passwords, API keys)  
**And** muestra origen de cada valor (CLI, .env, default)

---

### Scenario 12: Hot reload de configuración (desarrollo)
**Given** configuración `DEBUG=true`  
**And** el sistema está corriendo  
**When** el usuario modifica `.env` durante ejecución  
**Then** detecta cambio (con watchdog)  
**And** registra:
```
🔄 Cambio detectado en .env
   ANALYSIS_DAYS: 30 → 60
   Recargando configuración...
✅ Configuración actualizada
```
**And** usa nueva configuración en siguiente ejecución  
**And** en producción (`DEBUG=false`), NO hace hot reload

---

## Technical Notes
- **Librería**: `python-dotenv` para cargar `.env`
- **Validación**: `pydantic` o dataclasses con `__post_init__`
- **Type hints**: Python 3.11+ con `typing.Literal`, `typing.Annotated`
- **Precedencia**: CLI args > environment vars > `.env` file > defaults
- **Seguridad**: 
  - NUNCA loguear passwords/API keys completas
  - Usar `***HIDDEN***` en exports
  - Validar permisos de `.env` (600 recomendado)
- **Hot reload**: `watchdog` library para file watching
- **Documentación**: Auto-generada desde dataclass annotations

---

## Out of Scope
❌ UI web para editar configuración  
❌ Base de datos para almacenar config  
❌ Encriptación de `.env` (usar herramientas OS)  
❌ Configuración remota (API endpoint)  
❌ Versionado automático de config  
❌ Rollback de configuración

---

## Testing Strategy
```python
# tests/test_config.py

import pytest
import os
from pathlib import Path
from src.config import Config, ConfigError

def test_load_config_from_env_file(tmp_path):
    """Scenario 1: Load from .env"""
    env_file = tmp_path / ".env"
    env_file.write_text("""
GARMIN_EMAIL=user@example.com
GARMIN_PASSWORD=mypass
ANALYSIS_DAYS=60
""")
    
    config = Config.load(env_file=env_file)
    
    assert config.garmin_email == "user@example.com"
    assert config.analysis_days == 60

def test_default_values_when_no_env():
    """Scenario 2: Defaults"""
    config = Config()
    
    assert config.analysis_days == 30
    assert config.max_tokens == 3000
    assert config.use_cache is True

def test_missing_required_fields_raises_error():
    """Scenario 3: Required validation"""
    with pytest.raises(ConfigError, match="GARMIN_EMAIL"):
        Config(garmin_email=None)

def test_invalid_type_raises_error():
    """Scenario 4: Type validation"""
    with pytest.raises(ValueError, match="ANALYSIS_DAYS"):
        Config(analysis_days="abc")

def test_out_of_range_value_raises_error():
    """Scenario 5: Range validation"""
    with pytest.raises(ValueError, match="TEMPERATURE"):
        Config(temperature=2.5)

def test_cli_overrides_env():
    """Scenario 6: CLI precedence"""
    config = Config.load(
        env_vars={'ANALYSIS_DAYS': '30'},
        cli_args={'days': 60}
    )
    
    assert config.analysis_days == 60

def test_multiple_environments(tmp_path):
    """Scenario 7: Multi-env"""
    (tmp_path / ".env.production").write_text("ANALYSIS_DAYS=90")
    (tmp_path / ".env.development").write_text("ANALYSIS_DAYS=30")
    
    config = Config.load(env='production', env_dir=tmp_path)
    assert config.analysis_days == 90

def test_api_key_format_validation():
    """Scenario 8: API key validation"""
    with pytest.raises(ValueError, match="API Key inválida"):
        Config(anthropic_api_key="invalid_key")

def test_generate_documentation(capsys):
    """Scenario 9: Auto-docs"""
    Config.generate_docs()
    
    captured = capsys.readouterr()
    assert "CONFIGURACIÓN DISPONIBLE" in captured.out
    assert "GARMIN_EMAIL" in captured.out

def test_type_safe_dataclass():
    """Scenario 10: Type safety"""
    config = Config(
        garmin_email="user@example.com",
        garmin_password="pass",
        analysis_days=60
    )
    
    # Should have type hints
    assert hasattr(config, '__annotations__')
    assert config.__annotations__['analysis_days'] == int

def test_export_config_hides_secrets(tmp_path):
    """Scenario 11: Export with hidden secrets"""
    config = Config(
        garmin_email="user@example.com",
        garmin_password="secret123",
        anthropic_api_key="sk-ant-xxxxx"
    )
    
    export_path = tmp_path / "config.json"
    config.export(export_path)
    
    import json
    with open(export_path) as f:
        exported = json.load(f)
    
    assert exported['config']['garmin_password'] == "***HIDDEN***"
    assert "sk-ant" not in str(exported)

def test_hot_reload_on_file_change(tmp_path):
    """Scenario 12: Hot reload"""
    env_file = tmp_path / ".env"
    env_file.write_text("ANALYSIS_DAYS=30")
    
    config = Config.load(env_file=env_file, hot_reload=True)
    assert config.analysis_days == 30
    
    # Modify file
    env_file.write_text("ANALYSIS_DAYS=60")
    
    # Should detect change and reload
    config.reload()
    assert config.analysis_days == 60
```

---

## Implementation Checklist
- [ ] Crear módulo `src/config.py` con dataclass `Config`
- [ ] Implementar carga desde `.env` con `python-dotenv`
- [ ] Añadir validación de tipos y rangos en `__post_init__`
- [ ] Implementar precedencia (CLI > env > defaults)
- [ ] Añadir soporte multi-entorno (.env.dev, .env.prod)
- [ ] Implementar validación de API keys (formato)
- [ ] Añadir generación automática de documentación
- [ ] Implementar export de configuración (JSON)
- [ ] Añadir hot reload con watchdog (modo debug)
- [ ] Crear CLI command `--export-config`
- [ ] Crear tests en `tests/test_config.py` (12 tests)
- [ ] Documentar configuración en README
- [ ] Crear `.env.example` con todos los parámetros comentados

---

## Related Specs
- [CLI Interface](../06-cli/command-line-interface.spec.md) - CLI override config
- [Authentication](../01-authentication/garmin-auth.spec.md) - Usa credenciales de config
- [LLM Analysis](../04-llm-analysis/multi-provider.spec.md) - Usa config LLM

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 11 (export) para troubleshooting
- **2025-01-30**: Añadido Scenario 12 (hot reload) para desarrollo ágil
