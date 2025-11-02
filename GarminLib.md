🔍 Cómo ver todos los métodos

En el repositorio de GitHub se menciona que el archivo demo.py ofrece “más de 100 métodos organizados en 11 categorías”. 
GitHub
+1

Puedes explorar directamente el código fuente (por ejemplo, clase Garmin en garminconnect/__init__.py) para ver todos los métodos disponibles.

En el ejemplo de uso se muestran métodos como get_stats(), get_heart_rates(), etc. 
PyPI
+1

📋 Principales métodos (selección)

A continuación te muestro algunos de los métodos más útiles, agrupados por categoría, con su nombre de método aproximado, descripción rápida y parámetros típicos. No es exhaustivo, pero te da buena base para tu proyecto de análisis de datos.

1. Autenticación y cliente básico

Garmin(email, password) → crea el cliente.

login() → inicia sesión y guarda token para posteriores llamadas.

logout() → borrar sesión/token (según versión).

Manejo de errores: GarminConnectConnectionError, GarminConnectAuthenticationError, GarminConnectTooManyRequestsError. 
PyPI
+1

2. Información de usuario / perfil

get_full_name() → devuelve nombre completo del usuario.

get_unit_system() → sistema de unidades configurado (metric/imperial).

get_user_profile_settings() → detalles del perfil/configuración (versión 0.2.x incluído). 
GitHub
+1

3. Salud diaria / actividad

get_stats(date) → estadísticas del día especificado (pasos, calorías, etc). Ej: fecha en formato YYYY-MM-DD.

get_steps_data(date) → datos de pasos del día.

get_heart_rates(date) → datos de frecuencia cardíaca del día (reposo, media, etc).

get_intensity_minutes_data(date) → minutos de intensidad del día. 
GitHub
+1

4. Actividades / workouts

get_activities(start, limit) → listado de actividades, con parámetros de paginación (inicio, cantidad). 
Biblos-e Repository
+1

download_activity(activityId, dl_fmt=ActivityDownloadFormat.GPX/FIT) → descarga la actividad con el id especificado en formato GPX o FIT. 
Biblos-e Repository

get_activity_typed_splits(activityId) → splits tipificados para la actividad (versión 0.2.20 según changelog) 
GitHub

set_activity_type() / create_manual_activity() → permite crear o modificar una actividad manualmente (versión reciente) 
GitHub

5. Cuerpo / composición / peso

get_body_composition(date) → composición corporal en fecha dada.

get_body_composition(startdate, enddate) → rango de fechas para composición corporal. 
PyPI

add_weigh_in_with_timestamps() → añadir registro de peso con timestamp antiguo (versión 0.2.20) 
GitHub

6. Métricas avanzadas de salud

get_body_battery(date) → “nivel de batería corporal” (versión 0.2.20) 
GitHub

get_body_battery_events(date) → eventos relacionados a battery corporal.

get_all_day_events() → eventos diarios (versión 0.2.20) 
GitHub

Incluye HRV, VO₂ max, etc (aunque los nombres exactos pueden variar).

7. Dispositivos / equipamiento / técnica

get_devices() → lista de dispositivos conectados.

get_gear() → equipamiento usado (calzado, etc).

Métodos para gestión de alarma, sincronización, etc.

8. Exportación / sistema

export_data() / get_graphql() → algunos métodos de exportación o consultas tipo GraphQL. 
GitHub

delete_blood_pressure() → método de eliminación de presión arterial (versión 0.2.20) 
GitHub

⚠️ Consideraciones importantes

Algunos endpoints pueden no estar documentados oficialmente por Garmin — esta librería se basa en “ingeniería inversa”. Por tanto la funcionalidad puede romperse si Garmin cambia internamente sus APIs.

Comprueba siempre la versión de la librería que estás usando (ej: 0.2.30 es una de las más recientes). 
data.safetycli.com

Dado que tú (David) eres ingeniero de datos y trabajas con proyectos de ETL, te conviene validar la estructura del JSON que devuelven los métodos, ya que para integración con tu pipeline (Snowflake, etc) quizá necesites mapear/normalizar campos.

Respeta los términos de uso de Garmin — aunque la librería es útil para proyectos personales, usarla en producción masiva o comercial puede tener implicaciones.