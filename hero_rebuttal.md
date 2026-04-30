# Hero Rebuttal Example: Utility Calibration

This file is a cleaned version of a prior successful rebuttal. The raw OpenReview separators and line-broken math have been removed. The goal is to preserve the useful structure for future rebuttal agents: identify the reviewer's true objection, answer it directly, make concrete revision commitments, and close the loop with post-rebuttal movement.

## Outcome

| Field | Value |
|---|---|
| Decision | Accept (Spotlight) |
| Decision date | 22 Jan 2026 |
| Paper topic | Utility-aware multiclass calibration |
| Main contribution | A binning-free utility calibration framework with scalable assessment and post-hoc patching |

**Decision summary.** The paper was accepted as a spotlight. The decision emphasized that the work shifts calibration toward task-specific, utility-aware evaluation; introduces a scalable and theoretically grounded binning-free post-hoc algorithm; clearly explains the sample-complexity issues of mean calibration error in many classes; unifies top-class and class-wise calibration; and validates the approach on ImageNet-1K with ViT.

## Rebuttal Pattern To Reuse

Good features of these rebuttals:

1. **Lead with the reviewer's core concern.** Each response begins by naming the issue the reviewer actually cared about: novelty, motivation, clarity, semantics, tractability, or empirical support.
2. **Turn broad concerns into precise claims.** For example, a vague concern that utility calibration is too narrow becomes a precise explanation of how the utility function can encode a decision rule and why thresholding the scalar predicted utility is still meaningful.
3. **Use equations sparingly but decisively.** Math is used to clarify reductions such as $u_\ell(p,y)=-\ell(y,\delta_\ell(p))$ and to distinguish the paper's guarantee from related work.
4. **Admit manuscript-level weaknesses.** Several responses concede that the main text overemphasized related work or buried algorithms/results in the appendix, then promise concrete structural edits.
5. **Separate theory from presentation.** When a reviewer attacks soundness but the issue is exposition, the response points to existing proofs and commits to making pointers and algorithms explicit.
6. **Close with a targeted revision promise.** The response does not only defend the paper; it tells the reviewer exactly what will change.

## Reviewer iGsi

**Review metadata**

| Field | Value |
|---|---|
| Rating | 6: Accept |
| Confidence | 5: Absolutely certain |
| Soundness | Correct / minor errors |
| Significance | Somewhat significant |
| Novelty | New results |
| Clarity | Clear |

**Core review.** The reviewer viewed the paper as a useful generalization of Zhao et al. from decision calibration to utilities. They wanted a clearer discussion of that relationship and asked for examples of genuinely new calibration notions that arise from the utility-calibration framework. They also suggested that the exposition could be written in terms of losses, with $\ell=-u$.

**Main concerns to answer**

- Is the paper more than an incremental generalization of Zhao et al.?
- What new weaker calibration notions become clearer under utility calibration?
- Can the framework say anything about the hard problem of full multiclass calibration?
- Should the paper phrase the framework in losses rather than utilities?

### Cleaned Author Response

We thank the reviewer for their feedback, which we address below.

#### 1. Relation to Zhao et al.

We agree that our framework can be viewed as a generalization of Zhao et al. In their setting, for every loss function $\ell$ with at most $K$ actions and best-response policy $\delta_\ell$, the model should provide an unbiased estimate of the expected loss of that policy. This can be encoded in our framework by defining

$$
u_\ell(p,y)=-\ell(y,\delta_\ell(p)),
$$

and collecting such utilities in the class $\mathcal U_{\mathrm{dec},K}$. Decision calibration of order $K$ is then implied by requiring $\mathrm{UC}(f,\mathcal U_{\mathrm{dec},K})$ to be small. We will highlight this reduction more explicitly in the manuscript.

The difference is the type of guarantee and the computational trade-off. Zhao et al. target simultaneous unbiasedness over all such policies, while Gopalan et al. (COLT 2024) show that auditing worst-case decision calibration is computationally hard in multiclass settings. Our work takes a different compromise: we push the decision-making into the utility $u$ and ask that, for a fixed utility, the predicted utility $v_u(X)$ be a reliable regressor of the realized utility $u(f(X),Y)$.

This gives simpler but still meaningful guarantees. A user can trust $v_u(X)$ as an approximate expectation of future true utility, and monotone post-processing of $v_u$ cannot substantially improve threshold decisions based on $v_u$. This captures settings where a user predicts future gain or loss and decides whether to participate or abstain. Because our framework generalizes Zhao et al., we can still identify multiple settings where utility calibration is measurable. For richer classes, such as linear and rank-based utilities, worst-case auditing is hard, so we instead propose auditing the distribution of utility calibration errors through eCDF plots.

We will revise the paper to compare more clearly with Zhao et al.

#### 2. What weaker calibration notions encode

Complete multiclass calibration of the full probability vector, while retaining good Brier score, is essentially unattainable in high dimensions. Full calibration error is not statistically estimable without strong assumptions and is often computationally intractable to audit. This forces us to use weaker, structured notions. Our framework clarifies what these weaker notions guarantee.

Top-label, top-$K$, and class-wise calibration are not intrinsic properties of $f$; they encode assumptions about how users act. Top-label calibration assumes only the argmax matters, top-$K$ calibration assumes membership in a top-$K$ set matters, and class-wise calibration treats each class one-vs-all. In our framework, each becomes a concrete utility class, such as $\mathcal U_{\mathrm{TCE}}$, $\mathcal U_{\mathrm{CWE}}$, or $\mathcal U_{\mathrm{top}K}$. This makes the downstream assumption explicit rather than implicit.

Ideally, predictors should be calibrated for the utility classes relevant to the application. When these are unknown, top-class, top-$K$, and class-wise utilities are reasonable defaults. Our work gives corresponding utility-calibration versions that are binning-free, scalable to measure, and decision-theoretically interpretable.

Beyond finite classes, linear and rank-based utilities are natural generalizations. Linear utilities $\mathcal U_{\mathrm{lin}}$ capture all linear payoffs simultaneously and calibrate one-dimensional projections of the output distribution. Rank-based utilities $\mathcal U_{\mathrm{rank}}$, including discounted cumulative gain utilities, capture ranking and retrieval goals not naturally covered by top-label or class-wise metrics.

Finally, empirical CDFs over utility classes reveal behavior that single scalar metrics can hide. In the appendix, we show cases where a calibration method improves a standard scalar metric, such as top-class error or Brier score, but shifts the eCDF to the right, meaning calibration worsens for subsets of utilities. These eCDFs provide a more nuanced assessment of reliability across plausible downstream utilities.

We also note the suggestion to describe the framework through losses and will point out the equivalent formulation with $\ell=-u$.

**Post-rebuttal outcome.** The reviewer thanked the authors and asked them to add salient points from the rebuttal to the paper. The score was unchanged.

## Reviewer oJiC

**Review metadata**

| Field | Value |
|---|---|
| Rating | 5: Borderline Accept |
| Confidence | 3: Fairly confident |
| Soundness | Correct / minor errors |
| Significance | Somewhat significant |
| Novelty | New results |
| Clarity | Mixed |

**Core review.** The reviewer appreciated the related-work discussion but felt that it crowded out the paper's own contributions. They wanted more motivating examples, clearer theorem/proposition statements, more main-text experimental evidence, and a clearer presentation of the algorithm and formal measurability results.

**Main concerns to answer**

- The main text overweights related work relative to the paper's contributions.
- The introduction does not clearly communicate why utility calibration matters as a standalone framework.
- Important algorithms, examples, and formal results are buried in the appendix.
- Several citations, notation choices, and local claims need correction.

### Cleaned Author Response

We thank the reviewer for their detailed assessment. We address the concerns below.

#### 1. Significance and novelty

Our paper starts from the canonical goal of calibration: ensuring that what is predicted matches what is observed on average. We consider a decision-making setting where a user observes $f(X)$, estimates the utility of an action, and later receives a realized utility. In this setting, the user's fundamental goal is to estimate expected utility by simulating $\hat Y$ from $f$. A core requirement for trust is that this expected utility aligns with realized utility. Our framework defines this requirement, generalizes it to arbitrary utility classes, and establishes its properties.

The manuscript contributes four concrete pieces.

**Unified, binning-free calibration framework.** We introduce utility calibration for arbitrary utility functions and show that it recovers and refines standard metrics such as top-class and class-wise calibration. The induced metrics are binning-free and upper bound commonly used binned variants, such as binned TCE and CWE, up to a multiplicative factor proportional to the number of bins.

**Decision-theoretic guarantees.** We show that the induced metrics are tractable and yield guarantees for downstream decisions that threshold expected utility, such as participating when predicted utility is high and abstaining when it is low. Small utility calibration error ensures that predicted utility behaves as a calibrated regressor of realized utility, giving a principled replacement for heuristic binning when decision quality matters.

**Scalable assessment for infinite utility classes.** We develop an eCDF-based methodology for assessing utility calibration over infinite utility classes, including linear and rank-based utilities. Although auditing a single worst-case utility is usually computationally hard, it is feasible and informative to audit the distribution of errors across utilities.

**Post-hoc calibration.** The framework yields a simple patching algorithm that provably decreases the proposed metrics and is empirically competitive with standard post-hoc calibration methods, while adapting to specific or domain-defined utility classes.

Practitioners currently relying on binned top-class or class-wise calibration can directly adopt these utility-based metrics to obtain binning-free, decision-theoretically grounded assessments. When application-specific utilities are known, the same framework can target those utilities directly. The eCDF protocol and patching procedure also provide modular primitives for future work.

#### 2. Clarity and structure

We agree that the current manuscript devotes too much main-text space to related work. We will restructure the paper to prioritize the main contributions. Specifically, we will move the extended literature review to the appendix, keep only a condensed version in the main text, and use the recovered space to move the post-hoc patching algorithm and formal interactive-measurability statements into the main body. The camera-ready version allows an additional page, so this revision is feasible.

#### 3. Specific technical points

We appreciate the detailed comments and agree with many of them, including the citation fixes and requested reformulations. We will correct the manuscript accordingly.

For Definition 1.1, there is indeed a missing power and a normalizing power $1/2$ outside the expectation. We will add a citation for the definition. Lee et al. (2023) and Duchi (2024) were cited for the impossibility of measuring calibration error, not for the definition itself.

We will move the related-work excerpts out of Section 3.

For Proposition 3.1, the phrase "barely benefit" will be clarified. If $\mathrm{UC}=0$, there is no benefit from the relevant post-processing. The bound quantifies the maximum possible benefit when the model is not perfectly utility calibrated.

For Example 3.4, the utility-calibration metrics may or may not select a bin with large Lebesgue volume. What matters is the worst-case bin with respect to the distribution of $v_u$. We prove that the empirical estimates converge at rate $O(1/\sqrt n)$. Consequently, utility-calibration-inspired metrics such as $\mathrm{UTCE}$ upper bound binned metrics such as $\mathrm{TCE}_{\mathrm{bin}}$ up to a multiplicative factor equal to the number of bins, typically 10 or 15 in practice. If the utility-calibration metric is zero, the binned alternatives are zero regardless of the binning heuristic; the converse is false. We provide a small example in Appendix B.2.

We will add citations for rank-dependent utility, including Jarvelin and Kekalainen, "Cumulated gain-based evaluation of IR techniques," ACM Transactions on Information Systems 20(4), 422-446 (2002), and for a single predictor being used in multiple downstream settings, including Elkan, "The foundations of cost-sensitive learning," IJCAI 2001.

**Post-rebuttal outcome.** The reviewer said the rebuttal addressed the major concern about the imbalance between related work and contributions, and stated that this was enough to raise the score toward borderline acceptance.

## Reviewer bzzn

**Review metadata**

| Field | Value |
|---|---|
| Rating | 6: Accept |
| Confidence | 3: Fairly confident |
| Soundness | Correct / minor errors |
| Significance | Somewhat significant |
| Novelty | New results |
| Clarity | Generally clear |

**Core review.** The reviewer was broadly positive but wanted more explicit support for the decision-theoretic guarantees, the exact $O(n\log n)$ UC computation, the patching algorithm, and the sampling distribution used for eCDF evaluation.

**Main concerns to answer**

- The Section 3.1 guarantees are not experimentally illustrated.
- The word "inherits" under-explains the relation to Cutoff calibration.
- The exact implementation behind the $O(n\log n)$ computation should be stated.
- The patching algorithm should be in the main text.
- The eCDF conclusions may depend on the sampling distribution $D_u$.

### Cleaned Author Response

We sincerely thank the reviewer for their feedback, which will help sharpen both exposition and scope.

#### 1. Theoretical and experimental support for guarantees

The guarantees in Section 3.1, including robustness to monotone post-processing and the DCU upper bound, are formally proved in the appendix. We used the term "inherits" to avoid overclaiming novelty, but we agree that the main text should point explicitly to the formal statements. We will add these pointers.

Our initial experiments focused on assessment scalability. We agree that empirical verification would make the decision-theoretic bounds more tangible. In the revision, for a subset of our classification experiments, we will add experiments that measure the effect of post-hoc calibration on the utility-risk gap from Proposition 3.1 and report its correlation with estimated UC.

#### 2. Computational complexity

The $O(n\log n)$ complexity is for an exact calculation, not an approximation. The procedure sorts samples by predicted utility, which costs $O(n\log n)$, and then performs a linear scan to find the maximum-deviation interval, using Kadane's algorithm. We will state this implementation detail in Section 3.2.

#### 3. Patching algorithm

We agree that surfacing the patching algorithm will improve readability. In the camera-ready version, we will use the additional page to move the algorithm description and formal result statement into the main body.

#### 4. Choice of eCDF distribution

Ideally, the utility distribution should be informed by the user base. Our experiments use a non-informative prior. For example, class-wise calibration can be viewed as a restriction of $\mathcal U_{\mathrm{lin}}$ obtained by parameterizing utilities with canonical basis vectors. Sampling uniformly from the boundary of the $\ell_\infty$ sphere generalizes this construction to the full utility range $[-1,1]$ without privileging a coordinate. We used a similar construction for rank-based utilities.

We tried several sampling approaches and observed similar conclusions. In the revision, we will include experiments that shift the prior distribution by biasing it toward specific regions of the $\ell_\infty$ hypersphere.

**Post-rebuttal outcome.** The reviewer thanked the authors for the clarifications and maintained the initial rating.

## Reviewer s2s3

**Review metadata**

| Field | Value |
|---|---|
| Rating | 4: Weak Accept / Weak Reject |
| Confidence | 2: Somewhat confident |
| Soundness | Marked as major errors, though the reviewer said the mathematical statements appear technically correct |
| Significance | Somewhat significant |
| Novelty | New results |
| Clarity | Clear but motivation could be stronger |

**Core review.** This was the most skeptical review. The reviewer thought the logical chain was incomplete: threshold guarantees seemed too narrow, interval witnesses seemed ad hoc, utilities seemed synthetic, and random utility sampling might reflect artifacts of the sampling distribution. They also questioned whether patching helps a whole utility class or only detected witnesses.

**Main concerns to answer**

- How can utility calibration handle multi-action or ranking decisions if the formal guarantee is about thresholding $v_u(X)$?
- Why are worst-case intervals the right witness class?
- Are the utility classes real or only synthetic?
- Why should an eCDF over randomly sampled utilities be meaningful?
- Can patching worsen calibration for utilities not used during auditing?

### Cleaned Author Response

We sincerely thank the reviewer for their feedback. We hope to address the main concerns below.

#### 1. Decision-theoretic guarantees and thresholds

Our framework handles multi-action decision rules by encoding the decision procedure into the utility function $u$. The user observes $f(X)$, takes an action based on $f(X)$, possibly through a complex optimization, and receives utility $u(f(X),Y)$. Before deploying $f$ and observing $Y$, the user wants to estimate future utility. Utility calibration directly targets this goal by requiring the model's simulated estimate to be unbiased for $u(f(X),Y)$ on average.

In particular, UC evaluates the reliability of the scalar predictor $v_u(X)$, which is the user's prediction of future utility. Low UC guarantees that $v_u(X)$ is an approximately unbiased estimator of realized utility. This aligns with the classical calibration principle: predicted quantities should match observed realizations on average.

Threshold policies are natural in this context. A user may abstain when estimated utility is below a threshold and act otherwise. Proposition 3.1 shows that if UC is low, threshold decisions based on $v_u(X)$ are robust to monotone post-processing. This gives a robustness guarantee for deciding whether to deploy predictor $f$.

We acknowledge that approaches such as Roth and Shi target stronger notions of policy optimality, where the predictor should enable optimal decisions. Those methods do not scale well and are generally intractable outside low-dimensional settings. Our approach offers concrete guarantees while scaling to high-dimensional settings with many classes.

#### 2. Motivation for interval-based witnesses

Worst-case intervals balance expressivity and computational tractability.

**Unification.** With appropriate $u$, UC upper bounds binned top-class and class-wise calibration estimators up to a multiplicative factor equal to the number of bins, often 10-15 in practice. This simplifies measurement and avoids dependence on binning heuristics, which are known to strongly affect error estimates.

**Principled structure.** Closed intervals are the closed convex sets of the real line. They form a natural witness class for the one-dimensional predicted utility $v_u(X)$. As shown in Proposition 3.1, this structure is sufficient to control errors under monotone post-processing and to guarantee that $v_u$ is itself a calibrated regressor.

**Scalable auditing.** For fixed $u$, computing UC reduces to sorting $v_u(X)$ and scanning cumulative discrepancies. The complexity is $O(n\log n)$ and is independent of the number of classes $C$ once $u$ has been evaluated. This matches the complexity of adaptive equal-weight binning schemes.

#### 3. Relevance of utility classes

Top-class, top-$K$, and class-wise utilities capture accuracy estimation when deploying $f$. These classes recover standard calibration metrics while adding the properties above. Although generic, they are not synthetic in the sense of being arbitrary; they mirror the established calibration objectives already reported in the literature.

Linear utilities generalize class-wise utilities to broader cost-sensitive classification structures. Rank utilities generalize top-$K$ calibration error. In the appendix, we also investigate discounted cumulative gain utilities, which directly mirror information-retrieval metrics and are a special case of rank-based utilities.

#### 4. Specific questions

In ideal settings, domain experts specify the utilities. When domain-specific utilities are unavailable, class-wise, top-$K$, and top-class utility classes are reasonable defaults because they target the same notions as existing calibration metrics while providing stronger guarantees and avoiding binning pathologies. Linear and rank utilities further generalize these finite classes and can be audited distributionally with eCDF plots. The patching algorithms are utility-independent in construction and can be adapted to domain-specific cases.

The framework is compatible with complex tasks because these tasks can be encoded in $u$. For instance, the appendix includes synthetic utilities modeling more complex settings.

For the experiments, we used non-informative priors such as uniform sampling from the $\ell_\infty$ sphere to cover the utility range. We tried several sampling approaches and observed consistent conclusions. In the revision, we will add experiments showing the effect of changing the sampling distribution by biasing it in different ways.

Theoretically, patching minimizes the worst-case error over a class. Empirically, Appendix C.2 shows that patching shifts the entire error distribution, the eCDF, to the left for the whole class.

**Post-rebuttal outcome.** The reviewer said the rebuttal clarified how utilities encode multi-action decisions, why intervals are used, and how the proposed utility classes relate to standard calibration metrics. They raised the score.

## Reviewer r3Gv

**Review metadata**

| Field | Value |
|---|---|
| Rating | 6: Accept |
| Confidence | 3: Fairly confident |
| Soundness | Correct / minor errors |
| Significance | Somewhat significant |
| Novelty | New results |
| Clarity | Contributions accurate but not accessible early enough |

**Core review.** The reviewer understood the technical construction after reading the full paper but wanted the introduction to explain the key ideas earlier: what UC is, what UC over a family is, and what new results are obtained for families. They also asked for concrete semantics: when does a user make a decision based on expected utility rather than directly using the high-dimensional prediction?

**Main concerns to answer**

- What decision is the user making if $v_u(X)$ is only one-dimensional?
- Why would one prefer the classifier with better utility-calibration behavior?
- How does this framework improve on existing evaluation metrics rather than merely changing model rankings?
- The introduction needs a more accessible motivating example.

### Cleaned Author Response

We thank the reviewer for their constructive feedback. We appreciate the opportunity to clarify the semantics of our framework.

#### 1. Motivation and semantics

Our framework handles multi-action decision rules by encoding the decision procedure into the utility function $u$. The user observes $f(X)$, takes an action based on $f(X)$, and receives utility $u(f(X),Y)$. Before acting, the user may want to estimate future utility using $f$ itself. Utility calibration directly targets this by ensuring that the user receives an unbiased estimate, on average, of $u(f(X),Y)$.

Although $f(X)$ is high-dimensional, the final decision to act often reduces to a scalar comparison: is expected benefit larger than cost? This can lead the user to participate or abstain depending on expected utility. The scalar $v_u(X)$ is the model's estimate of this future utility. Thresholding $v_u(X)$ is therefore a canonical family of actions.

Section 3 proves that, when UC is low, threshold decisions based on $v_u(X)$ are robust to monotone post-processing. Moreover, $v_u$ is itself a calibrated regression function of true utility. This gives a robustness guarantee for the user's decision about whether to deploy $f$. Some related work, such as Roth and Shi (2025), offers stronger multi-action policy-optimality guarantees, but these guarantees are intractable beyond a few dimensions. Our goal is to provide concrete guarantees that scale.

#### 2. Why this evaluation framework is better

Our framework improves on currently used metrics in two ways.

**A principled alternative to binned metrics.** Standard top-class and class-wise calibration metrics rely on heuristic binning schemes, which suffer from bias and instability. Nixon et al. (2019) show that changing the binning scheme can strongly affect the ranking of post-hoc calibration methods, and Kumar et al. (2019) show that binning schemes can have large bias. Our framework gives a unified, binning-free alternative. With suitable $u$, utility calibration recovers the same notions as classical metrics and upper bounds binned estimators up to a multiplicative factor equal to the number of bins. The utility-calibration metrics concentrate at dimension-independent rates, up to a logarithmic factor for $\mathrm{UCWE}$ and $\mathrm{UtopK}$, are fast to compute, and have decision-theoretic interpretations.

**Nuanced diagnostics through eCDFs.** Scalar metrics can hide important behavior. Our eCDF-based evaluation provides a finer diagnostic for infinite utility classes, such as all linear or rank-based tasks. In appendix experiments, we observe cases where post-hoc methods improve scalar summary metrics but worsen the eCDF curves by shifting the distribution of errors to the right. Thus, eCDF plots identify degradation that standard metrics miss.

#### 3. Clarity

We appreciate the feedback on the introduction. We will revise it to state earlier and more clearly: (A) the definition of $\mathrm{UC}(f,u)$, (B) reliability over a family $\mathcal U$, and (C) the key results on interactive measurability. We will also introduce the threshold-decision examples earlier in the paper.

**Post-rebuttal outcome.** The reviewer thanked the authors and raised the rating.

## Consolidated Lessons For Future Rebuttals

- When a reviewer calls a guarantee too narrow, explain the modeling reduction before defending the theorem. In this case, the action rule is encoded in $u$, while thresholding applies to the scalar predicted utility $v_u(X)$.
- When a reviewer calls a design choice ad hoc, give three answers: what it unifies, what principle motivates it, and what computational benefit it buys.
- When a reviewer asks for real-world relevance, connect abstract utility classes back to existing metrics first, then to richer domain-specific utilities.
- When important material is in the appendix, concede the presentation issue and promise exact main-text moves.
- Score movement often comes from clarity, not from adding new claims. The strongest responses here made reviewers feel that the existing contribution was easier to understand.
