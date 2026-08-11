# ERA5 Reanalysis & PVWatts/pvlib Physical Modeling Technical Specification (v2.0)

**Date**: August 11, 2026  
**Status**: Scope Locked & Approved for Execution

---

## 1. Geographical Corridor Project Siting Coordinates

To eliminate spatial ambiguity and avoid single-point noise, exact project siting coordinates are locked to primary utility project DPRs and verified renewable corridor centroids:

| State Corridor | RE Asset Type | Primary Location / Siting Project | Latitude (°N) | Longitude (°E) |
| :--- | :--- | :--- | :--- | :--- |
| **Rajasthan** | Solar PV & Onshore Wind | Jaisalmer / Thar Desert Renewable Energy Park | 26.9124 | 70.9000 |
| **Gujarat** | Solar PV & Onshore Wind | Khavda Hybrid Renewable Energy Park (Kutch) | 23.8500 | 69.7500 |
| **Tamil Nadu** | Solar PV & Onshore Wind | Muppandal Wind Pass & Kayathar Solar Belt | 8.1800 | 77.5300 |
| **Karnataka (Solar)** | Solar PV | Pavagada Solar Park (Tumkur District DPR) | 14.1000 | 77.2700 |
| **Karnataka (Wind)** | Onshore Wind | Chitradurga High-Speed Wind Pass | 14.2200 | 76.4000 |

---

## 2. Time Horizon & Timezone Conventions

- **Native Extraction Window**: 2021-01-01 00:00:00 UTC to 2023-12-31 23:00:00 UTC.
- **Hours per Year**: 8,760 hours per calendar year (2021, 2022, 2023).
- **Timezone Conversion**: Converted to Indian Standard Time (IST, UTC+5:30) immediately upon extraction before any solar position or generation modeling.

---

## 3. ERA5 Meteorological Variables & Radiation Decomposition

Reanalysis data is fetched from the Copernicus Climate Data Store (CDS 2.0 API, `reanalysis-era5-single-levels`):
1. `100m_u_component_of_wind`, `100m_v_component_of_wind` ($100\text{ m}$ vector wind components)
2. `10m_u_component_of_wind`, `10m_v_component_of_wind` ($10\text{ m}$ vector wind components)
3. `surface_solar_radiation_downwards` ($ssrd$, accumulated $\text{J/m}^2$)
4. `2m_temperature` ($T_{2m}$, K)
5. `surface_pressure` ($sp$, Pa)

### Radiative & Boundary Layer De-Accumulation Logic
- **$ssrd$ De-accumulation**: Instantaneous $GHI$ ($\text{W/m}^2$) is calculated via step-differencing: $GHI_t = \frac{\max(0, ssrd_t - ssrd_{t-1})}{3600}$, respecting ECMWF 00:00/12:00 UTC accumulation boundary resets.
- **Solar Zenith Computation**: Solar zenith angle $\theta_z(t)$ is calculated using `pvlib.solarposition.get_solarposition(lat, lon, timestamps_ist)`.
- **DNI/DHI Decomposition**: Global Horizontal Irradiance ($GHI$) and $\theta_z(t)$ are fed to `pvlib.irradiance.disc` to separate $GHI$ into Direct Normal Irradiance ($DNI$) and Diffuse Horizontal Irradiance ($DHI$).

---

## 4. Solar PV Generation Physics (`pvlib.pvsystem`)

- **Tracking System**: Single-axis tracking ($1$-axis, North-South axis, 0° tilt, 180° azimuth) with backtracking enabled (`pvlib.tracking.singleaxis`).
- **PVWatts v8 Loss Stack**:
  - Soiling loss: 2.0%
  - DC wiring loss: 1.5%
  - AC wiring loss: 0.5%
  - Inverter efficiency: 98.2% (CEC inverter model)
  - Availability & shading: 1.5%
  - **Net Derate Factor**: $\approx 93.5\%$ total system performance ratio.

---

## 5. Wind Generation Physics & Commercial Turbine Specifications

- **Turbine Model**: **Envision E-156 3.3 MW IEC Class IIA**
  - Rated Capacity: $3.30\text{ MW}$
  - Rotor Diameter: $156.0\text{ m}$
  - Hub Height: $120.0\text{ m}$
  - Cut-in Wind Speed: $3.0\text{ m/s}$
  - Rated Wind Speed: $11.5\text{ m/s}$
  - Cut-out Wind Speed: $20.0\text{ m/s}$
  - Source: Envision Energy Commercial Datasheet & NREL OpenOA Public Turbine Library.
- **Dynamic Wind Shear Extrapolation**: Hourly shear exponent $\alpha_t = \frac{\ln(v_{100m,t} / v_{10m,t})}{\ln(100 / 10)}$.
  - Hub-height speed: $v_{120m,t} = v_{100m,t} \times \left(\frac{120}{100}\right)^{\alpha_t}$.
- **Power Curve Application**: Ingests the 3.3 MW turbine power curve directly in Python with a documented 3.5% balance-of-plant & electrical collection array loss factor.

---

## 6. Exact Non-Overlapping 288 Scenario Matrix Arithmetic

Total solved scenarios = **288** non-overlapping instances:
1. **Baseline Policy Scenarios (96 Solves)**: 6 Commissioning Vintages (FY 2024–25 to FY 2029–30) $\times$ 4 State Corridors (RJ, GJ, TN, KA) $\times$ 4 Storage Durations (2h, 4h, 6h, 8h) under 10% baseline WACC.
2. **Battery Degradation Sensitivity Scenarios (144 Solves)**: FY 2029–30 baseline $\times$ 4 State Corridors $\times$ 4 Storage Durations $\times$ 3 Stack Replacement Horizons (7, 10, 13 yrs) $\times$ 3 Throughput Wear Penalties (0, 400, 800 INR/MWh) (subtracting baseline overlaps).
3. **Multi-Year Weather & WACC Sensitivity Scenarios (48 Solves)**: FY 2029–30 baseline $\times$ 4 State Corridors $\times$ 4 Storage Durations $\times$ 3 Weather Years (2021, 2022, 2023) at 8% WACC.
