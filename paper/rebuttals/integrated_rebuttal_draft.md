# Integrated Rebuttal Draft

## OpenReview Draft

We thank the reviewers for the constructive feedback. We agree that the manuscript should better separate the target guarantee, the information model, and the empirical scope.

First, the method is alpha-spending, but not only a default schedule for one union event. Under conditional within-batch exchangeability, the true-label conformal p-values are independent across batches. Writing \(s_t=-\log(1-\tau_t)\) and \(L=-\log(1-\alpha)\), mask validity is exactly the simultaneous constraint
\[
\sum_t M_t s_t \le L,\qquad \forall M\in\mathcal M .
\]
Singleton masks and the all-ones mask recover marginal and anytime endpoints; rolling windows, production shifts, scheduled high-risk periods, and maintenance cadences give different ex ante monitoring contracts. Replanning chooses among schedules satisfying these constraints. Forecast error affects efficiency, not validity. Restart validity is also separate: after a monitored error, the remaining procedure must again control the next monitored error, and our restricted closed-loop policies do this without using past test labels.

Second, we added targeted experiments in an anonymous supplement [link]. An exact Gaussian check isolates the alpha-spending issue: with \(\tau_t=1-\exp(-s_t)\), every schedule using the same log budget has exact all-ones failure probability \(1-\exp(-\sum_t s_t)=\alpha\); Monte Carlo estimates stay at \(0.15\). A forecasting diagnostic shows the intended positive claim: replanning helps when future difficulty is forecastable. Uniform spending is optimal in the flat setting and remains best when a high-variance final block has no past signal, while sigma-based replanning improves mean width by about \(1.9\%\) on a linear ramp and \(12.3\%\) on a single-spike profile. Protocol-mask experiments further show that masks can encode concrete audit contracts rather than post hoc hyperparameters.

Finally, we will revise the paper to make the scope explicit: the main theorem is for batch-sequential p-value threshold policies, not arbitrary online CP. We will clarify the distinction between labeled calibration data and unavailable test labels, state that variable batch sizes and different conformal scores are allowed when chosen from past-observable information, add the p-value grid lower-bound remark, include related work on shift/non-exchangeability, soften the e-process comparison as a tradeoff against stronger anytime guarantees, and add a conclusion, code note, and typo fixes.

## Figure And Table Links

- [Attachment guide](../../.workspace/experiments/rebuttal_link_ready/ATTACHMENT_GUIDE.md)
- [Hero summary figure](../../.workspace/experiments/rebuttal_link_ready/figures/rebuttal_hero_summary.png)
- [Exact Gaussian validity figure](../../.workspace/experiments/rebuttal_link_ready/figures/gaussian_exact_validity.png)
- [Synthetic forecasting table](../../.workspace/experiments/rebuttal_link_ready/tables/synthetic_diagnostics_ci.md)
- [Synthetic allocation figure](../../.workspace/experiments/rebuttal_link_ready/figures/synthetic_profiles_allocations.png)
- [Clean mask schematic](../../.workspace/experiments/rebuttal_link_ready/figures/protocol_mask_schematic_clean.png)
- [Protocol-mask table](../../.workspace/experiments/rebuttal_link_ready/tables/protocol_masks_ci.md)
- [Core regression frontier](../../.workspace/experiments/rebuttal_link_ready/figures/core_frontier_efficiency_regression.png)

## Expanded Working Version

We thank all reviewers for the careful and constructive feedback. The central lesson for us is that the paper needs to make three distinctions more visible: what guarantee is being targeted, what information the procedure may use, and what empirical claim the experiments support.

On novelty and motivation, we agree that the construction has an alpha-spending core. The additional structure is that the spending schedule must satisfy a whole declared family of masks simultaneously. In the log-budget parameterization \(s_t=-\log(1-\tau_t)\), every mask \(M\) imposes a linear budget constraint \(\sum_t M_t s_t\le -\log(1-\alpha)\). This makes marginal CP and anytime CP two endpoints of a larger design space: singleton masks give per-batch control, the all-ones mask gives full-trajectory control, and intermediate families represent rolling audit windows, production shifts, supplier-specific runs, maintenance cadences, or scheduled high-risk periods. We will revise the introduction and Section 4 to present masks as ex ante monitoring contracts, not tuning knobs.

The information model also deserves a clearer explanation. At batch \(t\), calibration labels are available for \(\mathcal S^t\), while operational test labels are the outcomes to be covered and may be delayed or unavailable. The assumption is local: conditional on the past, the calibration sample and current test point are exchangeable within the batch. Cross-batch drift is allowed through the filtration. Thresholds may use past calibration data and unlabeled covariates, but not realized test labels. This is the restricted closed-loop setting; restart validity then asks that after a monitored failure, the suffix procedure again controls future monitored failures.

We added experiments to answer the empirical concerns without overclaiming. The exact Gaussian check shows that the validity calculation is literal: if all methods use the same log budget, the all-ones failure probability is \(1-\exp(-\sum_t s_t)=\alpha\), and Monte Carlo estimates stay at \(\alpha=0.15\). The forecasting diagnostic is deliberately honest: replanning does not improve in flat settings or when a hard final block has no earlier signal; it improves when future difficulty is forecastable, with about \(1.9\%\) lower width on a linear ramp and \(12.3\%\) lower width on a single-spike profile. The protocol-mask experiments then show concrete mask choices and their efficiency tradeoffs.

For the revision, we will also clarify that variable batch sizes only change the p-value grid and efficiency, not the proof; that the method is score-agnostic in the usual split-conformal sense as long as the score is fixed from past-observable information; and that the lower-bound analogue follows by replacing \(\tau_t\) with the grid probability \(q_t=\lfloor(n_t+1)\tau_t\rfloor/(n_t+1)\). We will add related work on covariate shift, non-exchangeability, and adaptive conformal inference, and soften the e-process discussion. E-process methods target stronger anytime guarantees; our comparison should be read as a guarantee-specific tradeoff, not a universal superiority claim. We will add a conclusion/limitations paragraph, code availability statement, clearer uncertainty reporting, and the requested typo/terminology fixes.
