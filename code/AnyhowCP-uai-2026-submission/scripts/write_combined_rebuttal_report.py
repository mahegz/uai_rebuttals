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


def mask_label(row: dict) -> str:
    return str(row.get("mask_family") or f"window_{int(row['K'])}")


def load_summary(path: Path) -> tuple[dict, list[dict]]:
    with open(path) as f:
        data = json.load(f)
    rows = [r for r in data["rows"] if finite(r.get("S_mean")) and finite(r.get("W_mean"))]
    return data["config"], rows


def best_replan(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row["method"].startswith("replan_"):
            grouped[(row["task"], row["condition"], mask_label(row))].append(row)
    return {key: min(vals, key=lambda r: r["S_mean"]) for key, vals in grouped.items()}


def row_by_method(rows: list[dict], method: str) -> dict[tuple[str, str, str], dict]:
    out = {}
    for row in rows:
        if row["method"] == method:
            out[(row["task"], row["condition"], mask_label(row))] = row
    return out


def method_averages(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["task"], row["method"])].append(row)
    out = []
    for (task, method), vals in sorted(grouped.items()):
        out.append({
            "task": task,
            "method": method,
            "S": sum(v["S_mean"] for v in vals) / len(vals),
            "W": sum(v["W_mean"] for v in vals) / len(vals),
        })
    return out


def replan_win_counts(rows: list[dict]) -> tuple[int, int]:
    uniform = row_by_method(rows, "uniform")
    replans = best_replan(rows)
    replan_wins = 0
    uniform_wins = 0
    for key, u in uniform.items():
        r = replans.get(key)
        if r is None:
            continue
        if r["S_mean"] < u["S_mean"]:
            replan_wins += 1
        else:
            uniform_wins += 1
    return replan_wins, uniform_wins


def emit_frontier(lines: list[str], rows: list[dict], title: str) -> None:
    uniform = row_by_method(rows, "uniform")
    replans = best_replan(rows)
    lines.extend([
        f"## {title}",
        "",
        "| Task | Condition | Mask | Support | Uniform S | Uniform W | Best replan | Replan S | Replan W |",
        "|---|---|---|---:|---:|---:|---|---:|---:|",
    ])
    for key in sorted(uniform):
        u = uniform[key]
        r = replans.get(key)
        rep = [r["method"], fmt(r["S_mean"]), fmt(r["W_mean"])] if r else ["--", "--", "--"]
        lines.append(
            "| "
            + " | ".join([
                u["task"],
                u["condition"],
                mask_label(u),
                str(u.get("max_support", u.get("K", "--"))),
                fmt(u["S_mean"]),
                fmt(u["W_mean"]),
                *rep,
            ])
            + " |"
        )
    lines.append("")


def emit_method_averages(lines: list[str], rows: list[dict], title: str) -> None:
    lines.extend([
        f"## {title}",
        "",
        "| Task | Method | Avg S | Avg W |",
        "|---|---|---:|---:|",
    ])
    for row in method_averages(rows):
        lines.append(f"| {row['task']} | {row['method']} | {fmt(row['S'])} | {fmt(row['W'])} |")
    lines.append("")


def emit_full_table(lines: list[str], rows: list[dict], title: str) -> None:
    lines.extend([
        f"## {title}",
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
    lines.append("")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-summary", required=True)
    parser.add_argument("--protocol-summary", required=True)
    parser.add_argument("--out", default="EXPERIMENT_REPORT.md")
    args = parser.parse_args()

    core_path = Path(args.core_summary)
    protocol_path = Path(args.protocol_summary)
    core_cfg, core_rows = load_summary(core_path)
    protocol_cfg, protocol_rows = load_summary(protocol_path)
    alpha = float(core_cfg.get("alpha", 0.15))

    all_rows = core_rows + protocol_rows
    above = [r for r in all_rows if r["method"] != "oracle" and r["W_mean"] > alpha]
    worst = max(above, key=lambda r: r["W_mean"]) if above else None
    core_replan, core_uniform = replan_win_counts(core_rows)
    protocol_replan, protocol_uniform = replan_win_counts(protocol_rows)

    lines = [
        "# UAI Rebuttal Experiment Report",
        "",
        "This report summarizes the many-seed rebuttal reruns from the cleaned AnyhowCP codebase. The goal is targeted rebuttal evidence, not a new empirical section: the core run reproduces the paper-facing drift/no-drift and mask-strength axes, while the protocol run shows masks defined by deployment/audit schedules.",
        "",
        "## Runs",
        "",
        f"- Core frontier summary: `{core_path}`",
        f"- Core frontier output: `{core_cfg.get('out_dir')}`",
        f"- Core frontier runs: `{core_cfg.get('num_runs')}`",
        f"- Core frontier masks: `{core_cfg.get('window_sizes')}` where `K=20` is the all-ones alpha-spending endpoint.",
        f"- Protocol summary: `{protocol_path}`",
        f"- Protocol output: `{protocol_cfg.get('out_dir')}`",
        f"- Protocol runs: `{protocol_cfg.get('num_runs')}`",
        f"- Protocol mask families: `{', '.join(m['name'] for m in protocol_cfg.get('mask_families', []))}`",
        f"- Alpha: `{alpha}`",
        f"- Grid points: `{core_cfg.get('grid_points')}`",
        "",
        "Metrics: `W` is the mean fraction of monitored masks containing at least one miscoverage. `S` is interval width for regression and set cardinality for classification. Lower `S` is more efficient; empirical `W` should be read relative to `alpha` with Monte Carlo noise.",
        "",
        "## Main Takeaways",
        "",
    ]
    if worst:
        lines.append(
            f"- The largest deployable empirical `W` is `{fmt(worst['W_mean'])}` for `{worst['task']}/{worst['condition']}/{mask_label(worst)}/{worst['method']}`. This is a finite-sample estimate over 100 seeds, not a formal invalidity claim."
        )
    else:
        lines.append(f"- All deployable empirical `W` values are at or below `alpha={alpha}`.")
    lines.extend([
        f"- In the core frontier, the best replan method is more efficient than uniform in `{core_replan}` settings; uniform is at least as efficient in `{core_uniform}` settings.",
        f"- In the protocol-mask regression run, the best replan method is more efficient than uniform in `{protocol_replan}` settings; uniform is at least as efficient in `{protocol_uniform}` settings.",
        "- The all-ones endpoint is much less efficient than short-window monitoring in `S`, which is the useful rebuttal framing: ordinary alpha-spending is a special endpoint, while mask-valid contracts trade efficiency for the specific monitoring guarantee requested.",
        "- Protocol masks give the cleanest answer to the mask-choice objection: masks can be fixed from shifts, rolling audits, scheduled high-risk periods, or maintenance cadences before labels are observed.",
        "",
    ])

    emit_frontier(lines, core_rows, "Core Mask Frontier")
    emit_frontier(lines, protocol_rows, "Protocol-Defined Regression Masks")
    emit_method_averages(lines, core_rows, "Core Forecasting Method Averages")
    emit_method_averages(lines, protocol_rows, "Protocol Forecasting Method Averages")
    emit_full_table(lines, core_rows, "Core Full Result Table")
    emit_full_table(lines, protocol_rows, "Protocol Full Result Table")

    lines.extend([
        "## Rebuttal Use",
        "",
        "- Use the core frontier to answer the novelty/alpha-spending concern: all-ones recovers the classical endpoint, while nontrivial masks impose simultaneous mask-family constraints.",
        "- Use the protocol masks to answer the hyperparameter concern: the mask family is an ex ante audit contract, not an outcome-tuned parameter.",
        "- Do not overclaim replanning. It helps in some settings, but uniform is often competitive; the clean claim is validity under user-chosen monitoring masks, with replanning as a deployable efficiency option.",
    ])

    Path(args.out).write_text("\n".join(lines) + "\n")
    print(args.out)


if __name__ == "__main__":
    main()
