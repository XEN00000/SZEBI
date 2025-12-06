import datetime
import threading
import time
from datetime import datetime, timedelta
from simulation.logic.base.environment import Environment

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
    def __init__(self):
        self.environments = []
        self.base_millis_per_tick = 15 * 60 * 1000
        self.simulated_millis_per_tick = self.base_millis_per_tick
        self.current_tick = 0
        self.STARTING_DATETIME = datetime.now()
        self.running = False

    """it's done this way on purpose: it makes it a bit harder to use,
    but makes it easier to catch unintended behaviour"""
    def start(self) -> None:
        if self.running:
            raise ValueError('simulation is already running')
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.running:
            raise ValueError('simulation is already not running')
        self.running = False
        if hasattr(self, "_thread"):
            self._thread.join(timeout=1)

    def _run_loop(self):
        interval = self.simulated_millis_per_tick / 1000.0
        next_tick = time.perf_counter()

        while self.get_running():
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
            if wait_time > 0:
                time.sleep(wait_time)
            else:
                raise RuntimeError(
                    f"Tick processing overran and loop is running {wait_time:.3f}s slow"
                )

    def tick(self):
        millis = self.base_millis_per_tick
        for env in self.environments:
            env.weather.update(millis)
            env.update(millis)
        self.current_tick += 1

    def get_running(self) -> bool:
        return self.running

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
            raise ValueError(f'time resolution must be between a millisecond (1) and a week (604800000), got {millis_per_tick}')
        sim_speed = self.get_simulation_speed()
        self.base_millis_per_tick = millis_per_tick
        self.set_simulation_speed(sim_speed)

    def get_time_resolution(self) -> int:
        return self.base_millis_per_tick

    def get_environments(self) -> list[Environment]:
        return self.environments

    def add_environment(self, env: Environment) :
        self.environments.append(env)