# Techno-Economic Optimization of Hybrid Wind–Solar–Storage Systems under India’s Renewable Purchase Obligations

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10876000.svg)](https://doi.org/10.5281/zenodo.10876000)

An 8,760-hour annual Linear Programming (LP) capacity expansion and operational dispatch optimization engine for evaluating hybrid utility-scale solar PV, onshore wind, and Lithium-ion Battery Energy Storage Systems (BESS) under India's statutory Renewable Purchase Obligations (RPO) through FY 2029–30.

---

## 📌 Technical Highlights & Data Provenance

> **Note on Repository Contents**: This repository is dedicated exclusively to **code, raw input preprocessing, optimization solvers, diagnostic logs, and scenario datasets**.

1. **100% Empirical Data Pipeline**:
   - **Irradiance & Wind Reanalysis**: ECMWF ERA5 global reanalysis (2019–2023) for surface solar radiation downwards (`ssrd`) and 100m wind vectors (`u100`, `v100`).
   - **Physics Performance Modeling**: NREL System Advisor Model (`PySAM`) for 540 Wp Mono-PERC single-axis tracking PV arrays and 3.3 MW IEC Class IIA wind turbines (120m hub height).
   - **DISCOM Demand Telemetry**: Grid-India (POSOCO) and National Power Portal (NPP) state load despatch center curves normalized to a 1,000 MW peak reference system.

2. **High-Speed Linear Programming Engine**:
   - Formulated as continuous linear programs solved via SciPy `scipy.optimize.linprog` (C++ HiGHS dual revised simplex backend).
   - Matrix dimensions per 8,760-hour scenario: $N_{\text{vars}} = 70,085$, $N_{\text{constraints}} = 78,843$.
   - Average solve runtime: ~0.182 seconds per scenario.

3. **Battery Degradation & Health Mechanics**:
   - Explicit throughput wear penalties ($C_{\text{deg}} \in \{0, 400, 800\}\text{ INR/MWh}$).
   - Mid-life cell stack replacement horizons ($Y_{\text{repl}} \in \{7, 10, 13\}$ calendar years at 60% initial CAPEX).

4. **Multi-Horizon Policy & Financial Analysis**:
   - Evaluates 96 baseline scenarios (FY 2024–25 to FY 2029–30 across Rajasthan, Gujarat, Tamil Nadu, and Karnataka for 2h, 4h, 6h, and 8h BESS).
   - Evaluates 144 BESS degradation sensitivity scenarios, 80 multi-year weather sensitivity scenarios, and WACC cost-of-capital sweeps ($r \in \{8\%, 10\%, 12\%\}$).

---

## 📂 Repository Structure

```
├── input_data/
│   ├── cost_trajectory_table2.json       # Machine-readable CAPEX/O&M projections (2024-30)
│   ├── demand_profiles/                  # 12 empirical DISCOM demand CSV profiles (2021-23)
│   └── profiles/                         # 12 PySAM PV/Wind hourly capacity factor CSVs
├── figures/                              # High-resolution publication PDFs & PNGs (Figs 1-7)
├── fetch_demand_data.py                  # Ingests & normalizes POSOCO/Grid-India demand curves
├── fetch_era5_data.py                    # Downloads ECMWF ERA5 NetCDF reanalysis via CDS API
├── pysam_profile_generator.py            # Simulates 8,760-hour PV and wind generation profiles
├── highs_rpo_solver.py                   # Sparse LP matrix generator & HiGHS C++ solver interface
├── run_rpo_scenarios.py                  # Batch execution runner for baseline & degradation sweeps
├── run_wacc_sensitivity.py              # Financial WACC sensitivity sweep runner (8%, 10%, 12%)
├── generate_rpo_figures.py               # Renders publication-quality figures
├── rpo_manuscript_scopus_q1.tex          # Complete LaTeX manuscript formatted for Elsevier Scopus Q1
└── README.md                             # Repository documentation
```

---

## 🚀 Quickstart & Reproducibility Guide

### 1. Prerequisites & Installation

```bash
# Clone the repository
git clone https://github.com/AkshaySahni/r1-india-rpo-bess-optimization.git
cd r1-india-rpo-bess-optimization

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install required dependencies
pip install numpy pandas scipy matplotlib xarray netCDF4 NREL-PySAM cdsapi
```

### 2. End-to-End Execution Sequence

```bash
# Step 1: Ingest DISCOM demand profiles & export cost trajectories
python fetch_demand_data.py
python fetch_era5_data.py

# Step 2: Generate 8,760-hour PySAM capacity factor profiles
python pysam_profile_generator.py

# Step 3: Run single HiGHS LP solver test
python highs_rpo_solver.py

# Step 4: Execute full scenario sweeps (96 baseline + 144 degradation + 48 weather)
python run_rpo_scenarios.py
python run_wacc_sensitivity.py

# Step 5: Regenerate all publication figures (Figures 1 to 7)
python generate_rpo_figures.py
```

---

## 📊 Key Analytical Findings

1. **Landed LCOE Convergence**: RPO-compliant hybrid system landed tariffs decline from **4.82–5.58 INR/kWh** (FY 2024–25) to **3.58–4.14 INR/kWh** (FY 2029–30) under a 4-hour BESS baseline (**3.47–4.04 INR/kWh** under 6-hour BESS).
2. **Global Optimal Storage Duration**: A **6-hour BESS duration** achieves the global cost-minimum landed LCOE across all four state corridors, balancing evening peak shifting against capital recovery costs.
3. **Statutory Penalty Arbitrage**: Green PPA procurement is **2.4 to 2.88× cheaper** than Section 14A statutory non-compliance penalties (10.00 INR/kWh / 10,000 INR/MWh) under the amended Energy Conservation Act 2022.

---

## 📜 Citation & License

If you use this codebase or dataset in your research, please cite:

```bibtex
@article{Sahni2026RPO,
  title={Techno-Economic Optimization of Hybrid Wind--Solar--Storage Systems under India's Statutory Renewable Purchase Obligations: An 8,760-Hour Multi-Horizon Analysis},
  author={Sahni, Akshay K.},
  journal={Applied Energy (Under Review)},
  year={2026},
  doi={10.5281/zenodo.10876000}
}
```

This project is licensed under the [MIT License](LICENSE).
