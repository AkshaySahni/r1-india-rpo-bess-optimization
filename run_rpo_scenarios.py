# -*- coding: utf-8 -*-
"""
Sequential/Batch Execution Engine for 8,760-Hour RPO Scenarios (SciPy HiGHS LP Engine).
Executes baseline, BESS degradation sensitivity, and 2021-2023 weather sensitivity sweeps.
"""

import os
import time
import pandas as pd
from highs_rpo_solver import solve_rpo_highs, STATUTORY_RPO

def run_all_scenarios():
    vintages = list(STATUTORY_RPO.keys())
    states = ["RJ", "GJ", "TN", "KA"]
    durations = [2.0, 4.0, 6.0, 8.0]
    
    print("=== 1. Running 96 Baseline Scenarios ===")
    base_results = []
    start_time = time.time()
    count = 0
    total = len(vintages) * len(states) * len(durations)
    
    for v in vintages:
        for st in states:
            for dur in durations:
                count += 1
                res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                                      bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0)
                if res is not None:
                    base_results.append(res)
                if count % 16 == 0 or count == total:
                    elapsed = time.time() - start_time
                    print(f"  [Baseline] Completed {count}/{total} scenarios in {elapsed:.1f}s...")
                    
    df_base = pd.DataFrame(base_results)
    df_base.to_csv("rpo_scenario_results_8760.csv", index=False)
    df_base.to_csv("github upload/rpo_scenario_results_8760.csv", index=False)
    print(f"[OK] Exported 96 baseline results to rpo_scenario_results_8760.csv")
    
    print("\n=== 2. Running 144 BESS Degradation & Lifespan Sensitivity Scenarios ===")
    sens_vintages = ["2029-30"]
    replace_years_list = [7, 10, 13]
    deg_penalties = [0.0, 400.0, 800.0]
    sens_results = []
    count = 0
    total_sens = len(sens_vintages) * len(states) * len(durations) * len(replace_years_list) * len(deg_penalties)
    
    for v in sens_vintages:
        for st in states:
            for dur in durations:
                for ry in replace_years_list:
                    for dp in deg_penalties:
                        count += 1
                        res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                                              bess_replace_years=ry, throughput_degradation_penalty_per_mwh=dp)
                        if res is not None:
                            res["BESS_Replace_Years"] = ry
                            res["Throughput_Penalty_INR_MWh"] = dp
                            sens_results.append(res)
                        if count % 36 == 0 or count == total_sens:
                            elapsed = time.time() - start_time
                            print(f"  [Degradation] Completed {count}/{total_sens} scenarios...")
                            
    df_sens = pd.DataFrame(sens_results)
    df_sens.to_csv("rpo_bess_degradation_sensitivity.csv", index=False)
    df_sens.to_csv("github upload/rpo_bess_degradation_sensitivity.csv", index=False)
    print(f"[OK] Exported 144 degradation sensitivity results to rpo_bess_degradation_sensitivity.csv")
    
    print("\n=== 3. Running 48 Multi-Year Weather Sensitivity Scenarios (2021-2023) ===")
    weather_years = [2021, 2022, 2023]
    weather_results = []
    count = 0
    total_w = len(sens_vintages) * len(states) * len(durations) * len(weather_years)
    
    for v in sens_vintages:
        for st in states:
            for dur in durations:
                for yr in weather_years:
                    count += 1
                    res = solve_rpo_highs(vintage=v, state=st, peak_demand_mw=1000.0, storage_duration_hrs=dur,
                                          bess_replace_years=10, throughput_degradation_penalty_per_mwh=400.0,
                                          weather_year=yr)
                    if res is not None:
                        res["Weather_Year"] = yr
                        weather_results.append(res)
                    if count % 16 == 0 or count == total_w:
                        elapsed = time.time() - start_time
                        print(f"  [Weather] Completed {count}/{total_w} scenarios...")
                        
    df_weather = pd.DataFrame(weather_results)
    df_weather.to_csv("rpo_multiyear_weather_sensitivity.csv", index=False)
    df_weather.to_csv("github upload/rpo_multiyear_weather_sensitivity.csv", index=False)
    print(f"[OK] Exported 48 multi-year weather sensitivity results to rpo_multiyear_weather_sensitivity.csv")
    
    print(f"\n[SUCCESS] Completed all 288 optimization scenario runs in {time.time() - start_time:.1f}s.")

if __name__ == "__main__":
    run_all_scenarios()
