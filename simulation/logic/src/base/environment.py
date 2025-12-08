from weather import Weather
from simulation import Simulation
from device import Device

from util.utils import validate_name

from uuid import UUID, uuid4

import weakref


class Environment:
    weather: Weather
    devices: list[Device]
    
    uuid: UUID = uuid4()
    name: str
    
    
    def __init__(self, name: str, simulation: Simulation, initial_temp: float = 21.0, insulation: float = 0.85):
        self._simulation = weakref.ref(simulation)    
        self.weather = Weather(simulation)
        
        self.name = name
        
    def sim(self) -> Simulation:
        s = self._simulation() 
        if s is None:
            raise RuntimeError('Environment exists outside of Simulation context')
        return s

    def update(self, millis_passed: int):
        self.weather.update(millis_passed)
        for d in self.devices:
            d.update(millis_passed)
    
    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name