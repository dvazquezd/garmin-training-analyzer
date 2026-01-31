# Feature: Exportación de Reportes en Múltiples Formatos

## Context
**Por qué existe**: Los usuarios tienen necesidades diferentes al consumir análisis: algunos prefieren texto plano (TXT) para lectura rápida, otros Markdown para documentación, y desarrolladores necesitan JSON para integración con otras herramientas. Soportar múltiples formatos aumenta la versatilidad del sistema.

**Valor que aporta**:
- TXT: Lectura rápida, compatible con cualquier editor
- Markdown: Formateo rico, versionable en Git, exportable a PDF
- JSON: Programáticamente accesible, integración con otros sistemas
- Flexibilidad para compartir en diferentes contextos

---

## User Story
**Como** usuario del sistema de análisis  
**Quiero** exportar mis reportes en diferentes formatos (TXT, MD, JSON)  
**Para** consumirlos según mi necesidad (lectura, documentación, integración)

---

## Acceptance Criteria

### Scenario 1: Generar reporte en formato TXT
**Given** el análisis ha completado exitosamente  
**And** tiene 15 actividades y análisis LLM de 1200 palabras  
**When** exporta con `generate_txt_report()`  
**Then** crea archivo `analysis_reports/analisis_20250130_143022.txt`:
```
================================================================================
              ANÁLISIS DE ENTRENAMIENTO - GARMIN TRAINING ANALYZER
================================================================================

Atleta: David García
Periodo: 2024-12-01 a 2025-01-30 (60 días)
Fecha de generación: 2025-01-30 14:30:22
Versión: 1.2.0

================================================================================
RESUMEN DE DATOS
================================================================================

Actividades:
  - Total: 15 actividades
  - Running: 10 (66.7%)
  - Cycling: 5 (33.3%)
  - Distancia total: 187.5 km
  - Tiempo total: 14h 32min
  - Calorías: 12,450 kcal

Composición Corporal:
  - Peso inicial: 76.8 kg
  - Peso final: 75.5 kg
  - Cambio: -1.3 kg (-1.69%)
  - % Grasa inicial: 19.2%
  - % Grasa final: 18.5%

================================================================================
ANÁLISIS DETALLADO
================================================================================

[Contenido del análisis LLM formateado]

================================================================================
ACTIVIDADES DETALLADAS
================================================================================

2025-01-30 | Morning Run      | 10.5 km | 54:05 | 145 bpm | 650 kcal
2025-01-28 | Evening Ride     | 25.0 km | 1:15:00 | 138 bpm | 780 kcal
...

================================================================================
Fin del reporte - Generado por Garmin Training Analyzer v1.2.0
================================================================================
```
**And** usa encoding UTF-8  
**And** líneas de máximo 80 caracteres (wrapping)  
**And** registra: `"📄 Reporte TXT generado (1,234 líneas, 45 KB)"`

---

### Scenario 2: Generar reporte en formato Markdown
**Given** el análisis ha completado  
**When** exporta con `generate_markdown_report()`  
**Then** crea archivo `analysis_reports/analisis_20250130_143022.md`:
```markdown
# 📊 Análisis de Entrenamiento

**Atleta:** David García  
**Periodo:** 2024-12-01 a 2025-01-30 (60 días)  
**Generado:** 2025-01-30 14:30:22

---

## 📈 Resumen de Datos

### Actividades
- **Total:** 15 actividades
- **Distribución:**
  - Running: 10 (66.7%)
  - Cycling: 5 (33.3%)
- **Métricas:**
  - Distancia total: 187.5 km
  - Tiempo total: 14h 32min
  - Calorías: 12,450 kcal

### Composición Corporal
| Métrica | Inicial | Final | Cambio |
|---------|---------|-------|--------|
| Peso | 76.8 kg | 75.5 kg | -1.3 kg (-1.69%) |
| % Grasa | 19.2% | 18.5% | -0.7% |

---

## 🎯 Análisis Detallado

[Contenido del análisis LLM - ya está en Markdown]

---

## 📋 Actividades Detalladas

| Fecha | Actividad | Distancia | Duración | FC Prom | Calorías |
|-------|-----------|-----------|----------|---------|----------|
| 2025-01-30 | Morning Run | 10.5 km | 54:05 | 145 bpm | 650 kcal |
| 2025-01-28 | Evening Ride | 25.0 km | 1:15:00 | 138 bpm | 780 kcal |

---

*Generado por Garmin Training Analyzer v1.2.0*
```
**And** usa formato Markdown estándar (CommonMark)  
**And** tablas para datos estructurados  
**And** emojis para secciones  
**And** registra: `"📄 Reporte Markdown generado (850 líneas, 38 KB)"`

---

### Scenario 3: Generar reporte en formato JSON
**Given** el análisis ha completado  
**When** exporta con `generate_json_report()`  
**Then** crea archivo `analysis_reports/datos_20250130_143022.json`:
```json
{
  "metadata": {
    "athlete_name": "David García",
    "period_start": "2024-12-01",
    "period_end": "2025-01-30",
    "analysis_days": 60,
    "generated_at": "2025-01-30T14:30:22Z",
    "version": "1.2.0",
    "llm_provider": "anthropic",
    "llm_model": "claude-sonnet-4-20250514"
  },
  "summary": {
    "activities": {
      "total": 15,
      "by_type": {
        "running": 10,
        "cycling": 5
      },
      "total_distance_km": 187.5,
      "total_duration_sec": 52320,
      "total_calories": 12450
    },
    "body_composition": {
      "initial_weight_kg": 76.8,
      "final_weight_kg": 75.5,
      "weight_change_kg": -1.3,
      "initial_body_fat_pct": 19.2,
      "final_body_fat_pct": 18.5
    }
  },
  "activities": [
    {
      "date": "2025-01-30",
      "name": "Morning Run",
      "type": "running",
      "distance_km": 10.5,
      "duration_sec": 3245,
      "average_hr": 145,
      "calories": 650
    }
  ],
  "body_composition_measurements": [...],
  "analysis": {
    "text": "[Análisis LLM completo]",
    "tokens_used": 2847,
    "generation_time_sec": 4.2
  }
}
```
**And** formato JSON válido (parseable)  
**And** pretty-printed con indentación de 2 espacios  
**And** encoding UTF-8  
**And** registra: `"📄 Reporte JSON generado (1,250 líneas, 52 KB)"`

---

### Scenario 4: Exportar solo actividades a CSV
**Given** el análisis tiene 15 actividades  
**When** exporta con `export_activities_csv()`  
**Then** crea archivo `analysis_reports/actividades_20250130_143022.csv`:
```csv
fecha,tipo,nombre,distancia_km,duracion_min,fc_promedio,fc_max,calorias
2025-01-30,running,Morning Run,10.5,54.08,145,178,650
2025-01-28,cycling,Evening Ride,25.0,75.00,138,165,780
...
```
**And** usa comas como delimitador  
**And** encoding UTF-8 con BOM (para Excel)  
**And** headers en español  
**And** números con punto decimal (formato internacional)  
**And** registra: `"📄 CSV de actividades exportado (15 filas)"`

---

### Scenario 5: Exportar todos los formatos a la vez
**Given** el análisis ha completado  
**When** ejecuta con flag `--export-all-formats`  
**Then** genera 4 archivos simultáneamente:
```
analysis_reports/
├── analisis_20250130_143022.txt
├── analisis_20250130_143022.md
├── datos_20250130_143022.json
└── actividades_20250130_143022.csv
```
**And** usa ThreadPoolExecutor para generación paralela (4 threads)  
**And** registra progreso:
```
📦 Exportando en múltiples formatos...
  [1/4] ✅ TXT generado (45 KB)
  [2/4] ✅ Markdown generado (38 KB)
  [3/4] ✅ JSON generado (52 KB)
  [4/4] ✅ CSV generado (3 KB)
Tiempo total: 0.8s
```

---

### Scenario 6: Validación de JSON con schema
**Given** se generó reporte JSON  
**When** valida con JSON Schema  
**Then** verifica estructura contra schema definido:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["metadata", "summary", "activities", "analysis"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["athlete_name", "period_start", "period_end"]
    },
    "activities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["date", "type", "distance_km"]
      }
    }
  }
}
```
**And** si la validación falla, registra error específico  
**And** retorna `is_valid: false` con detalles del error

---

### Scenario 7: Compresión automática de reportes grandes
**Given** el reporte JSON tiene tamaño > 10 MB  
**When** guarda el archivo  
**Then** crea también versión comprimida:
```
analysis_reports/
├── datos_20250130_143022.json        (12.5 MB)
└── datos_20250130_143022.json.gz     (1.8 MB - 85% reducción)
```
**And** registra: `"💾 Reporte comprimido (12.5 MB → 1.8 MB, 85% reducción)"`  
**And** el archivo `.json` sin comprimir también existe (para acceso directo)

---

### Scenario 8: Reporte con metadatos extendidos
**Given** configuración: `INCLUDE_EXTENDED_METADATA=true`  
**When** genera JSON  
**Then** incluye metadata adicional:
```json
{
  "metadata": {
    ...
    "system": {
      "os": "Darwin 23.2.0",
      "python_version": "3.11.7",
      "garminconnect_version": "0.2.30",
      "anthropic_version": "0.40.0"
    },
    "execution": {
      "cache_hit_rate": 0.87,
      "api_calls_made": 3,
      "total_time_sec": 12.5,
      "memory_peak_mb": 245
    },
    "git": {
      "commit": "a3f2e1b",
      "branch": "main",
      "is_dirty": false
    }
  }
}
```

---

### Scenario 9: Sanitización de datos personales
**Given** configuración: `ANONYMIZE_EXPORT=true`  
**When** exporta en cualquier formato  
**Then** reemplaza datos personales:
- Nombre: `"David García"` → `"Athlete #12345"`
- Email: `"user@example.com"` → `"athlete_12345@anonymized.com"`
- Ubicaciones GPS: truncadas a 2 decimales (±1 km precisión)
**And** registra: `"🔒 Datos personales anonimizados en exportación"`  
**And** incluye disclaimer: `"[DATOS ANONIMIZADOS]"` en header

---

### Scenario 10: Diff entre dos reportes JSON
**Given** existen 2 reportes JSON de diferentes periodos  
**When** ejecuta `compare_reports(report1.json, report2.json)`  
**Then** genera diff estructurado:
```json
{
  "comparison": {
    "period1": "2024-11-01 a 2024-12-31",
    "period2": "2024-12-01 a 2025-01-30",
    "changes": {
      "total_activities": {
        "before": 12,
        "after": 15,
        "change": +3,
        "change_pct": +25.0
      },
      "weight_kg": {
        "before": 77.5,
        "after": 75.5,
        "change": -2.0
      }
    }
  }
}
```
**And** guarda como `comparison_20250130.json`

---

### Scenario 11: Template customizable para reportes
**Given** existe archivo `templates/report_template.txt`:
```
==== REPORTE PERSONALIZADO ====
Atleta: {{athlete_name}}
Periodo: {{period}}

{{#activities}}
- {{date}}: {{name}} ({{distance}} km)
{{/activities}}
```
**When** genera reporte con template  
**Then** usa Mustache/Jinja2 para interpolar variables  
**And** permite personalización completa del formato

---

### Scenario 12: Notificación post-exportación
**Given** configuración: `NOTIFY_ON_EXPORT=true`  
**And** email configurado: `NOTIFICATION_EMAIL=user@example.com`  
**When** completa la exportación de reportes  
**Then** envía email con resumen:
```
Subject: ✅ Análisis de Entrenamiento Completado

Tu análisis de 60 días ha sido generado:
- Actividades: 15
- Peso: -1.3 kg
- Reportes generados: 4 archivos

Archivos adjuntos:
- analisis_20250130.txt
- analisis_20250130.md
```
**And** adjunta reportes TXT y MD (< 5 MB combinados)  
**And** JSON/CSV disponible via link (si muy grandes)

---

## Technical Notes
- **Formato TXT**: Plain text, UTF-8, LF line endings, max 80 chars/line
- **Formato MD**: CommonMark compatible, GitHub Flavored Markdown
- **Formato JSON**: RFC 8259 compliant, UTF-8, pretty-print indent=2
- **Formato CSV**: RFC 4180, UTF-8 with BOM, comma delimiter
- **Compresión**: gzip level 9 para archivos > 10 MB
- **Templates**: Jinja2 o Mustache para customización
- **JSON Schema**: Draft 07 para validación
- **Multithreading**: `concurrent.futures.ThreadPoolExecutor` (max 4 workers)
- **Email**: SMTP con TLS, librerías: `smtplib`, `email.mime`

---

## Out of Scope
❌ Exportación a Excel (.xlsx) con fórmulas  
❌ Reportes en formato Word (.docx)  
❌ XML export  
❌ Integración directa con Google Drive/Dropbox  
❌ Generación de QR codes para compartir  
❌ Reportes en tiempo real (streaming)

---

## Testing Strategy
```python
# tests/test_multi_format_reports.py

import pytest
import json
from pathlib import Path
from src.report_generator import ReportGenerator

def test_generate_txt_report(tmp_path):
    """Scenario 1: TXT generation"""
    data = mock_analysis_data()
    generator = ReportGenerator(output_dir=tmp_path)
    
    txt_path = generator.generate_txt_report(data)
    
    assert txt_path.exists()
    content = txt_path.read_text(encoding='utf-8')
    assert "ANÁLISIS DE ENTRENAMIENTO" in content
    assert len(content.splitlines()) > 100

def test_generate_markdown_report(tmp_path):
    """Scenario 2: Markdown generation"""
    data = mock_analysis_data()
    generator = ReportGenerator(output_dir=tmp_path)
    
    md_path = generator.generate_markdown_report(data)
    
    assert md_path.exists()
    content = md_path.read_text(encoding='utf-8')
    assert content.startswith('# ')  # Header
    assert '|' in content  # Table
    assert '**' in content  # Bold

def test_generate_json_report(tmp_path):
    """Scenario 3: JSON generation"""
    data = mock_analysis_data()
    generator = ReportGenerator(output_dir=tmp_path)
    
    json_path = generator.generate_json_report(data)
    
    assert json_path.exists()
    with open(json_path) as f:
        parsed = json.load(f)
    
    assert 'metadata' in parsed
    assert 'activities' in parsed
    assert isinstance(parsed['activities'], list)

def test_export_activities_csv(tmp_path):
    """Scenario 4: CSV export"""
    activities = mock_activities(15)
    generator = ReportGenerator(output_dir=tmp_path)
    
    csv_path = generator.export_activities_csv(activities)
    
    assert csv_path.exists()
    content = csv_path.read_text(encoding='utf-8-sig')  # BOM
    assert 'fecha,tipo,nombre' in content
    assert len(content.splitlines()) == 16  # Header + 15 rows

def test_export_all_formats_parallel(tmp_path):
    """Scenario 5: Parallel export"""
    data = mock_analysis_data()
    generator = ReportGenerator(output_dir=tmp_path)
    
    paths = generator.export_all_formats(data)
    
    assert len(paths) == 4
    assert all(p.exists() for p in paths.values())
    assert paths['txt'].suffix == '.txt'
    assert paths['json'].suffix == '.json'

def test_json_schema_validation():
    """Scenario 6: Schema validation"""
    data = mock_analysis_data()
    generator = ReportGenerator()
    
    is_valid, errors = generator.validate_json_schema(data)
    
    assert is_valid is True
    assert len(errors) == 0

def test_automatic_compression_large_files(tmp_path):
    """Scenario 7: Compression"""
    # Generate large report (> 10 MB)
    large_data = mock_large_analysis_data()
    generator = ReportGenerator(output_dir=tmp_path)
    
    json_path = generator.generate_json_report(large_data)
    gz_path = tmp_path / f"{json_path.stem}.json.gz"
    
    assert json_path.exists()
    assert gz_path.exists()
    assert gz_path.stat().st_size < json_path.stat().st_size * 0.5

def test_extended_metadata_inclusion(tmp_path):
    """Scenario 8: Extended metadata"""
    data = mock_analysis_data()
    generator = ReportGenerator(
        output_dir=tmp_path,
        include_extended_metadata=True
    )
    
    json_path = generator.generate_json_report(data)
    with open(json_path) as f:
        parsed = json.load(f)
    
    assert 'system' in parsed['metadata']
    assert 'execution' in parsed['metadata']

def test_data_anonymization(tmp_path):
    """Scenario 9: Anonymization"""
    data = mock_analysis_data()
    data['athlete_name'] = "John Doe"
    
    generator = ReportGenerator(output_dir=tmp_path, anonymize=True)
    json_path = generator.generate_json_report(data)
    
    with open(json_path) as f:
        parsed = json.load(f)
    
    assert "John Doe" not in str(parsed)
    assert "Athlete #" in parsed['metadata']['athlete_name']

def test_compare_two_reports():
    """Scenario 10: Report diff"""
    report1 = mock_analysis_data(period='2024-11')
    report2 = mock_analysis_data(period='2024-12')
    
    generator = ReportGenerator()
    diff = generator.compare_reports(report1, report2)
    
    assert 'changes' in diff
    assert 'total_activities' in diff['changes']

def test_custom_template_rendering(tmp_path):
    """Scenario 11: Custom template"""
    template_path = tmp_path / "custom_template.txt"
    template_path.write_text("Athlete: {{athlete_name}}")
    
    data = mock_analysis_data()
    generator = ReportGenerator(template_path=template_path)
    
    txt_path = generator.generate_txt_report(data)
    content = txt_path.read_text()
    
    assert "Athlete: " in content

def test_email_notification_on_export():
    """Scenario 12: Email notification"""
    data = mock_analysis_data()
    
    with patch('smtplib.SMTP') as mock_smtp:
        generator = ReportGenerator(notify_on_export=True)
        generator.export_all_formats(data)
        
        mock_smtp.assert_called_once()
```

---

## Implementation Checklist
- [ ] Crear módulo `src/report_generator.py` con clase `ReportGenerator`
- [ ] Implementar generadores para TXT, MD, JSON, CSV
- [ ] Añadir validación de JSON Schema
- [ ] Implementar compresión gzip para archivos grandes
- [ ] Añadir exportación paralela con ThreadPoolExecutor
- [ ] Implementar sistema de templates (Jinja2)
- [ ] Añadir anonimización de datos personales
- [ ] Implementar comparación de reportes (diff)
- [ ] Añadir notificaciones por email (opcional)
- [ ] Crear tests en `tests/test_multi_format_reports.py` (12 tests)
- [ ] Documentar formatos en README
- [ ] Añadir ejemplos de cada formato en `docs/examples/`

---

## Related Specs
- [HTML Reports](./html-reports.spec.md) - Otro formato de reporte
- [Visualizations](./visualizations.spec.md) - Puede incluir referencias a gráficos
- [LLM Analysis](../04-llm-analysis/multi-provider.spec.md) - Fuente del análisis

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 9 (anonimización) para privacidad
- **2025-01-30**: Añadido Scenario 12 (notificaciones) para automatización
