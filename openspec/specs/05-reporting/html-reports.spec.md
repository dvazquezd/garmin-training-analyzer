# Feature: Generación de Reportes HTML Interactivos

## Context
**Por qué existe**: Los usuarios necesitan visualizar análisis de forma profesional y compartirlos con entrenadores/equipos. Reportes TXT/Markdown son limitados: sin gráficos embebidos, estilo básico, difíciles de compartir. HTML permite charts embebidos, responsive design, portabilidad (un archivo standalone) y marca profesional.

**Valor que aporta**:
- Reportes visuales con gráficos embebidos (matplotlib → PNG → base64)
- Diseño responsive y mobile-friendly
- Compartible vía email/web (archivo único, sin dependencias externas)
- Marca profesional (gradients, cards, iconos, animaciones sutiles)
- Exportable a PDF (via navegador: Print → Save as PDF)

---

## User Story
**Como** atleta que comparte análisis con su entrenador o equipo  
**Quiero** generar reporte HTML profesional con gráficos embebidos  
**Para** enviar resultados de forma clara, visualmente atractiva y fácil de entender

---

## Acceptance Criteria

### Scenario 1: Generar reporte HTML completo con datos reales
**Given** el análisis tiene datos completos:
- 15 actividades en los últimos 30 días
- Análisis LLM de 1200 palabras (Markdown formateado)
- 4 gráficos PNG (composición corporal, distribución actividades, volumen semanal, zonas FC)
- Composición corporal: peso, % grasa, masa muscular
**When** ejecuta `generate_html_report(activities, analysis, charts, body_comp)`  
**Then** crea archivo `analysis_reports/reporte_20250130_143022.html`  
**And** el HTML contiene estructura completa:
- `<head>` con meta tags (viewport, charset, Open Graph)
- Header con título, nombre atleta, periodo, fecha generación
- Cards de KPIs: total distancia, actividades, calorías, FC promedio
- Sección de análisis LLM (Markdown → HTML)
- 4 gráficos embebidos como base64
- Tabla de actividades con todas las métricas
- Footer con timestamp y versión del sistema
**And** el archivo es standalone (CSS inline, sin JS/CSS externos)  
**And** tamaño del archivo < 5 MB  
**And** registra: `"📄 Reporte HTML generado: reporte_20250130_143022.html (2.3 MB)"`

---

### Scenario 2: Responsive design para dispositivos móviles
**Given** se generó reporte HTML completo  
**When** se abre en dispositivo móvil (viewport 375px × 667px)  
**Then** el layout se adapta automáticamente:
- Cards de KPIs apiladas verticalmente (grid 1 columna)
- Gráficos escalados a 100% width (mantienen aspect ratio)
- Tabla de actividades con scroll horizontal
- Texto legible: font-size >= 14px
- Padding/margins ajustados para pantalla pequeña
- Gradiente del header visible y atractivo
**And** NO hay contenido cortado, solapado o fuera de viewport  
**And** interacción táctil funciona correctamente

---

### Scenario 3: Gráficos embebidos como base64 (sin archivos externos)
**Given** matplotlib generó 4 gráficos PNG en memoria:
- `body_composition.png` (150 KB)
- `activity_distribution.png` (80 KB)
- `weekly_volume.png` (120 KB)
- `heart_rate_zones.png` (100 KB)
**When** se embebe en HTML  
**Then** cada imagen se convierte a base64:
```python
img_bytes = chart_fig.to_bytes()
img_b64 = base64.b64encode(img_bytes).decode('utf-8')
html_img = f'<img src="data:image/png;base64,{img_b64}" alt="Chart" class="chart-img">'
```
**And** NO genera archivos PNG separados en disco  
**And** todos los gráficos están embebidos en el HTML  
**And** el HTML es portable (funciona sin acceso a archivos externos)  
**And** tamaño total del HTML es razonable (< 5 MB)

---

### Scenario 4: Manejo de datos faltantes - sin actividades
**Given** el usuario no tiene actividades en el periodo analizado  
**When** genera reporte HTML  
**Then** muestra mensaje informativo en lugar de gráficos vacíos:
```html
<div class="alert alert-warning">
  <span class="icon">⚠️</span>
  <div>
    <strong>No hay actividades para mostrar</strong>
    <p>No se encontraron actividades en este periodo. 
       Intenta aumentar ANALYSIS_DAYS o sincroniza tu dispositivo Garmin.</p>
  </div>
</div>
```
**And** NO genera gráficos PNG vacíos (que romperían layout)  
**And** cards de KPIs muestran "N/A" o "0"  
**And** tabla de actividades oculta (no se muestra vacía)  
**And** el reporte sigue siendo HTML válido (sin errores 500)  
**And** el análisis LLM puede sugerir acciones

---

### Scenario 5: Análisis LLM con Markdown → HTML enriquecido
**Given** el LLM retorna análisis con formato Markdown complejo:
```markdown
## 1. Resumen Ejecutivo
Tu entrenamiento muestra **mejora consistente** en las últimas 4 semanas:
- Volumen: 45 km/semana (+15% vs mes anterior)
- FC promedio: 145 bpm (zona 2 predominante)
- Consistencia: 4-5 sesiones/semana

### Recomendaciones
1. **Incrementar volumen**: +10% semanal
2. **Añadir trabajo en Z2**: 80% del volumen total
3. **Recovery**: mínimo 1 día completo/semana

> "La consistencia vence al talento" - Eliud Kipchoge
```
**When** se convierte a HTML  
**Then** aplica transformación completa:
```html
<h2>1. Resumen Ejecutivo</h2>
<p>Tu entrenamiento muestra <strong>mejora consistente</strong> en las últimas 4 semanas:</p>
<ul>
  <li>Volumen: 45 km/semana (+15% vs mes anterior)</li>
  <li>FC promedio: 145 bpm (zona 2 predominante)</li>
  <li>Consistencia: 4-5 sesiones/semana</li>
</ul>
<h3>Recomendaciones</h3>
<ol>
  <li><strong>Incrementar volumen</strong>: +10% semanal</li>
  <li><strong>Añadir trabajo en Z2</strong>: 80% del volumen total</li>
  <li><strong>Recovery</strong>: mínimo 1 día completo/semana</li>
</ol>
<blockquote>
  <p>"La consistencia vence al talento" - Eliud Kipchoge</p>
</blockquote>
```
**And** aplica estilos CSS:
- `h2` con color primario (#00A1E0), font-size 1.8rem
- `h3` con color secundario, font-size 1.4rem
- `ul/ol` con indentación y spacing
- `blockquote` con borde izquierdo (4px solid) y fondo gris claro
- `strong` con font-weight 700

---

### Scenario 6: Tabla de actividades completa y estilizada
**Given** el reporte incluye tabla con 15 actividades  
**When** se renderiza en HTML  
**Then** genera tabla HTML completa:
```html
<table class="activities-table">
  <thead>
    <tr>
      <th>Fecha</th>
      <th>Tipo</th>
      <th>Nombre</th>
      <th>Distancia</th>
      <th>Duración</th>
      <th>FC Prom</th>
      <th>FC Max</th>
      <th>Calorías</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-30</td>
      <td><span class="badge badge-running">Running</span></td>
      <td>Morning Run</td>
      <td>10.5 km</td>
      <td>54:05</td>
      <td>145 bpm</td>
      <td>178 bpm</td>
      <td>650 kcal</td>
    </tr>
    <!-- ... más filas -->
  </tbody>
</table>
```
**And** tiene estilos aplicados:
- Header con background gradient
- Filas alternadas (nth-child(odd) con fondo gris claro)
- Hover effect en filas (cambio de fondo)
- Badges de colores para tipos de actividad
- Scroll horizontal si ancho > viewport
- Bordes redondeados (border-radius)
**And** métricas formateadas: distancia en km, duración en HH:MM:SS, FC con "bpm"

---

### Scenario 7: Tema/branding personalizado con colores Garmin
**Given** el sistema tiene configuración de tema:
```python
THEME = {
    'primary': '#00A1E0',      # Garmin blue
    'secondary': '#FF6B35',    # Orange accent
    'success': '#28A745',      # Green
    'warning': '#FFC107',      # Yellow
    'danger': '#DC3545',       # Red
    'background': '#F8F9FA',   # Light gray
    'text': '#212529',         # Dark gray
    'text_muted': '#6C757D'    # Muted gray
}
```
**When** genera reporte HTML  
**Then** aplica colores del tema en todos los elementos:
- Header: gradient linear 135deg (primary → secondary)
- Cards: border-top 4px solid primary
- KPI values: color primary, font-weight bold
- Links: color primary, hover con darken 10%
- Badges: background según tipo (running=primary, cycling=success, etc.)
- Buttons: background primary, hover con darken 15%
**And** el tema es consistente en todo el documento  
**And** contraste de colores cumple WCAG AA (accesibilidad)

---

### Scenario 8: Metadatos Open Graph para compartir en redes sociales
**Given** se genera reporte HTML  
**When** se comparte link en WhatsApp/Telegram/Slack  
**Then** incluye meta tags Open Graph en `<head>`:
```html
<meta property="og:title" content="Training Analysis - David García" />
<meta property="og:description" content="60 days analysis · 45 activities · 312 km" />
<meta property="og:type" content="article" />
<meta property="og:image" content="data:image/png;base64,..." />
<meta name="twitter:card" content="summary_large_image" />
```
**And** muestra preview atractivo al compartir (título, descripción, imagen)  
**And** la imagen preview es el primer gráfico (composición corporal o distribución)

---

### Scenario 9: Exportar a PDF desde navegador (Print friendly)
**Given** se generó reporte HTML completo  
**When** el usuario abre en navegador y hace Print → Save as PDF  
**Then** el CSS incluye reglas `@media print`:
```css
@media print {
  @page { margin: 1cm; }
  header { page-break-after: avoid; }
  .chart-container { page-break-inside: avoid; }
  table { font-size: 10pt; }
  .no-print { display: none; }
}
```
**And** el PDF generado es limpio:
- Sin colores de fondo innecesarios (ahorro de tinta)
- Gráficos en alta resolución
- Saltos de página lógicos (no corta gráficos/tablas)
- Márgenes apropiados
**And** tamaño del PDF < 3 MB

---

### Scenario 10: Loading states y animaciones sutiles (futuro: con JS)
**Given** el reporte HTML se carga en navegador  
**When** el usuario scroll por el contenido  
**Then** aplica animaciones CSS sutiles:
- Cards con `fade-in` animation (0.3s ease)
- Gráficos con `slide-up` animation (0.5s ease)
- Hover effects suaves (transition: all 0.2s ease)
**And** las animaciones NO son intrusivas  
**And** se pueden desactivar con `prefers-reduced-motion`

---

### Scenario 11: Versión impresa del reporte (sin interactividad)
**Given** el sistema genera reporte HTML  
**When** NO se incluye JavaScript (HTML/CSS puro)  
**Then** el reporte funciona completamente sin JS:
- Todos los gráficos son imágenes estáticas (base64)
- Tabla de actividades visible y scrollable (CSS overflow)
- No hay elementos interactivos (tooltips, modals, etc.)
- Funcionamiento garantizado en cualquier navegador (incluso antiguos)
**And** carga en < 2 segundos en conexión lenta  
**And** compatible con lectores de pantalla (accesibilidad)

---

### Scenario 12: Internacionalización - soporte para español e inglés
**Given** el usuario tiene configurado idioma en `.env`:
```env
LANGUAGE=es  # español / en (english)
```
**When** genera reporte HTML  
**Then** todos los textos se muestran en español:
- "Análisis de Entrenamiento" (no "Training Analysis")
- "Actividades" (no "Activities")
- "Distancia Total" (no "Total Distance")
- Fechas en formato DD/MM/YYYY (no MM/DD/YYYY)
**And** los números usan formato local:
- 10.5 km (español) vs 10.5 km (inglés igual, pero 1,234.56 vs 1.234,56)
**And** el HTML tiene atributo `lang="es"` en tag `<html>`

---

## Technical Notes
- **Template engine**: Jinja2 (`pip install jinja2`)
- **Markdown parser**: `markdown` library (`pip install markdown`)
- **Base64 encoding**: `base64.b64encode(png_bytes).decode('utf-8')`
- **CSS framework**: Custom CSS inline (no Bootstrap/Tailwind para portabilidad)
- **Estilos**: 
  - CSS Grid para layout responsive
  - Flexbox para cards y componentes
  - Media queries: `@media (max-width: 768px)` para mobile
- **Tamaño límite**: Alertar si HTML > 10 MB (gráficos muy pesados)
- **Formato de fechas**: `datetime.strftime('%d/%m/%Y %H:%M')` para español
- **Accesibilidad**: 
  - Alt text en imágenes
  - Roles ARIA en tablas
  - Contraste WCAG AA mínimo

---

## Out of Scope
❌ JavaScript interactivo (gráficos con D3.js/Chart.js/Plotly)  
❌ Exportación directa a PDF (usar navegador → Print → PDF)  
❌ Dark mode (solo light theme por ahora)  
❌ Editor WYSIWYG para customizar reporte  
❌ Hosting del reporte (upload a servidor)  
❌ Firma digital o watermarking avanzado

---

## Testing Strategy
```python
# tests/test_html_reporter.py

import pytest
from bs4 import BeautifulSoup
from src.html_reporter import HTMLReporter

def test_generate_html_with_full_data():
    """Scenario 1: Full report"""
    reporter = HTMLReporter()
    html = reporter.generate(
        activities=mock_activities(15),
        analysis="# Test analysis...",
        charts=[mock_chart() for _ in range(4)],
        body_composition=mock_body_comp()
    )
    
    assert '<html' in html
    assert 'data:image/png;base64' in html
    assert len(html) < 5_000_000  # < 5 MB

def test_responsive_meta_tags():
    """Scenario 2: Mobile-friendly"""
    reporter = HTMLReporter()
    html = reporter.generate(activities=[], analysis="Test")
    
    soup = BeautifulSoup(html, 'html.parser')
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    
    assert viewport_meta is not None
    assert 'width=device-width' in viewport_meta['content']

def test_embed_charts_as_base64():
    """Scenario 3: Base64 images"""
    reporter = HTMLReporter()
    chart_png = create_test_chart_bytes()
    
    html_img = reporter._embed_chart(chart_png, alt="Test Chart")
    
    assert html_img.startswith('<img src="data:image/png;base64,')
    assert 'alt="Test Chart"' in html_img

def test_no_activities_shows_warning():
    """Scenario 4: Empty data"""
    reporter = HTMLReporter()
    html = reporter.generate(
        activities=[],
        analysis="No data analysis",
        charts=[]
    )
    
    assert '⚠️' in html or 'alert-warning' in html
    assert 'No hay actividades' in html

def test_markdown_to_html_conversion():
    """Scenario 5: Markdown rendering"""
    reporter = HTMLReporter()
    md = "## Título\n**Negrita** y _cursiva_\n- Item 1\n- Item 2"
    
    html = reporter._markdown_to_html(md)
    
    assert '<h2>Título</h2>' in html
    assert '<strong>Negrita</strong>' in html
    assert '<em>cursiva</em>' in html
    assert '<ul>' in html and '<li>Item 1</li>' in html

def test_activities_table_with_data():
    """Scenario 6: Table generation"""
    reporter = HTMLReporter()
    activities = mock_activities(5)
    
    table_html = reporter._generate_activities_table(activities)
    
    assert '<table' in table_html
    assert '<thead>' in table_html
    assert '<tbody>' in table_html
    assert 'activities-table' in table_html

def test_theme_colors_applied():
    """Scenario 7: Branding"""
    theme = {
        'primary': '#00A1E0',
        'secondary': '#FF6B35'
    }
    reporter = HTMLReporter(theme=theme)
    html = reporter.generate(activities=[], analysis="Test")
    
    assert '#00A1E0' in html  # Primary color used
    assert '#FF6B35' in html  # Secondary color used

def test_open_graph_meta_tags():
    """Scenario 8: Social sharing"""
    reporter = HTMLReporter()
    html = reporter.generate(
        activities=mock_activities(10),
        analysis="Test analysis",
        athlete_name="John Doe"
    )
    
    soup = BeautifulSoup(html, 'html.parser')
    og_title = soup.find('meta', property='og:title')
    
    assert og_title is not None
    assert 'John Doe' in og_title['content']

def test_print_friendly_styles():
    """Scenario 9: Print CSS"""
    reporter = HTMLReporter()
    html = reporter.generate(activities=[], analysis="Test")
    
    assert '@media print' in html
    assert 'page-break-inside: avoid' in html

def test_no_javascript_required():
    """Scenario 11: Static HTML"""
    reporter = HTMLReporter()
    html = reporter.generate(activities=[], analysis="Test")
    
    assert '<script' not in html  # No JS
    assert 'onclick=' not in html  # No inline JS

def test_internationalization_spanish():
    """Scenario 12: i18n"""
    reporter = HTMLReporter(language='es')
    html = reporter.generate(
        activities=mock_activities(5),
        analysis="Test"
    )
    
    assert 'Análisis de Entrenamiento' in html
    assert 'Actividades' in html
    assert 'lang="es"' in html
```

---

## Implementation Checklist
- [ ] Crear módulo `src/html_reporter.py` con clase `HTMLReporter`
- [ ] Crear template Jinja2 en `src/templates/report_template.html`
- [ ] Implementar conversión Markdown → HTML con `markdown` library
- [ ] Añadir embebido de gráficos como base64
- [ ] Crear CSS inline completo (responsive + print)
- [ ] Implementar generación de tabla de actividades
- [ ] Añadir sistema de temas (colors, fonts)
- [ ] Incluir meta tags Open Graph para sharing
- [ ] Implementar manejo de datos faltantes (warnings)
- [ ] Añadir internacionalización (español/inglés)
- [ ] Crear tests en `tests/test_html_reporter.py` (12 tests)
- [ ] Documentar en README con screenshots
- [ ] Añadir ejemplos de reportes generados

---

## Related Specs
- [Visualizations](./visualizations.spec.md) - Genera los gráficos PNG
- [LLM Analysis](../04-llm-analysis/multi-provider.spec.md) - Proporciona el texto del análisis
- [Activities Extraction](../02-data-extraction/activities.spec.md) - Proporciona datos de actividades

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 11 (sin JS) para máxima compatibilidad
- **2025-01-30**: Añadido Scenario 12 (i18n) para soporte multiidioma
