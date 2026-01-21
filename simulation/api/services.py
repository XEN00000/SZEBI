from simulation.logic.src.base.simulation import Simulation
from simulation.logic.src.base.weatherTypes.insideWeather import InsideWeather
from simulation.logic.src.base.weatherTypes.outsideWeather import OutsideWeather
from simulation.logic.src.base.devices.smartdevices.lighting import Lighting
from simulation.logic.src.base.devices.smartdevices.airconditioning import AirConditioning
from simulation.logic.src.base.devices.energysources.photovoltaic import PhotoVoltaic
from simulation.logic.src.base.devices.energysources.energystorage import EnergyStorage
from simulation.logic.src.base.devices.smartdevices.heating import Heating
from simulation.logic.src.base.devices.energysources.windturbine import WindTurbine
from simulation.logic.src.base.electricgrid import ElectricGrid

from .models import SimulationConfig
from ..logic.src.base.electricgrid import ElectricGrid

_simulation_runtime = {}

def _build_weather_map(sim_cfg, sim):
    weather_map = {}
    for wcfg in sim_cfg.weathers.filter(type="outside"):
        w = OutsideWeather(wcfg.name, sim)
        sim.weathers.append(w)
        weather_map[str(wcfg.id)] = w
    for wcfg in sim_cfg.weathers.filter(type="inside"):
        print('found inside weather')
        ref = weather_map.get(str(wcfg.outside_ref.id))
        if not ref:
            print('outside weather not found')
            continue
        w = InsideWeather(wcfg.name, sim, ref)
        sim.weathers.append(w)
        weather_map[str(wcfg.id)] = w
    return weather_map

def load_simulation(sim_cfg: SimulationConfig) -> Simulation:
    if sim_cfg.id in _simulation_runtime:
        return _simulation_runtime[sim_cfg.id]

    sim = Simulation(sim_cfg.name)
    weather_map = _build_weather_map(sim_cfg, sim)
    sim.base_millis_per_tick = sim_cfg.base_millis_per_tick
    sim.simulated_millis_per_tick = sim_cfg.simulated_millis_per_tick
    for dcfg in sim_cfg.devices.all():
        print(dcfg.name, dcfg.type)
        weather = weather_map.get(str(dcfg.weather_ref.id))
        if not weather:
            print("weather not found")
            continue
        if dcfg.type == "lighting":
            print("lighting")
            dev = Lighting(dcfg.name, weather, dcfg.extra.get("power", 15), dcfg.extra.get("light_output", 1))
            sim.devices.append(dev)
        elif dcfg.type == "airconditioning":
            print("airconditioning")
            dev = AirConditioning(dcfg.name, weather, dcfg.extra.get("power", 3000), dcfg.extra.get("cooling_power", 100))
            sim.devices.append(dev)
        elif dcfg.type == "photovoltaic":
            print("photovoltaic")
            dev = PhotoVoltaic(dcfg.name, weather, dcfg.extra.get("peak_power", 8000))
            sim.energy_generators.append(dev)
        elif dcfg.type == "energystorage":
            dev = EnergyStorage(
                dcfg.name,
                weather,
                dcfg.extra.get("capacity", 150000),
                dcfg.extra.get("max_charge", 8000),
                dcfg.extra.get("max_discharge", 5000),
            )
            sim.energy_storages.append(dev)
        elif dcfg.type == "heating":
            dev = Heating(
                dcfg.name,
                weather,
                dcfg.extra.get("power", 1500),
                dcfg.extra.get("standby", 150)
            )
            sim.devices.append(dev)
        elif dcfg.type == "windturbine":
            dev = WindTurbine(
                dcfg.name,
                weather,
                dcfg.extra.get("rated_power", 3000)
            )
            sim.energy_generators.append(dev)
        elif dcfg.type == "electricgrid":
            dev = ElectricGrid(
                weather,
                dcfg.extra.get("connection_power", 4000),
            )
            sim.electric_grid = dev
    print(len(sim.devices))
    print(weather_map)
    _simulation_runtime[sim_cfg.id] = sim
    return sim

def start_simulation(sim_cfg: SimulationConfig):
    sim = load_simulation(sim_cfg)
    if not sim.is_running():
        sim.start()
    return sim

def stop_simulation(sim_cfg: SimulationConfig):
    sim = _simulation_runtime.get(sim_cfg.id)
    if sim and sim.is_running():
        sim.stop()