from abc import ABC, abstractmethod

from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather


class EnergyGenerator(EnergySource, ABC):
    def __init__(self, name: str, weather: Weather, rated_power_watt: float):
        super().__init__(name, weather)
        self.peak_power = rated_power_watt

