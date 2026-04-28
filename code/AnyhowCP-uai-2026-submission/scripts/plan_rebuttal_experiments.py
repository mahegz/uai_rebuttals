from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anyhowcp.masks import all_ones_masks, sliding_window_masks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "rebuttal_template.yaml"))
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    T = int(cfg["T"])
    windows = [int(k) for k in cfg["window_sizes"]]
    mask_summary = {
        f"sliding_window_K={K}": {
            "num_masks": int(sliding_window_masks(T, K).shape[0]),
            "support_size": K,
        }
        for K in windows
    }
    mask_summary["all_ones"] = {
        "num_masks": int(all_ones_masks(T).shape[0]),
        "support_size": T,
    }

    print(
        json.dumps(
            {
                "note": "Planning only. This script does not download data or run experiments.",
                "config": cfg,
                "mask_summary": mask_summary,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
