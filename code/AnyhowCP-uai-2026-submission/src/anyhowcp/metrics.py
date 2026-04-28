"""Small metrics used by rebuttal checks."""

from __future__ import annotations

import numpy as np

from anyhowcp.masks import as_mask_matrix


def mask_failure_indicators(errors: np.ndarray, masks: np.ndarray) -> np.ndarray:
    e = np.asarray(errors, dtype=bool)
    M = as_mask_matrix(masks).astype(bool)
    if e.ndim == 1:
        return np.array([np.any(e[m]) for m in M], dtype=bool)
    assert e.ndim == 2
    return np.stack([np.any(e[:, m], axis=1) for m in M], axis=1)


def window_failure_rate(errors: np.ndarray, masks: np.ndarray) -> float:
    return float(mask_failure_indicators(errors, masks).mean())


def mean_set_size(set_sizes: np.ndarray) -> float:
    return float(np.asarray(set_sizes, dtype=np.float64).mean())
