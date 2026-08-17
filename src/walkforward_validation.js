// Overnight test 1: REAL walk-forward 30yr windows for the allocation, using every actual overlapping
// starting month in the 1977-2023 no-gold-equivalent cache (559 months = 46.6yrs of history ->
// 199 real 30yr windows). Folds gold weight into STB since this cache predates gold data (2002+).
// Answers: is the "median 7.2x" result concentrated in a few lucky starting decades, or stable
// across every real 30yr stretch that's actually occurred?
//
// Run: node overnight_walkforward_30yr.js

const fs = require('fs');
const path = require('path');
const { loadDeepCache, simulateSequence } = require('./lib.js');

const WINDOW_YEARS = 30;
const OUT_FILE = path.join(__dirname, 'overnight_walkforward_30yr_results.csv');

// the allocation (51/12.75/7.87/25/3.38) with gold folded into STB (safe-asset equivalent),
// plus comparators, run against the long no-gold cache.
const CANDIDATES = {
  'A_Current':            { VWCE: 0.65, ZPRV: 0.30, IDTL: 0.05, STB: 0.00 },
  'G15_noGoldEquiv':      { VWCE: 0.45, ZPRV: 0.15, IDTL: 0.15, STB: 0.25 },
  'allocation_noGoldEquiv': { VWCE: 0.51, ZPRV: 0.1275, IDTL: 0.0787, STB: 0.3038 },
};

function decadeOf(dateStr) {
  const year = parseInt(dateStr.slice(0, 4), 10);
  return `${Math.floor(year / 10) * 10}s`;
}

function main() {
  const cache = loadDeepCache('historical_cache_deep_noGold4.json');
  const { aligned, dates } = cache;
  const windowMonths = WINDOW_YEARS * 12;
  const numWindows = dates.length - windowMonths;

  if (numWindows < 1) throw new Error(`Not enough history for a ${WINDOW_YEARS}yr window.`);

  console.log(`Walk-forward: ${numWindows} overlapping real 30yr windows (${dates[0]} -> ${dates[dates.length - 1]})\n`);

  fs.writeFileSync(OUT_FILE, 'candidate,start_date,end_date,start_decade,final_multiple,cagr,max_drawdown\n');

  const results = {};
  for (const name of Object.keys(CANDIDATES)) results[name] = [];

  for (let start = 0; start < numWindows; start++) {
    for (const [name, weights] of Object.entries(CANDIDATES)) {
      const r = simulateSequence(aligned, weights, start, windowMonths, 12);
      const endDate = dates[start + windowMonths - 1];
      const cagr = Math.pow(Math.max(r.finalValue, 0.001), 1 / WINDOW_YEARS) - 1;
      const dec = decadeOf(dates[start]);
      results[name].push({ startDate: dates[start], endDate, dec, finalValue: r.finalValue, cagr, maxDD: r.maxDD });
      fs.appendFileSync(OUT_FILE, `${name},${dates[start]},${endDate},${dec},${r.finalValue.toFixed(4)},${(cagr * 100).toFixed(3)},${(r.maxDD * 100).toFixed(2)}\n`);
    }
    if ((start + 1) % 25 === 0 || start === numWindows - 1) {
      console.log(`  ${start + 1}/${numWindows} windows done`);
    }
  }

  console.log('\n=== Overall summary ===');
  console.log('Candidate                | Median mult | Worst mult (start)         | Best mult (start)          | Median maxDD | Worst maxDD');
  for (const [name, arr] of Object.entries(results)) {
    const byVal = [...arr].sort((a, b) => a.finalValue - b.finalValue);
    const median = byVal[Math.floor(byVal.length / 2)];
    const worst = byVal[0];
    const best = byVal[byVal.length - 1];
    const byDD = [...arr].sort((a, b) => a.maxDD - b.maxDD);
    const medianDD = byDD[Math.floor(byDD.length / 2)].maxDD;
    const worstDD = byDD[byDD.length - 1].maxDD;
    console.log(
      `${name.padEnd(25)} | ${median.finalValue.toFixed(2)}x`.padEnd(38) +
      `| ${worst.finalValue.toFixed(2)}x (${worst.startDate})`.padEnd(30) +
      `| ${best.finalValue.toFixed(2)}x (${best.startDate})`.padEnd(30) +
      `| ${(medianDD * 100).toFixed(1)}%`.padEnd(15) +
      `| ${(worstDD * 100).toFixed(1)}%`
    );
  }

  console.log('\n=== By starting decade (allocation_noGoldEquiv) ===');
  const nl2 = results['allocation_noGoldEquiv'];
  const byDecade = {};
  for (const r of nl2) {
    if (!byDecade[r.dec]) byDecade[r.dec] = [];
    byDecade[r.dec].push(r);
  }
  for (const [dec, arr] of Object.entries(byDecade).sort()) {
    const vals = arr.map((a) => a.finalValue).sort((a, b) => a - b);
    const med = vals[Math.floor(vals.length / 2)];
    const min = vals[0], max = vals[vals.length - 1];
    console.log(`  Starting ${dec}: n=${arr.length}, median=${med.toFixed(2)}x, range=[${min.toFixed(2)}x, ${max.toFixed(2)}x]`);
  }

  console.log(`\nFull per-window results saved to ${OUT_FILE}`);
}

main();
