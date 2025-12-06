from simulation.logic.base.devices.energysource import EnergySource

class ElectricGrid(EnergySource):
    def __init__(self, price_per_kwh: float = 0.8):
        super().__init__("electric-grid")
        self.price_per_kwh = price_per_kwh

    def calculate_production(self, weather, millis_passed: int) ->float:
        return 0.0

    def update(self, millis_passed: int, **kwargs) -> None:
        pass

    def supply(self, needed_kwh: float)->float:
        return needed_kwh