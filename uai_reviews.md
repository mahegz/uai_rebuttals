# UAI 2026 Reviews

This file contains the cleaned review dump for Submission 823. It is structured for future rebuttal planning: first the quantitative scores, then the reviewer's main positive points, then the objections that need to be answered.

## Reviewer Me2Q

**Review metadata**

| Field | Value |
|---|---|
| Submission | 823 |
| Reviewer | Me2Q |
| Review date | 14 Apr 2026, 21:37 |
| Last modified | 24 Apr 2026, 00:45 |
| Rating | 6: Weak Accept |
| Confidence | 4: Quite confident |

**Scores**

| Criterion | Score |
|---|---|
| Novelty | 2: Fair; the paper contributes some new ideas. |
| Correctness | 3: Good; the paper appears technically sound, but the reviewer has not carefully checked all details. |
| Evidence-based support | 3: Good; the main claims are supported by convincing evidence. |
| Reproducibility | 3: Good; key resources and details are sufficiently described. |
| Writing clarity | 3: Good; the paper is organized, but the presentation could be improved. |

**Reviewer summary**

The paper aims to improve anytime-valid and standard conformal prediction by addressing gaps in existing guarantees:

- reliance on previous test labels;
- validity on certain subsets of time steps;
- validity conditional on an error being made.

The reviewer understands the method as a family of alpha-spending algorithms designed to address these issues.

**Strengths**

- Ensuring error control conditional on an error having been made, and into the future, is useful.
- The theory of planning the spending schedule is reasonable.
- The framework includes an interesting solution to the alpha-spending problem.

**Weaknesses and rebuttal targets**

1. **Novelty concern.** The reviewer sees the method as equivalent to planning an alpha-spending schedule for independent errors.
2. **Motivation concern.** The reviewer finds the problem somewhat contrived because the user's mask choice is a difficult practical hyperparameter.
3. **Empirical sensitivity concern.** The simulations make efficiency depend strongly on the chosen masks.
4. **Concrete examples needed.** The reviewer asks for examples where a user knows the right family of masks, and where mask-and-restart validity is the correct guarantee.

**Specific comments**

- Prop. 2.7 typo: `"Independenceconformal"`.
- Consider replacing the term `"admissible"` because it has a specific statistical meaning; `"feasible"` may be clearer.

**Reviewer justification**

The theory and methods are solid and well developed. The main reservations are that the motivation feels contrived and that the alpha-spending methodology seems like the default way to control errors over multiple batches, weakening the perceived novelty.

## Initial Rebuttal Plan

The rebuttal should probably focus on the two core objections rather than spending space on the minor comments:

1. **Separate the paper from ordinary alpha-spending.** Explain what ordinary alpha-spending would require, where it fails, and what the mask/restart structure adds. Make the distinction formal if possible.
2. **Make masks feel operational rather than arbitrary.** Give concrete settings where masks are dictated by the deployment protocol, subgroup structure, stopping/restart rule, or auditing objective.
3. **Explain efficiency sensitivity honestly.** If mask choice affects power, frame this as expected: the method gives validity for the analyst's chosen future-facing query class, and efficiency reflects how ambitious that class is.
4. **Promise easy manuscript changes.** Mention the typo and terminology fix quickly, then commit to improving examples and motivation.
