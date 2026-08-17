"""
Generates professional, print-quality charts (equity-research style) from the real
Monte Carlo output in results/*.json and results/*.csv. Output: results/charts/*.png,
300 DPI, sized for both the PDF report and standalone LinkedIn upload.
"""
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')
OUT = os.path.join(RESULTS, 'charts')
os.makedirs(OUT, exist_ok=True)

# --- Professional palette: navy / slate / muted gold accent ---
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
# Chart 1: Distribution histogram of 30-year terminal outcome
# =========================================================================
with open(os.path.join(RESULTS, 'distribution_data.json')) as f:
    dist = json.load(f)

finals = np.array(dist['allocation']['finalMultiples'])
median = np.percentile(finals, 50)
p5 = np.percentile(finals, 5)
p95 = np.percentile(finals, 95)

fig, ax = plt.subplots(figsize=(6.5, 3.6))
# Clip the top 1% for display so one extreme tail doesn't compress the whole histogram
display_max = np.percentile(finals, 99)
clipped = finals[finals <= display_max]
ax.hist(clipped, bins=70, color=NAVY, alpha=0.85, edgecolor='white', linewidth=0.3)
ax.axvline(median, color=GOLD, linewidth=1.6, linestyle='-', label=f'Median: {median:.1f}x')
ax.axvline(p5, color=SLATE, linewidth=1.2, linestyle='--', label=f'5th pct.: {p5:.1f}x')
ax.axvline(p95, color=SLATE, linewidth=1.2, linestyle='--', label=f'95th pct.: {p95:.1f}x')
ax.set_xlabel('Terminal value, multiple of contributed capital (30-year horizon)')
ax.set_ylabel('Trials (of 50,000)')
# (title removed — captioned externally in report/HTML)
ax.legend(frameon=False, fontsize=8, loc='upper right')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savefig(fig, 'distribution_histogram.png')

# =========================================================================
# Chart 2: Fan chart — percentile bands over time
# =========================================================================
with open(os.path.join(RESULTS, 'fan_chart_paths.json')) as f:
    fan = json.load(f)

paths = np.array(fan['paths'])  # trials x points
n_points = fan['pointsPerPath']
years = np.linspace(0, fan['years'], n_points)
p10 = np.percentile(paths, 10, axis=0)
p50 = np.percentile(paths, 50, axis=0)
p90 = np.percentile(paths, 90, axis=0)

fig, ax = plt.subplots(figsize=(6.5, 3.6))
# Light spaghetti underlay (subsample for print clarity)
subsample = paths[::10]
for p in subsample:
    ax.plot(years, p, color=NAVY, alpha=0.05, linewidth=0.5)
ax.fill_between(years, p10, p90, color=NAVY, alpha=0.12, label='10th–90th percentile range')
ax.plot(years, p50, color=NAVY, linewidth=2.0, label='Median simulated path')
ax.set_xlabel('Years')
ax.set_ylabel('Portfolio value (€, illustrative €150/mo contribution)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
# (title removed — captioned externally in report/HTML)
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savefig(fig, 'fan_chart.png')

# =========================================================================
# Chart 3: Median outcome & drawdown risk by gold allocation (real historical
# block-bootstrap, lump-sum, same engine/methodology as every other chart here)
# =========================================================================
with open(os.path.join(RESULTS, 'gold_comparison_real.json')) as f:
    goldcmp = json.load(f)['results']

gold_labels = ['0% Gold', '10% Gold', '15% Gold', '20% Gold', '25% Gold\n(tested)']
gold_keys = ['0% Gold', '10% Gold', '15% Gold', '20% Gold', '25% Gold (tested allocation)']
gold_median = [goldcmp[k]['median'] for k in gold_keys]
gold_dd50 = [goldcmp[k]['pDD50'] * 100 for k in gold_keys]

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
x = np.arange(len(gold_labels))

axes[0].bar(x, gold_median, color=NAVY, width=0.6)
axes[0].set_xticks(x)
axes[0].set_xticklabels(gold_labels, fontsize=7.5, rotation=20, ha='right')
axes[0].set_ylabel('Median multiple (30yr)')
axes[0].set_title('Median Outcome', fontsize=9.5, fontweight='bold', color=INK, loc='left')
axes[0].spines[['top', 'right']].set_visible(False)
for i, v in enumerate(gold_median):
    axes[0].text(i, v + np.max(gold_median) * 0.015, f'{v:.1f}x', ha='center', fontsize=7.5, color=INK)

axes[1].bar(x, gold_dd50, color=GOLD, width=0.6)
axes[1].set_xticks(x)
axes[1].set_xticklabels(gold_labels, fontsize=7.5, rotation=20, ha='right')
axes[1].set_ylabel('P(drawdown ≥ 50%)')
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter())
axes[1].set_title('Drawdown Risk', fontsize=9.5, fontweight='bold', color=INK, loc='left')
axes[1].spines[['top', 'right']].set_visible(False)
for i, v in enumerate(gold_dd50):
    axes[1].text(i, v + np.max(gold_dd50) * 0.03, f'{v:.2f}%', ha='center', fontsize=7.5, color=INK)

# (suptitle removed — captioned externally in report/HTML)
fig.tight_layout()
savefig(fig, 'gold_comparison.png')

# =========================================================================
# Chart 4: Outcome stability across starting decades (real CSV data)
# =========================================================================
rows = []
with open(os.path.join(RESULTS, 'walkforward_full_results.csv')) as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

def decade_median(candidate, decade):
    vals = [float(r['final_multiple']) for r in rows if r['candidate'] == candidate and r['start_decade'] == decade]
    return float(np.median(vals))

candidates = [('allocation_noGoldEquiv', 'Tested allocation'), ('A_Current', 'Current (0% gold)'), ('G15_noGoldEquiv', 'G15 (15% gold, no SCV)')]
decades = ['1970s', '1980s', '1990s']
data = {label: [decade_median(cand, d) for d in decades] for cand, label in candidates}

fig, ax = plt.subplots(figsize=(6.5, 3.4))
x = np.arange(len(decades))
width = 0.26
colors = [NAVY, SLATE, GOLD]
for i, (label, vals) in enumerate(data.items()):
    ax.bar(x + (i - 1) * width, vals, width=width, label=label, color=colors[i])

ax.set_xticks(x)
ax.set_xticklabels([f'{d} starts' for d in decades])
ax.set_ylabel('Median 30-year multiple')
# (title removed — captioned externally in report/HTML)
ax.legend(frameon=False, fontsize=7.5, loc='upper right')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savefig(fig, 'decade_stability.png')

print('All charts generated.')
