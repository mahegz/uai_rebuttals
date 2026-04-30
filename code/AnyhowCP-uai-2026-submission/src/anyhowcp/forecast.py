"""Forecast realized cost grids for restricted closed-loop replanning."""

from __future__ import annotations

import numpy as np

from anyhowcp.costs import ewma_cost_grid


def _weighted_trend(history: np.ndarray, decay: float) -> np.ndarray:
    H = np.asarray(history, dtype=np.float64)
    if H.shape[0] < 2:
        return np.zeros(H.shape[1], dtype=np.float64)
    t = np.arange(H.shape[0], dtype=np.float64)
    w = np.array([decay ** (H.shape[0] - 1 - i) for i in range(H.shape[0])], dtype=np.float64)
    w = w / w.sum()
    t_bar = float(w @ t)
    y_bar = np.sum(w[:, None] * H, axis=0)
    denom = float(np.sum(w * (t - t_bar) ** 2))
    if denom <= 1e-12:
        return np.zeros(H.shape[1], dtype=np.float64)
    return np.sum(w[:, None] * (t[:, None] - t_bar) * (H - y_bar[None, :]), axis=0) / denom


def forecast_row(
    history: np.ndarray,
    horizon: int,
    kind: str = "ewma",
    decay: float = 0.7,
    blend_weight: float = 0.35,
) -> np.ndarray:
    """Forecast one future cost-grid row from cost history available now.

    ``history`` is ordered oldest to newest. The returned row has the same
    grid shape as a realized cost row. Forecasts are clipped to remain
    nonnegative, but mask validity still comes from log-budget constraints,
    not from any forecasting assumption.
    """
    H = np.asarray(history, dtype=np.float64)
    assert H.ndim == 2 and H.shape[0] >= 1
    assert horizon >= 1
    kind = kind.lower()

    if kind == "last":
        pred = H[-1]
    elif kind == "mean":
        pred = H.mean(axis=0)
    elif kind == "ewma":
        pred = ewma_cost_grid([row for row in H], decay=decay)
    elif kind == "trend":
        slope = _weighted_trend(H, decay=decay)
        pred = H[-1] + horizon * slope
    elif kind == "blend":
        ewma = ewma_cost_grid([row for row in H], decay=decay)
        slope = _weighted_trend(H, decay=decay)
        trend = H[-1] + horizon * slope
        prior = H.mean(axis=0)
        pred = blend_weight * trend + (1.0 - blend_weight) * 0.5 * (ewma + prior)
    else:
        raise ValueError(f"unknown forecaster kind {kind!r}")

    pred = np.maximum(np.asarray(pred, dtype=np.float64), 0.0)
    return np.minimum.accumulate(pred)


def build_replanning_forecasts(
    realized_cost_grid: np.ndarray,
    kind: str = "ewma",
    decay: float = 0.7,
    blend_weight: float = 0.35,
) -> list[np.ndarray]:
    """Build the tail forecast list expected by ``run_grid_replanning``.

    The first row of each tail forecast is always the current realized cost
    curve, which is available from the current calibration batch. Rows beyond
    the current time are predicted from previous/current calibration batches.
    """
    realized = np.asarray(realized_cost_grid, dtype=np.float64)
    assert realized.ndim == 2
    T = realized.shape[0]
    kind = kind.lower()
    forecasts: list[np.ndarray] = []
    for t in range(T):
        rows = [realized[t]]
        history = realized[: t + 1]
        for u in range(t + 1, T):
            rows.append(
                forecast_row(
                    history,
                    horizon=u - t,
                    kind=kind,
                    decay=decay,
                    blend_weight=blend_weight,
                )
            )
        forecasts.append(np.vstack(rows))
    return forecasts


def forecast_error_summary(realized_cost_grid: np.ndarray, forecasts: list[np.ndarray]) -> dict[str, float]:
    realized = np.asarray(realized_cost_grid, dtype=np.float64)
    abs_errors = []
    sq_errors = []
    deriv_abs_errors = []
    for t, tail in enumerate(forecasts):
        for h in range(1, tail.shape[0]):
            pred = tail[h]
            truth = realized[t + h]
            err = pred - truth
            abs_errors.append(np.abs(err).mean())
            sq_errors.append(np.mean(err**2))
            if pred.size >= 2:
                deriv_abs_errors.append(np.abs(np.diff(pred) - np.diff(truth)).mean())
    if not abs_errors:
        return {"mae": 0.0, "rmse": 0.0, "derivative_mae": 0.0}
    return {
        "mae": float(np.mean(abs_errors)),
        "rmse": float(np.sqrt(np.mean(sq_errors))),
        "derivative_mae": float(np.mean(deriv_abs_errors)) if deriv_abs_errors else 0.0,
    }
