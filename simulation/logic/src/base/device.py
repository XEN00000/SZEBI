from abc import abstractmethod, ABC
from uuid import UUID, uuid4

from simulation.logic.src.base.weather import Weather
from simulation.logic.src.util.utils import validate_name
import weakref
import json


class Device(ABC):
    is_active: bool = True

    def __init__(self, name: str, weather: Weather) -> None:
        if type(self) is Device:
            raise TypeError("Device is abstract")
        self.uuid = uuid4()
        self.weather = weather

        self.set_name(name)

    def enable(self) -> None:
        if self.is_active:
            raise ValueError('Device is already enabled')
        self.is_active = True

    def disable(self) -> None:
        if not self.is_active:
            raise ValueError('Device is already disabled')
        self.is_active = False


    def sim(self):
        s = self.weather.sim()
        if s is None:
            raise RuntimeError('Device exists outside of Simulation context')
        return s

    def publish_state(self, extra):
        topic = f"szebi/{self.sim().name}/devices/{self.name}/state"

        payload = {
            "name": self.name,
            "type": self.__class__.__name__,
            "is_active": self.is_active,
            "ts": int(self.sim().get_current_date().timestamp())
        }

        if extra:
            payload.update(extra)

        self.sim().mqtt.publish(topic, json.dumps(payload), qos=1, retain=True)

    @abstractmethod
    def update(self, millis_passed: int) -> None:
        self.publish_state()

    def get_uuid(self) -> UUID:
        return self.uuid

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name
