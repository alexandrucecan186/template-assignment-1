from pathlib import Path
from typing import Dict, List, Any


from data_ops import DataLoader, DataProcessor
from data_ops.data_visualizer import DataVisualizer
from opt_model.opt_model import OptModel


class Runner:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, results saving and ploting
    """

    def __init__(self, data_dir: str = "data/question_1a"):
        self.data_dir = data_dir

    def _load_config(self) -> None:
        """Load configuration (placeholder method)"""
    # Extract simulation configuration and hyperparameter values (e.g. question, scenarios for sensitivity analysis, duration of simulation, solver name, etc.) and store them as class attributes (e.g. self.scenario_list, self.solver_name, etc.)
    
    def _create_directories(self) -> None:
        """Create required directories for each simulation configuration. (placeholder method)"""

    def prepare_data_single_simulation(self, question_name) -> None:
        """Prepare input data for a single simulation (placeholder method)"""
        # Prepare input data using DataProcessor for a given simulation configuration and store it as class attributes (e.g. self.data)

    def prepare_data_all_simulations(self) -> None:
        """Prepare input data for multiple scenarios/sensitivity analysis/questions (placeholder method)"""
        # Extend data_loader to handle multiple scenarios/questions
        # Prepare data using data_loader for multiple scenarios/questions
        
    def run_single_simulation(self) -> Dict[str, Any]:
        data = DataLoader(self.data_dir).load_all_jsons()

        model = OptModel(extract_duals=True, solver_output=False)
        res = model.solve(data)

        print(f"Status: {res['status']}, Objective (DKK): {res['obj_val_DKK']:.4f}")
        if "totals" in res:
            t = res["totals"]
            print(f"Totals  |  load={t['sum_l']:.3f}  pv={t['sum_pv']:.3f}  imp={t['sum_imp']:.3f}  exp={t['sum_exp']:.3f}")
            balance = t["sum_pv"] + t["sum_imp"] - t["sum_exp"]
            print(f"Balance check: sum(l)={t['sum_l']:.3f}  vs  pv+imp-exp={balance:.3f}")

        viz = DataVisualizer()
        viz.plot_series(res, save_path="results_plot.png")
        viz.plot_stacked(res, save_path="results_stacked.png")
        
        return res
    
    def run_all_simulations(self) -> None:
        """Run all simulations for the configured scenarios (placeholder method)."""
        pass