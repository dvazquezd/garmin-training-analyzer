# Feature: Autenticación Segura con Garmin Connect

## Context
**Por qué existe**: La app necesita acceder a datos privados del usuario en Garmin Connect (actividades, composición corporal, métricas de salud). Garmin requiere autenticación por email/password sin soporte OAuth oficial.

**Valor que aporta**: 
- Acceso confiable a datos del usuario
- Manejo robusto de errores de red/autenticación
- Seguridad de credenciales (no exponer passwords en logs)
- Recuperación automática ante fallos temporales

---

## User Story
**Como** atleta que usa Garmin Training Analyzer  
**Quiero** autenticarme de forma segura con mis credenciales de Garmin  
**Para** que la app pueda extraer mis datos de entrenamiento sin comprometer mi seguridad

---

## Acceptance Criteria

### Scenario 1: Autenticación exitosa con credenciales válidas
**Given** el usuario tiene credenciales válidas en `.env`:
```env
GARMIN_EMAIL=user@example.com
GARMIN_PASSWORD=valid_password123
```
**When** ejecuta `python training_analyzer.py`  
**Then** el sistema se autentica exitosamente con Garmin Connect  
**And** retorna un cliente autenticado (`Garmin` object con sesión activa)  
**And** registra en log: `"✅ Autenticado como: [nombre completo del usuario]"`  
**And** NO imprime la contraseña en logs (usar `password=***` en debug logs)

---

### Scenario 2: Fallo por credenciales inválidas
**Given** el usuario tiene credenciales incorrectas:
```env
GARMIN_EMAIL=user@example.com
GARMIN_PASSWORD=wrong_password
```
**When** ejecuta `python training_analyzer.py`  
**Then** el sistema captura `GarminConnectAuthenticationError`  
**And** muestra mensaje user-friendly:
```
❌ Error de autenticación con Garmin Connect
   Verifica tus credenciales en .env:
   - GARMIN_EMAIL
   - GARMIN_PASSWORD
```
**And** el programa termina con código de salida `1`  
**And** NO expone la contraseña en el mensaje de error

---

### Scenario 3: Falta de variables de entorno
**Given** el archivo `.env` no existe  
**OR** falta `GARMIN_EMAIL` o `GARMIN_PASSWORD`  
**When** ejecuta `python training_analyzer.py`  
**Then** el sistema lanza `ValueError` antes de intentar conectar  
**And** muestra mensaje detallado:
```
❌ Configuración incompleta
   Credenciales de Garmin no encontradas.
   
   Pasos para configurar:
   1. Copia .env.example a .env
   2. Completa GARMIN_EMAIL y GARMIN_PASSWORD
   3. Verifica que .env tiene permisos correctos (600)
```
**And** el programa termina con código de salida `1`

---

### Scenario 4: Reintento automático en fallo de red temporal
**Given** el usuario tiene credenciales válidas  
**And** Garmin Connect responde con error temporal (timeout/502/503)  
**When** ejecuta `python training_analyzer.py`  
**Then** el sistema reintenta automáticamente (máximo 3 intentos)  
**And** aplica exponential backoff: espera 2s, 4s, 8s entre reintentos  
**And** registra cada intento en log:
```
⏳ Intento 1/3 falló (ConnectionTimeout). Reintentando en 2s...
⏳ Intento 2/3 falló (502 Bad Gateway). Reintentando en 4s...
✅ Autenticado correctamente en intento 3/3
```
**And** si todos los reintentos fallan, muestra mensaje final:
```
❌ No se pudo conectar con Garmin tras 3 intentos
   Posibles causas:
   - Sin conexión a internet
   - Garmin Connect está caído
   - Firewall bloqueando conexión
   
   Intenta nuevamente en unos minutos.
```

---

### Scenario 5: Credenciales por CLI (override .env)
**Given** el `.env` tiene credenciales configuradas  
**When** el usuario ejecuta:
```bash
python training_analyzer.py --email alt@example.com --password altpass
```
**Then** el sistema usa las credenciales del CLI (no las de `.env`)  
**And** NO guarda las credenciales CLI en ningún archivo  
**And** muestra warning en stderr:
```
⚠️  Usando credenciales proporcionadas por CLI
   Nota: No recomendado en producción (quedan en historial de shell)
   Usa .env para mayor seguridad
```
**And** las credenciales CLI tienen prioridad sobre `.env`

---

### Scenario 6: Usuario con 2FA activado (no soportado)
**Given** la cuenta de Garmin tiene autenticación de dos factores (2FA) habilitada  
**When** intenta autenticarse con email/password  
**Then** Garmin rechaza el login (la librería `garminconnect` no soporta 2FA)  
**And** el sistema detecta el error específico de 2FA  
**And** muestra mensaje informativo:
```
❌ Tu cuenta tiene autenticación de dos factores (2FA) activada
   
   La librería garminconnect no soporta 2FA actualmente.
   
   Soluciones temporales:
   1. Desactiva 2FA temporalmente en connect.garmin.com
   2. O espera a que la librería añada soporte 2FA
   
   Seguimiento del issue:
   https://github.com/cyberjunky/python-garminconnect/issues/XXX
```
**And** proporciona link al issue de GitHub para seguimiento

---

### Scenario 7: Rate limiting de Garmin (demasiados intentos)
**Given** el usuario ha intentado autenticarse 5+ veces en 1 minuto  
**When** intenta login nuevamente  
**Then** Garmin responde con `429 Too Many Requests`  
**And** el sistema detecta el rate limit  
**And** muestra mensaje:
```
⏸️  Demasiados intentos de login
   Garmin ha bloqueado temporalmente tu IP por seguridad.
   
   Espera 5 minutos antes de reintentar.
   
   Tip: Verifica tus credenciales antes de intentar nuevamente
        para evitar más bloqueos.
```
**And** NO reintenta automáticamente (para no empeorar el rate limit)  
**And** el programa termina con código de salida `2`

---

### Scenario 8: Sesión expirada durante ejecución larga
**Given** el usuario ejecutó el script con sesión válida  
**And** el análisis tarda más de 2 horas en completarse  
**When** intenta hacer request después de 2 horas  
**Then** Garmin responde con `401 Unauthorized` (sesión expirada)  
**And** el sistema detecta la expiración  
**And** reautentica automáticamente usando credenciales almacenadas  
**And** reintenta el request que falló  
**And** registra en log:
```
🔄 Sesión expirada detectada. Re-autenticando...
✅ Sesión renovada. Continuando análisis...
```
**And** el análisis continúa sin intervención del usuario

---

## Technical Notes
- **Librería**: `garminconnect==0.2.30`
  - Método principal: `Garmin(email, password).login()`
  - Excepciones: `GarminConnectAuthenticationError`, `GarminConnectConnectionError`, `GarminConnectTooManyRequestsError`
- **Seguridad**: 
  - Usar `logging.Filter` para sanitizar passwords en logs
  - Validar que `.env` tiene permisos `600` (solo owner read/write)
  - NO almacenar credenciales en memoria más tiempo del necesario
- **Rate Limiting**: 
  - Garmin limita a ~10 logins/hora por IP
  - Implementar cooldown local de 60s entre intentos consecutivos
- **Sesión**: 
  - La sesión Garmin dura ~24 horas
  - Cookies almacenadas en memoria (no disco) por `requests.Session`
  - Re-login automático si detecta 401 en requests posteriores

---

## Out of Scope
❌ OAuth 2.0 (Garmin no lo soporta en API no oficial)  
❌ Refresh tokens automáticos  
❌ Almacenamiento encriptado de credenciales en disco  
❌ Multi-cuenta (múltiples usuarios de Garmin simultáneos)  
❌ Proxy/VPN para evadir rate limits  
❌ Captcha solving (si Garmin lo implementa)

---

## Testing Strategy
```python
# tests/test_auth.py

import pytest
from unittest.mock import patch, MagicMock
from garminconnect import GarminConnectAuthenticationError
from src.auth import authenticate_garmin, get_credentials

def test_successful_auth_with_valid_credentials(caplog):
    """Scenario 1: Happy path"""
    with patch('garminconnect.Garmin') as mock_garmin:
        mock_client = MagicMock()
        mock_client.login.return_value = None
        mock_client.get_full_name.return_value = "John Doe"
        mock_garmin.return_value = mock_client
        
        client = authenticate_garmin("valid@email.com", "valid_pass")
        
        assert client is not None
        assert "✅ Autenticado como: John Doe" in caplog.text
        assert "valid_pass" not in caplog.text  # No password in logs

def test_auth_failure_with_invalid_credentials():
    """Scenario 2: Invalid credentials"""
    with patch('garminconnect.Garmin') as mock_garmin:
        mock_garmin.return_value.login.side_effect = GarminConnectAuthenticationError("Invalid")
        
        with pytest.raises(GarminConnectAuthenticationError):
            authenticate_garmin("user@email.com", "wrong_pass")

def test_missing_env_vars():
    """Scenario 3: Missing config"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="Credenciales.*no encontradas"):
            get_credentials()

@patch('garminconnect.Garmin.login')
@patch('time.sleep')  # Mock sleep para tests rápidos
def test_retry_on_network_error(mock_sleep, mock_login, caplog):
    """Scenario 4: Network retry with exponential backoff"""
    mock_login.side_effect = [
        ConnectionError("Timeout"),
        ConnectionError("502 Bad Gateway"),
        None  # Success on 3rd attempt
    ]
    
    client = authenticate_garmin("user@email.com", "pass")
    
    assert mock_login.call_count == 3
    assert "Intento 1/3 falló" in caplog.text
    assert "Intento 2/3 falló" in caplog.text
    assert "✅ Autenticado correctamente" in caplog.text
    # Verify exponential backoff: 2s, 4s
    assert mock_sleep.call_args_list == [call(2), call(4)]

def test_cli_credentials_override_env():
    """Scenario 5: CLI override"""
    with patch.dict('os.environ', {'GARMIN_EMAIL': 'env@email.com', 'GARMIN_PASSWORD': 'envpass'}):
        args = MagicMock(email='cli@email.com', password='clipass')
        email, password = get_credentials(args)
        
        assert email == 'cli@email.com'
        assert password == 'clipass'

def test_2fa_not_supported_message():
    """Scenario 6: 2FA detection"""
    with patch('garminconnect.Garmin.login') as mock_login:
        mock_login.side_effect = GarminConnectAuthenticationError("MFA token required")
        
        with pytest.raises(SystemExit) as exc_info:
            authenticate_garmin("user@email.com", "pass")
        
        # Verify exit code and error message contains 2FA info
        assert exc_info.value.code == 1

def test_rate_limit_no_retry():
    """Scenario 7: Rate limit stops retries"""
    with patch('garminconnect.Garmin.login') as mock_login:
        mock_login.side_effect = GarminConnectTooManyRequestsError("429")
        
        with pytest.raises(SystemExit) as exc_info:
            authenticate_garmin("user@email.com", "pass")
        
        assert mock_login.call_count == 1  # No retries
        assert exc_info.value.code == 2

@patch('garminconnect.Garmin.get_activities')
def test_session_expired_reauth(mock_get_activities):
    """Scenario 8: Session expiry during long execution"""
    mock_get_activities.side_effect = [
        GarminConnectAuthenticationError("401 Unauthorized"),
        [{'id': 1}]  # Success after reauth
    ]
    
    client = authenticate_garmin("user@email.com", "pass")
    activities = client.get_activities_with_reauth()
    
    assert len(activities) == 1
    assert mock_get_activities.call_count == 2
```

---

## Implementation Checklist
- [ ] Crear módulo `src/auth.py` con función `authenticate_garmin(email, password)`
- [ ] Implementar retry logic con exponential backoff (2s, 4s, 8s)
- [ ] Añadir logging con sanitización de passwords
- [ ] Validar variables de entorno en startup
- [ ] Implementar detección de 2FA con mensaje específico
- [ ] Añadir manejo de rate limit (429) sin reintentos
- [ ] Implementar re-auth automático en caso de sesión expirada
- [ ] Crear tests en `tests/test_auth.py` (8 tests mínimo)
- [ ] Documentar en README.md sección "Authentication"
- [ ] Actualizar `.env.example` con comentarios explicativos
- [ ] Verificar permisos de `.env` (600) en script de setup

---

## Related Specs
- [Cache System](../03-caching/sqlite-cache.spec.md) - El cache puede reducir necesidad de re-auth frecuente
- [Data Extraction](../02-data-extraction/activities.spec.md) - Usa el cliente autenticado

---

## Changelog
- **2025-01-30**: Spec inicial creada con 8 escenarios
- **2025-01-30**: Añadido Scenario 8 (sesión expirada) para ejecuciones largas
