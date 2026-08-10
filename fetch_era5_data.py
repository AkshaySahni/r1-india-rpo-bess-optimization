# -*- coding: utf-8 -*-
"""
Input Data Fetching & Preprocessing Pipeline for India RPO 8,760 LP Optimization.
Primary Data Sources & Provenance:
----------------------------------
1. ECMWF ERA5 Global Reanalysis (2021-2023): Hourly Surface Solar Radiation Downwards (ssrd)
   and 100m Wind Components (u100, v100) via Copernicus Climate Data Store (CDS) API.
2. NREL System Advisor Model (SAM): Performance loss factors and solar/wind power curves.
3. Zenodo DOI: 10.5281/zenodo.14983362 (Daily State Energy Met E_{s,d} and Peak Met P_{s,d}, 2014-2024)
4. Mendeley Data DOI: 10.17632/y58jknpgs8.2 (1-Hour Regional Demand Met Load Shapes S_{r,t}, 2021-2023)
5. Ministry of Power (MoP) / CERC Benchmark Orders: CAPEX & O&M cost trajectory (Table 2).
"""

import os
import json
import numpy as np
import pandas as pd

TABLE2_COST_TRAJECTORY = {
    "units": {
        "CAPEX": "USD/kW (1 USD = 83.5 INR)",
        "Fixed_O_and_M": "INR/MW-year",
        "WACC": "10.0%",
        "Lifetime": "25 years",
        "CRF": 0.11017
    },
    "trajectory": {
        "2024-25": {"Solar_USD_kW": 480, "Wind_USD_kW": 880, "BESS_Pwr_USD_kW": 180, "BESS_Eng_USD_kWh": 125},
        "2025-26": {"Solar_USD_kW": 450, "Wind_USD_kW": 850, "BESS_Pwr_USD_kW": 165, "BESS_Eng_USD_kWh": 112},
        "2026-27": {"Solar_USD_kW": 420, "Wind_USD_kW": 820, "BESS_Pwr_USD_kW": 150, "BESS_Eng_USD_kWh": 102},
        "2027-28": {"Solar_USD_kW": 390, "Wind_USD_kW": 790, "BESS_Pwr_USD_kW": 135, "BESS_Eng_USD_kWh": 90},
        "2028-29": {"Solar_USD_kW": 370, "Wind_USD_kW": 770, "BESS_Pwr_USD_kW": 125, "BESS_Eng_USD_kWh": 82},
        "2029-30": {"Solar_USD_kW": 350, "Wind_USD_kW": 750, "BESS_Pwr_USD_kW": 115, "BESS_Eng_USD_kWh": 75}
    },
    "fixed_om": {
        "Solar_INR_MW_yr": 500000.0,
        "Wind_INR_MW_yr": 1200000.0,
        "BESS_Pwr_INR_MW_yr": 300000.0
    },
    "state_coordinates": {
        "Rajasthan": {"lat": 27.0, "lon": 71.0, "zone": "Bhadla Solar Park"},
        "Gujarat": {"lat": 23.5, "lon": 71.5, "zone": "Khavda Renewable Park"},
        "Tamil Nadu": {"lat": 9.2, "lon": 78.4, "zone": "Kamuthi/Muppandal Zone"},
        "Karnataka": {"lat": 14.2, "lon": 77.4, "zone": "Pavagada Solar Park"}
    }
}

def export_table2_json(output_path="input_data/cost_trajectory_table2.json"):
    """Exports Table 2 CAPEX and O&M benchmark trajectory into machine-readable JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(TABLE2_COST_TRAJECTORY, f, indent=4)
    print(f"[OK] Exported machine-readable Table 2 cost trajectory to: {output_path}")

def fetch_era5_reanalysis_data(years=[2021, 2022, 2023], output_dir="input_data/era5"):
    """
    Downloads raw ECMWF ERA5 100m wind speed and surface solar radiation downwards (ssrd)
    reanalysis NetCDF files via Copernicus Climate Data Store (CDS) API.
    """
    os.makedirs(output_dir, exist_ok=True)
    try:
        import cdsapi
        c = cdsapi.Client()
        print(f"[INFO] Connected to Copernicus CDS API. Requesting ERA5 reanalysis for years: {years}...")
        for year in years:
            target = os.path.join(output_dir, f"era5_india_{year}.nc")
            if os.path.exists(target):
                print(f"[SKIP] {target} already exists.")
                continue
            c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '100m_u_component_of_wind',
                        '100m_v_component_of_wind',
                        'surface_solar_radiation_downwards',
                    ],
                    'year': str(year),
                    'month': [f'{m:02d}' for m in range(1, 13)],
                    'day': [f'{d:02d}' for d in range(1, 32)],
                    'time': [f'{h:02d}:00' for h in range(0, 24)],
                    'area': [28.0, 68.0, 8.0, 79.0],
                    'format': 'netcdf',
                },
                target
            )
            print(f"[OK] Downloaded ERA5 NetCDF: {target}")
    except Exception as e:
        print(f"[NOTE] CDS API client unavailable or credentials key missing (~/.cdsapirc): {e}")
        print("[INFO] Run 'pip install cdsapi' and setup ~/.cdsapirc key to execute live CDS API downloads.")

if __name__ == "__main__":
    export_table2_json()
    fetch_era5_reanalysis_data()
