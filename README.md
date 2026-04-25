# SOP — Stock Return Out-of-Sample Prediction

A replication and extension of the Goyal-Welch (2008) out-of-sample equity return forecasting framework, enhanced with VIX-regime filtering, volatility-managed portfolio strategies, and Connor-shrunk OLS predictors.

---

## Overview

This project implements and extends the **Sum-of-Parts (SOP)** return decomposition model, which breaks monthly log equity returns into three fundamental components:

| Component | Formula | Description |
|-----------|---------|-------------|
| `dp` | `log(1 + D12 / (12·P))` | Dividend-price term (monthly yield) |
| `ge` | `log(E12_t / E12_{t-1})` | Earnings growth |
| `gm` | `log(M_t / M_{t-1})` | Multiple growth (P/E change) |

The SOP forecast `ms = gs + dp` (where `gs` is a rolling-mean smoothed earnings growth) is evaluated against the historical mean benchmark and a large set of Goyal-Welch predictors.

---

## Repository Structure

```
SOP/
├── SOP.ipynb                    # Main analysis notebook (11 steps)
├── agoyal_data.xlsx             # Goyal-Welch predictor data (Monthly + Annual sheets)
├── sop_monthly_enriched.csv     # Enriched monthly panel (1871–2024)
├── sop_annual_enriched.csv      # Enriched annual panel
├── sop_monthly_vix_filtered.csv # VIX-sample panel (1990–2024)
├── sop_benchmark_results.csv    # OOS R² results for all Goyal-Welch predictors
├── sop_tier_comparison.csv      # Predictor tier rankings (Best 3 / Middle / Worst)
├── sop_last12_forecasts.csv     # Most recent 12-month rolling forecasts
├── fig_sop_components.png       # SOP component diagnostic chart
├── fig_oos_r2_comparison.png    # OOS R² comparison across predictors
├── fig_cum_mse_gain.png         # Cumulative MSE gain over historical mean
└── vix_crisis_chart.png         # VIX time series with crisis shading
```

---

## Methodology

### Step 1–2: Data Loading & Enrichment
- Loads Goyal-Welch monthly and annual data from Excel
- Extends the panel with FRED series (VIX, SP500, CPI, T-bill, NBER recession indicator) via the FRED API
- Optionally extends with Shiller CAPE data

### Step 3: SOP Component Construction
- Constructs `dp`, `ge`, `gm`, `gs`, and `ms` from raw price, dividend, and earnings data
- Builds both monthly and annual aggregated panels

### Step 4: Baseline SOP Forecast Evaluation
- Expanding-window out-of-sample evaluation starting from 1948
- Compares SOP forecast `ms` against the historical mean benchmark
- Reports OOS R², MSE, and MAE improvement

### Step 5: Benchmark Regressions (Connor-Shrunk OLS)
- For each Goyal-Welch predictor, runs an expanding-window OLS regression with Connor (1997) shrinkage:

  ```
  beta* = (s / (s + i)) * beta_hat,   i = 1200
  ```

- Intercept adjusted to preserve the training-sample mean
- Results ranked into tiers: **Best 3**, **Middle**, **Worst**

### Steps 6–9: VIX Regime Analysis
- Filters the panel to the VIX sample (1990-01-31 onward)
- Plots VIX with crisis shading and the VIX=25 threshold
- Tests `gm` predictors and builds an **Enhanced SOP** using VIX as a regime multiplier
- Two-stage reversion model with ADF stationarity diagnostics
- Fair model comparison over matched 2010–2024 evaluation window

### Steps 10–11: Volatility-Managed SOP Strategies
- Implements Moreira-Muir (2017) realized-variance overlay
- Compares Strategies A/B/C/D using VIX percentile scaling
- Crisis period OOS R² split (crisis vs. non-crisis)
- Jobson-Korkie significance test and CEQ certainty equivalent

---

## Getting Started

### Prerequisites

```bash
pip install pandas numpy matplotlib openpyxl requests statsmodels
```

A FRED API key is required for data extension. Register for free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html).

### Configuration

Open `SOP.ipynb` and set the user settings in **Cell 0**:

```python
EXCEL_PATH   = "agoyal_data.xlsx"   # Path to Goyal-Welch data file
OUTPUT_DIR   = "."                  # Output directory for CSV/figures
TARGET_END   = "2024-12-31"         # End date of the analysis

FRED_API_KEY = "<your_key_here>"    # FRED API key
USE_FRED_EXTENSION    = True        # Fetch FRED series (VIX, CPI, etc.)
USE_SHILLER_EXTENSION = True        # Extend with Shiller CAPE data

FORECAST_START       = "1948-01-31" # OOS evaluation start
MIN_TRAIN_MONTHS     = 240          # Minimum training window (months)
SHRINKAGE_INTENSITY  = 1200         # Connor shrinkage parameter
```

### Data

The notebook expects `agoyal_data.xlsx` (Amit Goyal's PredictorData), available from:
> https://www.hec.unil.ch/agoyal/

### Running

Run all cells in order within Jupyter:

```bash
jupyter notebook SOP.ipynb
```

---

## Key Results

- The **SOP forecast** (`ms = gs + dp`) achieves positive OOS R² over the full 1948–2024 sample, outperforming the historical mean
- **Top Goyal-Welch predictors** (by OOS R²): variance premium (`vp`), market sentiment (`ms`), WTI crude (`wtexas`), corporate spread (`corpr`)
- **VIX regime filtering** improves forecast performance during high-volatility periods (VIX > 25)
- **Volatility-managed SOP strategies** based on Moreira-Muir further improve risk-adjusted returns during crisis windows

---

## References

- Goyal, A. & Welch, I. (2008). *A Comprehensive Look at the Empirical Performance of Equity Premium Prediction*. Review of Financial Studies.
- Connor, G. (1997). *Sensible Return Forecasting for Portfolio Management*. Financial Analysts Journal.
- Moreira, A. & Muir, T. (2017). *Volatility-Managed Portfolios*. Journal of Finance.