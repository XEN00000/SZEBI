from __future__ import annotations

import json
import random
import threading
from datetime import datetime, timedelta
from datetime import time as dt_time
import time

from paho.mqtt import client


from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.devices.energysources.energygenerator import EnergyGenerator
from simulation.logic.src.base.devices.energysources.energystorage import EnergyStorage
from simulation.logic.src.base.devices.smartdevice import SmartDevice
from simulation.logic.src.base.electricgrid import ElectricGrid
from simulation.logic.src.base.weather import Weather
from simulation.logic.src.util.utils import validate_name



class Simulation:
    def __init__(self, name: str):
        self.set_name(name)

        self.mqtt = client.Client(f"simulation-{self.name}")
        # self.mqtt.on_message = self.on_mqtt_message
        self.mqtt.connect("mqtt", 1883)
        # self.mqtt.subscribe(f"szebi/{self.name}/#")
        self.mqtt.loop_start()

        self.weathers: list[Weather] = []

        self.devices: list[SmartDevice] = []
        self.energy_storages: list[EnergyStorage] = []
        self.energy_generators: list[EnergyGenerator] = []
        self.electric_grid: ElectricGrid = None

        #       self.consumption: can be configured by MQTT. Is a string containing energy source types in order where:
        #           - "R" stands for "renewables" and represents our own energy generators
        #           - "S" stands for "storage"
        #           - "G" stands for "grid" and represents paid grid power
        #       This sets priority for where should energy to power devices be taken from first.
        #       Examples:
        #           a) self.mode = "RSG":
        #               - will first take energy from generators, then from batteries and then from the grid
        #               - if generators satisfy demand, batteries won't be depleted and no energy will be
        #               taken from the grid
        #               - consequently, if generators don't satisfy demand, energy will be taken out from batteries,
        #               but if they satisfy demand, no energy will be bought from the grid
        #           b) self.mode = "GRS":
        #               - will first take energy from the grid. This may be useful when we want to use inexpensive
        #               grid energy when tarrif is low and use energy from generators to charge up baterries
        #           c) self.mode = "G"
        #               - energy to power devices will be taken exclusively from the grid and if the grid is
        #               down then no energy will be supplied to devices and they will turn off.
        #               Batteries will still charge if generators produce energy
        #
        #       NOTE: THIS ONLY AFFECTS POWERING DEVICES, CHARGING BATTERIES IS A SEPARATE CONFIGURATION BELOW
        self.consumption_mode = "RSG"

        #       self.charging_mode: can be configured by MQTT. Is a number from 0 to 2 where each number means that energy storage units are:
        #           - 0: not being charged
        #           - 1: being charged using excess produced energy
        #           - 2: being charged using excess produced energy AND energy from the grid
        #
        self.charging_mode = 1



        # how many milliseconds of simulated time passes in one tick
        self.base_millis_per_tick: int = 100
        # how many milliseconds does it actually take to process one tick
        self.simulated_millis_per_tick: int = self.base_millis_per_tick
        # Both of these together determine how fast time in simulation passes
        # Example:
        #   self.base_millis_per_tick = 1000
        #   self.simulated_millis_per_tick = 100
        #   - Devices and everything else in the simulation is updated once per second (1000ms)
        #   - Time inside the simulation passes in 1 seconds increments.
        #   - since self.simulated_millis_per_tick is less than self.base_millis_per_tick,
        #     the simulation runs faster than real-time (10x faster in this case,
        #     so when 1 second of real life passes, 10 seconds pass in the simulation)
        #   Basically dividing base_millis_per_tick by simulated_millis_per_tick gives you the speed multiplier

        self.current_tick: int = 0
        self.STARTING_DATETIME: datetime = datetime.combine(
            datetime.today(),
            dt_time(hour=14, minute=0)
        )

        self.running: bool = False

    # Running logic

    # def on_mqtt_message(self, client, userdata, msg):
    #     try:
    #         import json
    #         payload = json.loads(msg.payload)
    #         topic = msg.topic
    #
    #         if "devices" in topic and topic.endswith("/set"):
    #
    #             device_uuid = topic.split("/")[-2]
    #             device = next((d for d in self.devices if str(d.get_uuid()) == device_uuid), None)
    #
    #             if device:
    #                 if "is_on" in payload:
    #                     device.is_on = bool(payload["is_on"])
    #
    #                 if "level" in payload and hasattr(device, 'set_level'):
    #                     device.set_level(float(payload["level"]))
    #
    #                 print(f"MQTT: Zaktualizowano urządzenie {device.name} ({device_uuid})")
    #
    #         elif topic.endswith("/simulation/control"):
    #             if "speed" in payload:
    #                 self.set_simulation_speed(payload["speed"])
    #
    #             if "mode" in payload:
    #                 self.consumption_mode = payload["mode"]
    #
    #             print(f"MQTT: Zaktualizowano parametry symulacji")
    #
    #     except Exception as e:
    #         print(f"Błąd MQTT: {e}")


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
        # Simulation process:
        # All power ratings are in Watts, and all energy is stored as Watthours
        # 1) Update weather conditions for next tick
        # 2) Update energy storage units, generators and grid for next tick
        #       (resets available energy to be taken out in that tick)
        # 3) Calculate total energy produced in that tick.
        # 4) Calculate partial and total energy available for powering devices from all available sources.
        #       (depends on self.consumption_mode and:
        #           - can be lower than produced energy, if for example only stored energy is used
        #           - can be higher than produced energy, because it may include energy that the grid can provide
        #       )
        # 5) Check if there is enough energy to power all devices, disable random devices until there is enough.
        # 6) Consume the energy according to self.consumption_mode
        # 7) Update devices for next tick
        # 8) Charge batteries according to self.charging_mode

        millis = self.base_millis_per_tick

        # 1) Update weather conditions for next tick
        for w in self.weathers:
            w.update(millis)

        # 2) Update energy storage units, generators and grid for next tick
        for d in self.energy_storages:
            d.update(millis)
        for d in self.energy_generators:
            d.update(millis)
        if self.electric_grid is not None:
            self.electric_grid.update(millis)

        # 3) Calculate total energy produced in that tick.
        total_energy_produced = 0.0
        for eg in self.energy_generators:
            total_energy_produced += eg.get_available_energy()

        # 4) Calculate partial and total energy available for powering devices from all available sources.
        available_energy_from_storage = 0.0
        for es in self.energy_storages:
            available_energy_from_storage += es.get_available_energy()

        available_grid_energy = 0.0
        if self.electric_grid is not None:
            self.electric_grid.get_available_energy()


        total_available_energy = (total_energy_produced if 'R' in self.consumption_mode else 0.0) \
                                 + (available_energy_from_storage if 'S' in self.consumption_mode else 0.0) \
                                 + (available_grid_energy if 'G' in self.consumption_mode else 0.0)

        # 5) Check if there is enough energy to power all devices, disable random devices until there is enough.
        total_energy_required = self.calculate_total_energy_required(millis)

        active_devices = [d for d in self.devices if d.is_active]
        while total_energy_required > total_available_energy:
            if not active_devices:
                raise RuntimeError("No active devices left to disable")
            rd = random.choice(active_devices)
            rd.disable()
            print(rd.name + " disabled due to insufficient energy. Required: " + str(total_energy_required) + " Available: " + str(total_available_energy))
            total_energy_required = self.calculate_total_energy_required(millis)

        # 6) Consume the energy according to self.consumption_mode
        total_energy_required -= self.consume_required_energy(total_energy_required)

        # for source_type in self.consumption_mode:
        #     if total_energy_required > 0.0:
        #         if source_type == "R":
        #             if total_energy_produced >= total_energy_required:
        #                 total_energy_produced -= total_energy_required
        #                 total_energy_required = 0.0
        #             else:
        #                 total_energy_required -= total_energy_produced
        #                 total_energy_produced = 0.0
        #         elif source_type == "S":
        #             for es in self.energy_storages:
        #                 available = es.calculate_available_energy(millis)
        #                 if available > total_energy_required:
        #                     es.discharge_battery(total_energy_required, millis)
        #                     total_energy_required = 0
        #                     break
        #                 else:
        #                     total_energy_required -= available
        #                     es.discharge_battery(available, millis)
        #         elif source_type == "G":
        #             if available_grid_energy >= total_energy_required:
        #                 available_grid_energy -= total_energy_required
        #                 total_energy_required = 0.0
        #             else:
        #                 total_energy_required -= available_grid_energy
        #                 available_grid_energy = 0.0

        # 7) Update devices for next tick
        for d in self.devices:
            d.update(millis)

        # If code is written properly then at this point total_energy_required should be 0.0
        if total_energy_required > 0.001:
            raise RuntimeError(f"Energy requirement not satisfied after consumption, remaining: {total_energy_required}")

        # 8) Charge batteries according to self.charging_mode
        if self.charging_mode > 0:
            for es in self.energy_storages:
                for d in self.energy_generators:
                    can_accept = es.get_max_energy_can_take()
                    es.charge_battery(d.consume_energy(can_accept))
                if self.charging_mode == 2:
                    can_accept = es.get_max_energy_can_take()
                    es.charge_battery(self.electric_grid.consume_energy(can_accept))

        self.current_tick += 1

    def calculate_total_energy_required(self, millis: int) -> float:
        total_energy_required = 0.0
        for d in self.devices:
            total_energy_required += d.calculate_required_energy(millis)
        return total_energy_required

    def calculate_total_energy_available(self, millis: int) -> float:
        total_energy_produced = 0.0
        available_energy_from_storage = 0.0
        if self.electric_grid is not None:
            available_grid_energy = self.electric_grid.get_available_energy()
        for eg in self.energy_generators:
            total_energy_produced += eg.get_available_energy()
        for es in self.energy_storages:
            available_energy_from_storage += es.get_available_energy()

        return (total_energy_produced if 'R' in self.consumption_mode else 0.0) \
                                 + (available_energy_from_storage if 'S' in self.consumption_mode else 0.0) \
                                 + (available_grid_energy if 'G' in self.consumption_mode else 0.0)

    def consume_required_energy(self, total_energy_required: float):
        energy_consumed = 0.0
        sources: list[EnergySource] = []
        for source_type in self.consumption_mode:
            if source_type == "R":
                sources.extend(self.energy_generators)
            elif source_type == "S":
                sources.extend(self.energy_storages)
            elif source_type == "G":
                sources.append(self.electric_grid)

        for s in sources:
            if s is not None:
                energy_consumed += s.consume_energy(total_energy_required)
        return energy_consumed

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

    def publish_state(self, topic: str, extra=None):
        payload = {
            "ts": int(self.get_current_date().timestamp())
        }

        if extra:
            payload.update(extra)

        self.mqtt.publish(self.build_topic(topic), json.dumps(payload), qos=1)

    def subscribe(self, topic: str, on_message):
        topic = self.build_topic(topic)
        self.mqtt.subscribe(topic)
        self.mqtt.message_callback_add(topic, on_message)

    def build_topic(self, topic: str):
        return f"{self.name}/{topic}"
