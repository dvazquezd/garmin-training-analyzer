"""
Módulo de visualizaciones para el análisis de entrenamiento.
Genera gráficos con matplotlib para datos de Garmin.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para servidores
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter, defaultdict


class TrainingVisualizer:
    """Genera visualizaciones de datos de entrenamiento."""

    def __init__(self, output_dir: str = "analysis_reports"):
        """
        Inicializa el visualizador.

        Args:
            output_dir: Directorio donde guardar los gráficos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configurar estilo
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10

    def generate_all_charts(
        self,
        activities: List[Any],
        body_composition: List[Dict],
        timestamp: str
    ) -> Dict[str, Path]:
        """
        Genera todos los gráficos disponibles.

        Args:
            activities: Lista de actividades
            body_composition: Datos de composición corporal
            timestamp: Timestamp para nombrar archivos

        Returns:
            Diccionario con rutas de los gráficos generados
        """
        charts = {}

        try:
            # 1. Evolución de peso y grasa corporal
            if body_composition and len(body_composition) > 0:
                weight_chart = self.plot_body_composition(body_composition, timestamp)
                if weight_chart:
                    charts['body_composition'] = weight_chart
                    self.logger.info("Gráfico de composición corporal generado: %s", weight_chart)

            # 2. Distribución de tipos de actividad
            if activities:
                activity_dist = self.plot_activity_distribution(activities, timestamp)
                if activity_dist:
                    charts['activity_distribution'] = activity_dist
                    self.logger.info("Gráfico de distribución generado: %s", activity_dist)

                # 3. Volumen semanal
                volume_chart = self.plot_weekly_volume(activities, timestamp)
                if volume_chart:
                    charts['weekly_volume'] = volume_chart
                    self.logger.info("Gráfico de volumen semanal generado: %s", volume_chart)

                # 4. Zonas de frecuencia cardíaca
                hr_chart = self.plot_heart_rate_zones(activities, timestamp)
                if hr_chart:
                    charts['heart_rate_zones'] = hr_chart
                    self.logger.info("Gráfico de zonas de FC generado: %s", hr_chart)

        except Exception as e:
            self.logger.error("Error generando gráficos: %s", e)

        return charts

    def plot_body_composition(
        self,
        body_composition: List[Dict],
        timestamp: str
    ) -> Optional[Path]:
        """
        Genera gráfico de evolución de peso y % grasa.

        Args:
            body_composition: Lista de mediciones
            timestamp: Timestamp para el nombre del archivo

        Returns:
            Path al archivo generado o None
        """
        try:
            # Extraer datos
            dates = []
            weights = []
            body_fats = []

            for measure in body_composition:
                if not isinstance(measure, dict):
                    continue

                # Fecha
                date_str = measure.get('calendarDate') or measure.get('date')
                if not date_str:
                    continue

                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    continue

                # Peso
                weight = measure.get('weight')
                if weight is not None:
                    # Convertir de gramos a kg si es necesario
                    if weight > 500:
                        weight = weight / 1000
                    dates.append(date)
                    weights.append(weight)

                    # % Grasa
                    body_fat = measure.get('bodyFat')
                    body_fats.append(body_fat if body_fat is not None else None)

            if not dates:
                return None

            # Crear figura con 2 subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            # Gráfico 1: Peso
            ax1.plot(dates, weights, marker='o', linewidth=2, markersize=6, color='#2E86AB')
            ax1.set_title('Evolución del Peso', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Fecha')
            ax1.set_ylabel('Peso (kg)')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

            # Añadir anotaciones de valores inicial y final
            if len(weights) > 1:
                ax1.annotate(f'{weights[0]:.1f} kg',
                           xy=(dates[0], weights[0]),
                           xytext=(10, 10),
                           textcoords='offset points',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                ax1.annotate(f'{weights[-1]:.1f} kg',
                           xy=(dates[-1], weights[-1]),
                           xytext=(10, -20),
                           textcoords='offset points',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # Gráfico 2: % Grasa corporal
            valid_body_fats = [(d, bf) for d, bf in zip(dates, body_fats) if bf is not None]
            if valid_body_fats:
                bf_dates, bf_values = zip(*valid_body_fats)
                ax2.plot(bf_dates, bf_values, marker='o', linewidth=2, markersize=6, color='#A23B72')
                ax2.set_title('Evolución del % Grasa Corporal', fontsize=14, fontweight='bold')
                ax2.set_xlabel('Fecha')
                ax2.set_ylabel('% Grasa Corporal')
                ax2.grid(True, alpha=0.3)
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

                # Anotaciones
                if len(bf_values) > 1:
                    ax2.annotate(f'{bf_values[0]:.1f}%',
                               xy=(bf_dates[0], bf_values[0]),
                               xytext=(10, 10),
                               textcoords='offset points',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    ax2.annotate(f'{bf_values[-1]:.1f}%',
                               xy=(bf_dates[-1], bf_values[-1]),
                               xytext=(10, -20),
                               textcoords='offset points',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            else:
                ax2.text(0.5, 0.5, 'No hay datos de % grasa disponibles',
                        ha='center', va='center', transform=ax2.transAxes)

            plt.tight_layout()

            # Guardar
            output_path = self.output_dir / f"body_composition_{timestamp}.png"
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()

            return output_path

        except Exception as e:
            self.logger.error("Error generando gráfico de composición corporal: %s", e)
            plt.close()
            return None

    def plot_activity_distribution(
        self,
        activities: List[Any],
        timestamp: str
    ) -> Optional[Path]:
        """
        Genera gráfico de distribución de tipos de actividad.

        Args:
            activities: Lista de actividades
            timestamp: Timestamp para el nombre del archivo

        Returns:
            Path al archivo generado o None
        """
        try:
            # Contar tipos de actividad
            activity_types = Counter()
            for activity in activities:
                activity_type = activity.activity_type if hasattr(activity, 'activity_type') else 'Desconocido'
                activity_types[activity_type] += 1

            if not activity_types:
                return None

            # Crear gráfico de pastel
            fig, ax = plt.subplots(figsize=(10, 8))

            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51']
            labels = list(activity_types.keys())
            sizes = list(activity_types.values())

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(labels)],
                textprops={'fontsize': 11}
            )

            # Mejorar formato
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            ax.set_title('Distribución de Tipos de Actividad', fontsize=14, fontweight='bold', pad=20)

            # Guardar
            output_path = self.output_dir / f"activity_distribution_{timestamp}.png"
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()

            return output_path

        except Exception as e:
            self.logger.error("Error generando gráfico de distribución: %s", e)
            plt.close()
            return None

    def plot_weekly_volume(
        self,
        activities: List[Any],
        timestamp: str
    ) -> Optional[Path]:
        """
        Genera gráfico de volumen semanal.

        Args:
            activities: Lista de actividades
            timestamp: Timestamp para el nombre del archivo

        Returns:
            Path al archivo generado o None
        """
        try:
            # Agrupar por semana
            weekly_data = defaultdict(lambda: {'distance': 0, 'duration': 0, 'count': 0})

            for activity in activities:
                try:
                    # Parsear fecha
                    date_str = activity.date if hasattr(activity, 'date') else ''
                    date = datetime.strptime(date_str[:10], '%Y-%m-%d')

                    # Obtener número de semana
                    week = date.strftime('%Y-W%U')

                    # Acumular datos
                    distance = activity.distance_km if hasattr(activity, 'distance_km') else 0
                    duration = activity.duration_minutes if hasattr(activity, 'duration_minutes') else 0

                    weekly_data[week]['distance'] += distance
                    weekly_data[week]['duration'] += duration / 60  # Convertir a horas
                    weekly_data[week]['count'] += 1

                except:
                    continue

            if not weekly_data:
                return None

            # Ordenar por semana
            weeks = sorted(weekly_data.keys())
            distances = [weekly_data[w]['distance'] for w in weeks]
            durations = [weekly_data[w]['duration'] for w in weeks]
            counts = [weekly_data[w]['count'] for w in weeks]

            # Crear figura
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            # Gráfico 1: Distancia semanal
            x = range(len(weeks))
            ax1.bar(x, distances, color='#2E86AB', alpha=0.8)
            ax1.set_title('Volumen Semanal - Distancia', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Semana')
            ax1.set_ylabel('Distancia (km)')
            ax1.set_xticks(x)
            ax1.set_xticklabels([w.split('-W')[1] for w in weeks], rotation=45)
            ax1.grid(True, alpha=0.3, axis='y')

            # Gráfico 2: Número de actividades
            ax2.bar(x, counts, color='#F18F01', alpha=0.8)
            ax2.set_title('Número de Actividades por Semana', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Semana')
            ax2.set_ylabel('Número de Actividades')
            ax2.set_xticks(x)
            ax2.set_xticklabels([w.split('-W')[1] for w in weeks], rotation=45)
            ax2.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()

            # Guardar
            output_path = self.output_dir / f"weekly_volume_{timestamp}.png"
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()

            return output_path

        except Exception as e:
            self.logger.error("Error generando gráfico de volumen semanal: %s", e)
            plt.close()
            return None

    def plot_heart_rate_zones(
        self,
        activities: List[Any],
        timestamp: str
    ) -> Optional[Path]:
        """
        Genera gráfico de distribución de zonas de frecuencia cardíaca.

        Args:
            activities: Lista de actividades
            timestamp: Timestamp para el nombre del archivo

        Returns:
            Path al archivo generado o None
        """
        try:
            # Recopilar FCs
            heart_rates = []
            for activity in activities:
                if hasattr(activity, 'avg_heart_rate') and activity.avg_heart_rate:
                    heart_rates.append(activity.avg_heart_rate)

            if not heart_rates or len(heart_rates) < 3:
                return None

            # Crear histograma
            fig, ax = plt.subplots(figsize=(12, 6))

            ax.hist(heart_rates, bins=20, color='#C73E1D', alpha=0.7, edgecolor='black')
            ax.set_title('Distribución de Frecuencia Cardíaca Promedio', fontsize=14, fontweight='bold')
            ax.set_xlabel('Frecuencia Cardíaca (bpm)')
            ax.set_ylabel('Número de Actividades')
            ax.grid(True, alpha=0.3, axis='y')

            # Añadir línea de promedio
            avg_hr = sum(heart_rates) / len(heart_rates)
            ax.axvline(avg_hr, color='red', linestyle='--', linewidth=2,
                      label=f'Promedio: {avg_hr:.0f} bpm')
            ax.legend()

            plt.tight_layout()

            # Guardar
            output_path = self.output_dir / f"heart_rate_zones_{timestamp}.png"
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()

            return output_path

        except Exception as e:
            self.logger.error("Error generando gráfico de zonas de FC: %s", e)
            plt.close()
            return None


if __name__ == "__main__":
    # Demo
    logging.basicConfig(level=logging.INFO)
    viz = TrainingVisualizer()
    print(f"Visualizador inicializado. Output: {viz.output_dir}")
