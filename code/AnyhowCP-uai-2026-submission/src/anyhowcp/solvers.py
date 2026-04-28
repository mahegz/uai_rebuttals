"""Small solver interfaces for the mask-valid log-budget programs."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp, minimize
from scipy.sparse import lil_matrix

from anyhowcp.masks import as_mask_matrix, log_budget


@dataclass
class SolverResult:
    s: np.ndarray
    objective: float
    status: str


def _budgets(masks: np.ndarray, alpha: float, budgets: np.ndarray | None) -> np.ndarray:
    M = as_mask_matrix(masks)
    if budgets is None:
        return np.full(M.shape[0], log_budget(alpha), dtype=np.float64)
    b = np.asarray(budgets, dtype=np.float64)
    assert b.shape == (M.shape[0],)
    return b


def solve_linear_highs(
    profit: np.ndarray,
    masks: np.ndarray,
    alpha: float = 0.15,
    budgets: np.ndarray | None = None,
    s_max: float | None = None,
) -> SolverResult:
    M = as_mask_matrix(masks)
    p = np.asarray(profit, dtype=np.float64)
    assert p.shape == (M.shape[1],)
    b = _budgets(M, alpha, budgets)
    upper = log_budget(alpha) if s_max is None else float(s_max)

    res = linprog(
        c=-p,
        A_ub=M,
        b_ub=b,
        bounds=[(0.0, upper)] * M.shape[1],
        method="highs",
    )
    assert res.success, res.message
    return SolverResult(s=res.x, objective=float(p @ res.x), status=res.message)


def solve_grid_milp(
    cost_grid: np.ndarray,
    s_grid: np.ndarray,
    masks: np.ndarray,
    alpha: float = 0.15,
    budgets: np.ndarray | None = None,
) -> SolverResult:
    costs = np.asarray(cost_grid, dtype=np.float64)
    grid = np.asarray(s_grid, dtype=np.float64)
    M = as_mask_matrix(masks)
    assert costs.ndim == 2
    T, G = costs.shape
    assert grid.shape == (G,)
    assert M.shape[1] == T
    b = _budgets(M, alpha, budgets)

    n_vars = T * G
    n_constraints = T + M.shape[0]
    A = lil_matrix((n_constraints, n_vars), dtype=np.float64)
    lower = np.zeros(n_constraints, dtype=np.float64)
    upper = np.zeros(n_constraints, dtype=np.float64)

    for t in range(T):
        row = t
        lower[row] = 1.0
        upper[row] = 1.0
        for g in range(G):
            A[row, t * G + g] = 1.0

    for j in range(M.shape[0]):
        row = T + j
        lower[row] = -np.inf
        upper[row] = b[j]
        for t in range(T):
            if M[j, t] == 0.0:
                continue
            for g in range(G):
                A[row, t * G + g] = grid[g]

    res = milp(
        c=costs.reshape(-1),
        integrality=np.ones(n_vars),
        bounds=Bounds(np.zeros(n_vars), np.ones(n_vars)),
        constraints=LinearConstraint(A.tocsr(), lower, upper),
        options={"mip_rel_gap": 1e-9},
    )
    assert res.success, res.message
    x = res.x.reshape(T, G)
    idx = np.argmax(x, axis=1)
    s = grid[idx]
    return SolverResult(s=s, objective=float(costs[np.arange(T), idx].sum()), status=res.message)


def solve_convex_scipy(
    value_and_grad,
    masks: np.ndarray,
    alpha: float = 0.15,
    budgets: np.ndarray | None = None,
    s_max: float | None = None,
    x0: np.ndarray | None = None,
) -> SolverResult:
    M = as_mask_matrix(masks)
    b = _budgets(M, alpha, budgets)
    T = M.shape[1]
    upper = log_budget(alpha) if s_max is None else float(s_max)

    if x0 is None:
        row_sums = M.sum(axis=1)
        cap = np.min(np.divide(b, row_sums, out=np.full_like(b, upper), where=row_sums > 0))
        x0 = np.full(T, min(upper, 0.5 * cap), dtype=np.float64)

    def objective(s: np.ndarray) -> float:
        values, _ = value_and_grad(s)
        return float(np.sum(values))

    def gradient(s: np.ndarray) -> np.ndarray:
        _, grad = value_and_grad(s)
        return np.asarray(grad, dtype=np.float64)

    res = minimize(
        objective,
        np.asarray(x0, dtype=np.float64),
        jac=gradient,
        bounds=Bounds(np.zeros(T), np.full(T, upper)),
        constraints=[LinearConstraint(M, -np.inf * np.ones(M.shape[0]), b)],
        method="SLSQP",
        options={"maxiter": 500, "ftol": 1e-12},
    )
    assert res.success, res.message
    return SolverResult(s=res.x, objective=float(res.fun), status=res.message)
