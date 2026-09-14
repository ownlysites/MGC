// What each real client would actually get. Not assertions — the packet.
//
// Runs every fixture through the whole pipeline the way the browser does:
// parse, analyse, pick the letters, compile them, build the printed plan. Then
// reports what came out, including anything that looks wrong.
const H = require('./harness');
const api = H.load(['mergeParsedReports', 'apParse', 'apIsActionPlan', 'apStanceSummary',
                    'findContradictions', 'findFactualInconsistencies', 'dedupeFactual']);

if (!H.haveFixtures()) { console.log('\nNo fixtures. cd dev && node extract.cjs\n'); process.exit(2); }

const CLIENTS = [
  {who: 'Michelle Ivery',        files: ['michelle.txt'],      plan: 'ap_michelle.txt'},
  {who: 'Michael Gibson',        files: ['smartcredit3.txt'],  note: 'his SmartCredit tri-merge'},
  {who: 'Michael Gibson',        files: ['mg_experian.txt', 'mg_equifax.txt', 'mg_transunion.txt'],
   note: 'the same person, three separate bureau PDFs, merged'},
  {who: 'Jose Santiago (Gio)',   files: ['jose_santiago.txt'], plan: 'ap_gio.txt'},
  {who: 'James Gibson',          files: ['gibson_james.txt'],  note: 'a 3-page extract, not a full report'}
];

const BAD = [
  [/\[[^\]]{2,60}\]/,                          'BRACKET'],
  [/undefined|NaN|\[object Object\]/,          'UNRESOLVED VALUE'],
  [/address (is |printed )?on your statement/i, 'PLACEHOLDER ADDRESS']
];
const allowBlanks = id => id === 'scra_default_protection';
function blanks(mail, id) {
  if (allowBlanks(id)) return [];
  return String(mail || '').split(/\r?\n/).filter(l =>
    /_{6,}/.test(l) && !/^\s*Date:\s*_+\s*$/.test(l) && !/^\s*_+\s*$/.test(l));
}

let problems = 0;

CLIENTS.forEach(c => {
  const texts = c.files.map(H.fixture);
  if (texts.some(t => !t)) { console.log('\n' + c.who + ': fixture missing'); return; }

  const st = H.session(api, {});
  const parts = texts.map(t => api.parseCreditReport(t));
  const parsed = parts.length > 1 ? api.mergeParsedReports(parts) : parts[0];
  st.upload = {parsed: parsed};

  if (c.plan) {
    const pt = H.fixture(c.plan);
    if (pt && api.apIsActionPlan && api.apIsActionPlan(pt)) st.actionPlan = api.apParse(pt);
  }

  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();
  api.buildActionPlanDoc();

  const a = st.analysis;
  const acc = parsed.accounts || [];
  const derog = acc.filter(x => x.has_late_payments || x.is_charge_off || x.is_collection ||
                                x.is_repossession || x.in_bankruptcy);
  const plan = String(st.planHtml || '').replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ');

  console.log('\n' + '='.repeat(74));
  console.log(c.who + (c.note ? '  —  ' + c.note : '') + '   [' + c.files.join(' + ') + ']');
  console.log('='.repeat(74));
  console.log('  format            ' + parsed.format + (parsed.low_confidence ? '   *** LOW CONFIDENCE — no item-level letters ***' : ''));
  console.log('  bureaus           ' + ((parsed.bureaus && parsed.bureaus.length ? parsed.bureaus : [parsed.bureau]).filter(Boolean).join(', ') || '—'));
  console.log('  accounts          ' + acc.length + '   (' + derog.length + ' derogatory)');
  console.log('  collections       ' + (parsed.collections || []).length +
              '    inquiries ' + (parsed.inquiries || []).length +
              '    public records ' + (parsed.publicRecords || []).length);
  const scores = (parsed.scores || []).filter(s => s && s.reported);
  console.log('  scores            ' + (scores.length ? scores.map(s => s.bureau + ' ' + s.score).join('  ') : 'none reported'));
  console.log('  contradictions    ' + (a.factual || []).length + ' factual, ' +
              ((a.contradictions || []).length) + ' cross-bureau');
  if (st.actionPlan && api.apStanceSummary) {
    const ss = api.apStanceSummary();
    if (ss) console.log('  action plan       ' + ss.protected.length + ' protected, ' + ss.targets.length + ' targeted');
  }

  // What the cover actually claims
  const coverClean = /There is nothing here to dispute/.test(plan);
  const coverSays = /No derogatory items found/.test(plan) ? 'no derogatory items'
    : /still is not accurate/.test(plan) ? 'clean but contradicted'
    : /items? worth working on/.test(plan) ? 'items to work on' : '(other)';
  console.log('  cover says        ' + coverSays);

  const ids = (a.letters || []).map(l => l.id);
  let copies = 0;
  const detail = [];
  ids.forEach(id => {
    const out = (st.letterVariants[id] || [st.letterOutputs[id]].filter(Boolean));
    copies += out.length;
    detail.push('     ' + id + (out.length > 1 ? ' ×' + out.length : ''));
    out.forEach(o => {
      BAD.forEach(([rx, why]) => { if (rx.test(String(o.mail || ''))) {
        console.log('  !! ' + why + ' in ' + id + (o.to ? ' → ' + o.to : '')); problems++; } });
      const b = blanks(o.mail, id);
      if (b.length) { console.log('  !! UNFILLED BLANK in ' + id + ': ' + JSON.stringify(b[0].trim().slice(0, 40))); problems++; }
      if (out.length > 1 && !(o.to && String(o.to).trim())) { console.log('  !! ' + id + ' copy addressed to nobody'); problems++; }
    });
  });
  console.log('  letters           ' + ids.length + ' templates, ' + copies + ' envelopes to sign');
  detail.forEach(d => console.log(d));

  // The invariant that bit us this week
  if (coverClean && copies > 0) {
    const disputing = api.buildLetterContext(api.letterTemplates.initial_bureau_dispute);
    if ((disputing.items || []).length > 0) {
      console.log('  !! COVER SAYS NOTHING TO DISPUTE BUT ' + disputing.items.length + ' ITEMS ARE DISPUTED');
      problems++;
    }
  }
});

console.log('\n' + '='.repeat(74));
console.log(problems ? problems + ' PROBLEM(S) FOUND' : 'No placeholders, no unaddressed letters, no contradictory claims.');
console.log('='.repeat(74) + '\n');
process.exit(problems ? 1 : 0);
