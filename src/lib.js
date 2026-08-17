// Shared helpers used by all test scripts in this folder.
const fs = require('fs');
const path = require('path');

const CACHE_FILE = path.join(__dirname, 'historical_data_cache.json');

function loadCache() {
  if (!fs.existsSync(CACHE_FILE)) {
    throw new Error(`Missing ${CACHE_FILE} - run portfolio_deep_test.js once first to download/cache the data.`);
  }
  return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8')); // { aligned: {VWCE:[...],ZPRV:[...],IDTL:[...],GOLD:[...],STB:[...]}, dates: [...] }
}

// Named candidates used across every script, kept in one place so they stay consistent.
const CANDIDATES = {
  'A_Current':  { VWCE: 0.65, ZPRV: 0.30, IDTL: 0.05, GOLD: 0.00, STB: 0.00 },
  'G10':        { VWCE: 0.50, ZPRV: 0.15, IDTL: 0.15, GOLD: 0.10, STB: 0.10 },
  'G15':        { VWCE: 0.45, ZPRV: 0.15, IDTL: 0.15, GOLD: 0.15, STB: 0.10 },
  'H_20pctGold':{ VWCE: 0.40, ZPRV: 0.15, IDTL: 0.15, GOLD: 0.20, STB: 0.10 },
  'K_25pctGold':{ VWCE: 0.35, ZPRV: 0.10, IDTL: 0.15, GOLD: 0.25, STB: 0.15 },
  'Gold30':     { VWCE: 0.30, ZPRV: 0.10, IDTL: 0.15, GOLD: 0.30, STB: 0.15 },
};

const ASSET_ORDER = ['VWCE', 'ZPRV', 'IDTL', 'GOLD', 'STB'];

// Run a fixed weight portfolio through an EXACT (non-randomized) sequence of monthly returns
// starting at index `startIdx`, for `months` months. No rebalancing unless rebalanceEveryMonths is set.
function simulateSequence(aligned, weights, startIdx, months, rebalanceEveryMonths = null) {
  const assets = Object.keys(weights); // use whatever assets this candidate actually specifies
  let holdings = {};
  for (const a of assets) holdings[a] = weights[a]; // treat as dollar values starting at total=1
  let peak = 1, maxDD = 0;
  const path_ = [];
  for (let m = 0; m < months; m++) {
    const idx = startIdx + m;
    let total = 0;
    for (const a of assets) {
      holdings[a] *= (1 + aligned[a][idx]);
      total += holdings[a];
    }
    if (total < 0.001) total = 0.001;
    if (total > peak) peak = total;
    const dd = (peak - total) / peak;
    if (dd > maxDD) maxDD = dd;
    path_.push(total);

    if (rebalanceEveryMonths && (m + 1) % rebalanceEveryMonths === 0) {
      for (const a of assets) holdings[a] = total * weights[a];
    }
  }
  return { finalValue: path_[path_.length - 1], maxDD, path: path_ };
}

// Same but with monthly contributions of `contribAmount` added (in the same units as starting total=1),
// rebalanced by contribution routing: new money goes to whichever sleeve is furthest below target weight.
function simulateDCA(aligned, weights, startIdx, months, monthlyContrib, rebalanceThreshold = 0.05) {
  let holdings = {};
  for (const a of ASSET_ORDER) holdings[a] = 0;
  holdings[ASSET_ORDER[0]] = 1e-9; // avoid div by zero on first month
  let totalContributed = 0;
  let peak = 0, maxDD = 0;
  const path_ = [];

  for (let m = 0; m < months; m++) {
    const idx = startIdx + m;
    // grow existing holdings
    let total = 0;
    for (const a of ASSET_ORDER) {
      holdings[a] *= (1 + aligned[a][idx]);
      total += holdings[a];
    }
    // add contribution, routed to the most-underweight sleeve (drift-based routing)
    if (total > 0) {
      let mostUnder = ASSET_ORDER[0], worstDrift = -Infinity;
      for (const a of ASSET_ORDER) {
        const currentW = holdings[a] / total;
        const drift = weights[a] - currentW;
        if (drift > worstDrift) { worstDrift = drift; mostUnder = a; }
      }
      holdings[mostUnder] += monthlyContrib;
      total += monthlyContrib;
    } else {
      holdings[ASSET_ORDER[0]] += monthlyContrib;
      total += monthlyContrib;
    }
    totalContributed += monthlyContrib;

    if (total > peak) peak = total;
    const dd = peak > 0 ? (peak - total) / peak : 0;
    if (dd > maxDD) maxDD = dd;
    path_.push(total);
  }
  return { finalValue: path_[path_.length - 1], totalContributed, maxDD, path: path_ };
}

// No-gold equivalents (gold weight folded into STB) - used against the deep 1977-2023 cache,
// which has no gold data before 2002-10.
const NOGOLD_CANDIDATES = {
  'A_Current':       { VWCE: 0.65, ZPRV: 0.30, IDTL: 0.05, STB: 0.00 },
  'G10_noGoldEquiv': { VWCE: 0.50, ZPRV: 0.15, IDTL: 0.15, STB: 0.20 },
  'G15_noGoldEquiv': { VWCE: 0.45, ZPRV: 0.15, IDTL: 0.15, STB: 0.25 },
  'H_noGoldEquiv':   { VWCE: 0.40, ZPRV: 0.15, IDTL: 0.15, STB: 0.30 },
};

function loadDeepCache(filename) {
  const file = path.join(__dirname, '..', 'data', filename);
  if (!fs.existsSync(file)) throw new Error(`Missing ${file} - run build_deep_history.js first (see data/README.md).`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

// Block bootstrap: build all possible block-start indices for a given block size.
function buildBlockIndex(nMonths, blockSize) {
  const starts = [];
  for (let i = 0; i <= nMonths - blockSize; i++) starts.push(i);
  return starts;
}

// Simulate ONE randomized path by stitching random historical blocks together, for whatever
// assets are present in `weights`. Returns { finalValue, maxDD, monthlyReturns }.
function simulateBootstrapPath(aligned, weights, blockStarts, blockSize, totalMonths) {
  const assets = Object.keys(weights);
  let holdings = {};
  for (const a of assets) holdings[a] = weights[a];
  let peak = 1, maxDD = 0;
  const monthlyReturns = [];
  let monthsFilled = 0;
  while (monthsFilled < totalMonths) {
    const start = blockStarts[(Math.random() * blockStarts.length) | 0];
    const len = Math.min(blockSize, totalMonths - monthsFilled);
    for (let k = 0; k < len; k++) {
      let total = 0;
      for (const a of assets) {
        holdings[a] *= (1 + aligned[a][start + k]);
        total += holdings[a];
      }
      if (total < 0.001) total = 0.001;
      if (total > peak) peak = total;
      const dd = (peak - total) / peak;
      if (dd > maxDD) maxDD = dd;
      let prevTotal = 0;
      for (const a of assets) prevTotal += holdings[a] / (1 + aligned[a][start + k]); // approx pre-return total, fine for return calc below
      monthlyReturns.push(total / (monthsFilled === 0 && k === 0 ? 1 : monthlyReturns._prevTotal || 1) - 1);
      monthlyReturns._prevTotal = total;
    }
    monthsFilled += len;
  }
  const finalValue = Object.values(holdings).reduce((a, b) => a + b, 0);
  return { finalValue, maxDD, monthlyReturns };
}

// Run `trials` bootstrap paths for one candidate over `years`, return summary stats.
function runBootstrapCandidate(aligned, blockStarts, weights, trials, years, blockSize, rfRate = 0.025) {
  const totalMonths = years * 12;
  const finals = new Array(trials);
  const maxDDs = new Array(trials);
  let allMonthlyReturns = [];

  for (let t = 0; t < trials; t++) {
    const r = simulateBootstrapPath(aligned, weights, blockStarts, blockSize, totalMonths);
    finals[t] = r.finalValue;
    maxDDs[t] = r.maxDD;
    if (t % 100 === 0) allMonthlyReturns = allMonthlyReturns.concat(r.monthlyReturns);
  }

  finals.sort((a, b) => a - b);
  const cagrs = finals.map((m) => Math.pow(Math.max(m, 0.001), 1 / years) - 1);
  const pct = (arr, p) => arr[Math.max(0, Math.floor(p * arr.length) - 1)];

  const median = pct(finals, 0.5);
  const medianCAGR = Math.pow(median, 1 / years) - 1;
  const worst5 = pct(finals, 0.05);
  const best5 = pct(finals, 0.95);
  const worstN = Math.max(1, Math.floor(0.05 * trials));
  const cvar5 = cagrs.slice(0, worstN).reduce((a, b) => a + b, 0) / worstN;
  const pDD30 = maxDDs.filter((d) => d >= 0.3).length / trials;
  const pDD50 = maxDDs.filter((d) => d >= 0.5).length / trials;

  const mean = allMonthlyReturns.reduce((a, b) => a + b, 0) / allMonthlyReturns.length;
  const variance = allMonthlyReturns.reduce((a, b) => a + (b - mean) ** 2, 0) / allMonthlyReturns.length;
  const annVol = Math.sqrt(variance * 12);
  const annMean = Math.pow(1 + mean, 12) - 1;
  const sharpe = (annMean - rfRate) / annVol;

  return { median, medianCAGR, worst5, best5, sharpe, pDD30, pDD50, cvar5 };
}

// Bootstrap-randomized DCA: monthly contribution, drift-based routing (new money goes to
// whichever sleeve is furthest below target weight), stitched from random historical blocks.
function simulateBootstrapDCA(aligned, weights, blockStarts, blockSize, totalMonths, monthlyContrib) {
  const assets = Object.keys(weights);
  let holdings = {};
  for (const a of assets) holdings[a] = 0;
  holdings[assets[0]] = 1e-9;
  let totalContributed = 0;
  let peak = 0, maxDD = 0;
  let monthsFilled = 0;

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
      totalContributed += monthlyContrib;
      if (total > peak) peak = total;
      const dd = peak > 0 ? (peak - total) / peak : 0;
      if (dd > maxDD) maxDD = dd;
    }
    monthsFilled += len;
  }
  const finalValue = Object.values(holdings).reduce((a, b) => a + b, 0);
  return { finalValue, totalContributed, maxDD };
}

function runBootstrapDCACandidate(aligned, blockStarts, weights, trials, years, blockSize, monthlyContrib) {
  const totalMonths = years * 12;
  const finals = new Array(trials);
  const maxDDs = new Array(trials);
  let totalContributed = 0;

  for (let t = 0; t < trials; t++) {
    const r = simulateBootstrapDCA(aligned, weights, blockStarts, blockSize, totalMonths, monthlyContrib);
    finals[t] = r.finalValue;
    maxDDs[t] = r.maxDD;
    totalContributed = r.totalContributed;
  }
  finals.sort((a, b) => a - b);
  const pct = (arr, p) => arr[Math.max(0, Math.floor(p * arr.length) - 1)];
  const median = pct(finals, 0.5);
  const worst5 = pct(finals, 0.05);
  const best5 = pct(finals, 0.95);
  const p25 = pct(finals, 0.25);
  const p75 = pct(finals, 0.75);
  const pDD30 = maxDDs.filter((d) => d >= 0.3).length / trials;
  const pDD50 = maxDDs.filter((d) => d >= 0.5).length / trials;
  return { median, worst5, best5, p25, p75, totalContributed, pDD30, pDD50 };
}

module.exports = {
  loadCache, CANDIDATES, NOGOLD_CANDIDATES, ASSET_ORDER, simulateSequence, simulateDCA,
  loadDeepCache, buildBlockIndex, runBootstrapCandidate, runBootstrapDCACandidate,
};
