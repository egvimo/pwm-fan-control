import logging
import time
from gpiozero import PWMOutputDevice, CPUTemperature
from gpiozero.pins.rpigpio import RPiGPIOFactory

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


def start() -> None:
    logging.info("Starting fan controller with initial speed of 50.0")

    _FAN.on()
    _FAN.value = 0.5

    last_log_time = time.time()

    def log_current_state(interval=600):
        nonlocal last_log_time
        if time.time() - last_log_time >= interval:
            current_speed: float = _FAN.value * 100
            temperature = _read_temperature()
            logging.info(
                "Current temperature: %.1f; current speed: %.1f",
                temperature,
                current_speed,
            )
            last_log_time = time.time()

    while True:
        temperature = _read_temperature()
        if abs(45 - temperature) > 3:
            logging.info("Temperature deviates: %.1f", temperature)
            speed_adjustment = 5 if temperature > 45 else -5
            _adjust_speed(speed_adjustment)

        log_current_state()

        time.sleep(30)


if __name__ == "__main__":
    start()
