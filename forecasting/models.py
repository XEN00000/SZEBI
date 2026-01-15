from django.db import models


class Forecast(models.Model):
    # Data utworzenia prognozy
    created_at = models.DateTimeField(auto_now_add=True)

    # Horyzont czasowy (w minutach, np. 1440 = 24h)
    horizon = models.IntegerField(help_text='Horyzont prognozy w minutach')

    # Wynik w formacie JSON
    # Struktura: { "consumption": [lista wartości], "production": [lista wartości] }
    result = models.JSONField(default=dict)

    # ID modelu, który wygenerował tę prognozę (dla celów audytowych)
    model_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']  # Najnowsze prognozy zawsze na górze listy

    def __str__(self):
        return f"Forecast {self.id} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"