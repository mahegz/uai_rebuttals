from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anyhowcp.experiments import run_paper_experiments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "main_experiments.yaml"))
    parser.add_argument("--num-runs", type=int, default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--grid-points", type=int, default=None)
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    if args.num_runs is not None:
        cfg["num_runs"] = args.num_runs
    if args.out_dir is not None:
        cfg["out_dir"] = args.out_dir
    if args.grid_points is not None:
        cfg["grid_points"] = args.grid_points

    summary = run_paper_experiments(cfg)
    print(json.dumps({"out_dir": cfg["out_dir"], "num_rows": len(summary["rows"])}, indent=2))


if __name__ == "__main__":
    main()
