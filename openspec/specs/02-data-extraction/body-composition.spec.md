# Feature: Extracción de Composición Corporal desde Garmin Connect

## Context
**Por qué existe**: La composición corporal (peso, % grasa, masa muscular, BMI) es crucial para evaluar progreso atlético. Garmin almacena datos de básculas conectadas (Index, Aria, etc.). Estas métricas complementan el análisis de actividades para entender adaptaciones fisiológicas al entrenamiento.

**Valor que aporta**:
- Seguimiento de evolución de peso y % grasa corporal
- Correlación entre composición y rendimiento
- Detección de pérdida muscular (overtraining)
- Validación de progreso en objetivos de composición
- Análisis de hidratación y masa ósea

---

## User Story
**Como** atleta que monitorea su composición corporal  
**Quiero** extraer datos históricos de peso, % grasa, masa muscular de Garmin  
**Para** analizar cómo mi cuerpo se adapta al entrenamiento y ajustar mi estrategia

---

## Acceptance Criteria

### Scenario 1: Extraer composición corporal de periodo definido
**Given** el usuario tiene báscula Garmin Index conectada  
**And** tiene 20 mediciones en los últimos 60 días  
**And** configuración:
```env
ANALYSIS_DAYS=60
```
**When** ejecuta `garmin_client.get_body_composition(days=60)`  
**Then** retorna lista con 20 mediciones  
**And** cada medición contiene estructura completa:
```python
{
    'date': '2025-01-30',
    'timestamp': '2025-01-30T07:15:00',
    'weight': 75500,              # gramos
    'bmi': 23.4,                  # kg/m²
    'bodyFat': 18.5,              # porcentaje
    'bodyWater': 58.2,            # porcentaje
    'boneMass': 3200,             # gramos
    'muscleMass': 58500,          # gramos
    'visceralFat': 8,             # nivel 1-59
    'metabolicAge': 28            # años
}
```
**And** ordena mediciones por fecha (más reciente primero)  
**And** registra: `"📊 Extraídas 20 mediciones de composición corporal (60 días)"`

---

### Scenario 2: Usuario sin báscula conectada
**Given** el usuario NO tiene báscula Garmin conectada  
**When** intenta extraer composición corporal  
**Then** Garmin API retorna lista vacía o `null`  
**And** registra warning:
```
⚠️  No se encontraron datos de composición corporal
   
   Posibles causas:
   - No tienes báscula Garmin conectada
   - La báscula no ha sincronizado datos
   - Los datos no existen en el periodo analizado
   
   El análisis continuará sin métricas de composición corporal.
```
**And** NO lanza excepción (el análisis continúa sin estos datos)  
**And** el sistema marca flag: `body_composition_available: false`

---

### Scenario 3: Conversión de unidades (gramos → kilogramos)
**Given** Garmin API retorna peso en gramos: `weight: 75500`  
**When** procesa la medición  
**Then** convierte automáticamente a kilogramos: `75.5 kg`  
**And** aplica redondeo a 1 decimal  
**And** lo mismo para masa muscular y ósea  
**And** registra en debug: `"Peso convertido: 75500g → 75.5kg"`

---

### Scenario 4: Mediciones con datos parciales (sin % grasa)
**Given** el usuario tiene báscula básica que solo mide peso  
**When** extrae mediciones  
**Then** los campos `bodyFat`, `muscleMass`, `boneMass` son `None`  
**And** el sistema acepta la medición (métricas opcionales)  
**And** marca con flag: `advanced_metrics_available: false`  
**And** el análisis menciona: `"Solo datos de peso disponibles"`

---

### Scenario 5: Cálculo de tendencias (weight change, body fat change)
**Given** hay 20 mediciones en el periodo  
**When** calcula estadísticas  
**Then** computa métricas agregadas:
```python
{
    'initial_weight': 76.8,      # kg (primera medición)
    'final_weight': 75.5,        # kg (última medición)
    'weight_change': -1.3,       # kg (final - initial)
    'weight_change_pct': -1.69,  # % ((final-initial)/initial * 100)
    'initial_body_fat': 19.2,    # %
    'final_body_fat': 18.5,      # %
    'body_fat_change': -0.7,     # puntos porcentuales
    'avg_weight': 76.1,          # kg (promedio periodo)
    'min_weight': 75.2,          # kg
    'max_weight': 77.1,          # kg
    'measurement_count': 20,
    'measurement_frequency': 3.0  # días entre mediciones (promedio)
}
```
**And** registra: `"📉 Cambio de peso: -1.3 kg (-1.69%) en 60 días"`

---

### Scenario 6: Cache de composición corporal
**Given** el usuario ejecutó análisis hace 5 horas  
**And** configuración:
```env
USE_CACHE=true
CACHE_TTL_HOURS=24
```
**When** ejecuta nuevamente  
**Then** carga mediciones desde cache SQLite  
**And** NO hace llamada a Garmin API  
**And** registra: `"💾 Composición corporal cargada desde caché (válido 19h más)"`

---

### Scenario 7: Detección de outliers (mediciones anómalas)
**Given** hay 15 mediciones con pesos entre 75-77 kg  
**And** existe 1 medición con peso 95 kg (claramente errónea)  
**When** procesa las mediciones  
**Then** detecta el outlier usando Z-score (> 3 std dev)  
**And** registra warning:
```
⚠️  Medición anómala detectada
   Fecha: 2025-01-15
   Peso: 95.0 kg (desviación: +18 kg del promedio)
   Acción: Marcada como sospechosa
```
**And** marca la medición con flag: `is_outlier: true`  
**And** NO la incluye en cálculos de tendencia (pero la muestra en tabla)

---

### Scenario 8: Interpolación de datos faltantes
**Given** hay mediciones los días 1, 2, 5, 8, 10 (falta días 3, 4, 6, 7, 9)  
**When** el usuario solicita interpolación: `interpolate=True`  
**Then** calcula valores intermedios con interpolación lineal  
**And** genera mediciones sintéticas:
```python
{
    'date': '2025-01-03',
    'weight': 75.7,  # interpolado entre día 2 y 5
    'is_interpolated': True
}
```
**And** registra: `"📈 5 mediciones interpoladas para visualización continua"`  
**And** las mediciones interpoladas se marcan visualmente en gráficos

---

### Scenario 9: Exportar composición corporal a CSV
**Given** hay 20 mediciones extraídas  
**When** el usuario ejecuta con flag `--export-body-comp-csv`  
**Then** crea archivo `analysis_reports/body_composition_20250130.csv`:
```csv
date,weight_kg,bmi,body_fat_pct,muscle_mass_kg,bone_mass_kg
2025-01-30,75.5,23.4,18.5,58.5,3.2
2025-01-29,75.7,23.5,18.6,58.4,3.2
...
```
**And** registra: `"📄 Composición corporal exportada a CSV (20 filas)"`

---

### Scenario 10: Correlación peso-rendimiento
**Given** hay mediciones de peso Y actividades en el mismo periodo  
**When** calcula correlaciones  
**Then** computa correlación entre peso y métricas de rendimiento:
```python
{
    'weight_vs_average_pace': -0.32,  # correlación negativa
    'weight_vs_average_hr': 0.18,
    'weight_vs_distance': -0.15
}
```
**And** interpreta correlaciones:
```
📊 Correlación Peso-Rendimiento
- Peso vs Pace: -0.32 (moderada negativa)
  → A menor peso, mejor pace
- Peso vs FC: 0.18 (débil positiva)
  → No hay relación clara
```
**And** incluye esta sección en el análisis LLM

---

### Scenario 11: Validación de rango de datos (health checks)
**Given** una medición tiene valores fuera de rango humano:
```python
{
    'weight': 250000,      # 250 kg (imposible)
    'bodyFat': 95.0,       # 95% (imposible)
    'bmi': 65.0            # 65 (extremo)
}
```
**When** valida la medición  
**Then** detecta valores anómalos  
**And** registra error:
```
❌ Medición con valores inválidos detectada
   Fecha: 2025-01-15
   Problemas:
   - Peso: 250.0 kg (rango válido: 30-200 kg)
   - % Grasa: 95.0% (rango válido: 3-50%)
   - BMI: 65.0 (rango válido: 15-45)
   
   Esta medición será excluida del análisis.
```
**And** NO incluye la medición en resultados finales

---

### Scenario 12: Métricas avanzadas (visceral fat, metabolic age)
**Given** el usuario tiene báscula Garmin Index S2 (avanzada)  
**When** extrae mediciones  
**Then** incluye métricas adicionales:
```python
{
    'visceralFat': 8,          # nivel 1-59 (1-12 saludable)
    'metabolicAge': 28,        # edad metabólica vs cronológica
    'bodyWater': 58.2,         # % agua corporal
    'proteinPercentage': 18.5  # % proteína
}
```
**And** el análisis interpreta estas métricas:
```
🏥 Métricas Avanzadas
- Grasa visceral: Nivel 8 (Saludable: < 12)
- Edad metabólica: 28 años (Tu edad: 35 → Excelente)
- Hidratación: 58.2% (Rango óptimo: 50-65%)
```

---

## Technical Notes
- **Método API**: `garminconnect.Garmin.get_body_composition(startdate, enddate)`
- **Formato de respuesta**:
  ```python
  {
      'dateWeightList': [
          {
              'date': 1706601600000,  # Unix timestamp (ms)
              'weight': 75500,        # gramos
              'bmi': 23.4,
              'bodyFat': 18.5,
              ...
          }
      ]
  }
  ```
- **Conversiones**:
  - Peso: gramos → kg (dividir por 1000)
  - Fecha: Unix timestamp (ms) → ISO date
- **Rangos válidos** (para validación):
  - Peso: 30-200 kg
  - BMI: 15-45
  - Body fat: 3-50%
  - Muscle mass: 20-90 kg
- **Cache key**: `body_composition_{days}days_{date}`
- **Outlier detection**: Z-score > 3 (3 desviaciones estándar)
- **Interpolación**: Linear interpolation con `numpy.interp()`

---

## Out of Scope
❌ Predicción de composición futura (forecasting)  
❌ Comparación con población general (percentiles)  
❌ Integración con apps de nutrición (MyFitnessPal)  
❌ Fotos de progreso (body photos)  
❌ Mediciones manuales (sin báscula)  
❌ Edición de mediciones (solo lectura)

---

## Testing Strategy
```python
# tests/test_body_composition.py

import pytest
from datetime import datetime
from unittest.mock import patch
from src.garmin_client import GarminClient

def test_extract_body_composition_with_data():
    """Scenario 1: Extract measurements"""
    mock_data = {
        'dateWeightList': [
            {
                'date': 1706601600000,
                'weight': 75500,
                'bmi': 23.4,
                'bodyFat': 18.5,
                'muscleMass': 58500
            }
        ]
    }
    
    with patch.object(GarminClient, '_fetch_body_comp_from_api', return_value=mock_data):
        client = GarminClient()
        measurements = client.get_body_composition(days=60)
        
        assert len(measurements) == 1
        assert measurements[0]['weight'] == 75.5  # Converted to kg

def test_no_body_composition_data(caplog):
    """Scenario 2: No scale connected"""
    with patch.object(GarminClient, '_fetch_body_comp_from_api', return_value={'dateWeightList': []}):
        client = GarminClient()
        measurements = client.get_body_composition(days=60)
        
        assert measurements == []
        assert "No se encontraron datos" in caplog.text

def test_weight_conversion_grams_to_kg():
    """Scenario 3: Unit conversion"""
    measurement = {'weight': 75500, 'muscleMass': 58500}
    
    converted = GarminClient._convert_units(measurement)
    
    assert converted['weight'] == 75.5
    assert converted['muscleMass'] == 58.5

def test_partial_data_without_body_fat():
    """Scenario 4: Basic scale data only"""
    measurement = {
        'weight': 75500,
        'bmi': 23.4,
        'bodyFat': None,
        'muscleMass': None
    }
    
    processed = GarminClient._process_body_comp(measurement)
    
    assert processed['advanced_metrics_available'] is False
    assert processed['weight'] == 75.5

def test_calculate_trends():
    """Scenario 5: Trend calculation"""
    measurements = [
        {'date': '2025-01-01', 'weight': 76.8, 'bodyFat': 19.2},
        {'date': '2025-01-15', 'weight': 76.0, 'bodyFat': 18.8},
        {'date': '2025-01-30', 'weight': 75.5, 'bodyFat': 18.5}
    ]
    
    trends = GarminClient.calculate_body_comp_trends(measurements)
    
    assert trends['weight_change'] == -1.3
    assert trends['body_fat_change'] == -0.7
    assert trends['measurement_count'] == 3

@patch('src.cache_manager.CacheManager.get')
def test_body_comp_loaded_from_cache(mock_cache):
    """Scenario 6: Cache hit"""
    mock_cache.return_value = [{'weight': 75.5}]
    
    client = GarminClient(use_cache=True)
    measurements = client.get_body_composition(days=60)
    
    assert len(measurements) == 1
    mock_cache.assert_called_once()

def test_outlier_detection():
    """Scenario 7: Detect anomalies"""
    measurements = [
        {'weight': 75.0}, {'weight': 76.0}, {'weight': 75.5},
        {'weight': 95.0},  # Outlier
        {'weight': 76.2}, {'weight': 75.8}
    ]
    
    processed = GarminClient.detect_outliers(measurements)
    
    outliers = [m for m in processed if m.get('is_outlier')]
    assert len(outliers) == 1
    assert outliers[0]['weight'] == 95.0

def test_data_interpolation():
    """Scenario 8: Fill gaps"""
    measurements = [
        {'date': '2025-01-01', 'weight': 75.0},
        {'date': '2025-01-05', 'weight': 76.0}  # Gap of 4 days
    ]
    
    interpolated = GarminClient.interpolate_measurements(measurements)
    
    assert len(interpolated) == 5  # Original 2 + 3 interpolated
    assert any(m.get('is_interpolated') for m in interpolated)

def test_export_to_csv(tmp_path):
    """Scenario 9: CSV export"""
    measurements = [
        {'date': '2025-01-30', 'weight': 75.5, 'bodyFat': 18.5}
    ]
    
    csv_path = tmp_path / "body_comp.csv"
    GarminClient.export_body_comp_csv(measurements, csv_path)
    
    assert csv_path.exists()
    content = csv_path.read_text()
    assert "date,weight_kg,body_fat_pct" in content

def test_weight_performance_correlation():
    """Scenario 10: Correlation analysis"""
    body_data = [{'weight': 75.0}, {'weight': 76.0}, {'weight': 75.5}]
    activities = [
        {'avg_pace': 5.2}, {'avg_pace': 5.5}, {'avg_pace': 5.1}
    ]
    
    correlation = GarminClient.correlate_weight_performance(body_data, activities)
    
    assert 'weight_vs_average_pace' in correlation
    assert -1 <= correlation['weight_vs_average_pace'] <= 1

def test_validate_measurement_ranges():
    """Scenario 11: Validation"""
    invalid = {
        'weight': 250000,  # 250 kg
        'bodyFat': 95.0,   # 95%
        'bmi': 65.0
    }
    
    is_valid = GarminClient.validate_measurement(invalid)
    
    assert is_valid is False

def test_advanced_metrics_extraction():
    """Scenario 12: Advanced metrics"""
    measurement = {
        'weight': 75500,
        'bodyFat': 18.5,
        'visceralFat': 8,
        'metabolicAge': 28,
        'bodyWater': 58.2
    }
    
    processed = GarminClient._process_body_comp(measurement)
    
    assert processed['visceralFat'] == 8
    assert processed['metabolicAge'] == 28
```

---

## Implementation Checklist
- [ ] Crear método `GarminClient.get_body_composition(days: int)`
- [ ] Implementar conversión de unidades (gramos → kg)
- [ ] Añadir cálculo de tendencias (weight_change, body_fat_change)
- [ ] Implementar detección de outliers (Z-score)
- [ ] Añadir interpolación de datos faltantes (opcional)
- [ ] Integrar con cache (key: `body_composition_{days}days`)
- [ ] Implementar validación de rangos (health checks)
- [ ] Añadir exportación a CSV
- [ ] Crear correlación peso-rendimiento
- [ ] Implementar procesamiento de métricas avanzadas
- [ ] Añadir logging detallado
- [ ] Crear tests en `tests/test_body_composition.py` (12 tests)
- [ ] Documentar en README con ejemplos
- [ ] Añadir sección de troubleshooting para básculas

---

## Related Specs
- [Activities Extraction](./activities.spec.md) - Para correlación peso-rendimiento
- [Visualizations](../05-reporting/visualizations.spec.md) - Gráficos de composición corporal
- [LLM Analysis](../04-llm-analysis/multi-provider.spec.md) - Incluye estos datos en análisis

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 10 (correlación) para análisis avanzado
- **2025-01-30**: Añadido Scenario 12 (métricas avanzadas) para básculas premium
