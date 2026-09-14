// Every real report must land on the parser that claims it, and yield what it
// actually contains.
//
// This harness exists because of a specific near-miss. The fixtures were first
// extracted with pypdf instead of the product's own pdf.js routine, and three
// of Michael Gibson's reports fell through to the low-confidence heuristic with
// zero collections and zero derogatory accounts. It read exactly like a parser
// regression, and the fix would have been to "repair" a parser that was working
// perfectly. Nothing caught it because nothing asserted what a given file is
// supposed to parse INTO. Now something does.
//
// Every expectation below was read off the report itself before being written
// here. Ranges rather than exact counts where extraction can legitimately
// wobble by one; exact where it cannot.
const H = require('./harness');
const R = H.reporter('parsers — every format, every real report');

if (!H.haveFixtures()) {
  console.log('\n  No fixtures. Run:  cd dev && node extract.cjs\n');
  process.exit(2);
}

const api = H.load(['isExperianPrintable', 'expBureau', 'tuIsOnlineServiceCenter', 'mergeParsedReports', 'findContradictions', 'findFactualInconsistencies', 'dedupeFactual', 'statusClass', 'statusSeverity']);

const EXPECT = [
  {file: 'michelle.txt',      format: 'columnar_tri_merge', accounts: [28, 36], inquiries: [8, 20],
   collections: [2, 5],  derog: [8, 14], lowConfidence: false,
   note: 'SmartCredit tri-merge — the format most of Dave’s clients arrive with'},
  {file: 'smartcredit3.txt',  format: 'columnar_tri_merge', accounts: [32, 40], inquiries: [10, 20],
   collections: [1, 3],  derog: [3, 8],  lowConfidence: false,
   note: 'second tri-merge, and the one carrying a collection with a late grid'},
  {file: 'mg_experian.txt',   format: 'experian_printable', accounts: [28, 38], inquiries: [3, 10],
   collections: [1, 3],  derog: [6, 12], lowConfidence: false, bureau: 'Experian'},
  {file: 'mg_equifax.txt',    format: 'experian_printable', accounts: [28, 38], inquiries: [3, 10],
   collections: [1, 3],  derog: [7, 14], lowConfidence: false, bureau: 'Equifax'},
  {file: 'mg_transunion.txt', format: 'experian_printable', accounts: [28, 38], inquiries: [2, 10],
   collections: [1, 3],  derog: [5, 12], lowConfidence: false, bureau: 'TransUnion'},
  {file: 'jose_santiago.txt', format: 'three_bureau',       accounts: [12, 20], inquiries: [12, 24],
   collections: [4, 5],  derog: [1, 6],  lowConfidence: false, publicRecords: [1, 3],
   // A tri-merge reports each collection once per bureau. The raw parse found
   // ten entries for four debts; dedupeCollections folds them, so the count
   // here is the number of debts, not the number of rows.
   note: 'the only report in the set carrying a public record'}
];

const within = (n, r) => n >= r[0] && n <= r[1];

EXPECT.forEach(e => {
  const text = H.fixture(e.file);
  R.section(e.file + (e.note ? ' — ' + e.note : ''));
  if (!text) { R.check('fixture present', false, 'missing'); return; }

  let p;
  try { p = api.parseCreditReport(text); }
  catch (err) { R.check('parses without throwing', false, err.message); return; }

  const acc = p.accounts || [], coll = p.collections || [], pub = p.publicRecords || [];
  const derog = acc.filter(a => a.has_late_payments || a.is_charge_off || a.is_collection ||
                                a.is_repossession || a.in_bankruptcy);

  R.check('format is ' + e.format, p.format === e.format, p.format);
  R.check('not low confidence', !p.low_confidence,
          p.low_confidence ? 'LOW CONFIDENCE — no letters would be built' : 'ok');
  R.check('accounts ' + e.accounts.join('-'), within(acc.length, e.accounts), acc.length + '');
  R.check('inquiries ' + e.inquiries.join('-'), within((p.inquiries || []).length, e.inquiries),
          (p.inquiries || []).length + '');
  R.check('collections ' + e.collections.join('-'), within(coll.length, e.collections), coll.length + '');
  R.check('derogatory ' + e.derog.join('-'), within(derog.length, e.derog), derog.length + '');
  if (e.publicRecords) R.check('public records ' + e.publicRecords.join('-'),
                               within(pub.length, e.publicRecords), pub.length + '');
  if (e.bureau) R.check('bureau read as ' + e.bureau,
                        (p.bureau === e.bureau) || (p.bureaus || []).indexOf(e.bureau) >= 0,
                        String(p.bureau || (p.bureaus || []).join(',')));

  // Whatever the format, an account the letters can name must have a creditor.
  const nameless = acc.filter(a => !a.creditor || !String(a.creditor).trim());
  R.check('every account has a creditor', nameless.length === 0, nameless.length + ' without');

  // Bureau names are title-cased everywhere, or the cross-bureau comparison
  // silently matches nothing.
  const badBureau = [];
  acc.forEach(a => (a.reported_by || []).forEach(b => {
    if (['Equifax', 'Experian', 'TransUnion', 'Innovis'].indexOf(b) < 0) badBureau.push(b);
  }));
  R.check('bureau names are canonical', badBureau.length === 0,
          [...new Set(badBureau)].slice(0, 4).join(', ') || 'clean');
});

// ---- the three single-bureau Gibson files are the same person, same day ----
R.section('the same file read three ways');
const mgFiles = ['mg_experian.txt', 'mg_equifax.txt', 'mg_transunion.txt'].map(H.fixture).filter(Boolean);
if (mgFiles.length === 3) {
  const parsed = mgFiles.map(t => api.parseCreditReport(t));
  const names = parsed.map(p => (p.accounts || []).map(a => String(a.creditor).toUpperCase()));

  // Exact name matching across bureaus finds almost nothing, and that is not a
  // parser fault — it is what the bureaus do. The same three accounts arrive as
  // FREEDOM MORTGAGE CORP / FREEDOM MORTGAGE / FREEDOM MTG, CREDIT ONE BANK NA /
  // CREDIT ONE BANK / CREDITONEBNK, GM FINANCIAL / GMFNANCIAL / GM FINANCIAL.
  // Equifax also truncates at twenty characters. Asserted here so the number is
  // on the record: any future cross-bureau matching has to be fuzzy.
  const exact = names[0].filter(n => names[1].indexOf(n) >= 0 && names[2].indexOf(n) >= 0);
  const norm = s => String(s).toUpperCase().replace(/[^A-Z0-9]/g, '');
  const loose = (a, list) => list.some(b => {
    const x = norm(a), y = norm(b);
    if (!x || !y) return false;
    const short = Math.min(x.length, y.length);
    return short >= 5 && (x.slice(0, short) === y.slice(0, short));
  });
  const shared = names[0].filter(n => loose(n, names[1]) && loose(n, names[2]));
  R.check('the three reports are the same person', shared.length >= 6,
          shared.length + ' creditors match loosely, only ' + exact.length + ' match exactly');
  R.check('exact matching across bureaus is near-useless', exact.length <= 3,
          exact.length + ' exact — recorded, not a defect');
  // Each one on its own cannot produce a cross-bureau contradiction, which is
  // the tool's strongest dispute. That is a product gap, not a parser fault —
  // recorded here so it stays visible.
  R.check('each single-bureau file reports one bureau only',
          parsed.every(p => (p.bureaus || [p.bureau]).filter(Boolean).length === 1),
          parsed.map(p => (p.bureaus || [p.bureau]).join('/')).join('  |  '));
}

// ---- three single-bureau files merged into one file ----
// The upload box has always promised "pick all three single-bureau PDFs at
// once — we'll combine them". It did combine them, and then dropped the
// per-bureau field maps, so the cross-bureau comparison had nothing to compare
// and the strongest dispute the tool can find was unreachable for anybody
// holding three separate reports. On this real set it produced zero findings.
R.section('three single-bureau reports merged');
if (mgFiles.length === 3) {
  const parts = mgFiles.map(t => api.parseCreditReport(t));
  const merged = api.mergeParsedReports(parts);
  const loose = merged.accounts.filter(a => (a.reported_by || []).length > 1);
  const withFields = merged.accounts.filter(a =>
    a.per_bureau_fields && Object.keys(a.per_bureau_fields).length > 1);
  const withStatus = merged.accounts.filter(a =>
    Array.isArray(a.per_bureau_status) && a.per_bureau_status.filter(Boolean).length > 1);

  R.check('the merge fires', merged.format === 'merged_single_bureau', merged.format);
  R.check('all three bureaus are named', (merged.bureaus || []).length === 3, (merged.bureaus || []).join(', '));
  R.check('duplicates collapse', merged.accounts.length < parts.reduce((n, p) => n + p.accounts.length, 0),
          merged.accounts.length + ' from ' + parts.reduce((n, p) => n + p.accounts.length, 0));
  R.check('accounts are cross-referenced', loose.length >= 15, loose.length + ' seen by more than one bureau');
  R.check('per-bureau FIELDS survive the merge', withFields.length >= 15,
          withFields.length + ' carry more than one bureau of fields');
  R.check('per-bureau STATUS survives the merge', withStatus.length >= 15,
          withStatus.length + ' carry more than one bureau status');

  // The payoff, and the only reason any of the above matters.
  const mergedFx = api.dedupeFactual ? api.dedupeFactual(api.findFactualInconsistencies(merged))
                                     : api.findFactualInconsistencies(merged);
  const aloneFx = parts.reduce((n, p) => n + (api.findFactualInconsistencies(p) || []).length, 0);
  R.check('merging finds what no single report shows',
          (mergedFx || []).length > aloneFx,
          (mergedFx || []).length + ' merged vs ' + aloneFx + ' across all three separately');

  // And the thing that must NOT happen: a disagreement invented out of wording.
  const contra = api.findContradictions(merged) || [];
  const bogus = contra.filter(c => {
    const a = merged.accounts.find(z => z.creditor === c.creditor) || {};
    const sev = (a.per_bureau_status || []).filter(Boolean)
      .map(v => api.statusSeverity ? api.statusSeverity(v) : null)
      .filter(v => v !== null);
    return sev.length > 1 && sev.every(v => v === sev[0]);   // all the same severity
  });
  R.check('no contradiction is invented from wording alone', bogus.length === 0,
          bogus.map(b => b.creditor).join(', ') || 'clean');
}

R.section('severity is compared by category, not by sentence');
['Collection', 'Collection account. $3,927', 'Collection account'].forEach(v => {
  R.check('"' + v + '" is severity 9', api.statusSeverity && api.statusSeverity(v) === 9,
          String(api.statusSeverity && api.statusSeverity(v)));
});
[['Pays account as agreed', 'clean'], ['Open/Never late.', 'clean'],
 ['Paid or paying as agreed', 'clean'], ['Charged off as bad debt', 'derogatory'],
 ['90 days past due', 'derogatory'], ['Closed', 'neutral']].forEach(([v, want]) => {
  R.check('"' + v + '" classifies as ' + want, api.statusClass && api.statusClass(v) === want,
          String(api.statusClass && api.statusClass(v)));
});
// Absence is not a clean status.
['-', '--', 'N/A', '', '   '].forEach(v => {
  R.check('"' + v + '" is not treated as a status', !api.statusClass || api.statusClass(v) === null,
          String(api.statusClass && api.statusClass(v)));
});

R.done();
