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

# findContradictions reads per_bureau_status — a three-slot array aligned to
# TB_BUREAU_COLS — not per_bureau_fields. A merged report had to carry both or
# the cross-bureau comparison had nothing to compare.
A = """        if (bureau) {
          const pf = perBureauFieldsFrom(a, bureau);
          if (pf) { t.per_bureau_fields = t.per_bureau_fields || {}; t.per_bureau_fields[bureau] = pf[bureau]; }
        }"""
B = """        if (bureau) {
          const pf = perBureauFieldsFrom(a, bureau);
          if (pf) { t.per_bureau_fields = t.per_bureau_fields || {}; t.per_bureau_fields[bureau] = pf[bureau]; }
          setPerBureauStatus(t, bureau, a);
        }"""
rep(A, B, 1, 'status triple on merge')

A = """        const pf0 = perBureauFieldsFrom(a, bureau);
        copy.per_bureau_fields = pf0 || a.per_bureau_fields || null;"""
B = """        const pf0 = perBureauFieldsFrom(a, bureau);
        copy.per_bureau_fields = pf0 || a.per_bureau_fields || null;
        if (bureau) setPerBureauStatus(copy, bureau, a);"""
rep(A, B, 1, 'status triple on first sight')

A = """// The shape findFactualInconsistencies and findContradictions actually read."""
B = """// findContradictions compares a three-slot array aligned to TB_BUREAU_COLS,
// which is how a tri-merge report arrives. Three separate single-bureau files
// have to be assembled into the same shape or the comparison has nothing to
// compare — which is exactly why merging three real reports used to produce
// zero contradictions while the person was holding the evidence for them.
//
// The status written here is the one the bureau actually reported. Where a
// report gives no status but the account is plainly derogatory, the derogatory
// fact is used instead of leaving the slot empty, because an empty slot reads
// as "this bureau does not have this account" and that is a different claim.
function setPerBureauStatus(target, bureau, src) {
  const i = TB_BUREAU_COLS.indexOf(bureau);
  if (i < 0) return;
  if (!Array.isArray(target.per_bureau_status)) {
    target.per_bureau_status = [null, null, null];
  }
  let v = src.status || null;
  if (!v) {
    if (src.is_collection) v = 'Collection';
    else if (src.is_charge_off) v = 'Charge off';
    else if (src.is_repossession) v = 'Repossession';
    else if (src.has_late_payments) v = 'Late';
    else if (src.open_closed) v = src.open_closed;
  }
  if (v) target.per_bureau_status[i] = String(v).trim();
}

// The shape findFactualInconsistencies and findContradictions actually read."""
rep(A, B, 1, 'setPerBureauStatus')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
