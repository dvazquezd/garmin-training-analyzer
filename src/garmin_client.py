"""
Cliente para interactuar con Garmin Connect.
Proporciona acceso a actividades, metricas de salud y composicion corporal.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from functools import wraps
from garminconnect import Garmin
from src.cache_manager import CacheManager


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para reintentar funciones con backoff exponencial.

    Args:
        max_retries: Número máximo de reintentos
        initial_delay: Delay inicial en segundos
        backoff_factor: Factor de multiplicación del delay
        exceptions: Tupla de excepciones a capturar

    Returns:
        Función decorada con retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        # Obtener logger si está disponible
                        if args and hasattr(args[0], 'logger'):
                            logger = args[0].logger
                            logger.warning(
                                "Error en %s (intento %d/%d): %s. Reintentando en %.1fs...",
                                func.__name__, attempt + 1, max_retries + 1, e, delay
                            )

                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        # Último intento fallido
                        if args and hasattr(args[0], 'logger'):
                            logger = args[0].logger
                            logger.error(
                                "Error en %s después de %d intentos: %s",
                                func.__name__, max_retries + 1, e
                            )

            # Si llegamos aquí, todos los intentos fallaron
            raise last_exception

        return wrapper
    return decorator


class GarminClient:
    """Cliente para interactuar con Garmin Connect API."""

    def __init__(self, email: str, password: str, use_cache: bool = True, cache_ttl_hours: int = 24):
        """
        Inicializa el cliente de Garmin.

        Args:
            email: Email de la cuenta de Garmin
            password: Contrasena de la cuenta de Garmin
            use_cache: Si True, usa caché para reducir llamadas a la API
            cache_ttl_hours: Tiempo de vida del caché en horas
        """
        self.email = email
        self.password = password
        self.client: Optional[Garmin] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.use_cache = use_cache

        # Inicializar caché si está habilitado
        if self.use_cache:
            self.cache = CacheManager(ttl_hours=cache_ttl_hours)
            self.logger.info("Caché habilitado (TTL: %sh)", cache_ttl_hours)
        else:
            self.cache = None
            self.logger.info("Caché deshabilitado")

    def connect(self) -> bool:
        """
        Establece conexion con Garmin Connect.

        Returns:
            bool: True si la conexion fue exitosa
        """
        try:
            self.logger.info("Conectando con Garmin Connect...")
            self.client = Garmin(self.email, self.password)
            self.client.login()
            self.logger.info("Conexion exitosa con Garmin")
            return True
        except Exception as e:
            self.logger.error("Error conectando con Garmin: %s", e)
            return False

    @retry_with_backoff(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def _fetch_activities_from_api(self, start_str: str, end_str: str) -> List[Dict[str, Any]]:
        """Obtiene actividades de la API de Garmin con retry."""
        return self.client.get_activities_by_date(start_str, end_str)

    def get_activities(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Obtiene actividades en un rango de fechas.

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Lista de actividades (diccionarios con datos completos)
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return []

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Intentar obtener del caché primero
        if self.use_cache and self.cache:
            cached_activities = self.cache.get_activities(start_str, end_str)
            if cached_activities is not None:
                return cached_activities

        # Si no está en caché, obtener de la API con retry
        try:
            self.logger.info("Obteniendo actividades de Garmin API (%s a %s)...", start_date.date(), end_date.date())

            activities = self._fetch_activities_from_api(start_str, end_str)

            self.logger.info("%s actividades obtenidas", len(activities))

            # Guardar en caché
            if self.use_cache and self.cache and activities:
                self.cache.set_activities(start_str, end_str, activities)

            return activities

        except Exception as e:
            self.logger.error("Error obteniendo actividades: %s", e)
            return []

    def get_activity_details(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos de una actividad especifica.

        Args:
            activity_id: ID de la actividad

        Returns:
            Diccionario con detalles de la actividad o None
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return None

        try:
            details = self.client.get_activity(activity_id)
            return details
        except Exception as e:
            self.logger.error("Error obteniendo detalles de actividad %s: %s", activity_id, e)
            return None

    def get_activity_splits(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene splits de una actividad.

        Args:
            activity_id: ID de la actividad

        Returns:
            Diccionario con splits o None
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return None

        try:
            splits = self.client.get_activity_splits(activity_id)
            return splits
        except Exception as e:
            self.logger.error("Error obteniendo splits de actividad %s: %s", activity_id, e)
            return None

    def get_user_profile(self) -> Dict[str, Any]:
        """
        Obtiene informacion del perfil del usuario.

        Returns:
            Diccionario con datos del perfil
        """
        if not self.client:
            return {}

        # Intentar obtener del caché primero
        if self.use_cache and self.cache:
            cached_profile = self.cache.get_user_profile()
            if cached_profile is not None:
                return cached_profile

        # Si no está en caché, obtener de la API
        try:
            self.logger.info("Obteniendo perfil de usuario de Garmin API...")

            profile = {
                "name": self.client.get_full_name(),
                "unit_system": self.client.get_unit_system()
            }

            # Intentar obtener settings adicionales
            try:
                settings = self.client.get_user_settings()
                if settings:
                    profile["settings"] = settings
            except:
                pass

            self.logger.info("Perfil obtenido: %s", profile['name'])

            # Guardar en caché
            if self.use_cache and self.cache and profile:
                self.cache.set_user_profile(profile)

            return profile

        except Exception as e:
            self.logger.warning("Error obteniendo perfil: %s", e)
            return {"name": "Usuario", "unit_system": "metric"}

    @retry_with_backoff(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def _fetch_body_composition_from_api(self, start_str: str, end_str: str):
        """Obtiene composición corporal de la API de Garmin con retry."""
        return self.client.get_body_composition(start_str, end_str)

    def get_body_composition(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:  # pylint: disable=too-many-branches
        """
        Obtiene datos de composicion corporal (peso, % grasa) en un rango de fechas.

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Lista de mediciones de composicion corporal
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return []

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Intentar obtener del caché primero
        if self.use_cache and self.cache:
            cached_composition = self.cache.get_body_composition(start_str, end_str)
            if cached_composition is not None:
                return cached_composition

        # Si no está en caché, obtener de la API con retry
        try:
            self.logger.info("Obteniendo composicion corporal de Garmin API (%s a %s)...", start_date.date(), end_date.date())

            composition = self._fetch_body_composition_from_api(start_str, end_str)

            # FIX: Garmin puede devolver dict o list
            measurements = []
            if composition:
                # Si es un diccionario, extraer la lista de mediciones
                if isinstance(composition, dict):
                    # Buscar la clave que contiene las mediciones
                    # Comunes: 'dateWeightList', 'dailyWeightSummaries', etc
                    for key in ['dateWeightList', 'dailyWeightSummaries', 'weightList']:
                        if key in composition:
                            measurements = composition[key]
                            self.logger.info("%s mediciones obtenidas", len(measurements))
                            break

                    if not measurements:
                        # Si no encontramos clave conocida, loguear estructura
                        self.logger.warning("Estructura desconocida. Keys: %s", list(composition.keys()))
                        # Intentar devolver el dict completo como lista
                        measurements = [composition]

                # Si ya es una lista, devolverla directamente
                elif isinstance(composition, list):
                    measurements = composition
                    self.logger.info("%s mediciones obtenidas", len(measurements))

                else:
                    self.logger.warning("Tipo inesperado: %s", type(composition))
                    measurements = []
            else:
                self.logger.info("No hay datos de composicion corporal")
                measurements = []

            # Guardar en caché
            if self.use_cache and self.cache and measurements:
                self.cache.set_body_composition(start_str, end_str, measurements)

            return measurements

        except Exception as e:
            self.logger.warning("Error obteniendo composicion corporal: %s", e)
            return []

    def get_daily_stats(self, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtiene estadisticas diarias (pasos, calorias, etc) para una fecha.

        Args:
            date: Fecha para la que obtener estadisticas

        Returns:
            Diccionario con estadisticas diarias o None
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return None

        try:
            stats = self.client.get_stats(date.strftime("%Y-%m-%d"))
            return stats
        except Exception as e:
            self.logger.warning("Error obteniendo stats para %s: %s", date.date(), e)
            return None

    def get_heart_rates(self, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de frecuencia cardiaca para una fecha.

        Args:
            date: Fecha para la que obtener datos de FC

        Returns:
            Diccionario con datos de FC o None
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return None

        try:
            hr_data = self.client.get_heart_rates(date.strftime("%Y-%m-%d"))
            return hr_data
        except Exception as e:
            self.logger.warning("Error obteniendo FC para %s: %s", date.date(), e)
            return None

    def get_body_battery(self, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de Body Battery para una fecha.

        Args:
            date: Fecha para la que obtener Body Battery

        Returns:
            Diccionario con datos de Body Battery o None
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return None

        try:
            battery = self.client.get_body_battery(date.strftime("%Y-%m-%d"))
            return battery
        except Exception as e:
            self.logger.warning("Error obteniendo Body Battery para %s: %s", date.date(), e)
            return None

    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de dispositivos conectados.

        Returns:
            Lista de dispositivos
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return []

        try:
            devices = self.client.get_devices()
            return devices if devices else []
        except Exception as e:
            self.logger.warning("Error obteniendo dispositivos: %s", e)
            return []

    def get_gear(self) -> List[Dict[str, Any]]:
        """
        Obtiene equipamiento del usuario (calzado, etc).

        Returns:
            Lista de equipamiento
        """
        if not self.client:
            self.logger.error("Cliente no conectado")
            return []

        try:
            try:
                # get_gear requiere userProfileNumber
                # Intentar obtenerlo del perfil del usuario
                profile = self.get_user_profile()
                if profile and 'id' in profile:
                    user_id = profile['id']
                    gear = self.client.get_gear(userProfileNumber=user_id)
                    return gear if gear else []
                else:
                    self.logger.debug("No se pudo obtener ID del usuario para get_gear")
                    return []
            except (TypeError, ValueError):
                # get_gear puede requerir parametros que no disponemos
                self.logger.debug("get_gear no disponible con los parametros actuales")
                return []
        except Exception as e:
            self.logger.warning("Error obteniendo equipamiento: %s", e)
            return []
