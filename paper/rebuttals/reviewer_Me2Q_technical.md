We thank the reviewer for the careful reading. We agree that alpha-spending is one ingredient, but the paper is not simply choosing a default spending schedule for one union event. The object being controlled is a declared family of masks. A single threshold sequence must satisfy all masks simultaneously: with \(s_t=-\log(1-\tau_t)\) and \(L=-\log(1-\alpha)\), mask validity becomes
\[
\sum_t M_t s_t\le L,\qquad \forall M\in\mathcal M.
\]
Thus rolling windows, shifts, and audit periods induce a mask-incidence constrained allocation problem. Marginal and anytime validity appear as endpoints of this formulation, not as the only two choices.

Two further pieces are essential. First, the policy is restricted closed-loop: thresholds may use calibration data and unlabeled test covariates, but not realized test labels. Replanning changes only the efficiency objective and always enforces the remaining mask budgets, so forecast error affects set size, not validity. Second, restart validity is a suffix guarantee: after a monitored miss, the future monitored process is again valid at level \(\alpha\). This rules out methods that are valid only up to the first failure and then become silent or vacuous.

We also agree that the draft makes masks look too much like a tuning hyperparameter. The intended interpretation is ex ante: the mask family is the monitoring contract. Examples include a regulator auditing every rolling 30-day window, an operations team monitoring production shifts or holiday windows, and scheduled high-risk periods after model updates or maintenance. Efficiency depends on the mask family because stronger monitoring contracts consume more budget; validity is for the declared family, not for post hoc selection of the most efficient \(K\).

We will revise the manuscript to make this explicit: add operational mask examples, state that mask choice specifies the target guarantee, and sharpen the novelty discussion around simultaneous mask constraints, restricted closed-loop implementability, restart validity, and cost-aware replanning. We will also fix the Prop. 2.7 typo and replace or qualify "admissible" where "feasible" is clearer.
