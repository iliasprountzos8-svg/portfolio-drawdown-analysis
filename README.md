# Does Gold Reduce the Risk of a Big Crash in a Long-Term Portfolio?

People often say gold protects a portfolio from a bad crash, but I wanted to actually check that instead of assuming it. I built a Monte Carlo simulation using real historical monthly returns going back to 1977, and tested a portfolio made of 51% global stocks, 12.75% small-cap value stocks, 7.87% long-term bonds, 25% gold, and 3.38% short-term bonds over a 30-year period.

This repo has the code, the data, and the full method. Not a "buy this allocation" pitch, just an attempt to test a common claim with real data.

> **Not financial advice.** Personal research project for education purposes. Simulated historical results do not guarantee anything about the future.

## Method

- **Block bootstrap Monte Carlo**: real historical monthly-return blocks are resampled and stitched into simulated 30-year paths, instead of assuming returns are normally distributed.
- **Real historical data back to 1977** across global stocks, US small-cap value, long-term government bonds, gold, and short-term government bonds.
- **Walk-forward check**: tested against all 199 real overlapping 30-year windows in the dataset (1977 to 2023), not just random simulations from one starting point.
- **Interest rate check**: split history into rising, falling, and flat rate periods to see if the bonds still help no matter what rates are doing.
- **Double-checked**: every number below was reproduced across 6+ independent runs (100,000 to 1,000,000 trials each) before I trusted it.

## Key findings

For the tested allocation (51% global stocks / 12.75% small-cap value / 7.87% long-term bonds / 25% gold / 3.38% short-term bonds), lump-sum bootstrap:

| Metric | Result |
|---|---|
| Chance of losing 50% or more, ever | ~2.5 to 2.6% |
| Median 30-year outcome | ~31.4 to 31.6x on invested capital |
| Sharpe ratio | ~0.95 |
| Stability across starting decades (1970s/80s/90s), walk-forward | Consistent: 52x / 30x / 22x medians, not a single-window fluke |

Gold's job here is lowering the chance of a really bad crash, not boosting returns. Going from 0% to 10% gold drops the chance of losing 50%+ from about 11.5% to about 2.6%. That's most of the benefit right there. Past 10%, adding more gold doesn't help much more, and the relationship isn't perfectly consistent (20% gold actually tests slightly better than 25% on drawdown risk in this dataset). I still went with 25% because it has the best Sharpe ratio of the range I tested, not because more gold is always better.

Long-term bonds also depend on the rate environment. Splitting history into rate-hiking, rate-cutting, and flat periods shows the bond sleeve genuinely helping during cutting and flat periods, and being roughly a wash during hiking periods.

## What this doesn't cover

- This is a simulation based on the past. It can't predict something that has never happened before, only test against what already has.
- I kept the ratio between the other assets fixed while testing different gold weights. I didn't re-optimize every weight at once.
- Taxes and fees are estimates and depend on where you live. Real results will differ per person.

## Repo structure

```
src/                                   Analysis engine
  lib.js                               Shared simulation primitives (block bootstrap, DCA, drawdown tracking)
  build_deep_history.js                Historical data pipeline (methodology reference)
  dca_bootstrap_30yr.js                Dollar-cost-averaging bootstrap
  walkforward_validation.js            199-window walk-forward test across real history
  grid_search_overfitting_check.js     3D grid search around the tested allocation
  generate_gold_comparison_real.js     Gold-weight comparison, real historical bootstrap
  rate_regime_conditional_test.js      Rate-hiking/cutting/flat regime split
  final_confidence_10M_trials.js       Confidence run on the tested allocation
  generate_distribution_data.js        Raw terminal-outcome and drawdown distributions (50,000 trials)
  generate_fan_chart_data.js           Full monthly-path generation for the fan chart
  generate_charts.py / generate_charts_gr.py   Chart generation (matplotlib), English and Greek labels
  generate_report_pdf.py / generate_report_pdf_gr.py   4-page report generation (reportlab), English and Greek
data/
  historical_cache_deep_full5.json     Historical return series (stocks/value/bonds/gold/cash), ready to run against
results/
  charts/, charts_gr/                  Generated PNG charts
  *.json, *.csv                        Raw output from each script above
Portfolio_Drawdown_Research_Note.pdf       Short written report, English
Portfolio_Drawdown_Research_Note_GR.pdf    Short written report, Greek
```

## Running it

Node.js (no external dependencies) for the simulations, Python (numpy/matplotlib/reportlab) for the charts and report:

```bash
node src/final_confidence_10M_trials.js
node src/walkforward_validation.js
node src/generate_gold_comparison_real.js
python src/generate_charts.py
python src/generate_report_pdf.py
```

Each Node script reads `data/historical_cache_deep_full5.json` and writes its results to `results/`.

## Data sources

Monthly return series built from publicly available historical price data for the relevant asset classes (global stocks, US small-cap value, long-term government bonds, gold, short-term government bonds), 1977 onward. See `src/build_deep_history.js` for the full construction method.
