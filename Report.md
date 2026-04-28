# SOP Research Results and Discussion

**Scope.** This report analyzes the uploaded project files: the README, the executed `SOP.ipynb` notebook, and the seven uploaded CSV outputs. The README references additional artifacts that were not included in the upload bundle, so this report treats the notebook outputs as evidence where a referenced CSV was not available as a standalone file.

## 1. Executive summary

The project is an empirical workflow for **sum-of-parts (SOP) equity-return forecasting**, forecast benchmarking, regime diagnostics, and forecast-to-portfolio translation. The core forecasting object is a one-month-ahead log return forecast built from a dividend-price term and a smoothed earnings-growth term. The notebook then tests whether additional predictors, especially VIX, improve the SOP model and whether the forecasts translate into portfolio value.

The main empirical result is **positive but small forecast improvement**. In the long 1948-2024 out-of-sample window, SOP beats the historical-mean benchmark with an OOS R² of **0.577%**, reducing RMSE by only **1.22 basis points** of monthly log return. This is meaningful as a forecast-ranking result because most traditional predictors are near zero or negative, but it is not a large standalone forecasting edge.

The VIX-enhanced SOP result is stronger on the matched modern sample. Over 2010-02 to 2024-12, VIX-enhanced SOP has an OOS R² of **1.337%** versus the historical mean and **2.282%** versus baseline SOP. However, Diebold-Mariano-style loss tests in the notebook have p-values from about 0.204 to 0.473, so the VIX result is best read as **directionally favorable but not statistically decisive**.

Portfolio results are more economically visible than forecast results. In the 179-month matched strategy sample, **B: SOP + vol-managed** has the highest Sharpe ratio (**0.956**) and **Historical mean + Markowitz** has the highest annual return (**17.87%**). Buy-and-hold has a lower annual return (**14.32%**) but a high Sharpe (**0.918**) and the lowest drawdown among the broad full-sample strategies. The forecast-driven strategies therefore add return mostly through higher average equity exposure and leverage, not through a clean, statistically proven alpha.

The crisis evidence is mixed. Fixed crisis windows favor the SOP forecast in forecasting metrics, but VIX>25 months show negative SOP forecast R². Portfolio performance also changes sharply by crisis definition: buy-and-hold is least bad in COVID, the inflation shock, and all fixed crisis months combined, while VIX-SOP Markowitz performs best in VIX>25 months. The regime labels are not interchangeable.

The biggest caveat is implementation realism. The portfolio tests allow weights up to 1.5x equity exposure and do not deduct transaction costs, taxes, financing spreads, slippage, or market impact. Vol-managed strategies improve Sharpe and drawdown, but they have much higher turnover. The report’s practical conclusion is therefore: **SOP is a useful structured forecasting signal, VIX augmentation is promising, but the investable edge needs transaction-cost, financing, and real-time data-release validation before being treated as production-ready.**

## 2. Files analyzed

| file                              | role                                   |
|:----------------------------------|:---------------------------------------|
| README.md                         | project README / prior report context  |
| SOP.ipynb                         | executable notebook (31 cells)         |
| sop_abcd_returns_matched.csv      | tabular output (179 rows x 14 columns) |
| sop_benchmark_results.csv         | tabular output (15 rows x 12 columns)  |
| sop_crisis_portfolio_outcomes.csv | tabular output (24 rows x 15 columns)  |
| sop_last12_forecasts.csv          | tabular output (12 rows x 10 columns)  |
| sop_robustness.csv                | tabular output (13 rows x 12 columns)  |
| sop_strategy_matched_results.csv  | tabular output (6 rows x 12 columns)   |
| sop_vix_common_results.csv        | tabular output (6 rows x 12 columns)   |

The notebook contains **31 cells** and a fully executed run state. Several important tables are visible in the notebook output even though their CSV files were not part of the uploaded bundle, including the source audit, descriptive statistics, VIX loss-difference tests, reversion extension, crisis forecast table, and mean excess-return tests.

## 3. Methodology reconstructed from the notebook

### 3.1 Data and timing

The data pipeline begins with the Goyal-Welch monthly and annual workbook, merges available FRED-style macro/market series from cache or API, and optionally supports a Shiller extension. In the executed notebook, the Goyal monthly panel spans **1871-01-31 to 2024-12-31** with **1,848 monthly rows**; the annual sheet spans **1871 to 2024** with **154 annual rows**. The forecast target is aligned so that row `t` forecasts the return at row `t+1`.

The operational settings recovered from the notebook are:

| setting | value | interpretation |
|---|---:|---|
| Forecast start | 1948-01-31 | first long-window OOS target month |
| Minimum training window | 240 months | 20-year initial training period |
| Shrinkage intensity | 1200 | univariate slopes are heavily shrunk |
| Rolling variance window | 60 months | 5-year realized variance for portfolio sizing |
| Markowitz gamma | 2.0 | risk-aversion parameter for weights |
| Weight bounds | 0.0 to 1.5 | no short equity; max 150% equity exposure |
| Vol-management scale bounds | 0.25 to 4.0 | limits inverse-volatility scaling |

### 3.2 SOP forecast construction

The notebook decomposes realized log returns into three components:

```text
r_log_t ≈ dp_t + ge_t + gm_t
```

where `dp` is a monthly dividend-price term, `ge` is earnings growth, and `gm` is the growth in the price-earnings multiple. The baseline SOP forecast is:

```text
ms_t = gs_t + dp_t
```

where `gs_t` is a rolling average of `ge` using the configured training window. This means baseline SOP intentionally forecasts the next return using a stable earnings-growth estimate plus the current dividend-price term, while leaving multiple growth unforecasted unless an enhancement is added.

The VIX-enhanced variant forecasts future multiple growth using a shrunk univariate expanding-window regression of future `gm` on VIX. The enhanced forecast takes the form:

```text
ms_enh_VIX_t = gs_t + dp_t + forecast(gm_{t+1} | VIX_t)
```

The same shrunk univariate method is used for benchmark predictors and alternative enhanced SOP variants. The shrinkage rule pulls the slope toward zero by multiplying the estimated slope by `n / (n + 1200)`, which is conservative; even with 240 observations, the slope is only about one-sixth of the unshrunk estimate.

### 3.3 Forecast metrics

The primary forecasting metric is out-of-sample R² versus the historical mean:

```text
OOS R² = 1 - MSE_model / MSE_historical_mean
```

Positive values mean the model has lower squared forecast error than the expanding historical mean. The notebook also reports MSE, MAE, MAE gain, and an MSE-F-style statistic computed from the model and benchmark MSEs. Because monthly equity-return forecasting is noisy, values near zero should not be overinterpreted.

### 3.4 Portfolio translation

Forecasts are converted into equity weights using a mean-variance/Markowitz rule:

```text
weight_t = (expected_simple_return_t - risk_free_t) / (gamma * rolling_variance_t)
```

Weights are clipped between 0 and 1.5. Vol-managed strategies multiply the Markowitz weight by an inverse-volatility scale before clipping. The portfolio return is then a mix of next-month equity return and next-month risk-free return:

```text
portfolio_return_{t+1} = weight_t * equity_return_{t+1} + (1 - weight_t) * rf_{t+1}
```

The notebook explicitly uses realized equity variance only through date `t`, not `t+1`, which is an important no-lookahead design choice.

## 4. Data coverage and descriptive facts

The source audit in the notebook shows that the core Goyal-Welch variables cover the full 1,848 monthly rows. FRED-derived coverage differs by series: VIX has 420 non-null observations, TB3MS has 1,092, CPIAUCSL has 936, SP500 has 104, and USREC has full monthly coverage in the enriched panel. The Shiller extension had zero non-null rows in the executed run because the Goyal workbook already reached the target end date.


Source audit summary from the notebook:

| variable | source | non-null rows |
|:--|:--|--:|
| price, d12, e12, ret, retx, rfree, Goyal predictors | Amit Goyal-Welch workbook | 1,848 |
| Shiller price/dividend/earnings extension | Robert Shiller data | 0 |
| SP500 | FRED cached in `sop_monthly_enriched.csv` | 104 |
| CPIAUCSL | FRED cached in `sop_monthly_enriched.csv` | 936 |
| TB3MS | FRED cached in `sop_monthly_enriched.csv` | 1,092 |
| VIXCLS | FRED cached in `sop_monthly_enriched.csv` | 420 |
| USREC | FRED cached in `sop_monthly_enriched.csv` | 1,848 |

Key descriptive statistics from the notebook are:

| variable   |   count |    mean |    std |     min |   median |     max |   skew |   kurt |
|:-----------|--------:|--------:|-------:|--------:|---------:|--------:|-------:|-------:|
| r_log      |    1188 |  0.0082 | 0.0537 | -0.3389 |   0.0131 |  0.3466 |  -0.48 |   7.66 |
| dp         |    1848 |  0.0035 | 0.0015 |  0.0009 |   0.0035 |  0.0127 |   0.57 |   1.31 |
| ge         |    1847 |  0.0034 | 0.0368 | -0.5283 |   0.0055 |  0.7039 |   1.9  | 114.38 |
| gm         |    1847 |  0.0005 | 0.0574 | -0.7238 |   0.0009 |  0.5361 |  -0.53 |  23.86 |
| gs         |    1608 |  0.0034 | 0.0027 | -0.0054 |   0.004  |  0.0087 |  -0.65 |  -0.29 |
| ms         |    1608 |  0.0068 | 0.0026 | -0.0028 |   0.0069 |  0.0143 |  -0.29 |   0.41 |
| hist_mean  |     949 |  0.0074 | 0.0009 |  0.0041 |   0.0077 |  0.0088 |  -1.88 |   3.59 |
| VIXCLS     |     420 | 19.5389 | 7.5035 |  9.51   |  17.665  | 59.89   |   1.71 |   4.47 |
| dfy        |    1272 |  0.0117 | 0.0068 |  0.0032 |   0.0094 |  0.0564 |   2.2  |   7.52 |
| ntis       |    1177 |  0.0153 | 0.0258 | -0.056  |   0.0156 |  0.177  |   1.61 |   7.73 |
| tbl        |    1260 |  0.0336 | 0.0295 |  0.0001 |   0.0304 |  0.163  |   1.1  |   1.6  |
| tms        |    1260 |  0.0155 | 0.0132 | -0.0365 |   0.0156 |  0.0455 |  -0.12 |  -0.08 |

Several details matter for interpretation. First, realized monthly log returns are fat-tailed: `r_log` has kurtosis of about 7.66. Second, the SOP forecast itself is much smoother than realized returns: `ms` has a standard deviation of about 0.0026, versus 0.0537 for `r_log`. Third, `ge` and `gm` are highly non-normal, with extreme skew/kurtosis, which explains why the notebook includes winsorized robustness checks.

## 5. Long-sample forecast results

The benchmark table covers the primary long OOS sample from **1948-01-31 to 2024-12-31** with **924 monthly forecast observations**. The combined uploaded benchmark CSV contains a duplicate SOP baseline row because the notebook concatenates full-sample and available-sample benchmark outputs; the analytical conclusion is unaffected.

| model        |   N | start      | end        | OOS R2 vs HM   |      MSE |   HM MSE |   MAE gain (bp) |   MSE-F |
|:-------------|----:|:-----------|:-----------|:---------------|---------:|---------:|----------------:|--------:|
| SOP baseline | 924 | 1948-01-31 | 2024-12-31 | 0.577%         | 0.001771 | 0.001781 |            0.25 |   5.359 |
| ep           | 924 | 1948-01-31 | 2024-12-31 | 0.269%         | 0.001776 | 0.001781 |           -0.99 |   2.489 |
| dy           | 924 | 1948-01-31 | 2024-12-31 | 0.046%         | 0.00178  | 0.001781 |           -1.79 |   0.422 |
| dp_gw        | 924 | 1948-01-31 | 2024-12-31 | 0.042%         | 0.00178  | 0.001781 |           -1.12 |   0.389 |
| infl         | 924 | 1948-01-31 | 2024-12-31 | 0.033%         | 0.00178  | 0.001781 |            0.26 |   0.309 |
| ntis         | 924 | 1948-01-31 | 2024-12-31 | 0.024%         | 0.00178  | 0.001781 |            1.19 |   0.223 |
| bm           | 924 | 1948-01-31 | 2024-12-31 | -0.014%        | 0.001781 | 0.001781 |           -2.13 |  -0.128 |
| dfy          | 924 | 1948-01-31 | 2024-12-31 | -0.036%        | 0.001781 | 0.001781 |           -0.13 |  -0.334 |
| ltr          | 924 | 1948-01-31 | 2024-12-31 | -0.040%        | 0.001782 | 0.001781 |           -0.49 |  -0.366 |
| tms          | 924 | 1948-01-31 | 2024-12-31 | -0.064%        | 0.001782 | 0.001781 |            0.08 |  -0.588 |
| dfr          | 924 | 1948-01-31 | 2024-12-31 | -0.073%        | 0.001782 | 0.001781 |           -0.16 |  -0.676 |
| tbl          | 924 | 1948-01-31 | 2024-12-31 | -0.076%        | 0.001782 | 0.001781 |           -0.01 |  -0.7   |
| svar         | 924 | 1948-01-31 | 2024-12-31 | -0.086%        | 0.001782 | 0.001781 |           -0.04 |  -0.797 |
| de           | 924 | 1948-01-31 | 2024-12-31 | -0.379%        | 0.001788 | 0.001781 |            0.08 |  -3.485 |

The baseline SOP model is the best performer in the long-sample table. Its OOS R² is **0.577%**, with MSE of **0.001771** versus historical-mean MSE of **0.001781**. This is a small absolute reduction in loss, but it is notable because many standard predictors have negative OOS R².

The strongest conventional predictor is `ep`, with OOS R² of **0.269%**, but it still trails SOP. Dividend yield (`dy`) and dividend-price (`dp_gw`) are barely positive. Variables such as `de`, `svar`, `tbl`, `dfr`, and `tms` underperform the historical mean on squared error. This pattern supports the project’s central premise: the structured SOP decomposition provides a more durable signal than isolated traditional predictors in this implementation.

The MAE evidence is weaker than the MSE evidence. SOP’s MAE gain is only **0.25 basis points** of monthly log return, while some models with near-zero or negative OOS R² have small positive MAE gains. That means SOP’s advantage is more visible in squared-error loss than in absolute-error loss, and the result may depend on how larger forecast misses are weighted.

## 6. VIX-enhanced forecasting results

The VIX-enhanced experiment uses a strict common sample from **2010-02-28 to 2024-12-31**, requiring all compared forecasts to be available on the same dates. This is the right design because it avoids giving one model an easier sample.

| model                |   N | start      | end        | OOS R2 vs HM   | R2 vs baseline SOP   |   MAE gain (bp) |   MSE-F |
|:---------------------|----:|:-----------|:-----------|:---------------|:---------------------|----------------:|--------:|
| Enhanced SOP: VIXCLS | 179 | 2010-02-28 | 2024-12-31 | 1.337%         | 2.282%               |           -0.76 |   2.426 |
| Enhanced SOP: ntis   | 179 | 2010-02-28 | 2024-12-31 | 0.116%         | 1.072%               |            3.27 |   0.208 |
| Enhanced SOP: tms    | 179 | 2010-02-28 | 2024-12-31 | -0.506%        | 0.456%               |           -0.36 |  -0.901 |
| Enhanced SOP: dfy    | 179 | 2010-02-28 | 2024-12-31 | -0.822%        | 0.143%               |           -4.08 |  -1.46  |
| Enhanced SOP: tbl    | 179 | 2010-02-28 | 2024-12-31 | -0.823%        | 0.142%               |           -1.63 |  -1.462 |
| Baseline SOP         | 179 | 2010-02-28 | 2024-12-31 | -0.967%        |                      |           -2.25 |  -1.714 |

The VIX-enhanced SOP model is clearly the top model in this common sample. It improves on historical mean by **1.337%** and improves on baseline SOP by **2.282%**. Baseline SOP is negative in this modern sample, with OOS R² of **-0.967%**, so the VIX enhancement does two things: it restores positive performance versus the historical mean and it materially improves versus baseline SOP.

However, the VIX model does not dominate every loss perspective. Its MAE gain versus historical mean is negative (**-0.76 bp**), while the NTIS-enhanced model has a positive MAE gain. This suggests VIX’s advantage is concentrated in reducing larger squared errors rather than improving the typical absolute forecast error.

### 6.1 Loss-difference tests

The notebook compares VIX-enhanced SOP against alternative enhanced models using HAC/Newey-West-style loss-difference tests.

| comparison                   |   N |   mean loss diff |   t-stat |   p-value |
|:-----------------------------|----:|-----------------:|---------:|----------:|
| ms_enh_VIXCLS vs ms_enh_dfy  | 179 |          3.8e-05 |    1.276 |     0.204 |
| ms_enh_VIXCLS vs ms_enh_ntis | 179 |          2.2e-05 |    0.719 |     0.473 |
| ms_enh_VIXCLS vs ms_enh_tbl  | 179 |          3.8e-05 |    1.229 |     0.221 |
| ms_enh_VIXCLS vs ms_enh_tms  | 179 |          3.3e-05 |    1.095 |     0.275 |

All mean loss differences are positive, meaning VIX has lower squared loss than the comparison model under the notebook’s sign convention. But the p-values are above conventional thresholds. The best p-value is about **0.204** versus the DFY-enhanced model. That supports a cautious interpretation: VIX is a promising conditioning variable, but the test does not establish a statistically decisive edge over the alternatives in the 179-month common sample.

### 6.2 Reversion extension

The notebook also evaluates an exploratory two-stage reversion extension based on valuation-level residuals. The notebook itself warns that the residual appears non-stationary in some tests and does not treat the reversion model as reliable evidence.

| model                 |   N | start      | end        | OOS R2 vs HM   |   MAE gain (bp) |
|:----------------------|----:|:-----------|:-----------|:---------------|----------------:|
| Reversion SOP: VIXCLS | 179 | 2010-02-28 | 2024-12-31 | 0.247%         |            0.32 |
| Baseline SOP          | 179 | 2010-02-28 | 2024-12-31 | -0.967%        |           -2.25 |
| Reversion SOP: dfy    | 179 | 2010-02-28 | 2024-12-31 | -1.597%        |           -4.44 |
| Reversion SOP: ntis   | 179 | 2010-02-28 | 2024-12-31 | -1.786%        |           -5.12 |

The VIX reversion variant is positive, but weaker than the direct VIX-enhanced model. DFY and NTIS reversion variants are negative. The right takeaway is that simple VIX conditioning on multiple growth is more compelling than the more elaborate reversion setup, at least in this run.

## 7. Crisis and regime forecast behavior

The notebook tests two crisis definitions: fixed historical windows and an ex-ante VIX>25 rule. These definitions are materially different.

| definition              | regime     |   N | start      | end        | OOS R2 vs HM   |   MAE gain (bp) |
|:------------------------|:-----------|----:|:-----------|:-----------|:---------------|----------------:|
| Fixed windows           | Crisis     |  63 | 2000-03-31 | 2022-10-31 | 2.052%         |            4.13 |
| Fixed windows           | Non-crisis | 861 | 1948-01-31 | 2024-12-31 | 0.246%         |           -0.03 |
| VIX>25 at forecast date | Crisis     |  79 | 1990-02-28 | 2022-11-30 | -1.445%        |           -7.97 |
| VIX>25 at forecast date | Non-crisis | 340 | 1990-03-31 | 2024-12-31 | 0.732%         |           -0.31 |

Under fixed windows, SOP performs better in crisis months than non-crisis months: crisis OOS R² is **2.052%**, compared with **0.246%** outside fixed crisis windows. Under the VIX>25 definition, the result flips: VIX>25 crisis months have **-1.445%** OOS R², while non-crisis VIX-observed months have **0.732%** OOS R².

The overlap table in the notebook explains why these conclusions diverge. Among 420 VIX-observed rows, only 31 rows are both fixed-crisis and VIX>25. There are 48 VIX>25 months outside fixed crisis windows and 32 fixed-crisis months without VIX>25. Therefore, “crisis” is not a single empirical object here. Fixed windows capture named historical episodes; the VIX rule captures elevated-volatility states, including non-crisis stress months.

The practical implication is that strategy evaluation should not claim generic “crisis alpha” without specifying the regime definition. The SOP signal behaves differently depending on whether crisis means historical event windows or current high volatility.

## 8. Portfolio results on the matched sample

The matched strategy sample runs from **2010-02-28 to 2024-12-31** with **179 monthly observations**. Six strategies are compared: four SOP/VIX-SOP variants plus historical-mean Markowitz and buy-and-hold equity.

| strategy                    |   N | start      | end        | annual return   | annual vol   |   Sharpe | cum return   | max drawdown   |   avg weight |   turnover | CEQ gamma=3 ann   |
|:----------------------------|----:|:-----------|:-----------|:----------------|:-------------|---------:|:-------------|:---------------|-------------:|-----------:|:------------------|
| A: SOP + Markowitz          | 179 | 2010-02-28 | 2024-12-31 | 16.77%          | 19.93%       |    0.826 | 910.30%      | -33.64%        |        1.317 |      0.02  | 10.50%            |
| B: SOP + vol-managed        | 179 | 2010-02-28 | 2024-12-31 | 16.95%          | 16.77%       |    0.956 | 933.48%      | -25.86%        |        1.282 |      0.178 | 11.82%            |
| C: VIX-SOP + Markowitz      | 179 | 2010-02-28 | 2024-12-31 | 16.36%          | 20.13%       |    0.801 | 858.92%      | -34.53%        |        1.186 |      0.151 | 10.05%            |
| D: VIX-SOP + vol-managed    | 179 | 2010-02-28 | 2024-12-31 | 16.91%          | 16.83%       |    0.95  | 927.67%      | -26.60%        |        1.211 |      0.215 | 11.75%            |
| Historical mean + Markowitz | 179 | 2010-02-28 | 2024-12-31 | 17.87%          | 20.19%       |    0.865 | 1062.31%     | -31.68%        |        1.348 |      0.01  | 11.34%            |
| Buy-and-hold equity         | 179 | 2010-02-28 | 2024-12-31 | 14.32%          | 14.57%       |    0.918 | 636.55%      | -23.67%        |        1     |      0     | 10.20%            |

Ranked by Sharpe:

| strategy                    | annual return   | annual vol   |   Sharpe | max drawdown   |
|:----------------------------|:----------------|:-------------|---------:|:---------------|
| B: SOP + vol-managed        | 16.95%          | 16.77%       |    0.956 | -25.86%        |
| D: VIX-SOP + vol-managed    | 16.91%          | 16.83%       |    0.95  | -26.60%        |
| Buy-and-hold equity         | 14.32%          | 14.57%       |    0.918 | -23.67%        |
| Historical mean + Markowitz | 17.87%          | 20.19%       |    0.865 | -31.68%        |
| A: SOP + Markowitz          | 16.77%          | 19.93%       |    0.826 | -33.64%        |
| C: VIX-SOP + Markowitz      | 16.36%          | 20.13%       |    0.801 | -34.53%        |

The best Sharpe belongs to **B: SOP + vol-managed** at **0.956**, followed closely by **D: VIX-SOP + vol-managed** at **0.950**. This is the cleanest economic result in the uploaded outputs: volatility management improves risk-adjusted performance for both baseline SOP and VIX-SOP.

But the highest annual return belongs to historical mean + Markowitz (**17.87%**), not to an SOP strategy. Its Sharpe is lower than the vol-managed SOP variants because it uses more leverage and has higher volatility. This means the forecast-driven strategies do not dominate on every objective; they mostly improve the return-volatility tradeoff.

Buy-and-hold is a strong benchmark. It has lower annual return than the forecast-driven strategies, but also lower volatility, zero turnover, and the lowest max drawdown in the full matched sample. This is important because an implementable strategy needs to beat buy-and-hold after friction, not just before friction.

### 8.1 Weight and implementation diagnostics

| strategy                    |   avg weight |   median |   min |   max | months at 1.5 cap   | months at 0   |
|:----------------------------|-------------:|---------:|------:|------:|:--------------------|:--------------|
| A: SOP + Markowitz          |        1.317 |    1.5   | 0.36  |   1.5 | 96/179              | 0/179         |
| B: SOP + vol-managed        |        1.282 |    1.5   | 0.306 |   1.5 | 111/179             | 0/179         |
| C: VIX-SOP + Markowitz      |        1.186 |    1.455 | 0     |   1.5 | 83/179              | 6/179         |
| D: VIX-SOP + vol-managed    |        1.211 |    1.5   | 0     |   1.5 | 107/179             | 6/179         |
| Historical mean + Markowitz |        1.348 |    1.5   | 0.594 |   1.5 | 112/179             | 0/179         |
| Buy-and-hold equity         |        1     |    1     | 1     |   1   | 0/179               | 0/179         |

The weight diagnostics show substantial use of the 1.5x cap. B is at the cap in **111 of 179 months**, D in **107 of 179**, and historical mean Markowitz in **112 of 179**. This matters because leverage is a major contributor to annual returns. The VIX-SOP Markowitz variants also hit zero equity exposure in 6 months, showing that the VIX augmentation can occasionally produce sufficiently low expected excess returns to de-risk completely.

Turnover is another implementation issue. Vol-managed B has turnover of **0.178** per month and D has **0.215** per month, compared with **0.020** for A and **0.010** for historical mean Markowitz. Without transaction costs and financing costs, the vol-managed strategies may look cleaner than they would in production.

### 8.2 Return correlations

| strategy   |     A |     B |     C |     D |    HM |   Buy-hold |
|:-----------|------:|------:|------:|------:|------:|-----------:|
| A          | 1     | 0.911 | 0.981 | 0.916 | 0.993 |      0.974 |
| B          | 0.911 | 1     | 0.875 | 0.978 | 0.917 |      0.926 |
| C          | 0.981 | 0.875 | 1     | 0.904 | 0.98  |      0.961 |
| D          | 0.916 | 0.978 | 0.904 | 1     | 0.92  |      0.912 |
| HM         | 0.993 | 0.917 | 0.98  | 0.92  | 1     |      0.978 |
| Buy-hold   | 0.974 | 0.926 | 0.961 | 0.912 | 0.978 |      1     |

All strategies are highly correlated because they are primarily equity-exposure strategies. The lowest correlations are between C and B/D, reflecting VIX-SOP’s different weight path. Still, even the lowest shown correlations are high. This argues against interpreting the strategies as independent return streams; they are different ways to time and lever the same equity beta.

### 8.3 Statistical tests of strategy differences

The notebook reports HAC/Newey-West-style tests of mean excess-return differences.

| comparison                                          |   N |   Sharpe diff | mean excess diff monthly   |   t-stat |   p-value |
|:----------------------------------------------------|----:|--------------:|:---------------------------|---------:|----------:|
| B vs A: vol-managed SOP vs SOP Markowitz            | 179 |         0.13  | -3.56 bp                   |   -0.271 |     0.786 |
| C vs A: VIX-SOP Markowitz vs SOP Markowitz          | 179 |        -0.025 | -2.72 bp                   |   -0.26  |     0.795 |
| D vs A: VIX-SOP vol-managed vs SOP Markowitz        | 179 |         0.125 | -3.81 bp                   |   -0.298 |     0.766 |
| A vs HM: SOP Markowitz vs historical-mean Markowitz | 179 |        -0.039 | -8.31 bp                   |   -1.627 |     0.105 |

These tests do not support strong statistical claims. B and D have higher Sharpe ratios than A, but their mean excess-return differences versus A are negative in the test table and have very high p-values. A versus historical-mean Markowitz has p≈0.105, which is suggestive but still not conventionally significant. The correct reading is that the point estimates are economically interesting, but strategy superiority is not statistically settled.

## 9. Crisis portfolio outcomes

The crisis portfolio output contains 24 rows: six strategies across COVID, inflation shock, all fixed crisis months, and VIX>25 months. Annualized volatility, Sharpe, and CEQ are intentionally blank for windows with fewer than 12 observations.

Best cumulative-return strategy by crisis definition:

| crisis                  |   N | best cumulative-return strategy   | cum return   | max drawdown   |   avg VIX |
|:------------------------|----:|:----------------------------------|:-------------|:---------------|----------:|
| All fixed crisis months |  13 | Buy-and-hold equity               | -24.96%      | -24.34%        |     28.64 |
| COVID                   |   3 | Buy-and-hold equity               | -9.00%       | -12.20%        |     37.5  |
| Inflation shock         |  10 | Buy-and-hold equity               | -17.55%      | -20.06%        |     25.99 |
| VIX>25 months           |  28 | C: VIX-SOP + Markowitz            | 92.35%       | -18.36%        |     31.1  |

Full crisis portfolio table:

| crisis                  | strategy                    |   N | cum return   | max drawdown   | Sharpe   |   avg weight |
|:------------------------|:----------------------------|----:|:-------------|:---------------|:---------|-------------:|
| COVID                   | A: SOP + Markowitz          |   3 | -14.60%      | -18.36%        |          |        1.5   |
| COVID                   | B: SOP + vol-managed        |   3 | -16.87%      | -9.54%         |          |        0.886 |
| COVID                   | C: VIX-SOP + Markowitz      |   3 | -14.60%      | -18.36%        |          |        1.5   |
| COVID                   | D: VIX-SOP + vol-managed    |   3 | -16.87%      | -9.54%         |          |        0.886 |
| COVID                   | Historical mean + Markowitz |   3 | -14.60%      | -18.36%        |          |        1.5   |
| COVID                   | Buy-and-hold equity         |   3 | -9.00%       | -12.20%        |          |        1     |
| Inflation shock         | A: SOP + Markowitz          |  10 | -27.25%      | -28.74%        |          |        1.458 |
| Inflation shock         | B: SOP + vol-managed        |  10 | -22.09%      | -19.56%        |          |        0.938 |
| Inflation shock         | C: VIX-SOP + Markowitz      |  10 | -26.73%      | -29.70%        |          |        1.5   |
| Inflation shock         | D: VIX-SOP + vol-managed    |  10 | -21.99%      | -20.36%        |          |        0.963 |
| Inflation shock         | Historical mean + Markowitz |  10 | -26.34%      | -26.63%        |          |        1.375 |
| Inflation shock         | Buy-and-hold equity         |  10 | -17.55%      | -20.06%        |          |        1     |
| All fixed crisis months | A: SOP + Markowitz          |  13 | -37.87%      | -35.35%        | -0.891   |        1.467 |
| All fixed crisis months | B: SOP + vol-managed        |  13 | -35.23%      | -29.69%        | -1.766   |        0.926 |
| All fixed crisis months | C: VIX-SOP + Markowitz      |  13 | -37.42%      | -36.22%        | -0.844   |        1.5   |
| All fixed crisis months | D: VIX-SOP + vol-managed    |  13 | -35.15%      | -30.39%        | -1.695   |        0.946 |
| All fixed crisis months | Historical mean + Markowitz |  13 | -37.09%      | -33.44%        | -0.908   |        1.404 |
| All fixed crisis months | Buy-and-hold equity         |  13 | -24.96%      | -24.34%        | -0.844   |        1     |
| VIX>25 months           | A: SOP + Markowitz          |  28 | 75.89%       | -18.36%        | 0.882    |        1.364 |
| VIX>25 months           | B: SOP + vol-managed        |  28 | 35.45%       | -11.40%        | 0.768    |        0.781 |
| VIX>25 months           | C: VIX-SOP + Markowitz      |  28 | 92.35%       | -18.36%        | 0.961    |        1.5   |
| VIX>25 months           | D: VIX-SOP + vol-managed    |  28 | 43.02%       | -11.40%        | 0.845    |        0.836 |
| VIX>25 months           | Historical mean + Markowitz |  28 | 84.42%       | -18.36%        | 0.937    |        1.42  |
| VIX>25 months           | Buy-and-hold equity         |  28 | 60.43%       | -12.20%        | 0.961    |        1     |

The results are heterogeneous. Buy-and-hold loses the least in COVID, inflation shock, and all fixed crisis months. VIX-SOP Markowitz has the best cumulative return during VIX>25 months, with **92.35%** cumulative return across 28 high-VIX months, but it does so at the 1.5x weight cap and with meaningful drawdown exposure.

Vol-managed strategies reduce drawdowns in several stress windows, but they do not always improve cumulative returns. For example, during COVID, B and D have smaller max drawdowns than A/C, but worse cumulative returns. This is a classic cost of de-risking: volatility control can cushion losses but may also reduce rebound capture.

## 10. Robustness checks

The robustness table tests training-window length, lagged fundamentals, winsorized components, and lagged VIX.

| robustness            | model                           |   N | start      | end        | OOS R2 vs HM   |   MAE gain (bp) |   MSE-F |
|:----------------------|:--------------------------------|----:|:-----------|:-----------|:---------------|----------------:|--------:|
| training_window       | Baseline SOP train=60           | 924 | 1948-01-31 | 2024-12-31 | -2.140%        |           -3.6  | -19.36  |
| vix_training_window   | VIX-enhanced SOP train=60       | 359 | 1995-02-28 | 2024-12-31 | -2.708%        |           -4.45 |  -9.466 |
| training_window       | Baseline SOP train=120          | 924 | 1948-01-31 | 2024-12-31 | 0.161%         |            0.3  |   1.491 |
| vix_training_window   | VIX-enhanced SOP train=120      | 299 | 2000-02-29 | 2024-12-31 | -1.222%        |           -1.06 |  -3.609 |
| training_window       | Baseline SOP train=180          | 924 | 1948-01-31 | 2024-12-31 | 0.485%         |            0.89 |   4.499 |
| vix_training_window   | VIX-enhanced SOP train=180      | 239 | 2005-02-28 | 2024-12-31 | 0.692%         |            2.95 |   1.665 |
| training_window       | Baseline SOP train=240          | 924 | 1948-01-31 | 2024-12-31 | 0.577%         |            0.25 |   5.359 |
| vix_training_window   | VIX-enhanced SOP train=240      | 179 | 2010-02-28 | 2024-12-31 | 1.337%         |           -0.76 |   2.426 |
| training_window       | Baseline SOP train=300          | 888 | 1951-01-31 | 2024-12-31 | 0.245%         |           -0.24 |   2.179 |
| vix_training_window   | VIX-enhanced SOP train=300      | 119 | 2015-02-28 | 2024-12-31 | 2.295%         |            2.1  |   2.796 |
| lagged_fundamentals   | Lag D12/E12 by 1m               | 924 | 1948-01-31 | 2024-12-31 | 0.506%         |            0.13 |   4.702 |
| winsorized_components | Winsorize ge/gm 1-99%           | 924 | 1948-01-31 | 2024-12-31 | 0.685%         |            0.46 |   6.37  |
| lagged_vix            | VIX-enhanced with VIX lagged 1m | 178 | 2010-03-31 | 2024-12-31 | 0.517%         |           -1.09 |   0.924 |

The baseline SOP result is sensitive to the training window. A 60-month window is clearly negative, 120 months becomes mildly positive, 180 months improves, 240 months is strongest among the main baseline windows, and 300 months weakens again. This supports the choice of 240 months but also shows that the baseline edge is not invariant to smoothing choices.

VIX-enhanced results improve with longer training windows in this table: 60 and 120 months are negative, 180 months is positive, 240 months is stronger, and 300 months is strongest at **2.295%** OOS R². The caveat is that longer VIX training windows reduce the sample size: the 300-month result has only 119 observations from 2015-02 to 2024-12.

The winsorized SOP variant has OOS R² of **0.685%**, better than the main baseline’s **0.577%**. This is a useful finding because the descriptive statistics show extreme tails in `ge` and `gm`. Winsorization appears to stabilize the signal without changing the model’s basic economic structure.

The lagged-fundamentals variant remains positive at **0.506%**, which is encouraging for real-time implementability. The lagged-VIX variant remains positive at **0.517%**, but it is much weaker than contemporaneous VIX-enhanced SOP at **1.337%**. That gap is important: it raises a possible real-time timing concern, because contemporaneous VIX at month-end may be easier to justify than contemporaneous fundamentals, but the exact tradability depends on when signals are formed and when positions are implemented.

## 11. Last-12 forecast inspection

The uploaded last-12 table covers forecast rows dated 2024-01-31 through 2024-12-31. The final row has no realized `ret_lead` because it would require the next target month beyond the panel.

Forecast error summary for the 11 realized target months:

| forecast      | avg forecast   | bias vs realized   | MAE   |      MSE |
|:--------------|:---------------|:-------------------|:------|---------:|
| ms_enh_ntis   | 1.04%          | -0.89%             | 2.77% | 0.000996 |
| hist_mean     | 0.81%          | -1.12%             | 2.89% | 0.001054 |
| ms_enh_VIXCLS | 0.49%          | -1.44%             | 3.01% | 0.001086 |
| ms_lagfund    | 0.65%          | -1.28%             | 2.96% | 0.001089 |
| ms            | 0.64%          | -1.29%             | 2.96% | 0.00109  |
| ms_winsor     | 0.61%          | -1.32%             | 2.98% | 0.001099 |
| ms_enh_dfy    | 0.45%          | -1.48%             | 3.05% | 0.00114  |

The realized 2024 target months in the table had an average log return of about **1.93%**, while all forecast variants averaged below that. In other words, the models were directionally positive but too conservative during this period. NTIS-enhanced SOP had the lowest MSE and MAE among the listed 2024 forecasts, despite VIX-enhanced SOP being the best in the broader 2010-2024 common-sample test.

Last five rows for inspection:

| date       | forecast_target_date   | ret_lead   | hist_mean   | ms    | ms_enh_VIXCLS   | ms_enh_ntis   | ms_winsor   |
|:-----------|:-----------------------|:-----------|:------------|:------|:----------------|:--------------|:------------|
| 2024-08-31 | 2024-09-30             | 2.26%      | 0.81%       | 0.63% | 0.47%           | 1.02%         | 0.59%       |
| 2024-09-30 | 2024-10-31             | -0.87%     | 0.82%       | 0.62% | 0.59%           | 1.01%         | 0.59%       |
| 2024-10-31 | 2024-11-30             | 5.87%      | 0.81%       | 0.63% | 1.03%           | 1.00%         | 0.59%       |
| 2024-11-30 | 2024-12-31             | -2.37%     | 0.82%       | 0.63% | 0.38%           | 0.95%         | 0.59%       |
| 2024-12-31 |                        |            | 0.82%       | 0.64% | 0.64%           | 0.95%         | 0.60%       |

The 2024 snapshot reinforces a broader point: short windows can tell a different story from full evaluation windows. A model can be best over 179 months and still not be best over the latest 11 realized months.

## 12. Discussion: what the evidence supports

### 12.1 The SOP decomposition is useful, but its edge is small

The long-sample benchmark result supports SOP as a robust structured predictor. It beats the historical mean and ranks above common standalone predictors. But the magnitude is small. A **0.577%** OOS R² is valuable in equity-return forecasting, where even small improvements are hard to obtain, yet it does not by itself imply a large economic edge.

The decomposition’s main advantage is that it imposes economic structure. Instead of asking a single predictor to forecast returns directly, SOP splits returns into dividend yield, earnings growth, and multiple growth. That likely reduces noise and helps explain why it beats individual predictors like `ep`, `dy`, `dfy`, and `tms`.

### 12.2 VIX helps, but mostly as a squared-error improvement

VIX-enhanced SOP is the strongest modern-sample forecast. Its incremental R² versus baseline SOP is meaningful. But the MAE and DM-test evidence warns against overselling it. The model appears to reduce larger errors more than it reduces average absolute errors, and the formal pairwise loss-difference tests are not significant.

That interpretation is economically plausible. VIX is most informative when volatility and discount-rate conditions are unusual. Those are exactly the periods where squared-error losses can be large. If VIX mainly improves forecasts in stress or rebound periods, then MSE can improve even when typical monthly MAE does not.

### 12.3 Portfolio gains come from risk management and exposure, not pure alpha

The strategy results show that volatility-managed variants have the best Sharpe and CEQ. This is important, but it is not the same as proving forecast alpha. The strategies remain highly correlated with buy-and-hold and often sit at the leverage cap. Forecasts are being translated into dynamic beta and leverage decisions.

The most practical interpretation is that SOP and VIX-SOP are **risk-budgeting signals**. They help decide when to scale exposure, but the strategies still depend heavily on equity risk premia and leverage. Any real deployment would need to model borrowing costs, margin requirements, ETF/futures implementation costs, and tax effects.

### 12.4 Regime conclusions depend on labels

Fixed crisis windows and VIX>25 months produce different forecast conclusions and different portfolio conclusions. This is not a bug; it is a substantive finding. Named crises include periods of both panic and recovery, while VIX>25 focuses on contemporaneous high-volatility states. Forecast and portfolio results should be reported separately for these regimes rather than merged into one generic crisis statement.

### 12.5 Robustness is encouraging but not complete

The lagged-fundamentals and winsorized variants are useful because they address two common criticisms: data-release timing and outlier sensitivity. The fact that both remain positive strengthens the baseline SOP evidence. The lagged-VIX result is also positive, but much weaker than the contemporaneous VIX result, so VIX timing should receive more scrutiny.

## 13. Limitations and threats to validity

1. **Missing transaction costs and financing costs.** The strategy table is gross of costs. Because B and D have materially higher turnover and all Markowitz variants allow leverage, cost assumptions could change rankings.

2. **Leverage-driven performance.** Many strategies frequently hit the 1.5x cap. Annual returns are partly a leverage result, not just a forecasting result.

3. **Short VIX common sample.** The VIX-enhanced matched sample has 179 observations. That is reasonable for a modern monthly sample but still small for equity forecasting.

4. **Weak statistical significance.** DM tests and mean excess-return tests do not establish strong statistical superiority.

5. **Regime small-N issues.** COVID and inflation-shock windows have 3 and 10 months respectively. The notebook correctly suppresses annualized metrics for these windows, but cumulative returns remain noisy.

6. **Real-time data-release uncertainty.** The notebook includes lagged fundamentals, but a fully real-time study would need exact release dates and tradable signal timestamps.

7. **Potential model-selection risk.** Several variants are tested. The best-performing specification may partly reflect selection over choices such as training window, VIX timing, and winsorization.

## 14. Recommended next research steps

1. **Add transaction-cost and financing-cost layers.** Recompute portfolio results with plausible monthly turnover costs, leverage financing spreads, and margin constraints.

2. **Run a real-time signal audit.** Explicitly timestamp D12, E12, VIX, interest-rate, and return data availability. Rebuild forecasts only with data known before trade execution.

3. **Use block bootstrap or expanding-window confidence intervals.** This would quantify uncertainty around OOS R² and Sharpe differences more directly than point estimates alone.

4. **Separate exposure timing from forecast accuracy.** Report strategy alpha against equity beta and dynamic beta benchmarks, not only buy-and-hold and historical-mean Markowitz.

5. **Stress-test leverage caps.** Rerun strategy results at caps such as 1.0, 1.25, and 2.0 to see whether conclusions depend on the 1.5x bound.

6. **Pre-register regime definitions.** Evaluate fixed crises, VIX>25, VIX quantiles, recessions, and drawdown regimes separately to avoid ambiguity.

7. **Investigate winsorization further.** Since winsorized components improve long-sample SOP, test whether robust component estimation can be made part of the primary model rather than a robustness afterthought.

## 15. Bottom-line conclusion

The uploaded files support a credible but cautious research narrative. Baseline SOP is a modestly successful long-sample forecasting framework. VIX enhancement improves the modern common-sample forecast, especially under squared-error loss, but does not pass strong significance tests. In portfolios, volatility-managed SOP variants produce the best Sharpe ratios, while historical-mean Markowitz produces the highest annual return and buy-and-hold remains hard to beat on simplicity, cost, and drawdown.

The strongest next step is not another forecast tweak; it is an implementation-validity layer. The strategy needs transaction costs, leverage financing, and real-time data timing before the economic results can be treated as investable rather than promising in-sample research evidence.
