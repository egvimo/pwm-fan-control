import logging
import time

from gpiozero import CPUTemperature, PWMOutputDevice
from gpiozero.pins.rpigpio import RPiGPIOFactory
from schedule import every, repeat, run_pending

# Constants
TEMPERATURE_TARGET = 45.0
TEMPERATURE_TOLERANCE = 3.0
SPEED_ADJUSTMENT = 5.0
INITIAL_FAN_SPEED = 50.0  # Percentage

# GPIO setup
_FACTORY = RPiGPIOFactory()
_FAN = PWMOutputDevice(18, pin_factory=_FACTORY)

# Logging setup
logging.basicConfig(level=logging.INFO)


def _read_temperature() -> float:
    """Read CPU temperature in Celsius."""
    return CPUTemperature().value * 100


def _adjust_speed(adjustment: float):
    """Adjust fan speed within valid range (0-100%)."""
    current_speed = _FAN.value * 100
    target_speed = min(max(current_speed + adjustment, 0), 100)

    if current_speed != target_speed:
        logging.info(
            "Adjusting speed from %.1f%% to %.1f%%", current_speed, target_speed
        )
        _FAN.value = target_speed / 100


@repeat(every(30).seconds)
def check_temperature():
    """Check CPU temperature and adjust fan speed accordingly."""
    temperature = _read_temperature()

    if temperature > TEMPERATURE_TARGET + TEMPERATURE_TOLERANCE:
        logging.info("Temperature high (%.1f°C), increasing fan speed", temperature)
        _adjust_speed(SPEED_ADJUSTMENT)
    elif temperature < TEMPERATURE_TARGET - TEMPERATURE_TOLERANCE:
        logging.info("Temperature low (%.1f°C), decreasing fan speed", temperature)
        _adjust_speed(-SPEED_ADJUSTMENT)


@repeat(every(10).minutes)
def log_current_state():
    """Log current CPU temperature and fan speed."""
    current_speed = _FAN.value * 100
    temperature = _read_temperature()
    logging.info(
        "Current temperature: %.1f°C, Fan speed: %.1f%%", temperature, current_speed
    )


def start():
    """Start the fan controller with an initial speed."""
    logging.info(
        "Starting fan controller with initial speed of %.1f%%", INITIAL_FAN_SPEED
    )
    _FAN.on()
    _FAN.value = INITIAL_FAN_SPEED / 100

    while True:
        run_pending()
        time.sleep(5)


if __name__ == "__main__":
    start()
