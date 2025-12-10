from simulation.logic.base.devices.smartdevices.airconditioning import AirConditioning
from simulation.logic.base.weather import Weather
from simulation.logic.base.environment import Environment

def test_airco_turns_on_when_hot():
    w = Weather()
    env = Environment(w, initial_temp=30)

    ac = AirConditioning("ac1", 1000, target_temp=24)
    ac.enable()

    ac.update(60_000, environment=env)

    assert ac.is_cooling is True