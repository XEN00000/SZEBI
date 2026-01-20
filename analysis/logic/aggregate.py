from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd

from .enums import Measurement, MeasurementUnit, ReportType


@dataclass
class Aggregate:
    """
       Klasa pomocnicza przechowująca zagregowane dane pomiarowe dla jednego pokoju i jednej metryki w zadanym przedziale czasu.
       Jest wykorzystywana do obliczeń statystycznych oraz do generowania wykresów i raportów.
    """
    roomId: str
    metric: Measurement
    unit: MeasurementUnit
    periodStart: datetime
    periodEnd: datetime
    period: ReportType
    mean: Optional[float]
    min: Optional[float]
    max: Optional[float]
    data: pd.DataFrame