"""Conformal p-values, prediction sets, and the small anytime baseline."""

from __future__ import annotations

import numpy as np


def conformal_p_value(calibration_scores: np.ndarray, candidate_score: float) -> float:
    scores = np.asarray(calibration_scores, dtype=np.float64)
    n = scores.size + 1
    return float((1 + np.sum(scores > candidate_score)) / n)


def conformal_p_values(calibration_scores: np.ndarray, candidate_scores: np.ndarray) -> np.ndarray:
    scores = np.asarray(calibration_scores, dtype=np.float64)
    candidates = np.asarray(candidate_scores, dtype=np.float64)
    n = scores.size + 1
    return (1 + np.sum(scores[:, None] > candidates[None, :], axis=0)) / n


def prediction_set_from_p_values(p_values: np.ndarray, tau: float) -> np.ndarray:
    return np.flatnonzero(np.asarray(p_values, dtype=np.float64) > tau)


def absolute_residual_scores(y: np.ndarray, y_hat: np.ndarray) -> np.ndarray:
    return np.abs(np.asarray(y, dtype=np.float64) - np.asarray(y_hat, dtype=np.float64))


def regression_radius(calibration_scores: np.ndarray, tau: float) -> float:
    scores = np.sort(np.asarray(calibration_scores, dtype=np.float64))
    n = scores.size + 1
    q = int(np.ceil((1.0 - tau) * n)) - 1
    q = int(np.clip(q, 0, scores.size - 1))
    return float(scores[q])


def e_value(calibration_scores: np.ndarray, candidate_score: float) -> float:
    scores = np.asarray(calibration_scores, dtype=np.float64)
    total = float(scores.sum() + candidate_score)
    assert total > 0.0
    return float((scores.size + 1) * candidate_score / total)


def e_values(calibration_scores: np.ndarray, candidate_scores: np.ndarray) -> np.ndarray:
    scores = np.asarray(calibration_scores, dtype=np.float64)
    candidates = np.asarray(candidate_scores, dtype=np.float64)
    total = scores.sum() + candidates
    assert np.all(total > 0.0)
    return (scores.size + 1) * candidates / total
