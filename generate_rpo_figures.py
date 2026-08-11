# -*- coding: utf-8 -*-
"""
Publication-Quality Figure Generation Script for India RPO 8760 Optimization Paper.
Target Journal: Elsevier Applied Energy / Renewable Energy (Scopus Q1)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configure publication style
plt.style.use('seaborn-v0_8-paper' if 'seaborn-v0_8-paper' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9.5
plt.rcParams['figure.titlesize'] = 13
plt.rcParams['savefig.dpi'] = 300

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

def generate_all_figures():
    csv_path = "rpo_scenario_results_8760.csv"
    sens_csv_path = "rpo_bess_degradation_sensitivity.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return
        
    df = pd.read_csv(csv_path)
    
    # Define strict chronological vintage order mapping
    chron_vintages = ["2024-25", "2025-26", "2026-27", "2027-28", "2028-29", "2029-30"]
    vintage_order = {v: i for i, v in enumerate(chron_vintages)}
    
    # Filter 4-hour BESS baseline safely using np.isclose
    df["Duration_Calc"] = df["BESS_Energy_GWh"] / np.maximum(1e-3, df["BESS_Power_GW"])
    df_4h = df[np.isclose(df["Duration_Calc"], 4.0, atol=0.1)].copy()
    df_4h["Sort_Key"] = df_4h["Vintage"].map(vintage_order)
    
    states = ["RJ", "GJ", "TN", "KA"]
    state_names = {"RJ": "Rajasthan", "GJ": "Gujarat", "TN": "Tamil Nadu", "KA": "Karnataka"}
    colors = {"RJ": "#e41a1c", "GJ": "#377eb8", "TN": "#4daf4a", "KA": "#984ea3"}
    markers = {"RJ": "o", "GJ": "s", "TN": "^", "KA": "d"}
    
    # ------------------ FIGURE 1: LANDED LCOE TRAJECTORY ------------------
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for st in states:
        sub = df_4h[df_4h["State"] == st].sort_values("Sort_Key")
        ax.plot(sub["Vintage"], sub["Landed_LCOE_INR_kWh"], 
                label=f"{state_names[st]} Corridor", 
                color=colors[st], marker=markers[st], linewidth=2.2, markersize=7)
                
    ax.axhline(y=10.0, color="black", linestyle="--", alpha=0.7, linewidth=1.5, label="Statutory REC Penalty (10.00 INR/kWh)")
    ax.set_title("Landed LCOE Trajectory across Statutory RPO Vintages (4-Hour BESS Baseline)")
    ax.set_xlabel("RPO Mandate Financial Year Vintage")
    ax.set_ylabel("Landed Levelized Cost of Electricity (INR/kWh)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig1_rpo_trajectory_lcoe.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig1_rpo_trajectory_lcoe.png"))
    plt.close(fig)
    print("Saved Figure 1: Landed LCOE Trajectory")

    # ------------------ FIGURE 2: CAPACITY MIX EXPANSION (GW) ------------------
    fig, ax = plt.subplots(figsize=(9.5, 5))
    rj_sub = df_4h[df_4h["State"] == "RJ"].sort_values("Sort_Key")
    
    x = np.arange(len(rj_sub))
    width = 0.25
    
    ax.bar(x - width, rj_sub["Solar_GW"], width, label="Utility Solar PV (GW)", color="#fdb863")
    ax.bar(x, rj_sub["Wind_GW"], width, label="Onshore Wind (GW)", color="#2b83ba")
    ax.bar(x + width, rj_sub["BESS_Power_GW"], width, label="BESS Power Capacity (GW)", color="#abdda4")
    
    ax.set_xticks(x)
    ax.set_xticklabels(rj_sub["Vintage"])
    ax.set_title("Optimal Hybrid Capacity Build-out for 1,000 MW Peak DISCOM Load (Rajasthan Corridor)")
    ax.set_xlabel("RPO Mandate Vintage")
    ax.set_ylabel("Installed Capacity (GW)")
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig2_capacity_mix_expansion.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig2_capacity_mix_expansion.png"))
    plt.close(fig)
    print("Saved Figure 2: Capacity Mix Expansion")

    # ------------------ FIGURE 3: HOURLY DISPATCH CURVES (48-HOUR SAMPLE) ------------------
    from highs_rpo_solver import generate_8760_profiles
    solar_prof, wind_prof, demand_prof = generate_8760_profiles(state="RJ")
    
    h_win = range(3600, 3648)
    t_win = np.arange(48)
    peak_mw = 1000.0
    s_mw, w_mw = 2250.0, 350.0
    
    s_gen = solar_prof[h_win] * s_mw
    w_gen = wind_prof[h_win] * w_mw
    d_mw = demand_prof[h_win] * peak_mw
    
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.plot(t_win, d_mw, 'k--', linewidth=2.2, label='DISCOM Demand (MW)')
    ax.stackplot(t_win, s_gen, w_gen, labels=['Solar PV Generation (MW)', 'Onshore Wind Generation (MW)'],
                 colors=['#fdb863', '#2b83ba'], alpha=0.85)
                 
    ax.set_title("Representative 48-Hour Operational Dispatch (Rajasthan FY 2029-30 Baseline)")
    ax.set_xlabel("Time (Hours)")
    ax.set_ylabel("Power (MW)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc='upper right', frameon=True, facecolor="white", framealpha=0.9)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig3_hourly_dispatch.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig3_hourly_dispatch.png"))
    plt.close(fig)
    print("Saved Figure 3: Hourly Dispatch Profiles")

    # ------------------ FIGURE 4: STORAGE DURATION SENSITIVITY ------------------
    fig, ax = plt.subplots(figsize=(8.5, 5))
    df_2030 = df[df["Vintage"] == "2029-30"]
    
    for st in states:
        sub = df_2030[df_2030["State"] == st]
        durations = sub["BESS_Energy_GWh"] / np.maximum(1e-3, sub["BESS_Power_GW"])
        sub_sorted = sub.assign(dur=durations).sort_values("dur")
        ax.plot(sub_sorted["dur"], sub_sorted["Landed_LCOE_INR_kWh"], marker=markers[st],
                color=colors[st], linewidth=2.0, markersize=7, label=state_names[st])
                
    ax.set_title("Landed LCOE Sensitivity to Battery Storage Duration (FY 2029-30, 43.3% RPO Mandate)")
    ax.set_xlabel("BESS Duration (Hours at Rated Power)")
    ax.set_ylabel("Landed LCOE (INR / kWh)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig4_storage_duration_sensitivity.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig4_storage_duration_sensitivity.png"))
    plt.close(fig)
    print("Saved Figure 4: Storage Duration Sensitivity")

    # ------------------ FIGURE 5: POLICY FEASIBILITY HEATMAP ------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Policy Feasibility Space: Landed LCOE vs. Thermal Grid Reliance (2024-30)', fontsize=13, fontweight='bold', y=1.01)

    ax1, ax2 = axes
    for st in states:
        sd = df[df.State == st]
        ax1.scatter(sd.Grid_Share_Pct, sd.Landed_LCOE_INR_kWh, 
                    c=[colors[st]]*len(sd), s=80, alpha=0.7, label=state_names[st], zorder=3)

    ax1.axhline(y=10.0, color='red', linestyle='--', alpha=0.7, linewidth=1.5, label='Statutory REC penalty (10 INR/kWh)')
    ax1.axhline(y=6.0, color='orange', linestyle=':', alpha=0.7, linewidth=1.5, label='Avg. retail tariff (6 INR/kWh)')
    ax1.axvline(x=5.0, color='gray', linestyle='--', alpha=0.5, linewidth=1.2, label='5% grid limit threshold')
    ax1.set_xlabel('Thermal Grid Reliance (%)', fontsize=11)
    ax1.set_ylabel('Landed LCOE (INR/kWh)', fontsize=11)
    ax1.set_title('(a) All Scenarios: LCOE vs. Thermal Reliance', fontsize=11)
    ax1.legend(fontsize=8, loc='upper right')
    ax1.grid(True, alpha=0.3)

    df2930 = df[df.Vintage == '2029-30'].copy()
    df2930["dur_rank"] = df2930.groupby(['Vintage','State']).cumcount()
    pivot = df2930.pivot_table(index='State', columns='dur_rank', values='Landed_LCOE_INR_kWh')
    pivot.index = [state_names[s] for s in pivot.index]
    pivot.columns = ['2h BESS', '4h BESS', '6h BESS', '8h BESS']
    im = ax2.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto', vmin=3.3, vmax=5.0)
    ax2.set_xticks(range(4)); ax2.set_xticklabels(pivot.columns, fontsize=10)
    ax2.set_yticks(range(4)); ax2.set_yticklabels(pivot.index, fontsize=10)
    for i in range(4):
        for j in range(4):
            ax2.text(j, i, f'{pivot.values[i,j]:.2f}', ha='center', va='center', fontsize=11, fontweight='bold')
    ax2.set_title('(b) FY 2029-30 Landed LCOE Heatmap (INR/kWh)\nby State and BESS Duration', fontsize=11)
    plt.colorbar(im, ax=ax2, label='Landed LCOE (INR/kWh)', shrink=0.8)

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig5_policy_feasibility_heatmap.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig5_policy_feasibility_heatmap.png"))
    plt.close(fig)
    print("Saved Figure 5: Policy Feasibility Heatmap")

    # ------------------ FIGURE 6: BESS DEGRADATION & LIFESPAN SENSITIVITY ------------------
    if os.path.exists(sens_csv_path):
        df_sens = pd.read_csv(sens_csv_path)
        fig, ax = plt.subplots(figsize=(9, 5.5))
        
        # Filter for FY 2029-30 4-hour BESS across states and replacement lifespans
        df_sens_4h = df_sens[(df_sens["Vintage"] == "2029-30") & (df_sens["BESS_Power_GW"] > 0)].copy()
        df_sens_4h["Duration_Calc"] = df_sens_4h["BESS_Energy_GWh"] / np.maximum(1e-3, df_sens_4h["BESS_Power_GW"])
        df_sub = df_sens_4h[np.isclose(df_sens_4h["Duration_Calc"], 4.0, atol=0.2)].copy()
        
        penalties = [0.0, 400.0, 800.0]
        pen_labels = {0.0: "Zero Degradation Penalty (₹0/MWh)", 
                      400.0: "Baseline Degradation Penalty (₹400/MWh)", 
                      800.0: "High Degradation Penalty (₹800/MWh)"}
        pen_styles = {0.0: "--", 400.0: "-", 800.0: ":"}
        
        for pen in penalties:
            p_df = df_sub[(df_sub["State"] == "RJ") & (df_sub["Throughput_Penalty_INR_MWh"] == pen)].sort_values("BESS_Replace_Years")
            if not p_df.empty:
                ax.plot(p_df["BESS_Replace_Years"], p_df["Landed_LCOE_INR_kWh"], 
                        marker="o", linewidth=2.2, linestyle=pen_styles[pen], label=pen_labels[pen])
                        
        ax.set_title("Landed LCOE Sensitivity to BESS Cell Stack Replacement Lifespan & Wear Penalties (Rajasthan 2029-30)")
        ax.set_xlabel("BESS Stack Replacement Horizon (Calendar Years)")
        ax.set_ylabel("Landed Levelized Cost of Electricity (INR/kWh)")
        ax.set_xticks([7, 10, 13])
        ax.set_xticklabels(["7 Years\n(~2,800 Cycles)", "10 Years\n(~4,000 Cycles)", "13 Years\n(~5,200 Cycles)"])
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(frameon=True, facecolor="white", framealpha=0.9)
        plt.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, "fig6_bess_degradation_sensitivity.pdf"))
        fig.savefig(os.path.join(FIG_DIR, "fig6_bess_degradation_sensitivity.png"))
        plt.close(fig)
        print("Saved Figure 6: BESS Degradation & Lifespan Sensitivity")

        # ------------------ FIGURE 7: MULTI-YEAR WEATHER INTER-ANNUAL VARIABILITY ------------------
        weather_csv_path = "rpo_multiyear_weather_sensitivity.csv"
        if os.path.exists(weather_csv_path):
            df_weather = pd.read_csv(weather_csv_path)
            fig, ax = plt.subplots(figsize=(9.5, 5.5))
            
            # Filter for FY 2029-30 4-hour BESS
            df_w4h = df_weather[(df_weather["Vintage"] == "2029-30")].copy()
            df_w4h["Duration_Calc"] = df_w4h["BESS_Energy_GWh"] / np.maximum(1e-3, df_w4h["BESS_Power_GW"])
            df_wsub = df_w4h[np.isclose(df_w4h["Duration_Calc"], 4.0, atol=0.2)].copy()
            
            years = [2021, 2022, 2023]
            df_wsub = df_wsub[df_wsub["Weather_Year"].isin(years)].copy()
            for st in states:
                st_data = df_wsub[df_wsub["State"] == st].sort_values("Weather_Year")
                if not st_data.empty:
                    mean_val = st_data['Landed_LCOE_INR_kWh'].mean()
                    min_val = st_data['Landed_LCOE_INR_kWh'].min()
                    max_val = st_data['Landed_LCOE_INR_kWh'].max()
                    y_err = [[mean_val - min_val] * len(st_data), [max_val - mean_val] * len(st_data)]
                    ax.errorbar(st_data["Weather_Year"], st_data["Landed_LCOE_INR_kWh"], 
                                yerr=y_err, fmt="-s", capsize=5, capthick=1.5, linewidth=2.2, 
                                color=colors[st], label=f"{state_names[st]} (Mean = ₹{mean_val:.2f}, Range [{min_val:.2f}-{max_val:.2f}])")
                    ax.fill_between(st_data["Weather_Year"], min_val, max_val, color=colors[st], alpha=0.10)
                            
            ax.set_title("Inter-Annual Landed LCOE Robustness Across 3 Historical Weather Calendar Years (FY 2029-30, 4h BESS)")
            ax.set_xlabel("Weather Calendar Year")
            ax.set_ylabel("Landed Levelized Cost of Electricity (INR/kWh)")
            ax.set_xticks(years)
            ax.set_xticklabels(["2021\n(Normal Ref)", "2022\n(Monsoon Surge)", "2023\n(El Niño Drought)"])
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.legend(frameon=True, facecolor="white", framealpha=0.9, fontsize=9.5)
            plt.tight_layout()
            fig.savefig(os.path.join(FIG_DIR, "fig7_interannual_weather_variability.pdf"))
            fig.savefig(os.path.join(FIG_DIR, "fig7_interannual_weather_variability.png"))
            plt.close(fig)
            print("Saved Figure 7: Multi-Year Weather Inter-Annual Variability with Error Bars & Range Shading")

        # ------------------ FIGURE 8 [NEW]: LCOE DISTRIBUTION BOXPLOT ACROSS ALL 288 SCENARIOS ------------------
        all_lcoes = []
        # Aggregate across base, degradation, weather, and wacc CSVs
        for path in ["rpo_scenario_results_8760.csv", "rpo_bess_degradation_sensitivity.csv", 
                     "rpo_multiyear_weather_sensitivity.csv", "rpo_wacc_financial_sensitivity.csv"]:
            if os.path.exists(path):
                f_df = pd.read_csv(path)
                if "Landed_LCOE_INR_kWh" in f_df.columns and "State" in f_df.columns:
                    all_lcoes.append(f_df[["State", "Landed_LCOE_INR_kWh"]])
        
        if all_lcoes:
            df_all_scenarios = pd.concat(all_lcoes, ignore_index=True)
            fig, ax = plt.subplots(figsize=(9.5, 5.5))
            data_to_plot = [df_all_scenarios[df_all_scenarios["State"] == st]["Landed_LCOE_INR_kWh"].dropna().values for st in states]
            
            bp = ax.boxplot(data_to_plot, patch_artist=True, tick_labels=[state_names[st] for st in states],
                            medianprops=dict(color="black", linewidth=2.0),
                            whiskerprops=dict(linewidth=1.5),
                            capprops=dict(linewidth=1.5))
            
            for patch, st in zip(bp['boxes'], states):
                patch.set_facecolor(colors[st])
                patch.set_alpha(0.65)
                
            ax.set_title("Landed LCOE Distribution Across All 288 Solved Policy & Technical Scenarios")
            ax.set_xlabel("State Renewable Corridor")
            ax.set_ylabel("Landed Levelized Cost of Electricity (INR/kWh)")
            ax.grid(True, linestyle="--", alpha=0.4)
            
            # Annotate medians
            for i, st in enumerate(states, start=1):
                vals = df_all_scenarios[df_all_scenarios["State"] == st]["Landed_LCOE_INR_kWh"].dropna()
                med = vals.median()
                ax.text(i, med + 0.08, f"Med: ₹{med:.2f}", horizontalalignment='center', fontsize=9.5, fontweight='bold')
                
            plt.tight_layout()
            fig.savefig(os.path.join(FIG_DIR, "fig8_lcoe_distribution_boxplot.pdf"))
            fig.savefig(os.path.join(FIG_DIR, "fig8_lcoe_distribution_boxplot.png"))
            plt.close(fig)
            print("Saved Figure 8: LCOE Distribution Boxplot across 288 Scenarios")

if __name__ == "__main__":
    generate_all_figures()


