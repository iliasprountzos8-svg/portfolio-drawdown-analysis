// Real historical block-bootstrap comparison across gold weights (replaces an earlier version
// that used a parametric regime-switching model with assumed returns — inconsistent with the
// rest of this project's real-history methodology). Uses the same runBootstrapCandidate
// (lump-sum) function as final_confidence_10M_trials.js, so all report figures are apples-to-apples.
const fs = require('fs');
const path = require('path');
const { loadDeepCache, buildBlockIndex, runBootstrapCandidate } = require('./lib.js');

const TRIALS = 100000;
const YEARS = 30;
const BLOCK_SIZE_MONTHS = 12;

const CANDIDATES = {
  '0% Gold':  { VWCE: 0.65, ZPRV: 0.30, IDTL: 0.05, GOLD: 0.00, STB: 0.00 },
  '10% Gold': { VWCE: 0.50, ZPRV: 0.15, IDTL: 0.15, GOLD: 0.10, STB: 0.10 },
  '15% Gold': { VWCE: 0.45, ZPRV: 0.15, IDTL: 0.15, GOLD: 0.15, STB: 0.10 },
  '20% Gold': { VWCE: 0.40, ZPRV: 0.15, IDTL: 0.15, GOLD: 0.20, STB: 0.10 },
  '25% Gold (tested allocation)': { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0.0787, GOLD: 0.25, STB: 0.0338 },
};

function main() {
  const cache = loadDeepCache('historical_cache_deep_full5.json');
  const blockStarts = buildBlockIndex(cache.dates.length, BLOCK_SIZE_MONTHS);
  const out = {};
  for (const [label, weights] of Object.entries(CANDIDATES)) {
    console.log(`Running ${TRIALS} trials for ${label}...`);
    const r = runBootstrapCandidate(cache.aligned, blockStarts, weights, TRIALS, YEARS, BLOCK_SIZE_MONTHS);
    out[label] = r;
    console.log(`  median=${r.median.toFixed(2)}x  pDD30=${(r.pDD30 * 100).toFixed(1)}%  pDD50=${(r.pDD50 * 100).toFixed(2)}%  sharpe=${r.sharpe.toFixed(3)}`);
  }
  const outFile = path.join(__dirname, '..', 'results', 'gold_comparison_real.json');
  fs.writeFileSync(outFile, JSON.stringify({ trials: TRIALS, years: YEARS, methodology: 'real historical block-bootstrap, lump-sum, same engine as final_confidence_10M_trials.js', results: out }, null, 2));
  console.log(`Saved to ${outFile}`);
}

main();
