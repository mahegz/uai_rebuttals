"""Sequential replanning with explicit remaining mask budgets."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from anyhowcp.masks import as_mask_matrix, log_budget
from anyhowcp.solvers import SolverResult, solve_grid_milp


@dataclass
class ReplanState:
    masks: np.ndarray
    budgets: np.ndarray
    allocations: list[float]


@dataclass
class ReplanStep:
    t: int
    s_t: float
    tau_t: float
    tail_solution: np.ndarray
    min_remaining_budget: float


def initial_state(masks: np.ndarray, alpha: float) -> ReplanState:
    M = as_mask_matrix(masks)
    return ReplanState(
        masks=M,
        budgets=np.full(M.shape[0], log_budget(alpha), dtype=np.float64),
        allocations=[],
    )


def commit_allocation(state: ReplanState, t: int, s_t: float) -> ReplanState:
    budgets = state.budgets - state.masks[:, t] * s_t
    assert np.all(budgets >= -1e-8)
    return ReplanState(
        masks=state.masks,
        budgets=np.maximum(budgets, 0.0),
        allocations=[*state.allocations, float(s_t)],
    )


def replan_grid_step(
    state: ReplanState,
    t: int,
    forecast_cost_grid: np.ndarray,
    s_grid: np.ndarray,
    alpha: float,
) -> tuple[ReplanStep, ReplanState]:
    tail_masks = state.masks[:, t:]
    active = tail_masks.sum(axis=1) > 0
    result: SolverResult = solve_grid_milp(
        forecast_cost_grid,
        s_grid,
        tail_masks[active],
        alpha=alpha,
        budgets=state.budgets[active],
    )
    s_t = float(result.s[0])
    next_state = commit_allocation(state, t, s_t)
    step = ReplanStep(
        t=t,
        s_t=s_t,
        tau_t=float(1.0 - np.exp(-s_t)),
        tail_solution=result.s,
        min_remaining_budget=float(next_state.budgets.min(initial=np.inf)),
    )
    return step, next_state


def run_grid_replanning(
    forecast_cost_grids: list[np.ndarray],
    masks: np.ndarray,
    s_grid: np.ndarray,
    alpha: float = 0.15,
) -> list[ReplanStep]:
    state = initial_state(masks, alpha)
    steps: list[ReplanStep] = []
    T = as_mask_matrix(masks).shape[1]
    assert len(forecast_cost_grids) == T

    for t in range(T):
        assert forecast_cost_grids[t].shape[0] == T - t
        step, state = replan_grid_step(state, t, forecast_cost_grids[t], s_grid, alpha)
        steps.append(step)
    return steps
