"""
Analizador de entrenamiento usando LangChain (multi-LLM).
Versión refactorizada que usa PromptManager para gestionar prompts externos.
"""

import logging
import traceback
from typing import List, Dict, Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import Config
from src.prompt_manager import PromptManager


class LLMAnalyzer:
    """Analizador de entrenamiento usando LangChain con soporte multi-LLM."""

    # ========================================
    # INICIALIZACIÓN
    # ========================================

    def __init__(self):
        """Inicializa el analizador con el LLM configurado."""
        self.logger = logging.getLogger(self.__class__.__name__)

        # Validar que los prompts existan
        self._validate_prompts()

        # Inicializar componentes
        self.llm = self._initialize_llm()
        self.prompt_template = self._create_prompt_template()
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    # ========================================
    # MÉTODOS ESTÁTICOS: ACCESO A PROMPTS
    # ========================================

    @staticmethod
    def get_system_prompt() -> str:
        """
        Obtiene el system prompt desde PromptManager.

        Returns:
            str: System prompt con las instrucciones base del sistema
        """
        return PromptManager.get_system_prompt()

    @staticmethod
    def get_user_prompt_template() -> str:
        """
        Obtiene el template del user prompt desde PromptManager.

        Returns:
            str: Template con placeholders para datos del usuario
        """
        return PromptManager.get_user_prompt_template()

    @staticmethod
    def reload_prompts() -> None:
        """
        Recarga los prompts desde los archivos.
        Útil después de modificar los archivos de prompts.
        """
        PromptManager.reload_prompts()

    # ========================================
    # MÉTODOS PRIVADOS: VALIDACIÓN
    # ========================================

    def _validate_prompts(self) -> None:
        """
        Valida que los prompts estén correctamente configurados.

        Raises:
            RuntimeError: Si los prompts no son válidos
        """
        is_valid, errors = PromptManager.validate_prompts()

        if not is_valid:
            error_msg = "Configuración de prompts inválida:\n" + "\n".join(f"  - {e}" for e in errors)
            self.logger.error("❌ %s", error_msg)
            raise RuntimeError(error_msg)

        self.logger.debug("✅ Prompts validados correctamente")

    # ========================================
    # MÉTODOS PRIVADOS: INICIALIZACIÓN LLM
    # ========================================

    def _initialize_llm(self):
        """
        Inicializa el LLM según la configuración.

        Returns:
            Instancia del LLM configurado

        Raises:
            ValueError: Si el proveedor no está soportado
        """
        llm_config = Config.get_llm_config()
        provider = llm_config['provider']

        self.logger.info("Inicializando LLM: %s (%s)", provider, llm_config['model'])

        if provider == 'anthropic':
            return ChatAnthropic(
                model=llm_config['model'],
                anthropic_api_key=llm_config['api_key'],
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )

        elif provider == 'openai':
            return ChatOpenAI(
                model=llm_config['model'],
                openai_api_key=llm_config['api_key'],
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )

        elif provider == 'google':
            return ChatGoogleGenerativeAI(
                model=llm_config['model'],
                google_api_key=llm_config['api_key'],
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )

        else:
            raise ValueError(f"Proveedor LLM no soportado: {provider}")

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """
        Crea el template del prompt usando PromptManager.

        Returns:
            ChatPromptTemplate: Template configurado para LangChain
        """
        # Usar el system prompt como base y crear template simple
        system_prompt = PromptManager.get_system_prompt()

        # Template simple que concatena system prompt + datos
        template = system_prompt + "\n\n{data}"

        return ChatPromptTemplate.from_template(template)

    # ========================================
    # MÉTODOS PÚBLICOS: ANÁLISIS
    # ========================================

    def analyze_training(
        self,
        activities: List[Any],
        activities_details: List[Dict],
        user_profile: Dict[str, Any],
        body_composition: List[Dict],
        training_plan: Optional[str] = None
    ) -> Optional[str]:
        """
        Analiza el entrenamiento usando LangChain.

        Args:
            activities: Lista de actividades basicas
            activities_details: Lista de detalles completos de cada actividad
            user_profile: Perfil del usuario
            body_composition: Datos de peso y % grasa
            training_plan: Plan de entrenamiento estructurado (opcional)

        Returns:
            str: Analisis generado por el LLM
            None: Si ocurre un error o no hay actividades
        """
        if not activities:
            self.logger.warning("No hay actividades para analizar")
            return "No se encontraron actividades en el periodo seleccionado."

        try:
            self.logger.info("Enviando datos a %s para analisis...", Config.LLM_PROVIDER.upper())

            # Formatear todos los datos
            data_text = self._format_all_data(
                activities,
                activities_details,
                user_profile,
                body_composition,
                training_plan
            )

            # Invocar la cadena con datos completos
            analysis = self.chain.invoke({"data": data_text})

            self.logger.info("Analisis completado")
            return analysis

        except Exception as e:
            self.logger.error("Error al analizar: %s", e)
            self.logger.error(traceback.format_exc())
            return None

    # ========================================
    # METODOS PRIVADOS: FORMATEO
    # ========================================

    def _format_all_data(
        self,
        activities: List[Any],
        activities_details: List[Dict],
        user_profile: Dict[str, Any],
        body_composition: List[Dict],
        training_plan: Optional[str]
    ) -> str:
        """
        Formatea todos los datos para el prompt.

        Args:
            activities: Lista de actividades basicas
            activities_details: Detalles completos de actividades
            user_profile: Perfil del usuario
            body_composition: Datos de composicion corporal
            training_plan: Plan de entrenamiento

        Returns:
            str: Texto completo formateado
        """
        text = f"ATLETA: {user_profile.get('name', 'Usuario')}\n\n"

        # Actividades con detalles
        text += f"ACTIVIDADES ({len(activities)} entrenamientos):\n\n"
        for idx, (activity, details) in enumerate(zip(activities, activities_details), 1):
            text += f"Actividad {idx}:\n"
            text += f"  Nombre: {activity.name}\n"
            text += f"  Tipo: {activity.activity_type}\n"
            text += f"  Fecha: {activity.date}\n"
            text += f"  Distancia: {activity.distance_km:.2f} km\n"
            text += f"  Duracion: {activity.duration_minutes:.0f} min\n"

            if activity.avg_heart_rate:
                text += f"  FC Promedio: {activity.avg_heart_rate} bpm\n"
            if activity.max_heart_rate:
                text += f"  FC Maxima: {activity.max_heart_rate} bpm\n"
            if activity.calories:
                text += f"  Calorias: {activity.calories}\n"
            if activity.avg_speed:
                text += f"  Velocidad media: {activity.avg_speed:.2f} m/s\n"
            if activity.elevation_gain:
                text += f"  Desnivel: {activity.elevation_gain:.0f} m\n"

            # Detalles adicionales si existen
            if details:
                if 'averagePower' in details:
                    text += f"  Potencia media: {details['averagePower']} W\n"
                if 'trainingEffect' in details:
                    text += f"  Training Effect: {details['trainingEffect']}\n"
                if 'lactateThresholdHeartRate' in details:
                    text += f"  FC Umbral: {details['lactateThresholdHeartRate']} bpm\n"

            text += "\n"

        # Composicion corporal
        if body_composition and len(body_composition) > 0:
            text += "\nCOMPOSICION CORPORAL:\n\n"

            for idx, measure in enumerate(body_composition, 1):
                # Validar que measure es un diccionario
                if not isinstance(measure, dict):
                    continue

                text += f"Medicion {idx}:\n"

                # Fecha (campo principal de Garmin)
                date = measure.get('calendarDate', measure.get('date', 'N/A'))
                text += f"  Fecha: {date}\n"

                # Peso (convertir de gramos a kg si es necesario)
                weight = measure.get('weight')
                if weight is not None:
                    # Si el peso es > 500, probablemente está en gramos
                    if weight > 500:
                        weight_kg = weight / 1000
                        text += f"  Peso: {weight_kg:.1f} kg\n"
                    else:
                        text += f"  Peso: {weight:.1f} kg\n"

                # IMC
                bmi = measure.get('bmi')
                if bmi is not None:
                    text += f"  IMC: {bmi:.1f}\n"

                # % Grasa corporal
                body_fat = measure.get('bodyFat')
                if body_fat is not None:
                    text += f"  % Grasa: {body_fat:.1f}%\n"

                # % Agua corporal
                body_water = measure.get('bodyWater')
                if body_water is not None:
                    text += f"  % Agua: {body_water:.1f}%\n"

                # Masa muscular (convertir de gramos a kg si es necesario)
                muscle = measure.get('muscleMass')
                if muscle is not None:
                    if muscle > 500:
                        muscle_kg = muscle / 1000
                        text += f"  Masa muscular: {muscle_kg:.1f} kg\n"
                    else:
                        text += f"  Masa muscular: {muscle:.1f} kg\n"

                # Masa ósea (convertir de gramos a kg si es necesario)
                bone = measure.get('boneMass')
                if bone is not None:
                    if bone > 100:
                        bone_kg = bone / 1000
                        text += f"  Masa osea: {bone_kg:.1f} kg\n"
                    else:
                        text += f"  Masa osea: {bone:.1f} kg\n"

                # Grasa visceral
                visceral_fat = measure.get('visceralFat')
                if visceral_fat is not None:
                    text += f"  Grasa visceral: {visceral_fat}\n"

                # Edad metabólica
                metabolic_age = measure.get('metabolicAge')
                if metabolic_age is not None:
                    text += f"  Edad metabolica: {metabolic_age} anos\n"

                text += "\n"
        else:
            text += "\nCOMPOSICION CORPORAL:\n"
            text += "  No hay datos disponibles en este periodo\n\n"

        # Plan de entrenamiento
        if training_plan:
            text += f"\nPLAN DE ENTRENAMIENTO:\n{training_plan}\n"

        return text


# ========================================
# FUNCIÓN DE UTILIDAD
# ========================================

def verify_analyzer_setup() -> None:
    """
    Verifica la configuración del analizador.
    Útil para debugging y setup inicial.
    """
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DEL ANALIZADOR")
    print("=" * 60)

    # Verificar prompts
    print("\n1. Verificando prompts...")
    is_valid, errors = PromptManager.validate_prompts()

    if is_valid:
        print("   ✅ Prompts válidos")
        info = PromptManager.get_prompts_info()
        print(f"   📄 System prompt: {info['system_prompt']['length']} caracteres")
        print(f"   📝 User template: {info['user_template']['length']} caracteres")
    else:
        print("   ❌ Errores en prompts:")
        for error in errors:
            print(f"      - {error}")
        return

    # Verificar configuración LLM
    print("\n2. Verificando configuración LLM...")
    llm_config = Config.get_llm_config()
    print(f"   Proveedor: {llm_config['provider']}")
    print(f"   Modelo: {llm_config['model']}")
    print(f"   API Key configurada: {'✅' if llm_config.get('api_key') else '❌'}")

    # Verificar que se puede crear el analizador
    print("\n3. Intentando crear instancia del analizador...")
    try:
        # No crear instancia real para no usar la API key
        print("   ⚠️  Validación de instancia omitida (requiere API key válida)")
        print("   ℹ️  Para probar completamente, ejecuta el script principal")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Ejecutar verificación
    verify_analyzer_setup()