// Overnight test 3: tight-confidence tail metrics for the FINAL candidate only (the allocation,
// 51/12.75/7.87/25/3.38). Cheap to push trial count way up once you're down to one allocation.
// Runs 10 independent batches of 1,000,000 trials each (10M total) so we get both a final
// pooled estimate AND a batch-to-batch spread - that spread IS the confidence interval on
// tail metrics like P(>=50% drawdown), P(>=30% drawdown), and CVaR5, without needing a closed-
// form formula for it.
//
// Run: node overnight_final_confidence.js

const fs = require('fs');
const path = require('path');
const { loadDeepCache, buildBlockIndex, runBootstrapCandidate } = require('./lib.js');

const BATCHES = 10;
const TRIALS_PER_BATCH = 1000000;
const YEARS = 30;
const BLOCK_SIZE_MONTHS = 12;

const CANDIDATE = { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0.0787, GOLD: 0.25, STB: 0.0338 };

function mean(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length; }
function stdev(arr) {
  const m = mean(arr);
  return Math.sqrt(arr.reduce((a, b) => a + (b - m) ** 2, 0) / arr.length);
}

function main() {
  const cache = loadDeepCache('historical_cache_deep_full5.json');
  console.log(`History: ${cache.dates[0]} -> ${cache.dates[cache.dates.length - 1]} (${cache.dates.length} months)`);
  console.log(`the allocation: ${JSON.stringify(CANDIDATE)}`);
  console.log(`${BATCHES} batches x ${TRIALS_PER_BATCH.toLocaleString()} trials = ${(BATCHES * TRIALS_PER_BATCH).toLocaleString()} total trials\n`);

  const blockStarts = buildBlockIndex(cache.dates.length, BLOCK_SIZE_MONTHS);

  const outFile = path.join(__dirname, 'overnight_final_confidence_batches.csv');
  fs.writeFileSync(outFile, 'batch,median,median_cagr,worst5,best5,sharpe,p_dd30,p_dd50,cvar5\n');

  const metrics = { median: [], medianCAGR: [], worst5: [], best5: [], sharpe: [], pDD30: [], pDD50: [], cvar5: [] };

  const start0 = Date.now();
  for (let b = 0; b < BATCHES; b++) {
    const r = runBootstrapCandidate(cache.aligned, blockStarts, CANDIDATE, TRIALS_PER_BATCH, YEARS, BLOCK_SIZE_MONTHS);
    for (const k of Object.keys(metrics)) metrics[k].push(r[k]);
    fs.appendFileSync(outFile, `${b + 1},${r.median.toFixed(4)},${(r.medianCAGR * 100).toFixed(3)},${r.worst5.toFixed(4)},${r.best5.toFixed(4)},${r.sharpe.toFixed(4)},${(r.pDD30 * 100).toFixed(3)},${(r.pDD50 * 100).toFixed(3)},${(r.cvar5 * 100).toFixed(3)}\n`);
    const elapsed = ((Date.now() - start0) / 1000).toFixed(0);
    console.log(`Batch ${b + 1}/${BATCHES} [${elapsed}s elapsed]: median=${r.median.toFixed(3)}x worst5=${r.worst5.toFixed(3)}x sharpe=${r.sharpe.toFixed(4)} pDD30=${(r.pDD30 * 100).toFixed(2)}% pDD50=${(r.pDD50 * 100).toFixed(2)}% cvar5=${(r.cvar5 * 100).toFixed(2)}%`);
  }

  console.log('\n=== Pooled estimate +/- batch-to-batch stdev (proxy for CI width) ===');
  for (const [k, arr] of Object.entries(metrics)) {
    const label = { median: 'Median multiple', medianCAGR: 'Median CAGR %', worst5: 'Worst5% multiple', best5: 'Best5% multiple',
      sharpe: 'Sharpe', pDD30: 'P(maxDD>=30%) %', pDD50: 'P(maxDD>=50%) %', cvar5: 'CVaR5 (CAGR) %' }[k];
    const scale = k === 'medianCAGR' || k === 'pDD30' || k === 'pDD50' || k === 'cvar5' ? 100 : 1;
    const m = mean(arr) * scale, s = stdev(arr) * scale;
    console.log(`${label.padEnd(20)}: ${m.toFixed(3)} +/- ${s.toFixed(4)} (batch range [${(Math.min(...arr) * scale).toFixed(3)}, ${(Math.max(...arr) * scale).toFixed(3)}])`);
  }

  console.log(`\nBatch-level results saved to ${outFile}`);
}

main();
