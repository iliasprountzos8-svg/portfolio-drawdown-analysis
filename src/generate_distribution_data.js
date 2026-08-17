// Runs a real 50,000-trial DCA bootstrap and dumps the FULL raw array of terminal outcomes and
// max drawdowns (not just summary percentiles) so a proper histogram/distribution chart can be
// built from actual simulation output.
const fs = require('fs');
const path = require('path');
const { loadDeepCache, buildBlockIndex } = require('./lib.js');

const ALLOCATION = { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0.0787, GOLD: 0.25, STB: 0.0338 };
const NO_GOLD    = { VWCE: 0.65, ZPRV: 0.30, IDTL: 0.05 };
const TRIALS = 50000;
const YEARS = 30;
const BLOCK_SIZE_MONTHS = 12;
const MONTHLY_CONTRIB = 150;

function simulateBootstrapDCA(aligned, weights, blockStarts, blockSize, totalMonths, monthlyContrib) {
  const assets = Object.keys(weights);
  let holdings = {};
  for (const a of assets) holdings[a] = 0;
  holdings[assets[0]] = 1e-9;
  let peak = 0, maxDD = 0, monthsFilled = 0;

  while (monthsFilled < totalMonths) {
    const start = blockStarts[(Math.random() * blockStarts.length) | 0];
    const len = Math.min(blockSize, totalMonths - monthsFilled);
    for (let k = 0; k < len; k++) {
      let total = 0;
      for (const a of assets) {
        holdings[a] *= (1 + aligned[a][start + k]);
        total += holdings[a];
      }
      if (total > 0) {
        let mostUnder = assets[0], worstDrift = -Infinity;
        for (const a of assets) {
          const drift = weights[a] - holdings[a] / total;
          if (drift > worstDrift) { worstDrift = drift; mostUnder = a; }
        }
        holdings[mostUnder] += monthlyContrib;
        total += monthlyContrib;
      } else {
        holdings[assets[0]] += monthlyContrib;
        total += monthlyContrib;
      }
      if (total > peak) peak = total;
      const dd = peak > 0 ? (peak - total) / peak : 0;
      if (dd > maxDD) maxDD = dd;
    }
    monthsFilled += len;
  }
  const finalValue = Object.values(holdings).reduce((a, b) => a + b, 0);
  return { finalValue, maxDD };
}

function runTrials(cache, weights, trials) {
  const totalMonths = YEARS * 12;
  const blockStarts = buildBlockIndex(cache.dates.length, BLOCK_SIZE_MONTHS);
  const finals = new Array(trials);
  const maxDDs = new Array(trials);
  for (let t = 0; t < trials; t++) {
    const r = simulateBootstrapDCA(cache.aligned, weights, blockStarts, BLOCK_SIZE_MONTHS, totalMonths, MONTHLY_CONTRIB);
    finals[t] = r.finalValue;
    maxDDs[t] = r.maxDD;
  }
  return { finals, maxDDs };
}

function main() {
  const cache = loadDeepCache('historical_cache_deep_full5.json');
  console.log(`Running ${TRIALS} trials for the tested allocation...`);
  const alloc = runTrials(cache, ALLOCATION, TRIALS);
  console.log(`Running ${TRIALS} trials for the no-gold comparison...`);
  const noGold = runTrials(cache, NO_GOLD, TRIALS);

  const totalContributed = MONTHLY_CONTRIB * YEARS * 12;
  const outFile = path.join(__dirname, '..', 'results', 'distribution_data.json');
  fs.writeFileSync(outFile, JSON.stringify({
    trials: TRIALS,
    years: YEARS,
    monthlyContrib: MONTHLY_CONTRIB,
    totalContributed,
    allocation: {
      weights: ALLOCATION,
      finalMultiples: alloc.finals.map(f => f / totalContributed),
      maxDrawdowns: alloc.maxDDs,
    },
    noGoldComparison: {
      weights: NO_GOLD,
      finalMultiples: noGold.finals.map(f => f / totalContributed),
      maxDrawdowns: noGold.maxDDs,
    },
  }));
  console.log(`Saved raw distributions (${TRIALS} trials each, 2 candidates) to ${outFile}`);
}

main();
