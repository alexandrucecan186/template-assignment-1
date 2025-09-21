import json
import csv
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

class DataVisualizer:
    def plot_series(self, results: dict, save_path: str = None):
        series = results.get("series", {})
        if not series:
            print("No series data in results")
            return

        hours = list(range(len(series["l"])))

        plt.figure(figsize=(10, 6))
        plt.plot(hours, series["l"],    label="Load (l)",    marker="o")
        plt.plot(hours, series["pv"],   label="PV used (pv)",marker="s")
        plt.plot(hours, series["gimp"], label="Import (gimp)",marker="^")
        plt.plot(hours, series["gexp"], label="Export (gexp)",marker="v")
        plt.xlabel("Hour")
        plt.ylabel("Energy [kWh]")
        plt.title("Optimal Scheduling - Q1(a)")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)

        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
        else:
            plt.show()

    def plot_stacked(self, results: dict, save_path: str = None):
        """
        Show how the load is covered by PV and imports, and when there are exports.
        """
        series = results.get("series", {})
        if not series:
            print("No series data in results")
            return

        hours = list(range(len(series["l"])))
        pv = series["pv"]
        gimp = series["gimp"]
        gexp = series["gexp"]
        l = series["l"]

        plt.figure(figsize=(10, 6))
        plt.stackplot(hours, pv, gimp, labels=["PV used", "Import"], alpha=0.8)
        plt.plot(hours, l, color="black", linewidth=2, label="Load")
        plt.plot(hours, gexp, color="red", linestyle="--", label="Export")

        plt.xlabel("Hour")
        plt.ylabel("Energy [kWh]")
        plt.title("Load Coverage and Exports - Q1(a)")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)

        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
            print(f"Stacked plot saved to {save_path}")
        else:
            plt.show()