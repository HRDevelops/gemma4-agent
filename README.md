# From 0.13 to 0.20: Trace-Guided Improvement of a Small Open-Weight Coding Agent

CS594/794 Deep Learning, final project, Nazarbayev University
Muhammad Husnain Rasool · Galymzhan Zaharas

## What we did
We improved an AI coding agent built on Google's Gemma 4 (31B, 4-bit) for the Kaggle *Gemma 4 Developer Agent* competition. The agent fixes real GitHub issues and is scored by hidden unit tests. It runs under a fixed compute budget: 4 × L4 GPUs and 12 hours for about 120 issues.

| | Budget-Fit (public baseline) | Patchsmith-check (ours) |
|---|---|---|
| Local tasks solved (of 118) | 47.9 | **51.9** (+4.0, 95% CI [+0.9, +7.2]) |
| Runs stopped by a limit, per run | 9.2 | **2.7** |
| Kaggle public score | 0.13 | **0.20** |

Research questions:
1. How noisy is one evaluation?
2. At equal compute, longer runs or more runs plus selection?
3. Does LoRA fine-tuning on solved runs help?
4. Can trace analysis find a change that transfers to hidden tasks?

The work involved more than 15,000 agent runs.

## Files
- `main.pdf`: final report (IEEE format, 8 pages, 27 references)
- `main.tex`, `refs.bib`: report source
- `figs/make_figs_v2.py`: generates every figure from `figs/figdata.json` (data taken from our run logs)
- `figs/v2/`: figures (PDF for the paper, PNG for slides) and `fig_pipeline.tex` (TikZ diagram)
- `slides/presentation_script.md`: talk script for each slide, plus a Q&A
- `slides/deck_preview.html`: open in a browser to view the slides
- `slides/project/`: slide source (HTML/CSS)

## Rebuild
```
cd figs && python make_figs_v2.py
pdflatex main && bibtex main && pdflatex main && pdflatex main
```
