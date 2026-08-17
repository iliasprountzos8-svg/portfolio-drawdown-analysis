Does gold meaningfully reduce catastrophic drawdown risk in a long-horizon equity portfolio, or is that conventional wisdom nobody actually tests?

I built a block-bootstrap Monte Carlo engine (Node.js, no external libraries) against real historical monthly returns back to 1977, and tested a 51% global equities / 12.75% small-cap value / 7.87% long-duration bonds / 25% gold / 3.38% short-term bonds allocation across a 30-year horizon.

Findings, verified across repeated independent bootstrap runs:

→ P(portfolio ever draws down ≥50%): ≈2.5–2.6%, vs. ≈11.5% for the same portfolio with no gold
→ Median 30-year outcome: ≈31x on invested capital, Sharpe ratio ≈0.95
→ Result is stable across every starting decade tested (1970s, 1980s, 1990s), not a single lucky window

One finding worth being precise about: the risk reduction is front-loaded, not linear. Moving from 0% to 10% gold captures most of the benefit; beyond that, the drawdown-risk curve flattens and isn't strictly monotonic — 20% gold tests marginally better than 25% on tail risk in this dataset. The case for 25% rests on it carrying the best Sharpe ratio of the range tested, not on "more gold is always better."

The part I'd flag as more important than any of the numbers above: while packaging this for publication, I found that an earlier "confirmed" result from the same codebase didn't reproduce against current data — a data file had been silently regenerated after the confirmation run that cited it, and nobody re-ran the check. Re-running the identical, unmodified script against today's data gave materially different numbers. The figures in this post are the re-verified ones. I think that failure mode — a result quietly going stale after the underlying data changes — is worth naming explicitly rather than glossing over, because it's an easy trap in any analysis pipeline, not just this one.

Full methodology, code, and a short write-up: https://github.com/iliasprountzos8-svg/portfolio-drawdown-analysis

Not financial advice — a research exercise in taking a common claim and actually testing it against real data.

#Finance #QuantitativeFinance #PortfolioConstruction #RiskManagement #MonteCarloSimulation
