
import io

P = '/Users/daveivery/Documents/Claude/Projects/MGC/index.html'
s = io.open(P, encoding='utf-8').read()
orig = len(s)

def rep(anchor, new, count=1, label=''):
    global s
    n = s.count(anchor)
    assert n == count, 'anchor %r found %d times (expected %d) :: %s' % (anchor[:80], n, count, label)
    s = s.replace(anchor, new, count)
    print('  ok  ' + (label or anchor[:50]))

# ---- the public-record rules ----
A = """// Every factual rule this app can fire, mapped to the one element it is really"""
B = """// ========== PUBLIC RECORDS: THE SAME TEST, APPLIED TO A COURT FILE ==========
// A public record is the one item on a credit report that has an independent,
// public original. Every other tradeline is the furnisher's word against the
// consumer's; a bankruptcy, a judgment or a tax lien exists in a court file
// anybody can pull. That makes two defects provable without arguing about the
// debt at all:
//
//   1. NO COURT. A bankruptcy is a court proceeding, and the court is the one
//      fact that makes the record checkable. A bureau reporting the record with
//      the Court column empty is reporting a proceeding it cannot have verified
//      against anything, and the consumer can say so without knowing a thing
//      about the filing.
//
//   2. DATES THAT DISAGREE. The filing date is stamped by the clerk. It is one
//      date. Two bureaus reporting the same record filed in different months
//      means at least one of them did not take it from the court, and the one
//      running late is holding the record past its own fall-off date.
//
// Both produce findings in exactly the shape findFactualInconsistencies does,
// so they flow into the same letters and the same dispute-reason vocabulary.
// creditor is the record's own description because a public record has no
// furnisher — the letter names the record, and the bureau is the recipient.
function prLabelFor(type) {
  const t = String(type || '').toLowerCase();
  if (/bankrupt/.test(t)) return 'bankruptcy';
  if (/judg/.test(t)) return 'judgment';
  if (/lien/.test(t)) return 'tax lien';
  return 'public record';
}

function prName(r) {
  const kind = prLabelFor(r.type);
  const ref = r.reference ? ' ' + r.reference : '';
  return kind.charAt(0).toUpperCase() + kind.slice(1) + ref;
}

function findPublicRecordDefects(parsed) {
  const out = [];
  const recs = (parsed && parsed.publicRecords) || [];
  if (!recs.length) return out;

  recs.forEach(r => {
    // Only where the layout actually has a Court column. A format that never
    // carried one says nothing about whether the bureau holds a court name,
    // and a finding built on that would be an assertion about a gap in our
    // parsing rather than a gap in their reporting.
    if (r.court_column && !r.court && /bankrupt/i.test(String(r.type || ''))) {
      out.push({
        rule: 'bankruptcy_court_not_reported',
        creditor: prName(r), account: r.reference || '',
        reason: 'not_mine', impact: 2,
        label: 'A bankruptcy is reported with no court named',
        detail: (r.bureau ? r.bureau + ' reports' : 'This report carries') +
                ' a bankruptcy filed ' + (r.date_filed || 'on a date it does not give') +
                (r.reference ? ', reference ' + r.reference : '') +
                ', and the Court field is blank. A bankruptcy is a proceeding in a named ' +
                'court, and the court is what makes the record verifiable. Reported without ' +
                'it, the record cannot have been checked against the court\\'s own file — which ' +
                'is what FCRA \\u00a7 611 requires the bureau to have done.',
        bureaus: r.bureau ? [r.bureau] : []
      });
    }
  });

  // Same record, two bureaus, two filing dates. Grouped by kind and reference
  // number; a record with no reference is not matched to anything, because
  // "the bankruptcy" on two bureaus could be two filings.
  const byRef = {};
  recs.forEach(r => {
    if (!r.reference || !r.bureau || !r.date_filed) return;
    const k = prLabelFor(r.type) + '|' + String(r.reference).toUpperCase();
    (byRef[k] = byRef[k] || []).push(r);
  });
  Object.keys(byRef).forEach(k => {
    const group = byRef[k];
    const bureaus = [...new Set(group.map(r => r.bureau))];
    if (bureaus.length < 2) return;
    if (!fiDatesDisagree(group.map(r => r.date_filed))) return;
    const kind = prLabelFor(group[0].type);
    out.push({
      rule: 'public_record_filing_date_mismatch',
      creditor: prName(group[0]), account: group[0].reference || '',
      reason: 'date_last_active', impact: 1,
      label: 'The bureaus report different filing dates for the same ' + kind,
      detail: group.map(r => r.bureau + ' reports it filed ' + r.date_filed).join('; ') +
              '. A filing date is stamped once by the court clerk. Whichever bureau has it ' +
              'wrong did not take the record from the court file, and if the later date is ' +
              'the wrong one the record is being held past the date it should come off.',
      bureaus: bureaus
    });
  });

  return out.sort((a, b) => a.impact - b.impact);
}

// Every factual rule this app can fire, mapped to the one element it is really"""
rep(A, B, 1, 'findPublicRecordDefects')

A = """  status_update_not_moved:        {outcome: 'Delete',  element: 'status',                  defect: 'inaccurate'},"""
B = """  status_update_not_moved:        {outcome: 'Delete',  element: 'status',                  defect: 'inaccurate'},
  bankruptcy_court_not_reported:  {outcome: 'Delete',  element: 'status',                  defect: 'incomplete'},
  public_record_filing_date_mismatch:
                                  {outcome: 'Delete',  element: 'date last active',        defect: 'reporting different dates'},"""
rep(A, B, 1, 'DR_RULE_MAP: public record rules')

A = """  analysis.factual = dedupeFactual(findFactualInconsistencies(parsed));"""
B = """  analysis.factual = dedupeFactual(
    findFactualInconsistencies(parsed).concat(findPublicRecordDefects(parsed)));"""
rep(A, B, 1, 'wire public-record defects into the analysis')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
