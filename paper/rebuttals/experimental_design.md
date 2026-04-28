# Rebuttal-Period Experimental Design

This document authorizes at most three rebuttal-period experiments. The goal is not to expand the empirical section broadly, but to produce a small amount of targeted evidence for the author response: one compact figure, one compact table, and clear language separating empirical claims from camera-ready promises.

## Reviewer Priority

Inputs read: `uai_reviews.md`, `paper/main.tex`, and drafts `paper/rebuttals/reviewer_1.md` through `paper/rebuttals/reviewer_5.md`.

Only one scored review is available locally: Reviewer Me2Q, rating 6 (Weak Accept), confidence 4. The local reviewer drafts do not expose additional scores, so this plan treats the repeated draft concerns as broad reviewer-risk signals and prioritizes concerns that appear across drafts:

- **Alpha-spending novelty concern:** Me2Q weakness 1; drafts for Reviewers 1--5.
- **Mask-choice motivation concern:** Me2Q weaknesses 2 and 4; drafts for Reviewers 1--5.
- **Efficiency sensitivity concern:** Me2Q weakness 3; drafts for Reviewers 1--5.
- **Restart/after-failure concern:** Me2Q concrete-example request; drafts for Reviewers 1--5.

If lower-rating reviewer metadata exists outside these local files, do not add new experiments. Map that reviewer to the concern list above and use the same three experiments, since they cover every repeated objection in the available rebuttal drafts.

## Rebuttal Experiments

### E1. Mask-Family Frontier and Equal-Spending Baseline

**Decision:** run first.

**Reviewer concerns answered.** Me2Q alpha-spending novelty and efficiency-sensitivity concerns; Reviewer 1--5 draft requests to distinguish the method from ordinary alpha-spending and quantify sensitivity over window size.

**Why high span/delta.** This single experiment addresses the central skeptical reading of the paper: "this is just alpha-spending with a mask hyperparameter." It turns the objection into an operating frontier: the all-ones case reduces to ordinary spending, while nontrivial mask families impose simultaneous constraints, and efficiency changes with the requested monitoring contract.

**Run.**

- Use the submitted setup: California Housing and CIFAR-10 if cached summaries/logits are available; otherwise complete California Housing first and use existing submitted CIFAR numbers only as context.
- Sliding-window masks with `K in {1, 3, 5, 7, 9}` plus an all-ones endpoint.
- Compare three methods where available: uniform open-loop log-budget schedule, cost-aware replanning, and the Anytime/e-process baseline.
- Keep `alpha = 0.15`, `T = 20`, drift/no-drift conditions, scores, models, and paired seeds unchanged from the paper.

**Report.**

- Validity: `W_mean` and `W_max` over masks, with bootstrap or Wilson-style intervals if easy.
- Efficiency: mean set size, median/IQR, and full-set rate.
- One operating-frontier figure: x-axis `K` or mask strength, set size on the main axis, window failure rate against the `alpha` line.
- One compact table comparing uniform spending versus replanning under the same mask constraints.

**Stop rule.** If CIFAR assets are missing or expensive to regenerate, do not block the rebuttal. A complete California Housing frontier has higher rebuttal value than an incomplete two-task sweep.

### E2. Protocol-Defined Mask Families

**Decision:** run second, only after E1 produces a clean regression result.

**Reviewer concerns answered.** Me2Q mask-choice motivation and concrete-example requests; Reviewer 1--5 draft requests to show masks are ex ante audit protocols rather than tuned hyperparameters.

**Why high span/delta.** This directly changes the perceived object from "arbitrary mask tuning" to "deployment contract." It gives the rebuttal examples reviewers asked for without introducing a new dataset or theory claim.

**Run.**

- California Housing only unless CIFAR summaries are already available.
- Define all masks before looking at outcomes:
  - shift masks: five disjoint four-batch shifts;
  - rolling four-batch audit masks;
  - scheduled high-risk mask: last five batches under the predeclared drift schedule, with the same calendar mask in no-drift;
  - sparse maintenance cadence: `{5, 10, 15, 20}`.
- Compare uniform open-loop and replanning if both are already supported. If not, report the method that is working and avoid adding runner complexity.

**Report.**

- A small mask schematic: rows are mask families, columns are batches.
- A compact table with `family`, `num_masks`, max support, density, `W_mean`, `W_max`, mean set size, and full-set rate.
- A short caption-level statement that masks were fixed from calendar/deployment metadata before labels or failures were inspected.

**Stop rule.** Do not add more operational families. Four families are enough to answer the reviewer request and keep the rebuttal focused.

### E3. Restart/After-Failure Diagnostic

**Decision:** compute from E1/E2 traces; do not launch a standalone simulation unless traces are unusable.

**Reviewer concerns answered.** Me2Q request for examples where mask-and-restart validity is the correct guarantee; Reviewer 1--5 draft emphasis on restart validity versus first-error/anytime control.

**Why high span/delta.** The theory already carries the main restart claim. A small diagnostic makes the practical point concrete: deployed systems continue after a miss, so a first-error guarantee is not the whole monitoring question.

**Compute.**

- For each run and mask family, identify the first monitored miscoverage time.
- Conditional on such a first miss, evaluate suffix behavior:
  - number of later monitored misses;
  - fraction of suffix masks that fail;
  - probability of at least one later monitored miss;
  - number of runs contributing to the conditional estimate.
- Include Anytime/e-process only where the existing run logs make the comparison straightforward. The main contrast can be conceptual: first-error control becomes silent after failure, whereas restart validity asks for renewed suffix control.

**Report.**

- One small table with `family`, runs with first miss, post-first monitored miss rate, and mean suffix failed-window rate.
- If counts are small, say so explicitly and use the diagnostic only as an illustration, not as a new statistical claim.

**Stop rule.** If too few runs have a first monitored miss, omit the table and keep the restart point theoretical plus narrative. Do not spend rebuttal time forcing rare failures.

## Rebuttal Artifacts

Produce at most:

- one operating-frontier figure from E1;
- one protocol-mask schematic from E2;
- one compact table combining E1/E2 metrics;
- optionally one tiny restart diagnostic table from E3.

The author response should quote only robust conclusions:

- all-ones masks recover ordinary spending, but nontrivial mask families impose simultaneous log-budget constraints;
- mask choice is an ex ante audit protocol, not outcome-based tuning;
- efficiency varies because stronger monitoring contracts consume more budget;
- restart validity answers post-failure monitoring, which first-error guarantees do not.

## Camera-Ready or Future-Work Promises

These can be promised separately from rebuttal experiments.

**Camera-ready manuscript edits.**

- Fix the Proposition 2.7 title typo: "Independenceconformal" to "Independence of conformal p-values."
- Replace or disambiguate "admissible" to avoid conflict with statistical admissibility.
- State explicitly that the all-ones open-loop case is classical alpha-spending.
- Add a short "choosing masks" paragraph: masks are fixed from reporting cadence, audit windows, shifts, scheduled risk periods, or maintenance cadences before labels are observed.
- Clarify that finite Monte Carlo estimates near `alpha = 0.15` should be interpreted with uncertainty intervals.

**Defer beyond rebuttal unless already free.**

- New datasets or new model training.
- Full CIFAR reruns without cached logits/weights.
- Horizon sensitivity beyond the submitted `T = 20` setup.
- Forecast-decay or replanning robustness sweeps.
- Runtime/memory profiling.
- External figure packs, pending venue policy.
- Adaptive or data-dependent mask selection; the rebuttal should emphasize ex ante masks.

## Execution Order

1. Inventory existing summaries/logs and regenerate plots from them where possible.
2. Complete E1 on California Housing with paired seeds and the all-ones endpoint.
3. Run E2 on California Housing using predeclared operational masks.
4. Derive E3 from the same traces only if enough first failures exist.
5. Add CIFAR evidence only from cached artifacts or already-submitted summaries.
6. Stop. Do not start a fourth experiment during the rebuttal period.
