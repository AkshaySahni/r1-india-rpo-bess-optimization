# -*- coding: utf-8 -*-
"""
High-Speed Parallel Scenario Sweep Engine using ProcessPoolExecutor.
"""

import os
import time
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from highs_rpo_solver import solve_rpo_highs, STATUTORY_RPO

def _run_single_baseline(args):
    v, st, dur = args
    try:
        return solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                               bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0)
    except Exception as e:
        print(f"[ERR] Baseline {v}-{st}-{dur}h: {e}")
        return None

def _run_single_degradation(args):
    v, st, dur, ry, dp = args
    try:
        res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                              bess_replace_years=ry, throughput_degradation_penalty_per_mwh=dp)
        if res is not None:
            res["BESS_Replace_Years"] = ry
            res["Throughput_Penalty_INR_MWh"] = dp
        return res
    except Exception as e:
        print(f"[ERR] Degradation {v}-{st}-{dur}h-{ry}y: {e}")
        return None

def _run_single_weather(args):
    v, st, dur, yr = args
    try:
        res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                              bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0,
                              weather_year=yr)
        if res is not None:
            res["Weather_Year"] = yr
        return res
    except Exception as e:
        print(f"[ERR] Weather {v}-{st}-{dur}h-{yr}: {e}")
        return None

def main():
    vintages = list(STATUTORY_RPO.keys())
    states = ["RJ", "GJ", "TN", "KA"]
    durations = [2.0, 4.0, 6.0, 8.0]
    num_workers = min(4, os.cpu_count() or 4)
    start_t = time.time()
    
    print(f"=== 1. Parallel Baseline Sweeps ({num_workers} Workers) ===")
    base_tasks = [(v, st, dur) for v in vintages for st in states for dur in durations]
    base_results = []
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_run_single_baseline, task): task for task in base_tasks}
        completed = 0
        for f in as_completed(futures):
            completed += 1
            res = f.result()
            if res is not None:
                base_results.append(res)
            if completed % 16 == 0 or completed == len(base_tasks):
                print(f"  [Baseline] {completed}/{len(base_tasks)} scenarios completed in {time.time() - start_t:.1f}s...")
                
    df_base = pd.DataFrame(base_results)
    df_base.to_csv("rpo_scenario_results_8760.csv", index=False)
    df_base.to_csv("github upload/rpo_scenario_results_8760.csv", index=False)
    print(f"[OK] Exported 96 baseline results to rpo_scenario_results_8760.csv")
    
    print(f"\n=== 2. Parallel BESS Degradation Sweeps ({num_workers} Workers) ===")
    sens_vintages = ["2029-30"]
    replace_years_list = [7, 10, 13]
    deg_penalties = [0.0, 400.0, 800.0]
    sens_tasks = [(v, st, dur, ry, dp) for v in sens_vintages for st in states for dur in durations 
                  for ry in replace_years_list for dp in deg_penalties]
    sens_results = []
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_run_single_degradation, task): task for task in sens_tasks}
        completed = 0
        for f in as_completed(futures):
            completed += 1
            res = f.result()
            if res is not None:
                sens_results.append(res)
            if completed % 36 == 0 or completed == len(sens_tasks):
                print(f"  [Degradation] {completed}/{len(sens_tasks)} scenarios completed...")
                
    df_sens = pd.DataFrame(sens_results)
    df_sens.to_csv("rpo_bess_degradation_sensitivity.csv", index=False)
    df_sens.to_csv("github upload/rpo_bess_degradation_sensitivity.csv", index=False)
    print(f"[OK] Exported 144 degradation results to rpo_bess_degradation_sensitivity.csv")

    print(f"\n=== 3. Parallel Weather Sensitivity Sweeps ({num_workers} Workers, 2021-2023) ===")
    weather_years = [2021, 2022, 2023]
    weather_tasks = [(v, st, dur, yr) for v in sens_vintages for st in states for dur in durations for yr in weather_years]
    weather_results = []
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_run_single_weather, task): task for task in weather_tasks}
        completed = 0
        for f in as_completed(futures):
            completed += 1
            res = f.result()
            if res is not None:
                weather_results.append(res)
            if completed % 16 == 0 or completed == len(weather_tasks):
                print(f"  [Weather] {completed}/{len(weather_tasks)} scenarios completed...")
                
    df_weather = pd.DataFrame(weather_results)
    df_weather.to_csv("rpo_multiyear_weather_sensitivity.csv", index=False)
    df_weather.to_csv("github upload/rpo_multiyear_weather_sensitivity.csv", index=False)
    print(f"[OK] Exported 48 weather sensitivity results to rpo_multiyear_weather_sensitivity.csv")
    
    print(f"\n[SUCCESS] Completed all 288 optimization scenarios in {time.time() - start_t:.1f}s.")

if __name__ == "__main__":
    main()
