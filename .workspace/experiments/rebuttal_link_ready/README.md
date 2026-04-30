# Link-Ready UAI Rebuttal Artifacts

Generated from completed core, protocol-mask, and 100-run synthetic Gaussian experiment summaries.

Start with `ATTACHMENT_GUIDE.md`; it lists the recommended figures/tables and the exact rebuttal framing.

## Contents

- `figures/`: PNG/PDF figures for the anonymous external link.
- `tables/`: compact Markdown tables for rebuttal text or supplement pages.
- `csv/`: machine-readable versions of the same summaries.

## Primary Files

- `figures/rebuttal_hero_summary.png`
- `figures/gaussian_exact_validity.png`
- `figures/synthetic_profiles_allocations.png`
- `figures/protocol_mask_schematic_clean.png`
- `tables/synthetic_diagnostics_ci.md`
- `tables/protocol_masks_ci.md`
- `tables/gaussian_exact_validity.md`

## Caveat

The completed core/protocol runs log mean mask failure `W`. True max-window failure requires rerunning with per-mask failure vectors. The validity figure therefore reports mean `W` with Monte Carlo intervals, not `W_max`.
