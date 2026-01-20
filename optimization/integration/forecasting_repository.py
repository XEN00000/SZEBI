import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ForecastingRepository:
    """
    Adapter na moduł forecasting.
    Optimization nie powinien znać szczegółów implementacji forecasting,
    tylko wołać jedną metodę: get_latest_forecast().
    """

    def get_latest_forecast(self) -> Optional[Dict[str, Any]]:
        try:
            # Import wewnątrz metody = brak problemów przy starcie Django / migrations
            from forecasting.services import get_latest_forecast
        except Exception as e:
            logger.error("[FORECAST] Nie mogę zaimportować forecasting.services.get_latest_forecast(): %s", e)
            return None

        try:
            forecast = get_latest_forecast()

            # forecast może być: dict / model / serializer output — normalizujemy do dict
            if forecast is None:
                return None

            if isinstance(forecast, dict):
                return forecast

            # jeśli to model Django, to spróbujmy z niego zrobić dict “bezpiecznie”
            if hasattr(forecast, "__dict__"):
                # Uwaga: model ma dużo pól technicznych, więc lepiej jawnie mapować,
                # ale tymczasowo to wystarczy do debug/testów
                return {k: v for k, v in forecast.__dict__.items() if not k.startswith("_")}

            # fallback
            return {"value": str(forecast)}

        except Exception as e:
            logger.error("[FORECAST] Błąd przy get_latest_forecast(): %s", e)
            return None