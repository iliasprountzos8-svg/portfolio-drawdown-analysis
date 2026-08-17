"""
Greek-labeled version of generate_charts.py, for the Greek PDF report only. Same data,
same methodology, translated axis labels/legends. Output: results/charts_gr/*.png.
"""
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')
OUT = os.path.join(RESULTS, 'charts_gr')
os.makedirs(OUT, exist_ok=True)

NAVY = '#1F3A5F'
SLATE = '#6B7280'
GOLD = '#B08D57'
LIGHT_GRID = '#E5E7EB'
INK = '#111827'
BG = '#FFFFFF'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.edgecolor': '#D1D5DB',
    'axes.linewidth': 0.8,
    'axes.grid': True,
    'grid.color': LIGHT_GRID,
    'grid.linewidth': 0.6,
    'axes.axisbelow': True,
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'text.color': INK,
    'axes.labelcolor': INK,
    'xtick.color': SLATE,
    'ytick.color': SLATE,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
})

def savefig(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor=BG)
    print(f'  saved {name}')
    plt.close(fig)

# =========================================================================
# Chart 1: Distribution histogram
# =========================================================================
with open(os.path.join(RESULTS, 'distribution_data.json')) as f:
    dist = json.load(f)

finals = np.array(dist['allocation']['finalMultiples'])
median = np.percentile(finals, 50)
p5 = np.percentile(finals, 5)
p95 = np.percentile(finals, 95)

fig, ax = plt.subplots(figsize=(6.5, 3.6))
display_max = np.percentile(finals, 99)
clipped = finals[finals <= display_max]
ax.hist(clipped, bins=70, color=NAVY, alpha=0.85, edgecolor='white', linewidth=0.3)
ax.axvline(median, color=GOLD, linewidth=1.6, linestyle='-', label=f'Διάμεσος: {median:.1f}x')
ax.axvline(p5, color=SLATE, linewidth=1.2, linestyle='--', label=f'5ο εκατοστημόριο: {p5:.1f}x')
ax.axvline(p95, color=SLATE, linewidth=1.2, linestyle='--', label=f'95ο εκατοστημόριο: {p95:.1f}x')
ax.set_xlabel('Τελική αξία, πολλαπλάσιο του επενδυμένου κεφαλαίου (ορίζοντας 30 ετών)')
ax.set_ylabel('Προσομοιώσεις (από 50.000)')
ax.legend(frameon=False, fontsize=8, loc='upper right')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savefig(fig, 'distribution_histogram.png')

# =========================================================================
# Chart 2: Fan chart
# =========================================================================
with open(os.path.join(RESULTS, 'fan_chart_paths.json')) as f:
    fan = json.load(f)

paths = np.array(fan['paths'])
n_points = fan['pointsPerPath']
years = np.linspace(0, fan['years'], n_points)
p10 = np.percentile(paths, 10, axis=0)
p50 = np.percentile(paths, 50, axis=0)
p90 = np.percentile(paths, 90, axis=0)

fig, ax = plt.subplots(figsize=(6.5, 3.6))
subsample = paths[::10]
for p in subsample:
    ax.plot(years, p, color=NAVY, alpha=0.05, linewidth=0.5)
ax.fill_between(years, p10, p90, color=NAVY, alpha=0.12, label='Εύρος 10ου–90ού εκατοστημορίου')
ax.plot(years, p50, color=NAVY, linewidth=2.0, label='Διάμεση προσομοιωμένη πορεία')
ax.set_xlabel('Έτη')
ax.set_ylabel('Αξία χαρτοφυλακίου (€, ενδεικτική συνεισφορά €150/μήνα)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savefig(fig, 'fan_chart.png')

# =========================================================================
# Chart 3: Gold comparison
# =========================================================================
with open(os.path.join(RESULTS, 'gold_comparison_real.json')) as f:
    goldcmp = json.load(f)['results']

gold_labels = ['0% Χρυσός', '10% Χρυσός', '15% Χρυσός', '20% Χρυσός', '25% Χρυσός\n(δοκιμασμένη)']
gold_keys = ['0% Gold', '10% Gold', '15% Gold', '20% Gold', '25% Gold (tested allocation)']
gold_median = [goldcmp[k]['median'] for k in gold_keys]
gold_dd50 = [goldcmp[k]['pDD50'] * 100 for k in gold_keys]

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
x = np.arange(len(gold_labels))

axes[0].bar(x, gold_median, color=NAVY, width=0.6)
axes[0].set_xticks(x)
axes[0].set_xticklabels(gold_labels, fontsize=7.5, rotation=20, ha='right')
axes[0].set_ylabel('Διάμεσο πολλαπλάσιο (30 έτη)')
axes[0].set_title('Διάμεσο Αποτέλεσμα', fontsize=9.5, fontweight='bold', color=INK, loc='left')
axes[0].spines[['top', 'right']].set_visible(False)
for i, v in enumerate(gold_median):
    axes[0].text(i, v + np.max(gold_median) * 0.015, f'{v:.1f}x', ha='center', fontsize=7.5, color=INK)

axes[1].bar(x, gold_dd50, color=GOLD, width=0.6)
axes[1].set_xticks(x)
axes[1].set_xticklabels(gold_labels, fontsize=7.5, rotation=20, ha='right')
axes[1].set_ylabel('Π(πτώση ≥ 50%)')
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter())
axes[1].set_title('Κίνδυνος Πτώσης', fontsize=9.5, fontweight='bold', color=INK, loc='left')
axes[1].spines[['top', 'right']].set_visible(False)
for i, v in enumerate(gold_dd50):
    axes[1].text(i, v + np.max(gold_dd50) * 0.03, f'{v:.2f}%', ha='center', fontsize=7.5, color=INK)

fig.tight_layout()
savefig(fig, 'gold_comparison.png')

# =========================================================================
# Chart 4: Decade stability
# =========================================================================
rows = []
with open(os.path.join(RESULTS, 'walkforward_full_results.csv')) as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

def decade_median(candidate, decade):
    vals = [float(r['final_multiple']) for r in rows if r['candidate'] == candidate and r['start_decade'] == decade]
    return float(np.median(vals))

candidates = [('allocation_noGoldEquiv', 'Δοκιμασμένη κατανομή'), ('A_Current', 'Τρέχουσα (0% χρυσός)'), ('G15_noGoldEquiv', 'G15 (15% χρυσός, χωρίς SCV)')]
decades = ['1970s', '1980s', '1990s']
data = {label: [decade_median(cand, d) for d in decades] for cand, label in candidates}

fig, ax = plt.subplots(figsize=(6.5, 3.4))
x = np.arange(len(decades))
width = 0.26
colors = [NAVY, SLATE, GOLD]
for i, (label, vals) in enumerate(data.items()):
    ax.bar(x + (i - 1) * width, vals, width=width, label=label, color=colors[i])

ax.set_xticks(x)
ax.set_xticklabels([f'Εκκίνηση δεκαετίας {d}' for d in decades])
ax.set_ylabel('Διάμεσο πολλαπλάσιο 30ετίας')
ax.legend(frameon=False, fontsize=7.5, loc='upper right')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savefig(fig, 'decade_stability.png')

print('All Greek charts generated.')
