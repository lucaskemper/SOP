"""
Standalone script: re-run strategies with 0-100% weight cap (no leverage)
and compare to baseline 0-150% cap results.
Same sample, same forecasts, same turnover cost (15bps), only weight cap differs.
"""
import math, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

TURNOVER_COST  = 0.0015
GAMMA_MARKOWITZ = 2.0
ROLLING_VAR_WINDOW = 60
VM_SCALE_BOUNDS = (0.25, 4.0)
OUTPUT_DIR = "."

def max_drawdown(returns):
    r = pd.Series(returns).dropna()
    if len(r) == 0:
        return np.nan
    wealth = (1 + r).cumprod()
    peak = wealth.cummax()
    return (wealth / peak - 1).min()

def markowitz_weight(forecast_log, rf_simple_forecast, variance, gamma=2.0, lo=0.0, hi=1.5):
    exp_simple = np.expm1(forecast_log)
    excess = exp_simple - rf_simple_forecast
    w = excess / (gamma * variance)
    return w.clip(lo, hi)

def strategy_metrics(frame, ret_col, weight_col=None, label=None):
    r = pd.to_numeric(frame[ret_col], errors="coerce").dropna()
    if len(r) == 0:
        return {"strategy": label or ret_col, "N": 0}
    sub = frame.loc[r.index]
    rf  = pd.to_numeric(sub["rf_simple_next"], errors="coerce")
    ex  = r - rf
    vol = r.std(ddof=1)
    return {
        "strategy":       label or ret_col,
        "N":             int(len(r)),
        "ann_return":    (1 + r).prod() ** (12 / len(r)) - 1,
        "ann_vol":       vol * math.sqrt(12),
        "ann_sharpe":    ex.mean() / vol * math.sqrt(12) if vol > 0 else np.nan,
        "cum_return":    (1 + r).prod() - 1,
        "max_drawdown":  max_drawdown(r),
        "avg_weight":    pd.to_numeric(sub[weight_col], errors="coerce").mean() if weight_col else np.nan,
        "turnover":      pd.to_numeric(sub[weight_col], errors="coerce").diff().abs().mean() if weight_col else np.nan,
        "CEQ_gamma3_ann": 12 * (ex.mean() - 0.5 * 3 * r.var(ddof=1)),
    }

def apply_turnover_cost_and_get_metrics(frame, strategy_map_in):
    """Apply turnover cost and return metrics dict for each strategy (doesn't mutate input)."""
    sm = {k: v for k, v in strategy_map_in.items()}  # shallow copy
    for label, (ret_col, weight_col) in list(sm.items()):
        w = pd.to_numeric(frame[weight_col], errors="coerce")
        abs_dw = w.diff().abs().fillna(0)
        mc = TURNOVER_COST * abs_dw
        net_col = ret_col + "_net"
        frame = frame.copy()  # avoid mutating original
        frame[net_col] = frame[ret_col] - mc
        sm[label] = (net_col, weight_col)
    return [
        strategy_metrics(frame, ret_col, weight_col, label)
        for label, (ret_col, weight_col) in sm.items()
    ]

# ── Load and build portfolio panel (same as notebook portfolio cell) ───────────
vix_df = pd.read_csv(f"{OUTPUT_DIR}/sop_vix_common_forecasts.csv", parse_dates=["date"])
vix_df["equity_simple_t"]   = pd.to_numeric(vix_df["ret_decimal"], errors="coerce")
vix_df["equity_simple_next"]= vix_df["equity_simple_t"].shift(-1)
vix_df["rf_simple_next"]    = pd.to_numeric(vix_df["rf_simple"], errors="coerce").shift(-1)
vix_df["rolling_var_5yr"]  = vix_df["equity_simple_t"].rolling(ROLLING_VAR_WINDOW, min_periods=ROLLING_VAR_WINDOW).var()
vix_df["rv_t"]             = pd.to_numeric(vix_df["svar"], errors="coerce")
vix_df["rv_t"]             = vix_df["rv_t"].where(vix_df["rv_t"] > 0, np.nan).fillna(vix_df["rolling_var_5yr"])
vix_df["rv_avg_expanding"] = vix_df["rv_t"].expanding(min_periods=ROLLING_VAR_WINDOW).mean()
vix_df["vm_scale"]         = (vix_df["rv_avg_expanding"] / vix_df["rv_t"]).clip(*VM_SCALE_BOUNDS)

port = vix_df.copy()

# ── Baseline (hi=1.5) weights ──────────────────────────────────────────────────
forecast_specs = {
    "A: SOP + Markowitz":          ("ms",           False),
    "B: SOP + vol-managed":         ("ms",           True),
    "C: VIX-SOP + Markowitz":      ("ms_enh_VIXCLS", False),
    "D: VIX-SOP + vol-managed":     ("ms_enh_VIXCLS", True),
    "Historical mean + Markowitz":  ("hist_mean",    False),
}
bsl_map = {}  # baseline
for label, (fc_col, vm) in forecast_specs.items():
    prefix = label.split(":")[0].strip().replace(" ", "_").replace("+", "_plus_")[:18]
    wc = f"w_bsl_{prefix}"
    rc = f"ret_bsl_{prefix}"
    w  = markowitz_weight(port[fc_col], port["rf_forecast_simple"], port["rolling_var_5yr"],
                          gamma=GAMMA_MARKOWITZ, lo=0.0, hi=1.5)
    if vm:
        w = (w * port["vm_scale"]).clip(0.0, 1.5)
    port[wc] = w
    port[rc] = w * port["equity_simple_next"] + (1 - w) * port["rf_simple_next"]
    bsl_map[label] = (rc, wc)

port["w_bsl_BuyHold"] = 1.0
port["ret_bsl_BuyHold"] = port["equity_simple_next"]
bsl_map["Buy-and-hold equity"] = ("ret_bsl_BuyHold", "w_bsl_BuyHold")

# ── No-leverage (hi=1.0) weights ──────────────────────────────────────────────
nl_map = {}   # no-leverage
for label, (fc_col, vm) in forecast_specs.items():
    prefix = label.split(":")[0].strip().replace(" ", "_").replace("+", "_plus_")[:18]
    wc = f"w_nl_{prefix}"
    rc = f"ret_nl_{prefix}"
    w  = markowitz_weight(port[fc_col], port["rf_forecast_simple"], port["rolling_var_5yr"],
                          gamma=GAMMA_MARKOWITZ, lo=0.0, hi=1.0)   # <-- no leverage
    if vm:
        w = (w * port["vm_scale"]).clip(0.0, 1.0)
    port[wc] = w
    port[rc] = w * port["equity_simple_next"] + (1 - w) * port["rf_simple_next"]
    nl_map[label] = (rc, wc)

port["w_nl_BuyHold"] = 1.0
port["ret_nl_BuyHold"] = port["equity_simple_next"]
nl_map["Buy-and-hold equity"] = ("ret_nl_BuyHold", "w_nl_BuyHold")

# ── Matched sample (same filter as notebook) ────────────────────────────────────
all_ret_cols = list(list(zip(*bsl_map.values()))[0]) + list(list(zip(*nl_map.values()))[0])
all_wt_cols  = list(list(zip(*bsl_map.values()))[1]) + list(list(zip(*nl_map.values()))[1])
required = ["forecast_target_date", "equity_simple_next", "rf_simple_next"] + all_ret_cols + all_wt_cols
matched = port.dropna(subset=required).copy()

print(f"Matched sample: N={len(matched)}, {matched['forecast_target_date'].min()} to {matched['forecast_target_date'].max()}")

# ── Apply turnover cost and compute metrics ────────────────────────────────────
bsl_metrics = pd.DataFrame(apply_turnover_cost_and_get_metrics(matched.copy(), bsl_map))
nl_metrics  = pd.DataFrame(apply_turnover_cost_and_get_metrics(matched.copy(), nl_map))

# ── Compare ────────────────────────────────────────────────────────────────────
base_r = bsl_metrics.rename(columns={c: f"{c}_bsl" for c in bsl_metrics.columns if c != "strategy"})
nl_r   = nl_metrics.rename(columns={c: f"{c}_nl"  for c in nl_metrics.columns if c != "strategy"})
cmp    = nl_r.merge(base_r, on="strategy", how="left")
cmp["Sharpe_diff"] = cmp["ann_sharpe_nl"] - cmp["ann_sharpe_bsl"]
cmp["AnnRet_diff"]  = (cmp["ann_return_nl"] - cmp["ann_return_bsl"]) * 10000  # bp/month
cmp["Wt_diff"]     = cmp["avg_weight_nl"]  - cmp["avg_weight_bsl"]

nl_metrics.to_csv(f"{OUTPUT_DIR}/sop_portfolio_robustness_leverage.csv", index=False)

print()
print("=== Portfolio robustness: 0-100% cap (no-leverage) vs 0-150% cap (baseline) ===")
print(f"{'Strategy':<35} {'Sharpe':>8} {'ShBase':>8} {'ΔSh':>7} {'ΔAnnRet(bp/m)':>14} {'AvgWtNL':>8} {'AvgWtBSL':>9} {'ΔWt':>7}")
print("-" * 110)
for _, r in cmp.sort_values("ann_sharpe_nl", ascending=False).iterrows():
    print(f"{r['strategy']:<35} {r['ann_sharpe_nl']:>8.4f} {r['ann_sharpe_bsl']:>8.4f} {r['Sharpe_diff']:>+7.4f} {r['AnnRet_diff']:>+13.2f} {r['avg_weight_nl']:>8.3f} {r['avg_weight_bsl']:>9.3f} {r['Wt_diff']:>+7.3f}")

print()
print("=== Ranking comparison ===")
nl_rank = cmp.sort_values("ann_sharpe_nl", ascending=False)["strategy"].tolist()
bsl_rank = cmp.sort_values("ann_sharpe_bsl", ascending=False)["strategy"].tolist()
print(f"  No-leverage rank:  {' > '.join(nl_rank)}")
print(f"  Baseline rank:      {' > '.join(bsl_rank)}")
print(f"  Rankings identical: {nl_rank == bsl_rank}")
