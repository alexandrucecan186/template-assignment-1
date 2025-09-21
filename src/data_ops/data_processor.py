import json
import csv
import pandas as pd
from pathlib import Path

from typing import Dict, Any


class DataProcessor:
    """
    Minimal placeholder so imports succeed.
    For Q1(a) we don't need any processing; just return the data as-is.
    """
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data