from datetime import datetime
from typing import List
import pandas as pd

from .data_manager import DataManager
from .enums import Measurement


class Statistics:
    """
    Liczy statystyki (mean/min/max) na podstawie surowych danych z DataManager.
    Wynik zwraca jako DataFrame, który potem wykorzystuje Reporting.
    """
    def __init__(self, dataManager: DataManager):
        self.dataManager = dataManager

    def calculateStatistics(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
    ) -> pd.DataFrame:
        """
            Dla podanego pokoju, zakresu czasu i listy metryk:
            1) pobiera dane z DataManager (lista obiektów Aggregate),
            2) liczy mean/min/max dla każdej metryki,
            3) składa wynik w jeden DataFrame.
            Jeśli dla metryki nie ma żadnych danych, wartości mean/min/max są None.
        """
        aggregates = self.dataManager.aggregateRoomData(roomId, periodStart, periodEnd, metric)

        rows = []
        for agg in aggregates:
            if agg.data.empty:
                agg.mean = None
                agg.min = None
                agg.max = None
            else:
                values = agg.data["value"].astype(float)
                agg.mean = float(values.mean())
                agg.min = float(values.min())
                agg.max = float(values.max())

            rows.append(
                {
                    "room_id": agg.roomId,
                    "metric": agg.metric.value,
                    "unit": agg.unit.value,
                    "period_start": agg.periodStart,
                    "period_end": agg.periodEnd,
                    "period": agg.period.value,
                    "mean": agg.mean,
                    "min": agg.min,
                    "max": agg.max,
                    "data": agg.data,
                }
            )

        return pd.DataFrame(rows)