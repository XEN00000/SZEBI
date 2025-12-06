import regex
from abc import abstractmethod, ABC
from uuid import UUID, uuid4


class Device(ABC):
    def __init__(self, name) -> None:
        if type(self) is Device:
            raise TypeError("Device is abstract")
        self.set_name(name)
        self.uuid = uuid4()
        self.is_active: bool = False

    def enable(self) -> None:
        if self.is_active:
            raise ValueError('device is already enabled')
        self.is_active = True

    def disable(self) -> None:
        if not self.is_active:
            raise ValueError('device is already disabled')
        self.is_active = False

    @abstractmethod
    def update(self, millis_passed: int, **kwargs) -> None:
        pass

    def get_uuid(self) -> UUID:
        return self.uuid

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        pattern = regex.compile(r'^[a-z][a-z0-9-]{2,}$')
        if not pattern.fullmatch(name):
            raise ValueError(f'device name has to start with a letter, and can contain only lowercase letter, digits and dashes. got: {name}')
        self.name = name



