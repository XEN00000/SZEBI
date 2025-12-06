
""""
WAZNE  ROBIL TO CZAT NIE MAM NA RAZIE NA TO POMYSLU ALE POKI CO
BEDZIE TO LACZNIK ZEBY MODUL STEROWANIA MOGL ZMIENIAC NASTAWY TEM ITP


"""


class Environment:
    def __init__(self, weather, initial_temp: float = 21.0, insulation: float = 0.85):

        self.weather = weather
        self.temperature = initial_temp
        self.insulation = insulation

        # Moc dostarczona przez urządzenia HVAC w danym ticku
        self.heating_power = 0.0   # W
        self.cooling_power = 0.0   # W

    def apply_heating(self, watt: float):
        self.heating_power += watt

    def apply_cooling(self, watt: float):
        self.cooling_power += watt

    def update(self, millis_passed: int):
        outside_temp = self.weather.get_temperature()
        inside_temp = self.temperature

        # 1. Wymiana ciepła z otoczeniem (prosty model)
        diff = outside_temp - inside_temp
        heat_flow = diff * (1 - self.insulation) * 0.01
        self.temperature += heat_flow

        # 2. Ogrzewanie / chłodzenie
        hours = millis_passed / (1000 * 3600)

        # Ogrzewanie — podnosi temperaturę
        self.temperature += (self.heating_power / 1000.0) * hours * 1.8

        # Chłodzenie — obniża temperaturę
        self.temperature -= (self.cooling_power / 1000.0) * hours * 2.0

        # Reset mocy po aktualizacji
        self.heating_power = 0.0
        self.cooling_power = 0.0

    def get_temperature(self):
        return self.temperature

    def get_insulation(self):
        return self.insulation

    def get_heating_power(self):
        return self.heating_power

    def get_cooling_power(self):
        return self.cooling_power