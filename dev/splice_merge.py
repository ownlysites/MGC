import io

P = '/Users/daveivery/Documents/Claude/Projects/MGC/index.html'
s = io.open(P, encoding='utf-8').read()
orig = len(s)

def rep(anchor, new, count=1, label=''):
    global s
    n = s.count(anchor)
    assert n == count, 'anchor %r found %d times (expected %d) :: %s' % (anchor[:70], n, count, label)
    s = s.replace(anchor, new, count)
    print('  ok  ' + (label or anchor[:50]))

# ------------------------------------------------------------------------
# 1. matching + the per-bureau field map
# ------------------------------------------------------------------------
A = """function acctKey(a) {
  const n = (a.account_number || '').replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  return n.length >= 4 ? n : null;
}"""

B = r"""function acctKey(a) {
  const n = (a.account_number || '').replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  return n.length >= 4 ? n : null;
}

// ========== MATCHING THE SAME ACCOUNT ACROSS THREE REPORTS ==========
// Somebody who pulls Experian, Equifax and TransUnion separately has three
// files describing one credit file, and merging them is the only way they get
// the strongest dispute there is: a contradiction on the face of their own
// report. Until now the merge matched on the account number alone and dropped
// the per-bureau field map, so on a real set — Michael Gibson's three reports
// from one day — it merged 97 accounts down to 51, matched 23 across bureaus,
// and found exactly zero contradictions. The feature was silently dead.
//
// Matching on the name is unavoidable, because the bureaus mask account numbers
// differently, and it is genuinely hard because they do not agree on names:
//
//     FREEDOM MORTGAGE CORP  /  FREEDOM MORTGAGE  /  FREEDOM MTG
//     CREDIT ONE BANK NA     /  CREDIT ONE BANK   /  CREDITONEBNK
//     GM FINANCIAL           /  GMFNANCIAL        /  GM FINANCIAL
//
// Equifax also truncates at twenty characters. On that set exactly ONE name
// matches exactly across all three.
//
// The danger runs the other way too. A wrong pairing does not produce a missing
// dispute, it produces an INVENTED one — a letter telling a bureau that two of
// them disagree about an account when they are describing different accounts.
// That is worse than not merging at all. So the rule is: merge only when
// confident, and when two accounts cannot be told apart, leave them separate.
function mgcCredNorm(s) {
  return String(s == null ? '' : s).toUpperCase().replace(/[^A-Z0-9]/g, '');
}

// Bounded edit distance. Stops as soon as it exceeds the cap, so it stays cheap.
function mgcEdit(a, b, cap) {
  if (Math.abs(a.length - b.length) > cap) return cap + 1;
  let prev = [];
  for (let j = 0; j <= b.length; j++) prev[j] = j;
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    let best = i;
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (cur[j] < best) best = cur[j];
    }
    if (best > cap) return cap + 1;
    prev = cur;
  }
  return prev[b.length];
}

function credSimilar(an, bn) {
  const x = mgcCredNorm(an), y = mgcCredNorm(bn);
  if (!x || !y) return false;
  if (x === y) return true;
  const short = Math.min(x.length, y.length);
  if (short < 4) return false;
  // Truncation: Equifax cuts the name off, so one is the start of the other.
  if (x.slice(0, short) === y.slice(0, short)) return true;
  if (x.indexOf(y) >= 0 || y.indexOf(x) >= 0) return true;
  // A typo or a dropped letter — GMFNANCIAL against GMFINANCIAL.
  if (Math.abs(x.length - y.length) <= 3 && mgcEdit(x, y, 2) <= 2) return true;
  // A shared opening long enough not to be a coincidence — CREDITONEB.
  let i = 0;
  while (i < short && x[i] === y[i]) i++;
  return i >= 7;
}

// true  — the numbers agree
// false — the numbers disagree, so these are different accounts
// null  — one or both are unusable, so the number decides nothing
function acctNumAgrees(a, b) {
  const x = String(a.account_number || '').replace(/[^0-9]/g, '');
  const y = String(b.account_number || '').replace(/[^0-9]/g, '');
  if (x.length < 4 || y.length < 4) return null;
  if (x.slice(-4) === y.slice(-4)) return true;
  if (x.slice(0, 4) === y.slice(0, 4)) return true;
  return false;
}

// The shape findFactualInconsistencies and findContradictions actually read.
// A single-bureau account carries these as flat fields; this is the same values
// filed under the bureau that reported them, which is what makes a disagreement
// between two of them visible at all.
function perBureauFieldsFrom(a, bureau) {
  if (!bureau) return null;
  const f = {};
  const put = (k, v) => { if (v !== null && v !== undefined && v !== '') f[k] = v; };
  put('account_status',    a.open_closed || a.status);
  put('account_rating',    a.status);
  put('payment_status',    a.status);
  put('creditor_remarks',  Array.isArray(a.comments) ? a.comments.join(' ') : a.comments);
  put('payment_amount',    a.monthly_payment);
  put('balance_owed',      a.balance);
  put('high_balance',      a.high_balance || a.high_credit);
  put('credit_limit',      a.credit_limit);
  put('past_due',          a.past_due);
  put('date_opened',       a.date_opened);
  put('date_last_activity', a.date_last_activity);
  put('date_last_paid',    a.date_last_payment);
  put('dofd',              a.dofd);
  const out = {};
  out[bureau] = f;
  return out;
}"""
rep(A, B, 1, 'matching helpers')

# ------------------------------------------------------------------------
# 2. use them in the merge
# ------------------------------------------------------------------------
A = """    (p.accounts || []).forEach(a => {
      const k = acctKey(a);
      if (k && byKey[k]) {
        const t = byKey[k];"""
B = """    (p.accounts || []).forEach(a => {
      const k = acctKey(a);
      // Exact account-number hit first, then a confident name match. findMate
      // returns nothing when two candidates cannot be told apart, which leaves
      // the account separate rather than guessing which one it is.
      let mate = (k && byKey[k]) ? byKey[k] : null;
      if (!mate) {
        const cands = merged.accounts.filter(t =>
          credSimilar(t.creditor, a.creditor) &&
          (t.reported_by || []).indexOf(bureau) < 0 &&   // never merge within one bureau
          acctNumAgrees(t, a) !== false);
        const numbered = cands.filter(t => acctNumAgrees(t, a) === true);
        if (numbered.length === 1) mate = numbered[0];
        else if (numbered.length === 0 && cands.length === 1) mate = cands[0];
        // more than one candidate and nothing to separate them: leave it alone
      }
      if (mate) {
        const t = mate;"""
rep(A, B, 1, 'fuzzy mate')

A = """        if (bureau) t.per_bureau = (t.per_bureau || []).concat([{bureau: bureau, status: a.status, balance: a.balance}]);
      } else {"""
B = """        if (bureau) t.per_bureau = (t.per_bureau || []).concat([{bureau: bureau, status: a.status, balance: a.balance}]);
        // The whole point of merging. Without this the contradiction detectors
        // get one bureau's worth of fields and find nothing to compare.
        if (bureau) {
          const pf = perBureauFieldsFrom(a, bureau);
          if (pf) { t.per_bureau_fields = t.per_bureau_fields || {}; t.per_bureau_fields[bureau] = pf[bureau]; }
        }
        // Keep every name the bureaus used. The letters name one account that
        // three companies spell three ways, and the person has to recognise it.
        const anAlias = String(a.creditor || '').trim();
        if (anAlias && anAlias !== t.creditor) {
          t.creditor_aliases = t.creditor_aliases || [];
          if (t.creditor_aliases.indexOf(anAlias) < 0) t.creditor_aliases.push(anAlias);
        }
      } else {"""
rep(A, B, 1, 'per-bureau fields on merge')

A = """        copy.per_bureau = bureau ? [{bureau: bureau, status: a.status, balance: a.balance}] : [];
        merged.accounts.push(copy);
        if (k) byKey[k] = copy;"""
B = """        copy.per_bureau = bureau ? [{bureau: bureau, status: a.status, balance: a.balance}] : [];
        const pf0 = perBureauFieldsFrom(a, bureau);
        copy.per_bureau_fields = pf0 || a.per_bureau_fields || null;
        if (bureau && copy.reported_by.indexOf(bureau) < 0) copy.reported_by.push(bureau);
        merged.accounts.push(copy);
        if (k) byKey[k] = copy;"""
rep(A, B, 1, 'per-bureau fields on first sight')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
