"""
Tests para el cliente de Garmin (src/garmin_client.py).
"""
# pylint: disable=unused-argument

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.garmin_client import GarminClient


class TestGarminClient:
    """Tests para la clase GarminClient."""

    @pytest.fixture
    def garmin_client(self):
        """Fixture que crea una instancia de GarminClient."""
        return GarminClient('test@example.com', 'test_password')

    def test_init(self, garmin_client):
        """Test que GarminClient se inicializa correctamente."""
        assert garmin_client.email == 'test@example.com'
        assert garmin_client.password == 'test_password'
        assert garmin_client.client is None

    @patch('src.garmin_client.Garmin')
    def test_connect_success(self, mock_garmin_class, garmin_client):
        """Test que connect establece conexión exitosamente."""
        mock_instance = MagicMock()
        mock_garmin_class.return_value = mock_instance

        result = garmin_client.connect()

        assert result is True
        assert garmin_client.client is not None
        mock_instance.login.assert_called_once()

    @patch('src.garmin_client.Garmin')
    def test_connect_failure(self, mock_garmin_class, garmin_client):
        """Test que connect maneja errores correctamente."""
        mock_garmin_class.side_effect = Exception("Connection failed")

        result = garmin_client.connect()

        assert result is False
        assert garmin_client.client is None

    def test_get_activities_without_connection(self, garmin_client):
        """Test que get_activities retorna lista vacía sin conexión."""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        result = garmin_client.get_activities(start_date, end_date)

        assert result == []

    @patch('src.garmin_client.Garmin')
    def test_get_activities_success(self, mock_garmin_class, garmin_client, sample_activity_data):
        """Test que get_activities retorna actividades correctamente."""
        mock_client = MagicMock()
        mock_client.get_activities_by_date.return_value = [sample_activity_data]
        garmin_client.client = mock_client

        start_date = datetime(2025, 11, 1)
        end_date = datetime(2025, 11, 8)

        result = garmin_client.get_activities(start_date, end_date)

        assert len(result) == 1
        assert result[0] == sample_activity_data
        mock_client.get_activities_by_date.assert_called_once_with(
            "2025-11-01",
            "2025-11-08"
        )

    def test_get_user_profile_without_connection(self, garmin_client):
        """Test que get_user_profile retorna dict vacío sin conexión."""
        result = garmin_client.get_user_profile()

        assert result == {}

    @patch('src.garmin_client.Garmin')
    def test_get_user_profile_success(self, mock_garmin_class, garmin_client):
        """Test que get_user_profile retorna perfil correctamente."""
        mock_client = MagicMock()
        mock_client.get_full_name.return_value = "Test User"
        mock_client.get_unit_system.return_value = "metric"
        garmin_client.client = mock_client

        result = garmin_client.get_user_profile()

        assert result['name'] == "Test User"
        assert result['unit_system'] == "metric"

    @patch('src.garmin_client.Garmin')
    def test_get_body_composition_dict_format(
            self, mock_garmin_class, garmin_client, sample_body_composition):
        """Test que get_body_composition maneja formato dict correctamente."""
        mock_client = MagicMock()
        # Simular respuesta en formato dict con lista
        mock_client.get_body_composition.return_value = {
            'dateWeightList': sample_body_composition
        }
        garmin_client.client = mock_client

        start_date = datetime(2025, 11, 1)
        end_date = datetime(2025, 11, 8)

        result = garmin_client.get_body_composition(start_date, end_date)

        assert len(result) == 2
        assert result[0]['weight'] == 75000

    @patch('src.garmin_client.Garmin')
    def test_get_body_composition_list_format(
            self, mock_garmin_class, garmin_client, sample_body_composition):
        """Test que get_body_composition maneja formato list correctamente."""
        mock_client = MagicMock()
        # Simular respuesta directamente como lista
        mock_client.get_body_composition.return_value = sample_body_composition
        garmin_client.client = mock_client

        start_date = datetime(2025, 11, 1)
        end_date = datetime(2025, 11, 8)

        result = garmin_client.get_body_composition(start_date, end_date)

        assert len(result) == 2
        assert result == sample_body_composition

    def test_get_activity_details_without_connection(self, garmin_client):
        """Test que get_activity_details retorna None sin conexión."""
        result = garmin_client.get_activity_details('12345')

        assert result is None

    @patch('src.garmin_client.Garmin')
    def test_get_activity_details_success(self, mock_garmin_class, garmin_client, sample_activity_data):
        """Test que get_activity_details retorna detalles correctamente."""
        mock_client = MagicMock()
        mock_client.get_activity.return_value = sample_activity_data
        garmin_client.client = mock_client

        result = garmin_client.get_activity_details('12345')

        assert result == sample_activity_data
        mock_client.get_activity.assert_called_once_with('12345')
