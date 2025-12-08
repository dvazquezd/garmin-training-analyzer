"""
Gestor de caché para datos de Garmin usando SQLite.
Reduce llamadas a la API y mejora el rendimiento.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class CacheManager:
    """Gestor de caché local para datos de Garmin."""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """
        Inicializa el gestor de caché.

        Args:
            cache_dir: Directorio para almacenar la base de datos de caché
            ttl_hours: Tiempo de vida del caché en horas (default: 24h)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "garmin_cache.db"
        self.ttl_hours = ttl_hours
        self.logger = logging.getLogger(self.__class__.__name__)

        # Inicializar base de datos
        self._init_database()

    def _init_database(self):
        """Crea las tablas de caché si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabla para actividades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            # Tabla para composición corporal
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS body_composition_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            # Tabla para perfiles de usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            # Índices para mejorar rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activities_expires
                ON activities_cache(expires_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_body_expires
                ON body_composition_cache(expires_at)
            """)

            conn.commit()
            self.logger.debug("Base de datos de caché inicializada")

    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _generate_cache_key(self, data_type: str, **params) -> str:
        """
        Genera una clave única para el caché basada en parámetros.

        Args:
            data_type: Tipo de datos (activities, body_composition, profile)
            **params: Parámetros adicionales (start_date, end_date, etc.)

        Returns:
            Clave de caché única
        """
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{data_type}:{param_str}"

    def get_activities(self, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        Obtiene actividades del caché.

        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)

        Returns:
            Lista de actividades o None si no está en caché o expiró
        """
        cache_key = self._generate_cache_key(
            "activities",
            start_date=start_date,
            end_date=end_date
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data, expires_at FROM activities_cache
                WHERE cache_key = ?
            """, (cache_key,))

            result = cursor.fetchone()

            if result:
                data_json, expires_at = result
                expires_dt = datetime.fromisoformat(expires_at)

                if datetime.now() < expires_dt:
                    self.logger.info("Cache HIT para actividades (%s - %s)", start_date, end_date)
                    return json.loads(data_json)
                else:
                    self.logger.info("Cache EXPIRED para actividades (%s - %s)", start_date, end_date)
                    # Eliminar entrada expirada
                    cursor.execute("DELETE FROM activities_cache WHERE cache_key = ?", (cache_key,))
                    conn.commit()
            else:
                self.logger.info("Cache MISS para actividades (%s - %s)", start_date, end_date)

            return None

    def set_activities(self, start_date: str, end_date: str, activities: List[Dict]):
        """
        Guarda actividades en el caché.

        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
            activities: Lista de actividades a cachear
        """
        cache_key = self._generate_cache_key(
            "activities",
            start_date=start_date,
            end_date=end_date
        )

        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.ttl_hours)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO activities_cache
                (cache_key, data, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                cache_key,
                json.dumps(activities),
                created_at.isoformat(),
                expires_at.isoformat()
            ))
            conn.commit()

        self.logger.info("Actividades cacheadas (%s - %s), expira: %s", start_date, end_date, expires_at)

    def get_body_composition(self, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        Obtiene composición corporal del caché.

        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)

        Returns:
            Lista de mediciones o None si no está en caché o expiró
        """
        cache_key = self._generate_cache_key(
            "body_composition",
            start_date=start_date,
            end_date=end_date
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data, expires_at FROM body_composition_cache
                WHERE cache_key = ?
            """, (cache_key,))

            result = cursor.fetchone()

            if result:
                data_json, expires_at = result
                expires_dt = datetime.fromisoformat(expires_at)

                if datetime.now() < expires_dt:
                    self.logger.info("Cache HIT para composición corporal (%s - %s)", start_date, end_date)
                    return json.loads(data_json)
                else:
                    self.logger.info("Cache EXPIRED para composición corporal (%s - %s)", start_date, end_date)
                    cursor.execute("DELETE FROM body_composition_cache WHERE cache_key = ?", (cache_key,))
                    conn.commit()
            else:
                self.logger.info("Cache MISS para composición corporal (%s - %s)", start_date, end_date)

            return None

    def set_body_composition(self, start_date: str, end_date: str, composition: List[Dict]):
        """
        Guarda composición corporal en el caché.

        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
            composition: Lista de mediciones a cachear
        """
        cache_key = self._generate_cache_key(
            "body_composition",
            start_date=start_date,
            end_date=end_date
        )

        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.ttl_hours)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO body_composition_cache
                (cache_key, data, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                cache_key,
                json.dumps(composition),
                created_at.isoformat(),
                expires_at.isoformat()
            ))
            conn.commit()

        self.logger.info("Composición corporal cacheada (%s - %s), expira: %s", start_date, end_date, expires_at)

    def get_user_profile(self, user_id: str = "default") -> Optional[Dict]:
        """
        Obtiene perfil de usuario del caché.

        Args:
            user_id: Identificador del usuario

        Returns:
            Perfil de usuario o None si no está en caché o expiró
        """
        cache_key = self._generate_cache_key("profile", user_id=user_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data, expires_at FROM user_profile_cache
                WHERE cache_key = ?
            """, (cache_key,))

            result = cursor.fetchone()

            if result:
                data_json, expires_at = result
                expires_dt = datetime.fromisoformat(expires_at)

                if datetime.now() < expires_dt:
                    self.logger.info("Cache HIT para perfil de usuario")
                    return json.loads(data_json)
                else:
                    self.logger.info("Cache EXPIRED para perfil de usuario")
                    cursor.execute("DELETE FROM user_profile_cache WHERE cache_key = ?", (cache_key,))
                    conn.commit()
            else:
                self.logger.info("Cache MISS para perfil de usuario")

            return None

    def set_user_profile(self, profile: Dict, user_id: str = "default"):
        """
        Guarda perfil de usuario en el caché.

        Args:
            profile: Datos del perfil a cachear
            user_id: Identificador del usuario
        """
        cache_key = self._generate_cache_key("profile", user_id=user_id)

        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.ttl_hours * 7)  # Perfil expira más lento

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_profile_cache
                (cache_key, data, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                cache_key,
                json.dumps(profile),
                created_at.isoformat(),
                expires_at.isoformat()
            ))
            conn.commit()

        self.logger.info("Perfil de usuario cacheado, expira: %s", expires_at)

    def clear_expired(self):
        """Elimina todas las entradas expiradas del caché."""
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Limpiar actividades
            cursor.execute("DELETE FROM activities_cache WHERE expires_at < ?", (now,))
            activities_deleted = cursor.rowcount

            # Limpiar composición corporal
            cursor.execute("DELETE FROM body_composition_cache WHERE expires_at < ?", (now,))
            composition_deleted = cursor.rowcount

            # Limpiar perfiles
            cursor.execute("DELETE FROM user_profile_cache WHERE expires_at < ?", (now,))
            profiles_deleted = cursor.rowcount

            conn.commit()

        total_deleted = activities_deleted + composition_deleted + profiles_deleted
        if total_deleted > 0:
            self.logger.info("Eliminadas %s entradas expiradas del caché", total_deleted)

    def clear_all(self):
        """Limpia todo el caché."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activities_cache")
            cursor.execute("DELETE FROM body_composition_cache")
            cursor.execute("DELETE FROM user_profile_cache")
            conn.commit()

        self.logger.info("Caché completo eliminado")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Contar actividades
            cursor.execute("SELECT COUNT(*) FROM activities_cache")
            activities_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM activities_cache WHERE expires_at > ?",
                          (datetime.now().isoformat(),))
            activities_valid = cursor.fetchone()[0]

            # Contar composición corporal
            cursor.execute("SELECT COUNT(*) FROM body_composition_cache")
            composition_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM body_composition_cache WHERE expires_at > ?",
                          (datetime.now().isoformat(),))
            composition_valid = cursor.fetchone()[0]

            # Contar perfiles
            cursor.execute("SELECT COUNT(*) FROM user_profile_cache")
            profiles_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM user_profile_cache WHERE expires_at > ?",
                          (datetime.now().isoformat(),))
            profiles_valid = cursor.fetchone()[0]

        return {
            "activities": {
                "total": activities_count,
                "valid": activities_valid,
                "expired": activities_count - activities_valid
            },
            "body_composition": {
                "total": composition_count,
                "valid": composition_valid,
                "expired": composition_count - composition_valid
            },
            "user_profiles": {
                "total": profiles_count,
                "valid": profiles_valid,
                "expired": profiles_count - profiles_valid
            },
            "ttl_hours": self.ttl_hours,
            "cache_dir": str(self.cache_dir),
            "db_size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0
        }


if __name__ == "__main__":
    # Demo del caché
    logging.basicConfig(level=logging.INFO)

    cache = CacheManager(ttl_hours=1)

    print("=== Estadísticas del Caché ===")
    stats = cache.get_cache_stats()
    print(json.dumps(stats, indent=2))

    # Limpiar expirados
    cache.clear_expired()
