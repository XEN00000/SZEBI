from abc import abstractmethod, ABC
from uuid import UUID, uuid4

from simulation.logic.src.base.weather import Weather
from simulation.logic.src.util.utils import validate_name, parse_bool
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

        def on_mqtt_message(client, userdata, msg):
            self.on_mqtt_message(client, userdata, msg)

        self.sim().subscribe(f"device/set/{self.uuid}", on_mqtt_message)
        self.sim().subscribe(f"device/set/{self.name}", on_mqtt_message)

    def on_mqtt_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            is_active = parse_bool(data.get("is_active"))
            if is_active is not None:
                self.is_active = is_active
        except Exception as e:
            client.publish(f'{msg.topic}/response',
                           f"{type(e).__name__}: {e}", qos=1)
            pass

    def enable(self) -> None:
        if self.is_active:
            raise ValueError('Device is already enabled')
        self.is_active = True

    def disable(self) -> None:
        if not self.is_active:
            raise ValueError('Device is already disabled')
        self.is_active = False


    def sim(self):
        if hasattr(self.weather, 'sim'):
            return self.weather.sim()
        return self.weather

    def publish_state(self, extra = None):
        topic1 = f"device/state/{self.uuid}"
        topic2 = f"device/state/{self.name}"

        payload = {
            "name": self.name,
            "uuid": str(self.uuid),
            "weather_uuid": str(self.weather.get_uuid()),
            "type": self.__class__.__name__,
            "is_active": self.is_active,
        }

        if extra:
            payload.update(extra)

        self.sim().publish_state(topic1, payload)
        self.sim().publish_state(topic2, payload)


    @abstractmethod
    def update(self, millis_passed: int) -> None:
        pass

    def get_uuid(self) -> UUID:
        return self.uuid

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name


