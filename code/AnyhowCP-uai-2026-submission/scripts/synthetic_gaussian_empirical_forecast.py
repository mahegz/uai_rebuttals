from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anyhowcp.costs import regression_quantile_cost_grid  # noqa: E402
from anyhowcp.forecast import build_replanning_forecasts, forecast_row  # noqa: E402
from anyhowcp.masks import all_ones_masks, exact_mask_failure_probabilities, log_budget  # noqa: E402


def sigma_profile(name: str, T: int) -> np.ndarray:
    if name == "flat":
        return np.ones(T, dtype=np.float64)
    if name == "last5_high":
        return np.array([1.0] * (T - 5) + [10.0] * 5, dtype=np.float64)
    if name == "linear_ramp":
        return np.linspace(0.5, 10.0, T, dtype=np.float64)
    if name == "single_spike":
        sigmas = np.ones(T, dtype=np.float64)
        sigmas[T // 2] = 30.0
        return sigmas
    raise ValueError(f"unknown profile {name!r}")


def log_budget_grid(alpha: float, units: int) -> np.ndarray:
    assert units >= 2
    L = log_budget(alpha)
    return L * np.arange(1, units + 1, dtype=np.float64) / float(units)


def gaussian_width_grid(sigmas: np.ndarray, s_grid: np.ndarray) -> np.ndarray:
    tau = -np.expm1(-s_grid)
    z = norm.isf(0.5 * tau)
    return 2.0 * sigmas[:, None] * z[None, :]


def sample_score_batches(
    rng: np.random.Generator,
    sigmas: np.ndarray,
    n_calibration: int,
) -> list[np.ndarray]:
    return [
        np.abs(rng.normal(loc=0.0, scale=float(sigma), size=n_calibration))
        for sigma in sigmas
    ]


def empirical_width_grid(score_batches: list[np.ndarray], s_grid: np.ndarray) -> np.ndarray:
    return 2.0 * regression_quantile_cost_grid(score_batches, s_grid)


def robust_sigma_estimates(score_batches: list[np.ndarray]) -> np.ndarray:
    denom = norm.ppf(0.75)
    sigmas = np.array([np.median(scores) / denom for scores in score_batches], dtype=np.float64)
    return np.maximum(sigmas, 1e-6)


def build_shrunk_cost_forecasts(
    empirical_costs: np.ndarray,
    kind: str,
    shrink_weight: float,
    decay: float,
    blend_weight: float,
) -> list[np.ndarray]:
    base = build_replanning_forecasts(
        empirical_costs,
        kind=kind,
        decay=decay,
        blend_weight=blend_weight,
    )
    out = []
    for t, tail in enumerate(base):
        prior = empirical_costs[: t + 1].mean(axis=0)
        shrunk = shrink_weight * tail + (1.0 - shrink_weight) * prior[None, :]
        out.append(np.minimum.accumulate(np.maximum(shrunk, 0.0), axis=1))
    return out


def build_sigma_forecasts(
    sigma_hats: np.ndarray,
    s_grid: np.ndarray,
    kind: str,
    decay: float,
    blend_weight: float,
) -> list[np.ndarray]:
    sigma_hats = np.asarray(sigma_hats, dtype=np.float64)
    T = sigma_hats.size
    out = []
    for t in range(T):
        tail_sigmas = [sigma_hats[t]]
        history = sigma_hats[: t + 1, None]
        for u in range(t + 1, T):
            pred = forecast_row(
                history,
                horizon=u - t,
                kind=kind,
                decay=decay,
                blend_weight=blend_weight,
            )
            tail_sigmas.append(float(pred[0]))
        out.append(gaussian_width_grid(np.asarray(tail_sigmas, dtype=np.float64), s_grid))
    return out


def solve_all_ones_grid(cost_grid: np.ndarray, budget_units: int) -> np.ndarray:
    costs = np.asarray(cost_grid, dtype=np.float64)
    H, G = costs.shape
    assert budget_units >= H

    dp = np.full(budget_units + 1, np.inf, dtype=np.float64)
    dp[0] = 0.0
    choices: list[np.ndarray] = []

    for h in range(H):
        new = np.full(budget_units + 1, np.inf, dtype=np.float64)
        choice = np.full(budget_units + 1, -1, dtype=np.int64)
        for unit in range(1, min(G, budget_units) + 1):
            prev = dp[: budget_units - unit + 1]
            vals = prev + costs[h, unit - 1]
            current = new[unit:]
            better = vals < current
            current[better] = vals[better]
            new[unit:] = current
            current_choice = choice[unit:]
            current_choice[better] = unit
            choice[unit:] = current_choice
        dp = new
        choices.append(choice)

    best_budget = budget_units
    assert np.isfinite(dp[best_budget])
    units = np.zeros(H, dtype=np.int64)
    budget = best_budget
    for h in range(H - 1, -1, -1):
        unit = int(choices[h][budget])
        assert unit >= 1
        units[h] = unit
        budget -= unit
    return units


def replan_all_ones(forecasts: list[np.ndarray], total_units: int) -> np.ndarray:
    T = len(forecasts)
    remaining = total_units
    out = np.zeros(T, dtype=np.int64)
    for t, tail_costs in enumerate(forecasts):
        tail_units = solve_all_ones_grid(tail_costs, remaining)
        out[t] = tail_units[0]
        remaining -= int(out[t])
    return out


def schedule_metrics(
    method: str,
    units_schedule: np.ndarray,
    sigmas: np.ndarray,
    alpha: float,
    total_units: int,
) -> dict:
    s = units_schedule.astype(np.float64) * log_budget(alpha) / float(total_units)
    tau = -np.expm1(-s)
    widths = gaussian_width_grid(sigmas, s)
    masks = all_ones_masks(sigmas.size)
    failures = exact_mask_failure_probabilities(tau, masks)
    return {
        "method": method,
        "S_mean_width": float(np.diag(widths).mean()),
        "S_max_width": float(np.diag(widths).max()),
        "W_exact": float(failures.max()),
        "budget_used": float(s.sum()),
        "min_unit": int(units_schedule.min()),
        "max_unit": int(units_schedule.max()),
    }


def forecast_losses(
    forecasts: list[np.ndarray],
    empirical_costs: np.ndarray,
    true_costs: np.ndarray,
) -> dict:
    true_abs = []
    true_sq = []
    empirical_abs = []
    derivative_abs = []
    for t, tail in enumerate(forecasts):
        for h in range(1, tail.shape[0]):
            pred = tail[h]
            true = true_costs[t + h]
            empirical = empirical_costs[t + h]
            true_abs.append(np.abs(pred - true).mean())
            true_sq.append(np.mean((pred - true) ** 2))
            empirical_abs.append(np.abs(pred - empirical).mean())
            derivative_abs.append(np.abs(np.diff(pred) - np.diff(true)).mean())
    return {
        "forecast_true_mae": float(np.mean(true_abs)),
        "forecast_true_rmse": float(np.sqrt(np.mean(true_sq))),
        "forecast_empirical_mae": float(np.mean(empirical_abs)),
        "forecast_derivative_mae": float(np.mean(derivative_abs)),
    }


def summarize(vals: list[float]) -> tuple[float, float]:
    arr = np.asarray(vals, dtype=np.float64)
    return float(arr.mean()), float(arr.std(ddof=1)) if arr.size > 1 else 0.0


def run_experiment(cfg: dict) -> dict:
    T = int(cfg.get("T", 20))
    alpha = float(cfg.get("alpha", 0.15))
    total_units = int(cfg.get("total_units", 200))
    num_runs = int(cfg.get("num_runs", 50))
    seed = int(cfg.get("seed", 0))
    calibration_sizes = [int(x) for x in cfg.get("calibration_sizes", [64, 512])]
    profiles = list(cfg.get("profiles", ["flat", "linear_ramp", "last5_high", "single_spike"]))
    forecasters = list(cfg.get("forecasters", ["last", "mean", "ewma", "trend", "blend"]))
    shrink_methods = list(
        cfg.get(
            "shrink_methods",
            [
                {"kind": "mean", "shrink_weight": 0.25},
                {"kind": "mean", "shrink_weight": 0.50},
                {"kind": "blend", "shrink_weight": 0.25},
                {"kind": "blend", "shrink_weight": 0.50},
            ],
        )
    )
    sigma_forecasters = list(cfg.get("sigma_forecasters", ["last", "mean", "ewma", "trend", "blend"]))
    forecast_cfg = dict(cfg.get("forecast", {"decay": 0.7, "blend_weight": 0.35}))

    assert total_units % T == 0
    s_grid = log_budget_grid(alpha, total_units)
    uniform_units = np.full(T, total_units // T, dtype=np.int64)

    per_run = []
    for profile in profiles:
        sigmas = sigma_profile(profile, T)
        true_costs = gaussian_width_grid(sigmas, s_grid)
        hidden_units = solve_all_ones_grid(true_costs, total_units)
        hidden_metrics = schedule_metrics(
            "hidden_exact_grid_reference", hidden_units, sigmas, alpha, total_units
        )
        uniform_metrics = schedule_metrics("uniform", uniform_units, sigmas, alpha, total_units)

        for n_calibration in calibration_sizes:
            for run in range(num_runs):
                rng = np.random.default_rng(seed + 100_000 * profiles.index(profile) + 1000 * n_calibration + run)
                score_batches = sample_score_batches(rng, sigmas, n_calibration)
                empirical_costs = empirical_width_grid(score_batches, s_grid)
                sigma_hats = robust_sigma_estimates(score_batches)

                for method, units_schedule, losses in [
                    ("uniform", uniform_units, {}),
                    ("hidden_exact_grid_reference", hidden_units, {}),
                ]:
                    row = {
                        "profile": profile,
                        "n_calibration": n_calibration,
                        "run": run,
                        **schedule_metrics(method, units_schedule, sigmas, alpha, total_units),
                        **losses,
                    }
                    row["regret_pct_vs_hidden"] = (
                        100.0
                        * (row["S_mean_width"] - hidden_metrics["S_mean_width"])
                        / hidden_metrics["S_mean_width"]
                    )
                    row["delta_pct_vs_uniform"] = (
                        100.0
                        * (row["S_mean_width"] - uniform_metrics["S_mean_width"])
                        / uniform_metrics["S_mean_width"]
                    )
                    per_run.append(row)

                for kind in forecasters:
                    forecasts = build_replanning_forecasts(
                        empirical_costs,
                        kind=kind,
                        decay=float(forecast_cfg.get("decay", 0.7)),
                        blend_weight=float(forecast_cfg.get("blend_weight", 0.35)),
                    )
                    units_schedule = replan_all_ones(forecasts, total_units)
                    row = {
                        "profile": profile,
                        "n_calibration": n_calibration,
                        "run": run,
                        **schedule_metrics(f"replan_{kind}", units_schedule, sigmas, alpha, total_units),
                        **forecast_losses(forecasts, empirical_costs, true_costs),
                    }
                    row["regret_pct_vs_hidden"] = (
                        100.0
                        * (row["S_mean_width"] - hidden_metrics["S_mean_width"])
                        / hidden_metrics["S_mean_width"]
                    )
                    row["delta_pct_vs_uniform"] = (
                        100.0
                        * (row["S_mean_width"] - uniform_metrics["S_mean_width"])
                        / uniform_metrics["S_mean_width"]
                    )
                    per_run.append(row)

                for spec in shrink_methods:
                    kind = str(spec["kind"])
                    shrink_weight = float(spec["shrink_weight"])
                    forecasts = build_shrunk_cost_forecasts(
                        empirical_costs,
                        kind=kind,
                        shrink_weight=shrink_weight,
                        decay=float(forecast_cfg.get("decay", 0.7)),
                        blend_weight=float(forecast_cfg.get("blend_weight", 0.35)),
                    )
                    units_schedule = replan_all_ones(forecasts, total_units)
                    row = {
                        "profile": profile,
                        "n_calibration": n_calibration,
                        "run": run,
                        **schedule_metrics(
                            f"replan_{kind}_shrink{int(round(100 * shrink_weight))}",
                            units_schedule,
                            sigmas,
                            alpha,
                            total_units,
                        ),
                        **forecast_losses(forecasts, empirical_costs, true_costs),
                    }
                    row["regret_pct_vs_hidden"] = (
                        100.0
                        * (row["S_mean_width"] - hidden_metrics["S_mean_width"])
                        / hidden_metrics["S_mean_width"]
                    )
                    row["delta_pct_vs_uniform"] = (
                        100.0
                        * (row["S_mean_width"] - uniform_metrics["S_mean_width"])
                        / uniform_metrics["S_mean_width"]
                    )
                    per_run.append(row)

                for kind in sigma_forecasters:
                    forecasts = build_sigma_forecasts(
                        sigma_hats,
                        s_grid,
                        kind=kind,
                        decay=float(forecast_cfg.get("decay", 0.7)),
                        blend_weight=float(forecast_cfg.get("blend_weight", 0.35)),
                    )
                    units_schedule = replan_all_ones(forecasts, total_units)
                    row = {
                        "profile": profile,
                        "n_calibration": n_calibration,
                        "run": run,
                        **schedule_metrics(f"replan_sigma_{kind}", units_schedule, sigmas, alpha, total_units),
                        **forecast_losses(forecasts, empirical_costs, true_costs),
                    }
                    row["regret_pct_vs_hidden"] = (
                        100.0
                        * (row["S_mean_width"] - hidden_metrics["S_mean_width"])
                        / hidden_metrics["S_mean_width"]
                    )
                    row["delta_pct_vs_uniform"] = (
                        100.0
                        * (row["S_mean_width"] - uniform_metrics["S_mean_width"])
                        / uniform_metrics["S_mean_width"]
                    )
                    per_run.append(row)

    grouped: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for row in per_run:
        grouped[(row["profile"], row["n_calibration"], row["method"])].append(row)

    rows = []
    metric_names = [
        "S_mean_width",
        "S_max_width",
        "W_exact",
        "regret_pct_vs_hidden",
        "delta_pct_vs_uniform",
        "budget_used",
        "min_unit",
        "max_unit",
        "forecast_true_mae",
        "forecast_true_rmse",
        "forecast_empirical_mae",
        "forecast_derivative_mae",
    ]
    for (profile, n_calibration, method), vals in sorted(grouped.items()):
        out = {
            "profile": profile,
            "n_calibration": n_calibration,
            "method": method,
            "num_runs": len(vals),
        }
        for name in metric_names:
            xs = [v[name] for v in vals if name in v]
            if xs:
                mean, std = summarize(xs)
                out[f"{name}_mean"] = mean
                out[f"{name}_std"] = std
        rows.append(out)

    return {
        "config": {
            "T": T,
            "alpha": alpha,
            "total_units": total_units,
            "num_runs": num_runs,
            "seed": seed,
            "calibration_sizes": calibration_sizes,
            "profiles": profiles,
            "forecasters": forecasters,
            "shrink_methods": shrink_methods,
            "sigma_forecasters": sigma_forecasters,
            "forecast": forecast_cfg,
            "mask": "all_ones",
            "empirical_access": "replanning sees only sampled calibration score cost curves; true sigmas are used only for evaluation/reference",
        },
        "rows": rows,
        "per_run": per_run,
    }


def fmt(x: float | None, digits: int = 3) -> str:
    if x is None:
        return "--"
    return f"{float(x):.{digits}f}"


def write_markdown(result: dict, out_path: Path) -> None:
    rows = result["rows"]
    cfg = result["config"]
    lines = [
        "# Synthetic Gaussian Empirical-Forecast Experiment",
        "",
        "Model: independent Gaussian errors with known profile only to the evaluator. The replanning methods do not receive `sigma_t`; they see empirical calibration-score cost curves sampled from the Gaussian model and forecast future cost curves from past/current empirical curves.",
        "",
        f"- `T`: `{cfg['T']}`",
        f"- `alpha`: `{cfg['alpha']}`",
        f"- Mask: `{cfg['mask']}`",
        f"- Log-budget grid units: `{cfg['total_units']}`",
        f"- Runs per setting: `{cfg['num_runs']}`",
        f"- Calibration sizes: `{cfg['calibration_sizes']}`",
        f"- Direct cost forecasters: `{cfg['forecasters']}`",
        f"- Shrinkage methods: `{cfg['shrink_methods']}`",
        f"- Sigma-estimate forecasters: `{cfg['sigma_forecasters']}`",
        "",
        "`hidden_exact_grid_reference` uses the true Gaussian cost grid and is not an admissible method. It is only the denominator for regret.",
        "",
    ]

    for profile in cfg["profiles"]:
        lines.extend([
            f"## {profile}",
            "",
            "| n cal | method | S width | vs uniform % | regret % | W exact | forecast true MAE | forecast true RMSE | empirical MAE | deriv MAE | units min-max |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        subset = [r for r in rows if r["profile"] == profile]
        shrink_names = [
            f"replan_{spec['kind']}_shrink{int(round(100 * float(spec['shrink_weight'])))}"
            for spec in cfg["shrink_methods"]
        ]
        sigma_names = [f"replan_sigma_{m}" for m in cfg["sigma_forecasters"]]
        method_order = (
            ["hidden_exact_grid_reference", "uniform"]
            + [f"replan_{m}" for m in cfg["forecasters"]]
            + shrink_names
            + sigma_names
        )
        for n_cal in cfg["calibration_sizes"]:
            for method in method_order:
                match = [r for r in subset if r["n_calibration"] == n_cal and r["method"] == method]
                if not match:
                    continue
                r = match[0]
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(n_cal),
                            method,
                            fmt(r.get("S_mean_width_mean")),
                            fmt(r.get("delta_pct_vs_uniform_mean")),
                            fmt(r.get("regret_pct_vs_hidden_mean")),
                            fmt(r.get("W_exact_mean")),
                            fmt(r.get("forecast_true_mae_mean")),
                            fmt(r.get("forecast_true_rmse_mean")),
                            fmt(r.get("forecast_empirical_mae_mean")),
                            fmt(r.get("forecast_derivative_mae_mean")),
                            f"{fmt(r.get('min_unit_mean'), 1)}-{fmt(r.get('max_unit_mean'), 1)}",
                        ]
                    )
                    + " |"
                )
        lines.append("")

        lines.extend([
            f"### Forecast-Loss Winners for {profile}",
            "",
            "| n cal | best S | best true MAE | best true RMSE | best empirical MAE | best derivative MAE |",
            "|---:|---|---|---|---|---|",
        ])
        for n_cal in cfg["calibration_sizes"]:
            replans = [
                r for r in subset
                if r["n_calibration"] == n_cal and r["method"].startswith("replan_")
            ]
            best_s = min(replans, key=lambda r: r["S_mean_width_mean"])
            best_mae = min(replans, key=lambda r: r["forecast_true_mae_mean"])
            best_rmse = min(replans, key=lambda r: r["forecast_true_rmse_mean"])
            best_emp = min(replans, key=lambda r: r["forecast_empirical_mae_mean"])
            best_deriv = min(replans, key=lambda r: r["forecast_derivative_mae_mean"])
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(n_cal),
                        f"{best_s['method']} ({fmt(best_s['S_mean_width_mean'])})",
                        f"{best_mae['method']} ({fmt(best_mae['forecast_true_mae_mean'])})",
                        f"{best_rmse['method']} ({fmt(best_rmse['forecast_true_rmse_mean'])})",
                        f"{best_emp['method']} ({fmt(best_emp['forecast_empirical_mae_mean'])})",
                        f"{best_deriv['method']} ({fmt(best_deriv['forecast_derivative_mae_mean'])})",
                    ]
                )
                + " |"
            )
        lines.append("")

    out_path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".workspace/experiments/synthetic_gaussian_empirical_forecast")
    parser.add_argument("--num-runs", type=int, default=50)
    parser.add_argument("--total-units", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = run_experiment(
        {
            "num_runs": args.num_runs,
            "total_units": args.total_units,
            "seed": args.seed,
        }
    )
    (out_dir / "summary.json").write_text(json.dumps({k: v for k, v in result.items() if k != "per_run"}, indent=2, sort_keys=True))
    with open(out_dir / "per_run.jsonl", "w") as f:
        for row in result["per_run"]:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    write_markdown(result, out_dir / "summary.md")
    print(out_dir / "summary.md")


if __name__ == "__main__":
    main()
