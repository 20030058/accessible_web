# Do Agent Skills Teach Accessibility? Working Plan

5-page short paper for **SE4All 2027 @ ICSE**, due **13 Nov 2026 (AoE)**. Source plan: `Do Agent Skills Teach Accessibility — Research Plan.pdf`.

## Decision: accessibility angle, not energy (5 Nov 2026)
- SE4All is a venue about inclusion and accessibility, so energy is a weak fit.
- The research questions, lexicon, coding scheme and evaluation harness (a11y-llm-eval) are already set up for accessibility.
- Energy would need a new measurement setup, and results for generated UIs are noisy. Mention it as one line of future work.

## Research questions
1. How often do UI skills mention accessibility?
2. How specific is the guidance, and does any of it conflict with accessibility?
3. Do popular frontend skills change the accessibility of generated UIs?

## Process
1. **Corpus (days 1–2):** collect skills, deduplicate them (content hash plus name and description), filter to UI and frontend skills with keywords, then check borderline cases with an LLM classifier validated on about 200 hand-labelled skills.
2. **Lexicon pass, RQ1 (day 2):** search for WCAG, ARIA, contrast, keyboard, alt text, focus and screen reader. Report the share of skills that mention any of them, by source and by popularity.
3. **Manual coding, RQ2 (days 3–4):** code about 150 skills as none, generic, specific, or verification, and flag conflicting advice. Two annotators, measured with Cohen's kappa.
4. **Experiment, RQ3 (days 2–5, alongside coding):** compare no skill, the 5–8 most popular frontend skills, and one accessibility skill. Use 10 tasks × 2–3 models × 3 samples. Save every generated page.
5. **Evaluation (day 5):** run a11y-llm-eval on every page to get the WCAG pass rate and failures per page. Compare conditions with effect sizes.
6. **Writing (days 6–8):** follow the 5-page structure, add threats to validity, and release a replication package.

## Data sources

| Source | What | Size | Role | Status |
|---|---|---|---|---|
| **GitSkills**: [HF dataset](https://huggingface.co/datasets/mvaccargiu/gitskills), [arXiv 2608.10906](https://arxiv.org/pdf/2608.10906) | 3.8M SKILL.md files from 282K GitHub repos (July 2026), CC-BY-4.0 | `artifacts` ≈ 6.5 GB, `repos` ≈ 0.02 GB (skip `artifact_siblings`, ≈ 7 GB) | **Main GitHub source**: the "GitSkills" named in the original plan | Not downloaded |
| **ClawHub** (https://clawhub.ai/api/v1) | OpenClaw skill registry with download, star and install counts | Catalog of 8.5K+ skills (total unknown) | Registry source and popularity signal | **Partial**: catalog stopped at about 8.5K rows; no SKILL.md files yet |
| **SkillMD-138K**: [HF dataset](https://huggingface.co/datasets/FayeZC/SkillMD-138K), [arXiv 2608.08453](https://arxiv.org/pdf/2608.08453) | 138K deduplicated skills, CC-BY-4.0 | 0.56 GB | Cross-check, or fallback if GitSkills is too large | Not downloaded |
| **skills.sh** (Vercel) | Registry and leaderboard with install counts | API not yet checked | Picking the most popular frontend skills for RQ3 | Not started |
| SkillsMP | Marketplace, search API needs a key | 63K–400K (sources disagree) | Low priority | Not started |
| GitHub code search (`filename:SKILL.md <term>`) | Keyword search, capped at 1,000 results per query | — | **Dropped**: GitSkills replaces it | 1 query saved (`ui`, 1,000 hits), then stopped |

## Current state (5 Nov 2026, all downloads stopped by user)
- `data/raw/clawhub/catalog.jsonl` holds 8,552 rows but is **incomplete**. Rerun `python3 scripts/download_clawhub.py` from the start, not with `--skip-catalog`.
- `data/raw/github/hits/ui.jsonl` holds 1,000 hits from the dropped code-search approach.
- `data/DATA_LOG.txt` records every dataset event. Scripts append to it, and manual steps should be logged there too.
- `skills/` contains three ClawHub planning skills (`planning-with-files`, `project-planning`, `task-planning`). They are tools for us, not research data, and are not installed. Review `planning-with-files/scripts/` before installing it.

## Next steps
1. Download GitSkills (`artifacts` and `repos`) and SkillMD-138K into `data/raw/`, and log both in DATA_LOG.txt.
2. Rerun the ClawHub download until it completes.
3. Check the skills.sh API for install counts.
4. Write the deduplication and UI filter step across all sources.

## Related work
- Microsoft A11y LLM Eval: the baseline harness.
- From Anatomy to Smells, [arXiv 2607.01456](https://arxiv.org/pdf/2607.01456): SKILL.md quality.
- Human or LLM?, arXiv 2503.15885: accessibility of LLM-generated web code.
- GitSkills, [arXiv 2608.10906](https://arxiv.org/pdf/2608.10906); What Keeps Agent Skills from Being Reusable?, [arXiv 2608.08453](https://arxiv.org/pdf/2608.08453); From Registry to Repository, [arXiv 2607.00911](https://arxiv.org/pdf/2607.00911); Inside the Skill Market, [arXiv 2607.09065](https://www.alphaxiv.org/abs/2607.09065.md).
