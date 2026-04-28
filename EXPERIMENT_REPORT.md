# UAI Rebuttal Experiment Report

This report summarizes the rerun in the cleaned rebuttal codebase. The run uses the paper's core axes: California Housing regression and CIFAR-10 classification; no-drift and drift settings; `T=20`; `alpha=0.15`; and sliding-window masks `K in {1,3,5,7,9}`. It also extends the paper-facing sweep with multiple deployable forecasters and an offline oracle diagnostic.

## Run Configuration

- Summary file: `.workspace/experiments/rebuttal_expanded_g21/summary.json`
- Output directory: `.workspace/experiments/rebuttal_expanded_g21`
- Runs: `30`
- Grid points: `21`
- Tasks: `regression, classification`
- Conditions: `nodrift, drift`
- Window sizes: `[1, 3, 5, 7, 9]`
- Forecasters: `last, mean, ewma, trend, blend`
- Oracle diagnostic included: `True`

Metrics: `W` is the mean fraction of monitored sliding windows containing at least one miscoverage. `S` is interval width for regression and set cardinality for classification. Lower `S` is better, while `W` should be interpreted relative to the target `alpha=0.15` with Monte Carlo variability.

## Best Deployable Method By Setting

| Task | Condition | K | Best method | S | W | Best replan | Replan S | Replan W |
|---|---|---:|---|---:|---:|---|---:|---:|
| classification | drift | 1 | uniform | 3.917 | 0.143 | replan_last | 3.917 | 0.143 |
| classification | drift | 3 | uniform | 6.690 | 0.141 | replan_blend | 6.692 | 0.176 |
| classification | drift | 5 | replan_mean | 7.540 | 0.206 | replan_mean | 7.540 | 0.206 |
| classification | drift | 7 | replan_ewma | 7.905 | 0.217 | replan_ewma | 7.905 | 0.217 |
| classification | drift | 9 | replan_mean | 8.352 | 0.192 | replan_mean | 8.352 | 0.192 |
| classification | nodrift | 1 | uniform | 0.865 | 0.152 | replan_last | 0.865 | 0.152 |
| classification | nodrift | 3 | uniform | 1.057 | 0.131 | replan_mean | 1.065 | 0.139 |
| classification | nodrift | 5 | uniform | 1.170 | 0.142 | replan_last | 1.170 | 0.131 |
| classification | nodrift | 7 | uniform | 1.277 | 0.138 | replan_last | 1.732 | 0.126 |
| classification | nodrift | 9 | uniform | 1.385 | 0.153 | replan_last | 4.592 | 0.139 |
| regression | drift | 1 | uniform | 190.787 | 0.168 | replan_last | 190.787 | 0.168 |
| regression | drift | 3 | uniform | 320.575 | 0.154 | replan_mean | 327.535 | 0.115 |
| regression | drift | 5 | replan_mean | 417.346 | 0.104 | replan_mean | 417.346 | 0.104 |
| regression | drift | 7 | uniform | 463.015 | 0.090 | replan_mean | 466.428 | 0.093 |
| regression | drift | 9 | replan_mean | 501.218 | 0.067 | replan_mean | 501.218 | 0.067 |
| regression | nodrift | 1 | uniform | 134.542 | 0.178 | replan_last | 134.542 | 0.178 |
| regression | nodrift | 3 | uniform | 233.324 | 0.161 | replan_mean | 239.004 | 0.161 |
| regression | nodrift | 5 | replan_ewma | 308.282 | 0.106 | replan_ewma | 308.282 | 0.106 |
| regression | nodrift | 7 | uniform | 343.881 | 0.100 | replan_mean | 353.415 | 0.117 |
| regression | nodrift | 9 | replan_mean | 389.697 | 0.086 | replan_mean | 389.697 | 0.086 |

## Forecasting Method Comparison

Averaging across drift settings and mask sizes gives a coarse view of each method's efficiency. The oracle row uses realized future costs and is not deployable; it is included only to indicate the price paid for forecasting.

| Task | Method | Avg S | Avg W |
|---|---|---:|---:|
| classification | oracle | 5.076 | 0.253 |
| classification | replan_blend | 4.683 | 0.163 |
| classification | replan_ewma | 4.575 | 0.181 |
| classification | replan_last | 4.483 | 0.141 |
| classification | replan_mean | 4.588 | 0.175 |
| classification | replan_trend | 5.156 | 0.123 |
| classification | uniform | 4.093 | 0.142 |
| regression | oracle | 373.180 | 0.100 |
| regression | replan_blend | 336.715 | 0.126 |
| regression | replan_ewma | 333.349 | 0.121 |
| regression | replan_last | 335.920 | 0.124 |
| regression | replan_mean | 332.853 | 0.120 |
| regression | replan_trend | 353.102 | 0.127 |
| regression | uniform | 332.638 | 0.125 |

## Full Result Table

| Task | Condition | K | Method | S mean | S std | W mean | W std | Forecast MAE | Forecast RMSE | Deriv MAE |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| classification | drift | 1 | replan_blend | 3.917 | 0.527 | 0.143 | 0.080 | -- | -- | -- |
| classification | drift | 1 | replan_ewma | 3.917 | 0.527 | 0.143 | 0.080 | -- | -- | -- |
| classification | drift | 1 | replan_last | 3.917 | 0.527 | 0.143 | 0.080 | -- | -- | -- |
| classification | drift | 1 | replan_mean | 3.917 | 0.527 | 0.143 | 0.080 | -- | -- | -- |
| classification | drift | 1 | replan_trend | 3.917 | 0.527 | 0.143 | 0.080 | -- | -- | -- |
| classification | drift | 1 | uniform | 3.917 | 0.527 | 0.143 | 0.080 | -- | -- | -- |
| classification | drift | 3 | oracle | 6.215 | 0.616 | 0.206 | 0.147 | 0.000 | 0.000 | 0.000 |
| classification | drift | 3 | replan_blend | 6.692 | 0.660 | 0.176 | 0.157 | 3.357 | 4.390 | 0.287 |
| classification | drift | 3 | replan_ewma | 6.692 | 0.601 | 0.167 | 0.116 | 2.740 | 3.310 | 0.239 |
| classification | drift | 3 | replan_last | 6.830 | 0.694 | 0.165 | 0.161 | 2.984 | 3.831 | 0.270 |
| classification | drift | 3 | replan_mean | 6.725 | 0.645 | 0.144 | 0.105 | 2.822 | 3.327 | 0.237 |
| classification | drift | 3 | replan_trend | 6.993 | 0.695 | 0.143 | 0.135 | 4.786 | 6.659 | 0.375 |
| classification | drift | 3 | uniform | 6.690 | 0.540 | 0.141 | 0.098 | -- | -- | -- |
| classification | drift | 5 | oracle | 6.978 | 0.567 | 0.296 | 0.225 | 0.000 | 0.000 | 0.000 |
| classification | drift | 5 | replan_blend | 7.720 | 0.668 | 0.175 | 0.176 | 3.357 | 4.390 | 0.287 |
| classification | drift | 5 | replan_ewma | 7.565 | 0.703 | 0.231 | 0.173 | 2.740 | 3.310 | 0.239 |
| classification | drift | 5 | replan_last | 7.812 | 0.683 | 0.171 | 0.184 | 2.984 | 3.831 | 0.270 |
| classification | drift | 5 | replan_mean | 7.540 | 0.643 | 0.206 | 0.187 | 2.822 | 3.327 | 0.237 |
| classification | drift | 5 | replan_trend | 8.185 | 0.546 | 0.119 | 0.171 | 4.786 | 6.659 | 0.375 |
| classification | drift | 5 | uniform | 7.667 | 0.583 | 0.158 | 0.173 | -- | -- | -- |
| classification | drift | 7 | oracle | 7.442 | 0.489 | 0.321 | 0.258 | 0.000 | 0.000 | 0.000 |
| classification | drift | 7 | replan_blend | 8.042 | 0.625 | 0.133 | 0.205 | 3.357 | 4.390 | 0.287 |
| classification | drift | 7 | replan_ewma | 7.905 | 0.678 | 0.217 | 0.252 | 2.740 | 3.310 | 0.239 |
| classification | drift | 7 | replan_last | 8.192 | 0.766 | 0.143 | 0.204 | 2.984 | 3.831 | 0.270 |
| classification | drift | 7 | replan_mean | 7.922 | 0.670 | 0.190 | 0.222 | 2.822 | 3.327 | 0.237 |
| classification | drift | 7 | replan_trend | 8.783 | 0.561 | 0.100 | 0.165 | 4.786 | 6.659 | 0.375 |
| classification | drift | 7 | uniform | 8.337 | 0.539 | 0.119 | 0.189 | -- | -- | -- |
| classification | drift | 9 | oracle | 7.703 | 0.439 | 0.325 | 0.339 | 0.000 | 0.000 | 0.000 |
| classification | drift | 9 | replan_blend | 8.448 | 0.597 | 0.189 | 0.296 | 3.357 | 4.390 | 0.287 |
| classification | drift | 9 | replan_ewma | 8.373 | 0.693 | 0.217 | 0.311 | 2.740 | 3.310 | 0.239 |
| classification | drift | 9 | replan_last | 8.642 | 0.546 | 0.111 | 0.265 | 2.984 | 3.831 | 0.270 |
| classification | drift | 9 | replan_mean | 8.352 | 0.669 | 0.192 | 0.277 | 2.822 | 3.327 | 0.237 |
| classification | drift | 9 | replan_trend | 8.838 | 0.378 | 0.153 | 0.290 | 4.786 | 6.659 | 0.375 |
| classification | drift | 9 | uniform | 8.567 | 0.522 | 0.142 | 0.227 | -- | -- | -- |
| classification | nodrift | 1 | replan_blend | 0.865 | 0.078 | 0.152 | 0.074 | -- | -- | -- |
| classification | nodrift | 1 | replan_ewma | 0.865 | 0.078 | 0.152 | 0.074 | -- | -- | -- |
| classification | nodrift | 1 | replan_last | 0.865 | 0.078 | 0.152 | 0.074 | -- | -- | -- |
| classification | nodrift | 1 | replan_mean | 0.865 | 0.078 | 0.152 | 0.074 | -- | -- | -- |
| classification | nodrift | 1 | replan_trend | 0.865 | 0.078 | 0.152 | 0.074 | -- | -- | -- |
| classification | nodrift | 1 | uniform | 0.865 | 0.078 | 0.152 | 0.074 | -- | -- | -- |
| classification | nodrift | 3 | oracle | 1.057 | 0.134 | 0.169 | 0.169 | 0.000 | 0.000 | 0.000 |
| classification | nodrift | 3 | replan_blend | 1.185 | 0.225 | 0.143 | 0.151 | 1.292 | 1.709 | 0.221 |
| classification | nodrift | 3 | replan_ewma | 1.085 | 0.124 | 0.137 | 0.154 | 1.012 | 1.254 | 0.172 |
| classification | nodrift | 3 | replan_last | 1.082 | 0.090 | 0.133 | 0.152 | 1.159 | 1.520 | 0.197 |
| classification | nodrift | 3 | replan_mean | 1.065 | 0.063 | 0.139 | 0.152 | 1.000 | 1.231 | 0.168 |
| classification | nodrift | 3 | replan_trend | 1.310 | 0.371 | 0.139 | 0.160 | 1.730 | 2.411 | 0.312 |
| classification | nodrift | 3 | uniform | 1.057 | 0.054 | 0.131 | 0.146 | -- | -- | -- |
| classification | nodrift | 5 | oracle | 2.362 | 0.745 | 0.196 | 0.205 | 0.000 | 0.000 | 0.000 |
| classification | nodrift | 5 | replan_blend | 1.753 | 0.535 | 0.131 | 0.192 | 1.292 | 1.709 | 0.221 |
| classification | nodrift | 5 | replan_ewma | 1.625 | 0.408 | 0.142 | 0.193 | 1.012 | 1.254 | 0.172 |
| classification | nodrift | 5 | replan_last | 1.170 | 0.116 | 0.131 | 0.192 | 1.159 | 1.520 | 0.197 |
| classification | nodrift | 5 | replan_mean | 1.653 | 0.385 | 0.142 | 0.193 | 1.000 | 1.231 | 0.168 |
| classification | nodrift | 5 | replan_trend | 2.520 | 1.138 | 0.090 | 0.151 | 1.730 | 2.411 | 0.312 |
| classification | nodrift | 5 | uniform | 1.170 | 0.113 | 0.142 | 0.193 | -- | -- | -- |
| classification | nodrift | 7 | oracle | 4.018 | 0.683 | 0.226 | 0.290 | 0.000 | 0.000 | 0.000 |
| classification | nodrift | 7 | replan_blend | 3.108 | 0.862 | 0.167 | 0.266 | 1.292 | 1.709 | 0.221 |
| classification | nodrift | 7 | replan_ewma | 2.680 | 0.702 | 0.181 | 0.256 | 1.012 | 1.254 | 0.172 |
| classification | nodrift | 7 | replan_last | 1.732 | 0.375 | 0.126 | 0.227 | 1.159 | 1.520 | 0.197 |
| classification | nodrift | 7 | replan_mean | 2.730 | 0.791 | 0.186 | 0.264 | 1.000 | 1.231 | 0.168 |
| classification | nodrift | 7 | replan_trend | 3.958 | 1.352 | 0.064 | 0.165 | 1.730 | 2.411 | 0.312 |
| classification | nodrift | 7 | uniform | 1.277 | 0.175 | 0.138 | 0.237 | -- | -- | -- |
| classification | nodrift | 9 | oracle | 4.832 | 0.596 | 0.289 | 0.366 | 0.000 | 0.000 | 0.000 |
| classification | nodrift | 9 | replan_blend | 5.102 | 0.809 | 0.217 | 0.321 | 1.292 | 1.709 | 0.221 |
| classification | nodrift | 9 | replan_ewma | 5.040 | 0.925 | 0.222 | 0.318 | 1.012 | 1.254 | 0.172 |
| classification | nodrift | 9 | replan_last | 4.592 | 2.226 | 0.139 | 0.284 | 1.159 | 1.520 | 0.197 |
| classification | nodrift | 9 | replan_mean | 5.112 | 0.906 | 0.256 | 0.345 | 1.000 | 1.231 | 0.168 |
| classification | nodrift | 9 | replan_trend | 6.188 | 0.828 | 0.128 | 0.271 | 1.730 | 2.411 | 0.312 |
| classification | nodrift | 9 | uniform | 1.385 | 0.244 | 0.153 | 0.288 | -- | -- | -- |
| regression | drift | 1 | replan_blend | 190.787 | 3.367 | 0.168 | 0.062 | -- | -- | -- |
| regression | drift | 1 | replan_ewma | 190.787 | 3.367 | 0.168 | 0.062 | -- | -- | -- |
| regression | drift | 1 | replan_last | 190.787 | 3.367 | 0.168 | 0.062 | -- | -- | -- |
| regression | drift | 1 | replan_mean | 190.787 | 3.367 | 0.168 | 0.062 | -- | -- | -- |
| regression | drift | 1 | replan_trend | 190.787 | 3.367 | 0.168 | 0.062 | -- | -- | -- |
| regression | drift | 1 | uniform | 190.787 | 3.367 | 0.168 | 0.062 | -- | -- | -- |
| regression | drift | 3 | oracle | 324.537 | 9.013 | 0.124 | 0.140 | 0.000 | 0.000 | 0.000 |
| regression | drift | 3 | replan_blend | 330.139 | 10.313 | 0.117 | 0.139 | 36.569 | 58.841 | 8.830 |
| regression | drift | 3 | replan_ewma | 327.703 | 9.897 | 0.113 | 0.139 | 30.064 | 40.058 | 5.806 |
| regression | drift | 3 | replan_last | 331.376 | 10.938 | 0.106 | 0.141 | 31.121 | 42.441 | 7.066 |
| regression | drift | 3 | replan_mean | 327.535 | 10.004 | 0.115 | 0.138 | 33.579 | 42.807 | 5.672 |
| regression | drift | 3 | replan_trend | 337.328 | 13.801 | 0.115 | 0.152 | 66.644 | 118.091 | 14.946 |
| regression | drift | 3 | uniform | 320.575 | 8.741 | 0.154 | 0.143 | -- | -- | -- |
| regression | drift | 5 | oracle | 413.263 | 12.790 | 0.077 | 0.173 | 0.000 | 0.000 | 0.000 |
| regression | drift | 5 | replan_blend | 421.966 | 13.269 | 0.110 | 0.196 | 36.569 | 58.841 | 8.830 |
| regression | drift | 5 | replan_ewma | 417.450 | 13.856 | 0.104 | 0.192 | 30.064 | 40.058 | 5.806 |
| regression | drift | 5 | replan_last | 422.952 | 13.806 | 0.104 | 0.186 | 31.121 | 42.441 | 7.066 |
| regression | drift | 5 | replan_mean | 417.346 | 11.641 | 0.104 | 0.192 | 33.579 | 42.807 | 5.672 |
| regression | drift | 5 | replan_trend | 439.458 | 18.490 | 0.144 | 0.213 | 66.644 | 118.091 | 14.946 |
| regression | drift | 5 | uniform | 424.250 | 12.083 | 0.094 | 0.183 | -- | -- | -- |
| regression | drift | 7 | oracle | 467.860 | 15.911 | 0.079 | 0.210 | 0.000 | 0.000 | 0.000 |
| regression | drift | 7 | replan_blend | 472.475 | 13.478 | 0.098 | 0.216 | 36.569 | 58.841 | 8.830 |
| regression | drift | 7 | replan_ewma | 468.297 | 14.258 | 0.098 | 0.188 | 30.064 | 40.058 | 5.806 |
| regression | drift | 7 | replan_last | 472.605 | 11.939 | 0.093 | 0.215 | 31.121 | 42.441 | 7.066 |
| regression | drift | 7 | replan_mean | 466.428 | 14.467 | 0.093 | 0.215 | 33.579 | 42.807 | 5.672 |
| regression | drift | 7 | replan_trend | 496.036 | 27.169 | 0.093 | 0.212 | 66.644 | 118.091 | 14.946 |
| regression | drift | 7 | uniform | 463.015 | 12.783 | 0.090 | 0.215 | -- | -- | -- |
| regression | drift | 9 | oracle | 502.071 | 16.013 | 0.061 | 0.187 | 0.000 | 0.000 | 0.000 |
| regression | drift | 9 | replan_blend | 505.341 | 19.956 | 0.111 | 0.233 | 36.569 | 58.841 | 8.830 |
| regression | drift | 9 | replan_ewma | 501.846 | 16.878 | 0.067 | 0.187 | 30.064 | 40.058 | 5.806 |
| regression | drift | 9 | replan_last | 501.439 | 15.029 | 0.106 | 0.232 | 31.121 | 42.441 | 7.066 |
| regression | drift | 9 | replan_mean | 501.218 | 14.782 | 0.067 | 0.187 | 33.579 | 42.807 | 5.672 |
| regression | drift | 9 | replan_trend | 528.318 | 31.713 | 0.128 | 0.231 | 66.644 | 118.091 | 14.946 |
| regression | drift | 9 | uniform | 509.528 | 14.738 | 0.089 | 0.238 | -- | -- | -- |
| regression | nodrift | 1 | replan_blend | 134.542 | 2.099 | 0.178 | 0.089 | -- | -- | -- |
| regression | nodrift | 1 | replan_ewma | 134.542 | 2.099 | 0.178 | 0.089 | -- | -- | -- |
| regression | nodrift | 1 | replan_last | 134.542 | 2.099 | 0.178 | 0.089 | -- | -- | -- |
| regression | nodrift | 1 | replan_mean | 134.542 | 2.099 | 0.178 | 0.089 | -- | -- | -- |
| regression | nodrift | 1 | replan_trend | 134.542 | 2.099 | 0.178 | 0.089 | -- | -- | -- |
| regression | nodrift | 1 | uniform | 134.542 | 2.099 | 0.178 | 0.089 | -- | -- | -- |
| regression | nodrift | 3 | oracle | 236.318 | 6.520 | 0.156 | 0.148 | 0.000 | 0.000 | 0.000 |
| regression | nodrift | 3 | replan_blend | 240.557 | 7.504 | 0.159 | 0.160 | 26.520 | 47.843 | 7.872 |
| regression | nodrift | 3 | replan_ewma | 239.082 | 7.266 | 0.161 | 0.155 | 15.319 | 24.914 | 5.322 |
| regression | nodrift | 3 | replan_last | 240.172 | 7.533 | 0.163 | 0.157 | 18.937 | 30.553 | 6.377 |
| regression | nodrift | 3 | replan_mean | 239.004 | 7.112 | 0.161 | 0.155 | 15.107 | 24.512 | 5.244 |
| regression | nodrift | 3 | replan_trend | 246.738 | 11.654 | 0.157 | 0.170 | 50.430 | 92.479 | 12.669 |
| regression | nodrift | 3 | uniform | 233.324 | 6.521 | 0.161 | 0.155 | -- | -- | -- |
| regression | nodrift | 5 | oracle | 303.329 | 10.799 | 0.144 | 0.172 | 0.000 | 0.000 | 0.000 |
| regression | nodrift | 5 | replan_blend | 311.375 | 11.001 | 0.110 | 0.173 | 26.520 | 47.843 | 7.872 |
| regression | nodrift | 5 | replan_ewma | 308.282 | 9.224 | 0.106 | 0.172 | 15.319 | 24.914 | 5.322 |
| regression | nodrift | 5 | replan_last | 313.265 | 9.105 | 0.123 | 0.175 | 18.937 | 30.553 | 6.377 |
| regression | nodrift | 5 | replan_mean | 308.559 | 9.775 | 0.115 | 0.188 | 15.107 | 24.512 | 5.244 |
| regression | nodrift | 5 | replan_trend | 330.982 | 19.464 | 0.133 | 0.185 | 50.430 | 92.479 | 12.669 |
| regression | nodrift | 5 | uniform | 311.288 | 9.517 | 0.115 | 0.173 | -- | -- | -- |
| regression | nodrift | 7 | oracle | 350.759 | 13.805 | 0.093 | 0.187 | 0.000 | 0.000 | 0.000 |
| regression | nodrift | 7 | replan_blend | 360.219 | 15.548 | 0.093 | 0.187 | 26.520 | 47.843 | 7.872 |
| regression | nodrift | 7 | replan_ewma | 354.851 | 17.847 | 0.107 | 0.201 | 15.319 | 24.914 | 5.322 |
| regression | nodrift | 7 | replan_last | 359.851 | 14.966 | 0.119 | 0.201 | 18.937 | 30.553 | 6.377 |
| regression | nodrift | 7 | replan_mean | 353.415 | 16.644 | 0.117 | 0.202 | 15.107 | 24.512 | 5.244 |
| regression | nodrift | 7 | replan_trend | 390.035 | 32.013 | 0.098 | 0.178 | 50.430 | 92.479 | 12.669 |
| regression | nodrift | 7 | uniform | 343.881 | 11.208 | 0.100 | 0.190 | -- | -- | -- |
| regression | nodrift | 9 | oracle | 387.305 | 15.628 | 0.067 | 0.197 | 0.000 | 0.000 | 0.000 |
| regression | nodrift | 9 | replan_blend | 399.750 | 22.174 | 0.114 | 0.248 | 26.520 | 47.843 | 7.872 |
| regression | nodrift | 9 | replan_ewma | 390.649 | 20.648 | 0.111 | 0.249 | 15.319 | 24.914 | 5.322 |
| regression | nodrift | 9 | replan_last | 392.210 | 16.471 | 0.083 | 0.203 | 18.937 | 30.553 | 6.377 |
| regression | nodrift | 9 | replan_mean | 389.697 | 20.393 | 0.086 | 0.218 | 15.107 | 24.512 | 5.244 |
| regression | nodrift | 9 | replan_trend | 436.798 | 33.758 | 0.056 | 0.139 | 50.430 | 92.479 | 12.669 |
| regression | nodrift | 9 | uniform | 395.195 | 16.214 | 0.097 | 0.222 | -- | -- | -- |

## Paper Reproduction Notes

- The rerun reproduces the paper's main mask-valid axes and drift protocols, but it is not an exact submitted-table clone: this compact run uses the rewritten flat package, a 21-point log-budget grid, and 30 Monte Carlo runs.
- The submitted paper table used 100 runs and included the archived anytime/e-process baseline. The current rewritten runner focuses on mask-valid uniform spending and closed-loop replanning; the anytime baseline remains in the archived supplementary package.
- Because the current repo intentionally separates the cleaned rebuttal runner from the archived full package, paper-table numerical equality should not be expected until the archived runner and rewritten runner are reconciled.

## Main Takeaways

- Some empirical `W` estimates exceed `alpha=0.15` in the 30-run sweep; the largest deployable value is `0.256` for `classification/nodrift/K=9/replan_mean`. Treat these as finite-run estimates, not proof of invalidity.
- Best observed deployable `classification` efficiency is `uniform` under `nodrift`, `K=1`, with `S=0.865` and `W=0.152`.
- Best observed deployable `regression` efficiency is `uniform` under `nodrift`, `K=1`, with `S=134.542` and `W=0.178`.
- Across task/condition/mask settings, the best replan method beats uniform spending in `7` settings and uniform is at least as efficient in `13` settings.

## Artifacts

- Machine summary: `.workspace/experiments/rebuttal_expanded_g21/summary.json`
- Per-run JSONL: `.workspace/experiments/rebuttal_expanded_g21/per_run.jsonl`
- This report intentionally reports aggregate metrics and does not include raw CIFAR or California Housing data.
