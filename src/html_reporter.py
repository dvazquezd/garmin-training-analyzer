"""
Generador de reportes HTML para el análisis de entrenamiento.
Crea reportes responsive con gráficos embebidos.
"""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
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
    <title>{{ athlete_name }} - Training Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Arial', sans-serif;
            background: #ffffff;
            color: #000000;
            line-height: 1.6;
            letter-spacing: 0.3px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #ffffff;
        }

        /* Header minimalista estilo Zara */
        .header {
            background: #000000;
            color: #ffffff;
            padding: 60px 40px;
            text-align: center;
            border-bottom: 1px solid #000000;
        }

        .header h1 {
            font-size: 2.2em;
            font-weight: 300;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }

        .header .subtitle {
            font-size: 0.95em;
            font-weight: 300;
            letter-spacing: 2px;
            opacity: 0.7;
            text-transform: uppercase;
        }

        /* Metadata minimalista */
        .metadata {
            background: #f5f5f5;
            padding: 30px 60px;
            border-bottom: 1px solid #e0e0e0;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .metadata-item {
            text-align: left;
        }

        .metadata-item .label {
            font-size: 0.75em;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
            font-weight: 400;
        }

        .metadata-item .value {
            font-size: 1em;
            font-weight: 400;
            color: #000000;
            letter-spacing: 0.5px;
        }

        /* Stats grid limpio */
        .stats {
            padding: 60px 40px;
            background: white;
            max-width: 1200px;
            margin: 0 auto;
        }

        .stats h2 {
            color: #000000;
            margin-bottom: 40px;
            font-size: 1.4em;
            font-weight: 300;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-align: center;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #ffffff;
            padding: 30px 20px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
            text-align: center;
        }

        .stat-card:hover {
            border-color: #000000;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .stat-card .stat-value {
            font-size: 2.2em;
            font-weight: 300;
            color: #000000;
            letter-spacing: 1px;
        }

        .stat-card .stat-label {
            font-size: 0.75em;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 10px;
            font-weight: 400;
        }

        /* Secciones de contenido */
        .content {
            padding: 60px 40px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .section {
            margin-bottom: 80px;
        }

        .section h2 {
            color: #000000;
            margin-bottom: 40px;
            font-size: 1.4em;
            font-weight: 300;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }

        /* Tabla minimalista */
        .activities-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
            font-size: 0.9em;
        }

        .activities-table th {
            background: #000000;
            color: #ffffff;
            padding: 15px 20px;
            text-align: left;
            font-weight: 400;
            font-size: 0.75em;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        .activities-table td {
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
            color: #000000;
            letter-spacing: 0.3px;
        }

        .activities-table tr:hover {
            background: #f5f5f5;
        }

        /* Gráficos limpios */
        .chart {
            margin: 40px 0;
            text-align: center;
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e0e0e0;
        }

        .chart h3 {
            font-size: 1em;
            font-weight: 300;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 25px;
            color: #000000;
        }

        .chart img {
            max-width: 100%;
            height: auto;
            border: 1px solid #e0e0e0;
        }

        /* Análisis minimalista */
        .analysis {
            background: #f5f5f5;
            padding: 50px 40px;
            border-top: 1px solid #e0e0e0;
            border-bottom: 1px solid #e0e0e0;
            line-height: 1.9;
            font-size: 1em;
            max-width: 900px;
            margin: 0 auto;
        }

        .analysis h1, .analysis h2, .analysis h3 {
            color: #000000;
            margin-top: 35px;
            margin-bottom: 20px;
            font-weight: 300;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .analysis h1 {
            font-size: 1.6em;
            border-bottom: 1px solid #000000;
            padding-bottom: 15px;
        }

        .analysis h2 {
            font-size: 1.3em;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 12px;
        }

        .analysis h3 {
            font-size: 1.1em;
        }

        .analysis p {
            margin-bottom: 20px;
            color: #333333;
            letter-spacing: 0.3px;
        }

        .analysis ul, .analysis ol {
            margin-left: 30px;
            margin-bottom: 20px;
            color: #333333;
        }

        .analysis li {
            margin-bottom: 12px;
            line-height: 1.8;
        }

        .analysis strong {
            color: #000000;
            font-weight: 500;
        }

        .analysis em {
            font-style: italic;
            color: #666666;
        }

        .analysis code {
            background: #e0e0e0;
            padding: 3px 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            letter-spacing: 0;
        }

        .analysis pre {
            background: #e0e0e0;
            padding: 20px;
            overflow-x: auto;
            margin-bottom: 20px;
            border: 1px solid #cccccc;
        }

        .analysis blockquote {
            border-left: 2px solid #000000;
            padding-left: 25px;
            margin: 25px 0;
            color: #666666;
            font-style: italic;
        }

        /* Footer minimalista */
        .footer {
            background: #000000;
            color: #ffffff;
            padding: 40px 20px;
            text-align: center;
            border-top: 1px solid #000000;
        }

        .footer p {
            font-size: 0.8em;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            opacity: 0.7;
            font-weight: 300;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .header {
                padding: 40px 20px;
            }

            .header h1 {
                font-size: 1.5em;
                letter-spacing: 2px;
            }

            .header .subtitle {
                font-size: 0.8em;
            }

            .metadata {
                padding: 20px 20px;
            }

            .stats-grid,
            .metadata-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .content {
                padding: 40px 20px;
            }

            .section h2 {
                font-size: 1.2em;
            }

            .activities-table {
                font-size: 0.85em;
            }

            .activities-table th,
            .activities-table td {
                padding: 10px 8px;
            }

            .analysis {
                padding: 30px 20px;
            }

            .stat-card {
                padding: 25px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Training Analysis Report</h1>
            <p class="subtitle">{{ athlete_name }}</p>
        </div>

        <!-- Metadata -->
        <div class="metadata">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="label">Report Date</div>
                    <div class="value">{{ report_date }}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Analysis Period</div>
                    <div class="value">Last {{ analysis_days }} days</div>
                </div>
                <div class="metadata-item">
                    <div class="label">AI Model</div>
                    <div class="value">{{ llm_provider }} - {{ llm_model }}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Total Activities</div>
                    <div class="value">{{ total_activities }}</div>
                </div>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats">
            <h2>Performance Metrics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ "%.2f"|format(total_distance) }}</div>
                    <div class="stat-label">Total Kilometers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ "%.0f"|format(total_duration / 60) }}</div>
                    <div class="stat-label">Training Hours</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ "%.0f"|format(total_calories) }}</div>
                    <div class="stat-label">Calories Burned</div>
                </div>
                {% if avg_hr > 0 %}
                <div class="stat-card">
                    <div class="stat-value">{{ "%.0f"|format(avg_hr) }}</div>
                    <div class="stat-label">Avg Heart Rate</div>
                </div>
                {% endif %}
                {% if weight_change %}
                <div class="stat-card">
                    <div class="stat-value">{{ "%.1f"|format(weight_change) }} kg</div>
                    <div class="stat-label">Weight Change</div>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Visualizations -->
        {% if charts %}
        <div class="content">
            <div class="section">
                <h2>Data Visualizations</h2>

                {% if charts.body_composition %}
                <div class="chart">
                    <h3>Body Composition Evolution</h3>
                    <img src="{{ charts.body_composition }}" alt="Body Composition">
                </div>
                {% endif %}

                {% if charts.activity_distribution %}
                <div class="chart">
                    <h3>Activity Type Distribution</h3>
                    <img src="{{ charts.activity_distribution }}" alt="Activity Distribution">
                </div>
                {% endif %}

                {% if charts.weekly_volume %}
                <div class="chart">
                    <h3>Weekly Training Volume</h3>
                    <img src="{{ charts.weekly_volume }}" alt="Weekly Volume">
                </div>
                {% endif %}

                {% if charts.heart_rate_zones %}
                <div class="chart">
                    <h3>Heart Rate Distribution</h3>
                    <img src="{{ charts.heart_rate_zones }}" alt="Heart Rate Zones">
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- Activities Table -->
        <div class="content">
            <div class="section">
                <h2>Activity Details</h2>
                <table class="activities-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Date</th>
                            <th>Distance (km)</th>
                            <th>Duration (min)</th>
                            <th>Avg HR</th>
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
                <h2>AI Analysis & Recommendations</h2>
                <div class="analysis">{{ analysis|safe }}</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Training Analysis System</p>
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
    logging.basicConfig(level=logging.INFO)
    reporter = HTMLReporter()
    print(f"HTML Reporter inicializado. Output: {reporter.output_dir}")
