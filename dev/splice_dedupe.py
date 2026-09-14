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

# ---- 1. one collection per debt, not one per bureau ----
A = """function canonBureauNames(result) {"""
B = r"""// A three-bureau report lists each collection once per bureau. Jose Santiago's
// file parsed as ten collections; he has four debts. LVNV Funding appears three
// times at $443, three times at $510 and three times at $1,651 — the same three
// debts as reported by Equifax, Experian and TransUnion.
//
// Telling somebody they have ten collections when they have four is wrong in
// the direction that frightens people, and it makes every count on the analysis
// screen and the plan cover wrong with it. Same agency and same balance is the
// same debt; where a balance is missing the agency and the original creditor
// have to match instead, and anything that cannot be told apart is left alone.
function dedupeCollections(result) {
  const list = result && result.collections;
  if (!Array.isArray(list) || list.length < 2) return result;
  const norm = v => String(v == null ? '' : v).toUpperCase().replace(/[^A-Z0-9]/g, '');
  const money = v => {
    const m = String(v == null ? '' : v).match(/[\d,]+(?:\.\d{2})?/);
    return m ? m[0].replace(/,/g, '') : '';
  };
  const byKey = {};
  const out = [];
  list.forEach(c => {
    const agency = norm(c.agency || c.creditor);
    const amount = money(c.balance);
    if (!agency) { out.push(c); return; }
    // Without a balance, fall back to the original creditor. With neither, keep
    // the row rather than collapsing two debts that might be different.
    const key = amount
      ? 'A|' + agency + '|' + amount
      : (c.original_creditor ? 'O|' + agency + '|' + norm(c.original_creditor) : null);
    if (!key) { out.push(c); return; }
    if (byKey[key]) {
      const t = byKey[key];
      t.reported_by = t.reported_by || [];
      [c.bureau].concat(c.reported_by || []).forEach(b => {
        if (b && t.reported_by.indexOf(b) < 0) t.reported_by.push(b);
      });
      ['original_creditor', 'date_reported', 'account_number', 'status', 'date_opened'].forEach(f => {
        if (!t[f] && c[f]) t[f] = c[f];
      });
      return;
    }
    const copy = Object.assign({}, c);
    copy.reported_by = [];
    [c.bureau].concat(c.reported_by || []).forEach(b => {
      if (b && copy.reported_by.indexOf(b) < 0) copy.reported_by.push(b);
    });
    byKey[key] = copy;
    out.push(copy);
  });
  result.collections = out;
  return result;
}

function canonBureauNames(result) {"""
rep(A, B, 1, 'dedupeCollections')

for old, new, lbl in [
    ("      if (tu && tu.accounts.length > 0) return canonBureauNames(tu);",
     "      if (tu && tu.accounts.length > 0) return dedupeCollections(canonBureauNames(tu));", 'tu'),
    ("      if (single && single.accounts.length > 0) return canonBureauNames(single);",
     "      if (single && single.accounts.length > 0) return dedupeCollections(canonBureauNames(single));", 'single'),
    ("      if (structured && structured.accounts.length > 0) return canonBureauNames(structured);",
     "      if (structured && structured.accounts.length > 0) return dedupeCollections(canonBureauNames(structured));", 'structured'),
    ("      if (columnar && columnar.accounts.length > 0) return canonBureauNames(columnar);",
     "      if (columnar && columnar.accounts.length > 0) return dedupeCollections(canonBureauNames(columnar));", 'columnar')]:
    rep(old, new, 1, 'dedupe at ' + lbl)

# ---- 2. no account listed twice in one letter ----
A = """  ctx.items = disputableItems.length > 0 ? disputableItems : [];"""
B = """  // One line per account per reason. Jose Santiago's bureau dispute listed
  // Credit One Bank twice because two rules reached the same conclusion about
  // the same account, and a letter that says the same thing twice reads as
  // careless to the person who has to answer it.
  const seenItem = {};
  const uniqueItems = [];
  disputableItems.forEach(it => {
    const k = String(it.creditor || '').toUpperCase() + '|' +
              String(it.account || '') + '|' + String(it.reason || '').slice(0, 80);
    if (seenItem[k]) return;
    seenItem[k] = 1;
    uniqueItems.push(it);
  });
  ctx.items = uniqueItems.length > 0 ? uniqueItems : [];"""
rep(A, B, 1, 'dedupe letter items')

# ---- 3. a bankruptcy on the report is a bankruptcy ----
A = """    bankruptcy: intake.special_flags && intake.special_flags.includes('bankruptcy'),"""
B = """    // A bankruptcy on the report is a bankruptcy whether or not the person
    // thought to tick the box. Jose Santiago's file carries a dismissed Chapter
    // filing from 2023 as a public record, and none of the bankruptcy handling
    // switched on because the intake flag was the only thing consulted.
    bankruptcy: (intake.special_flags && intake.special_flags.includes('bankruptcy')) ||
      ((parsed.publicRecords || []).some(r => /bankrupt|chapter\\s*(7|11|13)/i.test(
        String((r && (r.type || r.kind || r.description)) || '')))) ||
      ((parsed.accounts || []).some(a => a && a.in_bankruptcy)),"""
rep(A, B, 1, 'bankruptcy from the report')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
