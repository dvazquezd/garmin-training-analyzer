# Feature: Visualizaciones de Datos de Entrenamiento con Matplotlib

## Context
**Por qué existe**: Los datos numéricos son difíciles de interpretar. Los gráficos permiten identificar tendencias, patrones y anomalías de forma visual. Los usuarios y entrenadores necesitan ver evolución de métricas (peso, volumen, FC) para tomar decisiones informadas.

**Valor que aporta**:
- Visualización rápida de tendencias (peso, volumen, FC)
- Identificación de patrones (progresión, estancamiento, overtraining)
- Comparación visual entre periodos
- Gráficos listos para compartir (PNG de alta calidad)
- Embebido en reportes HTML

---

## User Story
**Como** atleta que analiza su progreso  
**Quiero** visualizar mis datos de entrenamiento en gráficos claros y profesionales  
**Para** identificar tendencias y tomar decisiones basadas en datos visuales

---

## Acceptance Criteria

### Scenario 1: Gráfico de composición corporal (peso y % grasa)
**Given** hay 20 mediciones de composición corporal en 60 días  
**When** genera el gráfico `body_composition_chart(measurements)`  
**Then** crea gráfico con 2 ejes Y:
- Eje Y izquierdo: Peso (kg) - línea azul
- Eje Y derecho: % Grasa corporal - línea naranja
- Eje X: Fechas
**And** incluye elementos visuales:
```python
- Título: "Evolución de Composición Corporal (60 días)"
- Grid horizontal sutil (alpha=0.3)
- Markers en puntos de datos
- Leyenda (superior derecha)
- Labels de ejes ("Fecha", "Peso (kg)", "Grasa Corporal (%)")
```
**And** guarda como PNG: `analysis_reports/body_composition_20250130_143022.png`  
**And** resolución: 1200x600 px (DPI=100)  
**And** retorna path del archivo generado  
**And** registra: `"📊 Gráfico de composición corporal generado (1200x600px, 180 KB)"`

---

### Scenario 2: Gráfico de distribución de actividades (pie chart)
**Given** hay 45 actividades: 30 running, 10 cycling, 5 swimming  
**When** genera `activity_distribution_chart(activities)`  
**Then** crea gráfico de pastel (pie chart):
```python
- Running: 66.7% (color azul)
- Cycling: 22.2% (color verde)
- Swimming: 11.1% (color naranja)
```
**And** elementos visuales:
- Título: "Distribución de Actividades por Tipo"
- Porcentajes mostrados en cada sección
- Colores distintivos por deporte
- Explode en sección más grande (Running: 0.05)
- Shadow para profundidad
**And** guarda como `activity_distribution_20250130_143022.png`  
**And** registra: `"📊 Gráfico de distribución generado (800x800px)"`

---

### Scenario 3: Gráfico de volumen semanal (bar chart)
**Given** hay actividades en 8 semanas  
**When** genera `weekly_volume_chart(activities)`  
**Then** crea gráfico de barras con 2 métricas:
- Barras azules: Distancia total (km) por semana
- Línea roja: Número de actividades por semana
**And** eje X: Semanas ("Sem 1", "Sem 2", ...)  
**And** eje Y izquierdo: Distancia (km)  
**And** eje Y derecho: Actividades (#)  
**And** include línea de tendencia (regresión lineal) en distancia  
**And** guarda como `weekly_volume_20250130_143022.png`  
**And** registra: `"📊 Gráfico de volumen semanal generado"`

---

### Scenario 4: Gráfico de zonas de frecuencia cardíaca (histogram)
**Given** hay datos de FC de 30 actividades  
**When** genera `heart_rate_zones_chart(activities)`  
**Then** crea histograma de distribución de FC:
```python
Zonas (colores):
- Z1 (< 122 bpm): Gris - Recuperación
- Z2 (122-140): Azul - Base aeróbica
- Z3 (141-158): Verde - Tempo
- Z4 (159-176): Naranja - Umbral
- Z5 (> 176): Rojo - VO2max
```
**And** eje X: Zonas de FC  
**And** eje Y: Tiempo en zona (minutos)  
**And** barras coloreadas según zona  
**And** anotaciones con porcentaje del tiempo total  
**And** guarda como `heart_rate_zones_20250130_143022.png`

---

### Scenario 5: Gráfico sin datos - mensaje informativo
**Given** NO hay mediciones de composición corporal  
**When** intenta generar `body_composition_chart([])`  
**Then** crea gráfico con mensaje:
```
┌──────────────────────────────────┐
│                                  │
│   ⚠️  No hay datos disponibles   │
│                                  │
│   Para mostrar este gráfico:     │
│   - Conecta una báscula Garmin   │
│   - Sincroniza mediciones        │
│   - Aumenta ANALYSIS_DAYS        │
│                                  │
└──────────────────────────────────┘
```
**And** fondo gris claro  
**And** texto centrado  
**And** guarda PNG igual (para consistencia en reportes)  
**And** registra: `"⚠️  Gráfico vacío generado (sin datos de composición corporal)"`

---

### Scenario 6: Personalización de colores (tema)
**Given** configuración de tema:
```python
CHART_THEME = {
    'primary': '#00A1E0',    # Garmin blue
    'secondary': '#FF6B35',  # Orange
    'background': '#FFFFFF',
    'grid': '#E0E0E0',
    'font_color': '#212529'
}
```
**When** genera cualquier gráfico  
**Then** aplica colores del tema:
- Líneas principales: primary
- Líneas secundarias: secondary
- Fondo: background
- Grid: grid (alpha=0.3)
- Texto: font_color
**And** permite override por gráfico específico

---

### Scenario 7: Exportar gráficos en múltiples formatos
**Given** se generó gráfico de composición corporal  
**When** el usuario especifica `formats=['png', 'svg', 'pdf']`  
**Then** guarda en 3 formatos:
- `body_composition_20250130.png` (para web/reportes)
- `body_composition_20250130.svg` (vectorial, editable)
- `body_composition_20250130.pdf` (impresión)
**And** registra: `"📊 Gráfico exportado en 3 formatos (PNG, SVG, PDF)"`  
**And** retorna dict con paths de todos los archivos

---

### Scenario 8: Gráfico de comparación mes a mes
**Given** hay actividades de 3 meses (Sep, Oct, Nov)  
**When** genera `monthly_comparison_chart(activities)`  
**Then** crea gráfico de barras agrupadas:
```python
Métricas por mes:
- Distancia total (km)
- Actividades (#)
- Calorías (kcal)
```
**And** eje X: Meses ("Sep", "Oct", "Nov")  
**And** 3 barras por mes (colores: azul, verde, naranja)  
**And** leyenda explicando cada métrica  
**And** guarda como `monthly_comparison_20250130.png`

---

### Scenario 9: Gráfico de progresión de pace (running)
**Given** hay 15 actividades de running  
**When** genera `pace_progression_chart(running_activities)`  
**Then** crea scatter plot + línea de tendencia:
- Eje X: Fecha
- Eje Y: Pace (min/km)
- Puntos: Cada actividad (color por distancia)
- Línea: Regresión lineal (tendencia)
**And** invierte eje Y (menor pace = mejor arriba)  
**And** anotaciones en mejores/peores paces  
**And** guarda como `pace_progression_20250130.png`

---

### Scenario 10: Gráfico con límite de datos (truncamiento)
**Given** hay 500 mediciones de composición corporal (período muy largo)  
**When** genera gráfico  
**Then** detecta exceso de datos (> 100 puntos)  
**And** aplica downsampling inteligente:
- Agrupa por semana (promedio semanal)
- Reduce a ~60-80 puntos
**And** registra: `"📊 500 mediciones agrupadas semanalmente (66 puntos finales)"`  
**And** el gráfico es legible (no sobrecargado)

---

### Scenario 11: Anotaciones automáticas (PRs y milestones)
**Given** el gráfico de pace muestra PR (personal record)  
**When** detecta el mejor pace del periodo  
**Then** añade anotación:
```python
- Arrow apuntando al punto PR
- Texto: "PR: 4:32 min/km"
- Color destacado (rojo)
- Offset para legibilidad
```
**And** lo mismo para otros milestones:
- Mayor distancia: "Más larga: 21.1 km"
- Mayor volumen semanal: "Pico: 65 km"

---

### Scenario 12: Gráficos responsive (ajuste automático de tamaño)
**Given** el gráfico se generará para reporte HTML (web)  
**When** especifica `output_target='web'`  
**Then** ajusta dimensiones:
- Web: 1200x600px (aspect ratio 2:1)
- Mobile: 800x600px (aspect ratio 4:3)
- Print: 2400x1200px (alta resolución, DPI=300)
**And** ajusta font sizes según resolución:
- Web: 10pt
- Mobile: 12pt (más grande para pantallas pequeñas)
- Print: 8pt (más denso para papel)

---

## Technical Notes
- **Librería**: `matplotlib==3.9.0` + `seaborn==0.13.0` (opcional para estilos)
- **Backend**: `Agg` (non-interactive, para server-side)
- **Formato de salida**: PNG por default (RGB, 24-bit)
- **Resolución**:
  - Web: 100 DPI, 1200x600px
  - Print: 300 DPI, 2400x1200px
- **Colores**: Usar paleta Garmin (azul #00A1E0, naranja #FF6B35)
- **Fonts**: Sans-serif (DejaVu Sans, Arial fallback)
- **Tamaño de archivo**: Optimizar PNG con `optimize=True` (PIL)
- **Memory management**: `plt.close()` después de guardar para liberar RAM
- **Multithreading**: Generar gráficos en paralelo con `ThreadPoolExecutor`

---

## Out of Scope
❌ Gráficos interactivos (Plotly/Bokeh) - solo estáticos  
❌ Animaciones (GIFs, videos)  
❌ Mapas de rutas GPS (leaflet/folium) - fuera de alcance  
❌ 3D plots  
❌ Dashboards en vivo (Streamlit/Dash)  
❌ Exportación a Excel con gráficos embebidos

---

## Testing Strategy
```python
# tests/test_visualizations.py

import pytest
from pathlib import Path
import matplotlib.pyplot as plt
from src.visualizations import TrainingVisualizer

def test_body_composition_chart_generation(tmp_path):
    """Scenario 1: Body composition chart"""
    measurements = [
        {'date': '2025-01-15', 'weight': 75.5, 'bodyFat': 18.5},
        {'date': '2025-01-20', 'weight': 75.2, 'bodyFat': 18.3}
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_body_composition_chart(measurements)
    
    assert chart_path.exists()
    assert chart_path.suffix == '.png'
    assert chart_path.stat().st_size > 10_000  # > 10 KB

def test_activity_distribution_pie_chart(tmp_path):
    """Scenario 2: Pie chart"""
    activities = [
        {'activityType': {'typeKey': 'running'}},
        {'activityType': {'typeKey': 'running'}},
        {'activityType': {'typeKey': 'cycling'}}
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_activity_distribution_chart(activities)
    
    assert chart_path.exists()
    # Verify it's a valid image
    from PIL import Image
    img = Image.open(chart_path)
    assert img.size == (800, 800)

def test_weekly_volume_bar_chart(tmp_path):
    """Scenario 3: Weekly volume"""
    activities = [
        {'date': '2025-01-01', 'distance': 10000},
        {'date': '2025-01-08', 'distance': 12000}
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_weekly_volume_chart(activities)
    
    assert chart_path.exists()

def test_heart_rate_zones_histogram(tmp_path):
    """Scenario 4: HR zones"""
    activities = [
        {'averageHR': 145, 'duration': 3600},  # Z2
        {'averageHR': 165, 'duration': 1800}   # Z4
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_hr_zones_chart(activities)
    
    assert chart_path.exists()

def test_empty_data_shows_message(tmp_path):
    """Scenario 5: No data"""
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_body_composition_chart([])
    
    assert chart_path.exists()
    # Image should exist but contain "No hay datos" text

def test_custom_theme_colors(tmp_path):
    """Scenario 6: Theme customization"""
    theme = {
        'primary': '#FF0000',  # Red
        'secondary': '#00FF00'  # Green
    }
    
    viz = TrainingVisualizer(output_dir=tmp_path, theme=theme)
    chart_path = viz.create_body_composition_chart([{'date': '2025-01-01', 'weight': 75}])
    
    # Verify custom colors are used (would need pixel analysis)
    assert chart_path.exists()

def test_export_multiple_formats(tmp_path):
    """Scenario 7: Multiple formats"""
    measurements = [{'date': '2025-01-01', 'weight': 75}]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    paths = viz.create_body_composition_chart(
        measurements,
        formats=['png', 'svg', 'pdf']
    )
    
    assert len(paths) == 3
    assert paths['png'].exists()
    assert paths['svg'].exists()
    assert paths['pdf'].exists()

def test_monthly_comparison_chart(tmp_path):
    """Scenario 8: Monthly comparison"""
    activities = [
        {'date': '2024-09-15', 'distance': 10000, 'calories': 600},
        {'date': '2024-10-15', 'distance': 12000, 'calories': 700},
        {'date': '2024-11-15', 'distance': 11000, 'calories': 650}
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_monthly_comparison_chart(activities)
    
    assert chart_path.exists()

def test_pace_progression_chart(tmp_path):
    """Scenario 9: Pace progression"""
    running_activities = [
        {'date': '2025-01-01', 'averageSpeed': 3.33},  # 5:00 min/km
        {'date': '2025-01-15', 'averageSpeed': 3.47}   # 4:48 min/km
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_pace_progression_chart(running_activities)
    
    assert chart_path.exists()

def test_downsampling_large_dataset(tmp_path):
    """Scenario 10: Truncation"""
    # Generate 500 measurements
    measurements = [
        {'date': f'2024-{i%12+1:02d}-01', 'weight': 75 + (i % 10) * 0.1}
        for i in range(500)
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_body_composition_chart(measurements)
    
    # Should downsample internally
    assert chart_path.exists()

def test_automatic_annotations_pr(tmp_path):
    """Scenario 11: Annotations"""
    activities = [
        {'date': '2025-01-01', 'averageSpeed': 3.0},
        {'date': '2025-01-15', 'averageSpeed': 3.5},  # PR
        {'date': '2025-01-30', 'averageSpeed': 3.2}
    ]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    chart_path = viz.create_pace_progression_chart(
        activities,
        annotate_pr=True
    )
    
    assert chart_path.exists()
    # Would need OCR to verify "PR" text is in image

def test_responsive_sizing(tmp_path):
    """Scenario 12: Responsive charts"""
    measurements = [{'date': '2025-01-01', 'weight': 75}]
    
    viz = TrainingVisualizer(output_dir=tmp_path)
    
    web_path = viz.create_body_composition_chart(
        measurements,
        output_target='web'
    )
    mobile_path = viz.create_body_composition_chart(
        measurements,
        output_target='mobile'
    )
    
    from PIL import Image
    web_img = Image.open(web_path)
    mobile_img = Image.open(mobile_path)
    
    assert web_img.size == (1200, 600)
    assert mobile_img.size == (800, 600)
```

---

## Implementation Checklist
- [ ] Crear módulo `src/visualizations.py` con clase `TrainingVisualizer`
- [ ] Implementar 5 tipos de gráficos principales
- [ ] Añadir manejo de datos vacíos (mensajes informativos)
- [ ] Implementar sistema de temas (colores personalizables)
- [ ] Añadir exportación multi-formato (PNG, SVG, PDF)
- [ ] Implementar downsampling para datasets grandes
- [ ] Añadir anotaciones automáticas (PRs, milestones)
- [ ] Implementar sizing responsive (web, mobile, print)
- [ ] Optimizar tamaño de archivos PNG
- [ ] Añadir memory management (`plt.close()`)
- [ ] Crear tests en `tests/test_visualizations.py` (12 tests)
- [ ] Documentar en README con ejemplos visuales
- [ ] Añadir galería de gráficos en docs/

---

## Related Specs
- [Body Composition](../02-data-extraction/body-composition.spec.md) - Datos para gráficos
- [Activities](../02-data-extraction/activities.spec.md) - Datos para gráficos
- [HTML Reports](./html-reports.spec.md) - Embebe estos gráficos

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 11 (anotaciones) para destacar PRs
- **2025-01-30**: Añadido Scenario 12 (responsive) para múltiples dispositivos
