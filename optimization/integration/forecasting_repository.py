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
            # Forecasting ma klasę ForecastingService z metodą get_latest_forecast()
            from forecasting.services import ForecastingService
        except Exception as e:
            logger.error("[FORECAST] Nie mogę zaimportować ForecastingService: %s", e)
            return None

        try:
            service = ForecastingService()
            forecast = service.get_latest_forecast()

            if forecast is None:
                return None

            if isinstance(forecast, dict):
                return forecast

            return {"value": str(forecast)}

        except Exception as e:
            logger.error("[FORECAST] Błąd przy ForecastingService.get_latest_forecast(): %s", e)
            return None