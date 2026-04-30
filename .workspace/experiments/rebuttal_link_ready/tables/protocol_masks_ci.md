| condition | mask | kind | support | uniform S | best replan | replan S | delta S | uniform W | replan W |
|---|---|---|---:|---:|---|---:|---:|---:|---:|
| nodrift | maintenance_every5 | cadence | 4 | 673.9 +/- 0.8 | replan_last | 162.5 +/- 1.0 | -75.9% | 0.130 +/- 0.066 | 0.100 +/- 0.059 |
| nodrift | rolling_audit_4 | sliding_window | 4 | 266.9 +/- 1.5 | replan_mean | 271.6 +/- 1.8 | 1.8% | 0.141 +/- 0.030 | 0.143 +/- 0.031 |
| nodrift | scheduled_high_risk_last5 | suffix | 5 | 659.7 +/- 1.0 | replan_mean | 177.3 +/- 1.3 | -73.1% | 0.120 +/- 0.064 | 0.140 +/- 0.068 |
| nodrift | shift_blocks_5x4 | block_partition | 4 | 266.9 +/- 1.5 | replan_mean | 271.1 +/- 1.7 | 1.6% | 0.138 +/- 0.028 | 0.150 +/- 0.030 |
| drift | maintenance_every5 | cadence | 4 | 696.7 +/- 1.2 | replan_ewma | 227.7 +/- 1.3 | -67.3% | 0.090 +/- 0.056 | 0.100 +/- 0.059 |
| drift | rolling_audit_4 | sliding_window | 4 | 364.9 +/- 2.2 | replan_mean | 371.0 +/- 2.7 | 1.7% | 0.126 +/- 0.034 | 0.122 +/- 0.033 |
| drift | scheduled_high_risk_last5 | suffix | 5 | 696.4 +/- 1.4 | replan_blend | 248.5 +/- 1.6 | -64.3% | 0.110 +/- 0.062 | 0.110 +/- 0.062 |
| drift | shift_blocks_5x4 | block_partition | 4 | 364.9 +/- 2.2 | replan_blend | 370.5 +/- 2.5 | 1.5% | 0.120 +/- 0.031 | 0.126 +/- 0.031 |
