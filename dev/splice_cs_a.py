
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

# ---- 1. a collection has no payment schedule to be late on ----
A = """      // Transferred means the original creditor no longer holds it.
      if (/transferred/i.test(status) && (bal > 0 || due > 0)) {
        out.push({rule: 'balance_on_transferred', creditor: acc.creditor, account: acc.account_number,
          reason: 'balance', impact: FACT_IMPACT.balance,
          label: 'An account marked transferred is still reporting a balance',
          detail: b + ' shows this account as transferred and still reports ' +
                  (bal > 0 ? 'a balance of $' + bal : '$' + due + ' past due') +
                  '. Once an account is transferred, the original creditor reports no balance.',
          bureaus: [b]});
      }"""
B = """      // Transferred means the original creditor no longer holds it. Balance and
      // past due are two different assertions and two different disputes: one
      // says the original creditor still holds money on the account, the other
      // says a payment is overdue to a creditor who no longer owns the debt.
      // Firing one rule for both meant a report showing only a past due got a
      // finding that said "balance", and the dispute reason cited was the wrong
      // field — which is the one thing a furnisher can answer in a line.
      if (/transferred/i.test(status) && bal > 0) {
        out.push({rule: 'balance_on_transferred', creditor: acc.creditor, account: acc.account_number,
          reason: 'balance', impact: FACT_IMPACT.balance,
          label: 'An account marked transferred is still reporting a balance',
          detail: b + ' shows this account as transferred and still reports a balance of $' + bal +
                  '. Once an account is transferred, the original creditor reports no balance.',
          bureaus: [b]});
      }

      if (/transferred/i.test(status) && due > 0) {
        out.push({rule: 'past_due_on_transferred', creditor: acc.creditor, account: acc.account_number,
          reason: 'balance', impact: FACT_IMPACT.balance,
          label: 'An account marked transferred is still reporting a past-due amount',
          detail: b + ' shows this account as transferred and still reports $' + due +
                  ' past due. A past due is money owed to the creditor reporting it, and a ' +
                  'creditor that transferred the account is no longer owed anything on it.',
          bureaus: [b]});
      }"""
rep(A, B, 1, 'split past-due off transferred')

# ---- 2. late marks on a collection tradeline ----
A = """    // A 90-day late with no 30 or 60 before it is a sequence that cannot happen.
    const lb = acc.late_by_bureau || {};"""
B = """    // A third-party collection is not an account you have a payment schedule
    // with, so there is nothing to be thirty days late on. Late marks on a
    // collection tradeline are payment history carried over from a closed
    // original account, or invented — either way the collection agency is
    // reporting activity on an account that closed before it ever held it.
    //
    // The cheat sheets call this "no late payments after close date". The close
    // date itself is not on every format and the late grid carries counts
    // rather than dated months, so this is not dated arithmetic — it is the
    // simpler point that the grid should not be there at all.
    const collLate = acc.late_counts || {};
    const collLateTotal = ['d30', 'd60', 'd90', 'd120', 'd150', 'd180']
      .reduce((t, k) => t + (Number(collLate[k]) || 0), 0);
    if (acc.is_collection && collLateTotal > 0) {
      out.push({rule: 'late_payments_on_collection', creditor: acc.creditor, account: acc.account_number,
        reason: 'activity_after_closed', impact: FACT_IMPACT.activity_after_closed,
        label: 'A collection account is reporting late payments',
        detail: 'This is reported as a collection and also carries ' + collLateTotal +
                ' late-payment mark(s). A collection agency has no payment arrangement with you ' +
                'to be late on, so the payment history on this tradeline belongs to a closed ' +
                'account and is being reported as activity on this one.',
        bureaus: Object.keys(per)});
    }

    // A 90-day late with no 30 or 60 before it is a sequence that cannot happen.
    const lb = acc.late_by_bureau || {};"""
rep(A, B, 1, 'late marks on a collection')

# ---- dispute-reason vocabulary for the two new rules ----
A = """  balance_on_transferred:         {outcome: 'Delete',  element: 'balance',                 defect: 'inaccurate'},"""
B = """  balance_on_transferred:         {outcome: 'Delete',  element: 'balance',                 defect: 'inaccurate'},
  past_due_on_transferred:        {outcome: 'Delete',  element: 'past due',                defect: 'inaccurate'},
  late_payments_on_collection:    {outcome: 'Delete',  element: 'activity after close date', defect: 'inaccurate'},"""
rep(A, B, 1, 'DR_RULE_MAP: two new rules')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
