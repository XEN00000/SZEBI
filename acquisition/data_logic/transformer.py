from typing import Dict
from ..models import Measurement

class Transformer:
    def __init__(self):
        self.conversion_table_dict: Dict = {}

    def convert_units(self, data: Measurement) -> Measurement:
        """
        Konwertuje jednostki pomiarowe do standardowego formatu systemowego.
        """

        return data