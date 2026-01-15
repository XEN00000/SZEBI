import random

class ForecastClient:
    """
    Klient do komunikacji z Modułem Prognozowania.
    Realizuje interfejs IEnergyForecast.
    """
    def get_energy_forecast(self):
        # MOCK: Symulujemy dane pogodowe i cenowe
        # requests.get('http://forecast-module/api/...')
        return {
            "energy_price": random.uniform(0.40, 1.50),  # Cena w PLN
            "temperature": random.uniform(-5.0, 30.0),   # Temp zewnętrzna
            "cloud_cover": random.randint(0, 100)        # Zachmurzenie %
        }

class SimulationClient:
    """
    Klient do komunikacji z Modułem Symulacji.
    Realizuje interfejs IDeviceControl[cite: 265].
    """
    def publish_command(self, device_id, command_map):
        # MOCK: Symulujemy wysłanie rozkazu do urządzenia
        print(f"\n[INTEGRATION] --> WYSYŁAM DO SYMULACJI (ID={device_id}): {command_map}")
        # Zwracamy True jako potwierdzenie (ACK)
        return True