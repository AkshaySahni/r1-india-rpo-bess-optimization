# Techno-Economic Optimization of Hybrid Wind–Solar–Storage Systems under India’s Renewable Purchase Obligations

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Solver: SciPy HiGHS](https://img.shields.io/badge/Solver-SciPy%20HiGHS%20C%2B%2B-green.svg)](https://highs.dev/)

This repository provides the complete, auditable code and data reproducibility pipeline for the 8,760-hour annual Mixed-Integer Linear Programming (MILP) optimization model of hybrid wind–solar–battery energy storage systems (BESS) under India’s statutory Renewable Purchase Obligation (RPO) trajectory.

---

## 📌 Repository Scope & Exclusions

> **Note on Repository Contents**: This repository is dedicated exclusively to **code, raw input preprocessing, optimization solvers, diagnostic logs, and scenario datasets**. 

---

## 📁 Repository Directory Structure

```
.
├── highs_rpo_solver.py                    # Core SciPy HiGHS 8,760-hour MILP matrix optimization engine & profile generator
├── run_rpo_scenarios_parallel.py         # Parallel multi-core scenario execution runner across 96/144/80 scenario sweeps
├── generate_rpo_figures.py               # Rendering pipeline to regenerate publication Figures 1 to 7 from result CSVs
├── fetch_era5_data.py                    # Input data preprocessing script & ECMWF CDS API downloader pipeline
├── rpo_scenario_results_8760.csv         # Complete baseline 8,760-hour scenario results dataset (96 runs)
├── rpo_bess_degradation_sensitivity.csv    # BESS throughput degradation & stack replacement sensitivity dataset (144 runs)
├── rpo_multiyear_weather_sensitivity.csv   # Multi-year ERA5 weather reanalysis sensitivity dataset (2019-2023, 80 runs)
├── solver_diagnostics.log                # Matrix dimension logs, variable breakdown, and C++ HiGHS solver benchmarks
├── input_data/                           # Machine-readable input configuration parameters
│   └── cost_trajectory_table2.json       # Table 2 CAPEX, fixed O&M, WACC, and state coordinates in JSON format
├── figures/                              # Subdirectory containing vector (.pdf) and raster (.png) publication figures
├── requirements.txt                      # Pinned Python package dependencies
├── LICENSE                               # MIT Open Source License
└── .gitignore                            # Standard Python gitignore rules
```

---

## 🌐 Data Provenance & Fetching Raw Data

The optimization model relies on auditable public datasets:

1. **ECMWF ERA5 Global Reanalysis (2019–2023)**: Hourly surface solar radiation downwards (`ssrd`) and 100m wind vectors (`u100`, `v100`) for Indian renewable zones:
   - **Rajasthan (RJ)**: 27.0°N, 71.0°E (Bhadla Solar Park zone)
   - **Gujarat (GJ)**: 23.5°N, 71.5°E (Khavda Renewable Park zone)
   - **Tamil Nadu (TN)**: 9.2°N, 78.4°E (Kamuthi/Muppandal wind-solar zone)
   - **Karnataka (KA)**: 14.2°N, 77.4°E (Pavagada Solar Park zone)
2. **NREL System Advisor Model (SAM)**: Performance loss derates and power curves.
3. **Grid-India (POSOCO) Utility Telemetry**: Hourly DISCOM load curves normalized to 1,000 MW peak demand.
4. **Table 2 Machine-Readable Cost Trajectory**: Stored in `input_data/cost_trajectory_table2.json`.

### Fetching ERA5 Reanalysis via CDS API

Due to ECMWF license redistribution terms, raw netCDF reanalysis files are fetched on-demand using Copernicus Climate Data Store (CDS) API:

```bash
# Register at https://cds.climate.copernicus.eu/ and setup ~/.cdsapirc key, then run:
python fetch_era5_data.py
```

---

## ⚡ Solver Performance & Diagnostic Logs

Detailed matrix dimensions and performance logs are recorded in `solver_diagnostics.log`:

- **Problem Dimensions**: $N_{\text{variables}} = 70,085$, $N_{\text{constraints}} = 78,843$ (Sparse matrix sparsity > 99.95%).
- **Solver Engine**: SciPy `linprog` (method=`highs`) wrapping C++ HiGHS Dual Simplex/Barrier engine.
- **Optimality Gap**: $0.00\%$ ($10^{-6}$ absolute feasibility tolerance).
- **Execution Benchmark**: Average solve time = **0.182 s ± 0.015 s per scenario** (~12.5 s for full 96-scenario baseline sweep across 8 CPU cores).

---

## 💻 Quick Start & Reproduction Guide

### 1. Environment Setup

Install pinned dependencies:

```bash
pip install -r requirements.txt
```

### 2. Export Input Data & Fetch Profiles

```bash
python fetch_era5_data.py
```

### 3. Execute Parallel Scenario Optimization

```bash
python run_rpo_scenarios_parallel.py
```

### 4. Regenerate Publication Figures

To regenerate all Figures 1 through 7 from the result CSV datasets:

```bash
python generate_rpo_figures.py
```

---

## 📄 License

This repository is released under the [MIT License](LICENSE).
