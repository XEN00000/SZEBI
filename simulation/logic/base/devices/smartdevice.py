from abc import ABC, abstractmethod
from ..device import Device


class SmartDevice(Device, ABC):
    def __init__(self, name: str, power_usage_watt: float):
        super().__init__(name)
        self.power_usage = power_usage_watt

    @abstractmethod
    def update(self, millis_passed: int, **kwargs) -> None:
        pass

    def get_power_usage(self, millis_passed) -> float:
        if not self.is_active:
            return 0.0

        hours = millis_passed / 3600000
        return (self.power_usage * hours) / 1000.0
