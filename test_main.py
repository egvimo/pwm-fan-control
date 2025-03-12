import sys
from unittest.mock import MagicMock

import pytest

# Mock gpiozero before importing main to prevent import-time errors
mock_gpiozero = MagicMock()
sys.modules["gpiozero"] = mock_gpiozero
sys.modules["gpiozero.pins.rpigpio"] = mock_gpiozero

import main  # noqa: E402


@pytest.fixture
def mock_fan(mocker):
    """Fixture to mock the PWM fan device."""
    return mocker.patch("main._FAN")


@pytest.fixture
def mock_temperature(mocker):
    """Fixture to mock CPU temperature readings."""
    return mocker.patch("main.CPUTemperature")


@pytest.mark.parametrize(
    "temp, initial_speed, expected_adjustment",
    [
        (50, 0.5, main.SPEED_ADJUSTMENT / 100),  # Temp too high -> increase speed
        (40, 0.5, -main.SPEED_ADJUSTMENT / 100),  # Temp too low -> decrease speed
        (45, 0.5, 0),  # Temp at target -> no change
    ],
)
def test_temperature_adjustment(
    mock_fan, mock_temperature, temp, initial_speed, expected_adjustment
):
    """Test fan speed adjustment based on CPU temperature."""
    mock_temperature().temperature = temp
    mock_fan.value = initial_speed  # Set initial fan speed

    main.check_temperature()

    expected_speed = min(max(initial_speed + expected_adjustment, 0), 1)
    assert mock_fan.value == expected_speed


def test_log_current_state(mocker, mock_fan, mock_temperature):
    """Test if current state is logged correctly."""
    mock_temperature().temperature = 47.0
    mock_fan.value = 0.6

    mock_logger = mocker.patch("main.logging.info")

    main.log_current_state()

    mock_logger.assert_called_with(
        "Current temperature: %.1f°C, Fan speed: %.1f%%", 47.0, 60.0
    )


def test_safe_shutdown(mocker, mock_fan):
    """Test if the fan safely shuts down on an exception."""
    mocker.patch("main.run_pending", side_effect=Exception("Test Error"))

    with pytest.raises(Exception):  # noqa: B017
        main.start()

    mock_fan.off.assert_called_once()
