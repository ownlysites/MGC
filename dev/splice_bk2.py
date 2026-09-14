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

# ---- 1. the agency name varies the same way a creditor name does ----
A = """    const key = amount
      ? 'A|' + agency + '|' + amount
      : (c.original_creditor ? 'O|' + agency + '|' + norm(c.original_creditor) : null);
    if (!key) { out.push(c); return; }
    if (byKey[key]) {
      const t = byKey[key];"""
B = """    const key = amount
      ? 'A|' + agency + '|' + amount
      : (c.original_creditor ? 'O|' + agency + '|' + norm(c.original_creditor) : null);
    if (!key) { out.push(c); return; }
    // "LVNV FUNDING" and "LVNV FUNDING LLC" are one agency, so an exact key
    // still left Jose Santiago with seven collections for four debts. Same
    // balance and a name that matches the way creditor names match is the same
    // debt, reported by two bureaus that write the agency differently.
    let hitKey = byKey[key] ? key : null;
    if (!hitKey && amount && typeof credSimilar === 'function') {
      const same = Object.keys(byKey).filter(k2 =>
        k2.charAt(0) === 'A' && k2.slice(k2.lastIndexOf('|') + 1) === amount &&
        credSimilar(k2.slice(2, k2.lastIndexOf('|')), agency));
      if (same.length === 1) hitKey = same[0];
    }
    if (hitKey) {
      const t = byKey[hitKey];"""
rep(A, B, 1, 'fuzzy agency dedupe')

A = """      ['original_creditor', 'date_reported', 'account_number', 'status', 'date_opened'].forEach(f => {
        if (!t[f] && c[f]) t[f] = c[f];
      });
      return;
    }"""
B = """      ['original_creditor', 'date_reported', 'account_number', 'status', 'date_opened'].forEach(f => {
        if (!t[f] && c[f]) t[f] = c[f];
      });
      // Keep the longer, more complete spelling of the agency — it is the one
      // that will match a mailing address.
      const an = String(c.agency || c.creditor || '');
      const tn = String(t.agency || t.creditor || '');
      if (an.length > tn.length) { if (t.agency) t.agency = an; else t.creditor = an; }
      return;
    }"""
rep(A, B, 1, 'keep the fuller agency name')

# ---- 2. the two remaining bankruptcy letters ----
A = """  const filingDate = ctx.filingDate || null;
  const caseNumber = ctx.caseNumber || null;"""
B = """  const filingDate = ctx.filingDate || null;
  const caseNumber = ctx.caseNumber || null;
  // These go to a collector, so they fan out like every other collector letter
  // rather than printing "[Collector]" into an envelope.
  const bkCollector = ctx.collector || {name: '', addr: ''};
  const bkCollName = typeof bkCollector === 'string' ? bkCollector : (bkCollector.name || '');
  const bkCollAddr = typeof bkCollector === 'object' ? (bkCollector.addr || '') : '';"""
rep(A, B, 1, 'stay letter collector')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
