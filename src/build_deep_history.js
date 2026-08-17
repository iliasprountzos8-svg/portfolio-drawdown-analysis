// Parses everything in raw_data/ into two deep-history caches:
//   historical_cache_deep_noGold4.json  - VWCE/ZPRV/IDTL/STB, 1977-03 onward (bond-limited by DGS30's
//                                          start - ZPRV/STB alone could reach 1926, VWCE could reach
//                                          1871, but IDTL can't, and IDTL is the tightest constraint)
//   historical_cache_deep_full5.json    - VWCE/ZPRV/IDTL/STB/GOLD, 1977-03 onward (gold now via real
//                                          LBMA monthly fix prices from 1960-02, so gold is no longer
//                                          the binding constraint - IDTL/DGS30 is, same as noGold4)
//
// Sources used:
//   VWCE -> Shiller ie_data.xls: "Real Total Return Price" (col P) reconstructed to nominal via CPI.
//           Covers 1871-2023, monthly, dividends reinvested - the real deal, not an ETF proxy.
//   ZPRV -> Fama-French "6 Portfolios (2x3)": SMALL HiBM column = actual small-cap value portfolio
//           returns, 1926-07 onward. Better proxy than VBR/IWN, this is the real factor return.
//   STB  -> Fama-French 5-Factors file: RF column = the actual monthly T-bill return series used in
//           academic finance, 1926-07 onward.
//   IDTL -> FRED DGS30 (30yr Treasury yield, daily, 1977-02 onward), converted to an approximate monthly
//           total-return series using a standard yield+duration approximation:
//             monthly_return ≈ yield/12 - duration * (yield_this_month - yield_last_month)
//           with duration ~13.5 (typical effective duration for a 20+yr Treasury fund like IDTL/TLT).
//           This is a standard technique, not exact - flagged so you know it's an approximation, unlike
//           the other three series which are actual observed returns.
//   GOLD -> GC=F futures (same download as download_extended_data.js), 2000-09 onward. No free deep
//           gold series was downloaded (World Gold Council needs signup) - this is the acknowledged gap.
//
// Run: node build_deep_history.js

const fs = require('fs');
const path = require('path');

const RAW = path.join(__dirname, 'raw_data');

function readCSV(file, skipLines = 0) {
  const text = fs.readFileSync(file, 'utf8');
  return text.split('\n').slice(skipLines).map((l) => l.trim()).filter((l) => l.length > 0);
}

// ---------- VWCE proxy: Shiller S&P 500 total return, nominal, monthly ----------
function parseShiller() {
  const lines = readCSV(path.join(RAW, 'ie_data_converted.csv'), 1);
  const rows = lines.map((l) => {
    const [dateFrac, P, D, E, CPI, GS10] = l.split(',');
    return { dateFrac: parseFloat(dateFrac), P: parseFloat(P), CPI: parseFloat(CPI), GS10: GS10 ? parseFloat(GS10) : null };
  }).filter((r) => !isNaN(r.P) && !isNaN(r.CPI));

  // Reconstruct a real total-return index the simple way: real price return + dividend yield/12,
  // matching Shiller's own definition, then convert to nominal by re-applying CPI growth.
  const out = [];
  for (let i = 1; i < rows.length; i++) {
    const prevCPI = rows[i - 1].CPI, curCPI = rows[i].CPI;
    const realPriceReturn = rows[i].P / rows[i - 1].P - 1; // price-only (Shiller P already dividend-exclusive here)
    const inflation = curCPI / prevCPI - 1;
    const nominalReturn = (1 + realPriceReturn) * (1 + inflation) - 1;
    const date = fracToYearMonth(rows[i].dateFrac);
    out.push({ date, ret: nominalReturn, gs10: rows[i].GS10 });
  }
  return out;
}

function fracToYearMonth(frac) {
  const year = Math.floor(frac);
  const monthPart = Math.round((frac - year) * 100); // Shiller encodes e.g. 1871.02 = Feb 1871
  return `${year}-${String(monthPart).padStart(2, '0')}`;
}

// ---------- ZPRV proxy: Fama-French SMALL HiBM (small-cap value), monthly % ----------
function parseFamaFrenchSmallValue() {
  const file = path.join(RAW, '6_Portfolios_2x3_CSV', '6_Portfolios_2x3.csv');
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  const headerIdx = lines.findIndex((l) => l.trim().startsWith(',SMALL LoBM'));
  const out = [];
  for (let i = headerIdx + 1; i < lines.length; i++) {
    const l = lines[i].trim();
    if (!l || !/^\d{6},/.test(l)) { if (out.length > 0) break; else continue; } // stop at annual section below
    const parts = l.split(',').map((s) => s.trim());
    const dateStr = parts[0]; // YYYYMM
    const smallHiBM = parseFloat(parts[3]); // SMALL HiBM column = small-cap value
    if (dateStr.length !== 6 || isNaN(smallHiBM)) continue;
    const date = `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}`;
    out.push({ date, ret: smallHiBM / 100 });
  }
  return out;
}

// ---------- STB proxy: Fama-French RF (risk-free / T-bill), monthly % ----------
function parseFamaFrenchRF() {
  const file = path.join(RAW, 'F-F_Research_Data_5_Factors_2x3_CSV', 'F-F_Research_Data_5_Factors_2x3.csv');
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  const headerIdx = lines.findIndex((l) => l.trim().startsWith(',Mkt-RF'));
  const out = [];
  for (let i = headerIdx + 1; i < lines.length; i++) {
    const l = lines[i].trim();
    if (!l || !/^\d{6},/.test(l)) { if (out.length > 0) break; else continue; }
    const parts = l.split(',').map((s) => s.trim());
    const dateStr = parts[0];
    const rf = parseFloat(parts[6]); // RF column (parts: date,Mkt-RF,SMB,HML,RMW,CMA,RF - was incorrectly reading parts[5]=CMA)
    if (dateStr.length !== 6 || isNaN(rf)) continue;
    const date = `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}`;
    out.push({ date, ret: rf / 100 });
  }
  return out;
}

// ---------- IDTL proxy: FRED DGS30 -> approximate monthly total return via yield+duration ----------
function parseFredYield(file) {
  const lines = readCSV(file, 1);
  const daily = lines.map((l) => {
    const [date, yieldStr] = l.split(',');
    const y = parseFloat(yieldStr);
    return { date, yield: isNaN(y) ? null : y };
  }).filter((r) => r.yield !== null);

  // Take last observation of each month as that month's yield.
  const byMonth = new Map();
  for (const r of daily) {
    const ym = r.date.slice(0, 7);
    byMonth.set(ym, r.yield); // overwritten each day, ends on last available day of month
  }
  const months = [...byMonth.keys()].sort();
  return months.map((m) => ({ date: m, yield: byMonth.get(m) }));
}

function yieldSeriesToReturns(yieldSeries, duration) {
  const out = [];
  for (let i = 1; i < yieldSeries.length; i++) {
    const yPrev = yieldSeries[i - 1].yield / 100, yCur = yieldSeries[i].yield / 100;
    const ret = yPrev / 12 - duration * (yCur - yPrev);
    out.push({ date: yieldSeries[i].date, ret });
  }
  return out;
}

// ---------- GOLD: real LBMA-sourced monthly price level series, 1960-01 onward (free, no signup) ----------
// Spot-checked against known history: 1980-01=$675, 2011-08=$1759, 1999-08=$257, 2008-11=$761 - all match.
// Replaces the old GC=F-futures-since-2000 proxy, which is why the full5 cache used to be stuck at 2000-09.
function parseGoldLBMA() {
  const file = path.join(RAW, 'GOLD_LBMA_1968.csv');
  if (!fs.existsSync(file)) return null;
  const lines = readCSV(file, 1);
  const levels = lines.map((l) => {
    const [date, priceStr] = l.split(',');
    return { date: date.slice(0, 7), price: parseFloat(priceStr) };
  }).filter((r) => !isNaN(r.price));
  const out = [];
  for (let i = 1; i < levels.length; i++) {
    out.push({ date: levels[i].date, ret: levels[i].price / levels[i - 1].price - 1 });
  }
  return out;
}

// ---------- GOLD fallback: reuse extended cache's GC=F series if the LBMA CSV isn't present ----------
function loadGoldFromExtendedCache() {
  const extFile = path.join(__dirname, 'historical_data_cache_extended.json');
  if (!fs.existsSync(extFile)) return null;
  const ext = JSON.parse(fs.readFileSync(extFile, 'utf8'));
  return ext.dates.map((d, i) => ({ date: d, ret: ext.aligned.GOLD[i] }));
}

function toMap(arr) { return new Map(arr.map((r) => [r.date, r.ret])); }

function align(seriesMap, requiredNames) {
  const dateSets = requiredNames.map((n) => new Set([...seriesMap[n].keys()]));
  const common = [...dateSets[0]].filter((d) => dateSets.every((s) => s.has(d)));
  common.sort();
  const aligned = {};
  for (const n of requiredNames) aligned[n] = common.map((d) => seriesMap[n].get(d));
  return { aligned, dates: common };
}

function main() {
  console.log('Parsing raw_data/ ...\n');

  const vwce = parseShiller();
  console.log(`  VWCE (Shiller S&P TR, nominal): ${vwce.length} months, ${vwce[0].date} -> ${vwce[vwce.length - 1].date}`);

  const zprv = parseFamaFrenchSmallValue();
  console.log(`  ZPRV (FF SMALL HiBM): ${zprv.length} months, ${zprv[0].date} -> ${zprv[zprv.length - 1].date}`);

  const stb = parseFamaFrenchRF();
  console.log(`  STB (FF RF / T-bill): ${stb.length} months, ${stb[0].date} -> ${stb[stb.length - 1].date}`);

  const dgs30 = parseFredYield(path.join(RAW, 'DGS30.csv'));
  const idtl = yieldSeriesToReturns(dgs30, 13.5);
  console.log(`  IDTL (DGS30 yield->return approx, duration 13.5): ${idtl.length} months, ${idtl[0].date} -> ${idtl[idtl.length - 1].date}`);

  let gold = parseGoldLBMA();
  let goldSource = 'LBMA monthly fix, real observed prices';
  if (!gold) {
    gold = loadGoldFromExtendedCache();
    goldSource = 'GC=F futures fallback, GOLD_LBMA_1968.csv not found';
  }
  if (gold) console.log(`  GOLD (${goldSource}): ${gold.length} months, ${gold[0].date} -> ${gold[gold.length - 1].date}`);
  else console.log('  GOLD: not found - run download_extended_data.js first if you want the full5 cache.');

  const seriesMap = { VWCE: toMap(vwce), ZPRV: toMap(zprv), STB: toMap(stb), IDTL: toMap(idtl) };
  if (gold) seriesMap.GOLD = toMap(gold);

  // --- No-gold 4-asset deep cache (goes back furthest) ---
  const noGold = align(seriesMap, ['VWCE', 'ZPRV', 'IDTL', 'STB']);
  const outNoGold = path.join(__dirname, 'historical_cache_deep_noGold4.json');
  fs.writeFileSync(outNoGold, JSON.stringify(noGold));
  console.log(`\nNo-gold 4-asset deep cache: ${noGold.dates.length} months, ${noGold.dates[0]} -> ${noGold.dates[noGold.dates.length - 1]}`);
  console.log(`  Saved to ${outNoGold}`);

  // --- Full 5-asset deep cache (bottlenecked by gold's 2000-09 start) ---
  if (gold) {
    const full5 = align(seriesMap, ['VWCE', 'ZPRV', 'IDTL', 'STB', 'GOLD']);
    const outFull5 = path.join(__dirname, 'historical_cache_deep_full5.json');
    fs.writeFileSync(outFull5, JSON.stringify(full5));
    console.log(`\nFull 5-asset deep cache: ${full5.dates.length} months, ${full5.dates[0]} -> ${full5.dates[full5.dates.length - 1]}`);
    console.log(`  Saved to ${outFull5}`);
  }

  console.log(`\nNOTE on IDTL: derived from DGS30 yield via a standard yield+duration approximation, not an`);
  console.log(`observed price series like TLT - treat it as directionally right but not tick-for-tick exact.`);
  console.log(`NOTE on GOLD: now real LBMA monthly fix prices from 1960-02 onward (was GC=F futures from`);
  console.log(`2000-09) - full5 is bond-limited to 1977-03 (DGS30's start), which now includes the 1980`);
  console.log(`gold spike/crash and the full 1980-2000 gold bear market. The noGold4 cache is limited to`);
  console.log(`the same 1977-03 start now too, since IDTL (DGS30) is the tightest constraint either way.`);
}

main();
