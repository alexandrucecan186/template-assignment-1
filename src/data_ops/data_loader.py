# -----------------------------
# Load Data
# -----------------------------
import json
import csv
import pandas as pd
from pathlib import Path

from pathlib import Path
from dataclasses import dataclass
from logging import Logger
import pandas as pd
import xarray as xr
import numpy as np
import yaml

from typing import Dict, Any

class DataLoader:
    """
    Loads energy system input data for a given configuration/question from structured CSV and json files
    and an auxiliary configuration metadata file.
    
    Example usage:
    open interactive window in VSCode,
    >>> cd ../../
    run the script data_loader.py in the interactive window,
    >>> data = DataLoader(input_path='..')
    """
    question: str
    input_path: Path

    def __init__(self, data_dir: str = "data/question_1a"):
        self.data_dir = Path(data_dir)

    def load_all_jsons(self) -> Dict[str, Any]:
        """Load inputs for Q1(a); return a single dict with consistent shapes."""
        bus = json.loads((self.data_dir / "bus_params.json").read_text())[0]          # first/only bus
        app_all = json.loads((self.data_dir / "appliance_params.json").read_text())   # list or dict
        der = json.loads((self.data_dir / "DER_production.json").read_text())[0]      # first profile
        usage = json.loads((self.data_dir / "usage_preference.json").read_text())[0]  # first consumer

        # Normalize appliance structure to a single dict
        app = app_all[0] if isinstance(app_all, list) else app_all

        # Basic shape check
        prices = bus["energy_price_DKK_per_kWh"]
        pv_ratio = der["hourly_profile_ratio"]
        assert len(prices) == len(pv_ratio), "PV ratio length must match price vector length."

        return {"bus": bus, "appliance": app, "der_profile": der, "usage": usage}

    def _load_dataset(self, question_name: str):
        """Helper function to load all CSV or json files, using the appropriate method based on file extension.
        
        example usage: 
        call the load_dataset() function from utils.py to load all files in the input_path directory
        save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)
        """
        pass


    def _load_data_file(self, question_name: str, file_name: str):
        """
        Placeholder function 
        Helper function to load a specific CSV or json file, using the appropriate method based on file extension.. Raises FileNotFoundError if missing.
        
        example usage: 
        define and call a load_data_file() function from utils.py to load a specific file in the input_path directory
        save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)"""
        pass

    def load_aux_data(self, question_name: str, filename: str):
        """
        Placeholder Helper function to Load auxiliary metadata for the scenario/question from a YAML/json file or other formats
        
        Example application: 
        define and call a load_aux_data() function from utils.py to load a specific auxiliary file in the input_path directory
        Save the content as s class attributes, in a dictionary, pd datframe or other: self.aux_data
        Attach key values as class attributes (flattened).
        """
        pass