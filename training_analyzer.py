"""
Sistema de Analisis de Entrenamiento Deportivo
Integracion: Garmin Connect + Claude AI
Autor: Sistema de Analisis Deportivo
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from src.garmin_client import GarminClient
from src.llm_analizer import LLMAnalyzer
from src.config import Config



# ========================================
# CONFIGURACIIN Y MODELOS DE DATOS
# ========================================

@dataclass
class ActivityData:
    """Modelo de datos para una actividad deportiva."""
    activity_id: str
    name: str
    activity_type: str
    date: str
    distance_km: float
    duration_minutes: float
    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    calories: Optional[int]
    avg_speed: Optional[float]
    elevation_gain: Optional[float]
    
    @classmethod
    def from_garmin_data(cls, garmin_activity: Dict) -> 'ActivityData':
        """Crea una instancia desde datos de Garmin."""
        return cls(
            activity_id=str(garmin_activity.get('activityId', '')),
            name=garmin_activity.get('activityName', 'Sin nombre'),
            activity_type=garmin_activity.get('activityType', {}).get('typeKey', 'Desconocido'),
            date=garmin_activity.get('startTimeLocal', ''),
            distance_km=garmin_activity.get('distance', 0) / 1000,
            duration_minutes=garmin_activity.get('duration', 0) / 60,
            avg_heart_rate=garmin_activity.get('averageHR'),
            max_heart_rate=garmin_activity.get('maxHR'),
            calories=garmin_activity.get('calories'),
            avg_speed=garmin_activity.get('averageSpeed'),
            elevation_gain=garmin_activity.get('elevationGain')
        )
    
    def to_readable_text(self) -> str:
        """Convierte la actividad a texto legible."""
        text = f" {self.name}\n"
        text += f"   Tipo: {self.activity_type}\n"
        text += f"   Fecha: {self.date}\n"
        text += f"   Distancia: {self.distance_km:.2f} km\n"
        text += f"   Duracion: {self.duration_minutes:.0f} min\n"
        
        if self.avg_heart_rate:
            text += f"   FC Promedio: {self.avg_heart_rate} bpm\n"
        if self.max_heart_rate:
            text += f"   FC Maxima: {self.max_heart_rate} bpm\n"
        if self.calories:
            text += f"   Calorias: {self.calories}\n"
        if self.elevation_gain:
            text += f"   Desnivel: {self.elevation_gain:.0f} m\n"
        
        return text


@dataclass
class AnalysisConfig:
    """Configuracion del analisis."""
    garmin_email: str
    garmin_password: str
    llm_provider: str = "anthropic"          #  NUEVO
    llm_model: str = "claude-sonnet-4"       #  NUEVO
    analysis_days: int = 7
    training_plan_path: Optional[str] = None
    output_dir: str = "analysis_reports"
    
    @classmethod
    def from_env(cls) -> 'AnalysisConfig':
        """Carga configuracion desde variables de entorno."""        
        # Obtener configuracion del LLM
        llm_config = Config.get_llm_config()
        
        return cls(
            garmin_email=os.getenv('GARMIN_EMAIL', ''),
            garmin_password=os.getenv('GARMIN_PASSWORD', ''),
            llm_provider=Config.LLM_PROVIDER,             
            llm_model=llm_config.get('model', 'Unknown'),  
            analysis_days=int(os.getenv('ANALYSIS_DAYS', '7')),
            training_plan_path=os.getenv('TRAINING_PLAN_PATH'),
            output_dir=os.getenv('OUTPUT_DIR', 'analysis_reports')
        )
    
    def validate(self) -> bool:
        """Valida que la configuracion este completa."""
        return bool(self.garmin_email and self.garmin_password)

# ========================================
# GESTOR DE TRAININGPEAKS
# ========================================

class TrainingPeaksManager:
    """Gestor para manejar planes de TrainingPeaks."""
    
    def __init__(self, plan_path: Optional[str] = None):
        """
        Inicializa el gestor de TrainingPeaks.
        
        Args:
            plan_path: Ruta al archivo con el plan de entrenamiento
        """
        self.plan_path = plan_path
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_training_plan(self) -> Optional[str]:
        """
        Carga el plan de entrenamiento desde archivo.
        
        Returns:
            Contenido del plan o None si no esta disponible
        """
        if not self.plan_path:
            self.logger.info("No se especifico ruta de plan de entrenamiento")
            return None
        
        plan_file = Path(self.plan_path)
        
        if not plan_file.exists():
            self.logger.warning(f"Archivo de plan no encontrado: {self.plan_path}")
            return None
        
        try:
            self.logger.info(f"Cargando plan desde {self.plan_path}...")
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = f.read()
            self.logger.info(" Plan de entrenamiento cargado")
            return plan
        except Exception as e:
            self.logger.error(f" Error cargando plan: {e}")
            return None


# ========================================
# ORQUESTADOR PRINCIPAL
# ========================================

class TrainingAnalyzer:
    """Orquestador principal del sistema de analisis."""
    
    def __init__(self, config: AnalysisConfig):
        """
        Inicializa el analizador de entrenamiento.
        
        Args:
            config: Configuracion del analisis
        """
        self.config = config
        self.llm_provider = Config.LLM_PROVIDER  #  Anade esta linea
        self.logger = self._setup_logging()
        
        
        # Inicializar componentes
        self.garmin_client = GarminClient(config.garmin_email, config.garmin_password)
        self.tp_manager = TrainingPeaksManager(config.training_plan_path)
        self.llm_analyzer = LLMAnalyzer()

        
        # Crear directorio de salida
        Path(config.output_dir).mkdir(exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging."""
        import sys
        
        # Configurar handlers con UTF-8
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(
            'training_analyzer.log',
            encoding='utf-8'  #  Esto es clave
        )
        file_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            handlers=[console_handler, file_handler]
        )
        
        return logging.getLogger(self.__class__.__name__)
    
    def run_analysis(self) -> bool:
        """
        Ejecuta el analisis completo.
        
        Returns:
            bool: True si el analisis fue exitoso
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO ANALISIS DE ENTRENAMIENTO")
        self.logger.info("=" * 60)
        
        # Validar configuracion
        if not self.config.validate():
            self.logger.error("Configuracion invalida. Verifica credenciales.")
            return False
        
        # 1. Conectar con Garmin
        if not self.garmin_client.connect():
            return False
        
        # 2. Calcular rango de fechas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config.analysis_days)
        
        # 3. Obtener actividades basicas
        raw_activities = self.garmin_client.get_activities(start_date, end_date)
        if not raw_activities:
            self.logger.warning("No se encontraron actividades")
            return False
        
        # Convertir a ActivityData
        activities = [ActivityData.from_garmin_data(act) for act in raw_activities]
        self.logger.info(f"{len(activities)} actividades obtenidas")
        
        # 4. Obtener detalles completos de cada actividad
        activities_details = []
        self.logger.info("Obteniendo detalles de actividades...")
        for activity in activities:
            details = self.garmin_client.get_activity_details(activity.activity_id)
            activities_details.append(details if details else {})
        
        # 5. Obtener perfil de usuario
        user_profile = self.garmin_client.get_user_profile()
        
        # 6. Obtener composicion corporal
        body_composition = self.garmin_client.get_body_composition(start_date, end_date)
        self.logger.info(f"{len(body_composition)} mediciones de composicion corporal obtenidas")
        
        # 7. Cargar plan de TrainingPeaks (si existe)
        training_plan = self.tp_manager.load_training_plan()
        
        # 8. Analizar con LLM
        analysis = self.llm_analyzer.analyze_training(
            activities,
            activities_details,
            user_profile,
            body_composition,
            training_plan
        )
        
        if not analysis:
            self.logger.error("No se pudo generar el analisis")
            return False
        
        # 9. Guardar resultados
        self._save_results(activities, analysis, user_profile)
        
        # 10. Mostrar resultados
        self._display_results(analysis)
        
        self.logger.info("Analisis completado exitosamente")
        return True

    def _save_results(
        self,
        activities: List[ActivityData],
        analysis: str,
        user_profile: Dict[str, Any]
    ) -> None:
        """Guarda los resultados del analisis en TXT, Markdown y JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        athlete_name = user_profile.get('name', 'Usuario')
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # ========================================
        # 1. GUARDAR EN FORMATO TEXTO (.txt)
        # ========================================
        txt_path = Path(self.config.output_dir) / f"analisis_{timestamp}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("REPORTE DE ANILISIS DE ENTRENAMIENTO\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Atleta: {athlete_name}\n")
            f.write(f"Fecha: {current_date}\n")
            f.write(f"Periodo analizado: Iltimos {self.config.analysis_days} dias\n")
            f.write(f"Actividades analizadas: {len(activities)}\n\n")
            f.write("=" * 60 + "\n")
            f.write("ANILISIS Y RECOMENDACIONES\n")
            f.write("=" * 60 + "\n\n")
            f.write(analysis)
        
        # ========================================
        # 2. GUARDAR EN FORMATO MARKDOWN (.md)
        # ========================================
        md_path = Path(self.config.output_dir) / f"analisis_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            # Header del documento
            f.write(f"#  Reporte de Analisis de Entrenamiento\n\n")
            
            # Metadata
            f.write(f"---\n\n")
            f.write(f"** Atleta:** {athlete_name}  \n")
            f.write(f"** Fecha del analisis:** {current_date}  \n")
            f.write(f"** Periodo analizado:** Iltimos {self.config.analysis_days} dias  \n")
            f.write(f"** Actividades analizadas:** {len(activities)}  \n")
            f.write(f"** Modelo usado:** {self.config.llm_provider.upper()} - {self._get_model_name()}  \n\n")
            f.write(f"---\n\n")
            
            # Resumen de actividades
            f.write(f"##  Resumen de Actividades\n\n")
            f.write(f"| # | Actividad | Tipo | Fecha | Distancia | Duracion | FC Avg |\n")
            f.write(f"|---|-----------|------|-------|-----------|----------|--------|\n")
            
            for idx, act in enumerate(activities, 1):
                f.write(
                    f"| {idx} | {act.name[:30]} | {act.activity_type} | "
                    f"{act.date[:10]} | {act.distance_km:.2f} km | "
                    f"{act.duration_minutes:.0f} min | "
                    f"{act.avg_heart_rate or '-'} bpm |\n"
                )
            
            f.write(f"\n---\n\n")
            
            # Analisis completo
            f.write(f"##  Analisis Detallado\n\n")
            f.write(analysis)
            
            # Footer
            f.write(f"\n\n---\n\n")
            f.write(f"*Generado automaticamente por el Sistema de Analisis de Entrenamiento*\n")
        
        # ========================================
        # 3. GUARDAR EN FORMATO JSON (.json)
        # ========================================
        json_path = Path(self.config.output_dir) / f"datos_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "user": athlete_name,
                "analysis_date": current_date,
                "analysis_days": self.config.analysis_days,
                "llm_provider": self.config.llm_provider,
                "model": self._get_model_name(),
                "activities": [asdict(act) for act in activities],
                "analysis": analysis
            }, f, indent=2, ensure_ascii=False)
        
        # Log de archivos generados
        self.logger.info(f" Resultados guardados:")
        self.logger.info(f"    Texto: {txt_path}")
        self.logger.info(f"    Markdown: {md_path}")
        self.logger.info(f"    JSON: {json_path}")

    def _get_model_name(self) -> str:
        """Obtiene el nombre del modelo usado."""
        llm_config = Config.get_llm_config()
        return llm_config.get('model', 'Unknown')
    
    def _display_results(self, analysis: str) -> None:
        """Muestra los resultados en pantalla."""
        print("\n" + "=" * 60)
        print(" ANILISIS Y RECOMENDACIONES")
        print("=" * 60 + "\n")
        print(analysis)
        print("\n" + "=" * 60 + "\n")


# ========================================
# PUNTO DE ENTRADA
# ========================================
def main():
    """Funcion principal del programa."""
    from dotenv import load_dotenv
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuracion desde variables de entorno
    config = AnalysisConfig.from_env()
    
    # Ejecutar analisis
    analyzer = TrainingAnalyzer(config)
    success = analyzer.run_analysis()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())