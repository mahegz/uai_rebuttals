"""Toy checks that exercise the mask constraints and solvers without datasets."""

from __future__ import annotations

import numpy as np

from anyhowcp.costs import exponential_cost_grid, exponential_value_and_grad, s_grid_from_alpha
from anyhowcp.masks import (
    check_log_schedule,
    exact_mask_failure_probabilities,
    sliding_window_masks,
    uniform_log_schedule,
)
from anyhowcp.metrics import window_failure_rate
from anyhowcp.replanning import run_grid_replanning
from anyhowcp.solvers import solve_convex_scipy, solve_grid_milp


def run_toy_check(cfg: dict) -> dict:
    T = int(cfg.get("T", 8))
    K = int(cfg.get("window_size", 3))
    alpha = float(cfg.get("alpha", 0.15))
    grid_points = int(cfg.get("grid_points", 81))
    seed = int(cfg.get("seed", 0))
    simulation_runs = int(cfg.get("simulation_runs", 500))

    rng = np.random.default_rng(seed)
    masks = sliding_window_masks(T, K)
    s_grid = s_grid_from_alpha(alpha, grid_points)

    trend = 1.0 + 0.7 * np.sin(np.linspace(0.0, 2.0 * np.pi, T, endpoint=False))
    weights = np.clip(trend + 0.15 * rng.normal(size=T), 0.15, None)
    cost_grid = exponential_cost_grid(weights, s_grid)

    milp = solve_grid_milp(cost_grid, s_grid, masks, alpha=alpha)
    convex = solve_convex_scipy(
        exponential_value_and_grad(weights),
        masks,
        alpha=alpha,
        s_max=s_grid[-1],
    )
    uniform_s = uniform_log_schedule(alpha, masks)

    forecasts = [cost_grid[t:] for t in range(T)]
    replan_steps = run_grid_replanning(forecasts, masks, s_grid, alpha=alpha)
    replan_s = np.array([step.s_t for step in replan_steps])

    tau = 1.0 - np.exp(-milp.s)
    exact_failures = exact_mask_failure_probabilities(tau, masks)
    toy_p = rng.random((simulation_runs, T))
    simulated_errors = toy_p <= tau[None, :]

    return {
        "T": T,
        "window_size": K,
        "alpha": alpha,
        "weights": weights.round(4).tolist(),
        "uniform_s": uniform_s.round(6).tolist(),
        "milp_s": milp.s.round(6).tolist(),
        "convex_s": convex.s.round(6).tolist(),
        "replan_s": replan_s.round(6).tolist(),
        "milp_objective": float(milp.objective),
        "convex_objective": float(convex.objective),
        "milp_validity": check_log_schedule(milp.s, masks, alpha),
        "convex_validity": check_log_schedule(convex.s, masks, alpha),
        "replan_validity": check_log_schedule(replan_s, masks, alpha),
        "max_exact_mask_failure_probability": float(exact_failures.max()),
        "simulated_window_failure_rate": window_failure_rate(simulated_errors, masks),
    }
