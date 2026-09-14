
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

A = """function findPublicRecordDefects(parsed) {"""
B = """// ========== DOUBLE JEOPARDY ==========
// One debt, two balances. When a charged-off account is sold or assigned, the
// original creditor's tradeline should report a zero balance and the collection
// agency reports what is owed — the debt moved, it did not multiply. A report
// showing a balance on both is claiming the consumer owes the same money twice,
// and it is counted twice in every utilisation and total-debt figure a lender
// sees.
//
// The cheat sheets call this double jeopardy. Their one-line version is "only
// the account-holder should report the balance", which is ambiguous between
// this and the authorized-user argument; this implements the reading that is an
// arithmetic inaccuracy on the face of the report rather than a contested legal
// claim about whose debt it is.
//
// Matching is by the collection's own stated original creditor, never by
// balance alone: two different debts of the same size are not one debt.
function findDoubleJeopardy(parsed) {
  const out = [];
  const accounts = (parsed && parsed.accounts) || [];
  const collections = (parsed && parsed.collections) || [];
  if (!accounts.length) return out;

  const money = v => {
    if (v === null || v === undefined) return null;
    const m = String(v).replace(/[$,]/g, '').match(/-?\\d+(\\.\\d+)?/);
    return m ? parseFloat(m[0]) : null;
  };

  // Every claim of an amount owed, from either side of the report.
  const claims = [];
  collections.forEach(c => {
    const orig = c.original_creditor || '';
    if (!orig) return;
    const bal = money(c.balance);
    if (!(bal > 0)) return;
    claims.push({orig: orig, who: c.agency || c.creditor || 'a collection agency',
                 amount: bal, kind: 'collection'});
  });
  accounts.filter(a => a && a.is_collection && a.original_creditor).forEach(a => {
    const bal = money(a.balance);
    if (!(bal > 0)) return;
    claims.push({orig: a.original_creditor, who: a.creditor || 'a collection agency',
                 amount: bal, kind: 'collection'});
  });
  if (!claims.length) return out;

  accounts.forEach(a => {
    if (!a || !a.creditor || a.is_collection) return;
    const bal = money(a.balance);
    if (!(bal > 0)) return;
    const hit = claims.find(c =>
      typeof credSimilar === 'function' ? credSimilar(mgcCredNorm(c.orig), mgcCredNorm(a.creditor))
                                        : mgcCredNorm(c.orig) === mgcCredNorm(a.creditor));
    if (!hit) return;
    out.push({
      rule: 'double_jeopardy_balance',
      creditor: a.creditor, account: a.account_number || '',
      reason: 'balance', impact: 2,
      label: 'This debt is reporting a balance twice',
      detail: a.creditor + ' still reports a balance of $' + bal + ' on this account, and ' +
              hit.who + ' reports $' + hit.amount + ' owed on the same debt as a collection. ' +
              'A debt that was sold or assigned moved; it did not become two debts. One of ' +
              'these balances has to be zero, and it is the original creditor\\'s — they no ' +
              'longer hold the account. Until then this is counted twice in every total a ' +
              'lender sees.',
      bureaus: Object.keys(a.per_bureau_fields || {})
    });
  });

  return out;
}

function findPublicRecordDefects(parsed) {"""
rep(A, B, 1, 'findDoubleJeopardy')

A = """  double_jeopardy_x_placeholder"""
# no-op guard removed; add the DR map entry instead
A = """  bankruptcy_court_not_reported:  {outcome: 'Delete',  element: 'status',                  defect: 'incomplete'},"""
B = """  bankruptcy_court_not_reported:  {outcome: 'Delete',  element: 'status',                  defect: 'incomplete'},
  double_jeopardy_balance:        {outcome: 'Update',  element: 'balance',                 defect: 'inaccurate'},"""
rep(A, B, 1, 'DR_RULE_MAP: double jeopardy')

A = """  analysis.factual = dedupeFactual(
    findFactualInconsistencies(parsed).concat(findPublicRecordDefects(parsed)));"""
B = """  analysis.factual = dedupeFactual(
    findFactualInconsistencies(parsed)
      .concat(findDoubleJeopardy(parsed))
      .concat(findPublicRecordDefects(parsed)));"""
rep(A, B, 1, 'wire double jeopardy into the analysis')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
