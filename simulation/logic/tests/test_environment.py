from simulation.logic.base.environment import Environment
from simulation.logic.base.weather import Weather

def test_environment_heating_increases_temp():
    w = Weather()
    env = Environment(w, initial_temp=20.0)

    before = env.get_temperature()
    env.apply_heating(2000)  # 2 kW
    env.update(15 * 60 * 1000)

    assert env.get_temperature() > before


def test_environment_cooling_decreases_temp():
    w = Weather()
    env = Environment(w, initial_temp=26.0)

    before = env.get_temperature()
    env.apply_cooling(3000)
    env.update(15 * 60 * 1000)

    assert env.get_temperature() < before