# Feature: Extracción de Actividades desde Garmin Connect

## Context
**Por qué existe**: Los usuarios necesitan analizar sus entrenamientos. Garmin almacena actividades (carreras, ciclismo, natación, gym) con métricas detalladas (distancia, duración, FC, pace, calorías).

**Valor que aporta**: 
- Obtener historial completo de actividades en periodo definido
- Extraer métricas clave para análisis con LLM
- Manejar casos edge (actividades sin GPS, datos incompletos, tipos raros)
- Optimizar con cache para reducir llamadas API

---

## User Story
**Como** atleta que entrena regularmente  
**Quiero** extraer todas mis actividades de los últimos N días con sus métricas  
**Para** analizar mi progreso, identificar patrones y recibir recomendaciones personalizadas

---

## Acceptance Criteria

### Scenario 1: Extraer actividades de periodo definido
**Given** el usuario tiene 10 actividades en los últimos 30 días  
**And** ejecuta con configuración:
```env
ANALYSIS_DAYS=30
```
**When** el sistema llama a `garmin_client.get_activities(days=30)`  
**Then** retorna lista con 10 actividades  
**And** cada actividad contiene estructura completa:
```python
{
    'activityId': 123456789,
    'activityName': 'Morning Run',
    'activityType': {'typeKey': 'running'},
    'distance': 10450.5,           # metros
    'duration': 3245.0,             # segundos
    'averageHR': 145,               # bpm
    'maxHR': 178,                   # bpm
    'startTimeLocal': '2025-01-15T07:30:00',
    'calories': 650,
    'averageSpeed': 3.22,           # m/s
    'elevationGain': 120.0          # metros
}
```
**And** ordena actividades por fecha descendente (más reciente primero)  
**And** registra en log: `"✅ Extraídas 10 actividades de los últimos 30 días"`

---

### Scenario 2: Usuario sin actividades en el periodo
**Given** el usuario no ha registrado actividades en los últimos 30 días  
**When** ejecuta `garmin_client.get_activities(days=30)`  
**Then** retorna lista vacía `[]`  
**And** registra warning en log:
```
⚠️  No se encontraron actividades en los últimos 30 días
   Sugerencias:
   - Aumenta ANALYSIS_DAYS en .env
   - Verifica sincronización de tu dispositivo Garmin
   - Comprueba que hay actividades en connect.garmin.com
```
**And** NO lanza excepción (permite análisis vacío)  
**And** el programa continúa normalmente

---

### Scenario 3: Actividad sin GPS (indoor/treadmill)
**Given** existe una actividad de tipo "Treadmill Running" o "Indoor Cycling"  
**When** extrae la actividad  
**Then** el campo `distance` puede ser `None` o `0` (si no hay sensor)  
**And** marca la actividad con flag: `gpsDisabled: true`  
**And** el sistema NO falla la extracción  
**And** incluye la actividad en el análisis con nota: `"(Indoor - distancia estimada)"`

---

### Scenario 4: Actividad con datos parciales (sin FC)
**Given** el usuario corrió sin banda de frecuencia cardíaca  
**When** extrae la actividad  
**Then** los campos `averageHR` y `maxHR` son `None`  
**And** el sistema acepta la actividad (métricas opcionales)  
**And** marca con flag: `hrDataMissing: true`  
**And** el análisis LLM considera esta limitación  
**And** registra en debug: `"Actividad 123456 sin datos de FC"`

---

### Scenario 5: Cache de actividades para evitar llamadas repetidas
**Given** el usuario ejecutó el análisis hace 2 horas  
**And** tiene configurado:
```env
USE_CACHE=true
CACHE_TTL_HOURS=24
```
**When** ejecuta nuevamente el análisis  
**Then** el sistema carga actividades desde cache SQLite  
**And** NO hace llamada a Garmin Connect API  
**And** registra en log:
```
💾 Actividades cargadas desde caché
   Periodo: últimos 30 días
   Válido por: 22h más
   Actividades: 10
```
**And** el análisis es instantáneo (< 1 segundo)

---

### Scenario 6: Cache expirado - refetch automático
**Given** el cache tiene datos de hace 25 horas  
**And** configuración:
```env
CACHE_TTL_HOURS=24
```
**When** ejecuta análisis  
**Then** el sistema detecta que `cache_age > TTL`  
**And** registra: `"🔄 Cache expirado (25h antiguo). Actualizando..."`  
**And** hace nueva llamada a Garmin API  
**And** actualiza el cache con datos frescos  
**And** registra: `"💾 Cache actualizado (válido 24h)"`

---

### Scenario 7: Rate limit de Garmin (429 Too Many Requests)
**Given** el usuario ejecutó el script 10 veces en 5 minutos (abusivo)  
**When** intenta extraer actividades nuevamente  
**Then** Garmin responde `429 Too Many Requests`  
**And** el sistema espera 60 segundos antes de reintentar (exponential backoff)  
**And** muestra progress bar en consola:
```
⏳ Rate limit alcanzado. Esperando...
[████████████░░░░░░░░] 40s / 60s
```
**And** si persiste tras 3 reintentos, intenta cargar desde cache  
**And** si no hay cache, termina con error explicativo:
```
❌ Límite de API alcanzado y no hay datos en caché
   Espera 10 minutos antes de reintentar
```

---

### Scenario 8: Tipos de actividades soportadas
**Given** el usuario tiene actividades variadas:
- Running (carrera)
- Cycling (ciclismo)  
- Swimming (natación)
- Strength Training (gym)
- Walking (caminata)
- Hiking (senderismo)
- Yoga
- Indoor Rowing
**When** extrae actividades  
**Then** el sistema reconoce todos los tipos estándar de Garmin (50+ tipos)  
**And** mapea tipos desconocidos a categoría genérica `"other"`  
**And** NO falla por tipos nuevos o personalizados  
**And** registra en debug: `"Tipo 'CustomWorkout' mapeado a 'other'"`

---

### Scenario 9: Paginación para periodos largos
**Given** el usuario solicita análisis de 180 días  
**And** tiene 250 actividades en ese periodo  
**When** ejecuta `garmin_client.get_activities(days=180)`  
**Then** el sistema divide en múltiples requests (Garmin limita a 100/request)  
**And** hace 3 requests:
  - Request 1: días 0-60 (100 actividades)
  - Request 2: días 61-120 (100 actividades)  
  - Request 3: días 121-180 (50 actividades)
**And** combina todos los resultados en una sola lista  
**And** registra progreso:
```
📥 Descargando actividades...
   [1/3] 0-60 días: 100 actividades
   [2/3] 61-120 días: 100 actividades
   [3/3] 121-180 días: 50 actividades
   ✅ Total: 250 actividades
```

---

### Scenario 10: Actividad con métricas avanzadas (potencia, cadencia)
**Given** el usuario tiene actividad de ciclismo con medidor de potencia  
**When** extrae la actividad  
**Then** además de campos básicos, incluye métricas avanzadas:
```python
{
    'averagePower': 220,           # watts
    'normalizedPower': 235,        # watts
    'averageCadence': 85,          # rpm (ciclismo) o spm (running)
    'trainingEffect': 3.2,         # TE aeróbico
    'vo2MaxValue': 52              # VO2max estimado
}
```
**And** estas métricas son opcionales (`None` si no existen)  
**And** el análisis LLM usa estas métricas si están disponibles

---

## Technical Notes
- **Método API**: `garminconnect.Garmin.get_activities_by_date(start_date, end_date)`
- **Formato fechas**: ISO 8601 `YYYY-MM-DD` (e.g., "2025-01-15")
- **Límites API**:
  - Máximo 100 actividades por request
  - Rate limit: ~100 requests/hora por IP
  - Timeout: 30 segundos por request
- **Paginación**: Si `days > 90` o resultado > 100, dividir en múltiples requests
- **Cache**: 
  - Almacenar en SQLite tabla `activities`
  - Key: `activities_{days}days_{date}`
  - TTL configurable (default 24h)
- **Retry logic**: 
  - Reintento automático con exponential backoff: 2s, 4s, 8s
  - Máximo 3 intentos
  - No reintentar en 429 (rate limit)

---

## Out of Scope
❌ Descarga de archivos FIT/TCX/GPX originales  
❌ Análisis de splits/laps detallados (vuelta por vuelta)  
❌ Sincronización bidireccional (solo lectura)  
❌ Edición o eliminación de actividades  
❌ Stream de datos en tiempo real (live tracking)  
❌ Análisis de métricas avanzadas de sueño/estrés (fuera de actividades)

---

## Testing Strategy
```python
# tests/test_activities.py

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.garmin_client import GarminClient

def test_extract_activities_with_data():
    """Scenario 1: Happy path"""
    mock_activities = [
        {'activityId': i, 'activityType': {'typeKey': 'running'}}
        for i in range(10)
    ]
    
    with patch.object(GarminClient, '_fetch_from_api', return_value=mock_activities):
        client = GarminClient()
        activities = client.get_activities(days=30)
        
        assert len(activities) == 10
        assert activities[0]['activityType']['typeKey'] == 'running'

def test_no_activities_in_period(caplog):
    """Scenario 2: Empty result"""
    with patch.object(GarminClient, '_fetch_from_api', return_value=[]):
        client = GarminClient()
        activities = client.get_activities(days=30)
        
        assert activities == []
        assert "No se encontraron actividades" in caplog.text

@pytest.mark.parametrize("activity_type,gps_enabled", [
    ("treadmill_running", False),
    ("indoor_cycling", False),
    ("virtual_ride", False)
])
def test_indoor_activities_without_gps(activity_type, gps_enabled):
    """Scenario 3: Indoor activities"""
    activity = {
        'activityType': {'typeKey': activity_type},
        'distance': None if not gps_enabled else 5000
    }
    
    processed = GarminClient._process_activity(activity)
    assert processed['gpsDisabled'] == (not gps_enabled)

def test_activities_without_heart_rate_data():
    """Scenario 4: Missing HR data"""
    activity = {
        'activityId': 123,
        'averageHR': None,
        'maxHR': None
    }
    
    processed = GarminClient._process_activity(activity)
    assert processed['hrDataMissing'] is True

@patch('src.cache_manager.CacheManager.get')
def test_activities_loaded_from_cache(mock_cache_get):
    """Scenario 5: Cache hit"""
    mock_cache_get.return_value = [{'id': 1}, {'id': 2}]
    
    client = GarminClient(use_cache=True)
    activities = client.get_activities(days=30)
    
    assert len(activities) == 2
    mock_cache_get.assert_called_once()

@patch('src.cache_manager.CacheManager.is_expired', return_value=True)
@patch.object(GarminClient, '_fetch_from_api')
def test_cache_expired_refetch(mock_fetch, mock_expired):
    """Scenario 6: Expired cache"""
    mock_fetch.return_value = [{'id': 1}]
    
    client = GarminClient(use_cache=True)
    activities = client.get_activities(days=30)
    
    assert len(activities) == 1
    mock_fetch.assert_called_once()

@patch('garminconnect.Garmin.get_activities_by_date')
@patch('time.sleep')
def test_rate_limit_retry_with_backoff(mock_sleep, mock_api):
    """Scenario 7: Rate limit handling"""
    mock_api.side_effect = [
        requests.HTTPError("429 Too Many Requests"),
        [{'id': 1}]  # Success after wait
    ]
    
    client = GarminClient()
    activities = client.get_activities(days=30)
    
    assert len(activities) == 1
    mock_sleep.assert_called_once_with(60)

@pytest.mark.parametrize("activity_type", [
    "running", "cycling", "swimming", "strength_training",
    "walking", "hiking", "yoga", "indoor_rowing"
])
def test_supported_activity_types(activity_type):
    """Scenario 8: Various activity types"""
    activity = {'activityType': {'typeKey': activity_type}}
    processed = GarminClient._process_activity(activity)
    assert processed['activityType']['typeKey'] in GarminClient.SUPPORTED_TYPES

@patch.object(GarminClient, '_fetch_from_api')
def test_pagination_for_large_periods(mock_fetch):
    """Scenario 9: Pagination"""
    # Mock 3 API calls returning 100, 100, 50 activities
    mock_fetch.side_effect = [
        [{'id': i} for i in range(100)],
        [{'id': i} for i in range(100, 200)],
        [{'id': i} for i in range(200, 250)]
    ]
    
    client = GarminClient()
    activities = client.get_activities(days=180)
    
    assert len(activities) == 250
    assert mock_fetch.call_count == 3

def test_advanced_metrics_optional():
    """Scenario 10: Advanced metrics"""
    activity_with_power = {
        'activityId': 123,
        'averagePower': 220,
        'normalizedPower': 235
    }
    
    activity_without_power = {
        'activityId': 456
    }
    
    proc1 = GarminClient._process_activity(activity_with_power)
    proc2 = GarminClient._process_activity(activity_without_power)
    
    assert proc1.get('averagePower') == 220
    assert proc2.get('averagePower') is None
```

---

## Implementation Checklist
- [ ] Crear método `GarminClient.get_activities(days: int) -> List[Dict]`
- [ ] Implementar conversión de fechas (days → start_date, end_date)
- [ ] Añadir lógica de paginación (chunks de 100 actividades)
- [ ] Implementar detección de actividades indoor (GPS disabled)
- [ ] Manejar campos opcionales (HR, potencia, cadencia) con valores None
- [ ] Integrar con sistema de cache (check → fetch → store)
- [ ] Añadir retry logic con exponential backoff
- [ ] Implementar manejo especial de rate limit (429)
- [ ] Crear mapeo de tipos de actividades (50+ tipos → categorías)
- [ ] Añadir logging detallado (debug, info, warning)
- [ ] Crear tests en `tests/test_activities.py` (10 tests)
- [ ] Documentar estructura de datos en README
- [ ] Añadir ejemplos de uso en documentación

---

## Related Specs
- [Authentication](../01-authentication/garmin-auth.spec.md) - Requiere cliente autenticado
- [Cache System](../03-caching/sqlite-cache.spec.md) - Usa cache para optimizar
- [LLM Analysis](../04-llm-analysis/multi-provider.spec.md) - Consume estos datos

---

## Changelog
- **2025-01-30**: Spec inicial creada con 10 escenarios
- **2025-01-30**: Añadido Scenario 9 (paginación) para periodos largos
- **2025-01-30**: Añadido Scenario 10 (métricas avanzadas) para ciclistas/runners avanzados
