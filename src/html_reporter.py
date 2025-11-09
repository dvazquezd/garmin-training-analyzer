"""
Generador de reportes HTML para el análisis de entrenamiento.
Crea reportes responsive con gráficos embebidos.
"""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Template
import markdown


class HTMLReporter:
    """Genera reportes HTML con diseño responsive y gráficos embebidos."""

    def __init__(self, output_dir: str = "analysis_reports"):
        """
        Inicializa el generador de reportes HTML.

        Args:
            output_dir: Directorio donde guardar los reportes
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_report(
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

            self.logger.info(f"Reporte HTML generado: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error generando reporte HTML: {e}")
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
                self.logger.warning(f"No se pudo embeber gráfico {chart_type}: {e}")

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

    def _render_template(
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
        template_str = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Análisis de Entrenamiento - {{ athlete_name }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2E86AB 0%, #1a4d66 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .metadata {
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 2px solid #e9ecef;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .metadata-item {
            padding: 10px;
        }

        .metadata-item .label {
            font-size: 0.85em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metadata-item .value {
            font-size: 1.1em;
            font-weight: 600;
            color: #2E86AB;
            margin-top: 5px;
        }

        .stats {
            padding: 40px;
            background: white;
        }

        .stats h2 {
            color: #2E86AB;
            margin-bottom: 20px;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            transition: transform 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .stat-card .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #2E86AB;
        }

        .stat-card .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 5px;
        }

        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 40px;
        }

        .section h2 {
            color: #2E86AB;
            margin-bottom: 20px;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
            font-size: 1.8em;
        }

        .activities-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            overflow: hidden;
            border-radius: 8px;
        }

        .activities-table th {
            background: #2E86AB;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }

        .activities-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }

        .activities-table tr:hover {
            background: #f8f9fa;
        }

        .activities-table tr:nth-child(even) {
            background: #f8f9fa;
        }

        .chart {
            margin: 30px 0;
            text-align: center;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }

        .chart img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .analysis {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 8px;
            border-left: 4px solid #A23B72;
            line-height: 1.8;
            font-size: 1.05em;
        }

        .analysis h1, .analysis h2, .analysis h3 {
            color: #2E86AB;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        .analysis h1 {
            font-size: 1.8em;
            border-bottom: 2px solid #2E86AB;
            padding-bottom: 10px;
        }

        .analysis h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #2E86AB;
            padding-bottom: 8px;
        }

        .analysis h3 {
            font-size: 1.3em;
        }

        .analysis p {
            margin-bottom: 15px;
        }

        .analysis ul, .analysis ol {
            margin-left: 25px;
            margin-bottom: 15px;
        }

        .analysis li {
            margin-bottom: 8px;
        }

        .analysis strong {
            color: #A23B72;
            font-weight: 600;
        }

        .analysis em {
            font-style: italic;
            color: #6c757d;
        }

        .analysis code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .analysis pre {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 15px;
        }

        .analysis blockquote {
            border-left: 4px solid #2E86AB;
            padding-left: 20px;
            margin: 15px 0;
            color: #6c757d;
            font-style: italic;
        }

        .footer {
            background: #2E86AB;
            color: white;
            padding: 20px;
            text-align: center;
        }

        .footer p {
            opacity: 0.9;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .stats-grid,
            .metadata-grid {
                grid-template-columns: 1fr;
            }

            .content {
                padding: 20px;
            }

            .activities-table {
                font-size: 0.9em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Reporte de Análisis de Entrenamiento</h1>
            <p class="subtitle">{{ athlete_name }}</p>
        </div>

        <!-- Metadata -->
        <div class="metadata">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="label">Fecha del Reporte</div>
                    <div class="value">{{ report_date }}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Periodo Analizado</div>
                    <div class="value">Últimos {{ analysis_days }} días</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Modelo IA</div>
                    <div class="value">{{ llm_provider }} - {{ llm_model }}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Actividades</div>
                    <div class="value">{{ total_activities }}</div>
                </div>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats">
            <h2>📈 Resumen de Estadísticas</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ "%.2f"|format(total_distance) }}</div>
                    <div class="stat-label">Kilómetros Totales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ "%.0f"|format(total_duration / 60) }}</div>
                    <div class="stat-label">Horas de Entrenamiento</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ "%.0f"|format(total_calories) }}</div>
                    <div class="stat-label">Calorías Quemadas</div>
                </div>
                {% if avg_hr > 0 %}
                <div class="stat-card">
                    <div class="stat-value">{{ "%.0f"|format(avg_hr) }}</div>
                    <div class="stat-label">FC Promedio (bpm)</div>
                </div>
                {% endif %}
                {% if weight_change %}
                <div class="stat-card">
                    <div class="stat-value">{{ "%.1f"|format(weight_change) }} kg</div>
                    <div class="stat-label">Cambio de Peso</div>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Visualizations -->
        {% if charts %}
        <div class="content">
            <div class="section">
                <h2>📊 Visualizaciones</h2>

                {% if charts.body_composition %}
                <div class="chart">
                    <h3>Evolución de Composición Corporal</h3>
                    <img src="{{ charts.body_composition }}" alt="Composición Corporal">
                </div>
                {% endif %}

                {% if charts.activity_distribution %}
                <div class="chart">
                    <h3>Distribución de Tipos de Actividad</h3>
                    <img src="{{ charts.activity_distribution }}" alt="Distribución de Actividades">
                </div>
                {% endif %}

                {% if charts.weekly_volume %}
                <div class="chart">
                    <h3>Volumen Semanal</h3>
                    <img src="{{ charts.weekly_volume }}" alt="Volumen Semanal">
                </div>
                {% endif %}

                {% if charts.heart_rate_zones %}
                <div class="chart">
                    <h3>Distribución de Frecuencia Cardíaca</h3>
                    <img src="{{ charts.heart_rate_zones }}" alt="Zonas de Frecuencia Cardíaca">
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- Activities Table -->
        <div class="content">
            <div class="section">
                <h2>🏃 Detalle de Actividades</h2>
                <table class="activities-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Nombre</th>
                            <th>Tipo</th>
                            <th>Fecha</th>
                            <th>Distancia (km)</th>
                            <th>Duración (min)</th>
                            <th>FC Avg</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for activity in activities %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ activity.name[:40] }}</td>
                            <td>{{ activity.activity_type }}</td>
                            <td>{{ activity.date[:10] }}</td>
                            <td>{{ "%.2f"|format(activity.distance_km) }}</td>
                            <td>{{ "%.0f"|format(activity.duration_minutes) }}</td>
                            <td>{{ activity.avg_heart_rate or '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Analysis -->
        <div class="content">
            <div class="section">
                <h2>🤖 Análisis y Recomendaciones</h2>
                <div class="analysis">{{ analysis|safe }}</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Generado automáticamente por el Sistema de Análisis de Entrenamiento</p>
            <p>{{ report_date }}</p>
        </div>
    </div>
</body>
</html>"""

        template = Template(template_str)

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
            activities=activities,
            analysis=analysis_html,
            charts=charts
        )


if __name__ == "__main__":
    # Demo
    import logging
    logging.basicConfig(level=logging.INFO)
    reporter = HTMLReporter()
    print(f"HTML Reporter inicializado. Output: {reporter.output_dir}")
