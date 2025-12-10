from typing import Dict, Tuple
from ..models import Measurement


class Deduplicator:
    def __init__(self):
        self.recent_records: Dict[int, Tuple] = {}

    def merge_duplicates(self, data: Measurement) -> bool:
        """
        Identyfikuje rekordy o identycznym sensor_id i timestamp, scala je.
        """
        # data.status = MeasurementStatus.DUPLICATE
        return False