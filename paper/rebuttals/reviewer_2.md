# Reviewer 2

We thank the reviewer for the careful assessment. The main concern is that our method may look like ordinary alpha-spending over independent errors. We agree that, for the all-ones mask, our threshold schedules reduce to classical alpha-spending; we will state this explicitly. The contribution is the batch-sequential extension: simultaneous validity for a pre-specified mask family, restart validity after monitored failures, and restricted closed-loop replanning using calibration data and test features without past test labels. In log-budget form, each mask imposes its own constraint, `sum_t M_t s_t <= -log(1-alpha)`. This collapses to one alpha-spending budget only for the all-ones family.

We also agree that the current motivation can make masks look like difficult hyperparameters. We will revise to present them as ex ante audit queries fixed by the deployment protocol: rolling K-batch quality audits, fixed clinical or production shifts, pre-declared high-risk periods, sparse maintenance checks, and incident review. Then mask-and-restart validity answers the intended question: what is the probability of at least one miss in the monitored period, and does the guarantee renew after a miss? K is an operational time scale; if several values are plausible, one should report the curve over K rather than tune K for the smallest sets.

Efficiency sensitivity to masks is real and expected. Larger or denser mask families impose more simultaneous budget constraints, so sets must grow. We will frame experiments as an operating frontier: validity is fixed for the monitoring question, while efficiency reflects its ambition.

Experiment/link slot, to fill only after runs complete: one short sentence or compact table should report window failure and set size across K/mask families, without claiming unrun results. If external anonymous links are allowed, detailed frontiers, mask schematics, and confidence-interval tables can be placed at [anonymous figure link: TBD].

Finally, we will fix the typo "Independenceconformal" in Proposition 2.7 and replace "admissible" by "feasible" where possible, or explicitly disambiguate the term.
