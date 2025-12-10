import pytest
from simulation.logic.base.devices.energysources.windturbine import WindTurbine
from simulation.logic.base.weather import Weather

def test_turbine_production():
    t = WindTurbine("turbine", rated_power_watt=3000)
    t.enable()

    w = Weather()
    w.wind = 12.0  # rated speed

    produced = t.calculate_production(w, 3600000)

    assert produced == pytest.approx(3.0, rel=0.1)