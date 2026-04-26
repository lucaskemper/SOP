# SOP Project Plan: Forecasting Stock Market Returns

**Project title:** Forecasting Stock Market Returns: An Extension of Ferreira and Santa-Clara (2011)  
**Core question:** Can the Sum-of-the-Parts (SOP) method, updated through 2024, improve equity risk premium forecasting for investors, especially during crisis periods, and does adding the VIX improve the multiple-growth component?

---

## 1. Purpose and Investor Framing

This project replicates and extends the Sum-of-the-Parts (SOP) forecasting method introduced by Ferreira and Santa-Clara (2011). The original paper decomposes stock market returns into interpretable components and shows that forecasting those components separately can outperform both the historical mean and standard predictive regressions.

This extension evaluates whether the SOP approach remains useful for a real-time investor using modern data through 2024. The project focuses on the **equity risk premium**, because the practical investment decision is whether to allocate capital to equities or to the risk-free asset.

The project must answer three investor-relevant questions:

1. **Forecasting value:** Does the SOP forecast still outperform the historical mean and standard predictors when updated through 2024?
2. **Crisis value:** Does the SOP forecast help most when investors need it most, namely during crisis periods?
3. **Implementation value:** Do VIX-enhanced forecasts and volatility-managed weights improve risk-adjusted returns, drawdowns, and certainty-equivalent gains?

The final interpretation should not stop at statistical significance. Results must be framed in terms of capital preservation, drawdown control, Sharpe ratios, and actionable portfolio decisions.

---

## 2. Project Structure

The project is organized into one foundation block and three main pillars.

| Block | Objective | Main Output |
|---|---|---|
| Foundation | Replicate Ferreira and Santa-Clara (2011) and extend the sample to 2024 | Baseline SOP forecasts and benchmark comparison |
| Pillar 1 | Test whether VIX improves forecasts of multiple growth | VIX versus Goyal predictor comparison |
| Pillar 2 | Evaluate crisis-period performance from an investor perspective | Crisis and non-crisis forecast/portfolio tables |
| Pillar 3 | Add volatility management to SOP-based trading strategies | Full strategy comparison table |

---

## 3. Required Data Sources

### 3.1 Goyal and Welch Predictor Dataset

**Source:** Amit Goyal website, `PredictorData2022.xlsx`  
**Use:** Main monthly dataset for return components and benchmark predictors.

Required variables:

- `Index`: S&P 500 price index
- `D12`: 12-month trailing dividends
- `E12`: 12-month trailing earnings
- `tbl`: 3-month Treasury bill rate
- `tms`: term spread
- `dfy`: default yield spread
- `ntis`: net equity expansion
- `infl`: inflation

This file is the backbone of the analysis because it contains the main return components and the benchmark predictors used in the literature.

### 3.2 FRED Data

Use FRED to cross-check or supplement recent observations.

Required series:

- `VIXCLS`: VIX index, used as a forward-looking measure of market uncertainty
- `USREC`: NBER recession indicator
- `SP500`: S&P 500 index, used for price cross-checks
- `CPIAUCSL`: CPI, used for inflation cross-checks
- `TB3MS`: 3-month Treasury bill rate, used for risk-free-rate cross-checks

### 3.3 Robert Shiller Data

**Use:** Supplementary source for price, dividends, and earnings in the latest sample extension when Goyal data do not fully cover the required endpoint.

### 3.4 Daily S&P 500 Data

**Source options:** Yahoo Finance ticker `^GSPC` or FRED series `SP500`  
**Use:** Daily returns for monthly realized variance in the volatility-managed strategy.

---

## 4. Foundation: Replication and Data Extension

### Step 1: Collect and Clean Monthly Data

1. Download the Goyal and Welch predictor file.
2. Import the monthly price, dividend, earnings, risk-free-rate, and predictor variables.
3. Extend or cross-check the sample through 2024 using FRED and Shiller data where needed.
4. Convert all date fields to monthly end-of-period dates.
5. Align all variables to a single monthly index.
6. Verify that no future information is used when constructing forecasts.

**Deliverables:**

- Clean monthly master dataset from 1927 to 2024, where available
- Separate data dictionary listing all variables and sources
- Missing-value audit showing where external sources were used for extension

---

### Step 2: Construct Return Components

Following Ferreira and Santa-Clara (2011), decompose the total log stock market return into three components:

1. **Dividend-price component (`dp`)**  
   Log of one plus trailing dividends divided by the current price index.

2. **Earnings-growth component (`ge`)**  
   Log change in 12-month trailing earnings per share.

3. **Multiple-growth component (`gm`)**  
   Log change in the price-earnings multiple.

4. **Total log return (`r`)**  
   Sum of the three components above.

**Quality check:** Confirm that the sum of the three components closely matches the total log return including dividends. Any persistent mismatch must be explained and fixed before forecasting begins.

**Deliverables:**

- Monthly series for `dp`, `ge`, `gm`, and `r`
- Replication check showing the return decomposition works mechanically

---

### Step 3: Build the Baseline SOP Forecast

At each forecast date, construct the baseline SOP forecast as:

```text
Expected return = expected earnings growth + expected dividend-price component + expected multiple growth
```

For the baseline specification:

1. Estimate expected earnings growth as a **20-year rolling average** of past earnings growth.
2. Use the current dividend-price component as the expected dividend-price component.
3. Set expected multiple growth equal to zero.
4. Start the expanding out-of-sample evaluation in January 1948, allowing for the initial 20-year estimation window.

**Important rule:** Every forecast must use only information available at the forecast date.

**Deliverables:**

- Baseline monthly SOP forecast
- Documentation of forecast timing conventions
- Verification that no look-ahead bias exists

---

### Step 4: Build Benchmark Forecasts

Use two benchmark families.

#### Benchmark A: Historical Mean

At each month, compute the expanding historical average of realized returns using only past observations.

#### Benchmark B: Predictive Regressions

Estimate expanding-window OLS regressions of returns on selected Goyal variables. Apply shrinkage following Connor (1997) to reduce estimation error and make the comparison consistent with the original paper.

Required Goyal predictors:

- Default yield spread (`DFY`)
- T-bill rate (`TBL`)
- Term spread (`TMS`)
- Net equity expansion (`NTIS`)

**Deliverables:**

- Historical mean forecast series
- Predictive-regression forecast series for each selected Goyal variable
- Benchmark comparison dataset aligned with SOP forecasts

---

### Step 5: Evaluate Baseline Forecast Performance

Report forecast performance at monthly and annual frequencies.

Required metrics:

1. **Out-of-sample R-squared relative to the historical mean**
   - Positive values indicate improvement over the historical mean.
   - Negative values indicate underperformance.

2. **McCracken (2007) MSE-F statistic**
   - Used to test whether the forecast error reduction is statistically significant.

3. **Mean absolute forecast error**
   - Included because it is intuitive for non-technical readers.

4. **Annual-frequency results**
   - Use non-overlapping annual observations to avoid overlapping-return concerns.

**Deliverables:**

- Monthly forecast-performance table
- Annual forecast-performance table
- Short interpretation focused on investor usefulness

---

## 5. Pillar 1: VIX as a Predictor of Multiple Growth

### Objective

The baseline SOP model assumes expected multiple growth is zero. This pillar tests whether the VIX improves forecasts of multiple growth, especially because VIX captures forward-looking market uncertainty and risk sentiment.

Because VIX data begin in January 1990, all VIX comparisons must be evaluated over the same 1990-2024 sample. The Goyal predictors must be re-tested over this same window for a fair comparison.

---

### Step 6: Select Benchmark Predictors

Use four Goyal and Welch predictors as benchmarks against VIX.

| Predictor | Economic Channel | Reason for Inclusion |
|---|---|---|
| `DFY` | Credit risk | Strong benchmark from the original paper |
| `TBL` | Monetary policy / short rates | Standard return predictor |
| `TMS` | Yield curve | Captures term-structure conditions |
| `NTIS` | Corporate financing behavior | Performed well in the original paper |

**Deliverables:**

- Predictor summary table
- Correlation matrix for VIX and the four Goyal predictors
- Summary statistics over the common 1990-2024 sample

---

### Step 7: Collect and Transform VIX Data

1. Download daily VIX data from FRED series `VIXCLS`.
2. Convert daily VIX to monthly frequency using the end-of-month value.
3. Align monthly VIX with the Goyal dataset.
4. Confirm that the forecast uses VIX observed at month-end to forecast next-period multiple growth.

**Deliverables:**

- Monthly VIX series from 1990 to 2024
- Plot of monthly VIX with major crisis periods highlighted
- Alignment check between VIX and return-component dates

---

### Step 8: Estimate Multiple-Growth Regression Forecasts

For VIX and each Goyal predictor, run an expanding-window regression of next-period multiple growth on the current predictor value.

Process:

1. Regress future `gm` on the current predictor.
2. Generate an out-of-sample forecast of `gm`.
3. Add the `gm` forecast to the baseline SOP components.
4. Compare the full return forecast against the historical mean and the baseline SOP forecast.
5. Apply the same shrinkage method used in the replication to keep the comparison fair.

**Deliverables:**

- Out-of-sample R-squared table for VIX and the four Goyal predictors
- Statistical comparison of VIX versus `DFY`
- Interpretation of whether VIX adds investor-relevant forecasting value

---

### Step 9: Estimate Multiple-Reversion Forecasts with VIX

Test whether VIX helps identify when the price-earnings multiple is away from fair value.

Process:

1. Regress the current price-earnings ratio level on the current VIX.
2. Treat the regression residual as the deviation from VIX-implied fair value.
3. Regress future multiple growth on this residual to estimate the speed of reversion.
4. Use the estimated reversion relationship to forecast future `gm`.
5. Repeat the same procedure for each Goyal predictor.
6. Add the predicted `gm` to the baseline SOP forecast.

**Economic intuition:** If VIX is high, investors demand higher risk premia, which tends to compress valuation multiples. If VIX captures this channel better than credit spreads or yield-curve variables, it should improve multiple-growth forecasts.

**Deliverables:**

- Multiple-reversion forecast table
- Comparison of VIX-implied fair-value model versus Goyal-variable models
- Chart of actual P/E, VIX-implied fair P/E, and residual deviations

---

## 6. Pillar 2: Crisis Performance Analysis

### Objective

This pillar evaluates whether the SOP forecast is especially useful during market stress. The analysis must translate forecast performance into investor outcomes such as drawdown protection, cumulative crisis returns, and crisis-period Sharpe ratios.

---

### Step 10: Define Crisis Periods

Use two crisis definitions.

#### Definition A: Fixed Historical Crisis Windows

| Crisis | Window |
|---|---|
| Dot-com crash | March 2000 to September 2002 |
| Global financial crisis | October 2007 to March 2009 |
| COVID crash | February 2020 to April 2020 |
| Post-COVID inflation shock | January 2022 to October 2022 |

#### Definition B: Dynamic VIX Threshold

Classify a month as a crisis month if the month-end VIX is above 25.

This threshold is rule-based, replicable, and captures months when market uncertainty is materially elevated.

**Deliverables:**

- Crisis-month indicator using fixed windows
- Crisis-month indicator using VIX threshold
- Comparison table showing overlap between the two definitions

---

### Step 11: Compare Forecast Performance Inside and Outside Crises

For each crisis definition, compare SOP forecast performance against the historical mean separately in crisis and non-crisis months.

Required metrics:

- Out-of-sample R-squared in crisis months
- Out-of-sample R-squared in non-crisis months
- Mean absolute forecast error in crisis months
- Mean absolute forecast error in non-crisis months

**Key question:** Does SOP generate a better signal when markets are stressed, or does it only work in calm periods?

**Deliverables:**

- Crisis versus non-crisis forecast-performance table
- Short interpretation focused on practical decision-making

---

### Step 12: Translate Forecasts into Crisis-Period Portfolio Outcomes

Use the Markowitz weight formula from Ferreira and Santa-Clara (2011) to convert forecasts into portfolio weights.

For each crisis window, compare:

1. Investor using the historical mean forecast
2. Investor using the baseline SOP forecast
3. Investor using the VIX-enhanced SOP forecast, where available

Required metrics:

- Cumulative return during the crisis window
- Peak-to-trough maximum drawdown
- Annualized Sharpe ratio during the crisis window
- Average equity weight during the crisis window

**Interpretation standard:** Explain results in plain investor terms. For example, do not only state that one model has a higher R-squared; explain whether it preserved capital, reduced drawdowns, or avoided excessive equity exposure.

**Deliverables:**

- Crisis-window portfolio table
- Drawdown chart for each major crisis
- Investor-focused interpretation

---

### Step 13: Run NBER Recession Robustness Check

Use FRED series `USREC` to split the full evaluation sample into recession and expansion months.

Process:

1. Download monthly `USREC` data.
2. Merge it with the forecast dataset.
3. Compute SOP out-of-sample R-squared separately for recession and expansion months.
4. Repeat for VIX-enhanced SOP where the VIX sample is available.

**Deliverables:**

- Recession versus expansion forecast-performance table
- Discussion of whether VIX improvements are concentrated in recessions

---

## 7. Pillar 3: Volatility-Managed SOP Trading Strategy

### Objective

This pillar tests whether scaling SOP portfolio weights by recent realized volatility improves investor outcomes. The extension follows Moreira and Muir (2017) and is practical because it uses only backward-looking volatility information.

---

### Step 14: Replicate the Base SOP Trading Strategy

Each month, compute the optimal equity weight using the SOP excess-return forecast and an estimated return variance.

Implementation rules:

1. Estimate return variance using a 5-year rolling window of past monthly returns.
2. Compute the equity weight using the paper's Markowitz allocation formula.
3. Cap equity weights between 0% and 150%.
4. Compare against:
   - Historical mean timing strategy
   - Fully invested buy-and-hold strategy

**Deliverables:**

- Monthly portfolio weights
- Strategy return series
- Replication table with mean return, volatility, Sharpe ratio, and maximum drawdown

---

### Step 15: Add Volatility-Managed Overlay

Scale the monthly equity weight by the inverse of realized variance relative to its long-run average.

Process:

1. Compute daily S&P 500 returns.
2. For each month, calculate realized variance as the sum of squared daily returns.
3. Compute the volatility scaling factor:

```text
Scaling factor = long-run average realized variance / current monthly realized variance
```

4. Multiply the SOP equity weight by the scaling factor.
5. Reapply the 0% to 150% weight cap.
6. Confirm that only information available at the time is used.

**Investment logic:** The strategy reduces equity exposure when volatility is high and increases exposure when volatility is low, while preserving the SOP return signal.

**Deliverables:**

- Monthly realized variance series
- Volatility scaling factor series
- Volatility-managed SOP weight series
- Comparison of base and volatility-managed weights

---

### Step 16: Build the Main Strategy Comparison Table

Compare four strategies across the full sample and crisis subsamples.

| Strategy | Forecast | Weighting Method |
|---|---|---|
| A | Baseline SOP | Standard Markowitz weights |
| B | Baseline SOP | Volatility-managed weights |
| C | VIX-enhanced SOP | Standard Markowitz weights |
| D | VIX-enhanced SOP | Volatility-managed weights |

Required performance metrics:

- Annualized mean return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Crisis-period Sharpe ratio
- Cumulative return during crisis months
- Average equity allocation

**Deliverables:**

- Main strategy comparison table
- Full-period cumulative wealth chart
- Crisis-period cumulative wealth chart
- Weight-comparison chart

---

### Step 17: Test Statistical and Economic Significance

Use both statistical and investor-welfare tests.

Required tests:

1. **Jobson and Korkie (1981) test with Memmel (2003) correction**  
   Tests whether Sharpe ratio differences are statistically significant.

2. **Certainty-equivalent return gain**  
   Measures the annual fee an investor would rationally pay to access the strategy instead of the benchmark.

Required comparisons:

- Strategy B versus Strategy A
- Strategy C versus Strategy A
- Strategy D versus Strategy A
- Best SOP strategy versus historical mean strategy

**Deliverables:**

- Sharpe-ratio significance table
- Certainty-equivalent gain table
- Final investor interpretation

---

## 8. Final Output Checklist

The final paper or project submission should include the following tables and figures.

### Required Tables

- Data source and variable definition table
- Replication forecast-performance table for 1927-2007
- Extended-sample forecast-performance table through 2024
- VIX versus Goyal predictor comparison table
- Multiple-growth regression results
- Multiple-reversion results
- Crisis versus non-crisis forecast-performance table
- Crisis-window investor outcome table
- NBER recession versus expansion robustness table
- Strategy comparison table
- Sharpe-ratio significance table
- Certainty-equivalent gain table

### Required Figures

- Return decomposition validation chart
- SOP forecast versus realized return chart
- VIX time-series chart with crisis shading
- Actual P/E versus VIX-implied fair P/E chart
- Crisis drawdown charts
- Full-period cumulative wealth chart
- Crisis-period cumulative wealth chart
- Strategy weight comparison chart

---

## 9. Implementation Standards

All analysis should be conducted in Python.

Recommended libraries:

- `pandas` for data handling
- `numpy` for numerical calculations
- `statsmodels` for regressions
- `matplotlib` for charts
- `scipy` for statistical tests

Implementation rules:

1. Use one reproducible notebook or script sequence.
2. Store raw data separately from cleaned data.
3. Never overwrite raw data.
4. Use clear date alignment conventions.
5. Avoid look-ahead bias in every forecast and trading strategy.
6. Save intermediate datasets for auditability.
7. Comment every major transformation.
8. Export final tables to CSV, Excel, or LaTeX for easy inclusion in the paper.


---

## 10. Six-Week Timeline

| Week | Main Tasks | Expected Output |
|---|---|---|
| Week 1 | Download data, clean variables, construct return components, replicate original sample | Clean dataset and initial replication table |
| Week 2 | Extend data to 2024, run baseline SOP and Goyal predictor benchmarks | Extended-sample benchmark table |
| Week 3 | Download VIX, estimate VIX multiple-growth and multiple-reversion models | VIX versus Goyal results |
| Week 4 | Run crisis analysis and investor-level drawdown/return comparisons | Crisis performance tables and charts |
| Week 5 | Estimate trading strategies and volatility-managed overlays | Strategy comparison and CE gain tables |
| Week 6 | Write final paper, refine charts/tables, prepare presentation | Final submission package |

---

## 11. Main Contribution Statement

The project contributes to the return-forecasting literature and investor decision-making in three ways.

First, it tests whether the SOP method of Ferreira and Santa-Clara (2011) remains effective in data updated through 2024. Second, it evaluates whether a forward-looking risk sentiment measure, the VIX, improves forecasts of the multiple-growth component. Third, it translates forecast improvements into practical portfolio outcomes using crisis-period performance, drawdown protection, Sharpe ratios, and volatility-managed trading strategies.

The strongest final paper will clearly distinguish between statistical forecasting gains and actual investor value. A model that improves out-of-sample R-squared but does not improve drawdowns, Sharpe ratios, or certainty-equivalent returns should be treated cautiously. Conversely, a model with modest statistical gains but strong crisis-period capital preservation may still be valuable for investors.

---

## 12. Final Research Question for the Paper

> Can an updated Sum-of-the-Parts forecasting model improve equity risk premium forecasts and investor portfolio outcomes through 2024, and does adding VIX-based multiple-growth information strengthen performance during periods of market stress?
