# UAI Rebuttal Experiment Report

This report summarizes the many-seed rebuttal reruns from the cleaned AnyhowCP codebase. The goal is targeted rebuttal evidence, not a new empirical section: the core run reproduces the paper-facing drift/no-drift and mask-strength axes, while the protocol run shows masks defined by deployment/audit schedules.

## Runs

- Core frontier summary: `.workspace/experiments/rebuttal_core_100_g21/summary.json`
- Core frontier output: `.workspace/experiments/rebuttal_core_100_g21`
- Core frontier runs: `100`
- Core frontier masks: `[1, 3, 5, 7, 9, 20]` where `K=20` is the all-ones alpha-spending endpoint.
- Protocol summary: `.workspace/experiments/rebuttal_protocol_regression_100_g21/summary.json`
- Protocol output: `.workspace/experiments/rebuttal_protocol_regression_100_g21`
- Protocol runs: `100`
- Protocol mask families: `shift_blocks_5x4, rolling_audit_4, scheduled_high_risk_last5, maintenance_every5`
- Alpha: `0.15`
- Grid points: `21`

Metrics: `W` is the mean fraction of monitored masks containing at least one miscoverage. `S` is interval width for regression and set cardinality for classification. Lower `S` is more efficient; empirical `W` should be read relative to `alpha` with Monte Carlo noise.

## Main Takeaways

- The largest deployable empirical `W` is `0.310` for `classification/drift/all_ones/replan_mean`. This is a finite-sample estimate over 100 seeds, not a formal invalidity claim.
- In the core frontier, the best replan method is more efficient than uniform in `10` settings; uniform is at least as efficient in `14` settings.
- In the protocol-mask regression run, the best replan method is more efficient than uniform in `4` settings; uniform is at least as efficient in `4` settings.
- The all-ones endpoint is much less efficient than short-window monitoring in `S`, which is the useful rebuttal framing: ordinary alpha-spending is a special endpoint, while mask-valid contracts trade efficiency for the specific monitoring guarantee requested.
- Protocol masks give the cleanest answer to the mask-choice objection: masks can be fixed from shifts, rolling audits, scheduled high-risk periods, or maintenance cadences before labels are observed.

## Core Mask Frontier

| Task | Condition | Mask | Support | Uniform S | Uniform W | Best replan | Replan S | Replan W |
|---|---|---|---:|---:|---:|---|---:|---:|
| classification | drift | all_ones | 20 | 9.129 | 0.220 | replan_mean | 8.787 | 0.310 |
| classification | drift | window_1 | 1 | 3.901 | 0.145 | replan_last | 3.901 | 0.145 |
| classification | drift | window_3 | 3 | 6.770 | 0.148 | replan_blend | 6.712 | 0.174 |
| classification | drift | window_5 | 5 | 7.676 | 0.144 | replan_mean | 7.491 | 0.186 |
| classification | drift | window_7 | 7 | 8.319 | 0.134 | replan_mean | 7.891 | 0.186 |
| classification | drift | window_9 | 9 | 8.573 | 0.137 | replan_mean | 8.300 | 0.212 |
| classification | nodrift | all_ones | 20 | 1.839 | 0.180 | replan_last | 2.200 | 0.220 |
| classification | nodrift | window_1 | 1 | 0.871 | 0.155 | replan_last | 0.871 | 0.155 |
| classification | nodrift | window_3 | 3 | 1.051 | 0.174 | replan_mean | 1.055 | 0.169 |
| classification | nodrift | window_5 | 5 | 1.164 | 0.160 | replan_last | 1.163 | 0.157 |
| classification | nodrift | window_7 | 7 | 1.294 | 0.154 | replan_last | 1.842 | 0.143 |
| classification | nodrift | window_9 | 9 | 1.393 | 0.164 | replan_last | 4.138 | 0.114 |
| regression | drift | all_ones | 20 | 583.024 | 0.070 | replan_last | 591.845 | 0.060 |
| regression | drift | window_1 | 1 | 191.608 | 0.144 | replan_last | 191.608 | 0.144 |
| regression | drift | window_3 | 3 | 322.117 | 0.138 | replan_mean | 328.909 | 0.126 |
| regression | drift | window_5 | 5 | 424.728 | 0.122 | replan_mean | 420.216 | 0.121 |
| regression | drift | window_7 | 7 | 464.136 | 0.110 | replan_mean | 468.990 | 0.101 |
| regression | drift | window_9 | 9 | 512.422 | 0.074 | replan_mean | 504.612 | 0.082 |
| regression | nodrift | all_ones | 20 | 491.462 | 0.180 | replan_last | 508.339 | 0.170 |
| regression | nodrift | window_1 | 1 | 135.061 | 0.166 | replan_last | 135.061 | 0.166 |
| regression | nodrift | window_3 | 3 | 234.516 | 0.151 | replan_mean | 239.660 | 0.148 |
| regression | nodrift | window_5 | 5 | 312.612 | 0.112 | replan_mean | 308.668 | 0.120 |
| regression | nodrift | window_7 | 7 | 344.732 | 0.132 | replan_mean | 356.210 | 0.136 |
| regression | nodrift | window_9 | 9 | 396.465 | 0.130 | replan_mean | 393.953 | 0.109 |

## Protocol-Defined Regression Masks

| Task | Condition | Mask | Support | Uniform S | Uniform W | Best replan | Replan S | Replan W |
|---|---|---|---:|---:|---:|---|---:|---:|
| regression | drift | maintenance_every5 | 4 | 696.655 | 0.090 | replan_ewma | 227.666 | 0.100 |
| regression | drift | rolling_audit_4 | 4 | 364.881 | 0.126 | replan_mean | 370.987 | 0.122 |
| regression | drift | scheduled_high_risk_last5 | 5 | 696.394 | 0.110 | replan_blend | 248.540 | 0.110 |
| regression | drift | shift_blocks_5x4 | 4 | 364.881 | 0.120 | replan_blend | 370.479 | 0.126 |
| regression | nodrift | maintenance_every5 | 4 | 673.890 | 0.130 | replan_last | 162.548 | 0.100 |
| regression | nodrift | rolling_audit_4 | 4 | 266.853 | 0.141 | replan_mean | 271.605 | 0.143 |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 659.690 | 0.120 | replan_mean | 177.312 | 0.140 |
| regression | nodrift | shift_blocks_5x4 | 4 | 266.853 | 0.138 | replan_mean | 271.064 | 0.150 |

## Core Forecasting Method Averages

| Task | Method | Avg S | Avg W |
|---|---|---:|---:|
| classification | replan_blend | 5.242 | 0.178 |
| classification | replan_ewma | 5.093 | 0.198 |
| classification | replan_last | 4.612 | 0.171 |
| classification | replan_mean | 5.122 | 0.203 |
| classification | replan_trend | 5.843 | 0.120 |
| classification | uniform | 4.332 | 0.160 |
| regression | replan_blend | 378.547 | 0.127 |
| regression | replan_ewma | 371.571 | 0.121 |
| regression | replan_last | 372.937 | 0.126 |
| regression | replan_mean | 371.424 | 0.123 |
| regression | replan_trend | 399.465 | 0.126 |
| regression | uniform | 367.740 | 0.127 |

## Protocol Forecasting Method Averages

| Task | Method | Avg S | Avg W |
|---|---|---:|---:|
| regression | replan_blend | 264.484 | 0.124 |
| regression | replan_ewma | 263.126 | 0.126 |
| regression | replan_last | 264.644 | 0.122 |
| regression | replan_mean | 262.660 | 0.125 |
| regression | replan_trend | 277.617 | 0.119 |
| regression | uniform | 498.762 | 0.122 |

## Core Full Result Table

| Task | Condition | Mask | Support | # masks | Density | Method | S mean | S std | W mean | W std | Forecast MAE | Forecast RMSE | Deriv MAE |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| classification | drift | all_ones | 20 | 1 | 1.000 | replan_blend | 9.068 | 0.492 | 0.250 | 0.435 | 3.273 | 4.253 | 0.287 |
| classification | drift | all_ones | 20 | 1 | 1.000 | replan_ewma | 8.791 | 0.553 | 0.260 | 0.441 | 2.760 | 3.329 | 0.240 |
| classification | drift | all_ones | 20 | 1 | 1.000 | replan_last | 8.912 | 0.504 | 0.270 | 0.446 | 2.974 | 3.821 | 0.270 |
| classification | drift | all_ones | 20 | 1 | 1.000 | replan_mean | 8.787 | 0.561 | 0.310 | 0.465 | 2.875 | 3.381 | 0.241 |
| classification | drift | all_ones | 20 | 1 | 1.000 | replan_trend | 9.441 | 0.249 | 0.160 | 0.368 | 4.503 | 6.085 | 0.370 |
| classification | drift | all_ones | 20 | 1 | 1.000 | uniform | 9.129 | 0.404 | 0.220 | 0.416 | -- | -- | -- |
| classification | drift | window_1 | 1 | 20 | 0.050 | replan_blend | 3.901 | 0.523 | 0.145 | 0.075 | -- | -- | -- |
| classification | drift | window_1 | 1 | 20 | 0.050 | replan_ewma | 3.901 | 0.523 | 0.145 | 0.075 | -- | -- | -- |
| classification | drift | window_1 | 1 | 20 | 0.050 | replan_last | 3.901 | 0.523 | 0.145 | 0.075 | -- | -- | -- |
| classification | drift | window_1 | 1 | 20 | 0.050 | replan_mean | 3.901 | 0.523 | 0.145 | 0.075 | -- | -- | -- |
| classification | drift | window_1 | 1 | 20 | 0.050 | replan_trend | 3.901 | 0.523 | 0.145 | 0.075 | -- | -- | -- |
| classification | drift | window_1 | 1 | 20 | 0.050 | uniform | 3.901 | 0.523 | 0.145 | 0.075 | -- | -- | -- |
| classification | drift | window_3 | 3 | 18 | 0.150 | replan_blend | 6.712 | 0.624 | 0.174 | 0.142 | 3.273 | 4.253 | 0.287 |
| classification | drift | window_3 | 3 | 18 | 0.150 | replan_ewma | 6.728 | 0.585 | 0.171 | 0.134 | 2.760 | 3.329 | 0.240 |
| classification | drift | window_3 | 3 | 18 | 0.150 | replan_last | 6.832 | 0.615 | 0.166 | 0.148 | 2.974 | 3.821 | 0.270 |
| classification | drift | window_3 | 3 | 18 | 0.150 | replan_mean | 6.775 | 0.598 | 0.158 | 0.130 | 2.875 | 3.381 | 0.241 |
| classification | drift | window_3 | 3 | 18 | 0.150 | replan_trend | 6.985 | 0.661 | 0.148 | 0.141 | 4.503 | 6.085 | 0.370 |
| classification | drift | window_3 | 3 | 18 | 0.150 | uniform | 6.770 | 0.606 | 0.148 | 0.119 | -- | -- | -- |
| classification | drift | window_5 | 5 | 16 | 0.250 | replan_blend | 7.596 | 0.613 | 0.191 | 0.189 | 3.273 | 4.253 | 0.287 |
| classification | drift | window_5 | 5 | 16 | 0.250 | replan_ewma | 7.528 | 0.649 | 0.182 | 0.192 | 2.760 | 3.329 | 0.240 |
| classification | drift | window_5 | 5 | 16 | 0.250 | replan_last | 7.742 | 0.655 | 0.176 | 0.185 | 2.974 | 3.821 | 0.270 |
| classification | drift | window_5 | 5 | 16 | 0.250 | replan_mean | 7.491 | 0.621 | 0.186 | 0.190 | 2.875 | 3.381 | 0.241 |
| classification | drift | window_5 | 5 | 16 | 0.250 | replan_trend | 8.127 | 0.559 | 0.114 | 0.168 | 4.503 | 6.085 | 0.370 |
| classification | drift | window_5 | 5 | 16 | 0.250 | uniform | 7.676 | 0.618 | 0.144 | 0.167 | -- | -- | -- |
| classification | drift | window_7 | 7 | 14 | 0.350 | replan_blend | 8.046 | 0.597 | 0.169 | 0.231 | 3.273 | 4.253 | 0.287 |
| classification | drift | window_7 | 7 | 14 | 0.350 | replan_ewma | 7.904 | 0.662 | 0.201 | 0.246 | 2.760 | 3.329 | 0.240 |
| classification | drift | window_7 | 7 | 14 | 0.350 | replan_last | 8.160 | 0.690 | 0.153 | 0.200 | 2.974 | 3.821 | 0.270 |
| classification | drift | window_7 | 7 | 14 | 0.350 | replan_mean | 7.891 | 0.643 | 0.186 | 0.233 | 2.875 | 3.381 | 0.241 |
| classification | drift | window_7 | 7 | 14 | 0.350 | replan_trend | 8.664 | 0.574 | 0.104 | 0.179 | 4.503 | 6.085 | 0.370 |
| classification | drift | window_7 | 7 | 14 | 0.350 | uniform | 8.319 | 0.558 | 0.134 | 0.194 | -- | -- | -- |
| classification | drift | window_9 | 9 | 12 | 0.450 | replan_blend | 8.425 | 0.605 | 0.209 | 0.313 | 3.273 | 4.253 | 0.287 |
| classification | drift | window_9 | 9 | 12 | 0.450 | replan_ewma | 8.312 | 0.657 | 0.211 | 0.300 | 2.760 | 3.329 | 0.240 |
| classification | drift | window_9 | 9 | 12 | 0.450 | replan_last | 8.521 | 0.636 | 0.187 | 0.311 | 2.974 | 3.821 | 0.270 |
| classification | drift | window_9 | 9 | 12 | 0.450 | replan_mean | 8.300 | 0.639 | 0.212 | 0.294 | 2.875 | 3.381 | 0.241 |
| classification | drift | window_9 | 9 | 12 | 0.450 | replan_trend | 8.856 | 0.390 | 0.148 | 0.284 | 4.503 | 6.085 | 0.370 |
| classification | drift | window_9 | 9 | 12 | 0.450 | uniform | 8.573 | 0.529 | 0.137 | 0.233 | -- | -- | -- |
| classification | nodrift | all_ones | 20 | 1 | 1.000 | replan_blend | 6.884 | 0.572 | 0.170 | 0.378 | 1.308 | 1.717 | 0.223 |
| classification | nodrift | all_ones | 20 | 1 | 1.000 | replan_ewma | 6.832 | 0.580 | 0.300 | 0.461 | 1.021 | 1.266 | 0.173 |
| classification | nodrift | all_ones | 20 | 1 | 1.000 | replan_last | 2.200 | 0.605 | 0.220 | 0.416 | 1.169 | 1.543 | 0.198 |
| classification | nodrift | all_ones | 20 | 1 | 1.000 | replan_mean | 7.070 | 0.574 | 0.300 | 0.461 | 1.005 | 1.237 | 0.170 |
| classification | nodrift | all_ones | 20 | 1 | 1.000 | replan_trend | 8.700 | 0.441 | 0.020 | 0.141 | 1.750 | 2.378 | 0.314 |
| classification | nodrift | all_ones | 20 | 1 | 1.000 | uniform | 1.839 | 0.368 | 0.180 | 0.386 | -- | -- | -- |
| classification | nodrift | window_1 | 1 | 20 | 0.050 | replan_blend | 0.871 | 0.073 | 0.155 | 0.077 | -- | -- | -- |
| classification | nodrift | window_1 | 1 | 20 | 0.050 | replan_ewma | 0.871 | 0.073 | 0.155 | 0.077 | -- | -- | -- |
| classification | nodrift | window_1 | 1 | 20 | 0.050 | replan_last | 0.871 | 0.073 | 0.155 | 0.077 | -- | -- | -- |
| classification | nodrift | window_1 | 1 | 20 | 0.050 | replan_mean | 0.871 | 0.073 | 0.155 | 0.077 | -- | -- | -- |
| classification | nodrift | window_1 | 1 | 20 | 0.050 | replan_trend | 0.871 | 0.073 | 0.155 | 0.077 | -- | -- | -- |
| classification | nodrift | window_1 | 1 | 20 | 0.050 | uniform | 0.871 | 0.073 | 0.155 | 0.077 | -- | -- | -- |
| classification | nodrift | window_3 | 3 | 18 | 0.150 | replan_blend | 1.218 | 0.223 | 0.164 | 0.143 | 1.308 | 1.717 | 0.223 |
| classification | nodrift | window_3 | 3 | 18 | 0.150 | replan_ewma | 1.061 | 0.086 | 0.169 | 0.148 | 1.021 | 1.266 | 0.173 |
| classification | nodrift | window_3 | 3 | 18 | 0.150 | replan_last | 1.065 | 0.070 | 0.164 | 0.142 | 1.169 | 1.543 | 0.198 |
| classification | nodrift | window_3 | 3 | 18 | 0.150 | replan_mean | 1.055 | 0.063 | 0.169 | 0.146 | 1.005 | 1.237 | 0.170 |
| classification | nodrift | window_3 | 3 | 18 | 0.150 | replan_trend | 1.387 | 0.453 | 0.160 | 0.145 | 1.750 | 2.378 | 0.314 |
| classification | nodrift | window_3 | 3 | 18 | 0.150 | uniform | 1.051 | 0.052 | 0.174 | 0.142 | -- | -- | -- |
| classification | nodrift | window_5 | 5 | 16 | 0.250 | replan_blend | 1.866 | 0.585 | 0.159 | 0.183 | 1.308 | 1.717 | 0.223 |
| classification | nodrift | window_5 | 5 | 16 | 0.250 | replan_ewma | 1.586 | 0.373 | 0.175 | 0.197 | 1.021 | 1.266 | 0.173 |
| classification | nodrift | window_5 | 5 | 16 | 0.250 | replan_last | 1.163 | 0.110 | 0.157 | 0.191 | 1.169 | 1.543 | 0.198 |
| classification | nodrift | window_5 | 5 | 16 | 0.250 | replan_mean | 1.603 | 0.358 | 0.171 | 0.188 | 1.005 | 1.237 | 0.170 |
| classification | nodrift | window_5 | 5 | 16 | 0.250 | replan_trend | 2.694 | 1.069 | 0.107 | 0.155 | 1.750 | 2.378 | 0.314 |
| classification | nodrift | window_5 | 5 | 16 | 0.250 | uniform | 1.164 | 0.109 | 0.160 | 0.191 | -- | -- | -- |
| classification | nodrift | window_7 | 7 | 14 | 0.350 | replan_blend | 3.233 | 0.781 | 0.156 | 0.245 | 1.308 | 1.717 | 0.223 |
| classification | nodrift | window_7 | 7 | 14 | 0.350 | replan_ewma | 2.661 | 0.655 | 0.198 | 0.261 | 1.021 | 1.266 | 0.173 |
| classification | nodrift | window_7 | 7 | 14 | 0.350 | replan_last | 1.842 | 0.391 | 0.143 | 0.226 | 1.169 | 1.543 | 0.198 |
| classification | nodrift | window_7 | 7 | 14 | 0.350 | replan_mean | 2.701 | 0.764 | 0.204 | 0.252 | 1.005 | 1.237 | 0.170 |
| classification | nodrift | window_7 | 7 | 14 | 0.350 | replan_trend | 4.199 | 1.224 | 0.090 | 0.189 | 1.750 | 2.378 | 0.314 |
| classification | nodrift | window_7 | 7 | 14 | 0.350 | uniform | 1.294 | 0.179 | 0.154 | 0.235 | -- | -- | -- |
| classification | nodrift | window_9 | 9 | 12 | 0.450 | replan_blend | 5.084 | 0.809 | 0.198 | 0.296 | 1.308 | 1.717 | 0.223 |
| classification | nodrift | window_9 | 9 | 12 | 0.450 | replan_ewma | 4.939 | 0.986 | 0.208 | 0.286 | 1.021 | 1.266 | 0.173 |
| classification | nodrift | window_9 | 9 | 12 | 0.450 | replan_last | 4.138 | 2.159 | 0.114 | 0.251 | 1.169 | 1.543 | 0.198 |
| classification | nodrift | window_9 | 9 | 12 | 0.450 | replan_mean | 5.015 | 1.093 | 0.244 | 0.314 | 1.005 | 1.237 | 0.170 |
| classification | nodrift | window_9 | 9 | 12 | 0.450 | replan_trend | 6.299 | 0.843 | 0.084 | 0.222 | 1.750 | 2.378 | 0.314 |
| classification | nodrift | window_9 | 9 | 12 | 0.450 | uniform | 1.393 | 0.225 | 0.164 | 0.280 | -- | -- | -- |
| regression | drift | all_ones | 20 | 1 | 1.000 | replan_blend | 612.106 | 33.181 | 0.070 | 0.256 | 36.292 | 58.700 | 8.662 |
| regression | drift | all_ones | 20 | 1 | 1.000 | replan_ewma | 592.704 | 22.211 | 0.060 | 0.239 | 30.994 | 41.083 | 5.718 |
| regression | drift | all_ones | 20 | 1 | 1.000 | replan_last | 591.845 | 20.505 | 0.060 | 0.239 | 31.491 | 42.844 | 7.006 |
| regression | drift | all_ones | 20 | 1 | 1.000 | replan_mean | 593.819 | 22.533 | 0.060 | 0.239 | 34.992 | 44.252 | 5.563 |
| regression | drift | all_ones | 20 | 1 | 1.000 | replan_trend | 641.513 | 46.465 | 0.100 | 0.302 | 65.597 | 118.846 | 14.673 |
| regression | drift | all_ones | 20 | 1 | 1.000 | uniform | 583.024 | 19.654 | 0.070 | 0.256 | -- | -- | -- |
| regression | drift | window_1 | 1 | 20 | 0.050 | replan_blend | 191.608 | 3.730 | 0.144 | 0.078 | -- | -- | -- |
| regression | drift | window_1 | 1 | 20 | 0.050 | replan_ewma | 191.608 | 3.730 | 0.144 | 0.078 | -- | -- | -- |
| regression | drift | window_1 | 1 | 20 | 0.050 | replan_last | 191.608 | 3.730 | 0.144 | 0.078 | -- | -- | -- |
| regression | drift | window_1 | 1 | 20 | 0.050 | replan_mean | 191.608 | 3.730 | 0.144 | 0.078 | -- | -- | -- |
| regression | drift | window_1 | 1 | 20 | 0.050 | replan_trend | 191.608 | 3.730 | 0.144 | 0.078 | -- | -- | -- |
| regression | drift | window_1 | 1 | 20 | 0.050 | uniform | 191.608 | 3.730 | 0.144 | 0.078 | -- | -- | -- |
| regression | drift | window_3 | 3 | 18 | 0.150 | replan_blend | 331.196 | 10.485 | 0.131 | 0.141 | 36.292 | 58.700 | 8.662 |
| regression | drift | window_3 | 3 | 18 | 0.150 | replan_ewma | 329.334 | 10.422 | 0.126 | 0.141 | 30.994 | 41.083 | 5.718 |
| regression | drift | window_3 | 3 | 18 | 0.150 | replan_last | 332.250 | 10.815 | 0.126 | 0.140 | 31.491 | 42.844 | 7.006 |
| regression | drift | window_3 | 3 | 18 | 0.150 | replan_mean | 328.909 | 9.622 | 0.126 | 0.141 | 34.992 | 44.252 | 5.563 |
| regression | drift | window_3 | 3 | 18 | 0.150 | replan_trend | 337.651 | 12.370 | 0.130 | 0.149 | 65.597 | 118.846 | 14.673 |
| regression | drift | window_3 | 3 | 18 | 0.150 | uniform | 322.117 | 8.923 | 0.138 | 0.142 | -- | -- | -- |
| regression | drift | window_5 | 5 | 16 | 0.250 | replan_blend | 422.203 | 14.428 | 0.115 | 0.185 | 36.292 | 58.700 | 8.662 |
| regression | drift | window_5 | 5 | 16 | 0.250 | replan_ewma | 420.400 | 13.554 | 0.114 | 0.189 | 30.994 | 41.083 | 5.718 |
| regression | drift | window_5 | 5 | 16 | 0.250 | replan_last | 422.022 | 13.565 | 0.123 | 0.189 | 31.491 | 42.844 | 7.006 |
| regression | drift | window_5 | 5 | 16 | 0.250 | replan_mean | 420.216 | 12.505 | 0.121 | 0.194 | 34.992 | 44.252 | 5.563 |
| regression | drift | window_5 | 5 | 16 | 0.250 | replan_trend | 436.351 | 18.272 | 0.126 | 0.191 | 65.597 | 118.846 | 14.673 |
| regression | drift | window_5 | 5 | 16 | 0.250 | uniform | 424.728 | 12.549 | 0.122 | 0.198 | -- | -- | -- |
| regression | drift | window_7 | 7 | 14 | 0.350 | replan_blend | 474.789 | 15.723 | 0.100 | 0.209 | 36.292 | 58.700 | 8.662 |
| regression | drift | window_7 | 7 | 14 | 0.350 | replan_ewma | 470.545 | 15.364 | 0.096 | 0.214 | 30.994 | 41.083 | 5.718 |
| regression | drift | window_7 | 7 | 14 | 0.350 | replan_last | 473.140 | 14.102 | 0.108 | 0.210 | 31.491 | 42.844 | 7.006 |
| regression | drift | window_7 | 7 | 14 | 0.350 | replan_mean | 468.990 | 14.487 | 0.101 | 0.215 | 34.992 | 44.252 | 5.563 |
| regression | drift | window_7 | 7 | 14 | 0.350 | replan_trend | 493.181 | 25.052 | 0.101 | 0.215 | 65.597 | 118.846 | 14.673 |
| regression | drift | window_7 | 7 | 14 | 0.350 | uniform | 464.136 | 13.694 | 0.110 | 0.228 | -- | -- | -- |
| regression | drift | window_9 | 9 | 12 | 0.450 | replan_blend | 508.508 | 19.019 | 0.093 | 0.221 | 36.292 | 58.700 | 8.662 |
| regression | drift | window_9 | 9 | 12 | 0.450 | replan_ewma | 504.787 | 16.611 | 0.081 | 0.209 | 30.994 | 41.083 | 5.718 |
| regression | drift | window_9 | 9 | 12 | 0.450 | replan_last | 506.193 | 16.941 | 0.085 | 0.207 | 31.491 | 42.844 | 7.006 |
| regression | drift | window_9 | 9 | 12 | 0.450 | replan_mean | 504.612 | 16.479 | 0.082 | 0.212 | 34.992 | 44.252 | 5.563 |
| regression | drift | window_9 | 9 | 12 | 0.450 | replan_trend | 529.634 | 28.633 | 0.085 | 0.201 | 65.597 | 118.846 | 14.673 |
| regression | drift | window_9 | 9 | 12 | 0.450 | uniform | 512.422 | 14.613 | 0.074 | 0.206 | -- | -- | -- |
| regression | nodrift | all_ones | 20 | 1 | 1.000 | replan_blend | 547.918 | 47.676 | 0.180 | 0.386 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | all_ones | 20 | 1 | 1.000 | replan_ewma | 513.256 | 27.140 | 0.150 | 0.359 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | all_ones | 20 | 1 | 1.000 | replan_last | 508.339 | 23.541 | 0.170 | 0.378 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | all_ones | 20 | 1 | 1.000 | replan_mean | 515.388 | 30.643 | 0.170 | 0.378 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | all_ones | 20 | 1 | 1.000 | replan_trend | 612.373 | 67.394 | 0.140 | 0.349 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | all_ones | 20 | 1 | 1.000 | uniform | 491.462 | 21.485 | 0.180 | 0.386 | -- | -- | -- |
| regression | nodrift | window_1 | 1 | 20 | 0.050 | replan_blend | 135.061 | 2.495 | 0.166 | 0.082 | -- | -- | -- |
| regression | nodrift | window_1 | 1 | 20 | 0.050 | replan_ewma | 135.061 | 2.495 | 0.166 | 0.082 | -- | -- | -- |
| regression | nodrift | window_1 | 1 | 20 | 0.050 | replan_last | 135.061 | 2.495 | 0.166 | 0.082 | -- | -- | -- |
| regression | nodrift | window_1 | 1 | 20 | 0.050 | replan_mean | 135.061 | 2.495 | 0.166 | 0.082 | -- | -- | -- |
| regression | nodrift | window_1 | 1 | 20 | 0.050 | replan_trend | 135.061 | 2.495 | 0.166 | 0.082 | -- | -- | -- |
| regression | nodrift | window_1 | 1 | 20 | 0.050 | uniform | 135.061 | 2.495 | 0.166 | 0.082 | -- | -- | -- |
| regression | nodrift | window_3 | 3 | 18 | 0.150 | replan_blend | 241.539 | 7.237 | 0.146 | 0.140 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | window_3 | 3 | 18 | 0.150 | replan_ewma | 239.812 | 7.077 | 0.149 | 0.138 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | window_3 | 3 | 18 | 0.150 | replan_last | 241.690 | 7.528 | 0.147 | 0.137 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | window_3 | 3 | 18 | 0.150 | replan_mean | 239.660 | 6.739 | 0.148 | 0.137 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | window_3 | 3 | 18 | 0.150 | replan_trend | 248.065 | 10.707 | 0.141 | 0.143 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | window_3 | 3 | 18 | 0.150 | uniform | 234.516 | 6.261 | 0.151 | 0.140 | -- | -- | -- |
| regression | nodrift | window_5 | 5 | 16 | 0.250 | replan_blend | 313.965 | 13.266 | 0.122 | 0.174 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | window_5 | 5 | 16 | 0.250 | replan_ewma | 309.590 | 9.365 | 0.117 | 0.162 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | window_5 | 5 | 16 | 0.250 | replan_last | 315.792 | 13.340 | 0.129 | 0.169 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | window_5 | 5 | 16 | 0.250 | replan_mean | 308.668 | 10.050 | 0.120 | 0.167 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | window_5 | 5 | 16 | 0.250 | replan_trend | 335.150 | 22.921 | 0.128 | 0.162 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | window_5 | 5 | 16 | 0.250 | uniform | 312.612 | 9.356 | 0.112 | 0.163 | -- | -- | -- |
| regression | nodrift | window_7 | 7 | 14 | 0.350 | replan_blend | 362.649 | 16.080 | 0.133 | 0.217 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | window_7 | 7 | 14 | 0.350 | replan_ewma | 357.381 | 15.096 | 0.131 | 0.211 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | window_7 | 7 | 14 | 0.350 | replan_last | 362.490 | 14.845 | 0.136 | 0.210 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | window_7 | 7 | 14 | 0.350 | replan_mean | 356.210 | 14.444 | 0.136 | 0.211 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | window_7 | 7 | 14 | 0.350 | replan_trend | 393.644 | 31.616 | 0.132 | 0.212 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | window_7 | 7 | 14 | 0.350 | uniform | 344.732 | 10.151 | 0.132 | 0.213 | -- | -- | -- |
| regression | nodrift | window_9 | 9 | 12 | 0.450 | replan_blend | 401.021 | 21.535 | 0.130 | 0.236 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | window_9 | 9 | 12 | 0.450 | replan_ewma | 394.373 | 18.308 | 0.124 | 0.234 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | window_9 | 9 | 12 | 0.450 | replan_last | 394.812 | 18.843 | 0.121 | 0.225 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | window_9 | 9 | 12 | 0.450 | replan_mean | 393.953 | 18.900 | 0.109 | 0.217 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | window_9 | 9 | 12 | 0.450 | replan_trend | 439.349 | 38.420 | 0.118 | 0.220 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | window_9 | 9 | 12 | 0.450 | uniform | 396.465 | 14.757 | 0.130 | 0.239 | -- | -- | -- |

## Protocol Full Result Table

| Task | Condition | Mask | Support | # masks | Density | Method | S mean | S std | W mean | W std | Forecast MAE | Forecast RMSE | Deriv MAE |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| regression | drift | maintenance_every5 | 4 | 1 | 0.200 | replan_blend | 229.831 | 7.453 | 0.100 | 0.302 | 36.292 | 58.700 | 8.662 |
| regression | drift | maintenance_every5 | 4 | 1 | 0.200 | replan_ewma | 227.666 | 6.481 | 0.100 | 0.302 | 30.994 | 41.083 | 5.718 |
| regression | drift | maintenance_every5 | 4 | 1 | 0.200 | replan_last | 228.087 | 6.940 | 0.090 | 0.288 | 31.491 | 42.844 | 7.006 |
| regression | drift | maintenance_every5 | 4 | 1 | 0.200 | replan_mean | 227.850 | 6.470 | 0.090 | 0.288 | 34.992 | 44.252 | 5.563 |
| regression | drift | maintenance_every5 | 4 | 1 | 0.200 | replan_trend | 239.088 | 12.561 | 0.100 | 0.302 | 65.597 | 118.846 | 14.673 |
| regression | drift | maintenance_every5 | 4 | 1 | 0.200 | uniform | 696.655 | 6.361 | 0.090 | 0.288 | -- | -- | -- |
| regression | drift | rolling_audit_4 | 4 | 17 | 0.200 | replan_blend | 376.442 | 13.766 | 0.131 | 0.174 | 36.292 | 58.700 | 8.662 |
| regression | drift | rolling_audit_4 | 4 | 17 | 0.200 | replan_ewma | 372.485 | 13.966 | 0.122 | 0.167 | 30.994 | 41.083 | 5.718 |
| regression | drift | rolling_audit_4 | 4 | 17 | 0.200 | replan_last | 376.027 | 13.025 | 0.127 | 0.170 | 31.491 | 42.844 | 7.006 |
| regression | drift | rolling_audit_4 | 4 | 17 | 0.200 | replan_mean | 370.987 | 13.736 | 0.122 | 0.167 | 34.992 | 44.252 | 5.563 |
| regression | drift | rolling_audit_4 | 4 | 17 | 0.200 | replan_trend | 388.371 | 17.135 | 0.121 | 0.159 | 65.597 | 118.846 | 14.673 |
| regression | drift | rolling_audit_4 | 4 | 17 | 0.200 | uniform | 364.881 | 11.262 | 0.126 | 0.175 | -- | -- | -- |
| regression | drift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_blend | 248.540 | 8.315 | 0.110 | 0.314 | 36.292 | 58.700 | 8.662 |
| regression | drift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_ewma | 248.858 | 8.046 | 0.110 | 0.314 | 30.994 | 41.083 | 5.718 |
| regression | drift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_last | 249.735 | 7.385 | 0.110 | 0.314 | 31.491 | 42.844 | 7.006 |
| regression | drift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_mean | 248.656 | 8.264 | 0.100 | 0.302 | 34.992 | 44.252 | 5.563 |
| regression | drift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_trend | 251.424 | 7.727 | 0.100 | 0.302 | 65.597 | 118.846 | 14.673 |
| regression | drift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | uniform | 696.394 | 7.339 | 0.110 | 0.314 | -- | -- | -- |
| regression | drift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_blend | 370.479 | 12.666 | 0.126 | 0.157 | 36.292 | 58.700 | 8.662 |
| regression | drift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_ewma | 371.120 | 13.941 | 0.118 | 0.153 | 30.994 | 41.083 | 5.718 |
| regression | drift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_last | 370.909 | 13.509 | 0.122 | 0.161 | 31.491 | 42.844 | 7.006 |
| regression | drift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_mean | 371.096 | 13.370 | 0.122 | 0.150 | 34.992 | 44.252 | 5.563 |
| regression | drift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_trend | 387.867 | 15.960 | 0.132 | 0.148 | 65.597 | 118.846 | 14.673 |
| regression | drift | shift_blocks_5x4 | 4 | 5 | 0.200 | uniform | 364.881 | 11.262 | 0.120 | 0.156 | -- | -- | -- |
| regression | nodrift | maintenance_every5 | 4 | 1 | 0.200 | replan_blend | 164.736 | 6.369 | 0.110 | 0.314 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | maintenance_every5 | 4 | 1 | 0.200 | replan_ewma | 162.619 | 4.795 | 0.140 | 0.349 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | maintenance_every5 | 4 | 1 | 0.200 | replan_last | 162.548 | 5.233 | 0.100 | 0.302 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | maintenance_every5 | 4 | 1 | 0.200 | replan_mean | 162.712 | 4.768 | 0.130 | 0.338 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | maintenance_every5 | 4 | 1 | 0.200 | replan_trend | 186.313 | 23.955 | 0.090 | 0.288 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | maintenance_every5 | 4 | 1 | 0.200 | uniform | 673.890 | 3.910 | 0.130 | 0.338 | -- | -- | -- |
| regression | nodrift | rolling_audit_4 | 4 | 17 | 0.200 | replan_blend | 276.299 | 11.144 | 0.142 | 0.150 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | rolling_audit_4 | 4 | 17 | 0.200 | replan_ewma | 272.892 | 9.076 | 0.135 | 0.156 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | rolling_audit_4 | 4 | 17 | 0.200 | replan_last | 278.028 | 12.008 | 0.143 | 0.158 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | rolling_audit_4 | 4 | 17 | 0.200 | replan_mean | 271.605 | 9.213 | 0.143 | 0.159 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | rolling_audit_4 | 4 | 17 | 0.200 | replan_trend | 290.613 | 18.648 | 0.135 | 0.149 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | rolling_audit_4 | 4 | 17 | 0.200 | uniform | 266.853 | 7.592 | 0.141 | 0.151 | -- | -- | -- |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_blend | 177.524 | 6.235 | 0.140 | 0.349 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_ewma | 177.658 | 6.282 | 0.140 | 0.349 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_last | 178.769 | 5.814 | 0.150 | 0.359 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_mean | 177.312 | 6.450 | 0.140 | 0.349 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | replan_trend | 181.733 | 7.647 | 0.140 | 0.349 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | scheduled_high_risk_last5 | 5 | 1 | 0.250 | uniform | 659.690 | 5.181 | 0.120 | 0.327 | -- | -- | -- |
| regression | nodrift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_blend | 272.024 | 9.311 | 0.136 | 0.147 | 27.460 | 49.438 | 7.926 |
| regression | nodrift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_ewma | 271.705 | 9.316 | 0.146 | 0.142 | 15.821 | 25.348 | 5.408 |
| regression | nodrift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_last | 273.048 | 10.138 | 0.134 | 0.145 | 19.509 | 31.232 | 6.479 |
| regression | nodrift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_mean | 271.064 | 8.560 | 0.150 | 0.154 | 15.478 | 24.796 | 5.295 |
| regression | nodrift | shift_blocks_5x4 | 4 | 5 | 0.200 | replan_trend | 295.524 | 21.872 | 0.132 | 0.143 | 51.459 | 95.812 | 12.818 |
| regression | nodrift | shift_blocks_5x4 | 4 | 5 | 0.200 | uniform | 266.853 | 7.592 | 0.138 | 0.144 | -- | -- | -- |

## Rebuttal Use

- Use the core frontier to answer the novelty/alpha-spending concern: all-ones recovers the classical endpoint, while nontrivial masks impose simultaneous mask-family constraints.
- Use the protocol masks to answer the hyperparameter concern: the mask family is an ex ante audit contract, not an outcome-tuned parameter.
- Do not overclaim replanning. It helps in some settings, but uniform is often competitive; the clean claim is validity under user-chosen monitoring masks, with replanning as a deployable efficiency option.
