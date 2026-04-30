# Baseline Codebase Implementation Notes

This note is meant to support experiment design, not to argue for a particular
rebuttal story. It describes what the current baseline runner actually does,
where the optimization is tight, where approximations enter, and what the
already-run forecasting comparisons suggest.

## 1. Base Experiments

The main entrypoint is:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/run_paper_experiments.py \
  --config <config.yaml>
```

The script loads a YAML config and calls `anyhowcp.experiments.run_paper_experiments`.
The base 100-run config is `code/AnyhowCP-uai-2026-submission/configs/base_100_g21.yaml`.
Its intended setting is:

| Field | Base value |
|---|---:|
| `alpha` | `0.15` |
| `T` | `20` |
| `num_runs` | `100` |
| `grid_points` | `21` |
| tasks | `regression`, `classification` |
| conditions | `nodrift`, `drift` |
| masks | sliding windows `K in {1,3,5,7,9}` |
| forecasters | `ewma`, `blend` |

The later 100-seed rebuttal run extended this to `K=20`, which is the all-ones
alpha-spending endpoint, and added `last`, `mean`, and `trend` forecasters.

### Regression Task

Regression uses `code/data/cal_housing_py3.pkz`. The code trains a
`GradientBoostingRegressor` on a fixed train/test split from `base_seed`.
Inside the current runner this fitted context is reused across Monte Carlo
runs, so the run seed changes the batch sampling and drift noise, not the
regression model itself.

For each of the `T=20` batches:

1. A random test-set batch is sampled.
2. Roughly half the batch becomes calibration data.
3. One held-out point from that batch becomes the test point.
4. The rest of the batch is discarded by the current code path.
5. Calibration scores are absolute residuals.
6. The true test p-value and a p-value grid over candidate `y` values are
   computed.

In the drift condition, both calibration and test covariates are shifted by
`0.5 * t/(T-1)`, and the labels receive Gaussian noise with standard deviation
`0.3 * t/(T-1)`.

The reported regression `S` is the mean interval width over the `T` test
points in a run.

### Classification Task

Classification uses precomputed CIFAR-10 probabilities from
`code/data/precomputed/cifar10_probs_T20.npz`. The conformal score is

```python
score = 1.0 / (log1p(probability) ** 0.25)
```

Thus higher class probability gives a smaller score. For each batch, the code
again uses half of the sampled batch as calibration data and one held-out point
as the test point. Candidate-label p-values are computed for the ten classes.

In the drift condition, the code uses the precomputed drift probability table
and additionally flips labels with a rate increasing linearly up to `0.3`.

The reported classification `S` is the mean prediction-set cardinality over the
`T` test points in a run.

### Masks and Validity Metric

The core masks are sliding windows. For a window length `K`, the mask matrix has
`T-K+1` rows, each selecting one contiguous length-`K` interval. The all-ones
endpoint is implemented as `K=T`.

The spending coordinate is

```text
s = -log(1 - tau),
tau = 1 - exp(-s).
```

The log budget for each mask is

```text
L = -log(1 - alpha).
```

For `alpha=0.15`, `L = 0.1625`. With `21` grid points, the solver grid spacing
is about `0.00813` in `s`.

The reported `W` is not per-time miscoverage. It is the mean fraction of
monitored masks that contain at least one miscoverage. For a run with binary
errors `e_t`, a mask fails if any selected time has `e_t=True`.

### Uniform Baseline

The uniform baseline is analytic, not optimized. It sets

```text
s_t = L / max_mask_support
```

on the union of the monitored times, and `s_t=0` outside that union. For
sliding-window masks, the union covers all times, so this is natural. For sparse
protocol masks, this becomes important and is discussed below.

### Current Runner Limitations

The rewritten runner does not currently include the anytime/e-process baseline
from the archived supplementary package. There are `e_value` helpers in
`conformal.py`, but the active experiment runner compares only uniform spending
and grid-based closed-loop replanning.

## 2. Solvers Used and Tightness

The active baseline path uses one solver for replanning:

```python
solve_grid_milp(...)
```

This is called by `run_grid_replanning(...)` at each time step.

### MILP Formulation

For each future time `t` and each grid point `g`, the solver has a binary
variable saying whether time `t` uses grid value `s_grid[g]`. The constraints are:

1. exactly one grid point is selected for each future time;
2. for every active remaining mask, the selected `s` values cannot exceed that
   mask's remaining log budget;
3. variables are binary.

The objective is the sum of forecast costs over the remaining horizon. In other
words, the solver chooses the future spending schedule that minimizes predicted
future interval width or predicted future set size, subject to the remaining mask
budgets.

The implementation uses SciPy's HiGHS MILP backend:

```python
scipy.optimize.milp(..., options={"mip_rel_gap": 1e-9})
```

After solving the tail problem, replanning commits only the first allocation
`s_t`, subtracts it from all masks containing time `t`, and repeats at `t+1`.

### What Is Tight

The MILP is tight for the finite grid objective. The feasibility diagnostics in
the completed 100-seed runs are essentially exact:

| Run | Per-run rows | Max violation | Min slack | Invalid schedules |
|---|---:|---:|---:|---:|
| core frontier | 14,400 | `2.78e-17` | `-2.78e-17` | `0` |
| protocol regression | 4,800 | `0.0` | `0.0` | `0` |

So the log-budget constraints are being enforced to numerical precision.

### What Is Not Tight

There are three approximation layers that matter more than the MILP tolerance.

First, the schedule is grid-valued. With `grid_points=21`, the solver can only
choose one of 21 `s` values between `0` and `L`. The continuous optimum may lie
between grid points.

Second, the objective is a smoothed cost grid, not the exact realized set size or
interval width. Regression costs are Gaussian-kernel-smoothed empirical
quantile curves. Classification costs replace hard indicators `1{p > tau}` with
a Gaussian CDF relaxation and spline the result in `s`.

Third, replanning optimizes forecast future cost curves. Validity does not depend
on forecast accuracy, but efficiency does.

### Unused Solver Paths

`solvers.py` also contains:

- `solve_linear_highs`, for a linear profit objective;
- `solve_convex_scipy`, for continuous SLSQP optimization.

The base experiment runner does not use these paths. The active baseline and
replanning experiments use the grid MILP path.

### Special Case: `K=1`

When `max_support == 1`, the runner does not call the forecasters. It copies the
uniform result for every replan method. This is justified by the code comment:
singleton masks decouple time steps, and all empirical costs decrease with `s`,
so every deployable forecaster chooses the same maximal feasible allocation.

Therefore, any `K=1` equality across forecasters is implementation-imposed, not
an empirical comparison of forecasting quality.

## 3. Forecasting Used

Forecasting is applied to cost curves, not directly to errors or p-values. At
time `t`, the current cost curve is treated as known. The unknown future cost
curves are predicted from the history of realized cost curves up to time `t`.

The deployable forecasters are:

| Forecaster | Implementation |
|---|---|
| `last` | repeats the most recent cost curve |
| `mean` | averages all observed cost curves |
| `ewma` | exponentially weighted moving average with `decay=0.7` |
| `trend` | weighted linear trend extrapolation with `decay=0.7` |
| `blend` | `0.35 * trend + 0.65 * 0.5 * (ewma + mean)` |

All forecast curves are clipped to be nonnegative and then forced to be
nonincreasing over the `s` grid via `np.minimum.accumulate`. This monotonicity
matches the expected direction that spending more budget should not increase the
predicted cost.

The summary reports three forecast error diagnostics when forecasts are used:

- `forecast_mae`: mean absolute error over future cost-grid entries;
- `forecast_rmse`: root mean squared error over future cost-grid entries;
- `forecast_derivative_mae`: mean absolute error of grid-slope differences.

These diagnostics exclude the current row because the current row is not
forecasted.

## 4. Effect of Different Forecasting Algorithms

The completed 100-seed core frontier compares `last`, `mean`, `ewma`, `trend`,
and `blend` on sliding windows plus the all-ones endpoint. Averaged over task,
condition, and mask settings:

| Task | Method | Avg S | Avg W |
|---|---|---:|---:|
| classification | uniform | 4.332 | 0.160 |
| classification | replan_last | 4.612 | 0.171 |
| classification | replan_ewma | 5.093 | 0.198 |
| classification | replan_mean | 5.122 | 0.203 |
| classification | replan_blend | 5.242 | 0.178 |
| classification | replan_trend | 5.843 | 0.120 |
| regression | uniform | 367.740 | 0.127 |
| regression | replan_mean | 371.424 | 0.123 |
| regression | replan_ewma | 371.571 | 0.121 |
| regression | replan_last | 372.937 | 0.126 |
| regression | replan_blend | 378.547 | 0.127 |
| regression | replan_trend | 399.465 | 0.126 |

This does not support a blanket claim that replanning improves efficiency. In the
core frontier, the best replan method beats uniform in 10 settings, while uniform
is at least as efficient in 14 settings.

The winner pattern among replan methods was:

| Run | Best-replan wins | Best-replan beats uniform |
|---|---|---|
| core frontier | `mean`: 13, `last`: 10, `blend`: 1 | `mean`: 8, `last`: 1, `blend`: 1 |
| protocol regression | `mean`: 4, `blend`: 2, `last`: 1, `ewma`: 1 | each of `mean`, `blend`, `last`, `ewma`: 1 |

Forecast error averages explain some of this. `trend` has the largest forecast
errors and usually spends conservatively, giving low `W` but high `S`.

| Task | Forecaster | MAE | RMSE | Derivative MAE |
|---|---|---:|---:|---:|
| classification | `ewma` | 1.890 | 2.298 | 0.207 |
| classification | `mean` | 1.940 | 2.309 | 0.206 |
| classification | `last` | 2.072 | 2.682 | 0.234 |
| classification | `blend` | 2.291 | 2.985 | 0.255 |
| classification | `trend` | 3.127 | 4.231 | 0.342 |
| regression | `ewma` | 23.408 | 33.215 | 5.563 |
| regression | `mean` | 25.235 | 34.524 | 5.429 |
| regression | `last` | 25.500 | 37.038 | 6.743 |
| regression | `blend` | 31.876 | 54.069 | 8.294 |
| regression | `trend` | 58.528 | 107.329 | 13.746 |

The lowest forecast error is usually `ewma` or `mean`, but the best downstream
`S` is not always the lowest forecast-error method. The solver is optimizing the
entire mask-constrained allocation problem, so forecast error interacts with mask
geometry, grid discretization, and how conservative the forecast curve is.

### Important Caveat About Protocol-Mask Results

The protocol-mask regression run should not be interpreted as clean evidence
that forecasting is better than uniform spending.

For sparse protocol masks, `uniform_log_schedule` sets `s_t=0` outside the union
of monitored times. The replanning MILP, however, can choose large `s_t` on
times that are not contained in any remaining active mask, because those times
consume no mask budget. Since the current metric averages `S` over all `T` times,
this makes replanning look much better on sparse masks for a partly mechanical
reason.

For example, in the protocol run:

| Setting | Uniform S | Best replan S |
|---|---:|---:|
| regression drift, maintenance cadence | 696.655 | 227.666 |
| regression nodrift, maintenance cadence | 673.890 | 162.548 |
| regression drift, scheduled high-risk suffix | 696.394 | 248.540 |
| regression nodrift, scheduled high-risk suffix | 659.690 | 177.312 |

These numbers are useful for finding an implementation issue, but they are not a
clean rebuttal result. Before using protocol masks as evidence, we should decide
one of the following:

1. evaluate `S` only on monitored times;
2. allow the uniform baseline to spend freely on unmonitored times, matching the
   replanning feasible set;
3. redefine protocol masks so every time belongs to at least one monitored family;
4. report monitored-time and all-time efficiency separately.

Without that fix, the protocol experiment answers a different question than we
probably intended.

## Practical Implications for New Experiment Design

The current implementation is reliable for testing validity under a given mask
family because the log-budget constraints are enforced tightly. The weak point is
not feasibility. The weak points are:

1. the cost objective is smoothed and grid-discretized;
2. forecast quality affects only efficiency, not validity;
3. the current uniform baseline is asymmetric for sparse masks;
4. `S` is averaged over all time steps, which can be misleading when a mask
   family monitors only a sparse subset of times;
5. the active runner does not include the anytime/e-process baseline.

For a clean next experiment, I would first fix the sparse-mask baseline/evaluation
issue, then rerun a smaller diagnostic comparing:

- sliding-window masks, where all times are monitored and the current comparison
  is fair;
- protocol masks with either monitored-time `S` or a uniform baseline that also
  spends freely on unmonitored times;
- `uniform`, `mean`, `ewma`, and maybe `last`;
- `trend` only as a stress test, not as a preferred forecasting method.

That would let the next design separate three effects that are currently mixed:
mask geometry, forecast accuracy, and evaluation convention.
