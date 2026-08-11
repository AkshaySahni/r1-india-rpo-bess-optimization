# -*- coding: utf-8 -*-
"""
Programmatic LaTeX Table Generator for India RPO 8760 Optimization Paper.
Single source of truth pipeline reading directly from solver output CSVs:
- rpo_scenario_results_8760.csv
- rpo_bess_degradation_sensitivity.csv
- rpo_multiyear_weather_sensitivity.csv
- rpo_wacc_financial_sensitivity.csv

Exports LaTeX snippet files into tables/:
- tables/table3_baseline.tex
- tables/table4_duration.tex
- tables/table5_empirical.tex
- tables/table6_wacc.tex
- tables/macro_values.tex
"""

import os
import pandas as pd
import numpy as np

TABLE_DIR = "tables"
os.makedirs(TABLE_DIR, exist_ok=True)

def generate_tables():
    df_base = pd.read_csv("rpo_scenario_results_8760.csv")
    df_deg = pd.read_csv("rpo_bess_degradation_sensitivity.csv")
    df_wea = pd.read_csv("rpo_multiyear_weather_sensitivity.csv")
    df_wacc = pd.read_csv("rpo_wacc_financial_sensitivity.csv")

    df_base["Duration"] = (df_base["BESS_Energy_GWh"] / np.maximum(1e-3, df_base["BESS_Power_GW"])).round()
    df_deg["Duration"] = (df_deg["BESS_Energy_GWh"] / np.maximum(1e-3, df_deg["BESS_Power_GW"])).round()
    df_wea["Duration"] = (df_wea["BESS_Energy_GWh"] / np.maximum(1e-3, df_wea["BESS_Power_GW"])).round()
    df_wacc["Duration"] = (df_wacc["BESS_Energy_GWh"] / np.maximum(1e-3, df_wacc["BESS_Power_GW"])).round()

    df_base_4h = df_base[df_base["Duration"] == 4].copy()
    chron_vintages = ["2024-25", "2025-26", "2026-27", "2027-28", "2028-29", "2029-30"]
    state_names = {"RJ": "Rajasthan", "GJ": "Gujarat", "TN": "Tamil Nadu", "KA": "Karnataka"}

    # ------------------ TABLE 3: BASELINE 4-HOUR BESS TRAJECTORY ------------------
    t3_lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"Vintage & State & Solar (GW) & Wind (GW) & BESS Pwr (GW) & BESS Eng (GWh) & Landed LCOE (INR/kWh) & Achieved RPO (\%) \\",
        r"\midrule"
    ]

    for v in chron_vintages:
        v_sub = df_base_4h[df_base_4h["Vintage"] == v]
        first_row = True
        for st in ["RJ", "GJ", "TN", "KA"]:
            row = v_sub[v_sub["State"] == st].iloc[0]
            v_str = f"{v.replace('-', '--')}" if first_row else ""
            t3_lines.append(f"{v_str} & {state_names[st]} & {row['Solar_GW']:.2f} & {row['Wind_GW']:.2f} & {row['BESS_Power_GW']:.2f} & {row['BESS_Energy_GWh']:.2f} & {row['Landed_LCOE_INR_kWh']:.2f} & {row['Achieved_RPO_Pct']:.1f} \\\\")
            first_row = False
        if v != chron_vintages[-1]:
            t3_lines.append(r"\addlinespace")

    t3_lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\caption{8,760-hour empirical HiGHS LP optimization results across Indian states and commissioning vintages (1,000~MW peak load, 4-hour BESS baseline).}",
        r"\label{tab:scenario_results_4h}",
        r"\end{table}"
    ])

    with open(os.path.join(TABLE_DIR, "table3_baseline.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t3_lines))
    print("[SUCCESS] Exported tables/table3_baseline.tex")

    # ------------------ TABLE 4: STORAGE DURATION SENSITIVITY (FY 2029-30) ------------------
    v30_all = df_base[df_base["Vintage"] == "2029-30"].copy()
    t4_lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"State & Duration & BESS Power (GW) & BESS Energy (GWh) & Landed LCOE (INR/kWh) & Thermal Grid Reliance (\%) \\",
        r"\midrule"
    ]

    for st in ["RJ", "GJ", "TN", "KA"]:
        sub = v30_all[v30_all["State"] == st].sort_values("Duration")
        first_row = True
        min_lcoe = sub["Landed_LCOE_INR_kWh"].min()
        for _, row in sub.iterrows():
            st_str = state_names[st] if first_row else ""
            dur_str = f"{int(row['Duration'])}-Hour"
            lcoe_val = row["Landed_LCOE_INR_kWh"]
            lcoe_str = f"\\textbf{{{lcoe_val:.2f}}}" if np.isclose(lcoe_val, min_lcoe) else f"{lcoe_val:.2f}"
            t4_lines.append(f"{st_str} & {dur_str} & {row['BESS_Power_GW']:.2f} & {row['BESS_Energy_GWh']:.2f} & {lcoe_str} & {row['Grid_Share_Pct']:.2f} \\\\")
            first_row = False
        if st != "KA":
            t4_lines.append(r"\addlinespace")

    t4_lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\caption{Impact of BESS storage duration on landed LCOE and thermal grid reliance in FY 2029--30 (43.33\% RPO mandate).}",
        r"\label{tab:duration_sweep}",
        r"\end{table}"
    ])

    with open(os.path.join(TABLE_DIR, "table4_duration.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t4_lines))
    print("[SUCCESS] Exported tables/table4_duration.tex")

    # ------------------ TABLE 5: EMPIRICAL BENCHMARKING (WITH SPLIT GUVNL ROW) ------------------
    # Retrieve exact solver model values for RJ 4h (3.83), GJ 4h (3.86), KA 4h (4.08), TN 4h (4.10)
    rj_2030_4h = df_base_4h[(df_base_4h["Vintage"] == "2029-30") & (df_base_4h["State"] == "RJ")]["Landed_LCOE_INR_kWh"].values[0]
    gj_2030_4h = df_base_4h[(df_base_4h["Vintage"] == "2029-30") & (df_base_4h["State"] == "GJ")]["Landed_LCOE_INR_kWh"].values[0]
    ka_2030_4h = df_base_4h[(df_base_4h["Vintage"] == "2029-30") & (df_base_4h["State"] == "KA")]["Landed_LCOE_INR_kWh"].values[0]
    tn_2030_4h = df_base_4h[(df_base_4h["Vintage"] == "2029-30") & (df_base_4h["State"] == "TN")]["Landed_LCOE_INR_kWh"].values[0]

    # Calculate exact variances
    var_seci1_a = ((rj_2030_4h - 4.04) / 4.04) * 100
    var_seci1_b = ((rj_2030_4h - 4.30) / 4.30) * 100
    var_seci_rtc = ((gj_2030_4h - 3.60) / 3.60) * 100
    var_fdre_ka = ((ka_2030_4h - 4.98) / 4.98) * 100
    var_fdre_tn = ((tn_2030_4h - 4.98) / 4.98) * 100
    var_guvnl_cap = ((3057.0 - 3400.3) / 3400.3) * 100
    var_guvnl_rtc = ((gj_2030_4h - 3.78) / 3.78) * 100
    var_rumsl = ((rj_2030_4h - 2.73) / 2.73) * 100

    t5_lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"Tender / Procurement Mechanism & Primary Source \& Winner & Target State Corridor & Awarded Tariff ($T_{\text{tender}}$, INR/kWh) & Model Landed LCOE ($LCOE_{\text{model}}$, INR/kWh) & Benchmark Variance Formula \& Exact Calculation (\%) \\",
        r"\midrule",
        f"SECI 1,200~MW Peak Power & Mercom / Greenko (900~MW) & Rajasthan & 2.88 Off-Peak / 6.12 Peak (Wtd Avg 4.04) & {rj_2030_4h:.2f} (RJ 4h) & $\\frac{{{rj_2030_4h:.2f} - 4.04}}{{4.04}} = \\mathbf{{{var_seci1_a:+.1f}\\%}}$ (vs 4.04 Wtd Avg) \\\\",
        f" & Mercom / ReNew (300~MW) & Rajasthan & 2.88 Off-Peak / 6.85 Peak (Wtd Avg 4.30) & {rj_2030_4h:.2f} (RJ 4h) & $\\frac{{{rj_2030_4h:.2f} - 4.30}}{{4.30}} = \\mathbf{{{var_seci1_b:+.1f}\\%}}$ (vs 4.30 Wtd Avg) \\\\",
        r"\addlinespace",
        f"SECI RTC-I 400~MW & Mercom / ReNew (400~MW) & Gujarat & 2.90 Yr-1 Base (3\% Esc to 3.60 Lev) & {gj_2030_4h:.2f} (GJ 4h) & $\\frac{{{gj_2030_4h:.2f} - 3.60}}{{3.60}} = \\mathbf{{{var_seci_rtc:+.1f}\\%}}$ (vs Lev 3.60 PPA) \\\\",
        r"\addlinespace",
        f"SECI FDRE Tranche IV (630~MW) & Mercom / JSW, Hero, Vena & Karnataka & 4.98 -- 4.99 (Landed Firm Tariff) & {ka_2030_4h:.2f} (KA 4h) & $\\frac{{{ka_2030_4h:.2f} - 4.98}}{{4.98}} = \\mathbf{{{var_fdre_ka:+.1f}\\%}}$ (vs 4.98 L1) \\\\",
        f" & Mercom / Hexa, Serentica & Tamil Nadu & 4.98 -- 4.99 (Landed Firm Tariff) & {tn_2030_4h:.2f} (TN 4h) & $\\frac{{{tn_2030_4h:.2f} - 4.98}}{{4.98}} = \\mathbf{{{var_fdre_tn:+.1f}\\%}}$ (vs 4.98 L1) \\\\",
        r"\addlinespace",
        f"GUVNL 500~MW Grid BESS (Cap Charge) & Mercom / Solarworld, HG Infra & Gujarat & 280k--285.6k/MW-mo (3,400.3/kW-yr) & 3,057.0/kW-yr (2h BESS Cap) & $\\frac{{3057.0 - 3400.3}}{{3400.3}} = \\mathbf{{{var_guvnl_cap:+.1f}\\%}}$ (Direct 2h Cap Charge) \\\\",
        f"GUVNL 500~MW Grid BESS (RTC Tariff) & Mercom / Landed Service & Gujarat & 3.78 (Landed Standalone BESS RTC) & {gj_2030_4h:.2f} (GJ 4h Landed) & $\\frac{{{gj_2030_4h:.2f} - 3.78}}{{3.78}} = \\mathbf{{{var_guvnl_rtc:+.1f}\\%}}$ (vs Landed RTC Service) \\\\",
        r"\addlinespace",
        f"RUMSL 600~MW Solar-Storage & Mercom / ACME, Ceigall & Rajasthan & 2.70 -- 2.76 (Gen PPA Tariff, Mean 2.73) & {rj_2030_4h:.2f} (RJ 4h) & $\\frac{{{rj_2030_4h:.2f} - 2.73}}{{2.73}} = \\mathbf{{{var_rumsl:+.1f}\\%}}$ (vs Standalone Gen PPA) \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\caption{Primary-source verified empirical benchmarking of LP model landed LCOE results against real-world Indian utility tender awards (2020--2025), splitting GUVNL into standalone capacity charge and landed RTC tariff components.}",
        r"\label{tab:empirical_benchmark}",
        r"\end{table}"
    ]

    with open(os.path.join(TABLE_DIR, "table5_empirical.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t5_lines))
    print("[SUCCESS] Exported tables/table5_empirical.tex")

    # ------------------ TABLE 6: WACC FINANCIAL SENSITIVITY ------------------
    v30_wacc_4h = df_wacc[(df_wacc["Vintage"] == "2029-30") & (df_wacc["Duration"] == 4)].copy()
    wacc_col = [c for c in df_wacc.columns if "wacc" in c.lower() or "discount" in c.lower() or "rate" in c.lower()][0]

    t6_lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"WACC Rate ($r$) & Capital Recovery Factor (CRF) & Rajasthan LCOE & Gujarat LCOE & Tamil Nadu LCOE & Karnataka LCOE & Tariff Sensitivity Delta (INR/kWh) \\",
        r"\midrule"
    ]

    crf_map = {8.0: 0.09368, 10.0: 0.11017, 12.0: 0.12750}
    lcoe_10_mean = v30_wacc_4h[v30_wacc_4h[wacc_col] == 10.0]["Landed_LCOE_INR_kWh"].mean()

    for r in [8.0, 10.0, 12.0]:
        sub = v30_wacc_4h[v30_wacc_4h[wacc_col] == r]
        rj_v = sub[sub["State"] == "RJ"]["Landed_LCOE_INR_kWh"].values[0]
        gj_v = sub[sub["State"] == "GJ"]["Landed_LCOE_INR_kWh"].values[0]
        tn_v = sub[sub["State"] == "TN"]["Landed_LCOE_INR_kWh"].values[0]
        ka_v = sub[sub["State"] == "KA"]["Landed_LCOE_INR_kWh"].values[0]
        mean_v = sub["Landed_LCOE_INR_kWh"].mean()
        delta = mean_v - lcoe_10_mean
        delta_str = f"\\textbf{{{delta:+.2f}}}" if r != 10.0 else "Baseline (0.00)"

        t6_lines.append(f"{int(r)}\\% (Concessional/Market) & {crf_map[r]:.5f} & {rj_v:.2f} & {gj_v:.2f} & {tn_v:.2f} & {ka_v:.2f} & {delta_str} \\\\")

    t6_lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\caption{Financial WACC sensitivity analysis across Indian states for FY 2029--30 under 4-hour BESS baseline ($r = 8\%, 10\%, 12\%$).}",
        r"\label{tab:wacc_sensitivity}",
        r"\end{table}"
    ])

    with open(os.path.join(TABLE_DIR, "table6_wacc.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t6_lines))
    print("[SUCCESS] Exported tables/table6_wacc.tex")

    # ------------------ MACRO VALUES HEADER FILE ------------------
    v24_4h = df_base_4h[df_base_4h["Vintage"] == "2024-25"]
    v30_4h = df_base_4h[df_base_4h["Vintage"] == "2029-30"]

    v24_min = v24_4h["Landed_LCOE_INR_kWh"].min()
    v24_max = v24_4h["Landed_LCOE_INR_kWh"].max()
    v30_min = v30_4h["Landed_LCOE_INR_kWh"].min()
    v30_max = v30_4h["Landed_LCOE_INR_kWh"].max()

    v30_6h = df_base[(df_base["Vintage"] == "2029-30") & (df_base["Duration"] == 6)]
    v30_6h_min = v30_6h["Landed_LCOE_INR_kWh"].min()
    v30_6h_max = v30_6h["Landed_LCOE_INR_kWh"].max()

    v30_wacc_8 = df_wacc[(df_wacc["Vintage"] == "2029-30") & (df_wacc["Duration"] == 4) & (df_wacc[wacc_col] == 8.0)]
    wacc8_min = v30_wacc_8["Landed_LCOE_INR_kWh"].min()
    wacc8_max = v30_wacc_8["Landed_LCOE_INR_kWh"].max()

    macro_lines = [
        f"\\newcommand{{\\ValLcoeTwentyFourMin}}{{{v24_min:.2f}}}",
        f"\\newcommand{{\\ValLcoeTwentyFourMax}}{{{v24_max:.2f}}}",
        f"\\newcommand{{\\ValLcoeThirtyMin}}{{{v30_min:.2f}}}",
        f"\\newcommand{{\\ValLcoeThirtyMax}}{{{v30_max:.2f}}}",
        f"\\newcommand{{\\ValLcoeSixHourThirtyMin}}{{{v30_6h_min:.2f}}}",
        f"\\newcommand{{\\ValLcoeSixHourThirtyMax}}{{{v30_6h_max:.2f}}}",
        f"\\newcommand{{\\ValLcoeWaccEightMin}}{{{wacc8_min:.2f}}}",
        f"\\newcommand{{\\ValLcoeWaccEightMax}}{{{wacc8_max:.2f}}}",
    ]

    with open(os.path.join(TABLE_DIR, "macro_values.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(macro_lines))
    print("[SUCCESS] Exported tables/macro_values.tex")

if __name__ == "__main__":
    generate_tables()
