from abc import ABC,abstractmethod
from simulation.logic.base.device import Device

class EnergySource(Device, ABC):
    def __init__(self, name: str):
        super().__init__(name)

    @abstractmethod
    def calculate_production(self, weather, millis_passed) -> float:
        pass

    def update(self, millis_passed: int, **kwargs) -> None:
        pass