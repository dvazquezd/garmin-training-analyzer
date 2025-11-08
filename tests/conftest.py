"""
Configuración de pytest y fixtures comunes para los tests.
"""

import pytest
import os
from datetime import datetime, timedelta
from pathlib import Path


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture que establece variables de entorno de prueba."""
    env_vars = {
        'GARMIN_EMAIL': 'test@example.com',
        'GARMIN_PASSWORD': 'test_password',
        'LLM_PROVIDER': 'anthropic',
        'ANTHROPIC_API_KEY': 'test-api-key-123',
        'ANALYSIS_DAYS': '30',
        'MAX_TOKENS': '3000',
        'TEMPERATURE': '0.7',
        'OUTPUT_DIR': 'test_reports',
        'LOG_LEVEL': 'INFO'
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def sample_activity_data():
    """Fixture con datos de actividad de ejemplo."""
    return {
        'activityId': '12345678',
        'activityName': 'Morning Run',
        'activityType': {'typeKey': 'running'},
        'startTimeLocal': '2025-11-08T08:00:00',
        'distance': 5000,  # metros
        'duration': 1800,  # segundos
        'averageHR': 150,
        'maxHR': 175,
        'calories': 350,
        'averageSpeed': 2.78,  # m/s
        'elevationGain': 50
    }


@pytest.fixture
def sample_body_composition():
    """Fixture con datos de composición corporal de ejemplo."""
    return [
        {
            'calendarDate': '2025-11-01',
            'weight': 75000,  # gramos
            'bmi': 23.5,
            'bodyFat': 18.5,
            'muscleMass': 60000,  # gramos
            'boneMass': 3000,  # gramos
            'bodyWater': 58.0
        },
        {
            'calendarDate': '2025-11-08',
            'weight': 74500,  # gramos
            'bmi': 23.3,
            'bodyFat': 18.0,
            'muscleMass': 60500,  # gramos
            'boneMass': 3000,  # gramos
            'bodyWater': 58.5
        }
    ]


@pytest.fixture
def sample_user_profile():
    """Fixture con perfil de usuario de ejemplo."""
    return {
        'name': 'Test User',
        'unit_system': 'metric'
    }


@pytest.fixture
def date_range():
    """Fixture con rango de fechas para pruebas."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return start_date, end_date


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture que crea un directorio temporal para reportes."""
    output_dir = tmp_path / "test_reports"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_garmin_client(mocker):
    """Fixture que mockea el cliente de Garmin."""
    mock_client = mocker.MagicMock()
    mock_client.login.return_value = True
    mock_client.get_full_name.return_value = "Test User"
    mock_client.get_unit_system.return_value = "metric"
    return mock_client
