"""
Generador de reportes HTML para el análisis de entrenamiento.

Crea reportes responsive con gráficos embebidos utilizando plantillas
Jinja2 externas. Las plantillas HTML y CSS se cargan desde src/templates/
(report_template.html y report_styles.css).
"""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import markdown


class HTMLReporter:  # pylint: disable=too-few-public-methods
    """
    Genera reportes HTML con diseño responsive y gráficos embebidos.

    Las plantillas se cargan desde archivos externos en src/templates/:
    - report_template.html: Estructura HTML del reporte
    - report_styles.css: Estilos CSS del reporte
    """

    def __init__(self, output_dir: str = "analysis_reports"):
        """
        Inicializa el generador de reportes HTML.

        Configura el directorio de salida y el entorno de plantillas Jinja2.
        Las plantillas se cargan desde el directorio src/templates/.

        Args:
            output_dir: Directorio donde guardar los reportes

        Raises:
            FileNotFoundError: Si el directorio de plantillas no existe
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize Jinja2 template environment
        template_dir = Path(__file__).parent / "templates"
        if not template_dir.exists():
            raise FileNotFoundError(
                f"Templates directory not found at {template_dir}. "
                "Expected templates at src/templates/"
            )
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate_report(  # pylint: disable=too-many-positional-arguments,too-many-arguments
        self,
        activities: List[Any],
        analysis: str,
        user_profile: Dict[str, Any],
        body_composition: List[Dict],
        charts: Dict[str, Path],
        config: Dict[str, Any],
        timestamp: str
    ) -> Path:
        """
        Genera un reporte HTML completo.

        Args:
            activities: Lista de actividades
            analysis: Texto del análisis LLM
            user_profile: Perfil del usuario
            body_composition: Datos de composición corporal
            charts: Diccionario con rutas de gráficos generados
            config: Configuración del análisis
            timestamp: Timestamp del reporte

        Returns:
            Path al archivo HTML generado
        """
        try:
            # Convertir gráficos a base64 para embeber
            embedded_charts = self._embed_charts(charts)

            # Calcular estadísticas
            stats = self._calculate_stats(activities, body_composition)

            # Renderizar template
            html_content = self._render_template(
                activities,
                analysis,
                user_profile,
                stats,
                embedded_charts,
                config,
                timestamp
            )

            # Guardar archivo
            output_path = self.output_dir / f"reporte_{timestamp}.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info("Reporte HTML generado: %s", output_path)
            return output_path

        except Exception as e:
            self.logger.error("Error generando reporte HTML: %s", e)
            raise

    def _embed_charts(self, charts: Dict[str, Path]) -> Dict[str, str]:
        """
        Convierte las imágenes de gráficos a base64 para embeber en HTML.

        Args:
            charts: Diccionario con rutas de gráficos

        Returns:
            Diccionario con gráficos en formato base64
        """
        embedded = {}
        for chart_type, chart_path in charts.items():
            try:
                if chart_path.exists():
                    with open(chart_path, 'rb') as f:
                        img_data = f.read()
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                        embedded[chart_type] = f"data:image/png;base64,{base64_data}"
            except Exception as e:
                self.logger.warning("No se pudo embeber gráfico %s: %s", chart_type, e)

        return embedded

    def _calculate_stats(
        self,
        activities: List[Any],
        body_composition: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas generales del periodo.

        Args:
            activities: Lista de actividades
            body_composition: Datos de composición corporal

        Returns:
            Diccionario con estadísticas
        """
        if not activities:
            return {}

        total_distance = sum(act.distance_km for act in activities)
        total_duration = sum(act.duration_minutes for act in activities)
        total_calories = sum(act.calories or 0 for act in activities)

        # Frecuencia cardíaca
        hr_activities = [act for act in activities if act.avg_heart_rate]
        avg_hr = sum(act.avg_heart_rate for act in hr_activities) / len(hr_activities) if hr_activities else 0

        # Composición corporal
        weight_start = None
        weight_end = None
        if body_composition and len(body_composition) > 0:
            for measure in body_composition:
                weight = measure.get('weight')
                if weight and weight > 500:
                    weight = weight / 1000
                if weight:
                    if weight_start is None:
                        weight_start = weight
                    weight_end = weight

        return {
            'total_activities': len(activities),
            'total_distance': total_distance,
            'total_duration': total_duration,
            'total_calories': total_calories,
            'avg_hr': avg_hr,
            'weight_start': weight_start,
            'weight_end': weight_end,
            'weight_change': (weight_end - weight_start) if (weight_start and weight_end) else None
        }

    def _render_template(  # pylint: disable=too-many-arguments,too-many-positional-arguments,unused-argument
        self,
        activities: List[Any],
        analysis: str,
        user_profile: Dict[str, Any],
        stats: Dict[str, Any],
        charts: Dict[str, str],
        config: Dict[str, Any],
        timestamp: str
    ) -> str:
        """
        Renderiza el template HTML con los datos.

        Carga la plantilla desde el archivo externo report_template.html ubicado
        en src/templates/ y la renderiza con los datos proporcionados.

        Args:
            activities: Lista de actividades
            analysis: Análisis LLM
            user_profile: Perfil de usuario
            stats: Estadísticas calculadas
            charts: Gráficos embebidos en base64
            config: Configuración del análisis
            timestamp: Timestamp del reporte

        Returns:
            HTML renderizado
        """
        # Load template from external file
        template = self.jinja_env.get_template('report_template.html')

        # Convertir el análisis de markdown a HTML
        analysis_html = markdown.markdown(
            analysis,
            extensions=['extra', 'nl2br', 'sane_lists']
        )

        return template.render(
            athlete_name=user_profile.get('name', 'Usuario'),
            report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            analysis_days=config.get('analysis_days', 30),
            llm_provider=config.get('llm_provider', 'Unknown').upper(),
            llm_model=config.get('llm_model', 'Unknown'),
            total_activities=stats.get('total_activities', 0),
            total_distance=stats.get('total_distance', 0),
            total_duration=stats.get('total_duration', 0),
            total_calories=stats.get('total_calories', 0),
            avg_hr=stats.get('avg_hr', 0),
            weight_change=stats.get('weight_change'),
            activities=activities[-20:],
            analysis=analysis_html,
            charts=charts
        )


if __name__ == "__main__":
    # Demo
    logging.basicConfig(level=logging.INFO)
    reporter = HTMLReporter()
    print(f"HTML Reporter inicializado. Output: {reporter.output_dir}")
