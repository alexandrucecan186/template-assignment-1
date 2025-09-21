from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
import xarray as xr

from typing import Dict, Any, Optional, List
from gurobipy import Model, GRB, quicksum

class OptModel:
    
    def __init__(self, extract_duals: bool = False, solver_output: bool = False):
        self.extract_duals = extract_duals
        self.solver_output = solver_output
        self.m: Optional[Model] = None
        self.vars: Dict[str, Any] = {}
        self.cons: Dict[str, List[Any]] = {}

    def _parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        bus = data["bus"]
        app = data["appliance"]
        der = data["der_profile"]
        usage = data["usage"]

        prices = bus["energy_price_DKK_per_kWh"]  # DKK/kWh
        T = len(prices)

        # Tariffs already corrected in your JSON to 0.5 / 0.4 DKK/kWh
        params = {
            "T": T,
            "prices": prices,
            "tau_imp": bus["import_tariff_DKK/kWh"],               # DKK/kWh
            "tau_exp": bus["export_tariff_DKK/kWh"],               # DKK/kWh
            "Gmax_imp": bus["max_import_kW"],                      # kW == kWh/h
            "Gmax_exp": bus["max_export_kW"],
            "c_pen_imp": bus["penalty_excess_import_DKK/kWh"],     # DKK/kWh
            "c_pen_exp": bus["penalty_excess_export_DKK/kWh"],     # DKK/kWh
            "Lmax": app["load"][0]["max_load_kWh_per_hour"],       # kWh/h
            "rhoL_up": app["load"][0]["max_ramp_rate_up_ratio"],   # 0..1
            "rhoL_dn": app["load"][0]["max_ramp_rate_down_ratio"], # 0..1
            "Ppv_max": app["DER"][0]["max_power_kW"],              # kW == kWh/h
            "rhoPV_up": app["DER"][0]["max_ramp_rate_up_ratio"],   # 0..1
            "rhoPV_dn": app["DER"][0]["max_ramp_rate_down_ratio"], # 0..1
            "pv_ratio": der["hourly_profile_ratio"],               # 0..1
        }

        # Daily minimum energy: value is “hours at max capacity” → multiply by Lmax to get kWh
        min_hours = usage["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"]
        params["Emin"] = min_hours * params["Lmax"]  # kWh

        assert len(params["pv_ratio"]) == params["T"]
        return params

    def solve(self, data: Dict[str, Any]) -> Dict[str, Any]:
        p = self._parse(data)
        T = p["T"]

        m = Model("Q1a_model")
        m.Params.OutputFlag = 1 if self.solver_output else 0

        # ---- Variables (kWh) ----
        l    = m.addVars(T, name="l",    lb=0.0, ub=p["Lmax"])  # load
        pv   = m.addVars(T, name="pv",   lb=0.0)                # PV used
        gimp = m.addVars(T, name="gimp", lb=0.0)                # import
        gexp = m.addVars(T, name="gexp", lb=0.0)                # export
        eimp = m.addVars(T, name="eimp", lb=0.0)                # excess import
        eexp = m.addVars(T, name="eexp", lb=0.0)                # excess export

        self.vars = {"l": l, "pv": pv, "gimp": gimp, "gexp": gexp, "eimp": eimp, "eexp": eexp}
        cons = {k: [] for k in ["pv_avail","balance","daily_min","imp_softcap","exp_softcap","l_rup","l_rdn","pv_rup","pv_rdn"]}

        # ---- Constraints ----
        for t in range(T):
            cons["pv_avail"].append(m.addConstr(pv[t] <= p["Ppv_max"] * p["pv_ratio"][t], name=f"pv_avail[{t}]"))
            cons["balance"].append(m.addConstr(l[t] == pv[t] + gimp[t] - gexp[t], name=f"balance[{t}]"))
            cons["imp_softcap"].append(m.addConstr(gimp[t] <= p["Gmax_imp"] + eimp[t], name=f"imp_softcap[{t}]"))
            cons["exp_softcap"].append(m.addConstr(gexp[t] <= p["Gmax_exp"] + eexp[t], name=f"exp_softcap[{t}]"))

        cons["daily_min"].append(m.addConstr(sum(l[t] for t in range(T)) >= p["Emin"], name="daily_min"))

        for t in range(1, T):
            cons["l_rup"].append(m.addConstr(l[t]   - l[t-1] <= p["rhoL_up"]  * p["Lmax"],    name=f"l_rup[{t}]"))
            cons["l_rdn"].append(m.addConstr(l[t-1] - l[t]   <= p["rhoL_dn"]  * p["Lmax"],    name=f"l_rdn[{t}]"))
            cons["pv_rup"].append(m.addConstr(pv[t]   - pv[t-1] <= p["rhoPV_up"] * p["Ppv_max"], name=f"pv_rup[{t}]"))
            cons["pv_rdn"].append(m.addConstr(pv[t-1] - pv[t]   <= p["rhoPV_dn"] * p["Ppv_max"], name=f"pv_rdn[{t}]"))

        self.cons = cons

        # ---- Objective (DKK) ----
        obj = quicksum(
            (p["prices"][t] + p["tau_imp"]) * gimp[t]
            - (p["prices"][t] - p["tau_exp"]) * gexp[t]
            + p["c_pen_imp"] * eimp[t]
            + p["c_pen_exp"] * eexp[t]
            for t in range(T)
        )
        m.setObjective(obj, GRB.MINIMIZE)
        m.optimize()
        self.m = m

        # ---- Results ----
        res = {
            "status": int(m.status),
            "obj_val_DKK": float(m.objVal) if m.SolCount > 0 else None,
            "params": p,
            "series": {
                "l":    [l[t].X    if m.SolCount>0 else None for t in range(T)],
                "pv":   [pv[t].X   if m.SolCount>0 else None for t in range(T)],
                "gimp": [gimp[t].X if m.SolCount>0 else None for t in range(T)],
                "gexp": [gexp[t].X if m.SolCount>0 else None for t in range(T)],
                "eimp": [eimp[t].X if m.SolCount>0 else None for t in range(T)],
                "eexp": [eexp[t].X if m.SolCount>0 else None for t in range(T)],
            }
        }
        if m.SolCount > 0:
            res["totals"] = {
                "sum_l":    float(sum(res["series"]["l"])),
                "sum_pv":   float(sum(res["series"]["pv"])),
                "sum_imp":  float(sum(res["series"]["gimp"])),
                "sum_exp":  float(sum(res["series"]["gexp"])),
                "sum_eimp": float(sum(res["series"]["eimp"])),
                "sum_eexp": float(sum(res["series"]["eexp"])),
            }

        if self.extract_duals and m.SolCount > 0:
            duals = {
                "mu": [c.Pi for c in cons["balance"]],
                "lambda": cons["daily_min"][0].Pi
            }
            for key in ["pv_avail","imp_softcap","exp_softcap","l_rup","l_rdn","pv_rup","pv_rdn"]:
                duals[key] = [c.Pi for c in cons[key]]
            res["duals"] = duals

        return res