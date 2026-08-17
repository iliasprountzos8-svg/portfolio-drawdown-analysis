// Overnight test 4: regime-conditional bootstrap. Classifies every month in the long no-gold
// cache (1977-2023) into rate-hiking / rate-cutting / flat based on the trailing 12-month change
// in the 10yr yield (from Shiller's GS10 series, raw_data/ie_data_converted.csv), then runs the
// block bootstrap separately within each regime's blocks only. Directly tests whether IDTL
// (long-duration bond sleeve) actually helps or hurts depending on the rate regime, by comparing
// the allocation-noGoldEquiv against a variant with IDTL's weight moved into STB (duration-free).
//
// Run: node overnight_regime_test.js

const fs = require('fs');
const path = require('path');
const { loadDeepCache, runBootstrapCandidate } = require('./lib.js');

const TRIALS = 100000;
const YEARS = 15; // shorter horizon than 30yr since regime blocks are scarcer than full history
const BLOCK_SIZE_MONTHS = 12;
const HIKE_THRESHOLD = 0.5;  // pp change over trailing 12mo to call it "hiking"
const CUT_THRESHOLD = -0.5;

const CANDIDATES = {
  'allocation_noGoldEquiv (has IDTL)': { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0.0787, STB: 0.3038 },
  'FortressAllocation_IDTLtoSTB (no duration)': { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0, STB: 0.3825 },
};

function loadGS10ByDate() {
  const lines = fs.readFileSync(path.join(__dirname, 'raw_data', 'ie_data_converted.csv'), 'utf8').trim().split('\n').slice(1);
  const map = new Map();
  for (const l of lines) {
    const [dateFrac, P, D, E, CPI, GS10] = l.split(',');
    if (!GS10) continue;
    const year = Math.floor(parseFloat(dateFrac));
    const month = Math.round((parseFloat(dateFrac) - year) * 100);
    const dateStr = `${year}-${String(month).padStart(2, '0')}`;
    map.set(dateStr, parseFloat(GS10));
  }
  return map;
}

function classifyRegimes(dates, gs10ByDate) {
  const regimes = new Array(dates.length).fill('flat');
  for (let i = 12; i < dates.length; i++) {
    const now = gs10ByDate.get(dates[i]);
    const prior = gs10ByDate.get(dates[i - 12]);
    if (now == null || prior == null) continue;
    const delta = now - prior;
    if (delta >= HIKE_THRESHOLD) regimes[i] = 'hiking';
    else if (delta <= CUT_THRESHOLD) regimes[i] = 'cutting';
    else regimes[i] = 'flat';
  }
  return regimes;
}

// Block starts restricted to blocks whose START month falls in the given regime.
function buildRegimeBlockIndex(regimes, blockSize, wantRegime) {
  const starts = [];
  for (let i = 0; i <= regimes.length - blockSize; i++) {
    if (regimes[i] === wantRegime) starts.push(i);
  }
  return starts;
}

function main() {
  const cache = loadDeepCache('historical_cache_deep_noGold4.json');
  const { aligned, dates } = cache;
  const gs10ByDate = loadGS10ByDate();
  const regimes = classifyRegimes(dates, gs10ByDate);

  const counts = { hiking: 0, cutting: 0, flat: 0 };
  for (const r of regimes) counts[r]++;
  console.log(`Regime classification over ${dates.length} months (${dates[0]} -> ${dates[dates.length - 1]}):`);
  console.log(`  hiking=${counts.hiking} (${(counts.hiking / dates.length * 100).toFixed(1)}%), cutting=${counts.cutting} (${(counts.cutting / dates.length * 100).toFixed(1)}%), flat=${counts.flat} (${(counts.flat / dates.length * 100).toFixed(1)}%)\n`);

  const outFile = path.join(__dirname, 'overnight_regime_results.csv');
  fs.writeFileSync(outFile, 'regime,candidate,n_blocks,median_multiple,median_cagr,worst5_multiple,best5_multiple,sharpe,p_dd30,p_dd50,cvar5\n');

  for (const regime of ['hiking', 'cutting', 'flat']) {
    const blockStarts = buildRegimeBlockIndex(regimes, BLOCK_SIZE_MONTHS, regime);
    console.log(`=== Regime: ${regime} (${blockStarts.length} eligible block-start months) ===`);
    if (blockStarts.length < 20) {
      console.log('  Too few blocks to bootstrap reliably, skipping.\n');
      continue;
    }
    for (const [name, weights] of Object.entries(CANDIDATES)) {
      const r = runBootstrapCandidate(aligned, blockStarts, weights, TRIALS, YEARS, BLOCK_SIZE_MONTHS);
      console.log(`  ${name.padEnd(38)} median=${r.median.toFixed(3)}x worst5=${r.worst5.toFixed(3)}x sharpe=${r.sharpe.toFixed(4)} pDD30=${(r.pDD30 * 100).toFixed(2)}% pDD50=${(r.pDD50 * 100).toFixed(2)}%`);
      fs.appendFileSync(outFile, `${regime},${name},${blockStarts.length},${r.median.toFixed(4)},${(r.medianCAGR * 100).toFixed(3)},${r.worst5.toFixed(4)},${r.best5.toFixed(4)},${r.sharpe.toFixed(4)},${(r.pDD30 * 100).toFixed(3)},${(r.pDD50 * 100).toFixed(3)},${(r.cvar5 * 100).toFixed(3)}\n`);
    }
    console.log('');
  }

  console.log(`Results saved to ${outFile}`);
}

main();
