# Feature: Interfaz de Línea de Comandos (CLI)

## Context
**Por qué existe**: Los usuarios necesitan ejecutar el análisis con diferentes configuraciones sin editar archivos `.env`. Una CLI robusta permite automatización (cron jobs, CI/CD), scripting y uso flexible. Los argumentos CLI deben override configuraciones de `.env` para máxima flexibilidad.

**Valor que aporta**:
- Ejecución flexible sin editar configuración
- Automatización con scripts/cron
- Override rápido de parámetros
- Help integrado (documentación CLI)
- Validación de argumentos
- Dry-run mode para testing

---

## User Story
**Como** usuario que ejecuta análisis frecuentemente  
**Quiero** controlar todas las opciones desde la línea de comandos  
**Para** automatizar tareas y experimentar rápidamente sin editar archivos

---

## Acceptance Criteria

### Scenario 1: Mostrar help completo
**Given** el usuario ejecuta:
```bash
python training_analyzer.py --help
```
**When** el sistema procesa el comando  
**Then** muestra documentación completa:
```
usage: training_analyzer.py [-h] [--days DAYS] [--provider PROVIDER]
                            [--model MODEL] [--email EMAIL]
                            [--password PASSWORD] [--no-cache]
                            [--clear-cache] [--export-all-formats]
                            [--debug] [--version]

🏃 Garmin Training Analyzer - AI-powered training analysis

optional arguments:
  -h, --help            show this help message and exit

Analysis Options:
  --days DAYS           Days to analyze (default: 30)
  --provider PROVIDER   LLM provider: anthropic|openai|google
  --model MODEL         LLM model name
  --max-tokens TOKENS   Maximum tokens for analysis (default: 3000)
  --temperature TEMP    LLM temperature 0.0-1.0 (default: 0.7)

Garmin Authentication:
  --email EMAIL         Garmin email (overrides .env)
  --password PASSWORD   Garmin password (overrides .env)

Cache Options:
  --no-cache            Disable cache (force fresh API calls)
  --clear-cache         Clear all cached data before running
  --cache-ttl HOURS     Cache TTL in hours (default: 24)

Export Options:
  --export-all-formats  Export in TXT, MD, JSON, CSV
  --export-html-only    Export only HTML report
  --no-export           Skip file export (analysis only)

Debug & Info:
  --debug               Enable debug logging
  --verbose, -v         Verbose output
  --quiet, -q           Minimal output
  --version             Show version and exit
  --estimate-cost       Estimate API cost without executing

Examples:
  # Analyze last 60 days with Claude
  python training_analyzer.py --days 60 --provider anthropic

  # Use GPT-4 with custom credentials
  python training_analyzer.py --provider openai --email user@example.com

  # Clear cache and run fresh analysis
  python training_analyzer.py --clear-cache --days 30

For more info: https://github.com/dvazquezd/garmin-training-analyzer
```
**And** termina con código de salida `0`

---

### Scenario 2: Override de días de análisis
**Given** el `.env` tiene `ANALYSIS_DAYS=30`  
**When** ejecuta:
```bash
python training_analyzer.py --days 60
```
**Then** usa 60 días (no 30 del `.env`)  
**And** registra: `"⚙️  Usando 60 días de análisis (override CLI)"`  
**And** el análisis cubre los últimos 60 días

---

### Scenario 3: Override de proveedor LLM
**Given** el `.env` tiene `LLM_PROVIDER=anthropic`  
**When** ejecuta:
```bash
python training_analyzer.py --provider openai --model gpt-4o
```
**Then** usa OpenAI con GPT-4o (ignora Anthropic del `.env`)  
**And** registra: `"⚙️  Proveedor LLM: openai (modelo: gpt-4o) - override CLI"`

---

### Scenario 4: Credenciales Garmin desde CLI
**Given** el usuario NO quiere guardar credenciales en `.env`  
**When** ejecuta:
```bash
python training_analyzer.py --email user@garmin.com --password mypass
```
**Then** usa esas credenciales para autenticación  
**And** NO las guarda en disco  
**And** muestra warning:
```
⚠️  Usando credenciales desde CLI
   Nota: Evita usar passwords en CLI (quedan en historial de shell)
   Recomendación: Usa .env para mayor seguridad
```

---

### Scenario 5: Limpiar cache antes de ejecutar
**Given** existe cache con datos de hace 5 días  
**When** ejecuta:
```bash
python training_analyzer.py --clear-cache
```
**Then** elimina TODO el cache antes de iniciar análisis  
**And** registra:
```
🗑️  Limpiando cache...
   Entradas eliminadas: 23
   Espacio liberado: 1.2 MB
✅ Cache limpiado
```
**And** luego ejecuta análisis normal (con fetch desde API)

---

### Scenario 6: Desactivar cache temporalmente
**Given** el `.env` tiene `USE_CACHE=true`  
**When** ejecuta:
```bash
python training_analyzer.py --no-cache
```
**Then** desactiva cache solo para esta ejecución  
**And** hace todas las llamadas directas a API  
**And** NO guarda resultados en cache  
**And** registra: `"⚠️  Cache desactivado para esta ejecución"`

---

### Scenario 7: Modo debug verboso
**Given** el usuario quiere ver logs detallados  
**When** ejecuta:
```bash
python training_analyzer.py --debug
```
**Then** configura logging a nivel DEBUG  
**And** muestra logs detallados en consola:
```
[DEBUG] Loading config from .env
[DEBUG] Authenticating with Garmin (email: user@example.com)
[DEBUG] Cache hit: activities_30days_20250130
[DEBUG] LLM provider: anthropic, model: claude-sonnet-4
[DEBUG] Prompt tokens: 1,234
[DEBUG] Building HTML report...
```

---

### Scenario 8: Estimación de coste sin ejecutar
**Given** el usuario quiere saber el coste antes de ejecutar  
**When** ejecuta:
```bash
python training_analyzer.py --days 60 --estimate-cost
```
**Then** calcula estimación SIN llamar a LLM:
```
📊 Estimación de Coste

Configuración:
  - Días de análisis: 60
  - Proveedor: anthropic (claude-sonnet-4)
  - Actividades estimadas: ~25
  - Tokens input (est.): 5,200
  - Tokens output (max): 3,000

Coste estimado:
  - Input: $0.016 (5,200 tokens × $3/MTok)
  - Output: $0.045 (3,000 tokens × $15/MTok)
  - TOTAL: $0.061

¿Continuar con el análisis? (s/n):
```
**And** espera confirmación del usuario  
**And** si responde "n", termina sin ejecutar

---

### Scenario 9: Modo silencioso (minimal output)
**Given** el usuario usa el script en automation  
**When** ejecuta:
```bash
python training_analyzer.py --quiet
```
**Then** solo muestra mensajes críticos:
```
✅ Análisis completado
📄 Reporte: analysis_reports/reporte_20250130_143022.html
```
**And** NO muestra progress bars, warnings no críticos, ni debug  
**And** útil para logs limpios en CI/CD

---

### Scenario 10: Validación de argumentos inválidos
**Given** el usuario ejecuta con argumento inválido:
```bash
python training_analyzer.py --days abc
```
**When** el sistema valida argumentos  
**Then** muestra error específico:
```
❌ Error de validación: Argumento '--days'
   Valor inválido: 'abc'
   Esperado: Número entero positivo (1-365)
   
   Uso correcto:
     python training_analyzer.py --days 60
   
   Ver ayuda completa: python training_analyzer.py --help
```
**And** termina con código de salida `2`  
**And** NO ejecuta el análisis

---

### Scenario 11: Modo dry-run (simulación)
**Given** el usuario quiere probar sin ejecutar realmente  
**When** ejecuta:
```bash
python training_analyzer.py --dry-run --days 60
```
**Then** simula la ejecución sin hacer calls reales:
```
🔍 Modo Dry-Run - Simulación sin ejecución real

Pasos a ejecutar:
  [1/5] ✓ Autenticar con Garmin (user@example.com)
  [2/5] ✓ Extraer actividades (últimos 60 días)
  [3/5] ✓ Extraer composición corporal
  [4/5] ✓ Generar análisis con Claude Sonnet 4
  [5/5] ✓ Exportar reporte HTML

Configuración:
  - Días: 60
  - Cache: Habilitado (TTL: 24h)
  - LLM: anthropic/claude-sonnet-4
  - Coste estimado: $0.061

⚠️  Esta fue una simulación. Usa sin --dry-run para ejecutar realmente.
```

---

### Scenario 12: Combinación de múltiples flags
**Given** el usuario ejecuta con múltiples argumentos:
```bash
python training_analyzer.py \
  --days 90 \
  --provider anthropic \
  --model claude-opus-4-20251101 \
  --clear-cache \
  --export-all-formats \
  --debug
```
**When** el sistema procesa todos los argumentos  
**Then** aplica todos correctamente en orden de precedencia:
1. Limpia cache primero
2. Configura 90 días
3. Usa Claude Opus 4
4. Activa debug logging
5. Ejecuta análisis
6. Exporta en todos los formatos
**And** cada paso se registra en debug log  
**And** NO hay conflictos entre flags

---

## Technical Notes
- **Librería**: `argparse` (stdlib Python) para parsing de argumentos
- **Precedencia**: CLI args > environment vars > defaults
- **Validación**: Usar `type=` y `choices=` en argparse para validación
- **Help formatting**: `formatter_class=argparse.RawDescriptionHelpFormatter`
- **Grupos de argumentos**: Agrupar args relacionados (Analysis, Cache, etc.)
- **Salida de error**: Stderr para errores, stdout para resultados
- **Exit codes**:
  - `0`: Éxito
  - `1`: Error de ejecución
  - `2`: Error de argumentos
- **Seguridad**: NUNCA loguear passwords, incluso en debug mode

---

## Out of Scope
❌ GUI (Graphical User Interface)  
❌ TUI interactiva (textual/rich)  
❌ Configuración interactiva (wizard)  
❌ Shell completion (bash/zsh autocomplete)  
❌ Subcomandos (e.g., `train analyze`, `train export`)  
❌ Alias de argumentos customizables

---

## Testing Strategy
```python
# tests/test_cli.py

import pytest
import sys
from unittest.mock import patch
from training_analyzer import main, parse_args

def test_help_flag_shows_documentation(capsys):
    """Scenario 1: Help"""
    with pytest.raises(SystemExit) as exc_info:
        parse_args(['--help'])
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Garmin Training Analyzer" in captured.out
    assert "--days" in captured.out

def test_days_override_from_cli():
    """Scenario 2: Days override"""
    args = parse_args(['--days', '60'])
    assert args.days == 60

def test_provider_override_from_cli():
    """Scenario 3: Provider override"""
    args = parse_args(['--provider', 'openai', '--model', 'gpt-4o'])
    assert args.provider == 'openai'
    assert args.model == 'gpt-4o'

def test_credentials_from_cli(caplog):
    """Scenario 4: CLI credentials"""
    args = parse_args(['--email', 'user@garmin.com', '--password', 'pass'])
    assert args.email == 'user@garmin.com'
    # Should show warning about CLI passwords

def test_clear_cache_flag():
    """Scenario 5: Clear cache"""
    args = parse_args(['--clear-cache'])
    assert args.clear_cache is True

def test_no_cache_flag():
    """Scenario 6: Disable cache"""
    args = parse_args(['--no-cache'])
    assert args.use_cache is False

def test_debug_flag_sets_logging():
    """Scenario 7: Debug mode"""
    with patch('logging.basicConfig') as mock_logging:
        args = parse_args(['--debug'])
        main(args)
        
        mock_logging.assert_called()
        # Verify DEBUG level was set

def test_estimate_cost_mode():
    """Scenario 8: Cost estimation"""
    with patch('builtins.input', return_value='n'):
        args = parse_args(['--estimate-cost'])
        result = main(args)
        
        # Should not execute analysis
        assert result['executed'] is False

def test_quiet_mode_minimal_output(capsys):
    """Scenario 9: Quiet mode"""
    args = parse_args(['--quiet'])
    main(args)
    
    captured = capsys.readouterr()
    # Should have minimal output
    assert len(captured.out.split('\n')) < 5

def test_invalid_days_argument():
    """Scenario 10: Validation"""
    with pytest.raises(SystemExit) as exc_info:
        parse_args(['--days', 'abc'])
    
    assert exc_info.value.code == 2

def test_dry_run_mode(caplog):
    """Scenario 11: Dry-run"""
    args = parse_args(['--dry-run', '--days', '60'])
    result = main(args)
    
    assert "Modo Dry-Run" in caplog.text
    assert result['dry_run'] is True
    # No API calls should be made

def test_multiple_flags_combination():
    """Scenario 12: Multiple flags"""
    args = parse_args([
        '--days', '90',
        '--provider', 'anthropic',
        '--clear-cache',
        '--export-all-formats',
        '--debug'
    ])
    
    assert args.days == 90
    assert args.provider == 'anthropic'
    assert args.clear_cache is True
    assert args.export_all_formats is True
    assert args.debug is True

def test_cli_precedence_over_env():
    """CLI should override environment variables"""
    with patch.dict('os.environ', {'ANALYSIS_DAYS': '30'}):
        args = parse_args(['--days', '60'])
        assert args.days == 60  # CLI wins
```

---

## Implementation Checklist
- [ ] Crear parser de argumentos en `training_analyzer.py`
- [ ] Implementar validación de argumentos (tipos, rangos)
- [ ] Añadir grupos de argumentos relacionados
- [ ] Implementar override de configuración (.env < CLI)
- [ ] Añadir modo `--estimate-cost`
- [ ] Implementar modo `--dry-run`
- [ ] Añadir flags de verbosidad (`--debug`, `--quiet`)
- [ ] Implementar `--clear-cache` y `--no-cache`
- [ ] Añadir help completo con ejemplos
- [ ] Implementar exit codes apropiados
- [ ] Crear tests en `tests/test_cli.py` (12 tests)
- [ ] Documentar CLI en README con ejemplos
- [ ] Añadir sección de troubleshooting CLI

---

## Related Specs
- [Configuration](../00-configuration/config-management.spec.md) - CLI override config
- [Cache System](../03-caching/sqlite-cache.spec.md) - Flags --no-cache, --clear-cache
- [Multi-Format Reports](../05-reporting/multi-format-reports.spec.md) - Flags --export-*

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 11 (dry-run) para testing seguro
- **2025-01-30**: Añadido Scenario 12 (múltiples flags) para casos complejos
