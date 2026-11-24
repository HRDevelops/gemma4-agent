"""New figures for the CS594/794 course report (others are reused from paper/figs and paper2/figs).
usage: python make_figs.py   (run inside course_report/figs)"""
import statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "lines.linewidth": 2,
})

# ---------- Fig A: local proxy vs public leaderboard
subs = [  # name, local mean solved /118, seeds, Kaggle public score
    ("Budget-Fit\n(starter)", 47.9, 10, 0.13),
    ("+ budget guard", 48.8, 5, 0.15),
    ("pub_v6", 47.5, 6, 0.17),
    ("Patchsmith", 50.2, 12, 0.17),
    ("Patchsmith-check\n(ours)", 51.9, 9, 0.20),
]
fig, ax = plt.subplots(figsize=(5.6, 3.9))
for i, (n, x, k, y) in enumerate(subs):
    col = C[1] if "ours" in n else C[0]
    ax.errorbar(x, y, yerr=0.048, fmt="o", color=col, ms=7, capsize=4, lw=1.4, alpha=0.95)
    dx, ha, dy = (0.15, "left", 0.004)
    if n.startswith("pub"): dx, ha = (-0.15, "right")
    if n.startswith("Budget"): dy = -0.03
    if n.startswith("+"): dy = 0.03
    ax.text(x + dx, y + dy, f"{n} (n={k})", fontsize=8, color=INK, ha=ha, va="bottom")
ax.set_xlabel("Local tasks solved (mean over n seeds, of 118)")
ax.set_ylabel("Kaggle public score")
ax.set_xlim(46.5, 53.5); ax.set_ylim(0.05, 0.28)
ax.set_title("Local evaluation vs. public leaderboard", loc="left", fontsize=11)
ax.text(46.65, 0.06, "Error bars: SD of the public score across identical\nsubmissions by other teams (0.048)", fontsize=7.5, color=INK2)
fig.tight_layout(); fig.savefig("fig_lb.png", dpi=220); plt.close(fig)

# ---------- Fig B: Patchsmith-check, per seed + mechanism
ps = {"screen": [54, 51, 50, 53, 51, 46], "fresh": [50, 51, 51, 49, 46, 51]}
pc = {"screen": [55, 53, 56], "fresh": [51, 53, 55, 46, 49, 49]}
fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.9), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axes[0]
rng = np.random.default_rng(0)
for gi, g in enumerate(["screen", "fresh"]):
    for j, (lab, d, col) in enumerate((("Patchsmith", ps, C[0]), ("Patchsmith-check", pc, C[1]))):
        x = gi * 1.0 + (j - 0.5) * 0.36
        v = d[g]
        ax.bar(x, st.mean(v), width=0.32, color=col, alpha=0.9, label=lab if gi == 0 else None)
        ax.scatter(x + rng.uniform(-0.08, 0.08, len(v)), v, color=INK, s=12, zorder=3)
        ax.text(x, max(v) + 0.6, f"{st.mean(v):.1f}", ha="center", fontsize=8.5)
ax.set_xticks([0, 1]); ax.set_xticklabels(["Screen seeds\n(PS 0-5, PC 0-2)", "Fresh seeds 6-11\n(both)"])
ax.set_ylim(40, 60); ax.set_ylabel("Tasks solved (of 118)")
ax.set_title("(a) Solved per seed", loc="left", fontsize=11); ax.grid(axis="x", visible=False)
ax.legend(fontsize=8, loc="lower left", frameon=False)
ax = axes[1]
mets = ["Behaviour check\nafter last edit", "...in failed runs", "pytest as\nfinal check", "Patches with\nscratch files"]
base = [70, 54, 9, 122 / 708 * 100]
ours = [74, 59, 27, 7 / 708 * 100]
x = np.arange(len(mets))
ax.bar(x - 0.18, base, 0.34, color=C[0], label="Patchsmith")
ax.bar(x + 0.18, ours, 0.34, color=C[1], label="Patchsmith-check")
for xi, a, b in zip(x, base, ours):
    ax.text(xi - 0.18, a + 1.2, f"{a:.0f}%", ha="center", fontsize=8)
    ax.text(xi + 0.18, b + 1.2, f"{b:.0f}%", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(mets, fontsize=8.5); ax.set_ylim(0, 88); ax.set_ylabel("Share of runs (%)")
ax.set_title("(b) Behaviour on fresh seeds (708 runs each)", loc="left", fontsize=11); ax.grid(axis="x", visible=False)
ax.legend(fontsize=8, frameon=False)
fig.tight_layout(); fig.savefig("fig_pscheck.png", dpi=220); plt.close(fig)

# ---------- Fig C: failure taxonomy of 30 audited failed Patchsmith runs
cats = [("Underspecified / hidden API", 8), ("Right diagnosis, flawed implementation", 6), ("Misread requirement", 4),
        ("Wrong location", 4), ("Missed verification", 4), ("Edit-tool loops", 3), ("No diagnosis", 1)]
fig, ax = plt.subplots(figsize=(5.6, 3.0))
y = np.arange(len(cats))[::-1]
ax.barh(y, [c[1] for c in cats], color=[C[1] if c[0] in ("Missed verification", "Edit-tool loops") else C[0] for c in cats], height=0.62)
for yi, (_, v) in zip(y, cats): ax.text(v + 0.15, yi, str(v), va="center", fontsize=8.5)
ax.set_yticks(y); ax.set_yticklabels([c[0] for c in cats], fontsize=8.5)
ax.set_xlabel("Failed runs (of 30, stratified sample)"); ax.set_xlim(0, 9.5); ax.grid(axis="y", visible=False)
ax.set_title("Why Patchsmith fails (manual audit)", loc="left", fontsize=11)
fig.tight_layout(); fig.savefig("fig_audit.png", dpi=220); plt.close(fig)
print("ok")
