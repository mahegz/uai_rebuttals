# Rebuttal Attachment Guide

This directory is ready to use as the anonymous external-link supplement for the rebuttal. The strongest story is deliberately narrow: protocol masks encode ex ante monitoring contracts, sparse contracts can make replanning useful, dense symmetric contracts behave like uniform spending, and exact Gaussian calculations isolate the validity/\(W\) question.

## Lead With These

1. `figures/protocol_mask_schematic_clean.png`: simple visual explanation of the mask families. Use this when replying to requests for intuition, motivation, or concrete industrial monitoring protocols.
2. `figures/protocol_efficiency.png`: main efficiency figure for the rebuttal. It separates dense symmetric windows, which behave almost like uniform spending, from sparse ex ante contracts, where replanning has exploitable structure.
3. `tables/protocol_masks_ci.md`: compact table for the protocol-mask claim. Maintenance-cadence and scheduled-high-risk masks reduce the reported size metric by about 64-76%, with empirical mean mask-failure estimates around `0.10-0.11` at `alpha=0.15` in the completed runs.
4. `tables/core_frontier.md` and `figures/core_frontier_efficiency_regression.png`: standard-window frontier evidence. Use this as a negative control: gains are modest or absent for dense/symmetric windows, so the method is not advertised as uniformly better.
5. `figures/gaussian_exact_validity.png` and `tables/gaussian_exact_validity.md`: exact Gaussian validity check. Use only for alpha-spending/\(W\) concerns because the exact max failure is `alpha` while schedules change.
6. `figures/rebuttal_hero_summary.png`: optional one-page overview. Because it includes the synthetic diagnostic, do not use it before the protocol-specific assets above.

## Use As Backup, Not The Headline

- `figures/core_frontier_validity.png` reports empirical mean mask failure with Monte Carlo intervals, not max-window failure. It should be cited only with that wording.
- `figures/core_frontier_efficiency_classification.png` is best kept as backup; it invites more scrutiny than it helps in the rebuttal.
- `tables/synthetic_diagnostics_ci.md`, `figures/synthetic_diagnostics.png`, and `figures/synthetic_profiles_allocations.png` are backup for the forecasting diagnostic. They should not be the lead empirical evidence in reviewer replies.
- `csv/core_full_rows.csv` is included for transparency, but the classification all-ones rows are noisy/high in this completed run and should not be foregrounded in the rebuttal.

## Recommended Rebuttal Claim

The added experiments do not claim that replanning always improves over uniform alpha-spending. They support the more defensible claim that masks can encode natural production/audit contracts such as shift blocks, rolling audit periods, scheduled high-risk periods, or maintenance cadences. Dense symmetric windows behave almost like uniform spending, as expected. Sparse ex ante contracts show the intended positive case: maintenance-cadence and scheduled-high-risk masks reduce the reported size metric by about 64-76%, with empirical mean mask-failure estimates around `0.10-0.11` at `alpha=0.15` in the completed runs. The exact Gaussian check is included only to address the validity/\(W\) concern.

## Exact Text Snippet

"In response to the reviewers, we added targeted experiments in an anonymous supplement. The main new evidence is protocol-mask based: dense symmetric windows behave almost like uniform spending, while sparse ex ante contracts such as maintenance cadence and scheduled high-risk periods reduce the reported size metric by about 64-76%, with empirical mean mask-failure estimates around 0.10-0.11 at alpha=0.15 in the completed runs. This is the intended positive claim. Replanning helps when the monitoring contract contains exploitable structure; it is not advertised as uniformly better. We also include an exact Gaussian check only for the alpha-spending/W concern: all compared full-budget schedules have exact max failure `W=alpha` even though their allocations differ."

## PNG Notes

Primary figure PNGs already exist, including `figures/protocol_mask_schematic_clean.png` and `figures/protocol_efficiency.png`. Keep the Markdown tables as the table uploads unless an image-only upload path is required.

## Remaining Camera-Ready Promises

The camera-ready version should add the broader experiments to the appendix, make the distinction between mean mask failure and max-window failure explicit, add the lower-bound propagation remark for p-values, add a short conclusion/related-work paragraph, and soften the e-process comparison as a tradeoff against a stronger guarantee.
