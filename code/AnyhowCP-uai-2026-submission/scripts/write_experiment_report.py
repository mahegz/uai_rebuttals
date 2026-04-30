from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def fmt(x, digits: int = 3) -> str:
    if x is None:
        return "--"
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return "--"
    return f"{float(x):.{digits}f}"


def finite(x) -> bool:
    return x is not None and not (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))


def load_rows(summary_path: Path) -> tuple[dict, list[dict]]:
    with open(summary_path) as f:
        data = json.load(f)
    rows = [r for r in data["rows"] if finite(r.get("S_mean")) and finite(r.get("W_mean"))]
    return data["config"], rows


def mask_label(r: dict) -> str:
    return str(r.get("mask_family") or f"window_{int(r['K'])}")


def row_lookup(rows: list[dict]) -> dict[tuple[str, str, str, str], dict]:
    return {
        (r["task"], r["condition"], mask_label(r), r["method"]): r
        for r in rows
    }


def best_method(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in rows:
        grouped[(r["task"], r["condition"], mask_label(r))].append(r)
    out = []
    for key in sorted(grouped):
        vals = grouped[key]
        best = min(vals, key=lambda r: r["S_mean"])
        replans = [r for r in vals if r["method"].startswith("replan_")]
        best_replan = min(replans, key=lambda r: r["S_mean"]) if replans else None
        task, condition, mask = key
        out.append({
            "task": task,
            "condition": condition,
            "mask": mask,
            "best": best,
            "best_replan": best_replan,
        })
    return out


def method_average(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        grouped[(r["task"], r["method"])].append(r)
    out = []
    for (task, method), vals in sorted(grouped.items()):
        s_vals = [v["S_mean"] for v in vals if finite(v["S_mean"])]
        w_vals = [v["W_mean"] for v in vals if finite(v["W_mean"])]
        out.append({
            "task": task,
            "method": method,
            "S_mean": sum(s_vals) / len(s_vals) if s_vals else float("nan"),
            "W_mean": sum(w_vals) / len(w_vals) if w_vals else float("nan"),
        })
    return out


def emit_report(summary_path: Path, out_path: Path) -> None:
    cfg, rows = load_rows(summary_path)
    lookup = row_lookup(rows)
    methods = sorted({r["method"] for r in rows})
    replan_methods = [m for m in methods if m.startswith("replan_")]
    masks = sorted({mask_label(r) for r in rows})
    num_runs = int(cfg.get("num_runs", 0))
    alpha = float(cfg.get("alpha", 0.15))

    lines: list[str] = []
    lines.extend([
        "# UAI Rebuttal Experiment Report",
        "",
        "This report summarizes the rerun in the cleaned rebuttal codebase. The run uses the paper's core axes: California Housing regression and CIFAR-10 classification; no-drift and drift settings; `T=20`; mask-valid spending schedules; and multiple deployable forecasters.",
        "",
        "## Run Configuration",
        "",
        f"- Summary file: `{summary_path}`",
        f"- Output directory: `{cfg.get('out_dir')}`",
        f"- Runs: `{num_runs}`",
        f"- Grid points: `{cfg.get('grid_points')}`",
        f"- Alpha: `{alpha}`",
        f"- Tasks: `{', '.join(cfg.get('tasks', []))}`",
        f"- Conditions: `{', '.join(cfg.get('conditions', []))}`",
        f"- Window sizes: `{cfg.get('window_sizes')}`",
        f"- Mask families: `{', '.join(masks)}`",
        f"- Forecasters: `{', '.join(cfg.get('forecasters', []))}`",
        "",
        f"Metrics: `W` is the mean fraction of monitored masks containing at least one miscoverage. `S` is interval width for regression and set cardinality for classification. Lower `S` is better, while `W` should be interpreted relative to the target `alpha={alpha}` with Monte Carlo variability.",
        "",
        "## Best Method By Setting",
        "",
        "| Task | Condition | Mask | Support | # masks | Best method | S | W | Best replan | Replan S | Replan W |",
        "|---|---|---|---:|---:|---|---:|---:|---|---:|---:|",
    ])
    for item in best_method(rows):
        best = item["best"]
        best_rep = item["best_replan"]
        if best_rep is None:
            rep = ["--", "--", "--"]
        else:
            rep = [best_rep["method"], fmt(best_rep["S_mean"]), fmt(best_rep["W_mean"])]
        lines.append(
            "| "
            + " | ".join([
                item["task"],
                item["condition"],
                item["mask"],
                str(best.get("max_support", best.get("K", "--"))),
                str(best.get("num_masks", "--")),
                best["method"],
                fmt(best["S_mean"]),
                fmt(best["W_mean"]),
                *rep,
            ])
            + " |"
        )

    lines.extend([
        "",
        "## Forecasting Method Comparison",
        "",
        "Averaging across drift settings and mask sizes gives a coarse view of each method's efficiency.",
        "",
        "| Task | Method | Avg S | Avg W |",
        "|---|---|---:|---:|",
    ])
    for r in method_average(rows):
        lines.append(
            f"| {r['task']} | {r['method']} | {fmt(r['S_mean'])} | {fmt(r['W_mean'])} |"
        )

    lines.extend([
        "",
        "## Full Result Table",
        "",
        "| Task | Condition | Mask | Support | # masks | Density | Method | S mean | S std | W mean | W std | Forecast MAE | Forecast RMSE | Deriv MAE |",
        "|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for r in sorted(rows, key=lambda x: (x["task"], x["condition"], mask_label(x), x["method"])):
        lines.append(
            "| "
            + " | ".join([
                r["task"],
                r["condition"],
                mask_label(r),
                str(r.get("max_support", r.get("K", "--"))),
                str(r.get("num_masks", "--")),
                fmt(r.get("mask_density")),
                r["method"],
                fmt(r["S_mean"]),
                fmt(r["S_std"]),
                fmt(r["W_mean"]),
                fmt(r["W_std"]),
                fmt(r.get("forecast_mae")),
                fmt(r.get("forecast_rmse")),
                fmt(r.get("forecast_derivative_mae")),
            ])
            + " |"
        )

    lines.extend([
        "",
        "## Paper Reproduction Notes",
        "",
        f"- The rerun reproduces the paper's main mask-valid axes and drift protocols, but it is not an exact submitted-table clone: this run uses the rewritten flat package, a `{cfg.get('grid_points')}`-point log-budget grid, and `{num_runs}` Monte Carlo runs.",
        "- The submitted paper table used 100 runs and included the archived anytime/e-process baseline. The current rewritten runner focuses on mask-valid uniform spending and closed-loop replanning; the anytime baseline remains in the archived supplementary package.",
        "- Because the current repo intentionally separates the cleaned rebuttal runner from the archived full package, paper-table numerical equality should not be expected until the archived runner and rewritten runner are reconciled.",
        "",
        "## Main Takeaways",
        "",
    ])

    above = [
        r for r in rows
        if finite(r["W_mean"]) and r["W_mean"] > alpha
    ]
    if above:
        worst = max(above, key=lambda r: r["W_mean"])
        lines.append(
            f"- Some empirical `W` estimates exceed `alpha={alpha}` in the `{num_runs}`-run sweep; the largest deployable value is `{fmt(worst['W_mean'])}` for `{worst['task']}/{worst['condition']}/{mask_label(worst)}/{worst['method']}`. Treat these as finite-run estimates, not proof of invalidity."
        )
    else:
        lines.append(f"- All deployable empirical `W` estimates are at or below `alpha={alpha}` in this sweep.")

    for task in sorted({r["task"] for r in rows}):
        task_rows = [r for r in rows if r["task"] == task]
        best = min(task_rows, key=lambda r: r["S_mean"])
        lines.append(
            f"- Best observed deployable `{task}` efficiency is `{best['method']}` under `{best['condition']}`, `{mask_label(best)}`, with `S={fmt(best['S_mean'])}` and `W={fmt(best['W_mean'])}`."
        )

    uniform_better = 0
    replan_better = 0
    settings = sorted({(r["task"], r["condition"], mask_label(r)) for r in rows})
    for task, condition, mask in settings:
        u = lookup.get((task, condition, mask, "uniform"))
        reps = [lookup.get((task, condition, mask, m)) for m in replan_methods]
        reps = [r for r in reps if r is not None]
        if not u or not reps:
            continue
        best_rep = min(reps, key=lambda r: r["S_mean"])
        if best_rep["S_mean"] < u["S_mean"]:
            replan_better += 1
        else:
            uniform_better += 1
    lines.append(
        f"- Across task/condition/mask settings, the best replan method beats uniform spending in `{replan_better}` settings and uniform is at least as efficient in `{uniform_better}` settings."
    )

    lines.extend([
        "",
        "## Artifacts",
        "",
        f"- Machine summary: `{summary_path}`",
        f"- Per-run JSONL: `{Path(cfg.get('out_dir')) / 'per_run.jsonl'}`",
        "- This report intentionally reports aggregate metrics and does not include raw CIFAR or California Housing data.",
    ])

    out_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--out", default="EXPERIMENT_REPORT.md")
    args = parser.parse_args()
    emit_report(Path(args.summary), Path(args.out))
    print(args.out)


if __name__ == "__main__":
    main()
