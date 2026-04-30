from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, minimize
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anyhowcp.masks import (  # noqa: E402
    check_log_schedule,
    exact_mask_failure_probabilities,
    log_budget,
    sliding_window_masks,
    uniform_log_schedule,
)
from anyhowcp.metrics import window_failure_rate  # noqa: E402


def gaussian_mean_width(sigmas: np.ndarray, s: np.ndarray) -> float:
    safe_s = np.maximum(np.asarray(s, dtype=np.float64), 1e-10)
    tau = -np.expm1(-safe_s)
    z = norm.isf(0.5 * tau)
    return float(np.mean(2.0 * sigmas * z))


def solve_exact_gaussian_schedule(
    sigmas: np.ndarray,
    masks: np.ndarray,
    alpha: float,
    x0: np.ndarray,
) -> np.ndarray:
    L = log_budget(alpha)
    result = minimize(
        lambda s: gaussian_mean_width(sigmas, s),
        x0,
        method="SLSQP",
        bounds=Bounds(np.full(sigmas.size, 1e-8), np.full(sigmas.size, L)),
        constraints=[LinearConstraint(masks, -np.inf * np.ones(masks.shape[0]), np.full(masks.shape[0], L))],
        options={"maxiter": 2000, "ftol": 1e-12},
    )
    assert result.success, result.message
    return np.asarray(result.x, dtype=np.float64)


def schedule_metrics(
    method: str,
    s: np.ndarray,
    sigmas: np.ndarray,
    masks: np.ndarray,
    alpha: float,
    rng: np.random.Generator,
    mc_runs: int,
) -> dict:
    tau = -np.expm1(-s)
    z = norm.isf(0.5 * tau)
    widths = 2.0 * sigmas * z
    exact_failures = exact_mask_failure_probabilities(tau, masks)
    eps = rng.normal(loc=0.0, scale=sigmas[None, :], size=(mc_runs, sigmas.size))
    errors = np.abs(eps) > (sigmas * z)[None, :]
    validity = check_log_schedule(s, masks, alpha)
    return {
        "method": method,
        "S_mean_width": float(widths.mean()),
        "S_max_width": float(widths.max()),
        "W_exact_mean": float(exact_failures.mean()),
        "W_exact_max": float(exact_failures.max()),
        "W_mc_mean": float(window_failure_rate(errors, masks)),
        "max_violation": validity["max_violation"],
        "valid": validity["valid"],
    }


def sigma_profile(name: str, T: int) -> np.ndarray:
    if name == "nodrift":
        return np.ones(T, dtype=np.float64)
    if name == "drift":
        return np.linspace(0.6, 2.0, T, dtype=np.float64)
    raise ValueError(f"unknown profile {name!r}")


def run_gaussian_exact_check(cfg: dict) -> dict:
    T = int(cfg.get("T", 20))
    alpha = float(cfg.get("alpha", 0.15))
    mc_runs = int(cfg.get("mc_runs", 200_000))
    seed = int(cfg.get("seed", 0))
    window_sizes = list(cfg.get("window_sizes", [1, 3, 5, 7, 9, 20]))
    profiles = list(cfg.get("profiles", ["nodrift", "drift"]))

    rows = []
    for profile in profiles:
        sigmas = sigma_profile(profile, T)
        for K in window_sizes:
            masks = sliding_window_masks(T, int(K))
            rng = np.random.default_rng(seed + 1000 * len(rows))

            uniform_s = uniform_log_schedule(alpha, masks)
            if profile == "nodrift" or int(K) == 1:
                exact_s = uniform_s
            else:
                exact_s = solve_exact_gaussian_schedule(sigmas, masks, alpha, uniform_s)

            for method, s in [
                ("uniform", uniform_s),
                ("exact_gaussian_opt", exact_s),
            ]:
                row = {
                    "profile": profile,
                    "K": int(K),
                    "mask_family": "all_ones" if int(K) == T else f"window_{int(K)}",
                    "num_masks": int(masks.shape[0]),
                    "max_support": int(masks.sum(axis=1).max()),
                    "sigma_min": float(sigmas.min()),
                    "sigma_max": float(sigmas.max()),
                    **schedule_metrics(method, s, sigmas, masks, alpha, rng, mc_runs),
                }
                rows.append(row)

    return {
        "config": {
            "T": T,
            "alpha": alpha,
            "mc_runs": mc_runs,
            "seed": seed,
            "window_sizes": window_sizes,
            "profiles": profiles,
            "quantile_model": "epsilon_t ~ N(0, sigma_t^2), interval half-width sigma_t * Phi^{-1}(1 - tau_t/2)",
            "tau_from_log_budget": "tau_t = 1 - exp(-s_t)",
        },
        "rows": rows,
    }


def write_markdown(result: dict, out_path: Path) -> None:
    rows = result["rows"]
    lines = [
        "# Gaussian Exact-Quantile Check",
        "",
        "Errors are independent Gaussian: `epsilon_t ~ N(0, sigma_t^2)`. For a log-budget value `s_t`, the experiment uses `tau_t = 1 - exp(-s_t)` and the exact two-sided interval half-width `sigma_t Phi^{-1}(1 - tau_t/2)`. Therefore each time has exact error probability `tau_t`, and each mask has exact failure probability `1 - exp(-sum_t M_t s_t)`.",
        "",
        f"- `T`: `{result['config']['T']}`",
        f"- `alpha`: `{result['config']['alpha']}`",
        "- Discretization grid: none; the optimizer uses the exact Gaussian quantile function.",
        f"- Monte Carlo sequences: `{result['config']['mc_runs']}`",
        "- `uniform`: paper uniform log-budget spending.",
        "- `exact_gaussian_opt`: continuous optimizer using the true Gaussian width curve.",
        "",
    ]

    for profile in result["config"]["profiles"]:
        subset = [r for r in rows if r["profile"] == profile]
        lines.extend([
            f"## {profile}",
            "",
            "| Mask | uniform S | exact S | delta S | exact W max | MC W exact |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for K in result["config"]["window_sizes"]:
            uniform = next(r for r in subset if int(r["K"]) == int(K) and r["method"] == "uniform")
            exact = next(
                r for r in subset if int(r["K"]) == int(K) and r["method"] == "exact_gaussian_opt"
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        uniform["mask_family"],
                        f"{uniform['S_mean_width']:.4f}",
                        f"{exact['S_mean_width']:.4f}",
                        f"{exact['S_mean_width'] - uniform['S_mean_width']:+.4f}",
                        f"{exact['W_exact_max']:.4f}",
                        f"{exact['W_mc_mean']:.4f}",
                    ]
                )
                + " |"
            )
        lines.append("")

        lines.extend([
            f"### Full {profile} rows",
            "",
            "| Mask | Method | S mean width | exact W mean | exact W max | MC W mean | max violation |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for r in sorted(subset, key=lambda x: (int(x["K"]), x["method"])):
            lines.append(
                "| "
                + " | ".join(
                    [
                        r["mask_family"],
                        r["method"],
                        f"{r['S_mean_width']:.4f}",
                        f"{r['W_exact_mean']:.4f}",
                        f"{r['W_exact_max']:.4f}",
                        f"{r['W_mc_mean']:.4f}",
                        f"{r['max_violation']:.2e}",
                    ]
                )
                + " |"
            )
        lines.append("")

    out_path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".workspace/experiments/gaussian_exact_check")
    parser.add_argument("--T", type=int, default=20)
    parser.add_argument("--alpha", type=float, default=0.15)
    parser.add_argument("--mc-runs", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = run_gaussian_exact_check(
        {
            "T": args.T,
            "alpha": args.alpha,
            "mc_runs": args.mc_runs,
            "seed": args.seed,
        }
    )
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True))
    write_markdown(result, out_dir / "summary.md")
    print(out_dir / "summary.md")


if __name__ == "__main__":
    main()
