"""
Standalone script to apply 15bps monthly turnover cost to strategy returns.
Reads existing matched returns CSV, applies costs, recomputes all metrics,
and saves updated outputs.

This replaces the need to re-run the full notebook for portfolio cells only.
"""
import warnings
import math
import numpy as np
import pandas as pd
import json

warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.width", 180)
pd.set_option("display.max_columns", 120)
pd.options.display.float_format = "{:,.6f}".format

# ── Constants (must match notebook) ────────────────────────────────────────────
TURNOVER_COST = 0.0015   # 15 basis points per month
ROLLING_VAR_WINDOW = 60
GAMMA_MARKOWITZ = 2.0
WEIGHT_BOUNDS = (0.0, 1.5)
VM_SCALE_BOUNDS = (0.25, 4.0)
OUTPUT_DIR = "."

CRISIS_WINDOWS = {
    "Dot-com": ("2000-03-31", "2002-09-30"),
    "GFC": ("2007-12-31", "2009-06-30"),
    "COVID": ("2020-02-29", "2020-04-30"),
    "Inflation shock": ("2022-01-31", "2022-10-31"),
}

def max_drawdown(returns):
    r = pd.Series(returns).dropna()
    if len(r) == 0:
        return np.nan
    wealth = (1 + r).cumprod()
    peak = wealth.cummax()
    return (wealth / peak - 1).min()

def compound_simple_return(x):
    x = pd.to_numeric(x, errors="coerce").dropna()
    return (1 + x).prod() - 1 if len(x) else np.nan

def hac_se_mean(x, max_lag=None):
    """Newey-West style HAC SE for sample mean."""
    x = pd.Series(x).dropna().to_numpy(dtype=float)
    n = len(x)
    if n < 3:
        return np.nan
    z = x - x.mean()
    if max_lag is None:
        max_lag = int(math.floor(4 * (n / 100) ** (2 / 9)))
    gamma0 = np.dot(z, z) / n
    var = gamma0
    for lag in range(1, max_lag + 1):
        cov = np.dot(z[lag:], z[:-lag]) / n
        weight = 1 - lag / (max_lag + 1)
        var += 2 * weight * cov
    return np.sqrt(max(var, 0) / n)

# ── Load matched returns CSV and enrich with rf_simple_next, VIXCLS, ms ───────
matched = pd.read_csv("sop_abcd_returns_matched.csv", parse_dates=["date", "forecast_target_date"])

# Pull rf_simple_next, VIXCLS, ms from the monthly enriched panel
enriched = pd.read_csv("sop_monthly_enriched.csv", parse_dates=["date"])
merge_cols = ["date", "rf_simple_next", "VIXCLS", "ms"]
available = [c for c in merge_cols if c in enriched.columns]
matched = matched.merge(enriched[available], on="date", how="left")

print(f"Loaded matched returns: {matched.shape}, {matched['forecast_target_date'].min().date()} to {matched['forecast_target_date'].max().date()}")

# ── Define strategy map (return_col, weight_col) ──────────────────────────────
strategy_map = {
    "A: SOP + Markowitz":        ("ret_A_SOP_Markowitz",     "w_A_SOP_Markowitz"),
    "B: SOP + vol-managed":      ("ret_B_SOP_VolManaged",    "w_B_SOP_VolManaged"),
    "C: VIX-SOP + Markowitz":    ("ret_C_VIX_Markowitz",    "w_C_VIX_Markowitz"),
    "D: VIX-SOP + vol-managed":  ("ret_D_VIX_VolManaged",   "w_D_VIX_VolManaged"),
    "Historical mean + Markowitz": ("ret_HM_Markowitz",      "w_HM_Markowitz"),
    "Buy-and-hold equity":        ("ret_BuyHold",             "w_BuyHold"),
}

# ── Apply turnover cost: create net return columns and update strategy_map ──────
# Net return = gross return - TURNOVER_COST * |w_t - w_{t-1}|
for label, (ret_col, weight_col) in strategy_map.items():
    w = pd.to_numeric(matched[weight_col], errors="coerce")
    abs_delta_w = w.diff().abs()   # per-month absolute weight change; first obs = NaN (no prior)
    monthly_cost = TURNOVER_COST * abs_delta_w.fillna(0)   # fill first-row NaN with 0 cost
    net_col = ret_col + "_net"
    matched[net_col] = matched[ret_col] - monthly_cost
    strategy_map[label] = (net_col, weight_col)   # update in-place

print("\nTurnover cost applied. Sample of gross vs net returns (strategy A):")
gross = matched["ret_A_SOP_Markowitz"]
net   = matched["ret_A_SOP_Markowitz_net"]
diff  = gross - net
print(f"  Mean monthly cost (bps): {diff.mean()*10000:.2f}")
print(f"  Max monthly cost (bps):  {diff.max()*10000:.2f}")
print(f"  Months with cost > 0:   {(diff > 0).sum()}")

# ── strategy_metrics helper ────────────────────────────────────────────────────
def strategy_metrics(frame, ret_col, weight_col=None, label=None):
    r = pd.to_numeric(frame[ret_col], errors="coerce").dropna()
    if len(r) == 0:
        return {"strategy": label or ret_col, "N": 0}
    sub = frame.loc[r.index]
    rf  = pd.to_numeric(sub["rf_simple_next"], errors="coerce")
    ex  = r - rf
    vol = r.std(ddof=1)
    return {
        "strategy":            label or ret_col,
        "N":                  int(len(r)),
        "start_date":         sub["forecast_target_date"].min(),
        "end_date":           sub["forecast_target_date"].max(),
        "ann_return":         (1 + r).prod() ** (12 / len(r)) - 1,
        "ann_vol":            vol * math.sqrt(12),
        "ann_sharpe":         ex.mean() / vol * math.sqrt(12) if vol > 0 else np.nan,
        "cum_return":         (1 + r).prod() - 1,
        "max_drawdown":       max_drawdown(r),
        "avg_weight":         pd.to_numeric(sub[weight_col], errors="coerce").mean() if weight_col else np.nan,
        "turnover":           pd.to_numeric(sub[weight_col], errors="coerce").diff().abs().mean() if weight_col else np.nan,
        "CEQ_gamma3_ann":     12 * (ex.mean() - 0.5 * 3 * r.var(ddof=1)),
    }

# ── 1. Main strategy table ────────────────────────────────────────────────────
strategy_table = pd.DataFrame([
    strategy_metrics(matched, ret_col, weight_col, label)
    for label, (ret_col, weight_col) in strategy_map.items()
])
strategy_table.to_csv(f"{OUTPUT_DIR}/sop_strategy_matched_results.csv", index=False)

print("\n=== MAIN STRATEGY TABLE (with 15bps turnover cost) ===")
display_cols = ["strategy","N","ann_return","ann_vol","ann_sharpe","cum_return","max_drawdown","avg_weight","turnover","CEQ_gamma3_ann"]
print(strategy_table[display_cols].to_string(index=False))

# Save matched returns (now with net return columns only)
matched_out_cols = (["date","forecast_target_date"]
                    + [v[0] for v in strategy_map.values()]
                    + [v[1] for v in strategy_map.values()])
matched[matched_out_cols].to_csv(f"{OUTPUT_DIR}/sop_abcd_returns_matched.csv", index=False)

# ── 2. Crisis portfolio outcomes ───────────────────────────────────────────────
def fixed_crisis_label(date):
    for name, (start, end) in CRISIS_WINDOWS.items():
        if pd.Timestamp(start) <= date <= pd.Timestamp(end):
            return name
    return None

matched["fixed_crisis"] = matched["forecast_target_date"].apply(fixed_crisis_label)
matched["vix_available"] = matched["VIXCLS"].notna()
vix_vals = pd.to_numeric(matched["VIXCLS"], errors="coerce")
matched["is_vix25"] = matched["vix_available"] & (vix_vals > 25)

crisis_port_rows = []
for crisis_name in list(CRISIS_WINDOWS.keys()) + ["All fixed crisis months", "VIX>25 months"]:
    if crisis_name == "All fixed crisis months":
        sub = matched[matched["fixed_crisis"].notna()]
    elif crisis_name == "VIX>25 months":
        sub = matched[matched["vix_available"] & matched["is_vix25"]]
    else:
        sub = matched[matched["fixed_crisis"] == crisis_name]

    if len(sub) == 0:
        continue

    for label, (ret_col, weight_col) in strategy_map.items():
        met = strategy_metrics(sub, ret_col, weight_col, label)
        sop_dir = np.sign(sub["ms"].mean()) if "ms" in sub.columns else np.nan
        vix_lvl = sub["VIXCLS"].mean() if "VIXCLS" in sub.columns else np.nan
        met.update({
            "crisis": crisis_name,
            "sop_signal_direction": sop_dir,
            "vix_level_mean": vix_lvl,
        })
        if len(sub) < 12:
            for _c in ["ann_sharpe", "ann_vol", "CEQ_gamma3_ann"]:
                met[_c] = np.nan
        crisis_port_rows.append(met)

crisis_portfolio_table = pd.DataFrame(crisis_port_rows)
crisis_portfolio_table.to_csv(f"{OUTPUT_DIR}/sop_crisis_portfolio_outcomes.csv", index=False)

print("\n=== CRISIS PORTFOLIO OUTCOMES (with 15bps turnover cost) ===")
crisis_display = ["crisis","strategy","N","cum_return","max_drawdown","ann_sharpe","avg_weight","sop_signal_direction","vix_level_mean"]
print(crisis_portfolio_table[crisis_display].to_string(index=False))

# ── 3. Mean excess-return difference tests ───────────────────────────────────
from scipy import stats

def mean_excess_test(frame, strategy_ret, benchmark_ret):
    use = frame[[strategy_ret, benchmark_ret, "rf_simple_next"]].dropna().copy()
    if len(use) < 12:
        return {
            "comparison": f"Mean excess-return difference: {strategy_ret} vs {benchmark_ret}",
            "N": len(use),
            "sharpe_strategy": np.nan, "sharpe_benchmark": np.nan, "sharpe_diff": np.nan,
            "mean_excess_diff_monthly": np.nan, "mean_excess_t_stat": np.nan, "mean_excess_p_value": np.nan,
        }
    a    = use[strategy_ret]   - use["rf_simple_next"]
    b    = use[benchmark_ret]  - use["rf_simple_next"]
    diff = a - b
    se   = hac_se_mean(diff)
    t    = diff.mean() / se if se and se > 0 else np.nan
    p    = 2 * (1 - stats.t.cdf(abs(t), df=len(use) - 1)) if pd.notna(t) else np.nan
    sr_a = a.mean() / use[strategy_ret].std(ddof=1)  * math.sqrt(12)
    sr_b = b.mean() / use[benchmark_ret].std(ddof=1) * math.sqrt(12)
    return {
        "comparison": f"Mean excess-return difference: {strategy_ret} vs {benchmark_ret}",
        "N": int(len(use)),
        "sharpe_strategy": sr_a,
        "sharpe_benchmark": sr_b,
        "sharpe_diff": sr_a - sr_b,
        "mean_excess_diff_monthly": diff.mean(),
        "mean_excess_t_stat": t,
        "mean_excess_p_value": p,
    }

sharpe_tests = pd.DataFrame([
    mean_excess_test(matched, "ret_B_SOP_VolManaged_net", "ret_A_SOP_Markowitz_net"),
    mean_excess_test(matched, "ret_C_VIX_Markowitz_net", "ret_A_SOP_Markowitz_net"),
    mean_excess_test(matched, "ret_D_VIX_VolManaged_net","ret_A_SOP_Markowitz_net"),
    mean_excess_test(matched, "ret_A_SOP_Markowitz_net", "ret_HM_Markowitz_net"),
])
sharpe_tests.to_csv(f"{OUTPUT_DIR}/sop_mean_excess_tests_matched.csv", index=False)

print("\n=== MEAN EXCESS-RETURN TESTS (with 15bps turnover cost) ===")
print(sharpe_tests.to_string(index=False))

print("\nAll outputs saved.")
