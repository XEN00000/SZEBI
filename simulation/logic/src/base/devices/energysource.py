from abc import ABC,abstractmethod
from base.weather import Weather
from base.device import Device
from base.environment import Environment

class EnergySource(Device, ABC):
    def __init__(self, name: str, env: Environment):
        super().__init__(name, env)

    @abstractmethod
    def calculate_production(self, weather: Weather, millis_passed: int) -> float:
        pass