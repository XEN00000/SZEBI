from __future__ import annotations

from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.electricgrid import ElectricGrid
from simulation.logic.src.base.devices.energysources.energystorage import EnergyStorage
from simulation.logic.src.base.weather import Weather

from simulation.logic.src.util.utils import validate_name
import paho.mqtt.client as mqtt
from uuid import uuid4

import weakref


class Environment:
    weather: Weather
    name: str

    def __init__(self, name: str, simulation, weather: Weather):
        self._simulation = weakref.ref(simulation)
        self.weather = weather
        self.uuid = uuid4()
        self.name = name
        self.mqtt = mqtt.Client(f"env-{self.uuid}")
        self.mqtt.connect("localhost")
        self.mqtt.loop_start()

    def sim(self):
        s = self._simulation()
        if s is None:
            raise RuntimeError('Environment exists outside of Simulation context')
        return s

    def update(self, millis_passed: int):
        self.declared_usage = 0.0


    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name

    def available_energy(self, millis_passed: int):
        total_power = 0.0
        for device in self.devices:
            if isinstance(device, EnergySource) and device.is_active:
                total_power += device.calculate_production(self.weather, millis_passed)
        return total_power

    def available_own_energy(self, millis_passed: int):
        total_power = 0.0
        for device in self.devices:
            if isinstance(device, EnergySource) \
                    and not isinstance(device, ElectricGrid) \
                    and device.is_active:
                total_power += device.calculate_production(self.weather, millis_passed)
        return total_power

    def current_energy_produced(self, millis_passed: int):
        total_power = 0.0
        for device in self.devices:
            if isinstance(device, EnergySource) \
                    and not isinstance(device, ElectricGrid) \
                    and not isinstance(device, EnergyStorage) \
                    and device.is_active:
                total_power += device.calculate_production(self.weather, millis_passed)
        return total_power

    def available_power(self):
        return self.available_energy(3600000)  # kilowatts

    def available_own_power(self):
        return self.available_own_energy(3600000)  # kilowatts

    def current_production(self):
        return self.current_energy_produced(3600000)  # kilowatts

    def declare_usage(self, needed_kwh: float, millis_passed: int) -> bool:
        if needed_kwh < 0:
            raise ValueError("Declared usage cannot be negative")
        new_usage = self.declared_usage + needed_kwh
        if new_usage <= self.current_energy_produced(millis_passed):
            self.declared_usage = new_usage
            return True
        else:
            return False
