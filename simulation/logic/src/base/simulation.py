from __future__ import annotations

import random
import threading
from datetime import datetime, timedelta
from datetime import time as dt_time
import time

from paho.mqtt import client

from simulation.logic.src.base.device import Device
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.devices.energysources.energygenerator import EnergyGenerator
from simulation.logic.src.base.devices.energysources.energystorage import EnergyStorage
from simulation.logic.src.base.electricgrid import ElectricGrid
from simulation.logic.src.base.weather import Weather
from simulation.logic.src.util.utils import validate_name


# class RandomEvent:
#     def __init__(self, chance: float, interval: int):
#         self.chance = chance
#         self.interval = interval
#         self.rules = []
#
#     def tryHappen(self):
#         pass
#
#     def forceHappen(self):
#         pass

class Simulation:
    def __init__(self, name: str):
        self.set_name(name)

        self.mqtt = client.Client(f"simulation-{self.name}")
        self.mqtt.connect("mqtt", 1883)
        self.mqtt.loop_start()

        self.weathers: list[Weather] = []

        self.devices: list[Device] = []
        self.energy_storages: list[EnergyStorage] = []
        self.energy_generators: list[EnergyGenerator] = []

        self.electric_grid: ElectricGrid = ElectricGrid(self, 5000)

        self.mode = "RSG"

        self.base_millis_per_tick: int = 100
        self.simulated_millis_per_tick: int = self.base_millis_per_tick
        self.current_tick: int = 0
        self.STARTING_DATETIME: datetime = datetime.combine(
            datetime.today(),
            dt_time(hour=14, minute=0)
        )

        self.running: bool = False

    # Running logic

    def start(self) -> None:
        if self.running:
            raise RuntimeError('simulation is already running')
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.running:
            raise RuntimeError('simulation is already not running')
        self.running = False
        if hasattr(self, "_thread"):
            self._thread.join(timeout=1)

    def _run_loop(self) -> None:
        interval = self.simulated_millis_per_tick / 1000.0
        next_tick = time.perf_counter()

        time.sleep(interval)

        while self.is_running():
            start = time.perf_counter()
            self.tick()
            end = time.perf_counter()

            elapsed = end - start
            if elapsed > interval:
                raise RuntimeError(
                    f"Tick took {elapsed:.3f}s but only {interval:.3f}s are allowed"
                )

            next_tick += interval
            wait_time = next_tick - time.perf_counter()
            if wait_time > -0.5:
                time.sleep(abs(wait_time))
            else:
                raise RuntimeError(
                    f"Tick processing overran and loop is running {wait_time:.3f}s slow"
                )

    def tick(self) -> None:
        millis = self.base_millis_per_tick

        for w in self.weathers:
            w.update(millis)
        for d in self.devices:
            d.update(millis)
        for d in self.energy_storages:
            d.update(millis)
        for d in self.energy_generators:
            d.update(millis)
        self.electric_grid.update(millis)

        total_energy_produced = 0.0
        available_energy_from_storage = 0.0
        available_grid_energy = self.electric_grid.calculate_available_energy(millis)
        for eg in self.energy_generators:
            total_energy_produced += eg.calculate_available_energy(millis)
        for es in self.energy_storages:
            available_energy_from_storage += es.calculate_available_energy(millis)

        total_available_energy = (total_energy_produced if 'R' in self.mode else 0.0) \
                                 + (available_energy_from_storage if 'S' in self.mode else 0.0) \
                                 + (available_grid_energy if 'G' in self.mode else 0.0)

        total_energy_required = self.calculate_total_energy_required(millis)

        active_devices = [d for d in self.devices if d.is_active]
        while total_energy_required > total_available_energy:
            if not active_devices:
                raise RuntimeError("No active devices left to disable")
            rd = random.choice(active_devices)
            rd.disable()
            print(rd.name + " disabled due to insufficient energy. Required: " + str(total_energy_required) + " Available: " + str(total_available_energy))
            total_energy_required = self.calculate_total_energy_required(millis)

        for source_type in self.mode:
            if source_type == "R":
                if total_energy_required > 0.0:
                    if total_energy_produced >= total_energy_required:
                        total_energy_produced -= total_energy_required
                        total_energy_required = 0.0
                    else:
                        total_energy_required -= total_energy_produced
                        total_energy_produced = 0.0
            elif source_type == "S":
                if total_energy_required > 0.0:
                    for es in self.energy_storages:
                        available = es.calculate_available_energy(millis)
                        if available > total_energy_required:
                            es.discharge_battery(total_energy_required)
                            total_energy_required = 0
                            break
                        else:
                            total_energy_required -= available
                            es.discharge_battery(available)
            elif source_type == "G":
                if total_energy_required > 0.0:
                    if available_grid_energy >= total_energy_required:
                        available_grid_energy -= total_energy_required
                        total_energy_required = 0.0
                    else:
                        total_energy_required -= available_grid_energy
                        available_grid_energy = 0.0

        # charge EnergyStorage with excess eneergy

        self.current_tick += 1

    def calculate_total_energy_required(self, millis: int) -> float:
        total_energy_required = 0.0
        for d in self.devices:
            total_energy_required += d.calculate_required_energy(millis)
        return total_energy_required

    def calculate_total_energy_available(self, millis: int) -> float:
        total_energy_produced = 0.0
        available_energy_from_storage = 0.0
        available_grid_energy = self.electric_grid.calculate_available_energy(millis)
        for eg in self.energy_generators:
            total_energy_produced += eg.calculate_available_energy(millis)
        for es in self.energy_storages:
            available_energy_from_storage += es.calculate_available_energy(millis)

        return (total_energy_produced if 'R' in self.mode else 0.0) \
                                 + (available_energy_from_storage if 'S' in self.mode else 0.0) \
                                 + (available_grid_energy if 'G' in self.mode else 0.0)

    def is_running(self) -> bool:
        return self.running

    # Time simulation

    def get_current_date(self) -> datetime:
        time_passed_since_start = self.current_tick * self.base_millis_per_tick
        return self.STARTING_DATETIME + timedelta(milliseconds=time_passed_since_start)

    def get_simulation_speed(self) -> float:
        return self.simulated_millis_per_tick / self.base_millis_per_tick

    def set_simulation_speed(self, multiplier: float) -> None:
        if multiplier < 0.01 or multiplier > 100.0:
            raise ValueError(f'multiplier must be between 0.01 and 100.0, got {multiplier}')
        self.simulated_millis_per_tick = int(self.base_millis_per_tick * multiplier)

    def set_time_resolution(self, millis_per_tick: int) -> None:
        if millis_per_tick < 1 or millis_per_tick > 7 * 24 * 60 * 60 * 1000:
            raise ValueError(
                f'time resolution must be between a millisecond (1) and a week (604800000), got {millis_per_tick}')
        sim_speed = self.get_simulation_speed()
        self.base_millis_per_tick = millis_per_tick
        self.set_simulation_speed(sim_speed)

    def get_time_resolution(self) -> int:
        return self.base_millis_per_tick

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name
