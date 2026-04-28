# UAI 2026 Rebuttal Repository

This repository contains the cleaned AnyhowCP rebuttal scaffold, the current paper
sources, reviewer-response notes, and many-seed reproduction/extension runs for the
UAI 2026 rebuttal.

The main experiment report is:

- `EXPERIMENT_REPORT.md`

The report summarizes no-drift and drift runs for regression and classification,
sliding-window masks `K in {1,3,5,7,9,20}`, deployable forecasting methods
`last/mean/ewma/trend/blend`, and protocol-defined regression masks. The
`K=20` mask is the all-ones alpha-spending endpoint.

## Reproducing The Current Runs

Core 100-seed frontier:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/run_paper_experiments.py \
  --config code/AnyhowCP-uai-2026-submission/configs/rebuttal_many_seed_g21.yaml
```

Protocol-mask regression run:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/run_paper_experiments.py \
  --config code/AnyhowCP-uai-2026-submission/configs/rebuttal_protocol_regression_100_g21.yaml
```

Then regenerate the human-readable report:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/write_combined_rebuttal_report.py \
  --core-summary .workspace/experiments/rebuttal_core_100_g21/summary.json \
  --protocol-summary .workspace/experiments/rebuttal_protocol_regression_100_g21/summary.json \
  --out EXPERIMENT_REPORT.md
```

Raw datasets are intentionally excluded from version control. Experiment outputs
belong under `.workspace/experiments/`; the compact rebuttal rerun artifacts are
tracked for the current report.
