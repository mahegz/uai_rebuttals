from __future__ import annotations

import argparse
import json
from pathlib import Path


def _fmt(x: float) -> str:
    return f"{x:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.summary) as f:
        data = json.load(f)
    rows = data["rows"]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    tasks = sorted({r["task"] for r in rows})
    conditions = sorted({r["condition"] for r in rows})
    ks = sorted({int(r["K"]) for r in rows})
    methods = sorted({r["method"] for r in rows})
    deployable = [m for m in methods if m != "oracle"]
    replan = [m for m in deployable if m.startswith("replan_")]

    lines = [
        "# Experiment Efficiency Summary",
        "",
        "Ranking criterion: smaller downstream set size/width `S_mean`. Forecast-error metrics are diagnostic only.",
        "The `oracle` method uses realized future costs and is not deployable.",
        "",
        "## Best Deployable Method by Setting",
        "",
        "| Task | Condition | K | Best method | S | W | Best replan forecast | Replan S | Replan W |",
        "|---|---|---:|---|---:|---:|---|---:|---:|",
    ]

    for task in tasks:
        for condition in conditions:
            for K in ks:
                subset = [
                    r for r in rows
                    if r["task"] == task and r["condition"] == condition and int(r["K"]) == K
                ]
                dep = [r for r in subset if r["method"] in deployable]
                rep = [r for r in subset if r["method"] in replan]
                if not dep:
                    continue
                best = min(dep, key=lambda r: r["S_mean"])
                best_rep = min(rep, key=lambda r: r["S_mean"]) if rep else None
                if best_rep is None:
                    rep_cols = ["--", "--", "--"]
                else:
                    rep_cols = [
                        best_rep["method"],
                        _fmt(best_rep["S_mean"]),
                        _fmt(best_rep["W_mean"]),
                    ]
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            task,
                            condition,
                            str(K),
                            best["method"],
                            _fmt(best["S_mean"]),
                            _fmt(best["W_mean"]),
                            *rep_cols,
                        ]
                    )
                    + " |"
                )

    lines.extend([
        "",
        "## Full Rows",
        "",
        "| Task | Condition | K | Method | S mean | S std | W mean | W std |",
        "|---|---|---:|---|---:|---:|---:|---:|",
    ])
    for r in sorted(rows, key=lambda x: (x["task"], x["condition"], int(x["K"]), x["method"])):
        lines.append(
            "| "
            + " | ".join(
                [
                    r["task"],
                    r["condition"],
                    str(r["K"]),
                    r["method"],
                    _fmt(r["S_mean"]),
                    _fmt(r["S_std"]),
                    _fmt(r["W_mean"]),
                    _fmt(r["W_std"]),
                ]
            )
            + " |"
        )

    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
