#!/usr/bin/env python3
"""Shared scoring metrics for CaseSignal v1 scripts."""

from __future__ import annotations

import math


def roc_auc_score(labels: list[int], scores: list[float]) -> float:
    """Compute ROC-AUC using average ranks (handles score ties)."""
    if len(labels) != len(scores) or not labels:
        return 0.5

    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5

    indexed_scores = list(enumerate(scores))
    indexed_scores.sort(key=lambda item: item[1])

    ranks = [0.0] * len(scores)
    i = 0
    while i < len(indexed_scores):
        j = i + 1
        while j < len(indexed_scores) and indexed_scores[j][1] == indexed_scores[i][1]:
            j += 1

        # Ranks are 1-indexed.
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            original_idx = indexed_scores[k][0]
            ranks[original_idx] = avg_rank

        i = j

    pos_rank_sum = sum(ranks[idx] for idx, label in enumerate(labels) if label == 1)
    auc = (pos_rank_sum - (n_pos * (n_pos + 1) / 2.0)) / (n_pos * n_neg)
    return float(max(0.0, min(1.0, auc)))


def precision_at_top_k(labels: list[int], scores: list[float], top_fraction: float) -> tuple[float, int]:
    """Return precision in the highest-risk top-k bucket."""
    if len(labels) != len(scores) or not labels:
        return 0.0, 0

    top_k = max(1, int(math.ceil(len(labels) * top_fraction)))
    sorted_idx = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)[:top_k]
    true_positives = sum(labels[idx] for idx in sorted_idx)
    return true_positives / top_k, top_k


def lift_at_top_k(labels: list[int], scores: list[float], top_fraction: float) -> tuple[float, float, int]:
    """Return top-k lift and base positive rate."""
    if len(labels) != len(scores) or not labels:
        return 0.0, 0.0, 0

    base_rate = sum(labels) / len(labels)
    precision, top_k = precision_at_top_k(labels, scores, top_fraction)
    if base_rate <= 0.0:
        return 0.0, base_rate, top_k
    return precision / base_rate, base_rate, top_k


def reviewer_time_proxy(
    labels: list[int],
    scores: list[float],
    target_positive_share: float,
) -> tuple[float, int]:
    """Estimate review share needed to capture a target share of positives."""
    if len(labels) != len(scores) or not labels:
        return 1.0, 0

    positives = sum(labels)
    if positives == 0:
        return 1.0, len(labels)

    target_hits = max(1, int(math.ceil(positives * target_positive_share)))
    sorted_idx = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)

    captured = 0
    reviewed = 0
    for idx in sorted_idx:
        reviewed += 1
        captured += labels[idx]
        if captured >= target_hits:
            return reviewed / len(labels), reviewed

    return 1.0, len(labels)


def model_metrics(
    labels: list[int],
    scores: list[float],
    top_fraction: float,
    target_positive_share: float,
) -> dict[str, float | int]:
    """Compute core ranking metrics for one score vector."""
    auc = roc_auc_score(labels, scores)
    precision, top_k = precision_at_top_k(labels, scores, top_fraction)
    lift, base_rate, _ = lift_at_top_k(labels, scores, top_fraction)
    review_share, review_count = reviewer_time_proxy(labels, scores, target_positive_share)

    return {
        "roc_auc": auc,
        "precision_top_k": precision,
        "lift_top_k": lift,
        "base_rate": base_rate,
        "top_k_count": top_k,
        "reviewer_time_proxy_share": review_share,
        "reviewer_time_proxy_count": review_count,
        "total_rows": len(labels),
        "positive_rows": sum(labels),
    }
