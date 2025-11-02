"""
Cliente para interactuar con Garmin Connect.
Proporciona acceso a actividades, metricas de salud y composicion corporal.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from garminconnect import Garmin


class GarminClient:
    """Cliente para interactuar con Garmin Connect API."""
    
    def __init__(self, email: str, password: str):
        """
        Inicializa el cliente de Garmin.
        
        Args:
            email: Email de la cuenta de Garmin
            password: Contrasena de la cuenta de Garmin
        """
        self.email = email
        self.password = password
        self.client: Optional[Garmin] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
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
            self.logger.error(f"Error conectando con Garmin: {e}")
            return False
    
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
        
        try:
            self.logger.info(f"Obteniendo actividades ({start_date.date()} a {end_date.date()})...")
            
            activities = self.client.get_activities_by_date(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            self.logger.info(f"{len(activities)} actividades obtenidas")
            return activities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo actividades: {e}")
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
            self.logger.error(f"Error obteniendo detalles de actividad {activity_id}: {e}")
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
            self.logger.error(f"Error obteniendo splits de actividad {activity_id}: {e}")
            return None
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Obtiene informacion del perfil del usuario.
        
        Returns:
            Diccionario con datos del perfil
        """
        if not self.client:
            return {}
        
        try:
            self.logger.info("Obteniendo perfil de usuario...")
            
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
            
            self.logger.info(f"Perfil obtenido: {profile['name']}")
            return profile
            
        except Exception as e:
            self.logger.warning(f"Error obteniendo perfil: {e}")
            return {"name": "Usuario", "unit_system": "metric"}
    
    def get_body_composition(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
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
        
        try:
            self.logger.info(f"Obteniendo composicion corporal ({start_date.date()} a {end_date.date()})...")
            
            composition = self.client.get_body_composition(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            # FIX: Garmin puede devolver dict o list
            if composition:
                # Si es un diccionario, extraer la lista de mediciones
                if isinstance(composition, dict):
                    # Buscar la clave que contiene las mediciones
                    # Comunes: 'dateWeightList', 'dailyWeightSummaries', etc
                    for key in ['dateWeightList', 'dailyWeightSummaries', 'weightList']:
                        if key in composition:
                            measurements = composition[key]
                            self.logger.info(f"{len(measurements)} mediciones obtenidas")
                            return measurements
                    
                    # Si no encontramos clave conocida, loguear estructura
                    self.logger.warning(f"Estructura desconocida. Keys: {list(composition.keys())}")
                    # Intentar devolver el dict completo como lista
                    return [composition]
                
                # Si ya es una lista, devolverla directamente
                elif isinstance(composition, list):
                    self.logger.info(f"{len(composition)} mediciones obtenidas")
                    return composition
                
                else:
                    self.logger.warning(f"Tipo inesperado: {type(composition)}")
                    return []
            else:
                self.logger.info("No hay datos de composicion corporal")
                return []
                
        except Exception as e:
            self.logger.warning(f"Error obteniendo composicion corporal: {e}")
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
            self.logger.warning(f"Error obteniendo stats para {date.date()}: {e}")
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
            self.logger.warning(f"Error obteniendo FC para {date.date()}: {e}")
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
            self.logger.warning(f"Error obteniendo Body Battery para {date.date()}: {e}")
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
            self.logger.warning(f"Error obteniendo dispositivos: {e}")
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
            gear = self.client.get_gear()
            return gear if gear else []
        except Exception as e:
            self.logger.warning(f"Error obteniendo equipamiento: {e}")
            return []