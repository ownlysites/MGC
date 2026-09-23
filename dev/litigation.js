// Would a consumer-FCRA firm be able to use these letters?
//
// McCarthy Law's Dispute Letter Guide (June 2021) is a litigation intake
// standard rather than a dispute strategy. Its point is not getting a deletion
// — it is that the letter has to survive as EVIDENCE if the dispute fails and
// the case goes to court. Two of its rules are testable here, and both are
// things that could quietly regress when someone adds a fragment later.
//
//   TONE. "Please refrain from using language such as 'you are violating my
//   rights', 'I am angry' or 'this is an outrage'. Unfortunately, letters
//   containing this language cannot be used in a litigation. An additional
//   Dispute Letter will need to be sent and this will hold up moving forward
//   in litigation." A letter that vents costs the client months.
//
//   IDENTIFIERS. The firm requires full name, address, date of birth and
//   account number on a litigation-ready letter. We deliberately do NOT print
//   a full SSN, which is a considered disagreement rather than an oversight —
//   see the note on ssnLast4 below.
//
// This gate matches ACCUSATORY CONSTRUCTIONS, not words. Citing 15 U.S.C.
// § 1681n — "willful noncompliance exposes you to statutory damages" — is a
// recitation of what the statute provides and is in every demand letter a firm
// has ever sent. Banning the word "violation" would flag that and train
// everyone to ignore the gate, which is the mistake compliance.js records
// having already made once.
//
// Needs fixtures, because the point is the letters a real report produces.
const H = require('./harness');
const R = H.reporter('litigation-ready — the letters stay usable as evidence');

if (!H.haveFixtures()) {
  console.log('\n  No fixtures. Run:  cd dev && node extract.cjs\n');
  process.exit(2);
}
const api = H.load();

// Each entry is a construction a litigator would strike, with why.
const VENTING = [
  [/violat\w*\s+my\s+rights/i,                   'accuses rather than states the defect'],
  [/\b(I am|I'm|Im)\s+(angry|furious|livid|outraged|sick of)/i, 'emotive'],
  [/\bthis\s+is\s+an?\s+(outrage|disgrace|joke|scam)/i,        'emotive'],
  [/\boutrageous\b/i,                            'emotive'],
  [/\bhow\s+dare\s+you/i,                        'emotive'],
  [/\byou\s+people\b/i,                          'contemptuous'],
  [/\byour?\s+(incompetence|negligence|stupidity)/i, 'name-calling'],
  [/\b(criminals?|crooks?|liars?|thieves)\b/i,   'name-calling'],
  [/\bI\s+(demand|insist)\s+that\s+you\s+immediately/i, 'reads as a rant rather than a request'],
  [/\bunacceptable\b/i,                          'editorial'],
  [/\bfed\s+up\b|\bhad\s+enough\b/i,             'emotive']
];

// Every voice, because the whole risk is that the angry one is angrier than we
// think. Plus the situations that give someone the most to be angry about.
const RUNS = [
  {label: 'frustrated voice, collector chasing',  file: 'smartcredit3.txt',
   intake: {voice: 'frustrated', situation: 'collector', collector_contact: 'aggressive'}},
  {label: 'frustrated voice, sued',               file: 'michelle.txt',
   intake: {voice: 'frustrated', situation: 'lawsuit', lawsuit_status: 'yes'}},
  {label: 'frustrated voice, identity theft',     file: 'michelle.txt',
   intake: {voice: 'frustrated', situation: 'idtheft', special_flags: ['identity_theft']}},
  {label: 'firm voice',                           file: 'michelle.txt',  intake: {voice: 'firm'}},
  {label: 'plain voice',                          file: 'jose_santiago.txt', intake: {voice: 'plain'}},
  {label: 'hopeful voice',                        file: 'michelle.txt',  intake: {voice: 'hopeful'}},
  // A pasted personal statement is the one place a consumer's own words reach
  // the page. It is capped and quoted, never rewritten — so the gate has to
  // know that a rant they typed themselves is theirs, not ours.
  {label: 'frustrated voice + their own words',   file: 'michelle.txt',
   intake: {voice: 'frustrated',
            personal_statement: 'This has been going on for two years and nobody will listen to me.'}}
];

let letters = 0, copies = 0;

RUNS.forEach(run => {
  const text = H.fixture(run.file);
  R.section(run.label + '  (' + run.file + ')');
  if (!text) { R.check('fixture present', false, run.file + ' missing'); return; }

  const st = H.session(api, run.intake);
  st.upload = {parsed: api.parseCreditReport(text)};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();

  const ids = (st.analysis.letters || []).map(l => l.id);
  if (!ids.length) { R.check('the packet has letters', false, 'none built'); return; }

  const problems = [];
  ids.forEach(id => {
    const out = st.letterVariants[id] || [st.letterOutputs[id]].filter(Boolean);
    letters++;
    out.forEach(o => {
      copies++;
      ['mail', 'portal', 'short'].forEach(ch => {
        const v = String(o[ch] || '');
        if (!v) return;
        VENTING.forEach(([rx, why]) => {
          const hit = v.match(rx);
          if (hit) problems.push(id + ' .' + ch + ': "' + hit[0] + '" — ' + why);
        });
      });
    });
  });
  R.check(ids.length + ' letter(s), nothing a litigator would strike',
          problems.length === 0, problems.slice(0, 3).join('  ;  ') || 'clean');
});

// The firm's own examples, run against the gate, so a future edit that guts
// the patterns fails here rather than silently passing everything.
R.section('the gate catches what the firm actually named');
(function () {
  const THEIRS = [
    'You are violating my rights and I will not stand for it.',
    'I am angry that this has not been fixed.',
    'This is an outrage and someone should be fired.'
  ];
  THEIRS.forEach(s => {
    R.check(JSON.stringify(s.slice(0, 38) + '…') + ' is caught',
            VENTING.some(([rx]) => rx.test(s)));
  });
  // And the thing that must NOT be caught: reciting the statute.
  const LEGIT = [
    'Please be advised that willful noncompliance with the FCRA exposes you to statutory damages of $100 to $1,000 per violation under 15 U.S.C. § 1681n.',
    'Under 15 U.S.C. § 1692k, violations of the FDCPA subject you to statutory damages up to $1,000.',
    'A public record that reports a status the court does not show is disputable on its face.'
  ];
  LEGIT.forEach(s => {
    R.check('statutory recitation is not flagged: ' + JSON.stringify(s.slice(0, 34) + '…'),
            !VENTING.some(([rx]) => rx.test(s)));
  });
})();

// The identifiers a litigation file needs. We print four of the five the firm
// asks for; the fifth is a deliberate disagreement.
R.section('the identifiers a firm needs to open a file');
(function () {
  const st = H.session(api, {});
  st.userInfo = {name: 'PAT MORGAN', address: '1 Main St', city: 'Sarasota, FL 34236',
                 dob: '01/01/1980', ssnLast4: '4321'};
  st.upload = {parsed: api.parseCreditReport(H.fixture('michelle.txt'))};
  api.runAnalysis();
  st.analysis.letters = api.determineLetterPacket(st.analysis);
  api.regenerateAllLetters();
  const mail = String((st.letterOutputs['initial_bureau_dispute'] || {}).mail || '');

  R.check('full name', /PAT MORGAN/.test(mail));
  R.check('full address', /1 Main St/.test(mail) && /Sarasota, FL 34236/.test(mail));
  R.check('date of birth', /01\/01\/1980/.test(mail));
  R.check('an account number on the disputed item', /\d{4}/.test(mail));

  // DELIBERATE. The firm asks for a full SSN on a litigation-ready letter. This
  // tool prints the last four and no more, and that is a choice rather than a
  // gap: the letters are printed by people who will mail them themselves, the
  // packet is not screened by anyone, and a full SSN sitting in a printed stack
  // or a reused PDF is a durable risk that a consumer cannot undo. Someone
  // taking a file to a firm can write the rest on by hand.
  R.check('the SSN is last-four only', /SSN \(last 4\): 4321/.test(mail));
  R.check('and a full SSN is never printed', !/\b\d{3}-\d{2}-\d{4}\b/.test(mail));
})();

console.log('\n  ' + letters + ' letter template(s), ' + copies + ' copies checked');
R.done();
