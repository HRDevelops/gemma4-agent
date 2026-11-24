"""All data figures of the CS594/794 report in the sci-paper-figures flat style (v2).
Data: figdata.json (dumped from the cluster run logs by dump.py), ../../paper/figs/fig2_data.csv,
fig3_data.csv, ../../paper2/figs/p2_seeds.csv, p2_steps.csv, and the audit / mechanism counts below.
usage: python make_figs_v2.py      (run inside course_report/figs; writes v2/*.pdf and v2/*.png)"""
import csv, json, statistics as st, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path.home() / ".claude/skills/sci-paper-figures/scripts"))
from plot_style import use_style, PAL

use_style(base_size=8)
plt.rcParams.update({"axes.axisbelow": True, "axes.titlesize": 8.5, "axes.titleweight": "bold",
                     "axes.titlelocation": "left", "legend.fontsize": 7})
HERE = Path(__file__).parent
OUT = HERE / "v2"; OUT.mkdir(exist_ok=True)
D = json.load(open(HERE / "figdata.json", encoding="utf-8"))
P1 = HERE.parent.parent / "paper/figs"; P2 = HERE.parent.parent / "paper2/figs"
BASE, OURS, LORA, GREY = PAL["blue"], PAL["orange"], PAL["red"], PAL["grey"]
rng = np.random.default_rng(0)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


def dots(ax, x, vals, color, w=0.12):
    ax.scatter(x + rng.uniform(-w, w, len(vals)), vals, s=9, color="white", edgecolor=color, lw=0.8, zorder=3)


# ---------------------------------------------------------------- Fig 1: baseline -> ours (headline)
cfg = [  # label, runs, source, Kaggle public score
    ("Budget-\nFit", ["baseline", "baseline_holdout"], "public", 0.13),
    ("+ guard", ["short_guard"], "ours", 0.15),
    ("pub_v6", ["pub_v6"], "public", 0.17),
    ("Patch-\nsmith", ["ps_base_12"], "public", 0.17),
    ("PS-check\n(ours)", ["ps_check_9"], "ours", 0.20),
]
fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5), constrained_layout=True,
                         gridspec_kw={"width_ratios": [1.25, 1, 1]})
x = np.arange(len(cfg))
labels = [c[0] for c in cfg]
for ax in axes:
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=6.0); ax.grid(axis="x", visible=False)
ax = axes[0]
for i, (lab, runs, src, lb) in enumerate(cfg):
    solved = sum((D[r]["solved"] for r in runs), [])
    col = OURS if i == len(cfg) - 1 else (BASE if i == 0 else GREY)
    ax.bar(i, st.mean(solved), 0.62, color=col, alpha=0.28 if i not in (0, len(cfg) - 1) else 0.45, edgecolor=col, lw=0.8)
    dots(ax, i, solved, col)
    ax.text(i, max(solved) + 0.7, f"{st.mean(solved):.1f}", ha="center", fontsize=7, color=PAL["ink"])
ax.set_ylim(40, 61.5); ax.set_ylabel("Tasks solved (of 118)")
ax.set_title("(a) Local tasks solved per seed")
ax.annotate("", xy=(4, 59.3), xytext=(0, 59.3), arrowprops=dict(arrowstyle="->", color=PAL["ink"], lw=0.8))
ax.text(2, 59.7, "+4.0 [+0.9, +7.2]", ha="center", fontsize=7)
ax = axes[1]
for i, (lab, runs, src, lb) in enumerate(cfg):
    to = sum((D[r]["timeouts"] for r in runs), [])
    col = OURS if i == len(cfg) - 1 else (BASE if i == 0 else GREY)
    ax.bar(i, st.mean(to), 0.62, color=col, alpha=0.45 if i in (0, 4) else 0.28, edgecolor=col, lw=0.8)
    ax.text(i, st.mean(to) + 0.5, f"{st.mean(to):.1f}", ha="center", fontsize=7)
ax.set_ylim(0, 19); ax.set_ylabel("Runs stopped by a limit (per seed)")
ax.set_title("(b) Wasted runs")
ax = axes[2]
for i, (lab, runs, src, lb) in enumerate(cfg):
    col = OURS if i == len(cfg) - 1 else (BASE if i == 0 else GREY)
    ax.errorbar(i, lb, yerr=0.048, fmt="o", ms=4.5, color=col, mfc="white" if 0 < i < 4 else col,
                capsize=2.5, lw=0.9)
    ax.text(i + 0.14, lb, f"{lb:.2f}", fontsize=7, va="center")
ax.set_ylim(0.05, 0.27); ax.set_ylabel("Kaggle public score")
ax.set_title("(c) Hidden leaderboard")
save(fig, "fig_overview")

# ---------------------------------------------------------------- Fig 2: per-task solve rates (noise)
def cats(rate):
    v = list(rate.values())
    return [sum(r == 0 for r in v), sum(0 < r < .5 for r in v), sum(.5 <= r < 1 for r in v), sum(r == 1 for r in v)]
short, long_ = cats(D["base10_rate"]), cats(D["baseline_long"]["rate"])
names = ["never", "1-49%\nof seeds", "50-99%\nof seeds", "always"]
fig, ax = plt.subplots(figsize=(3.4, 2.1), constrained_layout=True)
xx = np.arange(4)
ax.bar(xx - 0.19, short, 0.36, color=BASE, label="short, 8 min (10 seeds)")
ax.bar(xx + 0.19, long_, 0.36, color=OURS, label="long, 40 min (5 seeds)")
for xi, a, b in zip(xx, short, long_):
    ax.text(xi - 0.19, a + 1, str(a), ha="center", fontsize=6.8); ax.text(xi + 0.19, b + 1, str(b), ha="center", fontsize=6.8)
ax.axvspan(0.5, 2.5, color=PAL["grey_fill"], alpha=0.35, lw=0, zorder=0)
ax.text(1.5, 60, "flipping tasks", ha="center", fontsize=7, color=GREY)
ax.set_xticks(xx); ax.set_xticklabels(names); ax.set_ylabel("Tasks (of 118)"); ax.set_ylim(0, 66)
ax.grid(axis="x", visible=False); ax.legend(loc="upper right", bbox_to_anchor=(1, 0.86))
save(fig, "fig_flip")

# ---------------------------------------------------------------- Fig 3: matched-cost frontier
rows = list(csv.DictReader(open(P1 / "fig2_data.csv", encoding="utf-8")))
fig, ax = plt.subplots(figsize=(3.4, 2.4), constrained_layout=True)
style = {"short (8 min)": (BASE, "o"), "medium (16 min)": (PAL["green"], "s"),
         "long (40 min)": (OURS, "^"), "long + budget-aware prompt": (PAL["teal"], "D")}
for reg, (col, m) in style.items():
    rr = [r for r in rows if r["regime"] == reg]
    xs = [float(r["minutes"]) for r in rr]; ys = [float(r["solved_selected"]) for r in rr]
    ax.plot(xs, ys, marker=m, ms=3.5, color=col, label=reg, lw=1.2)
    ax.annotate("k=1", (xs[0], ys[0]), xytext=(3, -8), textcoords="offset points", fontsize=6, color=col) if reg.startswith("short") else None
ax.set_xlabel("Measured agent minutes per task"); ax.set_ylabel("Tasks solved (selected patch)")
ax.set_ylim(46, 60); ax.legend(loc="lower right", fontsize=6.5)
save(fig, "fig_frontier")

# ---------------------------------------------------------------- Fig 4: selector holdout
rows = []
for line in open(P1 / "fig3_data.csv", encoding="utf-8").read().splitlines()[1:]:
    parts = line.split(","); k, single, sel_, orc, share = parts[-5:]
    rows.append({"selector": ",".join(parts[:-5]), "k": k, "share_pct": share})
fig, ax = plt.subplots(figsize=(3.4, 2.2), constrained_layout=True)
for sel, col, ls, lab in [("R-short, seeds 0–4 (rule chosen here)", BASE, "-", "best rule, seeds 0-4 (chosen here)"),
                          ("R-short, fresh seeds 5–9 (holdout)", OURS, "-", "same rule, fresh seeds 5-9"),
                          ("validity filter only, seeds 5–9", GREY, "--", "validity filter only, seeds 5-9")]:
    rr = [r for r in rows if r["selector"] == sel]
    ax.plot([int(r["k"]) for r in rr], [float(r["share_pct"]) for r in rr], ls, marker="o", ms=3.5, color=col, label=lab)
ax.set_xlabel("Runs per task (k)"); ax.set_ylabel("Oracle headroom recovered (%)")
ax.set_xticks([2, 3, 4, 5]); ax.set_ylim(0, 100); ax.legend(loc="lower left", fontsize=6.5)
save(fig, "fig_holdout")

# ---------------------------------------------------------------- Fig 5: LoRA adapters
seeds = {}
for r in csv.DictReader(open(P2 / "p2_seeds.csv", encoding="utf-8")):
    seeds.setdefault(r["run"], []).append((int(r["solved_118"]), int(r["solved_heldout_24"])))
order = [("pub_v6_k", "31B\nbase", BASE), ("pub_v6_lora_h1", "31B +\nself LoRA", LORA),
         ("pub_v6_lora_q1e1", "31B +\nQwen LoRA", LORA), ("e4b_v6_b", "E4B\nbase", BASE), ("e4b_lora", "E4B +\n31B LoRA", LORA)]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.1), constrained_layout=True, gridspec_kw={"width_ratios": [1.2, 1]})
for ax, j, title, ylim in [(axes[0], 0, "(a) All 118 tasks", 62), (axes[1], 1, "(b) 24 held-out tasks", 20)]:
    for i, (run, lab, col) in enumerate(order):
        v = [s[j] for s in seeds[run]]
        ax.bar(i, st.mean(v), 0.6, color=col, alpha=0.3, edgecolor=col, lw=0.8)
        dots(ax, i, v, col, 0.1)
        ax.text(i, max(v) + ylim * 0.03, f"{st.mean(v):.1f}", ha="center", fontsize=7)
    ax.axvline(2.5, color=PAL["grid"], lw=1.2)
    ax.set_xticks(range(len(order))); ax.set_xticklabels([o[1] for o in order], fontsize=6.8)
    ax.set_ylim(0, ylim); ax.set_title(title); ax.grid(axis="x", visible=False)
axes[0].set_ylabel("Tasks solved per seed")
save(fig, "fig_lora")

# ---------------------------------------------------------------- Fig 6: step length, E4B LoRA loops
tok = {"e4b_v6_b": [], "e4b_lora": []}
for r in csv.DictReader(open(P2 / "p2_steps.csv", encoding="utf-8")):
    if r["run"] in tok: tok[r["run"]].append(int(r["completion_tokens"]))
fig, ax = plt.subplots(figsize=(3.4, 2.1), constrained_layout=True)
bins = np.arange(0, 4400, 100)
ax.hist(tok["e4b_v6_b"], bins, color=PAL["blue_fill"], alpha=0.9, label=f"E4B base (n={len(tok['e4b_v6_b']):,} steps)")
ax.hist(tok["e4b_lora"], bins, histtype="step", color=LORA, lw=1.1, label=f"E4B + 31B LoRA (n={len(tok['e4b_lora']):,})")
ax.set_yscale("log"); ax.set_xlabel("Tokens generated per model step"); ax.set_ylabel("Steps (log)")
ax.axvline(4096, color=GREY, ls="--", lw=0.8); ax.text(4000, 2500, "thinking cap\n4,096", ha="right", fontsize=6.5, color=GREY)
ax.legend(loc="upper center", fontsize=6.5)
save(fig, "fig_steps")

# ---------------------------------------------------------------- Fig 7: audit of 30 failed runs
cats7 = [("Under-specified issue / hidden API", 8), ("Right diagnosis, flawed code", 6), ("Misread requirement", 4),
         ("Wrong location", 4), ("Missed final verification", 4), ("Edit-tool loops", 3), ("No diagnosis", 1)]
fig, ax = plt.subplots(figsize=(3.4, 2.0), constrained_layout=True)
yy = np.arange(len(cats7))[::-1]
proc = ("Missed final verification", "Edit-tool loops")
ax.barh(yy, [c[1] for c in cats7], 0.62, color=[OURS if c[0] in proc else BASE for c in cats7])
for yi, (_, v) in zip(yy, cats7): ax.text(v + 0.15, yi, str(v), va="center", fontsize=7)
ax.set_yticks(yy); ax.set_yticklabels([c[0] for c in cats7], fontsize=6.8); ax.set_xlabel("Failed runs (of 30)")
ax.set_xlim(0, 9.5); ax.grid(axis="y", visible=False)
save(fig, "fig_audit")

# ---------------------------------------------------------------- Fig 8: Patchsmith-check
ps = {"screen": [54, 51, 50, 53, 51, 46], "fresh": [50, 51, 51, 49, 46, 51]}
pc = {"screen": [55, 53, 56], "fresh": [51, 53, 55, 46, 49, 49]}
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.3), constrained_layout=True, gridspec_kw={"width_ratios": [1, 1.5]})
ax = axes[0]
for gi, g in enumerate(["screen", "fresh"]):
    for j, (lab, d, col) in enumerate((("Patchsmith", ps, BASE), ("Patchsmith-check", pc, OURS))):
        xg = gi + (j - 0.5) * 0.36; v = d[g]
        ax.bar(xg, st.mean(v), 0.32, color=col, alpha=0.35, edgecolor=col, lw=0.8, label=lab if gi == 0 else None)
        dots(ax, xg, v, col, 0.06)
        ax.text(xg, max(v) + 0.6, f"{st.mean(v):.1f}", ha="center", fontsize=7)
ax.set_xticks([0, 1]); ax.set_xticklabels(["screen seeds", "fresh seeds 6-11"])
ax.set_ylim(40, 60); ax.set_ylabel("Tasks solved (of 118)"); ax.set_title("(a) Solved per seed")
ax.grid(axis="x", visible=False); ax.legend(loc="lower left", fontsize=6.5)
ax = axes[1]
mets = ["behaviour check\nafter last edit", "... in failed\nruns", "pytest as\nfinal check", "patches with\nscratch files"]
b0 = [70, 54, 9, 122 / 708 * 100]; b1 = [74, 59, 27, 7 / 708 * 100]
xm = np.arange(4)
ax.bar(xm - 0.18, b0, 0.34, color=BASE, label="Patchsmith"); ax.bar(xm + 0.18, b1, 0.34, color=OURS, label="Patchsmith-check")
for xi, a, b in zip(xm, b0, b1):
    ax.text(xi - 0.18, a + 1.5, f"{a:.0f}", ha="center", fontsize=6.8); ax.text(xi + 0.18, b + 1.5, f"{b:.0f}", ha="center", fontsize=6.8)
ax.set_xticks(xm); ax.set_xticklabels(mets, fontsize=6.8); ax.set_ylim(0, 88); ax.set_ylabel("Share of runs (%)")
ax.set_title("(b) Targeted behaviours, fresh seeds (708 runs each)"); ax.grid(axis="x", visible=False); ax.legend(fontsize=6.5)
save(fig, "fig_pscheck")
print("ok", sorted(p.name for p in OUT.iterdir()))
