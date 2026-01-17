from abc import ABC,abstractmethod

from simulation.logic.src.base.device import Device
from simulation.logic.src.base.weather import Weather


class EnergySource(Device, ABC):
    def __init__(self, name: str, weather: Weather):
        super().__init__(name, weather)

    @abstractmethod
    def calculate_available_energy(self, millis_passed: int) -> float:
        pass
    
    def update(self, millis_passed: int) -> None:
        pass
