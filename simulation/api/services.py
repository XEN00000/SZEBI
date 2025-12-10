import random
from datetime import timedelta
from django.utils import timezone
from .models import SimulationState, WeatherData, Device

class EnvironmentSimulator:
    def __init__(self):
        self.state = SimulationState.get_state()

    def step(self, minutes=15):
        """Wykonuje jeden krok symulacji."""
        # 1. Przesuń czas symulacji
        self.state.current_sim_time += timedelta(minutes=minutes)
        self.state.save()
        
        current_time = self.state.current_sim_time

        # 2. Wygeneruj pogodę dla nowego czasu
        self.generate_weather(current_time)

        # 3. (Opcjonalnie tutaj można dodać logikę zmiany stanu urządzeń
        # np. jeśli jest noc, wyłącz PV)
        
        return f"Symulacja przesunięta na: {current_time}"

    def generate_weather(self, time):
        """Prosta, losowa pogoda zależna od pory dnia."""
        hour = time.hour
        
        # Baza temperatury: w nocy zimniej, w dzień cieplej
        base_temp = 10 + (10 * (1 - abs(hour - 14) / 12)) 
        # Dodaj losowość (-2 do +2 stopnie)
        actual_temp = base_temp + random.uniform(-2, 2)
        
        # Zachmurzenie (losowe)
        clouds = random.uniform(0, 100)

        WeatherData.objects.create(
            timestamp=time,
            temperature=round(actual_temp, 2),
            cloud_cover=round(clouds, 1)
        )