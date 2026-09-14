// Shared scaffolding. Every harness evaluates the page's own script blocks in
// Node against a stub DOM, so what gets tested is the shipped code rather than
// a copy of it.
const fs = require('fs');
const path = require('path');

const INDEX = process.env.MGC_INDEX ||
  path.join(__dirname, '..', 'index.html');
const FIXTURES = path.join(__dirname, 'fixtures');

function load(extra) {
  const src = fs.readFileSync(INDEX, 'utf8');
  const blocks = [];
  const re = /<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(src)) !== null) blocks.push(m[1]);

  const stub = new Proxy(function () {}, {
    get(t, k) {
      if (k === 'style' || k === 'classList' || k === 'dataset') return stub;
      if (k === 'value' || k === 'innerHTML' || k === 'textContent' || k === 'id') return '';
      if (k === 'children' || k === 'childNodes') return [];
      if (k === Symbol.toPrimitive || k === 'toString') return () => '';
      return stub;
    },
    set() { return true; },
    apply() { return stub; }
  });

  // The personalisation inputs have to answer with what state.userInfo holds.
  // A blanket stub returns '' for every .value, and buildActionPlanDoc calls
  // updateUserInfo() which reads those inputs — so building the plan wiped the
  // name and address and every letter came out saying [YOUR FULL NAME]. That
  // looked like a serious product defect and was entirely the stub. The real
  // page has a guard (planDetailsComplete) that asks for the details first.
  const UI_FIELDS = {'ui-name': 'name', 'ui-address': 'address', 'ui-city': 'city',
                     'ui-dob': 'dob', 'ui-ssn': 'ssnLast4'};
  const inputStub = key => new Proxy(function () {}, {
    get(t, k) {
      if (k === 'value') return (global.__api && global.__api.state && global.__api.state.userInfo &&
                                 global.__api.state.userInfo[key]) || '';
      if (k === 'style' || k === 'classList' || k === 'dataset') return stub;
      if (k === 'children' || k === 'childNodes') return [];
      if (k === Symbol.toPrimitive || k === 'toString') return () => '';
      return stub;
    },
    set() { return true; },
    apply() { return stub; }
  });

  global.document = {
    getElementById: id => (UI_FIELDS[id] ? inputStub(UI_FIELDS[id]) : stub),
    querySelector: () => stub,
    querySelectorAll: () => [], createElement: () => stub,
    addEventListener: () => {}, body: stub, head: stub, documentElement: stub};
  global.window = {addEventListener: () => {},
    matchMedia: () => ({matches: false, addListener: () => {}}),
    location: {href: 'http://localhost/'}, print: () => {}};
  global.navigator = {userAgent: 'node'};
  global.localStorage = {getItem: () => null, setItem: () => {}, removeItem: () => {}};
  global.sessionStorage = {getItem: () => null, setItem: () => {}, removeItem: () => {}};
  global.alert = () => {};
  global.requestAnimationFrame = f => setTimeout(f, 0);

  const want = ['state', 'parseCreditReport', 'runAnalysis', 'determineLetterPacket',
    'regenerateAllLetters', 'buildLetterContext', 'letterTemplates', 'buildActionPlanDoc',
    'fragments', 'pickFrom', 'pickMulti'].concat(extra || []);
  eval(blocks.join('\n;\n') + ';global.__api={' +
    want.map(n => n + ': (typeof ' + n + ' !== "undefined" ? ' + n + ' : undefined)').join(',') + '};');
  const api = global.__api;
  api.SRC = src;
  return api;
}

function fixture(name) {
  const p = path.join(FIXTURES, name);
  if (!fs.existsSync(p)) return null;
  return fs.readFileSync(p, 'utf8');
}

function haveFixtures() {
  return fs.existsSync(FIXTURES) && fs.readdirSync(FIXTURES).some(f => f.endsWith('.txt'));
}

// A fresh, fully-reset session. Every harness starts here so no test inherits
// another's answers — a stale state.roundTwo once made a whole suite green.
function session(api, intake) {
  const st = api.state;
  st.upload = {}; st.analysis = null; st.letterOutputs = {}; st.letterVariants = {};
  st.r2Dropped = []; st.actionPlan = null; st.roundTwo = null; st.mode = null;
  st.selectedBreach = null; st.ftcReportNumber = ''; st.lettersRendered = false;
  st.itemReview = {inquiries: {}, accounts: {}, resolved: {}, reviewed: false};
  st.identityReview = {addresses: {}, aka: {}, employers: {}, au_explains: null, reviewed: false};
  st.userInfo = {name: 'PAT MORGAN', address: '1 Main St', city: 'Sarasota, FL 34236',
                 dob: '01/01/1980', ssnLast4: '4321'};
  st.intake = Object.assign({
    situation: 'cleanup', special_flags: [], state: 'FL', voice: 'plain',
    prior_dispute: 'no', prior_dispute_when: null, prior_dispute_resolved: null,
    collector_contact: 'none', lawsuit_status: 'no', personal_statement: null,
    recent_move: 'no', primary_goal: 'remove_items',
    why_now: null, payment_status: null, hardship: [], deadline: null,
    channel: [], military_status: null,
    breach_which: [], breach_notice: null, breach_misuse: []
  }, intake || {});
  return st;
}

// Parse, analyse, pick the packet, compile every letter. Returns the letters
// keyed by id, each an array of copies (a letter that fans out has several).
function build(api, reportText, intake) {
  const st = session(api, intake);
  st.upload = {parsed: api.parseCreditReport(reportText)};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();
  const out = {};
  (st.analysis.letters || []).forEach(t => {
    out[t.id] = (st.letterVariants[t.id] || [st.letterOutputs[t.id]].filter(Boolean));
  });
  return {st: st, parsed: st.upload.parsed, letters: out};
}

function reporter(title) {
  let fails = 0;
  console.log('\n=== ' + title + ' ===');
  return {
    check(name, cond, detail) {
      console.log((cond ? '  PASS  ' : '  FAIL  ') + name + (detail ? '  [' + detail + ']' : ''));
      if (!cond) fails++;
      return !!cond;
    },
    section(s) { console.log('\n-- ' + s + ' --'); },
    done() {
      console.log(fails ? '\n' + fails + ' CHECK(S) FAILED\n' : '\nall clear\n');
      process.exit(fails ? 1 : 0);
    },
    get fails() { return fails; }
  };
}

module.exports = {load, fixture, haveFixtures, session, build, reporter, FIXTURES, INDEX};
