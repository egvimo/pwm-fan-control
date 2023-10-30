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
    currentSpeed: float = _FAN.value * 100
    targetSpeed = min(max(currentSpeed + adjustment, 0), 100)
    logging.info(f"Adjusting speed from {currentSpeed} to {targetSpeed}")
    _FAN.value = targetSpeed / 100


def start() -> None:
    logging.info(f"Starting fan controller with initial speed of 50.0")

    _FAN.on()
    _FAN.value = 0.5

    while True:
        temperature = _read_temperature()
        if abs(45 - temperature) > 3:
            logging.info(f"Temperature deviates: {temperature}")
            speedAdjustment = 1 if temperature > 45 else -1
            _adjust_speed(speedAdjustment)

        time.sleep(5)


if __name__ == "__main__":
    start()
