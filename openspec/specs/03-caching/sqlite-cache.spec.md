# Feature: Sistema de Caché Local SQLite

## Context
**Por qué existe**: Garmin Connect API tiene rate limits estrictos (100 requests/hora). Los usuarios ejecutan el análisis múltiples veces para ajustar prompts LLM, probar configuraciones o generar reportes en diferentes formatos. Sin cache, cada ejecución consume cuota API innecesariamente y tarda 10-30 segundos.

**Valor que aporta**:
- Reducir 90% de llamadas API a Garmin (ahorro de cuota)
- Análisis instantáneo (< 1s vs 10-30s con API calls)
- Funcionamiento offline con datos recientes
- Respetar límites de Garmin automáticamente
- Permitir iteración rápida en desarrollo

---

## User Story
**Como** desarrollador que itera en prompts LLM o experimenta con reportes  
**Quiero** reutilizar datos de Garmin previamente descargados  
**Para** no agotar mi cuota API, acelerar el desarrollo y trabajar offline

---

## Acceptance Criteria

### Scenario 1: Primera ejecución - crear cache vacío
**Given** es la primera vez que se ejecuta el script  
**And** el directorio `.cache/` no existe  
**When** el sistema inicializa `CacheManager()`  
**Then** crea directorio `.cache/` con permisos `700` (solo owner)  
**And** crea base de datos SQLite `.cache/garmin_cache.db`  
**And** crea tabla `cache_entries` con schema:
```sql
CREATE TABLE cache_entries (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    data_type TEXT,
    metadata TEXT
);

CREATE INDEX idx_expires_at ON cache_entries(expires_at);
```
**And** registra en log: `"💾 Cache inicializado en .cache/garmin_cache.db"`  
**And** el archivo `.db` tiene permisos `600` (seguridad)

---

### Scenario 2: Guardar actividades en cache
**Given** el sistema descargó 15 actividades de Garmin API  
**And** configuración: `CACHE_TTL_HOURS=24`  
**When** guarda en cache con `cache.set('activities_30days', data, ttl_hours=24)`  
**Then** serializa actividades como JSON string  
**And** inserta en `cache_entries`:
```python
{
    'key': 'activities_30days_20250130',
    'value': '[{"activityId": 123, ...}, ...]',  # JSON
    'created_at': '2025-01-30 10:00:00',
    'expires_at': '2025-01-31 10:00:00',  # +24h
    'data_type': 'activities',
    'metadata': '{"count": 15, "days": 30}'
}
```
**And** registra: `"💾 15 actividades guardadas en caché (válido 24h)"`  
**And** la operación es atómica (transacción SQL)

---

### Scenario 3: Leer desde cache válido
**Given** existen actividades en cache guardadas hace 10 horas  
**And** `CACHE_TTL_HOURS=24`  
**When** ejecuta `cache.get('activities_30days_20250130')`  
**Then** busca en SQLite: `SELECT value FROM cache_entries WHERE key=? AND expires_at > NOW()`  
**And** verifica que `expires_at > datetime.now(UTC)`  
**And** deserializa JSON → Python dict  
**And** retorna datos completos  
**And** registra: `"💾 Actividades cargadas desde caché (válido 14h más)"`  
**And** NO hace llamada a Garmin API  
**And** la operación tarda < 100ms

---

### Scenario 4: Cache expirado - refetch y actualizar
**Given** existen actividades en cache guardadas hace 25 horas  
**And** `CACHE_TTL_HOURS=24`  
**When** ejecuta `cache.get('activities_30days_20250130')`  
**Then** detecta que `expires_at < datetime.now(UTC)`  
**And** retorna `None` (cache miss)  
**And** registra: `"🔄 Cache expirado (25h antiguo)"`  
**And** el caller (GarminClient) hace nueva llamada a API  
**And** actualiza cache con `cache.set()` (nuevo TTL)  
**And** borra entrada expirada automáticamente  
**And** registra: `"💾 Cache actualizado (válido 24h)"`

---

### Scenario 5: Desactivar cache completamente
**Given** el usuario configura:
```env
USE_CACHE=false
```
**When** ejecuta el script  
**Then** `CacheManager` se inicializa en modo disabled  
**And** `cache.get()` siempre retorna `None`  
**And** `cache.set()` NO guarda datos (no-op)  
**And** NO verifica cache SQLite  
**And** SIEMPRE hace llamadas directas a Garmin API  
**And** registra al inicio: `"⚠️  Cache desactivado - usando API directamente"`

---

### Scenario 6: Limpiar cache manualmente (CLI)
**Given** el cache contiene 23 entradas (algunas expiradas)  
**When** el usuario ejecuta:
```bash
python training_analyzer.py --clear-cache
```
**Then** elimina TODAS las entradas: `DELETE FROM cache_entries`  
**And** mantiene la estructura de la BD (no borra archivo `.db`)  
**And** resetea autoincrement counters  
**And** ejecuta `VACUUM` para compactar BD  
**And** registra:
```
🗑️  Cache limpiado completamente
   Entradas eliminadas: 23
   Espacio liberado: 1.2 MB
```
**And** continúa con ejecución normal (fetch desde API)

---

### Scenario 7: Ver estadísticas del cache (debug/monitoring)
**Given** el cache contiene 50 entradas en total  
**When** el usuario ejecuta:
```bash
python -m src.cache_manager
```
**Then** calcula y muestra estadísticas:
```
📊 Estadísticas del Cache
┌────────────────────────────┬─────────┐
│ Métrica                    │ Valor   │
├────────────────────────────┼─────────┤
│ Total entries              │ 50      │
│ Entries válidas            │ 35      │
│ Entries expiradas          │ 15      │
│ Tamaño BD (MB)             │ 2.4     │
│ Antigüedad promedio (h)    │ 8.3     │
│ Hit rate (última hora)     │ 87%     │
│ Espacio usado / disponible │ 2.4/100 │
└────────────────────────────┴─────────┘

Top 5 keys más accedidos:
1. activities_30days_20250130 (15 hits)
2. body_composition_60days    (8 hits)
3. activities_60days_20250129 (5 hits)
...
```
**And** muestra breakdown por tipo de dato:
```
Por tipo:
- activities: 30 entries (1.8 MB)
- body_composition: 15 entries (0.4 MB)
- user_profile: 5 entries (0.2 MB)
```

---

### Scenario 8: Caché con diferentes periodos de análisis (keys únicas)
**Given** el usuario ejecuta análisis de 30 días  
**When** llama `cache.get('activities_30days_20250130')`  
**Then** genera key única: `activities_30days_20250130`  
**And** cuando luego ejecuta análisis de 60 días  
**Then** genera key diferente: `activities_60days_20250130`  
**And** ambos caches coexisten sin colisiones  
**And** cada uno tiene su TTL independiente  
**And** no se sobrescriben mutuamente

---

### Scenario 9: Corrupción de cache - recuperación automática
**Given** el archivo `.cache/garmin_cache.db` está corrupto (escritura interrumpida por crash)  
**When** el sistema intenta inicializar `CacheManager()`  
**Then** detecta error SQLite: `sqlite3.DatabaseError`  
**And** registra: `"⚠️  Cache corrupto detectado. Reinicializando..."`  
**And** renombra archivo corrupto: `.cache/garmin_cache.db.corrupt.TIMESTAMP`  
**And** crea nueva BD limpia  
**And** registra: `"💾 Nuevo cache creado"`  
**And** continúa ejecución normal (fetch desde API)  
**And** NO pierde datos críticos (solo cache temporal)

---

### Scenario 10: Limpieza automática de entradas expiradas
**Given** el cache tiene 100 entradas  
**And** 40 están expiradas (antigüedad > TTL)  
**When** ejecuta `cache._cleanup_expired()` (automático cada hora)  
**Then** elimina solo entradas expiradas:
```sql
DELETE FROM cache_entries WHERE expires_at < datetime('now')
```
**And** registra: `"🧹 Limpieza automática: 40 entradas expiradas eliminadas"`  
**And** libera espacio en disco  
**And** mejora performance de queries  
**And** ejecuta `VACUUM` si espacio liberado > 10 MB

---

### Scenario 11: Límite de tamaño del cache (protección)
**Given** el cache ha crecido a 95 MB  
**And** el límite configurado es `MAX_CACHE_SIZE_MB=100`  
**When** intenta guardar nueva entrada de 10 MB  
**Then** verifica tamaño total antes de insertar  
**And** detecta que sobrepasaría límite (95 + 10 > 100)  
**And** ejecuta limpieza agresiva: elimina 30% de entradas más antiguas  
**And** registra:
```
⚠️  Cache cerca del límite (95/100 MB)
🧹 Limpiando entradas antiguas...
💾 Espacio liberado: 30 MB
✅ Nueva entrada guardada
```
**And** continúa operación normalmente

---

### Scenario 12: Cache thread-safe (accesos concurrentes)
**Given** el usuario ejecuta 2 instancias del script simultáneamente  
**When** ambas intentan leer/escribir cache al mismo tiempo  
**Then** SQLite maneja concurrencia con WAL mode:
```sql
PRAGMA journal_mode=WAL;
```
**And** lecturas nunca bloquean otras lecturas  
**And** escrituras esperan con timeout de 5s  
**And** NO se corrompe la BD  
**And** ambas instancias obtienen datos correctos  
**And** registra en debug: `"Lock acquired after 1.2s"`

---

## Technical Notes
- **Base de datos**: SQLite3 (stdlib Python, no requiere instalación)
- **Serialización**: `json.dumps()` con `ensure_ascii=False` para UTF-8
- **Timestamps**: Siempre en UTC (`datetime.utcnow()`) para evitar issues de timezone
- **Concurrencia**: 
  - `PRAGMA journal_mode=WAL` para escrituras concurrentes
  - `PRAGMA busy_timeout=5000` para retries automáticos
- **Tamaño límite**: Alertar si `.cache/` supera 100 MB (configurable)
- **Índices**: `CREATE INDEX idx_expires_at` para queries rápidas
- **Seguridad**: Permisos `700` en directorio, `600` en archivo BD
- **Performance**: 
  - Inserción: ~1ms
  - Lectura: ~0.5ms
  - Limpieza de 1000 entradas: ~50ms

---

## Out of Scope
❌ Cache distribuido (Redis/Memcached)  
❌ Invalidación selectiva por ID de actividad  
❌ Versionado de schema (migraciones automáticas)  
❌ Compresión de datos (gzip/zstd) - no necesario para volúmenes actuales  
❌ Replicación del cache entre máquinas  
❌ Cache en memoria (LRU) - SQLite ya es suficientemente rápido

---

## Testing Strategy
```python
# tests/test_cache.py

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from src.cache_manager import CacheManager
from freezegun import freeze_time

def test_initialize_cache_first_run(tmp_path):
    """Scenario 1: Create cache"""
    cache = CacheManager(cache_dir=tmp_path)
    assert (tmp_path / 'garmin_cache.db').exists()
    # Verify schema
    result = cache._execute("SELECT name FROM sqlite_master WHERE type='table'")
    assert 'cache_entries' in [r[0] for r in result]

def test_save_and_retrieve_from_valid_cache():
    """Scenarios 2 & 3: Save/retrieve"""
    cache = CacheManager()
    test_data = [{'id': 1, 'name': 'test'}]
    
    cache.set('activities_30days', test_data, ttl_hours=24)
    retrieved = cache.get('activities_30days')
    
    assert retrieved == test_data

def test_expired_cache_returns_none():
    """Scenario 4: Expired cache"""
    cache = CacheManager()
    cache.set('old_data', {'test': 1}, ttl_hours=1)
    
    # Fast-forward time 2 hours
    with freeze_time(datetime.now() + timedelta(hours=2)):
        result = cache.get('old_data')
        assert result is None

def test_cache_disabled_bypasses_storage():
    """Scenario 5: Disabled cache"""
    cache = CacheManager(use_cache=False)
    
    cache.set('key', 'value')
    result = cache.get('key')
    
    assert result is None  # Not stored

def test_clear_cache_removes_all_entries():
    """Scenario 6: Clear cache"""
    cache = CacheManager()
    cache.set('key1', 'val1')
    cache.set('key2', 'val2')
    
    deleted_count = cache.clear()
    
    assert deleted_count == 2
    assert cache.count() == 0

def test_cache_statistics():
    """Scenario 7: Statistics"""
    cache = CacheManager()
    cache.set('key1', 'val1', ttl_hours=1)
    cache.set('key2', 'val2', ttl_hours=24)
    
    with freeze_time(datetime.now() + timedelta(hours=2)):
        stats = cache.get_statistics()
        
        assert stats['total_entries'] == 2
        assert stats['valid_entries'] == 1
        assert stats['expired_entries'] == 1

def test_different_periods_different_keys():
    """Scenario 8: Unique keys"""
    cache = CacheManager()
    
    cache.set('activities_30days_20250130', [1, 2, 3])
    cache.set('activities_60days_20250130', [4, 5, 6, 7])
    
    data30 = cache.get('activities_30days_20250130')
    data60 = cache.get('activities_60days_20250130')
    
    assert len(data30) == 3
    assert len(data60) == 4

def test_corrupted_db_reinitializes(tmp_path):
    """Scenario 9: Recovery from corruption"""
    cache_file = tmp_path / 'garmin_cache.db'
    
    # Create corrupted file
    cache_file.write_bytes(b'corrupted data not sqlite')
    
    # Initialize should handle corruption
    cache = CacheManager(cache_dir=tmp_path)
    
    # Verify new DB was created
    assert cache_file.exists()
    assert cache.count() == 0  # Empty after recovery

def test_automatic_cleanup_expired():
    """Scenario 10: Auto cleanup"""
    cache = CacheManager()
    
    # Add entries with short TTL
    for i in range(5):
        cache.set(f'key_{i}', f'val_{i}', ttl_hours=1)
    
    # Fast-forward 2 hours
    with freeze_time(datetime.now() + timedelta(hours=2)):
        deleted = cache._cleanup_expired()
        
        assert deleted == 5
        assert cache.count() == 0

def test_cache_size_limit_enforcement(tmp_path):
    """Scenario 11: Size limit"""
    cache = CacheManager(cache_dir=tmp_path, max_size_mb=1)
    
    # Try to add large data
    large_data = 'x' * 2_000_000  # 2 MB string
    
    with pytest.raises(ValueError, match="Cache size limit"):
        cache.set('large_key', large_data)

@pytest.mark.slow
def test_concurrent_access(tmp_path):
    """Scenario 12: Thread safety"""
    import threading
    
    cache = CacheManager(cache_dir=tmp_path)
    errors = []
    
    def worker(thread_id):
        try:
            for i in range(100):
                cache.set(f'key_{thread_id}_{i}', f'val_{i}')
                cache.get(f'key_{thread_id}_{i}')
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0  # No concurrency errors
    assert cache.count() == 500  # All entries saved
```

---

## Implementation Checklist
- [ ] Crear módulo `src/cache_manager.py`
- [ ] Implementar clase `CacheManager` con métodos: `get()`, `set()`, `clear()`, `count()`
- [ ] Añadir inicialización de BD con schema completo
- [ ] Implementar serialización JSON (UTF-8 safe)
- [ ] Configurar WAL mode para concurrencia
- [ ] Añadir método `get_statistics()` para monitoring
- [ ] Implementar limpieza automática de expirados
- [ ] Añadir protección de tamaño máximo
- [ ] Manejar corrupción con recovery automático
- [ ] Crear CLI para estadísticas: `python -m src.cache_manager`
- [ ] Añadir logging detallado (debug, info)
- [ ] Crear tests exhaustivos en `tests/test_cache.py` (12 tests)
- [ ] Documentar configuración en README
- [ ] Añadir ejemplos de uso

---

## Related Specs
- [Authentication](../01-authentication/garmin-auth.spec.md) - Cache reduce necesidad de re-auth
- [Activities Extraction](../02-data-extraction/activities.spec.md) - Principal consumidor del cache
- [Body Composition](../02-data-extraction/body-composition.spec.md) - También usa cache

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 11 (límite de tamaño) para prevenir crecimiento infinito
- **2025-01-30**: Añadido Scenario 12 (thread safety) para ejecuciones concurrentes
