from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd

from .enums import Measurement, MeasurementUnit, ReportType


@dataclass
class Aggregate:
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