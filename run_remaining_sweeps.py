# -*- coding: utf-8 -*-
"""
Streaming Scenario Runner for BESS Degradation & Multi-Year Weather Sweeps.
"""

import os
import time
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from highs_rpo_solver import solve_rpo_highs, STATUTORY_RPO

def _run_deg(args):
    v, st, dur, ry, dp = args
    try:
        res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                              bess_replace_years=ry, throughput_degradation_penalty_per_mwh=dp)
        if res is not None:
            res["BESS_Replace_Years"] = ry
            res["Throughput_Penalty_INR_MWh"] = dp
        return res
    except Exception as e:
        return None

def _run_w(args):
    v, st, dur, yr = args
    try:
        res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                              bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0,
                              weather_year=yr)
        if res is not None:
            res["Weather_Year"] = yr
        return res
    except Exception as e:
        return None

def main():
    num_workers = min(4, os.cpu_count() or 4)
    start_t = time.time()
    states = ["RJ", "GJ", "TN", "KA"]
    durations = [2.0, 4.0, 6.0, 8.0]
    
    print(f"=== Running 144 BESS Degradation Sweeps ({num_workers} Workers) ===")
    sens_vintages = ["2029-30"]
    replace_years_list = [7, 10, 13]
    deg_penalties = [0.0, 400.0, 800.0]
    sens_tasks = [(v, st, dur, ry, dp) for v in sens_vintages for st in states for dur in durations 
                  for ry in replace_years_list for dp in deg_penalties]
    
    deg_results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_run_deg, task): task for task in sens_tasks}
        completed = 0
        for f in as_completed(futures):
            completed += 1
            res = f.result()
            if res is not None:
                deg_results.append(res)
            if completed % 12 == 0 or completed == len(sens_tasks):
                df = pd.DataFrame(deg_results)
                df.to_csv("rpo_bess_degradation_sensitivity.csv", index=False)
                df.to_csv("github upload/rpo_bess_degradation_sensitivity.csv", index=False)
                print(f"  [Degradation] Saved {completed}/{len(sens_tasks)} scenarios ({time.time() - start_t:.1f}s)...")
                
    print(f"\n=== Running 48 Multi-Year Weather Sweeps ({num_workers} Workers, 2021-2023) ===")
    weather_years = [2021, 2022, 2023]
    weather_tasks = [(v, st, dur, yr) for v in sens_vintages for st in states for dur in durations for yr in weather_years]
    
    w_results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_run_w, task): task for task in weather_tasks}
        completed = 0
        for f in as_completed(futures):
            completed += 1
            res = f.result()
            if res is not None:
                w_results.append(res)
            if completed % 12 == 0 or completed == len(weather_tasks):
                df = pd.DataFrame(w_results)
                df.to_csv("rpo_multiyear_weather_sensitivity.csv", index=False)
                df.to_csv("github upload/rpo_multiyear_weather_sensitivity.csv", index=False)
                print(f"  [Weather] Saved {completed}/{len(weather_tasks)} scenarios ({time.time() - start_t:.1f}s)...")

    print(f"\n[SUCCESS] All remaining sweeps completed and saved in {time.time() - start_t:.1f}s.")

if __name__ == "__main__":
    main()
