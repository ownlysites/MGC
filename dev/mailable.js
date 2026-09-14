// Every letter in every packet must be ready to sign and post.
//
// Dave found this class of defect twice by hand. First the § 623(b) direct
// dispute, which had been printing "[Furnisher Name] / [Furnisher Address]"
// every time it was ever built. Then the breach notification, which printed
// five placeholders and was addressed to nobody — and passed the earlier
// version of this file only because none of its scenarios ticked the breach
// flag. Scenarios are cheap; add one whenever a path is not covered here.
//
// A letter is mailable when it names a real recipient, contains no bracket, no
// instruction to the consumer, and no unfilled blank in the body.
const H = require('./harness');
const R = H.reporter('mailable — every letter, every scenario');

if (!H.haveFixtures()) {
  console.log('\n  No fixtures. Run:  cd dev && node extract.cjs\n');
  process.exit(2);
}
const api = H.load(['bankruptcyRecord']);

const BAD = [
  [/\[[^\]]{2,60}\]/g,                         'a bracket'],
  [/SEND A SEPARATE COPY/i,                    'an instruction to the consumer'],
  [/WHILE YOU ARE AT IT/i,                     'guidance inside the envelope'],
  [/address (is |printed )?on your statement/i, 'a placeholder address'],
  [/_{6,}/g,                                    'an unfilled blank'],
  [/\bTODO\b|\bFIXME\b|\bXXX\b/,               'a marker'],
  [/undefined|NaN|\[object Object\]/,          'a value that did not resolve']
];

// Two underscore runs are legitimate envelope furniture and always have been:
// the date the consumer writes in, and the rule they sign above. Naming them is
// safer than slicing by position — an earlier version of this cut from "To Whom
// It May Concern" to the last underscore, and every letter with a different
// salutation kept its date line and failed. Anything else made of underscores
// is a blank nobody filled.
function unfilledBlanks(mail) {
  return String(mail || '').split(/\r?\n/).filter(l => {
    if (!/_{6,}/.test(l)) return false;
    if (/^\s*Date:\s*_+\s*$/.test(l)) return false;   // the consumer dates it
    if (/^\s*_+\s*$/.test(l)) return false;           // the signature rule
    return true;
  });
}

const SCENARIOS = [
  {label: 'tri-merge, plain cleanup',        file: 'michelle.txt',      intake: {}},
  {label: 'tri-merge, collector chasing',    file: 'smartcredit3.txt',  intake: {situation: 'collector', collector_contact: 'aggressive'}},
  {label: 'single-bureau Experian print',    file: 'mg_experian.txt',   intake: {}},
  {label: 'single-bureau Equifax print',     file: 'mg_equifax.txt',    intake: {}},
  {label: 'single-bureau TransUnion print',  file: 'mg_transunion.txt', intake: {}},
  {label: 'three-bureau with a public record', file: 'jose_santiago.txt', intake: {}},
  {label: 'identity theft',                  file: 'michelle.txt',      intake: {situation: 'idtheft', special_flags: ['identity_theft']}},
  {label: 'breach, none named',              file: 'michelle.txt',      intake: {situation: 'breach', special_flags: ['data_breach'], breach_misuse: ['nothing']}},
  {label: 'breach, Equifax named',           file: 'smartcredit3.txt',  intake: {situation: 'breach', special_flags: ['data_breach'], breach_which: ['equifax_2017'], breach_notice: 'yes_ssn', breach_misuse: ['nothing']}},
  {label: 'breach with real misuse',         file: 'jose_santiago.txt', intake: {situation: 'breach', special_flags: ['data_breach', 'identity_theft'], breach_which: ['npd_2024'], breach_misuse: ['new_accounts', 'tax']}},
  {label: 'military',                        file: 'michelle.txt',      intake: {special_flags: ['scra'], military_status: 'active'}},
  // The bankruptcy letters were never covered here, and both were printing
  // "[Collector]" and "[Address]" into an envelope because neither was wired
  // into the fan-out. jose_santiago.txt carries a DISMISSED filing, so its
  // bankruptcy letters are the ones the packet must WITHHOLD; michelle.txt has
  // no public record, so the intake tick is what builds them.
  {label: 'bankruptcy filed, from intake',   file: 'michelle.txt',      intake: {special_flags: ['bankruptcy']}},
  {label: 'considering bankruptcy',          file: 'michelle.txt',      intake: {special_flags: ['bankruptcy_considering']}},
  {label: 'round two, all verified',         file: 'michelle.txt',      intake: {}, roundTwo: 'verified'},
  {label: 'round two, no response',          file: 'smartcredit3.txt',  intake: {}, roundTwo: 'no_response'},
  // Nobody filled the optional identity fields in. Every bureau letter carries
  // an SSN/DOB line and this used to post "[XXXX]" and "[MM/DD/YYYY]".
  {label: 'no DOB, no SSN4, no FTC number',  file: 'michelle.txt',      intake: {special_flags: ['identity_theft']}, bareUser: true}
];

let letters = 0, copies = 0;

SCENARIOS.forEach(s => {
  const text = H.fixture(s.file);
  R.section(s.label + '  (' + s.file + ')');
  if (!text) { R.check('fixture present', false, s.file + ' missing'); return; }

  const st = H.session(api, s.intake);
  if (s.bareUser) st.userInfo = {name: 'PAT MORGAN', address: '1 Main St', city: 'Sarasota, FL 34236'};
  st.upload = {parsed: api.parseCreditReport(text)};
  api.runAnalysis();

  // Flag one account and one inquiry so the consent-gated letters build too.
  const accs = st.upload.parsed.accounts || [];
  if (accs.length && api.setAccountAnswer && api.accountKey) {
    try { api.setAccountAnswer(api.accountKey(accs[0], 0), 'never'); } catch (e) {}
  }
  if ((st.upload.parsed.inquiries || []).length) st.itemReview.inquiries[0] = 'no';

  if (s.roundTwo) {
    st.roundTwo = {items: {}, mailedOn: '2026-06-01'};
    (st.analysis.findings || []).forEach(f => {
      if (f.account && f.account.creditor) st.roundTwo.items[String(f.account.creditor).toUpperCase()] = s.roundTwo;
    });
    (st.analysis.factual || []).forEach(fx => {
      if (fx.creditor) st.roundTwo.items[String(fx.creditor).toUpperCase()] = s.roundTwo;
    });
    api.runAnalysis();
  }

  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();

  const ids = (st.analysis.letters || []).map(l => l.id);
  if (!ids.length) { R.check('the packet has letters in it', false, 'none built'); return; }

  ids.forEach(id => {
    const out = (st.letterVariants[id] || [st.letterOutputs[id]].filter(Boolean));
    if (!out.length) { R.check(id + ' produced a letter', false, 'built nothing'); return; }
    letters++;
    const problems = [];
    // One deliberate exception, and it earns it. scra_default_protection is a
    // motion to a court, not a letter to a company: the court's name, the case
    // number and the servicemember's defences are on the papers they were
    // served with and nothing here can know them. It is allowed to carry ruled
    // blanks ONLY because the separator sheet says so in terms — which is
    // asserted separately below, so the exemption cannot become a hiding place.
    // The stay notice earns the same exemption for the same reason: the court
    // it was filed in and the dates of the contact that violated the stay are
    // on the petition and in the person's own log, not on a credit report. Its
    // separator-sheet wording is asserted separately below too.
    // And the discharge dispute, whose chapter, case number and discharge date
    // are on the court's order and on no credit report.
    const blanksAllowed = (id === 'scra_default_protection' ||
                           id === 'bankruptcy_automatic_stay' ||
                           id === 'bankruptcy_discharged');
    out.forEach((o, i) => {
      copies++;
      const who = out.length > 1 ? (o.to || 'copy ' + (i + 1)) : '';
      BAD.forEach(([rx, why]) => {
        if (rx.source.indexOf('_{6,}') >= 0) {
          if (blanksAllowed) return;
          const blanks = unfilledBlanks(o.mail);
          if (blanks.length) problems.push(why + ': ' + JSON.stringify(blanks[0].trim().slice(0, 40)) + (who ? ' → ' + who : ''));
          return;
        }
        const hit = String(o.mail || '').match(rx);
        if (hit) problems.push(why + ': ' + [...new Set(hit)].slice(0, 3).join(' | ') + (who ? ' → ' + who : ''));
      });
      // A letter that fans out must know who it is going to.
      if (out.length > 1 && !(o.to && String(o.to).trim())) problems.push('copy ' + (i + 1) + ' is addressed to nobody');
    });
    R.check(id + (out.length > 1 ? ' ×' + out.length : ''), problems.length === 0,
            problems.slice(0, 3).join('  ;  ') || 'mailable');
  });
});

// The exemption above is only defensible if the packet tells the person. This
// is the check that keeps it honest.
R.section('the one letter allowed to carry blanks says so');
(function () {
  const st = H.session(api, {special_flags: ['scra'], military_status: 'active', lawsuit_status: 'yes'});
  st.upload = {parsed: api.parseCreditReport(H.fixture('michelle.txt'))};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();
  api.buildActionPlanDoc();
  const plan = String(st.planHtml || '').replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ');
  const built = (st.analysis.letters || []).some(l => l.id === 'scra_default_protection');
  R.check('the court motion is in this packet', built, built ? 'yes' : 'not built — check below is vacuous');
  if (built) {
    R.check('the separator sheet says to fill it in first', /Fill this one in before you file it/i.test(plan));
    R.check('and says a filing with blanks is returned', /returned/i.test(plan));
    R.check('and points at free legal assistance', /legal assistance/i.test(plan));
  }
  R.check('the pre-service warning is on the 6% letter',
          /BEFORE you went on active duty/i.test(plan));
})();

// Same rule for the stay notice, plus the two gating decisions that keep the
// packet from asserting something the court record contradicts.
R.section('the bankruptcy letters');
(function () {
  const st = H.session(api, {special_flags: ['bankruptcy']});
  st.upload = {parsed: api.parseCreditReport(H.fixture('michelle.txt'))};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();
  api.buildActionPlanDoc();
  const plan = String(st.planHtml || '').replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ');
  const ids = (st.analysis.letters || []).map(l => l.id);
  const built = ids.indexOf('bankruptcy_automatic_stay') >= 0;
  R.check('a filing with no court record still builds the stay notice', built,
          built ? 'yes' : 'not built — the checks below are vacuous');
  if (built) {
    R.check('the separator sheet says to fill it in first',
            /Fill this one in before you send it/i.test(plan));
    R.check('and says the court is on the petition', /petition/i.test(plan));
    R.check('and asks for the dates of the contact', /dates? of the calls|each date/i.test(plan));
    const copiesOut = st.letterVariants['bankruptcy_automatic_stay'] || [];
    R.check('it fans out to the collectors rather than one "[Collector]"',
            copiesOut.length >= 1 && copiesOut.every(c => c.to && String(c.to).trim()),
            copiesOut.length + ' copies');
  }
  R.check('ticking "I have filed" does not produce a pre-filing notice',
          ids.indexOf('bankruptcy_pre_filing') < 0);
  if (ids.indexOf('bankruptcy_discharged') >= 0) {
    R.check('the discharge dispute says to copy the case off the order',
            /discharge order/i.test(plan));
    const disc = st.letterOutputs['bankruptcy_discharged'] || {};
    R.check('and never prints "Chapter null"', !/Chapter null|Chapter undefined/.test(String(disc.mail || '')));
  }
})();

(function () {
  const st = H.session(api, {special_flags: ['bankruptcy_considering']});
  st.upload = {parsed: api.parseCreditReport(H.fixture('michelle.txt'))};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();
  const ids = (st.analysis.letters || []).map(l => l.id);
  R.check('"considering" builds the pre-filing notice', ids.indexOf('bankruptcy_pre_filing') >= 0);
  R.check('and does not claim a stay that does not exist yet',
          ids.indexOf('bankruptcy_automatic_stay') < 0);
})();

(function () {
  // Jose Santiago's filing reads DISMISSED. The stay ended with the case under
  // 11 U.S.C. § 362(c)(2)(B) and the debts were never discharged, so neither
  // letter is true and neither may be in the packet.
  const st = H.session(api, {});
  st.upload = {parsed: api.parseCreditReport(H.fixture('jose_santiago.txt'))};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  const ids = (st.analysis.letters || []).map(l => l.id);
  const rec = api.bankruptcyRecord(st.upload.parsed);
  R.check('the dismissed filing is read as dismissed', !!(rec && rec.dismissed),
          rec ? JSON.stringify({d: rec.discharged, x: rec.dismissed}) : 'no record found');
  R.check('no discharge letter on a dismissed case', ids.indexOf('bankruptcy_discharged') < 0);
  R.check('no stay letter on a dismissed case', ids.indexOf('bankruptcy_automatic_stay') < 0);
  R.check('no pre-filing notice on a case already filed', ids.indexOf('bankruptcy_pre_filing') < 0);
})();

console.log('\n  ' + letters + ' letter template(s), ' + copies + ' copies checked');
R.done();
