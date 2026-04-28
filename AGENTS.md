# UAI Paper 2026

This repository is a lightweight project scaffold.

Shared agent tooling:
- `.agents` points to `../research-agent/.agents` for Codex.
- `.claude/skills` points to `../../research-agent/.claude/skills` for Claude.

Project-specific content now lives under `code/` and `paper/`.

Runtime environments:
- Use `codex_env` for Codex-side maintenance operations, lightweight scripts,
  and agent/tooling work that is not part of the experimental pipeline.
- Use the conda environment `anyhow_conformal` for AnyhowCP experiments,
  package checks, and paper/rebuttal experiment runs. The environment was
  created at `/data/mahmoud.hegazy/.condacustom/envs/anyhow_conformal`.
- When invoking the experiment package from the repository root, prefer:

```bash
conda run -n anyhow_conformal env PYTHONNOUSERSITE=1 \
  python code/AnyhowCP-uai-2026-submission/scripts/run_paper_experiments.py
```

Keep experiment outputs under `.workspace/experiments/` unless the user asks
for paper-ready figures or tables.
