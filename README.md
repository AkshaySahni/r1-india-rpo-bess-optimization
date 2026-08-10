# Techno-Economic Optimization of Hybrid Wind–Solar–Storage Systems under India’s Renewable Purchase Obligations

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Zenodo DOI](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.14983362-blue)](https://doi.org/10.5281/zenodo.14983362)
[![Mendeley DOI](https://img.shields.io/badge/Mendeley-10.17632%2Fy58jknpgs8.2-orange)](https://doi.org/10.17632/y58jknpgs8.2)

An 8,760-hour annual Linear Programming (LP) capacity expansion and operational dispatch optimization engine for evaluating hybrid utility-scale solar PV, onshore wind, and Lithium-ion Battery Energy Storage Systems (BESS) under India's statutory Renewable Purchase Obligations (RPO) through FY 2029–30.

---

## 📌 Technical Highlights & Data Provenance

1. **Empirical Data & Calibrated Physical Profile Pipeline**:
   - **Solar PV & Wind Profiles**: Formulated via analytical solar-position (elevation/declination geometry, single-axis tracking) and 3.3 MW IEC IIA wind-shear power-law boundary layer physical models, scaled to representative state annual capacity factor baselines (Rajasthan 24.5% Solar / 28.5% Wind; Gujarat 23.8% Solar / 33.5% Wind; Tamil Nadu 22.2% Solar / 36.2% Wind; Karnataka 22.8% Solar / 31.5% Wind).
   - **DISCOM Demand Telemetry**: Ingested via a 2-step hybrid disaggregation of Zenodo daily state totals ([DOI: 10.5281/zenodo.14983362](https://doi.org/10.5281/zenodo.14983362)) and Mendeley Data regional utility hourly shapes ([DOI: 10.17632/y58jknpgs8.2](https://doi.org/10.17632/y58jknpgs8.2)), normalized to a 1,000 MW peak reference system.

2. **High-Speed Linear Programming Engine**:
   - Formulated as continuous linear programs solved via SciPy `scipy.optimize.linprog` (C++ HiGHS dual revised simplex backend).
   - Matrix dimensions per 8,760-hour scenario: $N_{\text{vars}} = 70,085$, $N_{\text{constraints}} = 70,084$.

3. **Battery Degradation & Health Mechanics**:
   - Explicit throughput wear penalties ($C_{\text{deg}} \in \{0, 400, 800\}\text{ INR/MWh}$).
   - Mid-life cell stack replacement horizons ($Y_{\text{repl}} \in \{7, 10, 13\}$ calendar years at 60% initial CAPEX).

4. **Multi-Horizon Policy & Financial Analysis**:
   - Evaluates 96 baseline scenarios (FY 2024–25 to FY 2029–30 across Rajasthan, Gujarat, Tamil Nadu, and Karnataka for 2h, 4h, 6h, and 8h BESS).
   - Evaluates 144 BESS degradation sensitivity scenarios, 48 multi-year weather sensitivity scenarios (2021–2023), and 48 WACC cost-of-capital sweeps ($r \in \{8\%, 10\%, 12\%\}$).

---

## 📂 Repository Structure

```
├── input_data/
│   ├── cost_trajectory_table2.json       # Machine-readable CAPEX/O&M projections (2024-30)
│   ├── demand_profiles/                  # 12 empirical DISCOM demand CSV profiles (2021-23)
│   └── profiles/                         # 12 analytical PV/Wind hourly capacity factor CSVs (2021-23)
├── figures/                              # High-resolution publication PDFs & PNGs (Figs 1-7)
├── fetch_demand_data.py                  # Ingests & normalizes Zenodo/Mendeley demand curves
├── profile_generator.py                  # Analytical solar-position & wind-shear profile generator
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
pip install numpy pandas scipy matplotlib
```

### 2. End-to-End Execution Sequence

```bash
# Step 1: Ingest DISCOM demand profiles & export cost trajectories
python fetch_demand_data.py

# Step 2: Generate 8,760-hour analytical capacity factor profiles
python profile_generator.py

# Step 3: Run single HiGHS LP solver test
python highs_rpo_solver.py

# Step 4: Execute full scenario sweeps (96 baseline + 144 degradation + 48 weather + 48 WACC)
python run_rpo_scenarios.py
python run_wacc_sensitivity.py

# Step 5: Regenerate all publication figures (Figures 1 to 7)
python generate_rpo_figures.py
```

---

## 📊 Key Analytical Findings

1. **Landed LCOE Convergence**: RPO-compliant hybrid system landed tariffs decline from **5.05–5.40 INR/kWh** (FY 2024–25) to **3.70–3.96 INR/kWh** (FY 2029–30) under a 4-hour BESS baseline (**2.96–3.34 INR/kWh** under 8% concessional debt).
2. **Global Optimal Storage Duration**: A **4-to-6 hour BESS duration** achieves the cost-optimal landed LCOE across all four state corridors.
3. **Statutory Penalty Arbitrage**: Green PPA procurement is **2.4 to 2.88× cheaper** than Section 14A statutory non-compliance penalties (10.00 INR/kWh / 10,000 INR/MWh) under the amended Energy Conservation Act 2022.
