## If uploading the PDF as a document (recommended)

**Document title** (when LinkedIn prompts for one):
Does Gold Reduce Portfolio Crash Risk? A Data Test

**Short caption** (use with the PDF, not the long version below):

Does gold actually lower the chance of a big crash in a long-term portfolio, or is that just something people repeat without checking?

I tested it with a Monte Carlo simulation on real market data back to 1977. Full write-up attached, code and data here: https://github.com/iliasprountzos8-svg/portfolio-drawdown-analysis

Not financial advice, just a personal attempt to test a common claim with real numbers.

#Finance #QuantitativeFinance #PortfolioConstruction #RiskManagement #MonteCarloSimulation

---

## Alternative, longer version (if uploading just an image, not the PDF)

**Hook**
Does gold actually lower the chance of a big crash in a long-term portfolio, or is that just something people repeat without checking?

**What I did**
I built a Monte Carlo simulation (Node.js, no external libraries) using real historical monthly returns going back to 1977, and tested a portfolio of 51% global stocks, 12.75% small-cap value stocks, 7.87% long-term bonds, 25% gold, and 3.38% short-term bonds over a 30-year period.

**Findings**
→ Chance of losing 50% or more, ever: about 2.5 to 2.6%, vs. about 11.5% for the same portfolio with no gold
→ Median 30-year outcome: about 31x on invested capital, Sharpe ratio about 0.95
→ Stable result across every starting decade I tested (1970s, 1980s, 1990s), not just one lucky window

**One honest caveat**
Most of the benefit comes from the first 10% of gold you add. After that it flattens out, and it's not perfectly consistent (20% gold actually tests a bit better than 25% on drawdown risk in this data). I went with 25% because it has the best Sharpe ratio of what I tested, not because more gold is always better.

**Link**
Full code, data, and a short written report: https://github.com/iliasprountzos8-svg/portfolio-drawdown-analysis

**Disclaimer + hashtags**
Not financial advice, just a personal attempt to test a common claim with real data.

#Finance #QuantitativeFinance #PortfolioConstruction #RiskManagement #MonteCarloSimulation

---

## Ready-to-post version (paste this)

Does gold actually lower the chance of a big crash in a long-term portfolio, or is that just something people repeat without checking?

I built a Monte Carlo simulation (Node.js, no external libraries) using real historical monthly returns going back to 1977, and tested a portfolio of 51% global stocks, 12.75% small-cap value stocks, 7.87% long-term bonds, 25% gold, and 3.38% short-term bonds over a 30-year period.

Findings, checked across several independent runs:

→ Chance of losing 50% or more, ever: about 2.5 to 2.6%, vs. about 11.5% for the same portfolio with no gold
→ Median 30-year outcome: about 31x on invested capital, Sharpe ratio about 0.95
→ Stable result across every starting decade I tested (1970s, 1980s, 1990s), not just one lucky window

One honest caveat: most of the benefit comes from the first 10% of gold you add. After that it flattens out, and it's not perfectly consistent (20% gold actually tests a bit better than 25% on drawdown risk in this data). I went with 25% because it has the best Sharpe ratio of what I tested, not because more gold is always better.

Full code, data, and a short written report: https://github.com/iliasprountzos8-svg/portfolio-drawdown-analysis

Not financial advice, just a personal attempt to test a common claim with real data.

#Finance #QuantitativeFinance #PortfolioConstruction #RiskManagement #MonteCarloSimulation
