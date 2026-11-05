# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This is a research project in its early stage. There is no code, build system, or test suite yet. So far the only file is `Do Agent Skills Teach Accessibility — Research Plan.pdf`. When you add tooling (a package manager, scripts, a test runner), update this file with the real commands.

## What this project is

It is a 5-page short paper for **SE4All 2027 at ICSE**, **due 13 November 2026 (AoE)**. The paper studies whether agent skills (SKILL.md files) for UI and frontend work teach accessibility.

Research questions:
1. How often do UI skills mention accessibility?
2. How specific is the guidance, and does any of it conflict with accessibility?
3. Do popular frontend skills change the accessibility of generated UIs?

## Planned pipeline

The code will most likely follow these stages:

1. **Corpus**: collect UI skills from GitSkills and ClawHub, deduplicate them, then filter with keywords plus an LLM classifier. The classifier is checked against about 200 hand-labelled skills.
2. **Mining**: run a lexicon pass (WCAG, ARIA, contrast, keyboard). Then manually code about 150 skills as `none` / `generic` / `specific` / `verification` and flag conflicting advice. There are two annotators, and agreement is measured with Cohen's kappa.
3. **Experiment**: compare three conditions: no skill, the top 5–8 frontend skills, and one accessibility skill. Use 10 test cases × 2–3 models × 3 samples each.
4. **Evaluation**: use Microsoft's `a11y-llm-eval` harness to measure the WCAG pass rate and the number of failures per page. This harness is also the baseline for related work.

Keep the stages separable and their outputs on disk: the raw corpus, the deduplicated and filtered corpus, the lexicon hits, the annotation sheets, generated UIs, and evaluation results. Manual coding and the writing happen after the automated runs, so they need stable intermediate artifacts.

## Related work referenced in the plan

- Microsoft A11y LLM Eval: the baseline harness. It shows that an accessibility skill improves results.
- *From Anatomy to Smells* (arXiv 2607.01456): an empirical study of SKILL.md quality.
- *Human or LLM?* (arXiv 2503.15885): accessibility of LLM-generated web code.

## Timeline

Week 1: corpus and experiment runs. Week 2: manual coding. Week 3: writing.
