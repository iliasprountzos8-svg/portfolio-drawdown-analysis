# Does Gold Reduce Catastrophic Drawdown Risk in a Long-Horizon Portfolio? A Real-History Monte Carlo Test

**Question:** a stock-heavy portfolio compounds well on average but carries real tail risk — the kind of ≥50% drawdown that can permanently derail a 20–30 year plan if it forces a sale near the bottom. Gold is the conventional answer to that risk. This project tests it directly: how much gold, combined with what else, actually moves catastrophic-drawdown probability, and at what cost to expected return.

This repo is the methodology, the code, and an honest account of the mistakes caught along the way — including a live data-integrity issue found and corrected the same week this was written. Not a "buy this allocation" pitch.

> **Not financial advice.** Personal research project for educational purposes. Simulated historical backtests do not guarantee future results.

## Method

- **Block bootstrap Monte Carlo**: real historical monthly-return blocks are resampled and stitched into simulated 30-year paths, preserving real sequencing and volatility clustering rather than assuming normally distributed returns.
- **Real historical data back to 1977** across global equities, US small-cap value, long-duration government bonds, gold, and short-term government bonds.
- **Walk-forward validation** across all 199 overlapping real 30-year windows in the dataset (1977–2023), not a single starting date.
- **Regime-conditional testing** — splitting history into rate-hiking, rate-cutting, and flat periods to check whether the bond sleeve's benefit depends on the regime.
- **Repeated independent verification**: every headline figure below was reproduced across 6+ independent bootstrap runs (100,000 to 1,000,000 trials each) rather than accepted from a single run.

## Two real mistakes, caught and corrected

Rigor mattered more than a clean story:

- **An overfitting trap, caught before it became a conclusion.** An early grid search kept surfacing near-zero-small-cap-value candidates with the best in-sample Sharpe ratio and median outcome. Testing that candidate out-of-sample against the full 1977–2023 history showed it collapsing well below a straightforward baseline — the "winner" was an artifact of small-cap value's specific underperformance in the shorter test window, not a real edge. Discarded.
- **A stale-data bug, caught while packaging this project for publication — after the underlying research had already been relied on for a real decision.** An earlier version of one "safe asset" series was mis-mapped to the wrong underlying factor and later corrected, but the correction wasn't propagated back through a final confirmation run before its headline numbers were treated as settled. Re-running the identical, unmodified script against current data produced materially different figures. This is the version of the numbers below — verified against data that actually exists on disk today, not a number carried forward without being re-checked.

## Key findings

For the tested allocation (51% global equities / 12.75% small-cap value / 7.87% long-duration bonds / 25% gold / 3.38% short-term bonds), lump-sum bootstrap, verified across repeated independent runs:

| Metric | Result |
|---|---|
| P(portfolio ever draws down ≥50%) | **≈2.5–2.6%** |
| Median 30-year outcome multiple | **≈31.4–31.6x** on invested capital |
| Sharpe ratio | **≈0.95** |
| Stability across starting decades (1970s/80s/90s), walk-forward | Consistent — 52x / 30x / 22x medians, not a single-window fluke |

**Gold's job is tail-risk reduction, and the effect is real but not perfectly monotonic.** Moving from 0% to 10% gold cuts P(≥50% drawdown) from ≈11.5% to ≈2.6% — the large majority of the benefit shows up early. Beyond 10%, the risk curve is roughly flat and not strictly decreasing with more gold (20% gold tests marginally lower drawdown risk than 25% in this dataset). The honest read: **10–25% gold captures essentially all of the tail-risk benefit available in this dataset**; the tested 25% allocation carries the best Sharpe ratio of the range tested, which is the basis for it rather than a claim that more gold is unconditionally better.

**Bond duration matters by rate regime, not universally.** Splitting history into rate-hiking, rate-cutting, and flat periods shows the long-duration bond sleeve genuinely helping during cutting and flat regimes and being roughly a wash during hiking regimes — it earns its place across a full cycle rather than being a permanent drag or boost.

## A resolved question: is a smaller bond sleeve better?

An earlier finding suggested a smaller bond allocation (~5% vs. the tested 15%) could beat this allocation on median outcome and worst-case outcome. Re-testing that comparison under a full realism gauntlet — lump-sum, realistic dollar-cost-averaged contributions, after fund fees and withholding tax, and conditioned on starting only from historically expensive (high-valuation) markets — the smaller-bond-sleeve alternative **loses on drawdown risk in every single test**, and loses outright on median outcome once realistic costs are applied. The larger bond sleeve earns its keep; this is not a free optimization sitting on the table.

## Repo structure

```
src/                                   Analysis engine
  lib.js                               Shared simulation primitives (block bootstrap, DCA, drawdown tracking)
  build_deep_history.js                Historical data pipeline (methodology reference)
  dca_bootstrap_30yr.js                Dollar-cost-averaging bootstrap
  walkforward_validation.js            199-window walk-forward test across real history
  grid_search_overfitting_check.js     The 3D grid search, including the overfitting catch above
  generate_gold_comparison_real.js     Gold-weight comparison, real historical bootstrap (not a parametric model)
  rate_regime_conditional_test.js      Rate-hiking/cutting/flat regime split
  final_confidence_10M_trials.js       Confidence run on the tested allocation
  generate_distribution_data.js        Raw terminal-outcome and drawdown distributions (50,000 trials)
  generate_fan_chart_data.js           Full monthly-path generation for the fan chart
  generate_charts.py                   Chart generation (matplotlib) from the JSON/CSV output above
data/
  historical_cache_deep_full5.json     Historical return series (equities/value/bonds/gold/cash), ready to run against
results/
  charts/                              Generated PNG charts
  *.json, *.csv                        Raw output from each script above
```

## Running it

Node.js (no external dependencies) for the simulations, Python (numpy/matplotlib) for the charts:

```bash
node src/final_confidence_10M_trials.js
node src/walkforward_validation.js
node src/generate_gold_comparison_real.js
python src/generate_charts.py
```

Each Node script reads `data/historical_cache_deep_full5.json` and writes its results to `results/`.

## Data sources

Monthly return series built from publicly available historical price data for the relevant asset classes (global equities, US small-cap value, long-duration government bonds, gold, short-term government bonds), 1977 onward. See `src/build_deep_history.js` for the full construction methodology.
