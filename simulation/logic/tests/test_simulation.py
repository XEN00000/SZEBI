import time
import pytest
from simulation.logic.base.simulation import Simulation
from simulation.logic.base.environment import Environment
from simulation.logic.base.weather import Weather


@pytest.fixture
def simulation() -> Simulation:
    sim = Simulation()
    return sim


@pytest.fixture
def simple_environment() -> Environment:
    weather = Weather()
    env = Environment(weather=weather, initial_temp=21.0)
    return env


def test_simulation_initial_state(simulation: Simulation):
    assert simulation.is_running() is False
    assert simulation.current_tick == 0
    assert simulation.get_time_resolution() == simulation.base_millis_per_tick


def test_add_environment(simulation: Simulation, simple_environment: Environment):
    simulation.add_environment(simple_environment)
    assert len(simulation.get_environments()) == 1


def test_tick_updates_environment(simulation: Simulation, simple_environment: Environment):
    simulation.add_environment(simple_environment)

    initial_temp = simple_environment.get_temperature()
    initial_brightness = simple_environment.weather.get_brightness()
    initial_sunlight = simple_environment.weather.get_sunlight()

    simulation.tick()

    # temperatura ZAWSZE się zmieni
    assert simple_environment.get_temperature() != initial_temp

    # brightness zmienia się TYLKO kiedy jest słońce
    if initial_sunlight > 0:
        assert simple_environment.weather.get_brightness() != initial_brightness
    else:
        # w nocy upewniamy się, że dalej jest 0.0 — poprawne zachowanie
        assert simple_environment.weather.get_brightness() == initial_brightness



def test_simulation_speed(simulation: Simulation):
    assert simulation.get_simulation_speed() == 1.0

    simulation.set_simulation_speed(2.0)
    assert simulation.get_simulation_speed() == 2.0

    simulation.set_simulation_speed(0.5)
    assert simulation.get_simulation_speed() == 0.5

    with pytest.raises(ValueError):
        simulation.set_simulation_speed(0.0001)

    with pytest.raises(ValueError):
        simulation.set_simulation_speed(1000.0)


def test_time_progress(simulation: Simulation, simple_environment: Environment):
    simulation.add_environment(simple_environment)

    t0 = simulation.get_current_date()
    simulation.tick()
    t1 = simulation.get_current_date()

    assert t1 > t0  # czas powinien iść do przodu


def test_start_and_stop(simulation: Simulation):
    simulation.start()
    assert simulation.is_running() is True

    time.sleep(0.1)  # pozwala wykonać kilka ticków
    simulation.stop()

    assert simulation.is_running() is False


def test_threading_does_not_crash(simulation: Simulation, simple_environment: Environment):
    simulation.add_environment(simple_environment)
    simulation.set_simulation_speed(0.1)  # szybsze ticki dla testu

    simulation.start()
    time.sleep(0.2)
    simulation.stop()

    assert simulation.current_tick > 0
