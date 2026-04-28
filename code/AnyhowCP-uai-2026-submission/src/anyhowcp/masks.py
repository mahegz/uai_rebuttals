"""Binary monitoring masks and log-budget checks."""

from __future__ import annotations

import numpy as np


def log_budget(alpha: float) -> float:
    assert 0.0 < alpha < 1.0
    return float(-np.log1p(-alpha))


def as_mask_matrix(masks: np.ndarray | list[list[int]] | list[np.ndarray]) -> np.ndarray:
    M = np.asarray(masks, dtype=np.float64)
    if M.ndim == 1:
        M = M[None, :]
    assert M.ndim == 2
    assert np.all((M == 0.0) | (M == 1.0))
    return M


def all_ones_masks(T: int) -> np.ndarray:
    assert T >= 1
    return np.ones((1, T), dtype=np.float64)


def singleton_masks(T: int) -> np.ndarray:
    assert T >= 1
    return np.eye(T, dtype=np.float64)


def sliding_window_masks(T: int, K: int) -> np.ndarray:
    assert 1 <= K <= T
    masks = np.zeros((T - K + 1, T), dtype=np.float64)
    for start in range(T - K + 1):
        masks[start, start : start + K] = 1.0
    return masks


def block_partition_masks(T: int, num_blocks: int) -> np.ndarray:
    assert T >= 1
    assert 1 <= num_blocks <= T
    blocks = np.array_split(np.arange(T), num_blocks)
    masks = np.zeros((len(blocks), T), dtype=np.float64)
    for row, idx in enumerate(blocks):
        masks[row, idx] = 1.0
    return masks


def suffix_mask(T: int, length: int) -> np.ndarray:
    assert 1 <= length <= T
    mask = np.zeros((1, T), dtype=np.float64)
    mask[0, T - length :] = 1.0
    return mask


def cadence_mask(T: int, every: int) -> np.ndarray:
    assert 1 <= every <= T
    mask = np.zeros((1, T), dtype=np.float64)
    mask[0, every - 1 :: every] = 1.0
    return mask


def named_mask_family(T: int, spec: dict) -> np.ndarray:
    kind = spec["kind"]
    if kind == "all_ones":
        return all_ones_masks(T)
    if kind == "sliding_window":
        return sliding_window_masks(T, int(spec["K"]))
    if kind == "block_partition":
        return block_partition_masks(T, int(spec["num_blocks"]))
    if kind == "suffix":
        return suffix_mask(T, int(spec["length"]))
    if kind == "cadence":
        return cadence_mask(T, int(spec["every"]))
    raise ValueError(f"unknown mask family kind {kind!r}")


def union_mask(masks: np.ndarray) -> np.ndarray:
    M = as_mask_matrix(masks)
    return (M.sum(axis=0) > 0.0).astype(np.float64)


def uniform_log_schedule(alpha: float, masks: np.ndarray, s_max: float | None = None) -> np.ndarray:
    M = as_mask_matrix(masks)
    L = log_budget(alpha)
    max_support = float(M.sum(axis=1).max())
    assert max_support > 0.0
    s = union_mask(M) * (L / max_support)
    if s_max is not None:
        s = np.minimum(s, s_max)
    return s


def check_log_schedule(
    s: np.ndarray,
    masks: np.ndarray,
    alpha: float,
    budgets: np.ndarray | None = None,
    tol: float = 1e-9,
) -> dict[str, float]:
    s = np.asarray(s, dtype=np.float64)
    M = as_mask_matrix(masks)
    b = np.full(M.shape[0], log_budget(alpha)) if budgets is None else np.asarray(budgets)
    used = M @ s
    slack = b - used
    return {
        "max_used": float(used.max(initial=0.0)),
        "min_slack": float(slack.min(initial=np.inf)),
        "max_violation": float(np.maximum(used - b, 0.0).max(initial=0.0)),
        "valid": float(np.all(used <= b + tol)),
    }


def exact_mask_failure_probabilities(tau: np.ndarray, masks: np.ndarray) -> np.ndarray:
    tau = np.asarray(tau, dtype=np.float64)
    M = as_mask_matrix(masks)
    no_error = np.exp(M @ np.log1p(-tau))
    return 1.0 - no_error
