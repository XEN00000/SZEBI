from abc import ABC,abstractmethod

from simulation.logic.src.base.device import Device
from simulation.logic.src.base.weather import Weather


class EnergySource(Device, ABC):
    def __init__(self, name: str, weather: Weather):
        super().__init__(name, weather)
        self.available_energy = 0.0

    def get_available_energy(self) -> float:
        return self.available_energy

    def consume_energy(self, requested_watthours: float) -> float:
        if not self.is_active:
            return 0.0
        provided = min(self.available_energy, requested_watthours)
        self.available_energy -= provided
        return provided

    def publish_state(self, extra=None):
        payload = {
            "available_energy": self.available_energy,
        }

        if extra:
            payload.update(extra)

        super().publish_state(payload)
