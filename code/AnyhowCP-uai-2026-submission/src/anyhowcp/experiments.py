"""Paper-style rebuttal experiments on California Housing and CIFAR-10."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from anyhowcp.conformal import conformal_p_value, conformal_p_values
from anyhowcp.costs import (
    s_grid_from_alpha,
    smoothed_classification_set_size_cost_grid,
    smoothed_regression_quantile_cost_grid,
)
from anyhowcp.forecast import build_replanning_forecasts, forecast_error_summary
from anyhowcp.masks import (
    check_log_schedule,
    named_mask_family,
    sliding_window_masks,
    uniform_log_schedule,
)
from anyhowcp.metrics import mask_failure_indicators
from anyhowcp.replanning import run_grid_replanning


def _as_float(x) -> float:
    return float(np.asarray(x, dtype=np.float64))


def _load_california_housing(path: Path) -> tuple[np.ndarray, np.ndarray]:
    obj = joblib.load(path)
    if isinstance(obj, dict):
        if "data" in obj and "target" in obj:
            return np.asarray(obj["data"], dtype=np.float64), np.asarray(obj["target"], dtype=np.float64)
        if "x" in obj and "y" in obj:
            return np.asarray(obj["x"], dtype=np.float64), np.asarray(obj["y"], dtype=np.float64)
    arr = np.asarray(obj, dtype=np.float64)
    assert arr.ndim == 2 and arr.shape[1] >= 2
    y = arr[:, 0]
    if float(np.nanmax(y)) > 1000.0:
        y = y / 1000.0
    return arr[:, 1:], y


def prepare_regression_context(data_dir: Path, seed: int) -> dict:
    X, y = _load_california_housing(data_dir / "cal_housing_py3.pkz")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    model = GradientBoostingRegressor(random_state=seed)
    model.fit(X_train, y_train)

    y_lo, y_hi = float(y_train.min()), float(y_train.max())
    margin = 0.3 * (y_hi - y_lo)
    y_grid = np.linspace(y_lo - margin, y_hi + margin, 300)
    return {
        "X_test": X_test,
        "y_test": y_test,
        "model": model,
        "y_grid": y_grid,
    }


def _regression_drift(
    x_cal: np.ndarray,
    y_cal: np.ndarray,
    x_test: np.ndarray,
    y_test: float,
    t: int,
    T: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    progress = t / max(T - 1, 1)
    shift = 0.5 * progress
    noise_std = 0.3 * progress
    y_all = np.concatenate([y_cal, np.array([y_test])])
    if noise_std > 0.0:
        y_all = y_all + rng.normal(0.0, noise_std, size=y_all.shape)
    return x_cal + shift, y_all[:-1], x_test + shift, float(y_all[-1])


def _apply_label_noise(
    labels: np.ndarray,
    num_classes: int,
    t: int,
    T: int,
    rng: np.random.Generator,
    max_noise_rate: float = 0.3,
) -> np.ndarray:
    out = np.asarray(labels, dtype=np.int64).copy()
    n_flip = int((max_noise_rate * t / max(T - 1, 1)) * out.size)
    if n_flip == 0:
        return out
    flip_idx = rng.choice(out.size, size=n_flip, replace=False)
    for idx in flip_idx:
        new_label = int(rng.integers(0, num_classes - 1))
        if new_label >= out[idx]:
            new_label += 1
        out[idx] = new_label
    return out


def _batch_indices(n: int, T: int, rng: np.random.Generator, samples_per_batch: int | None) -> list[np.ndarray]:
    batch_size = samples_per_batch if samples_per_batch is not None else max(10, n // T)
    perm = rng.permutation(n)
    return [perm[t * batch_size : min((t + 1) * batch_size, n)] for t in range(T)]


def _summarize_runs(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {"mean": float(arr.mean()), "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0}


def _mask_specs_from_config(cfg: dict, T: int) -> list[dict]:
    specs = []
    for K in [int(k) for k in cfg.get("window_sizes", [1, 3, 5, 7, 9])]:
        masks = sliding_window_masks(T, K)
        name = "all_ones" if K == T else f"window_{K}"
        specs.append(_mask_spec(name, "sliding_window", K, masks))
    for raw in cfg.get("mask_families", []):
        masks = named_mask_family(T, raw)
        max_support = int(np.asarray(masks).sum(axis=1).max())
        specs.append(_mask_spec(raw["name"], raw["kind"], max_support, masks))
    return specs


def _mask_spec(name: str, kind: str, K: int, masks: np.ndarray) -> dict:
    M = np.asarray(masks, dtype=np.float64)
    return {
        "name": name,
        "kind": kind,
        "K": int(K),
        "masks": M,
        "num_masks": int(M.shape[0]),
        "max_support": int(M.sum(axis=1).max()),
        "density": float(M.mean()),
    }


def _evaluate_regression_schedule(records: list[dict], s: np.ndarray, masks: np.ndarray, alpha: float) -> dict:
    errors = []
    widths = []
    taus = 1.0 - np.exp(-np.asarray(s, dtype=np.float64))
    for rec, tau in zip(records, taus):
        p_grid = rec["p_grid"]
        selected = rec["grid"][p_grid > tau]
        width = 0.0 if selected.size == 0 else float(selected[-1] - selected[0])
        errors.append(bool(rec["p_true"] <= tau))
        widths.append(width)
    fail = mask_failure_indicators(np.asarray(errors, dtype=bool), masks)
    return {
        "window_failure_rate": float(fail.mean()),
        "mean_set_size": float(np.mean(widths)),
        "max_set_size": float(np.max(widths)),
        "valid_schedule": check_log_schedule(s, masks, alpha),
    }


def _evaluate_classification_schedule(records: list[dict], s: np.ndarray, masks: np.ndarray, alpha: float) -> dict:
    errors = []
    sizes = []
    taus = 1.0 - np.exp(-np.asarray(s, dtype=np.float64))
    for rec, tau in zip(records, taus):
        p_values = rec["p_values"]
        pred_set = p_values > tau
        errors.append(not bool(pred_set[int(rec["label"])]))
        sizes.append(int(pred_set.sum()))
    fail = mask_failure_indicators(np.asarray(errors, dtype=bool), masks)
    return {
        "window_failure_rate": float(fail.mean()),
        "mean_set_size": float(np.mean(sizes)),
        "max_set_size": float(np.max(sizes)),
        "valid_schedule": check_log_schedule(s, masks, alpha),
    }


def regression_iteration(
    data_dir: Path,
    seed: int,
    T: int,
    alpha: float,
    grid_points: int,
    drift: bool,
    smoothing: dict,
    samples_per_batch: int | None = None,
    context: dict | None = None,
) -> tuple[np.ndarray, list[dict]]:
    ctx = prepare_regression_context(data_dir, seed) if context is None else context
    X_test = ctx["X_test"]
    y_test = ctx["y_test"]
    model = ctx["model"]
    y_grid = ctx["y_grid"]
    rng = np.random.default_rng(seed)
    batches = _batch_indices(len(y_test), T, rng, samples_per_batch)

    score_batches: list[np.ndarray] = []
    records: list[dict] = []
    for t, idx in enumerate(batches):
        assert idx.size >= 3
        split = rng.permutation(idx.size)
        n_cal = max(1, idx.size // 2)
        cal_idx = idx[split[:n_cal]]
        test_idx = int(idx[split[n_cal]])
        x_cal = X_test[cal_idx]
        yy_cal = y_test[cal_idx]
        x_test = X_test[test_idx : test_idx + 1]
        yy_test = float(y_test[test_idx])
        if drift:
            x_cal, yy_cal, x_test, yy_test = _regression_drift(
                x_cal, yy_cal, x_test, yy_test, t, T, rng
            )
        cal_pred = model.predict(x_cal)
        cal_scores = np.abs(yy_cal - cal_pred)
        pred = float(model.predict(x_test)[0])
        p_grid = conformal_p_values(cal_scores, np.abs(y_grid - pred))
        p_true = conformal_p_value(cal_scores, abs(yy_test - pred))
        score_batches.append(cal_scores)
        records.append({"grid": y_grid, "p_grid": p_grid, "p_true": p_true})

    s_grid = s_grid_from_alpha(alpha, grid_points)
    costs = smoothed_regression_quantile_cost_grid(
        score_batches,
        s_grid,
        bandwidth=smoothing.get("bandwidth"),
        bandwidth_multiplier=float(smoothing.get("bandwidth_multiplier", 1.0)),
        spline_points=int(smoothing.get("spline_points", 400)),
    )
    return costs, records


def _probs_to_scores(probs: np.ndarray) -> np.ndarray:
    probs = np.clip(np.asarray(probs, dtype=np.float64), 1e-12, 1.0)
    return 1.0 / (np.log1p(probs) ** 0.25)


def classification_iteration(
    data_dir: Path,
    seed: int,
    T: int,
    alpha: float,
    grid_points: int,
    drift: bool,
    smoothing: dict,
    samples_per_batch: int | None = None,
) -> tuple[np.ndarray, list[dict]]:
    data = np.load(data_dir / "precomputed" / f"cifar10_probs_T{T}.npz")
    probs_nodrift = data["probs_nodrift"]
    probs_drift = data["probs_drift"]
    labels = np.asarray(data["labels"], dtype=np.int64)
    scores_nodrift = _probs_to_scores(probs_nodrift)
    scores_drift = np.stack([_probs_to_scores(probs_drift[t]) for t in range(T)])
    num_classes = probs_nodrift.shape[1]

    rng = np.random.default_rng(seed)
    batches = _batch_indices(labels.size, T, rng, samples_per_batch)
    p_value_batches: list[np.ndarray] = []
    records: list[dict] = []
    for t, idx in enumerate(batches):
        assert idx.size >= 3
        split = rng.permutation(idx.size)
        n_cal = max(1, idx.size // 2)
        cal_idx = idx[split[:n_cal]]
        test_idx = int(idx[split[n_cal]])
        score_table = scores_drift[t] if drift else scores_nodrift
        cal_labels = labels[cal_idx].copy()
        test_label = int(labels[test_idx])
        if drift:
            noisy = _apply_label_noise(
                np.concatenate([cal_labels, np.array([test_label])]),
                num_classes,
                t,
                T,
                rng,
            )
            cal_labels = noisy[:-1]
            test_label = int(noisy[-1])
        cal_scores = score_table[cal_idx, cal_labels]
        p_values = conformal_p_values(cal_scores, score_table[test_idx])
        p_value_batches.append(p_values)
        records.append({"p_values": p_values, "label": test_label})

    s_grid = s_grid_from_alpha(alpha, grid_points)
    costs = smoothed_classification_set_size_cost_grid(
        p_value_batches,
        s_grid,
        bandwidth=smoothing.get("bandwidth"),
        bandwidth_multiplier=float(smoothing.get("bandwidth_multiplier", 1.0)),
        spline_points=int(smoothing.get("spline_points", 400)),
    )
    return costs, records


def run_paper_experiments(cfg: dict) -> dict:
    data_dir = Path(cfg.get("data_dir", "code/data"))
    out_dir = Path(cfg.get("out_dir", ".workspace/experiments/main"))
    out_dir.mkdir(parents=True, exist_ok=True)
    alpha = float(cfg.get("alpha", 0.15))
    T = int(cfg.get("T", 20))
    num_runs = int(cfg.get("num_runs", 100))
    grid_points = int(cfg.get("grid_points", 81))
    mask_specs = _mask_specs_from_config(cfg, T)
    tasks = list(cfg.get("tasks", ["regression", "classification"]))
    conditions = list(cfg.get("conditions", ["nodrift", "drift"]))
    forecasters = list(cfg.get("forecasters", ["ewma", "trend", "blend"]))
    smoothing = dict(cfg.get("smoothing", {}))
    forecast_cfg = dict(cfg.get("forecast", {}))
    base_seed = int(cfg.get("seed", 0))

    s_grid = s_grid_from_alpha(alpha, grid_points)
    rows = []
    per_run = []

    def write_outputs() -> None:
        summary = {
            "config": cfg,
            "rows": rows,
            "notes": [
                "W is the mean fraction of failed monitored masks across runs.",
                "S is interval width for regression and set cardinality for classification.",
            ],
        }
        with open(out_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
        with open(out_dir / "per_run.jsonl", "w") as f:
            for row in per_run:
                f.write(json.dumps(row, sort_keys=True) + "\n")

    for task in tasks:
        for condition in conditions:
            print(f"running task={task} condition={condition} runs={num_runs}")
            drift = condition == "drift"
            run_cache = []
            regression_context = (
                prepare_regression_context(data_dir, base_seed) if task == "regression" else None
            )
            for run in range(num_runs):
                seed = base_seed + run
                if task == "regression":
                    costs, records = regression_iteration(
                        data_dir,
                        seed,
                        T,
                        alpha,
                        grid_points,
                        drift,
                        smoothing,
                        context=regression_context,
                    )
                    eval_fn = _evaluate_regression_schedule
                elif task == "classification":
                    costs, records = classification_iteration(
                        data_dir, seed, T, alpha, grid_points, drift, smoothing
                    )
                    eval_fn = _evaluate_classification_schedule
                else:
                    raise ValueError(f"unknown task {task!r}")
                run_cache.append((costs, records, eval_fn))

            for spec in mask_specs:
                masks = spec["masks"]
                K = spec["K"]
                method_metrics: dict[str, list[dict]] = {"uniform": []}
                for kind in forecasters:
                    method_metrics[f"replan_{kind}"] = []

                for run, (costs, records, eval_fn) in enumerate(run_cache):
                    uniform_s = uniform_log_schedule(alpha, masks, s_max=s_grid[-1])
                    metric = eval_fn(records, uniform_s, masks, alpha)
                    method_metrics["uniform"].append(metric)
                    per_run.append(
                        {
                            "task": task,
                            "condition": condition,
                            "run": run,
                            "K": K,
                            "mask_family": spec["name"],
                            "mask_kind": spec["kind"],
                            "num_masks": spec["num_masks"],
                            "max_support": spec["max_support"],
                            "mask_density": spec["density"],
                            "method": "uniform",
                            **metric,
                        }
                    )

                    if spec["max_support"] == 1:
                        # Singleton masks decouple time steps. Since all empirical costs
                        # are decreasing in s, every deployable forecaster chooses the
                        # same maximal feasible per-time allocation as uniform spending.
                        for kind in forecasters:
                            name = f"replan_{kind}"
                            copied = dict(metric)
                            method_metrics[name].append(copied)
                            per_run.append(
                                {
                                    "task": task,
                                    "condition": condition,
                                    "run": run,
                                    "K": K,
                                    "mask_family": spec["name"],
                                    "mask_kind": spec["kind"],
                                    "num_masks": spec["num_masks"],
                                    "max_support": spec["max_support"],
                                    "mask_density": spec["density"],
                                    "method": name,
                                    **copied,
                                }
                            )
                        continue

                    for kind in forecasters:
                        forecasts = build_replanning_forecasts(
                            costs,
                            kind=kind,
                            decay=float(forecast_cfg.get("decay", 0.7)),
                            blend_weight=float(forecast_cfg.get("blend_weight", 0.35)),
                        )
                        steps = run_grid_replanning(forecasts, masks, s_grid, alpha=alpha)
                        s = np.array([step.s_t for step in steps], dtype=np.float64)
                        metric = eval_fn(records, s, masks, alpha)
                        metric["forecast_error"] = forecast_error_summary(costs, forecasts)
                        name = f"replan_{kind}"
                        method_metrics[name].append(metric)
                        per_run.append(
                            {
                                "task": task,
                                "condition": condition,
                                "run": run,
                                "K": K,
                                "mask_family": spec["name"],
                                "mask_kind": spec["kind"],
                                "num_masks": spec["num_masks"],
                                "max_support": spec["max_support"],
                                "mask_density": spec["density"],
                                "method": name,
                                **metric,
                            }
                        )

                for method, vals in method_metrics.items():
                    if not vals:
                        continue
                    W = _summarize_runs([v["window_failure_rate"] for v in vals])
                    S = _summarize_runs([v["mean_set_size"] for v in vals])
                    row = {
                        "task": task,
                        "condition": condition,
                        "K": K,
                        "mask_family": spec["name"],
                        "mask_kind": spec["kind"],
                        "num_masks": spec["num_masks"],
                        "max_support": spec["max_support"],
                        "mask_density": spec["density"],
                        "method": method,
                        "W_mean": W["mean"],
                        "W_std": W["std"],
                        "S_mean": S["mean"],
                        "S_std": S["std"],
                    }
                    if vals and "forecast_error" in vals[0]:
                        row["forecast_mae"] = float(
                            np.mean([v["forecast_error"]["mae"] for v in vals])
                        )
                        row["forecast_rmse"] = float(
                            np.mean([v["forecast_error"]["rmse"] for v in vals])
                        )
                        row["forecast_derivative_mae"] = float(
                            np.mean([v["forecast_error"]["derivative_mae"] for v in vals])
                        )
                    rows.append(row)
            write_outputs()
            print(f"checkpoint rows={len(rows)} per_run={len(per_run)} out_dir={out_dir}")
    write_outputs()
    summary = {
        "config": cfg,
        "rows": rows,
        "notes": [
            "W is the mean fraction of failed monitored masks across runs.",
            "S is interval width for regression and set cardinality for classification.",
        ],
    }
    return summary
