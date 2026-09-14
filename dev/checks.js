// The nine checks added from the cheat sheets, each proven to fire and proven
// not to fire on a clean report.
//
// A detection rule that has never been seen firing is not a feature. Several of
// these cannot be demonstrated on the seven real reports — no collection in any
// of them names an original creditor, and only one carries a public record at
// all — so the fixtures here are synthetic and built to the shape the parsers
// actually produce. The real reports are the other half of the evidence and
// live in parsers.js and endtoend.js.
//
// Needs no client data.
const H = require('./harness');
const R = H.reporter('checks — the nine rules from the cheat sheets');
const api = H.load(['findPublicRecordDefects', 'findDoubleJeopardy', 'findFactualInconsistencies']);

const BUREAUS = ['Equifax', 'Experian', 'TransUnion'];

function fields(o) {
  return Object.assign({
    account_status: 'Open', account_rating: 'Pays as agreed', payment_status: 'Current',
    creditor_remarks: '', payment_amount: '$50', balance_owed: '$1,000',
    high_balance: '$2,000', past_due: '$0', date_opened: '01/01/2015',
    date_last_activity: '08/01/2026', date_last_paid: '08/01/2026'
  }, o);
}
function perBureau(o, only) {
  const out = {};
  (only || BUREAUS).forEach(b => { out[b] = fields(o); });
  return out;
}
function acct(o) {
  return Object.assign({
    creditor: 'GOOD BANK', account_number: '1234567890123456', account_type: 'Credit Card',
    date_opened: '01/01/2015', date_closed: null, date_reported: '08/01/2026',
    date_last_payment: '08/01/2026', open_closed: 'Open', status: 'Pays as agreed',
    balance: '$1,000', high_balance: '$2,000', credit_limit: '$5,000', monthly_payment: '$50',
    past_due: '$0', responsibility: 'Individual', comments: [], dofd: null,
    is_collection: false, is_charge_off: false, has_late_payments: false,
    is_repossession: false, in_bankruptcy: false,
    per_bureau_fields: perBureau({})
  }, o);
}
function report(o) {
  return Object.assign({
    accounts: [], collections: [], inquiries: [], publicRecords: [], scores: [],
    personal: {}, bureaus: BUREAUS.slice(), format: 'three_bureau'
  }, o);
}

function analyse(parsed, intake, roundTwo) {
  const st = H.session(api, intake || {});
  st.upload = {parsed: parsed};
  if (roundTwo) st.roundTwo = roundTwo;
  api.runAnalysis();
  return (st.analysis.factual || []);
}
const has = (list, rule) => list.some(f => f.rule === rule);
const one = (list, rule) => list.filter(f => f.rule === rule)[0];

// ---------------------------------------------------------------- clean base
R.section('a clean report fires nothing');
(function () {
  const f = analyse(report({accounts: [acct({})]}));
  R.check('no findings at all on a clean tradeline', f.length === 0,
          f.map(x => x.rule).join(', ') || 'none');
})();

// ------------------------------------------------- 3. late marks on a collection
R.section('a collection reporting late payments');
(function () {
  const f = analyse(report({accounts: [acct({
    creditor: 'MIDLAND CREDIT', is_collection: true, status: 'Collection account',
    late_counts: {d30: 2, d60: 1, d90: 0, d120: 0},
    per_bureau_fields: perBureau({account_status: 'Collection', payment_status: 'Collection',
                                 payment_amount: '$0', past_due: '$0'})
  })]}));
  R.check('fires', has(f, 'late_payments_on_collection'));
  const hit = one(f, 'late_payments_on_collection');
  if (hit) R.check('counts every late mark', /3 late-payment/.test(hit.detail), hit.detail.slice(0, 60));
  const clean = analyse(report({accounts: [acct({
    creditor: 'MIDLAND CREDIT', is_collection: true, status: 'Collection account',
    late_counts: {d30: 0, d60: 0, d90: 0, d120: 0},
    per_bureau_fields: perBureau({account_status: 'Collection', payment_status: 'Collection',
                                 payment_amount: '$0', past_due: '$0'})
  })]}));
  R.check('and not on a collection with no late grid', !has(clean, 'late_payments_on_collection'));
})();

// -------------------------------------------------- 4. past due on transferred
R.section('a transferred account still reporting a past due');
(function () {
  const f = analyse(report({accounts: [acct({
    creditor: 'OLD MORTGAGE CO', status: 'Transferred',
    per_bureau_fields: perBureau({account_status: 'Transferred', payment_status: 'Transferred',
                                 balance_owed: '$0', past_due: '$430'})
  })]}));
  R.check('past due fires on its own', has(f, 'past_due_on_transferred'));
  R.check('and is not reported as a balance problem', !has(f, 'balance_on_transferred'));
  const b = analyse(report({accounts: [acct({
    creditor: 'OLD MORTGAGE CO', status: 'Transferred',
    per_bureau_fields: perBureau({account_status: 'Transferred', payment_status: 'Transferred',
                                 balance_owed: '$2,100', past_due: '$0'})
  })]}));
  R.check('balance still fires on its own', has(b, 'balance_on_transferred'));
  R.check('and is not reported as a past-due problem', !has(b, 'past_due_on_transferred'));
})();

// --------------------------------------------------- 9 + 15. the day-31 checks
R.section('the day-31 checks, run rather than recommended');
(function () {
  const disputed = report({accounts: [acct({
    creditor: 'CAPITAL ONE', status: 'Charge-off', is_charge_off: true,
    date_reported: '07/15/2026', comments: ['Account charged off'],
    per_bureau_fields: perBureau({account_status: 'Closed', payment_status: 'Charge-off',
                                 payment_amount: '$0', balance_owed: '$1,000', high_balance: '$2,000'})
  })]});
  const r2 = {mailedOn: '2026-05-01', items: {'CAPITAL ONE': 'verified'}};

  const f = analyse(disputed, {}, r2);
  R.check('the missing dispute notation fires', has(f, 'notice_of_dispute_missing'));

  const noted = JSON.parse(JSON.stringify(disputed));
  noted.accounts[0].comments = ['Account charged off', 'Consumer disputes this account information'];
  R.check('and does not fire once the notation is there',
          !has(analyse(noted, {}, r2), 'notice_of_dispute_missing'));

  const early = JSON.parse(JSON.stringify(disputed));
  early.accounts[0].date_reported = '05/10/2026';   // nine days after the dispute
  R.check('and does not fire on a report pulled before day 30',
          !has(analyse(early, {}, r2), 'notice_of_dispute_missing'));

  R.check('no round two, no day-31 findings',
          !has(analyse(disputed), 'notice_of_dispute_missing'));

  // Verified, but the last-reported date predates the dispute.
  const stale = JSON.parse(JSON.stringify(disputed));
  stale.accounts[0].date_reported = '02/01/2026';
  const sf = analyse(stale, {}, r2);
  R.check('a verified account whose date never moved fires', has(sf, 'status_update_not_moved'));
  const hit = one(sf, 'status_update_not_moved');
  if (hit) R.check('and names the dispute date', /May 1, 2026/.test(hit.detail), hit.detail.slice(0, 70));

  const deleted = {mailedOn: '2026-05-01', items: {'CAPITAL ONE': 'deleted'}};
  R.check('an item they say was deleted is not chased for a stale date',
          !has(analyse(stale, {}, deleted), 'status_update_not_moved'));
})();

// ----------------------------------------------- 11. a bankruptcy with no court
R.section('public records');
(function () {
  const f = analyse(report({
    accounts: [acct({})],
    publicRecords: [{type: 'bankruptcy', date_filed: 'May 30, 2023', status: 'Dismissed',
                     reference: '2310741', court: null, court_column: true, bureau: 'TransUnion'}]
  }));
  R.check('a bankruptcy with an empty Court column fires', has(f, 'bankruptcy_court_not_reported'));
  const hit = one(f, 'bankruptcy_court_not_reported');
  if (hit) R.check('and names the bureau reporting it', /TransUnion/.test(hit.detail));

  const named = analyse(report({
    accounts: [acct({})],
    publicRecords: [{type: 'bankruptcy', date_filed: 'May 30, 2023', status: 'Dismissed',
                     reference: '2310741', court: 'US Bankruptcy Court Middle Dist FL',
                     court_column: true, bureau: 'TransUnion'}]
  }));
  R.check('and not when a court is named', !has(named, 'bankruptcy_court_not_reported'));

  // A format with no Court column at all says nothing either way.
  const noCol = analyse(report({
    accounts: [acct({})],
    publicRecords: [{type: 'bankruptcy', date_filed: 'May 30, 2023', status: 'Dismissed',
                     reference: '2310741', court: null, court_column: false, bureau: null}]
  }));
  R.check('and never on a layout that has no Court column',
          !has(noCol, 'bankruptcy_court_not_reported'));
})();

// --------------------------------- 12 + 13. filing dates that disagree
(function () {
  const rec = (bureau, date, type) => ({type: type || 'bankruptcy', date_filed: date,
    status: 'Filed', reference: 'ABC-991', court: 'District Court', court_column: true, bureau: bureau});

  const f = analyse(report({accounts: [acct({})],
    publicRecords: [rec('Equifax', 'Mar 04, 2021'), rec('TransUnion', 'Sep 18, 2021')]}));
  R.check('two bureaus, two filing dates, fires', has(f, 'public_record_filing_date_mismatch'));

  const same = analyse(report({accounts: [acct({})],
    publicRecords: [rec('Equifax', 'Mar 04, 2021'), rec('TransUnion', 'Mar 04, 2021')]}));
  R.check('and not when they agree', !has(same, 'public_record_filing_date_mismatch'));

  // Same event described at two precisions is not a disagreement.
  const near = analyse(report({accounts: [acct({})],
    publicRecords: [rec('Equifax', 'Mar 01, 2021'), rec('TransUnion', 'Mar 04, 2021')]}));
  R.check('and not on three days apart', !has(near, 'public_record_filing_date_mismatch'));

  const lien = analyse(report({accounts: [acct({})],
    publicRecords: [rec('Equifax', 'Mar 04, 2021', 'lien'), rec('Experian', 'Nov 02, 2021', 'lien')]}));
  R.check('works for a lien too', has(lien, 'public_record_filing_date_mismatch'));
  const lhit = one(lien, 'public_record_filing_date_mismatch');
  if (lhit) R.check('and calls it a tax lien', /tax lien/.test(lhit.label), lhit.label);

  const oneBureau = analyse(report({accounts: [acct({})],
    publicRecords: [rec('Equifax', 'Mar 04, 2021'), rec(null, 'Sep 18, 2021')]}));
  R.check('a record with no bureau is never matched against another',
          !has(oneBureau, 'public_record_filing_date_mismatch'));
})();

// ------------------------------------------------------- 14. double jeopardy
R.section('one debt, two balances');
(function () {
  const f = analyse(report({
    accounts: [acct({creditor: 'SYNCB/AMAZON', status: 'Charge-off', is_charge_off: true,
                     balance: '$1,842',
                     per_bureau_fields: perBureau({account_status: 'Closed',
                       payment_status: 'Charge-off', payment_amount: '$0',
                       balance_owed: '$1,842', high_balance: '$2,400'})})],
    collections: [{agency: 'PORTFOLIO RECOVERY', original_creditor: 'SYNCB/AMAZON',
                   balance: '$1,842', bureau: 'Equifax', status: 'collection'}]
  }));
  R.check('original creditor and collector both claiming a balance fires',
          has(f, 'double_jeopardy_balance'));
  const hit = one(f, 'double_jeopardy_balance');
  if (hit) R.check('and names both', /PORTFOLIO RECOVERY/.test(hit.detail) &&
                                     /SYNCB\/AMAZON/.test(hit.detail));

  const zeroed = analyse(report({
    accounts: [acct({creditor: 'SYNCB/AMAZON', status: 'Charge-off', is_charge_off: true,
                     balance: '$0',
                     per_bureau_fields: perBureau({account_status: 'Closed',
                       payment_status: 'Charge-off', payment_amount: '$0',
                       balance_owed: '$0', high_balance: '$2,400'})})],
    collections: [{agency: 'PORTFOLIO RECOVERY', original_creditor: 'SYNCB/AMAZON',
                   balance: '$1,842', bureau: 'Equifax', status: 'collection'}]
  }));
  R.check('and not once the original creditor reports zero',
          !has(zeroed, 'double_jeopardy_balance'));

  const other = analyse(report({
    accounts: [acct({creditor: 'CHASE CARD', balance: '$1,842'})],
    collections: [{agency: 'PORTFOLIO RECOVERY', original_creditor: 'SYNCB/AMAZON',
                   balance: '$1,842', bureau: 'Equifax', status: 'collection'}]
  }));
  R.check('and never matches two different debts of the same size',
          !has(other, 'double_jeopardy_balance'));
})();

// --------------------------------------------- 16. late grids that disagree
R.section('late payments that differ between bureaus');
(function () {
  const f = analyse(report({accounts: [acct({
    creditor: 'CREDIT ONE BANK', has_late_payments: true,
    late_by_bureau: {Equifax: {d30: 2, d60: 1, d90: 0, d120: 0},
                     Experian: {d30: 2, d60: 2, d90: 0, d120: 0},
                     TransUnion: {d30: 2, d60: 1, d90: 0, d120: 0}}
  })]}));
  R.check('fires', has(f, 'late_grid_mismatch'));
  const hit = one(f, 'late_grid_mismatch');
  if (hit) R.check('and prints each bureau\'s figures', /Experian reports 2 at 30 days, 2 at 60 days/.test(hit.detail),
                   hit.detail.slice(0, 80));

  const agree = analyse(report({accounts: [acct({
    creditor: 'CREDIT ONE BANK', has_late_payments: true,
    late_by_bureau: {Equifax: {d30: 2, d60: 1, d90: 0, d120: 0},
                     Experian: {d30: 2, d60: 1, d90: 0, d120: 0},
                     TransUnion: {d30: 2, d60: 1, d90: 0, d120: 0}}
  })]}));
  R.check('and not when all three agree', !has(agree, 'late_grid_mismatch'));

  // The false positive this rule is most likely to invent: a bureau that does
  // not carry the account is absent, not on zero.
  const partial = analyse(report({accounts: [acct({
    creditor: 'CREDIT ONE BANK', has_late_payments: true,
    per_bureau_fields: perBureau({}, ['Equifax', 'Experian']),
    late_by_bureau: {Equifax: {d30: 2, d60: 1, d90: 0, d120: 0},
                     Experian: {d30: 2, d60: 1, d90: 0, d120: 0}}
  })]}));
  R.check('a bureau that does not report the account is not read as never-late',
          !has(partial, 'late_grid_mismatch'));

  const solo = analyse(report({accounts: [acct({
    creditor: 'CREDIT ONE BANK', has_late_payments: true,
    per_bureau_fields: perBureau({}, ['Equifax']),
    late_by_bureau: {Equifax: {d30: 2, d60: 1, d90: 0, d120: 0}}
  })]}));
  R.check('one bureau alone never produces a disagreement', !has(solo, 'late_grid_mismatch'));
})();

// ------------------------------------------ every new rule can build a letter
R.section('each new rule carries a dispute reason');
(function () {
  const RULES = ['past_due_on_transferred', 'late_payments_on_collection',
                 'notice_of_dispute_missing', 'status_update_not_moved',
                 'bankruptcy_court_not_reported', 'public_record_filing_date_mismatch',
                 'double_jeopardy_balance', 'late_grid_mismatch'];
  const src = api.SRC;
  RULES.forEach(r => {
    R.check(r + ' is in DR_RULE_MAP',
            new RegExp(r + '\\s*:|' + r + '\\s*\\n\\s*:').test(src));
  });
})();

// ------------------------------------------- the § 605B path, end to end
//
// Dave asked why MGC does not build the identity-theft letter. It does — but
// only once the consumer has marked which accounts are not theirs, because the
// letter is sworn under penalty of perjury and nothing here will assemble a
// sworn statement out of the derogatory list. That gate is correct and it is
// why an earlier harness run, which ticked the intake box and marked nothing,
// saw no letter and made it look broken. This proves both halves.
R.section('the § 605B block letter, for someone who really is a victim');
(function () {
  const idtApi = H.load(['accountKey', 'renderIdentityTheftWalkthrough', 'reviewedAccounts']);
  const parsed = idtApi.parseCreditReport(H.fixture('michelle.txt'));
  if (!parsed || !(parsed.accounts || []).length) {
    R.check('fixture parsed', false, 'no accounts'); return;
  }

  // Nothing marked: no letter, and the walkthrough says why.
  const st1 = H.session(idtApi, {situation: 'idtheft', special_flags: ['identity_theft']});
  st1.upload = {parsed: parsed};
  idtApi.runAnalysis();
  st1.analysis.letters = idtApi.determineLetterPacket(st1.analysis);
  const ids1 = (st1.analysis.letters || []).map(l => l.id);
  R.check('nothing marked yet — no sworn letter is produced',
          ids1.indexOf('idtheft_block') < 0);
  R.check('and the fraud alert still goes out immediately', ids1.indexOf('fraud_alert') >= 0);
  const walk1 = String(idtApi.renderIdentityTheftWalkthrough() || '');
  R.check('Step 5 says the letter is not built yet', /not built yet/i.test(walk1));
  R.check('and says what builds it', /Never mine/i.test(walk1));
  R.check('and does not still promise a letter that is not there',
          !/mail the § 605B Block letter we&#39;ve generated|we’ve generated \(above\)/.test(
            walk1.split('not built yet')[0] || ''));

  // One account marked "never mine": the letter appears, naming it.
  const st2 = H.session(idtApi, {situation: 'idtheft', special_flags: ['identity_theft']});
  st2.upload = {parsed: parsed};
  const victimOf = parsed.accounts[0];
  st2.itemReview.accounts[idtApi.accountKey(victimOf, 0)] = 'never';
  st2.itemReview.reviewed = true;
  idtApi.runAnalysis();
  st2.analysis.letters = idtApi.determineLetterPacket(st2.analysis);
  const ids2 = (st2.analysis.letters || []).map(l => l.id);
  R.check('one account marked "never mine" — the § 605B letter is built',
          ids2.indexOf('idtheft_block') >= 0, ids2.join(', '));

  idtApi.regenerateAllLetters();
  const out = st2.letterOutputs['idtheft_block'] || {};
  const mail = String(out.mail || '');
  R.check('and it names that account', mail.indexOf(victimOf.creditor) >= 0,
          victimOf.creditor);
  R.check('and no FTC number is invented when none was entered',
          !/Report Number:\s*\S/.test(mail));

  // With a number entered, it prints — the same live-rebuild round two uses.
  st2.ftcReportNumber = 'FTC-2026-114477';
  idtApi.regenerateAllLetters();
  const withNum = String((st2.letterOutputs['idtheft_block'] || {}).mail || '');
  R.check('entering the FTC number puts it in the letter',
          withNum.indexOf('FTC-2026-114477') >= 0);
  const walk2 = String(idtApi.renderIdentityTheftWalkthrough() || '');
  R.check('and Step 5 now confirms what it was built from',
          /Built from what you marked/i.test(walk2));

  // Both found by driving the live page, neither visible to a harness that
  // renders the walkthrough on its own.
  //
  // 1. The "Take me there" button scrolled to #item-review — which is on the
  //    ANALYSIS step, while the walkthrough renders on the LETTERS step. The
  //    element is display:none at that moment and scrollIntoView on a hidden
  //    element does nothing. The button was dead.
  R.check('the review button changes step rather than scrolling to a hidden node',
          /goToItemReview\(\)/.test(walk1) && /function goToItemReview/.test(idtApi.SRC));
  R.check('and goToItemReview shows the analysis step first',
          /function goToItemReview[\s\S]{0,220}showStep\('analysis'\)/.test(idtApi.SRC));

  // 2. The enclosure line said "mail the § 605B Block letter we've generated
  //    (above)" directly beneath a red block saying the letter is not built.
  R.check('the enclosure line does not promise a letter that is not built',
          !/mail the § 605B Block letter/i.test(walk1));
  R.check('and does say to mail it once it is', /Mail the § 605B Block letter above/i.test(walk2));
})();

// Entering the FTC number rebuilt the letters and left everything around them
// stale — the walkthrough still read "No FTC report number entered yet", and an
// already-built plan still carried the separator sheet telling the victim to
// hold the letter. That sheet is the one that costs them the four-business-day
// clock once the number is actually in hand.
R.section('entering the FTC number refreshes what is on screen, not just the letter');
(function () {
  const src = api.SRC;
  R.check('there is a refresh helper', /function refreshIdentityTheftViews/.test(src));
  R.check('it regenerates the letters', /refreshIdentityTheftViews[\s\S]{0,400}regenerateAllLetters/.test(src));
  R.check('it re-renders the letters step', /refreshIdentityTheftViews[\s\S]{0,700}renderLetterPacket/.test(src));
  R.check('and rebuilds an already-built plan',
          /refreshIdentityTheftViews[\s\S]{0,1100}state\.planHtml[\s\S]{0,120}buildActionPlanDoc/.test(src));
  R.check('the FTC input calls it on change',
          /id="ftc-report-number"[\s\S]{0,260}onchange="refreshIdentityTheftViews\(\)"/.test(src));
  R.check('and still updates the letter on every keystroke',
          /id="ftc-report-number"[\s\S]{0,200}oninput="state\.ftcReportNumber[\s\S]{0,60}regenerateAllLetters/.test(src));
  // On input rather than on change would destroy the field mid-typing.
  R.check('but does not re-render while they are still typing in the field',
          !/oninput="[^"]*refreshIdentityTheftViews/.test(src));
  R.check('the police-report toggle uses the same refresh',
          /function setPoliceReport[\s\S]{0,420}refreshIdentityTheftViews/.test(src));
})();

// Also found on screen and not in any assertion: the review printed
// "balance $$1,412". acc.balance is a number from the columnar parser and a
// string like "$1,412" from the three-bureau one, and toLocaleString() on a
// string returns the string, so prefixing "$" doubled it on every three-bureau
// report — on the one screen where someone decides whether an account is
// theirs.
// A § 623(b) letter for a tradeline whose account number the report did not
// carry printed "Account ending [XXXX]". Every real fixture has numbers on
// every account, so no harness had ever built this letter without one.
R.section('a missing account number does not become a bracket');
(function () {
  const fdApi = H.load(['buildLetterContext']);
  const st = H.session(fdApi, {});
  st.upload = {parsed: {
    format: 'three_bureau', bureaus: BUREAUS.slice(), inquiries: [], collections: [],
    publicRecords: [], scores: [], personal: {},
    accounts: [acct({creditor: 'HARBOR POINT CARD', account_number: '',
      status: 'Late 60 Days', has_late_payments: true,
      late_counts: {d30: 3, d60: 1, d90: 0, d120: 0},
      per_bureau_fields: perBureau({account_status: 'Late 60 Days',
        payment_status: 'Late 60 Days', past_due: '$180'})})]
  }};
  fdApi.runAnalysis();
  st.analysis.letters = fdApi.determineLetterPacket(st.analysis);
  fdApi.regenerateAllLetters();
  const copies = st.letterVariants['furnisher_dispute'] ||
                 [st.letterOutputs['furnisher_dispute']].filter(Boolean);
  R.check('the § 623(b) letter is built', copies.length > 0, copies.length + ' copies');
  copies.forEach((o, i) => {
    const mail = String(o.mail || '');
    R.check('copy ' + (i + 1) + ' carries no bracket', !/\[[^\]]{2,60}\]/.test(mail),
            (mail.match(/\[[^\]]{2,60}\]/g) || []).slice(0, 2).join(' '));
    R.check('copy ' + (i + 1) + ' still names the creditor', /HARBOR POINT CARD/i.test(mail));
  });

  // And where the number IS there, it is still printed.
  const st2 = H.session(fdApi, {});
  st2.upload = {parsed: {
    format: 'three_bureau', bureaus: BUREAUS.slice(), inquiries: [], collections: [],
    publicRecords: [], scores: [], personal: {},
    accounts: [acct({creditor: 'HARBOR POINT CARD', account_number: '4417',
      status: 'Late 60 Days', has_late_payments: true,
      late_counts: {d30: 3, d60: 1, d90: 0, d120: 0},
      per_bureau_fields: perBureau({account_status: 'Late 60 Days',
        payment_status: 'Late 60 Days', past_due: '$180'})})]
  }};
  fdApi.runAnalysis();
  st2.analysis.letters = fdApi.determineLetterPacket(st2.analysis);
  fdApi.regenerateAllLetters();
  const c2 = st2.letterVariants['furnisher_dispute'] ||
             [st2.letterOutputs['furnisher_dispute']].filter(Boolean);
  R.check('a report that does carry the number still prints it',
          c2.some(o => /account ending 4417/i.test(String(o.mail || ''))));
})();

R.section('the item review prints money once');
(function () {
  const revApi = H.load(['renderItemReview']);
  ['jose_santiago.txt', 'michelle.txt', 'smartcredit3.txt', 'mg_experian.txt'].forEach(f => {
    const text = H.fixture(f);
    if (!text) { R.check(f + ' present', false, 'missing'); return; }
    const st = H.session(revApi, {});
    st.upload = {parsed: revApi.parseCreditReport(text)};
    revApi.runAnalysis();
    const html = String(revApi.renderItemReview() || '');
    const doubled = (html.match(/\$\$/g) || []).length;
    R.check(f + ' — no doubled dollar sign', doubled === 0, doubled + ' found');
  });
})();

R.done();
