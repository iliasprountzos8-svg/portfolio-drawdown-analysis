// Generates full monthly value paths for N Monte Carlo trials (not just summary stats) so they
// can be plotted as a "spaghetti"/fan chart. Uses the same block-bootstrap DCA mechanics as
// simulateBootstrapDCA in lib.js, but records the path instead of just the final value.
const fs = require('fs');
const path = require('path');
const { loadDeepCache, buildBlockIndex } = require('./lib.js');

const CANDIDATE = { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0.0787, GOLD: 0.25, STB: 0.0338 }; // the allocation
const TRIALS = 300;
const YEARS = 30;
const BLOCK_SIZE_MONTHS = 12;
const MONTHLY_CONTRIB = 150; // illustrative contribution level, not a real personal figure

function simulateBootstrapDCAWithPath(aligned, weights, blockStarts, blockSize, totalMonths, monthlyContrib) {
  const assets = Object.keys(weights);
  let holdings = {};
  for (const a of assets) holdings[a] = 0;
  holdings[assets[0]] = 1e-9;
  let monthsFilled = 0;
  const path_ = [];

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
      path_.push(total);
    }
    monthsFilled += len;
  }
  return path_;
}

function main() {
  const cache = loadDeepCache('historical_cache_deep_full5.json');
  const totalMonths = YEARS * 12;
  const blockStarts = buildBlockIndex(cache.dates.length, BLOCK_SIZE_MONTHS);

  console.log(`Generating ${TRIALS} full monthly paths, ${YEARS}yr horizon, the allocation weights...`);
  const paths = [];
  for (let t = 0; t < TRIALS; t++) {
    paths.push(simulateBootstrapDCAWithPath(cache.aligned, CANDIDATE, blockStarts, BLOCK_SIZE_MONTHS, totalMonths, MONTHLY_CONTRIB));
    if ((t + 1) % 50 === 0) console.log(`  ${t + 1}/${TRIALS} trials done`);
  }

  // Downsample to quarterly points to keep the output/SVG light (still 120 points per line).
  const downsampled = paths.map(p => p.filter((_, i) => i % 3 === 0));

  const outFile = path.join(__dirname, '..', 'results', 'fan_chart_paths.json');
  fs.writeFileSync(outFile, JSON.stringify({
    candidate: 'the allocation',
    weights: CANDIDATE,
    trials: TRIALS,
    years: YEARS,
    monthlyContrib: MONTHLY_CONTRIB,
    note: 'monthlyContrib is illustrative, not a real personal figure',
    pointsPerPath: downsampled[0].length,
    paths: downsampled,
  }));
  console.log(`Saved ${TRIALS} paths to ${outFile}`);
}

main();
