# AnyhowCP UAI 2026 Rebuttal Code

This is a deliberately small research-code rewrite for the UAI 2026 rebuttal.
The code mirrors the paper objects directly:

- binary mask families `M`;
- conformal p-values and e-values;
- log-budget schedules `s_t = -log(1 - tau_t)`;
- mask constraints `M @ s <= -log(1 - alpha)`;
- static and sequential solver paths.

The core code is NumPy/SciPy/sklearn-first. JAX is listed for later numerical
experiments, but the core package does not import it at module import time.
PyTorch is not a hard dependency; use it only later if CIFAR-10 logits or
features need to be regenerated.

## Layout

```text
src/anyhowcp/
  masks.py        mask families and validity checks
  conformal.py    p-values, prediction sets, e-values
  costs.py        empirical and smoothed cost grids in log-budget coordinates
  forecast.py     EWMA, trend, blend, and oracle tail forecasts
  solvers.py      SciPy/HiGHS LP and MILP solvers plus a continuous SciPy path
  replanning.py   explicit remaining-budget replanning state
  metrics.py      window failure metrics
  experiments.py  California Housing / CIFAR-10 rebuttal experiment runner
  toy.py          dataset-free checks
scripts/
  toy_check.py
  plan_rebuttal_experiments.py
  run_paper_experiments.py
configs/
  toy.yaml
  rebuttal_template.yaml
  main_experiments.yaml
```

## Toy Checks

From this directory:

```bash
PYTHONPATH=src python scripts/toy_check.py --config configs/toy.yaml
```

This runs only a small synthetic check. It solves the same masked log-budget
problem with:

- `solve_grid_milp`: a grid MILP through `scipy.optimize.milp` / HiGHS;
- `solve_convex_scipy`: a continuous constrained solve for smooth toy costs;
- `run_grid_replanning`: sequential replanning with remaining mask budgets.

The output includes the selected schedules, exact mask failure probabilities,
and a small simulated window failure rate for independent uniform p-values.

## Rebuttal Experiment Hook

The approved rebuttal experiments should plug into `configs/rebuttal_template.yaml`.
Before running data jobs, inspect the plan:

```bash
PYTHONPATH=src python scripts/plan_rebuttal_experiments.py --config configs/rebuttal_template.yaml
```

For regression, feed batches of calibration residual scores into
`smoothed_regression_quantile_cost_grid`, forecast future grids with
`build_replanning_forecasts`, and call `run_grid_replanning`.

For classification, prefer precomputed class-probability or logit files. Convert
candidate scores to conformal p-values with `conformal_p_values`, build set-size
cost grids with `smoothed_classification_set_size_cost_grid`, and use the same
replanning path. Regenerate CIFAR features/logits with PyTorch only if the
precomputed artifact is missing or stale.

## Main Rebuttal Runs

Use the experiment environment from the repository root:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/run_paper_experiments.py \
  --config code/AnyhowCP-uai-2026-submission/configs/main_experiments.yaml
```

The default config runs California Housing and CIFAR-10, drift and no-drift,
`K in {1, 3, 5, 7, 9}`, and the deployable forecasters `ewma` and `blend`.
The `trend` forecaster remains in the pilot config as a diagnostic, but the
main run excludes it because the first pilot made it look too volatile. The
runner can log an offline `oracle` diagnostic when `include_oracle: true`; do
not describe oracle numbers as deployable. The main/base configs disable oracle
to keep the full 100-run reproduction focused on deployable methods.

For a quick smoke check:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/run_paper_experiments.py \
  --config code/AnyhowCP-uai-2026-submission/configs/smoke_experiments.yaml
```

Summarize a completed run by downstream efficiency:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/summarize_experiment_results.py \
  --summary .workspace/experiments/main/summary.json \
  --out .workspace/experiments/main/efficiency_summary.md
```
