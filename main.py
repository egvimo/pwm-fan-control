import logging
import time

from gpiozero import CPUTemperature, PWMOutputDevice
from gpiozero.pins.rpigpio import RPiGPIOFactory
from schedule import every, repeat, run_pending

_FACTORY = RPiGPIOFactory()
_FAN = PWMOutputDevice(18, pin_factory=_FACTORY)

logging.basicConfig(level=logging.INFO)


def _read_temperature() -> float:
    return CPUTemperature().value * 100


def _adjust_speed(adjustment: int):
    current_speed: float = _FAN.value * 100
    target_speed = min(max(current_speed + adjustment, 0), 100)
    logging.info("Adjusting speed from %.1f to %.1f", current_speed, target_speed)
    _FAN.value = target_speed / 100


@repeat(every(30).seconds)
def check_temperature():
    temperature = _read_temperature()
    if abs(45 - temperature) > 3:
        logging.info("Temperature deviates: %.1f", temperature)
        speed_adjustment = 5 if temperature > 45 else -5
        _adjust_speed(speed_adjustment)


@repeat(every(10).minutes)
def log_current_state():
    current_speed: float = _FAN.value * 100
    temperature = _read_temperature()
    logging.info(
        "Current temperature: %.1f; current speed: %.1f", temperature, current_speed
    )


def start():
    logging.info("Starting fan controller with initial speed of 50.0")
    _FAN.on()
    _FAN.value = 0.5

    while True:
        run_pending()
        time.sleep(5)


if __name__ == "__main__":
    start()
