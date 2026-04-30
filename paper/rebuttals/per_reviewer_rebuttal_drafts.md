# Per-Reviewer Rebuttal Drafts

Use `[link]` as the anonymous supplement URL placeholder. The local figure/table pointers are for us, not necessarily for OpenReview.

## Reviewer Me2Q

We thank the reviewer for the careful reading. We agree that the motivation should be more concrete. The problem came from a batch-production monitoring setting: items arrive in batches within production runs, and the monitoring question is not only "did anything ever fail over all time?" but also "did any failure occur within this run, this rolling audit period, or all runs associated with a particular supplier?" These are ex ante monitoring contracts. Here the operational decision is local: whether to halt or audit a run, supplier, or maintenance period. Full-trajectory anytime control is valid but mismatched to that decision because it spends budget on time points the operator is not jointly evaluating.

We also agree that alpha-spending is a central ingredient. Our contribution is to identify the batch-sequential structure under which true-label conformal p-values are independent conditional on the past, and then develop the consequences for mask validity, restricted closed-loop implementability, restart validity, and replanning error. In the log-budget parameterization \(s_t=-\log(1-\tau_t)\), a mask family imposes simultaneous constraints
\[
\sum_t M_t s_t \le -\log(1-\alpha),\qquad M\in\mathcal M.
\]
Thus singleton masks and the all-ones mask recover marginal and anytime endpoints, while production runs, rolling windows, supplier groups, and maintenance periods produce different feasible schedules. These masks are fixed before deployment because they define the monitoring contract; the schedule is optimized only after that guarantee family is declared. The novelty is therefore not that alpha-spending exists, but that this batch-sequential conformal structure turns a practical monitoring contract into a valid and implementable simultaneous guarantee.

The supplement [link] adds protocol-mask experiments. Dense symmetric windows behave almost like uniform spending, as expected. In contrast, sparse ex ante contracts show large efficiency gains: maintenance-cadence and scheduled-high-risk masks reduce the reported size metric by about 64-76% with empirical mean mask-failure estimates near alpha in these runs. This is the intended positive claim: replanning helps when the monitoring contract contains exploitable structure; it is not advertised as uniformly better.

In revision we will strengthen the industrial monitoring motivation, add concrete mask examples and an illustration, clarify that mask choice is the target guarantee rather than a post hoc hyperparameter, and fix the Proposition 2.7 typo. We will also replace or qualify "admissible" where "feasible" is clearer.

**Useful attachment pointers:** `figures/protocol_mask_schematic_clean.png`, `figures/protocol_efficiency.png`, `tables/protocol_masks_ci.md`.

## Reviewer tMt5

We thank the reviewer for the constructive comments. We agree that the paper is dense, and we will add an illustration of restart validity and restricted closed-loop monitoring. The motivating example will be made explicit: a deployed production system produces batches; small labeled calibration samples may be available at each batch, while operational test labels are delayed or unavailable; the relevant guarantee may concern a production run, rolling audit, supplier subset, or scheduled high-risk period.

Our assumption is only that, at time \(t\), the labeled calibration sample used to form \(p_t\) is exchangeable with the current test point conditional on the observed history. This is inherited from split/anytime conformal analyses and is what gives conditionally independent conformal p-values. The operational asymmetry is that a small inspected or historically labeled calibration sample may be available at batch \(t\), while labels for the deployed test stream are delayed or unavailable when thresholds must be chosen. It does not assert stationarity: drift can enter through the history and changing batch distribution. We will connect this more clearly to covariate-shift and adaptive/non-exchangeable conformal work in revision.

The supplement [link] adds protocol-mask experiments that make the operational protocol concrete. They instantiate shift blocks, rolling audits, scheduled high-risk windows, and maintenance cadences. They give a useful sanity check: dense rolling/shift masks are close to uniform spending, whereas sparse scheduled contracts reduce size by about 64-76% with empirical mean mask-failure estimates near alpha in these runs. This supports a positive but precise claim: replanning is useful when the declared monitoring protocol has structure to exploit.

For Section 4, we will clarify that the cost is a proxy for expected set size or interval width estimated from calibration scores. Optimization quality affects efficiency, not validity, because each candidate schedule must satisfy the log-budget constraints. If accepted, we will use the extra page to add a conclusion/discussion rather than moving more assumptions to the appendix.

**Useful attachment pointers:** `figures/protocol_mask_schematic_clean.png`, `figures/protocol_efficiency.png`, `tables/protocol_masks_ci.md`, `figures/gaussian_exact_validity.png` for the validity point.

## Reviewer XdVF

We thank the reviewer for the helpful questions. The current experiments are controlled batch-sequential stress tests: each time step is treated as a batch with its own calibration/test split, and the procedure may use past calibration data and unlabeled covariates but not realized test labels. We agree that the paper should make this more explicit and should separate completed evidence from possible future additions. In revision, we will foreground the existing protocol-mask and core-frontier results with the same mask-valid metrics. A naturally ordered sequential dataset remains a possible revision addition, not part of the completed supplement.

The quantity \(W\) also needs clearer presentation. The formal guarantee is for each declared mask:
\[
\mathbb P(\text{at least one monitored error on }M)\le \alpha.
\]
For threshold policies, conditional exchangeability gives independent true-label p-values. Therefore, with \(\tau_t=1-\exp(-s_t)\),
\[
\mathbb P(F(M))=1-\prod_{t:M_t=1}(1-\tau_t)
=1-\exp\!\left(-\sum_t M_t s_t\right)\le \alpha.
\]
We agree the presentation was ambiguous: the reported table summarized empirical mean mask failure over repeated windows and runs, not the theoretical max-over-mask quantity in the guarantee. Finite-sample estimates of that mean can sit slightly above \(\alpha\), which is why we now separate the exact guarantee from the Monte Carlo summary. In response, we added an exact Gaussian check in the supplement [link]: exact max \(W\) is \(0.15\), and Monte Carlo estimates concentrate around \(0.15\) across masks and schedules. We will revise the metric definition and report Monte Carlo intervals; where possible, we will also add max-over-window summaries.

The lower-bound question is a good one. The usual finite-sample p-value grid effect carries over directly to our setting; we will add this as a short remark, since it is a discretization issue rather than a new phenomenon.

**Useful attachment pointers:** `figures/gaussian_exact_validity.png`, `tables/gaussian_exact_validity.md`, `figures/core_frontier_validity.png` only with the mean-\(W\) caveat.

## Reviewer D6dM

We thank the reviewer for the careful reading. The guarantees do not require fixed batch sizes. We used a constant calibration size \(n\) mainly for notation and experiments. With variable \(n_t\), the conformal p-value at time \(t\) lies on the grid \(\{1/(n_t+1),\ldots,1\}\) and remains conditionally sub-uniform under within-batch exchangeability. If \(n_t\) is fixed in advance or observable before choosing \(\tau_t\), the same log-budget proof applies using the actual per-batch grids. Smaller batches can reduce efficiency through coarser p-values, but they do not invalidate mask validity or restart validity.

The method is also agnostic to the score function in the usual split-conformal sense. Any score \(S_t(x,y)\) that is pre-specified or chosen using only past-observable information gives valid conformal p-values under the same within-batch exchangeability assumption. Different scores can produce different sets and efficiencies; the mask-valid guarantee controls the events \(\{p_t(X_t,Y_t)\le \tau_t\}\), not a particular score choice.

The values \(K=\{1,3,5,7,9\}\) were chosen for \(T=20\) to give a compact interpolation between singleton masks and the all-ones trajectory mask. In the supplement [link], the core frontier provides the negative control: dense, symmetric windows produce modest or sometimes no gains. The protocol masks provide the positive case: sparse ex ante contracts such as maintenance cadence and scheduled high-risk periods reduce the reported size metric by about 64-76%, with empirical mean mask-failure estimates around \(0.10\)–\(0.11\) at \(\alpha=0.15\) in these runs. We will report these existing results in the appendix and add a conclusion/limitations paragraph.

**Useful attachment pointers:** `figures/protocol_mask_schematic_clean.png`, `figures/protocol_efficiency.png`, `tables/protocol_masks_ci.md`, `tables/core_frontier.md`.

## Reviewer wJbH

We thank the reviewer for the detailed assessment. We agree that the paper should narrow its positioning. Our result is not a general online/adaptive CP theorem; it is for batch-sequential p-value threshold policies under conditional within-batch exchangeability. The one-test-point notation is for exposition. Multiple test points per batch can be handled by applying the method to valid batch-level p-values or to separately defined within-batch units, but the required super-uniformity/independence must be stated; we will make this explicit rather than imply it is automatic.

We will also soften the e-process comparison. E-process methods target a stronger anytime guarantee and are the right tool when that is the scientific objective. Our point is that this stronger target can be inefficient when the operational goal is a declared family of windows, and batch-sequential conformal p-values provide additional structure: independence, no dependence on past test labels, and restart validity. Once the target is a declared mask family rather than the full trajectory, conditional p-value independence turns the design problem into a simultaneous log-budget allocation with restart-valid and label-free implementability constraints; that package is the contribution. Our comparison is therefore a tradeoff statement, not a superiority claim. The Gamma model includes common squared-error cases, e.g. Gaussian errors imply chi-square/Gamma squared residuals, but we will state the scope carefully.

The supplement [link] directly answers the simple-baseline concern. Core frontier tables compare uniform spending with replanning on standard window families, where gains are modest or absent; this is an important negative control. In the protocol-mask table, uniform spending is also the comparator in every row. Those experiments instantiate production-style contracts: shift blocks, rolling audits, scheduled high-risk periods, and maintenance cadences. Dense rolling/shift masks remain close to uniform, while sparse scheduled contracts reduce size by about 64-76%, with empirical mean mask-failure estimates around \(0.10\)–\(0.11\) at \(\alpha=0.15\) in these runs. Thus the empirical claim is not that replanning always wins; it wins when the declared monitoring protocol has exploitable structure.

We will make the optimization concrete: \(c_t(\tau)\) is expected set size or interval width estimated from calibration scores. Forecast error affects efficiency, not validity, because every replan must satisfy the same mask log-budget constraints. We will add simpler baseline tables, a concrete K-window constraint example, uncertainty reporting, code availability, and a conclusion/limitations paragraph.

**Useful attachment pointers:** `figures/protocol_mask_schematic_clean.png`, `figures/protocol_efficiency.png`, `tables/protocol_masks_ci.md`, `tables/core_frontier.md`, `figures/gaussian_exact_validity.png` for \(W\).
