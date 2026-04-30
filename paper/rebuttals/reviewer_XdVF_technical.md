We thank the reviewer. The key distinction is between the theorem and the finite simulation summary. The theorem controls
\[
\sup_{M\in\mathcal M}\mathbb P(F_T(M,\mathcal A))\le\alpha,
\]
where \(F_T\) is the event of at least one monitored error. For threshold policies, conditional within-batch exchangeability makes the true-label conformal \(p\)-values independent and grid-uniform, so \(\mathbb P(F_T(M))\le 1-\prod_{t\in S(M)}(1-\tau_t)\le\alpha\). This is a repeated-sampling guarantee for each fixed mask, not a deterministic bound on one simulation table.

On datasets, we agree the manuscript should distinguish statistical setting from application realism. The benchmarks are controlled batch-sequential stress tests: each batch has its own calibration/test split, thresholds may use past calibration data and unlabeled features but not past test labels, and drift changes across batches while preserving within-batch exchangeability. We will revise the text and add concrete ex ante mask examples, such as rolling audit windows, production shifts, and flagged subsets.

The W column should have been clearer. The formal quantity is the worst-mask probability above. Table 1 reports W as an empirical average over starting windows and runs to summarize many masks compactly. Since each summand has expectation at most \(\alpha\), the population average is also at most \(\alpha\), but the finite Monte Carlo estimate need not be. We will rewrite the metric definition and add max-over-window estimates or Monte Carlo intervals from the same outputs.

The entries above \(\alpha\) have the same explanation. With 100 runs and overlapping windows, values such as 0.17 or 0.20 at \(\alpha=0.15\) are consistent with Monte Carlo noise. They should not be read as violations of mask validity, whose probability statement is over repeated draws under the stated assumptions.

A lower-bound analogue is possible but must reflect discreteness. Under unique scores, \(p_t\) is uniform on \(\{1/(n+1),\ldots,1\}\). For \(q_t=\mathbb P(p_t\le\tau_t)=\lfloor(n+1)\tau_t\rfloor/(n+1)\), any fixed mask satisfies \(\mathbb P(F_T(M))=1-\prod_{t\in S(M)}(1-q_t)\). Thus a tight schedule attains the nominal failure probability up to grid error of order \(|S(M)|/(n+1)\). Exact equality is not universal because ties, off-grid thresholds, and simultaneous mask constraints can introduce slack. We will add this as a proposition/remark.
