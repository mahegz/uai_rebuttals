We thank the reviewer. We will better separate our contribution from ordinary alpha-spending and make masks operational.

Alpha-spending is the right primitive once monitored events are fixed. Our contribution is the validity target: simultaneous control over an ex ante family of masked windows, plus restart validity and deployability without past test labels. For threshold policies, independence of conformal p-values gives exact product constraints; in log-budget form,
$$
\sum_t M_t s_t \le -\log(1-\alpha),\qquad M\in\mathcal M .
$$
Thus the mask-incidence matrix, not a single horizon, defines the feasible set. The optimization allocates risk by cost curves and overlapping audit constraints. The same constraints imply suffix/restart validity: after a monitored error, the remaining suffix still respects the budget. By contrast, a Ville/e-process guarantee controls first boundary crossing and need not provide post-failure control. We will revise Sections 1--4 to make this comparison explicit.

Masks should not be tuned after seeing results. $\mathcal M$ is fixed by the reporting or audit protocol: all $K$-day rolling windows, production shifts, hospital/weekend periods, scheduled high-risk intervals, sparse maintenance checks, or externally flagged cases. Test labels are not used to choose masks or update thresholds. We will add a short "choosing masks" paragraph and expand examples so $\mathcal M$ is a deployment contract, not a modeling convenience.

Efficiency sensitivity is real and expected: larger or richer mask families impose stronger simultaneous guarantees and spend the same $\alpha$ more conservatively. We will state this safety-efficiency tradeoff directly. Validity is unchanged when $\mathcal M$ is fixed ex ante; set size reflects the ambition of the query class.

Experiment/link slot: include only completed sensitivity evidence, ideally one compact K/frontier sentence or table. If anonymous external links are allowed, detailed plots/tables can go at [anonymous figure link: TBD]; no actual link or result will be invented.

We will fix the Proposition 2.7 typo ("Independence of conformal p-values"). We agree that "admissible" has statistical baggage; barring notation conflicts, we will rename it "feasible" or "valid deployable" policies and define the term once.
