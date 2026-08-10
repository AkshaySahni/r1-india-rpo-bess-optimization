# -*- coding: utf-8 -*-
"""
Parallel Multi-Processing Execution Engine for 8,760-Hour RPO Scenario Sweeps.
Executes 96 baseline scenarios and degradation sensitivity sweeps concurrently across CPU cores.
"""

import os
import pandas as pd
import multiprocessing as mp

from highs_rpo_solver import solve_rpo_highs, STATUTORY_RPO

def _worker_baseline(args):
    v, st, dur = args
    res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                          bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0)
    return res

def _worker_degradation_sensitivity(args):
    v, st, dur, rep_yrs, deg_pen = args
    res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                          bess_replace_years=rep_yrs, throughput_degradation_penalty_per_mwh=deg_pen)
    res["BESS_Replace_Years"] = rep_yrs
    res["Throughput_Penalty_INR_MWh"] = deg_pen
    return res

def _worker_multiyear_weather(args):
    v, st, dur, yr = args
    res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                          bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0,
                          weather_year=yr)
    res["Weather_Year"] = yr
    return res

def run_parallel_scenarios():
    vintages = list(STATUTORY_RPO.keys())
    states = ["RJ", "GJ", "TN", "KA"]
    durations = [2.0, 4.0, 6.0, 8.0]
    
    # 1. Baseline 96 Scenarios
    task_args = [(v, st, dur) for v in vintages for st in states for dur in durations]
    total_tasks = len(task_args)
    num_cpus = max(1, mp.cpu_count() - 1)
    print(f"Launching Parallel Pool ({num_cpus} CPUs) for {total_tasks} baseline scenarios...")
    
    with mp.Pool(processes=num_cpus) as pool:
        results = pool.map(_worker_baseline, task_args)
        
    df_base = pd.DataFrame([r for r in results if r is not None])
    df_base.to_csv("rpo_scenario_results_8760.csv", index=False)
    print(f"Saved baseline results to: rpo_scenario_results_8760.csv")
    
    # 2. BESS Degradation & Lifespan Sensitivity (FY 2029-30, 4 States, 4 Durations x 3 Lifespans x 3 Throughput Penalties)
    sens_vintages = ["2029-30"]
    replace_years_list = [7, 10, 13]
    deg_penalties = [0.0, 400.0, 800.0]
    
    sens_args = [(v, st, dur, ry, dp) for v in sens_vintages for st in states for dur in durations 
                 for ry in replace_years_list for dp in deg_penalties]
                 
    print(f"Launching Parallel Pool for {len(sens_args)} BESS degradation sensitivity scenarios...")
    with mp.Pool(processes=num_cpus) as pool:
        sens_results = pool.map(_worker_degradation_sensitivity, sens_args)
        
    df_sens = pd.DataFrame([r for r in sens_results if r is not None])
    df_sens.to_csv("rpo_bess_degradation_sensitivity.csv", index=False)
    print(f"Saved BESS degradation sensitivity results to: rpo_bess_degradation_sensitivity.csv")

    # 3. Multi-Year Weather Sensitivity (2019-2023 ERA5 Reanalysis, FY 2029-30, 4 States, 4 Durations)
    weather_years = [2019, 2020, 2021, 2022, 2023]
    weather_args = [(v, st, dur, yr) for v in sens_vintages for st in states for dur in durations for yr in weather_years]
    print(f"Launching Parallel Pool for {len(weather_args)} multi-year weather reanalysis scenarios...")
    with mp.Pool(processes=num_cpus) as pool:
        weather_results = pool.map(_worker_multiyear_weather, weather_args)
        
    df_weather = pd.DataFrame([r for r in weather_results if r is not None])
    df_weather.to_csv("rpo_multiyear_weather_sensitivity.csv", index=False)
    print(f"Saved multi-year weather sensitivity results to: rpo_multiyear_weather_sensitivity.csv")

    return df_base, df_sens, df_weather

if __name__ == "__main__":
    mp.freeze_support()
    run_parallel_scenarios()

