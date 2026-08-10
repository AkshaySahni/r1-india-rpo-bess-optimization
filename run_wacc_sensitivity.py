# -*- coding: utf-8 -*-
"""
Execution Script for Phase 13: WACC Financial Sensitivity Analysis (8%, 10%, 12%).
Calculates landed LCOE impact across low (8%), baseline (10%), and high (12%) cost of capital environments.
"""

import os
import time
import pandas as pd
from highs_rpo_solver import solve_rpo_highs

def run_wacc_sensitivity_sweeps():
    states = ["RJ", "GJ", "TN", "KA"]
    vintages = ["2029-30"]
    durations = [4.0]
    wacc_rates = [0.08, 0.10, 0.12]
    
    results = []
    start_time = time.time()
    total = len(vintages) * len(states) * len(durations) * len(wacc_rates)
    count = 0
    
    print(f"=== Running {total} WACC Financial Sensitivity Scenarios (r = 8%, 10%, 12%) ===", flush=True)
    for v in vintages:
        for st in states:
            for dur in durations:
                for wacc in wacc_rates:
                    count += 1
                    res = solve_rpo_highs(
                        vintage=v,
                        state=st,
                        peak_demand_mw=1000.0,
                        storage_duration_hrs=dur,
                        bess_replace_years=10,
                        throughput_degradation_penalty_per_mwh=400.0,
                        weather_year=2022,
                        discount_rate=wacc
                    )
                    if res is not None:
                        res["WACC_Pct"] = wacc * 100.0
                        res["CRF"] = round((wacc * (1.0 + wacc)**25) / ((1.0 + wacc)**25 - 1.0), 5)
                        results.append(res)
                    print(f"  [{count}/{total}] {st} {v} {dur}h WACC={wacc*100:.0f}% -> LCOE: INR {res['Landed_LCOE_INR_kWh']:.2f}/kWh", flush=True)

    df_wacc = pd.DataFrame(results)
    output_path = "rpo_wacc_financial_sensitivity.csv"
    github_path = "github upload/rpo_wacc_financial_sensitivity.csv"
    df_wacc.to_csv(output_path, index=False)
    os.makedirs("github upload", exist_ok=True)
    df_wacc.to_csv(github_path, index=False)
    print(f"\n[SUCCESS] WACC sensitivity sweeps completed in {time.time() - start_time:.2f}s!", flush=True)

if __name__ == "__main__":
    run_wacc_sensitivity_sweeps()
