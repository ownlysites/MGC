
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

# ---- read the late grid per bureau instead of collapsing it to a max ----
A = """function tbMaxInt(s) {
  if (!s) return 0;
  const nums = (s.match(/\\b\\d+\\b/g) || []).map(Number);
  return nums.length ? Math.max.apply(null, nums) : 0;
}"""
B = """function tbMaxInt(s) {
  if (!s) return 0;
  const nums = (s.match(/\\b\\d+\\b/g) || []).map(Number);
  return nums.length ? Math.max.apply(null, nums) : 0;
}

// The same row, read as three values instead of one.
//
// "30 Days Past Due   2   0   2" is three bureaus disagreeing about how many
// times an account went thirty days late, and tbMaxInt threw that away to
// return 2. The disagreement is the finding: a payment either was or was not
// made on time, every furnisher reports to all three, and two bureaus giving
// different counts means at least one history is wrong.
//
// N/A is a bureau not reporting the account, which is not a count of zero.
function tbIntTriple(row) {
  if (!row) return [null, null, null];
  const toks = row.trim().split(/\\s+/);
  const out = [];
  for (const t of toks) {
    if (out.length >= 3) break;
    if (/^N\\/A$/i.test(t) || /^-$/.test(t)) { out.push(null); continue; }
    if (/^\\d+$/.test(t)) { out.push(parseInt(t, 10)); continue; }
  }
  while (out.length < 3) out.push(null);
  return out;
}"""
rep(A, B, 1, 'tbIntTriple')

A = """      // Per-bureau field map, in the same shape the columnar parser produces,"""
B = """      // Per-bureau late grid, in the same shape the columnar parser produces, so
      // one rule compares both formats. Only bureaus that report a count at all
      // appear — a bureau not carrying the account is absent, not on zero.
      late_by_bureau: (function () {
        const t30 = tbIntTriple(tbRow(blk, '30 Days Past Due'));
        const t60 = tbIntTriple(tbRow(blk, '60 Days Past Due'));
        const t90 = tbIntTriple(tbRow(blk, '90 Days Past Due'));
        const t120 = tbIntTriple(tbRow(blk, '120 Days Past Due'));
        const lbb = {};
        TB_BUREAU_COLS.forEach((b, i) => {
          if (t30[i] === null && t60[i] === null && t90[i] === null && t120[i] === null) return;
          lbb[b] = {d30: t30[i] || 0, d60: t60[i] || 0, d90: t90[i] || 0, d120: t120[i] || 0};
        });
        return lbb;
      })(),
      // Per-bureau field map, in the same shape the columnar parser produces,"""
rep(A, B, 1, 'three_bureau late_by_bureau')

# ---- the rule ----
A = """    // A 90-day late with no 30 or 60 before it is a sequence that cannot happen.
    const lb = acc.late_by_bureau || {};"""
B = """    // Late payments should be the same on all three. A payment either was or was
    // not made on time; the furnisher reports the same history to every bureau
    // it reports to. Two bureaus giving different counts is not a matter of
    // opinion — one of them is carrying a history the furnisher did not send,
    // and neither can be verified without producing the payment record.
    //
    // Only bureaus that report the account are compared, so a bureau that has
    // never carried it does not read as "zero lates" and manufacture a finding.
    const lbCmp = acc.late_by_bureau || {};
    const lbNames = Object.keys(lbCmp);
    if (lbNames.length >= 2) {
      const sig = b => ['d30', 'd60', 'd90', 'd120']
        .map(k => Number(lbCmp[b][k]) || 0).join('/');
      const sigs = [...new Set(lbNames.map(sig))];
      if (sigs.length > 1) {
        const worst = lbNames.map(b => ({b: b, t: ['d30', 'd60', 'd90', 'd120']
          .reduce((x, k) => x + (Number(lbCmp[b][k]) || 0), 0)}));
        const lo = Math.min(...worst.map(w => w.t));
        const hi = Math.max(...worst.map(w => w.t));
        out.push({rule: 'late_grid_mismatch', creditor: acc.creditor, account: acc.account_number,
          reason: 'first_delinquency', impact: FACT_IMPACT.first_delinquency,
          label: 'The bureaus report different late payments on this account',
          detail: lbNames.map(b => b + ' reports ' +
                    ['30', '60', '90', '120'].map((d, i) =>
                      (Number(lbCmp[b]['d' + d]) || 0) + ' at ' + d + ' days').join(', ')).join('; ') +
                  '. The same furnisher reports the same payment history to every bureau it ' +
                  'reports to, so these cannot all be right' +
                  (lo === 0 ? ' \\u2014 and one of them is showing this account as never late' : '') +
                  '. Ask each of them to produce the payment record behind its own figure.',
          bureaus: lbNames});
        void hi;
      }
    }

    // A 90-day late with no 30 or 60 before it is a sequence that cannot happen.
    const lb = acc.late_by_bureau || {};"""
rep(A, B, 1, 'late grid mismatch rule')

A = """  double_jeopardy_balance:        {outcome: 'Update',  element: 'balance',                 defect: 'inaccurate'},"""
B = """  double_jeopardy_balance:        {outcome: 'Update',  element: 'balance',                 defect: 'inaccurate'},
  late_grid_mismatch:             {outcome: 'Delete',  element: 'late payments',           defect: 'reporting inaccurate dates'},"""
rep(A, B, 1, 'DR_RULE_MAP: late grid')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
