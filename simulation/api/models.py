from django.db import models
from django.utils import timezone
import datetime

class SimulationState(models.Model):
    """
    Singleton - przechowuje aktualny wirtualny czas symulacji.
    Tylko jeden rekord w tej tabeli powinien istnieć.
    """
    current_sim_time = models.DateTimeField(default=timezone.now)
    is_running = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.pk = 1 # Zawsze nadpisujemy ID=1, żeby mieć tylko jeden stan
        super(SimulationState, self).save(*args, **kwargs)

    @classmethod
    def get_state(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Symulacja: {self.current_sim_time.strftime('%Y-%m-%d %H:%M')}"

class EnergyTariff(models.Model):
    """Definicja taryfy dostawcy energii."""
    name = models.CharField(max_length=50) # np. G11, G12-Szczyt
    price_per_kwh = models.DecimalField(max_digits=6, decimal_places=4)
    # Uproszczone godziny obowiązywania (0-23)
    start_hour = models.IntegerField(default=0)
    end_hour = models.IntegerField(default=23)

    def __str__(self):
        return f"{self.name} ({self.price_per_kwh} PLN)"

class Device(models.Model):
    """Urządzenia w budynku (odbiorniki i źródła)."""
    TYPE_CHOICES = [
        ('CONSUMER', 'Odbiornik (np. HVAC, Oświetlenie)'),
        ('PRODUCER', 'Producent (np. Fotowoltaika)'),
        ('STORAGE', 'Magazyn Energii'),
    ]
    
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    nominal_power = models.FloatField(help_text="Moc w kW (dodatnia)")
    
    # Opcjonalnie: priorytet (do optymalizacji)
    priority = models.IntegerField(default=1, help_text="1 = krytyczne, 10 = można wyłączyć")

    def __str__(self):
        return f"{self.name} ({self.device_type}) - {self.nominal_power}kW"

class WeatherData(models.Model):
    """Historia i prognoza pogody."""
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    cloud_cover = models.FloatField(help_text="0-100%")
    wind_speed = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp}: {self.temperature}°C"