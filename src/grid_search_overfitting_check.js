// Overnight test 2: fine-grained parameter sensitivity sweep around the allocation (gold=25%,
// safety_pct=15%, idtl_share=70%, vz_share=80%). The original full_grid_search.js used coarse
// steps (gold in 5% increments, vz_share in 10pt increments) - this checks whether 25% gold /
// 80% vz_share is a genuine local optimum or just the coarsest grid point that happened to win,
// by stepping gold in 1% increments and vz_share/safety_pct in 2pt increments around the winner.
// idtl_share held at the allocation's 0.70 (already screened coarsely elsewhere).
//
// Screening pass at 20k trials/combo, then the top 12 finalists (by median, tie-broken by
// pDD50) get re-run at 1,000,000 trials for a trustworthy final ranking.
//
// Run: node overnight_fine_grid.js

const fs = require('fs');
const path = require('path');
const { loadDeepCache, buildBlockIndex, runBootstrapCandidate } = require('./lib.js');

const SCREEN_TRIALS = 20000;
const FINAL_TRIALS = 1000000;
const YEARS = 30;
const BLOCK_SIZE_MONTHS = 12;
const IDTL_SHARE = 0.70;

const GOLD_STEPS = Array.from({ length: 11 }, (_, i) => 20 + i);          // 20..30, step 1
const SAFETY_STEPS = Array.from({ length: 11 }, (_, i) => +(0.05 + i * 0.02).toFixed(2)); // 0.05..0.25, step 0.02
const VZ_STEPS = Array.from({ length: 11 }, (_, i) => +(0.70 + i * 0.02).toFixed(2));      // 0.70..0.90, step 0.02

function buildWeights(goldPct, safetyPct, idtlShare, vzShare) {
  const gold = goldPct / 100;
  const nonGold = 1 - gold;
  const safety = nonGold * safetyPct;
  const equity = nonGold - safety;
  const idtl = safety * idtlShare;
  const stb = safety * (1 - idtlShare);
  const vwce = equity * vzShare;
  const zprv = equity * (1 - vzShare);
  return { VWCE: vwce, ZPRV: zprv, IDTL: idtl, GOLD: gold, STB: stb };
}

function buildGrid() {
  const combos = [];
  const seen = new Set();
  for (const goldPct of GOLD_STEPS) {
    for (const safetyPct of SAFETY_STEPS) {
      for (const vzShare of VZ_STEPS) {
        const w = buildWeights(goldPct, safetyPct, IDTL_SHARE, vzShare);
        const key = `${w.VWCE.toFixed(4)}|${w.ZPRV.toFixed(4)}|${w.IDTL.toFixed(4)}|${w.GOLD.toFixed(4)}|${w.STB.toFixed(4)}`;
        if (seen.has(key)) continue;
        seen.add(key);
        combos.push({ goldPct, safetyPct, idtlShare: IDTL_SHARE, vzShare, weights: w });
      }
    }
  }
  return combos;
}

function appendWithRetry(file, text, retries = 20, delayMs = 500) {
  for (let i = 0; i < retries; i++) {
    try { fs.appendFileSync(file, text); return; }
    catch (err) {
      if (err.code === 'EBUSY' && i < retries - 1) {
        const wait = Date.now() + delayMs;
        while (Date.now() < wait) {}
      } else throw err;
    }
  }
}

function main() {
  const cache = loadDeepCache('historical_cache_deep_full5.json');
  console.log(`History: ${cache.dates[0]} -> ${cache.dates[cache.dates.length - 1]} (${cache.dates.length} months)`);
  const blockStarts = buildBlockIndex(cache.dates.length, BLOCK_SIZE_MONTHS);

  const combos = buildGrid();
  console.log(`Fine grid: ${combos.length} combos, ${SCREEN_TRIALS} trials each (screening pass)\n`);

  const screenFile = path.join(__dirname, 'overnight_fine_grid_screen.csv');
  fs.writeFileSync(screenFile, 'gold_pct,safety_pct,idtl_share,vz_share,vwce_w,zprv_w,idtl_w,gold_w,stb_w,median_multiple,median_cagr,worst5_multiple,best5_multiple,sharpe,p_dd30,p_dd50,cvar5\n');

  const screened = [];
  const start0 = Date.now();
  for (let i = 0; i < combos.length; i++) {
    const c = combos[i];
    const r = runBootstrapCandidate(cache.aligned, blockStarts, c.weights, SCREEN_TRIALS, YEARS, BLOCK_SIZE_MONTHS);
    screened.push({ ...c, result: r });
    const row = [
      c.goldPct, c.safetyPct, c.idtlShare, c.vzShare,
      c.weights.VWCE.toFixed(4), c.weights.ZPRV.toFixed(4), c.weights.IDTL.toFixed(4), c.weights.GOLD.toFixed(4), c.weights.STB.toFixed(4),
      r.median.toFixed(4), (r.medianCAGR * 100).toFixed(3), r.worst5.toFixed(4), r.best5.toFixed(4),
      r.sharpe.toFixed(3), (r.pDD30 * 100).toFixed(2), (r.pDD50 * 100).toFixed(2), (r.cvar5 * 100).toFixed(3),
    ].join(',');
    appendWithRetry(screenFile, row + '\n');
    if ((i + 1) % 50 === 0 || i === combos.length - 1) {
      const elapsed = ((Date.now() - start0) / 1000).toFixed(0);
      console.log(`[${i + 1}/${combos.length}, ${elapsed}s] gold=${c.goldPct}% safety=${c.safetyPct} vz=${c.vzShare} -> median=${r.median.toFixed(2)}x sharpe=${r.sharpe.toFixed(3)} pDD50=${(r.pDD50 * 100).toFixed(1)}%`);
    }
  }

  // Rank by median multiple, break ties by lower pDD50, take top 12 for confirmation.
  screened.sort((a, b) => b.result.median - a.result.median || a.result.pDD50 - b.result.pDD50);
  const finalists = screened.slice(0, 12);

  console.log(`\nScreening done. Top 12 finalists re-running at ${FINAL_TRIALS.toLocaleString()} trials...\n`);

  const confirmFile = path.join(__dirname, 'overnight_fine_grid_confirm.csv');
  fs.writeFileSync(confirmFile, 'rank,gold_pct,safety_pct,idtl_share,vz_share,vwce_w,zprv_w,idtl_w,gold_w,stb_w,median_multiple,median_cagr,worst5_multiple,best5_multiple,sharpe,p_dd30,p_dd50,cvar5\n');

  console.log('Rank | gold% | safety% | vz%  | median  | worst5  | sharpe | pDD50');
  for (let i = 0; i < finalists.length; i++) {
    const c = finalists[i];
    const r = runBootstrapCandidate(cache.aligned, blockStarts, c.weights, FINAL_TRIALS, YEARS, BLOCK_SIZE_MONTHS);
    const row = [
      i + 1, c.goldPct, c.safetyPct, c.idtlShare, c.vzShare,
      c.weights.VWCE.toFixed(4), c.weights.ZPRV.toFixed(4), c.weights.IDTL.toFixed(4), c.weights.GOLD.toFixed(4), c.weights.STB.toFixed(4),
      r.median.toFixed(4), (r.medianCAGR * 100).toFixed(3), r.worst5.toFixed(4), r.best5.toFixed(4),
      r.sharpe.toFixed(3), (r.pDD30 * 100).toFixed(2), (r.pDD50 * 100).toFixed(2), (r.cvar5 * 100).toFixed(3),
    ].join(',');
    appendWithRetry(confirmFile, row + '\n');
    console.log(`${String(i + 1).padEnd(4)} | ${String(c.goldPct).padEnd(5)} | ${String(c.safetyPct).padEnd(7)} | ${String(c.vzShare).padEnd(4)} | ${r.median.toFixed(3)}x | ${r.worst5.toFixed(3)}x | ${r.sharpe.toFixed(3)} | ${(r.pDD50 * 100).toFixed(2)}%`);
  }

  console.log(`\nFor reference, the allocation itself = gold25 safety0.15 idtlShare0.70 vz0.80.`);
  console.log(`Screening results: ${screenFile}\nConfirmed finalists: ${confirmFile}`);
}

main();
