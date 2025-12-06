from simulation.logic.base.devices.energysource import EnergySource

class EnergyStorage(EnergySource):
    def __init__(self, name, capacity_kwh: float, max_charge_kw: float, max_discharge_kw: float):
        super().__init__(name)
        self.capacity = capacity_kwh
        self.charge = 0.0
        self.max_charge = max_charge_kw
        self.max_discharge = max_discharge_kw

    def charge_battery(self, energy_kwh):
        accepted = min(self.capacity - self.charge, self.max_charge, energy_kwh)
        self.charge += accepted
        return accepted

    def discharge_battery(self, needed_kwh):
        provided = min(self.charge, self.max_discharge, needed_kwh)
        self.charge -= provided
        return provided

    def calculate_production(self, weather, millis_passed: int) -> float:
        return 0.0