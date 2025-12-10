from simulation.logic.base.devices.smartdevices.heating import Heating
from simulation.logic.base.weather import Weather
from simulation.logic.base.environment import Environment

def test_heating_turns_on_and_uses_energy():
    w = Weather()
    env = Environment(w, initial_temp=15)

    heater = Heating("heater", power_usage_watt=2000, target_temp=21)
    heater.enable()

    heater.update(15 * 60 * 1000, environment=env)
    assert heater.is_heating is True