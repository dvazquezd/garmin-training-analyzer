"""
Sistema de Analisis de Entrenamiento Deportivo
Integracion: Garmin Connect + Claude AI
Autor: Sistema de Analisis Deportivo
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any

from dotenv import load_dotenv

from src.garmin_client import GarminClient
from src.llm_analizer import LLMAnalyzer
from src.config import Config
from src.visualizations import TrainingVisualizer
from src.html_reporter import HTMLReporter



# ========================================
# CONFIGURACIÓN Y MODELOS DE DATOS
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
            self.logger.warning("Archivo de plan no encontrado: %s", self.plan_path)
            return None

        try:
            self.logger.info("Cargando plan desde %s...", self.plan_path)
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = f.read()
            self.logger.info(" Plan de entrenamiento cargado")
            return plan
        except IOError as e:
            self.logger.error(" Error cargando plan: %s", e)
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
        self.llm_provider = Config.LLM_PROVIDER
        self.logger = self._setup_logging()


        # Inicializar componentes con configuración de caché
        use_cache = os.getenv('USE_CACHE', 'true').lower() == 'true'
        cache_ttl_hours = int(os.getenv('CACHE_TTL_HOURS', '24'))

        self.garmin_client = GarminClient(
            config.garmin_email,
            config.garmin_password,
            use_cache=use_cache,
            cache_ttl_hours=cache_ttl_hours
        )
        self.tp_manager = TrainingPeaksManager(config.training_plan_path)
        self.llm_analyzer = LLMAnalyzer()

        # Crear directorio de salida
        Path(config.output_dir).mkdir(exist_ok=True)

        # Inicializar visualizador y reporteador HTML
        self.visualizer = TrainingVisualizer(config.output_dir)
        self.html_reporter = HTMLReporter(config.output_dir)

    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging."""
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
        self.logger.info("%d actividades obtenidas", len(activities))

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
        self.logger.info("%d mediciones de composicion corporal obtenidas", len(body_composition))

        # 7. Cargar plan de TrainingPeaks (si existe)
        training_plan = self.tp_manager.load_training_plan()

        # 8. Analizar con LLM
        analysis = self.llm_analyzer.analyze_training(
            activities,
            activities_details,
            user_profile,
            body_composition,
            training_plan,
            wellness_data=wellness_data
        )

        if not analysis:
            self.logger.error("No se pudo generar el analisis")
            return False

        # 9. Guardar resultados
        self._save_results(activities, analysis, user_profile, body_composition)

        # 10. Mostrar resultados
        self._display_results(analysis)

        self.logger.info("Analisis completado exitosamente")
        return True

    def _save_results(
        self,
        activities: List[ActivityData],
        analysis: str,
        user_profile: Dict[str, Any],
        body_composition: List[Dict] = None,
        wellness_data: Dict[str, Any] = None
    ) -> None:
        """Guarda los resultados del analisis en TXT, Markdown y JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        athlete_name = user_profile.get('name', 'Usuario')
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Generar visualizaciones
        if body_composition is None:
            body_composition = []
        if wellness_data is None:
            wellness_data = {}

        self.logger.info("Generando gráficos...")
        charts = self.visualizer.generate_all_charts(
            activities,
            body_composition,
            timestamp
        )
        if charts:
            self.logger.info("✓ %d gráfico(s) generado(s):", len(charts))
            for chart_type, chart_path in charts.items():
                self.logger.info("    %s: %s", chart_type, chart_path)

        # ========================================
        # 1. GUARDAR EN FORMATO TEXTO (.txt)
        # ========================================
        txt_path = Path(self.config.output_dir) / f"analisis_{timestamp}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("REPORTE DE ANÁLISIS DE ENTRENAMIENTO\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Atleta: {athlete_name}\n")
            f.write(f"Fecha: {current_date}\n")
            f.write(f"Periodo analizado: Últimos {self.config.analysis_days} días\n")
            f.write(f"Actividades analizadas: {len(activities)}\n\n")
            f.write("=" * 60 + "\n")
            f.write("ANÁLISIS Y RECOMENDACIONES\n")
            f.write("=" * 60 + "\n\n")
            f.write(analysis)

        # ========================================
        # 2. GUARDAR EN FORMATO MARKDOWN (.md)
        # ========================================
        md_path = Path(self.config.output_dir) / f"analisis_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            # Header del documento
            f.write(f"#  Reporte de Análisis de Entrenamiento\n\n")

            # Metadata
            f.write(f"---\n\n")
            f.write(f"** Atleta:** {athlete_name}  \n")
            f.write(f"** Fecha del análisis:** {current_date}  \n")
            f.write(f"** Periodo analizado:** Últimos {self.config.analysis_days} días  \n")
            f.write(f"** Actividades analizadas:** {len(activities)}  \n")
            model_info = f"{self.config.llm_provider.upper()} - {self._get_model_name()}"
            f.write(f"** Modelo usado:** {model_info}  \n\n")
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

        # ========================================
        # 4. GUARDAR EN FORMATO HTML (.html)
        # ========================================
        try:
            html_path = self.html_reporter.generate_report(
                activities=activities,
                analysis=analysis,
                user_profile=user_profile,
                body_composition=body_composition,
                charts=charts,
                config={
                    'analysis_days': self.config.analysis_days,
                    'llm_provider': self.config.llm_provider,
                    'llm_model': self._get_model_name()
                },
                timestamp=timestamp
            )
        except Exception as e:
            self.logger.error("Error generando reporte HTML: %s", e)
            html_path = None

        # Log de archivos generados
        self.logger.info(" Resultados guardados:")
        self.logger.info("    Texto: %s", txt_path)
        self.logger.info("    Markdown: %s", md_path)
        self.logger.info("    JSON: %s", json_path)
        if html_path:
            self.logger.info("    HTML: %s", html_path)

    def _collect_wellness_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Recopila métricas de bienestar: sueño, predisposición, estado del entrenamiento.

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Diccionario con métricas de bienestar
        """
        wellness_data = {
            'sleep': [],
            'readiness': [],
            'training_status': []
        }

        try:
            self.logger.info("Recopilando métricas de bienestar (sueño, predisposición, estado)...")

            # Iterar sobre cada día del rango
            current_date = start_date
            while current_date <= end_date:
                # Obtener sueño
                sleep_data = self.garmin_client.get_sleep_data(current_date)
                if sleep_data:
                    wellness_data['sleep'].append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'data': sleep_data
                    })

                # Obtener predisposición para entrenar
                readiness_data = self.garmin_client.get_training_readiness(current_date)
                if readiness_data:
                    wellness_data['readiness'].append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'data': readiness_data
                    })

                # Obtener estado del entrenamiento
                training_status = self.garmin_client.get_training_status(current_date)
                if training_status:
                    wellness_data['training_status'].append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'data': training_status
                    })

                current_date += timedelta(days=1)

            # Log de resultados
            self.logger.info(f"Metricas recopiladas - Sleep: {len(wellness_data['sleep'])}, "
                           f"Readiness: {len(wellness_data['readiness'])}, "
                           f"Training Status: {len(wellness_data['training_status'])}")

            return wellness_data

        except Exception as e:
            self.logger.warning(f"Error recopilando métricas de bienestar: {e}")
            return wellness_data

    def _get_model_name(self) -> str:
        """Obtiene el nombre del modelo usado."""
        llm_config = Config.get_llm_config()
        return llm_config.get('model', 'Unknown')

    def _display_results(self, analysis: str) -> None:
        """Muestra resumen de resultados (análisis completo guardado en archivos)."""
        try:
            print("\n" + "=" * 60)
            print(" ANALISIS COMPLETADO")
            print("=" * 60)
            print("\nLos resultados se han guardado en los siguientes archivos:")
            print("  • analysis_reports/analisis_[timestamp].txt")
            print("  • analysis_reports/analisis_[timestamp].md")
            print("  • analysis_reports/datos_[timestamp].json")
            print("  • analysis_reports/reporte_[timestamp].html")
            print("\nPara ver el analisis completo, abre el reporte HTML en tu navegador.")
            print("=" * 60 + "\n")
        except Exception as e:
            self.logger.error(f"Error mostrando resumen: {e}")


# ========================================
# PUNTO DE ENTRADA
# ========================================
def parse_arguments():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Sistema de Análisis de Entrenamiento Deportivo con Garmin Connect',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s
  %(prog)s --days 60
  %(prog)s --provider openai --days 90
  %(prog)s --email user@example.com --password mypass --days 30

Notas:
  - Los argumentos CLI tienen prioridad sobre las variables de entorno
  - Si no se especifican, se usan los valores de .env o los defaults
        """
    )

    # Credenciales de Garmin
    parser.add_argument(
        '--email',
        type=str,
        help='Email de Garmin Connect (default: variable GARMIN_EMAIL)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Contraseña de Garmin Connect (default: variable GARMIN_PASSWORD)'
    )

    # Configuración de LLM
    parser.add_argument(
        '--provider',
        type=str,
        choices=['anthropic', 'openai', 'google'],
        help='Proveedor de LLM a usar (default: variable LLM_PROVIDER o anthropic)'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Modelo específico a usar (default: modelo por defecto del proveedor)'
    )

    # Parámetros de análisis
    parser.add_argument(
        '--days',
        type=int,
        help='Número de días a analizar (default: variable ANALYSIS_DAYS o 30)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directorio para guardar reportes (default: variable OUTPUT_DIR o analysis_reports)'
    )
    parser.add_argument(
        '--training-plan',
        type=str,
        help='Ruta al archivo de plan de entrenamiento'
    )

    # Parámetros de LLM
    parser.add_argument(
        '--max-tokens',
        type=int,
        help='Máximo de tokens en respuesta (default: variable MAX_TOKENS o 3000)'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        help='Temperatura del modelo 0.0-1.0 (default: variable TEMPERATURE o 0.7)'
    )

    # Opciones de caché
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Deshabilitar caché de datos de Garmin'
    )
    parser.add_argument(
        '--cache-ttl',
        type=int,
        help='Tiempo de vida del caché en horas (default: 24)'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Limpiar caché antes de ejecutar'
    )

    # Opciones de debugging
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Habilitar modo debug con logs detallados'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser.parse_args()


def merge_config_with_args(args):
    """
    Combina argumentos CLI con variables de entorno.
    Los argumentos CLI tienen prioridad.
    """
    # Cargar variables de entorno
    load_dotenv()

    # Configurar nivel de log según --debug
    if args.debug:
        os.environ['LOG_LEVEL'] = 'DEBUG'

    # Sobrescribir variables de entorno con argumentos CLI si existen
    if args.email:
        os.environ['GARMIN_EMAIL'] = args.email
    if args.password:
        os.environ['GARMIN_PASSWORD'] = args.password
    if args.provider:
        os.environ['LLM_PROVIDER'] = args.provider
    if args.days:
        os.environ['ANALYSIS_DAYS'] = str(args.days)
    if args.output_dir:
        os.environ['OUTPUT_DIR'] = args.output_dir
    if args.training_plan:
        os.environ['TRAINING_PLAN_PATH'] = args.training_plan
    if args.max_tokens:
        os.environ['MAX_TOKENS'] = str(args.max_tokens)
    if args.temperature:
        os.environ['TEMPERATURE'] = str(args.temperature)

    # Sobrescribir modelo específico si se proporciona
    if args.model:
        provider = os.getenv('LLM_PROVIDER', 'anthropic').lower()
        if provider == 'anthropic':
            os.environ['ANTHROPIC_MODEL'] = args.model
        elif provider == 'openai':
            os.environ['OPENAI_MODEL'] = args.model
        elif provider == 'google':
            os.environ['GOOGLE_MODEL'] = args.model

    # Configuración de caché
    if args.no_cache:
        os.environ['USE_CACHE'] = 'false'
    if args.cache_ttl:
        os.environ['CACHE_TTL_HOURS'] = str(args.cache_ttl)


def main():
    """Función principal del programa."""
    # Parsear argumentos de línea de comandos
    args = parse_arguments()

    # Combinar con variables de entorno
    merge_config_with_args(args)

    # Si se solicita limpiar caché, hacerlo antes
    if args.clear_cache:
        from src.cache_manager import CacheManager
        cache = CacheManager()
        cache.clear_all()
        print("✓ Caché limpiado exitosamente")

    # Configuración desde variables de entorno (ya modificadas por args)
    config = AnalysisConfig.from_env()

    # Ejecutar análisis
    analyzer = TrainingAnalyzer(config)
    success = analyzer.run_analysis()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
