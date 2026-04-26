# SOP — Forecasting Stock Market Returns

A replication and extension of Ferreira and Santa-Clara (2011), using the **Sum-of-Parts (SOP)** return decomposition to forecast the equity risk premium. The project evaluates the SOP approach against Goyal-Welch (2008) benchmark predictors, tests VIX as an enhancer of multiple-growth forecasts, analyzes performance during crisis periods, and applies volatility-managed portfolio strategies.

---

## Overview

The SOP model decomposes monthly log equity returns into three interpretable components:

| Component | Formula | Description |
|-----------|---------|-------------|
| `dp` | `log(1 + D12 / (12·P))` | Dividend-price term (monthly yield) |
| `ge` | `log(E12_t / E12_{t-1})` | Earnings growth (log change in trailing earnings) |
| `gm` | `log(M_t / M_{t-1})` | Multiple growth (log change in P/E ratio) |

The baseline SOP forecast is `ms = gs + dp`, where `gs` is a 20-year rolling average of past earnings growth and expected multiple growth is set to zero. This forecast is evaluated against the historical mean benchmark and a large set of Goyal-Welch predictors using expanding-window out-of-sample evaluation.

The project is organized around three pillars:

1. **Foundation** — Replicate Ferreira & Santa-Clara (2011) and extend the sample through 2024
2. **Pillar 1** — Test whether VIX improves forecasts of multiple growth (VIX sample: 1990–2024)
3. **Pillar 2** — Evaluate crisis-period performance from an investor perspective
4. **Pillar 3** — Add volatility-managed overlay to SOP-based trading strategies

---

## Repository Structure

```
SOP/
├── SOP.ipynb                          # Main analysis notebook (Steps 1–19 + STRICT block)
├── SOP Project Plan Steps.md          # Full project specification and methodology
├── agoyal_data.xlsx                   # Goyal-Welch predictor data (Monthly + Annual sheets)
│
├── sop_monthly_enriched.csv           # Enriched monthly panel (1871–2024)
├── sop_annual_enriched.csv            # Enriched annual panel
├── sop_monthly_vix_filtered.csv       # VIX-sample panel (1990–2024)
├── sop_benchmark_results.csv          # OOS R² results for all Goyal-Welch predictors
├── sop_tier_comparison.csv            # Predictor tier rankings (Best 3 / Middle / Worst)
├── sop_last12_forecasts.csv           # Most recent 12-month rolling forecasts
│
├── strict_replication_1927_2007.csv   # 1927–2007 replication table (ERP framing)
├── strict_reversion_comparison.csv    # Multiple-reversion model comparison (VIX vs Goyal)
├── strict_crisis_mae_table.csv        # Crisis vs non-crisis OOS R² and MAE split
├── strict_hm_vs_sop_crisis_portfolios.csv  # Investor portfolio outcomes per crisis window
├── strict_nber_baseline_vs_vix.csv    # NBER recession/expansion OOS R² split
├── strict_nber_vix_sensitivity.csv    # NBER split sensitivity to training window length
│
├── fig_sop_components.png             # SOP component diagnostic chart
├── fig_oos_r2_comparison.png          # OOS R² comparison across predictors
├── fig_cum_mse_gain.png               # Cumulative MSE gain over historical mean
├── vix_crisis_chart.png               # VIX time series with crisis shading
└── sop_figures/
    └── vix_crisis_chart.png           # VIX crisis chart (figures subfolder copy)
```

---

## Methodology

### Foundation: Data Loading & SOP Construction (Steps 1–5)

**Steps 1–2: Data Loading & Enrichment**
- Loads Goyal-Welch monthly and annual data (`agoyal_data.xlsx`)
- Extends the panel with FRED series (`VIXCLS`, `SP500`, `CPIAUCSL`, `TB3MS`, `USREC`) via the FRED API
- Optionally extends through 2024 using Shiller data

**Step 3: SOP Component Construction**
- Constructs `dp`, `ge`, `gm`, `gs`, and `ms` from raw price, dividend, and earnings data
- Builds both monthly (`sop_monthly_enriched.csv`) and annual (`sop_annual_enriched.csv`) panels
- Verifies that the three components sum to the total log return (no look-ahead bias)

**Step 4: Baseline SOP Forecast Evaluation**
- Expanding-window out-of-sample evaluation starting from January 1948
- Compares SOP forecast `ms` against the historical mean benchmark
- Reports OOS R², MSE-F statistic (McCracken 2007), and MAE improvement
- Dedicated 1927–2007 replication table (`strict_replication_1927_2007.csv`)

**Step 5: Benchmark Regressions (Connor-Shrunk OLS)**
- For each Goyal-Welch predictor, runs an expanding-window OLS regression with Connor (1997) shrinkage:

  ```
  beta* = (s / (s + i)) * beta_hat,   i = 1200
  ```

- Intercept adjusted to preserve the training-sample mean
- Results saved to `sop_benchmark_results.csv` and ranked into tiers: **Best 3** (`wtexas`, `corpr`, `b/m`), **Middle**, **Worst** (`sop_tier_comparison.csv`)

---

### Pillar 1: VIX as a Predictor of Multiple Growth (Steps 6–9)

**Step 6: VIX Sample Alignment**
- Filters the panel to the VIX sample (1990-01-31 onward) → `sop_monthly_vix_filtered.csv`
- Rebuilds `ret_lead` and `gm` series over the aligned sample

**Step 7: VIX Crisis Chart**
- Plots monthly VIX (1990–2024) with shaded crisis regions and the VIX = 25 threshold
- Output: `vix_crisis_chart.png`

**Step 8: `gm` Predictor Regressions + Enhanced SOP**
- Tests VIX and four Goyal predictors (`DFY`, `TBL`, `TMS`, `NTIS`) as predictors of multiple growth
- Builds **Enhanced SOP** by adding the VIX-based `gm` forecast to the baseline `ms`
- Fair comparison over matched 2010–2024 evaluation window

**Step 9: Two-Stage Reversion Model**
- Stage 1: Regresses current P/E on VIX to extract valuation-deviation residuals
- Stage 2: Forecasts future `gm` from the Stage 1 residual (mean-reversion channel)
- Includes ADF stationarity diagnostics and comparison across all reversion predictors (`strict_reversion_comparison.csv`)

---

### Pillar 2: Crisis Performance Analysis (Steps 10–15)

**Steps 10–11: Crisis Definitions & OOS R² Split**
- Two crisis definitions: (A) fixed historical windows (Dot-com, GFC, COVID, Post-COVID inflation) and (B) dynamic VIX > 25 threshold
- OOS R² and MAE computed separately for crisis and non-crisis months → `strict_crisis_mae_table.csv`

**Step 12: Portfolio Simulation (Markowitz Allocation)**
- Uses Ferreira & Santa-Clara (2011) Markowitz weight formula; equity weights capped at [0%, 150%]
- Compares HM vs SOP strategies per crisis window → `strict_hm_vs_sop_crisis_portfolios.csv`
- Reports cumulative return, maximum drawdown, annualized Sharpe ratio, and average equity weight

**Steps 13–15: NBER Recession Robustness**
- Splits full evaluation sample into NBER recession and expansion months (`USREC`)
- Reports OOS R² for baseline SOP and VIX-enhanced SOP in each regime
- Sensitivity table for alternative training-window lengths → `strict_nber_baseline_vs_vix.csv`, `strict_nber_vix_sensitivity.csv`

---

### Pillar 3: Volatility-Managed SOP Strategies (Steps 16–19)

**Step 16: Base Markowitz Strategy Replication**
- Baseline SOP + standard Markowitz weights (Strategy A)
- Benchmark: historical mean timing strategy and buy-and-hold

**Step 17: Moreira-Muir Realized Variance Overlay**
- Computes monthly realized variance from daily S&P 500 returns
- Scales equity weight by `long-run avg variance / current realized variance` (Strategy B)

**Step 18: Strategies A/B/C/D Comparison**

| Strategy | Forecast | Weighting |
|----------|----------|-----------|
| A | Baseline SOP | Standard Markowitz |
| B | Baseline SOP | Volatility-managed (Moreira-Muir) |
| C | VIX-enhanced SOP | Standard Markowitz |
| D | VIX-enhanced SOP | Volatility-managed |

Reports annualized return, volatility, Sharpe ratio, max drawdown, crisis-period Sharpe, and average equity allocation.

**Step 19: Statistical & Economic Significance**
- Jobson-Korkie (1981) test with Memmel (2003) correction for Sharpe ratio differences
- Certainty-equivalent return (CEQ) gain: annual fee an investor would pay to access the strategy

---

### Strict Compliance Block (STRICT-01 to STRICT-05)

A final set of cells closes all plan-compliance items:

| Tag | Content |
|-----|---------|
| STRICT-01 | ERP framing + dedicated 1927–2007 replication table |
| STRICT-02 | Formal VIX vs DFY forecast comparison + full multiple-reversion benchmark set |
| STRICT-03 | Crisis MAE table + investor crisis outcomes (HM vs SOP, same Markowitz rule) |
| STRICT-04 | NBER recession/expansion split including VIX-enhanced SOP |
| STRICT-05 | End-to-end data integrity sweep for all research inputs and exported outputs |

---

## Getting Started

### Prerequisites

```bash
pip install pandas numpy matplotlib openpyxl requests statsmodels scipy
```

A FRED API key is required for data extension. Register for free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html).

### Configuration

Open `SOP.ipynb` and set the user settings in **Cell 0**:

```python
EXCEL_PATH   = "agoyal_data.xlsx"   # Path to Goyal-Welch predictor file
OUTPUT_DIR   = "."                  # Output directory for CSVs and figures
TARGET_END   = "2024-12-31"         # End date of the analysis

FRED_API_KEY = "<your_key_here>"    # FRED API key
USE_FRED_EXTENSION    = True        # Fetch FRED series (VIX, CPI, USREC, etc.)
USE_SHILLER_EXTENSION = True        # Extend with Shiller CAPE data

FORECAST_START       = "1948-01-31" # OOS evaluation start
MIN_TRAIN_MONTHS     = 240          # Minimum training window (months)
SHRINKAGE_INTENSITY  = 1200         # Connor shrinkage parameter
```

### Data

The notebook expects `agoyal_data.xlsx` (Amit Goyal's PredictorData2022), available from:
> https://www.hec.unil.ch/agoyal/

Daily S&P 500 data for realized variance (Steps 17–18) is fetched automatically via FRED (`SP500`).

### Running

Run all cells in order within Jupyter:

```bash
jupyter notebook SOP.ipynb
```

---

## Key Results

- The **SOP forecast** (`ms = gs + dp`) achieves positive OOS R² over the 1927–2024 sample and over the strict 1927–2007 replication window, outperforming the historical mean
- **Top Goyal-Welch predictors** (by OOS R² over 1948–2024): WTI crude (`wtexas`), corporate spread (`corpr`), book-to-market ratio (`b/m`)
- **VIX-enhanced SOP** improves OOS R² over VIX-filtered expansion months and shows large gains in the limited NBER recession sample
- **Crisis performance**: SOP-Markowitz significantly reduces drawdowns versus HM-Markowitz during the dot-com crash (cumulative return −13.8% vs −38.2%)
- **Volatility-managed strategies** (B, D) further improve risk-adjusted returns; CEQ and Jobson-Korkie tests assess statistical significance of Sharpe improvements

---

## References

- Ferreira, T. & Santa-Clara, P. (2011). *Forecasting Stock Market Returns: The Sum of the Parts Is More Than the Whole*. Journal of Financial Economics.
- Goyal, A. & Welch, I. (2008). *A Comprehensive Look at the Empirical Performance of Equity Premium Prediction*. Review of Financial Studies.
- Connor, G. (1997). *Sensible Return Forecasting for Portfolio Management*. Financial Analysts Journal.
- Moreira, A. & Muir, T. (2017). *Volatility-Managed Portfolios*. Journal of Finance.
- Jobson, J.D. & Korkie, B. (1981). *Performance Hypothesis Testing with the Sharpe and Treynor Measures*. Journal of Finance.
- McCracken, M.W. (2007). *Asymptotics for Out of Sample Tests of Granger Causality*. Journal of Econometrics.