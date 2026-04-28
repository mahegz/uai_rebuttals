"""Cost curves in the log-budget coordinate s = -log(1 - tau)."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.stats import norm


def s_grid_from_alpha(alpha: float, points: int = 81) -> np.ndarray:
    assert points >= 2
    return np.linspace(0.0, float(-np.log1p(-alpha)), points)


def exponential_cost_grid(weights: np.ndarray, s_grid: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=np.float64)
    grid = np.asarray(s_grid, dtype=np.float64)
    return weights[:, None] * np.exp(-grid[None, :])


def exponential_value_and_grad(weights: np.ndarray):
    weights = np.asarray(weights, dtype=np.float64)

    def value_and_grad(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        s = np.asarray(s, dtype=np.float64)
        values = weights * np.exp(-s)
        return values, -values

    return value_and_grad


def regression_quantile_cost_grid(score_batches: list[np.ndarray], s_grid: np.ndarray) -> np.ndarray:
    grid = np.asarray(s_grid, dtype=np.float64)
    out = np.zeros((len(score_batches), grid.size), dtype=np.float64)
    for t, scores in enumerate(score_batches):
        x = np.sort(np.asarray(scores, dtype=np.float64))
        n = x.size + 1
        for g, s in enumerate(grid):
            tau = 1.0 - np.exp(-s)
            idx = int(np.ceil((1.0 - tau) * n)) - 1
            out[t, g] = x[int(np.clip(idx, 0, x.size - 1))]
    return out


def classification_set_size_cost_grid(p_value_batches: list[np.ndarray], s_grid: np.ndarray) -> np.ndarray:
    grid = np.asarray(s_grid, dtype=np.float64)
    out = np.zeros((len(p_value_batches), grid.size), dtype=np.float64)
    for t, p_values in enumerate(p_value_batches):
        p = np.asarray(p_values, dtype=np.float64)
        for g, s in enumerate(grid):
            tau = 1.0 - np.exp(-s)
            out[t, g] = np.sum(p > tau)
    return out


def ewma_cost_grid(history: list[np.ndarray], decay: float = 0.7) -> np.ndarray:
    assert len(history) > 0
    weights = np.array([decay ** (len(history) - 1 - i) for i in range(len(history))])
    weights = weights / weights.sum()
    out = np.zeros_like(history[0], dtype=np.float64)
    for w, costs in zip(weights, history):
        out += w * np.asarray(costs, dtype=np.float64)
    return out


def silverman_bandwidth(x: np.ndarray, min_bandwidth: float = 1e-8) -> float:
    x = np.asarray(x, dtype=np.float64)
    assert x.size > 0
    if x.size == 1:
        return float(min_bandwidth)
    std = float(np.std(x, ddof=1))
    iqr = float(np.subtract(*np.percentile(x, [75, 25])))
    spread = min(std, iqr / 1.34) if iqr > 0.0 else std
    if not np.isfinite(spread) or spread <= 0.0:
        spread = max(float(np.max(x) - np.min(x)), 1.0)
    return float(max(0.9 * spread * x.size ** (-0.2), min_bandwidth))


def _monotone_nonincreasing(values: np.ndarray) -> np.ndarray:
    return np.minimum.accumulate(np.asarray(values, dtype=np.float64))


def _convexify_on_uniform_grid(values: np.ndarray, passes: int = 4) -> np.ndarray:
    vals = np.asarray(values, dtype=np.float64).copy()
    if vals.size < 3:
        return vals
    for _ in range(passes):
        for i in range(1, vals.size - 1):
            midpoint = 0.5 * (vals[i - 1] + vals[i + 1])
            if vals[i] > midpoint:
                vals[i] = midpoint
        vals = _monotone_nonincreasing(vals)
    return vals


def _smoothed_cdf(x_grid: np.ndarray, scores: np.ndarray, bandwidth: float) -> np.ndarray:
    z = (x_grid[:, None] - scores[None, :]) / bandwidth
    return np.mean(norm.cdf(z), axis=1)


def _smoothed_quantile_values(
    scores: np.ndarray,
    s_eval: np.ndarray,
    bandwidth: float,
    spline_points: int,
) -> np.ndarray:
    x = np.sort(np.asarray(scores, dtype=np.float64))
    assert x.size > 0
    lo = float(x[0] - 4.0 * bandwidth)
    hi = float(x[-1] + 4.0 * bandwidth)
    if hi <= lo:
        lo -= 1.0
        hi += 1.0

    score_grid = np.linspace(lo, hi, max(50, spline_points))
    cdf = np.clip(_smoothed_cdf(score_grid, x, bandwidth), 1e-10, 1.0 - 1e-10)
    keep = np.concatenate(([True], np.diff(cdf) > 1e-10))
    cdf = cdf[keep]
    score_grid = score_grid[keep]
    if cdf.size < 4:
        probs = np.clip(np.exp(-s_eval), 1.0 / (x.size + 1), 1.0)
        return np.quantile(x, probs, method="linear")

    s_fit = np.linspace(float(s_eval.min()), float(s_eval.max()), max(50, spline_points))
    probs = np.clip(np.exp(-s_fit), cdf[0], cdf[-1])
    vals = np.interp(probs, cdf, score_grid)
    vals = _convexify_on_uniform_grid(vals)
    spline = CubicSpline(s_fit, vals, bc_type="natural")
    return np.maximum(spline(s_eval), 0.0)


def smoothed_regression_quantile_cost_grid(
    score_batches: list[np.ndarray],
    s_grid: np.ndarray,
    bandwidth: float | None = None,
    bandwidth_multiplier: float = 1.0,
    spline_points: int = 400,
) -> np.ndarray:
    """Smooth regression interval-radius costs using the paper's CDF-inversion recipe.

    Each batch cost is a Gaussian-kernel-smoothed empirical CDF, inverted to a
    quantile curve and spline-smoothed in the log-budget coordinate. The output
    stays grid-valued so the MILP path remains simple and debuggable.
    """
    grid = np.asarray(s_grid, dtype=np.float64)
    out = np.zeros((len(score_batches), grid.size), dtype=np.float64)
    for t, scores in enumerate(score_batches):
        x = np.asarray(scores, dtype=np.float64)
        bw = silverman_bandwidth(x) if bandwidth is None else float(bandwidth)
        bw = max(bw * float(bandwidth_multiplier), 1e-8)
        out[t] = _smoothed_quantile_values(x, grid, bw, spline_points)
    return out


def smoothed_classification_set_size_cost_grid(
    p_value_batches: list[np.ndarray],
    s_grid: np.ndarray,
    bandwidth: float | None = None,
    bandwidth_multiplier: float = 1.0,
    spline_points: int = 400,
) -> np.ndarray:
    """Smooth classification set-size costs from candidate-label p-values.

    For p-values ``p_{ik}``, the raw cost is ``mean_i sum_k 1{p_{ik} > tau}``.
    We replace the indicator by ``Phi((p_{ik} - tau) / h)`` and spline the
    resulting curve in ``s``. This conditions on current test features/scores
    but not on the true test labels.
    """
    grid = np.asarray(s_grid, dtype=np.float64)
    s_fit = np.linspace(float(grid.min()), float(grid.max()), max(50, spline_points))
    tau_fit = 1.0 - np.exp(-s_fit)
    out = np.zeros((len(p_value_batches), grid.size), dtype=np.float64)
    for t, p_values in enumerate(p_value_batches):
        p = np.asarray(p_values, dtype=np.float64)
        if p.ndim == 1:
            p = p[None, :]
        flat = np.clip(p.reshape(-1), 0.0, 1.0)
        bw = silverman_bandwidth(flat, min_bandwidth=0.01) if bandwidth is None else float(bandwidth)
        bw = max(bw * float(bandwidth_multiplier), 0.005)
        z = (flat[:, None] - tau_fit[None, :]) / bw
        vals = norm.cdf(z).sum(axis=0) / p.shape[0]
        vals = _convexify_on_uniform_grid(vals)
        spline = CubicSpline(s_fit, vals, bc_type="natural")
        out[t] = np.clip(spline(grid), 0.0, p.shape[1])
    return out
