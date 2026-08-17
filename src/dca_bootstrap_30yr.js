// Real €150/mo contribution, drift-based routing, 30-year horizon, block-bootstrapped from
// the deep multi-era historical data (not a lump sum, not the short 2005-2026 window).
// Answers: "where does my actual monthly contribution end up in 30 years, for each candidate?"
//
// Run: node dca_bootstrap_30yr.js

const fs = require('fs');
const path = require('path');
const { loadDeepCache, NOGOLD_CANDIDATES, CANDIDATES, buildBlockIndex, runBootstrapDCACandidate } = require('./lib.js');

const TRIALS = 500000;
const YEARS = 30;
const BLOCK_SIZE_MONTHS = 12;
const MONTHLY_CONTRIB = 150;

function runSet(cache, candidates, label) {
  console.log(`\n########## ${label} ##########`);
  console.log(`History: ${cache.dates[0]} -> ${cache.dates[cache.dates.length - 1]}`);
  console.log(`€${MONTHLY_CONTRIB}/mo for ${YEARS} years\n`);
  const blockStarts = buildBlockIndex(cache.dates.length, BLOCK_SIZE_MONTHS);

  console.log('Candidate            | Total in | Median value | Worst 5%  | Best 5%    | 25th pct  | 75th pct');
  const rows = [];
  for (const [name, weights] of Object.entries(candidates)) {
    const r = runBootstrapDCACandidate(cache.aligned, blockStarts, weights, TRIALS, YEARS, BLOCK_SIZE_MONTHS, MONTHLY_CONTRIB);
    rows.push({ name, ...r });
    console.log(
      `${name.padEnd(21)} | €${r.totalContributed.toFixed(0)}`.padEnd(32) +
      `| €${r.median.toFixed(0)}`.padEnd(15) +
      `| €${r.worst5.toFixed(0)}`.padEnd(12) +
      `| €${r.best5.toFixed(0)}`.padEnd(13) +
      `| €${r.p25.toFixed(0)}`.padEnd(12) +
      `| €${r.p75.toFixed(0)}`
    );
  }
  return rows;
}

function main() {
  const noGold = loadDeepCache('historical_cache_deep_noGold4.json');
  const noGoldRows = runSet(noGold, NOGOLD_CANDIDATES, 'No-gold candidates (1977-2023 source data)');

  const full5File = path.join(__dirname, 'historical_cache_deep_full5.json');
  let full5Rows = [];
  if (fs.existsSync(full5File)) {
    const full5 = loadDeepCache('historical_cache_deep_full5.json');
    full5Rows = runSet(full5, CANDIDATES, 'Gold-inclusive candidates (2002-2023 source data)');
  }

  const outFile = path.join(__dirname, 'dca_30yr_results.csv');
  const header = 'candidate,total_contributed,median_value,worst5_value,best5_value,p25_value,p75_value,p_dd30,p_dd50\n';
  const allRows = [...noGoldRows, ...full5Rows];
  const csv = header + allRows.map(r =>
    [r.name, r.totalContributed.toFixed(2), r.median.toFixed(2), r.worst5.toFixed(2), r.best5.toFixed(2), r.p25.toFixed(2), r.p75.toFixed(2), (r.pDD30*100).toFixed(2), (r.pDD50*100).toFixed(2)].join(',')
  ).join('\n') + '\n';
  fs.writeFileSync(outFile, csv);
  console.log(`\nSaved to ${outFile}`);
}

main();
