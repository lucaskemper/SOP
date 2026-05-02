# SOP Report: Return Forecasting, Portfolio Translation, and Regime Diagnostics

This repository is a complete empirical workflow for SOP-style equity return forecasting, benchmark comparison, regime analysis, and forecast-to-portfolio translation. The work is implemented as one executable notebook and a set of generated CSV and figure artifacts.

The center of the project is [SOP.ipynb](SOP.ipynb), which loads raw inputs, engineers features, runs forecasting experiments, computes portfolio outcomes, and exports all report tables and charts.

## 1. What Is In This Repo

### Core implementation
- [SOP.ipynb](SOP.ipynb): Full pipeline from data load to final exports.
- [agoyal_data.xlsx](agoyal_data.xlsx): Main source workbook used by the notebook.
- [README.md](README.md): This report.

### Main generated data products
- [sop_monthly_enriched.csv](sop_monthly_enriched.csv): Master monthly panel used downstream.
- [sop_data_source_audit.csv](sop_data_source_audit.csv): Variable-level source traceability.
- [sop_descriptive_stats.csv](sop_descriptive_stats.csv): Distributional summary of key inputs and constructed variables.

### Forecast evaluation outputs
- [sop_benchmark_results.csv](sop_benchmark_results.csv)
- [sop_benchmark_full_sample.csv](sop_benchmark_full_sample.csv)
- [sop_benchmark_available_sample.csv](sop_benchmark_available_sample.csv)
- [sop_vix_common_results.csv](sop_vix_common_results.csv)
- [sop_vix_common_forecasts.csv](sop_vix_common_forecasts.csv)
- [sop_vix_dm_tests.csv](sop_vix_dm_tests.csv)
- [sop_reversion_results.csv](sop_reversion_results.csv)
- [sop_crisis_forecast.csv](sop_crisis_forecast.csv)
- [sop_crisis_definition_overlap.csv](sop_crisis_definition_overlap.csv)

### Portfolio evaluation outputs
- [sop_strategy_matched_results.csv](sop_strategy_matched_results.csv)
- [sop_abcd_returns_matched.csv](sop_abcd_returns_matched.csv)
- [sop_crisis_portfolio_outcomes.csv](sop_crisis_portfolio_outcomes.csv)
- [sop_mean_excess_tests_matched.csv](sop_mean_excess_tests_matched.csv)

### Robustness and near-term forecast outputs
- [sop_robustness.csv](sop_robustness.csv)
- [sop_last12_forecasts.csv](sop_last12_forecasts.csv)

### Figures
- [fig_cum_mse_gain.png](fig_cum_mse_gain.png)
- [fig_oos_r2_comparison.png](fig_oos_r2_comparison.png)
- [fig_sop_components.png](fig_sop_components.png)
- [fig_strategy_cum_wealth_matched.png](fig_strategy_cum_wealth_matched.png)
- [fig_strategy_weights_matched.png](fig_strategy_weights_matched.png)
- [vix_crisis_chart.png](vix_crisis_chart.png)

## 2. How The Files Work Together

The pipeline is linear and auditable:

1. Raw ingest and source audit
- Input: [agoyal_data.xlsx](agoyal_data.xlsx)
- Optional augmentation: FRED series (cached or downloaded by notebook settings)
- Output: [sop_data_source_audit.csv](sop_data_source_audit.csv)

2. Feature construction and benchmark setup
- SOP decomposition components are built in the monthly panel.
- The historical-mean benchmark is constructed once and reused in all forecast cells.
- Output: [sop_monthly_enriched.csv](sop_monthly_enriched.csv)

3. Forecast model comparisons
- Baseline SOP vs cleaned benchmark predictors.
- VIX-enhanced and alternative enhanced variants on a strict common sample.
- Output: [sop_benchmark_results.csv](sop_benchmark_results.csv), [sop_vix_common_results.csv](sop_vix_common_results.csv), [sop_vix_dm_tests.csv](sop_vix_dm_tests.csv)

4. Regime-specific forecast diagnostics
- Fixed crisis windows and dynamic VIX greater than 25 splits.
- Output: [sop_crisis_forecast.csv](sop_crisis_forecast.csv), [sop_crisis_definition_overlap.csv](sop_crisis_definition_overlap.csv)

5. Forecast-to-portfolio translation
- Forecasts are transformed into strategy weights and returns.
- Matched-sample A/B/C/D portfolio tests plus benchmark portfolios are computed.
- Output: [sop_strategy_matched_results.csv](sop_strategy_matched_results.csv), [sop_abcd_returns_matched.csv](sop_abcd_returns_matched.csv)

6. Statistical and economic strategy diagnostics
- Mean excess-return difference tests.
- Crisis-window portfolio outcomes.
- Output: [sop_mean_excess_tests_matched.csv](sop_mean_excess_tests_matched.csv), [sop_crisis_portfolio_outcomes.csv](sop_crisis_portfolio_outcomes.csv)

7. Stress and sensitivity checks
- Training-window, lagged-input, winsorized, lagged-VIX variants.
- Output: [sop_robustness.csv](sop_robustness.csv)

8. Presentation exports
- Last-12 forecast table and figures.
- Output: [sop_last12_forecasts.csv](sop_last12_forecasts.csv) plus all png files.

## 3. Notebook Architecture And Execution Stages

[SOP.ipynb](SOP.ipynb) currently contains 31 cells with a fully executed run state. The functional stages are:

- Stage A: Settings and imports.
- Stage B: Utility functions and forecasting helpers.
- Stage C: Data loading, source merge logic, and source audit export.
- Stage D: SOP component construction, target alignment, historical-mean benchmark construction.
- Stage E: Descriptive stats export.
- Stage F: Benchmark forecast comparisons and separated full-sample vs available-sample outputs.
- Stage G: VIX-enhanced common-sample experiment and loss-difference tests.
- Stage H: Reversion extension table (reported as exploratory).
- Stage I: Crisis forecast splits and overlap table.
- Stage J: Portfolio helper functions and matched-sample strategy outputs.
- Stage K: Crisis portfolio outcomes with small-N annualized-metric suppression.
- Stage L: Mean excess-return difference tests.
- Stage M: Robustness suite.
- Stage N: Figures and last-12 export.

## 4. Methodological Design Choices In This Version

The repository currently reflects these intentional choices:

- Annual non-overlap SOP evaluation was removed.
- Forecast tables and portfolio tables are separated by design.
- A single historical-mean benchmark is used consistently across forecast evaluation cells.
- VIX-based regime classification requires VIX availability, so overlap counts are computed on VIX-observed rows.
- For crisis windows with N less than 12, annualized volatility, Sharpe, and CEQ are left blank intentionally.
- Strategy-level inference is framed as mean excess-return difference tests, not as a renamed Sharpe test.
- Portfolio weights allow moderate leverage with explicit bounds.

## 5. Data Coverage And Panel Facts

From [sop_monthly_enriched.csv](sop_monthly_enriched.csv):

- Rows: 1,848
- Columns: 57
- Date range: 1871-01-31 to 2024-12-31

Operationally relevant evaluation windows:

- Long forecast OOS window for primary benchmark table: 1948-01 to 2024-12, N=924.
- Common VIX-enhanced matched forecasting window: 2010-02 to 2024-12, N=179.
- VIX availability overlap table base: 420 rows in total.

## 6. Results In Depth

### 6.1 Baseline SOP vs benchmark predictors
Source: [sop_benchmark_results.csv](sop_benchmark_results.csv)

Key point estimate in the long sample:
- SOP baseline OOS R2 vs historical mean: 0.005767
- MAE gain: 0.000025
- MSE-F: 5.359241

Interpretation:
- The SOP gain is positive but economically modest.
- Among top rows, ep is second but materially lower than SOP on OOS R2.
- Most traditional predictors remain near zero or negative OOS R2 over this long horizon.

### 6.2 VIX-enhanced common-sample forecasting
Source: [sop_vix_common_results.csv](sop_vix_common_results.csv), [sop_vix_dm_tests.csv](sop_vix_dm_tests.csv)

In the common sample (N=179):
- Enhanced SOP: VIXCLS OOS R2 vs historical mean: 0.013373
- Baseline SOP OOS R2 vs historical mean: -0.009666
- Incremental R2 vs baseline SOP: 0.022818

Loss-difference test context:
- VIX-enhanced model has favorable mean loss differences vs dfy, ntis, tbl, and tms enhancements.
- p-values remain above conventional thresholds, so this is directional evidence, not strong statistical confirmation.

### 6.3 Crisis forecast behavior
Source: [sop_crisis_forecast.csv](sop_crisis_forecast.csv), [sop_crisis_definition_overlap.csv](sop_crisis_definition_overlap.csv)

Fixed-window split:
- Crisis: OOS R2 0.020523, N=63.
- Non-crisis: OOS R2 0.002455, N=861.

Dynamic VIX split (VIX-observed rows only):
- Crisis (VIX greater than 25): OOS R2 -0.014450, N=79.
- Non-crisis: OOS R2 0.007315, N=340.

Interpretation:
- Fixed-window crisis labeling and VIX-threshold labeling capture different subsets and produce different conclusions.
- The overlap table confirms this mismatch and is critical for preventing regime-definition confusion.

### 6.4 Matched-sample portfolio outcomes
Source: [sop_strategy_matched_results.csv](sop_strategy_matched_results.csv), [sop_abcd_returns_matched.csv](sop_abcd_returns_matched.csv)

Matched sample: N=179 (2010-02 to 2024-12).

Headline comparisons (all after 15bps/month flat turnover cost):
- Best Sharpe among SOP variants is B: SOP plus vol-managed at 0.937.
- D: VIX-SOP plus vol-managed is close at 0.928.
- Buy-and-hold Sharpe is 0.918 with zero turnover (cost-immune).
- Historical mean plus Markowitz has highest annual return (17.85%) but lower Sharpe than B.

Risk and implementation texture:
- Vol-managed variants reduce volatility and drawdown vs pure Markowitz SOP variants.
- Turnover is substantially higher for vol-managed strategies, so friction sensitivity matters.
- Average weights above 1 reflect leverage usage under the configured bounds.

### 6.5 Inference on strategy differences
Source: [sop_mean_excess_tests_matched.csv](sop_mean_excess_tests_matched.csv)

Across reported pairwise comparisons:
- Mean excess-return difference p-values are weak (range 0.10 to 0.66 after turnover cost; example 0.654, 0.658, 0.601; best case around 0.10).

Interpretation:
- Performance ranking in point estimates should not be overinterpreted as statistically settled.
- The repository is transparent about this and treats portfolio inference cautiously.

### 6.6 Crisis-window portfolio outcomes
Source: [sop_crisis_portfolio_outcomes.csv](sop_crisis_portfolio_outcomes.csv)

Small-N handling:
- COVID (N=3) and Inflation shock (N=10) rows intentionally suppress annualized Sharpe/volatility/CEQ.

Best cumulative return by crisis definition:
- COVID: Buy-and-hold equity performs least negatively by cumulative return.
- Inflation shock: Buy-and-hold equity performs least negatively by cumulative return.
- All fixed crisis months: Buy-and-hold equity performs least negatively by cumulative return.
- VIX greater than 25 months: C: VIX-SOP plus Markowitz has strongest cumulative return.

Interpretation:
- Regime-dependent behavior is heterogeneous, and there is no single strategy dominance across all crisis definitions.

### 6.7 Robustness profile
Source: [sop_robustness.csv](sop_robustness.csv)

Core findings:
- Baseline SOP is strongest around the 240-month training setup in this report context.
- VIX-enhanced variants improve with longer windows in some specifications, but shorter windows can be negative.
- Winsorizing ge and gm improves baseline SOP OOS R2 vs the main baseline point estimate.
- Lagging VIX by one month weakens the VIX-enhanced result relative to contemporaneous VIX setup.

Interpretation:
- Results are somewhat parameter-sensitive but directionally coherent with the main narrative.
- The robustness table is essential for understanding where improvements are stable vs fragile.

### 6.8 Leverage cap robustness
Source: [sop_portfolio_robustness_leverage.csv](sop_portfolio_robustness_leverage.csv)

All six strategies are re-run with a strict 0-100% weight cap (no leverage), holding everything else constant: same 15bps/month turnover cost, same matched sample. **Sharpe ranking is unchanged**: B (0.972) > D (0.942) > Buy-and-hold (0.918) > HM (0.892) > A (0.873) > C (0.821). Removing leverage improves Sharpe for every strategy because volatility falls more than return. The vol-managed strategies' Sharpe advantage is robust to the leverage assumption.

## 7. Practical Reading Guide By Objective

If your objective is forecast comparison:
- Start with [sop_benchmark_results.csv](sop_benchmark_results.csv).
- Then read [sop_vix_common_results.csv](sop_vix_common_results.csv) and [sop_vix_dm_tests.csv](sop_vix_dm_tests.csv).

If your objective is portfolio selection:
- Start with [sop_strategy_matched_results.csv](sop_strategy_matched_results.csv).
- Then inspect [sop_mean_excess_tests_matched.csv](sop_mean_excess_tests_matched.csv).
- Use [sop_abcd_returns_matched.csv](sop_abcd_returns_matched.csv) for custom backtests.

If your objective is crisis behavior:
- Pair [sop_crisis_forecast.csv](sop_crisis_forecast.csv) with [sop_crisis_definition_overlap.csv](sop_crisis_definition_overlap.csv).
- Then inspect [sop_crisis_portfolio_outcomes.csv](sop_crisis_portfolio_outcomes.csv).

If your objective is reliability and reproducibility:
- Review [sop_data_source_audit.csv](sop_data_source_audit.csv), [sop_robustness.csv](sop_robustness.csv), and [sop_monthly_enriched.csv](sop_monthly_enriched.csv).


## 8. Caveats And Limits

- Forecast R2 gains are small in absolute magnitude, even when positive.
- Several inference p-values are weak, limiting strong claims about strategy superiority.
- A flat 15bps per month turnover cost is applied to all strategy returns (deducted as 15bps times absolute weight change each month); no financing costs, taxes, slippage, or market impact beyond this friction proxy.
- Leverage is allowed by construction, which can inflate both upside and downside outcomes depending on regime.
- Regime-definition choice materially changes crisis conclusions.

