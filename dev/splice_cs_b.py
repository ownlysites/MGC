
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

# ---- a date parser that accepts every shape the parsers produce ----
A = """function fiParseDate(v) {
  const m = String(v).match(/^(\\d{1,2})\\/(\\d{1,2})\\/(\\d{4})$/);
  if (!m) return null;
  const d = new Date(+m[3], +m[1] - 1, +m[2]);
  return isNaN(d.getTime()) ? null : d;
}"""
B = """function fiParseDate(v) {
  const m = String(v).match(/^(\\d{1,2})\\/(\\d{1,2})\\/(\\d{4})$/);
  if (!m) return null;
  const d = new Date(+m[3], +m[1] - 1, +m[2]);
  return isNaN(d.getTime()) ? null : d;
}

// The day-31 checks compare a report date against the date the consumer says
// they mailed round one, and those two dates arrive in different shapes: the
// intake date field is ISO, while a parsed report date is "May 30, 2023" on one
// format and "05/30/2023" on another. fiParseDate is deliberately strict
// because the cross-bureau comparison must not guess at a date it cannot read;
// this one is for the two places where a wider read is correct.
const FI_MONTHS = {jan:0, feb:1, mar:2, apr:3, may:4, jun:5,
                   jul:6, aug:7, sep:8, oct:9, nov:10, dec:11};
function fiAnyDate(v) {
  const s = String(v == null ? '' : v).trim();
  if (!s) return null;
  const iso = s.match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
  if (iso) {
    const d = new Date(+iso[1], +iso[2] - 1, +iso[3]);
    return isNaN(d.getTime()) ? null : d;
  }
  const slash = fiParseDate(s);
  if (slash) return slash;
  const named = s.match(/^([A-Za-z]{3})[a-z]*\\.?\\s+(\\d{1,2}),?\\s*(\\d{4})$/);
  if (named) {
    const mo = FI_MONTHS[named[1].toLowerCase()];
    if (mo === undefined) return null;
    const d = new Date(+named[3], mo, +named[2]);
    return isNaN(d.getTime()) ? null : d;
  }
  const monthYear = s.match(/^([A-Za-z]{3})[a-z]*\\.?\\s+(\\d{4})$/);
  if (monthYear) {
    const mo = FI_MONTHS[monthYear[1].toLowerCase()];
    if (mo === undefined) return null;
    const d = new Date(+monthYear[2], mo, 1);
    return isNaN(d.getTime()) ? null : d;
  }
  return null;
}
function fiDaysBetween(a, b) {
  return Math.floor((b.getTime() - a.getTime()) / 86400000);
}

// Whether a tradeline carries the § 623(a)(3) dispute notation. The exact
// wording differs by furnisher and by bureau, so this matches the shapes that
// actually appear rather than one canonical string.
const FI_DISPUTE_NOTE = /(consumer|customer)\\s+disput|disputed\\s+by\\s+(consumer|customer)|dispute\\s+resolved|account\\s+information\\s+disputed|disputes?\\s+this\\s+account|now\\s+resolved.*reported\\s+by\\s+(consumer|subscriber)/i;
function fiHasDisputeNote(acc) {
  const hay = [(acc.comments || []).join(' '), fiText(acc.status),
               fiText(acc.payment_status), fiText(acc.creditor_remarks)].join(' ');
  return FI_DISPUTE_NOTE.test(hay);
}"""
rep(A, B, 1, 'fiAnyDate + dispute-note detector')

# ---- the two day-31 rules ----
A = """    // A third-party collection is not an account you have a payment schedule"""
B = """    // ---- the two day-31 checks, run rather than recommended ----
    //
    // The packet has always told people to pull a fresh report on day 31 and
    // look for these two things by hand. In round two we have both halves: the
    // date they say round one was received, and a report pulled since. So look.
    //
    // Both are violations regardless of whether the dispute succeeded, which is
    // what makes them worth more than the deletion that was asked for.
    if (typeof r2Active === 'function' && r2Active() && r2MailedOn()) {
      const mailed = fiAnyDate(r2MailedOn());
      const r2s = (typeof r2Status === 'function') ? r2Status(acc.creditor) : null;
      const reported = fiAnyDate(acc.date_reported);

      // 1. NOTICE OF DISPUTE — FCRA § 623(a)(3), 15 U.S.C. § 1681s-2(a)(3).
      // A furnisher that knows an account is disputed must say so when it
      // reports it. Thirty days after the bureau received the dispute the
      // notation should be on the tradeline. The report in hand has to have
      // been pulled after day 30 for its silence to mean anything.
      if (mailed && r2s && !R2_ROUND_ONE_ONLY[r2s] && reported &&
          fiDaysBetween(mailed, reported) >= 30 && !fiHasDisputeNote(acc)) {
        out.push({rule: 'notice_of_dispute_missing', creditor: acc.creditor, account: acc.account_number,
          reason: 'notice_of_dispute', impact: FACT_IMPACT.notice_of_dispute,
          label: 'The dispute notation never appeared on this account',
          detail: 'You disputed this on ' + r2LongDate(r2MailedOn()) + '. This report was last ' +
                  'updated ' + fiText(acc.date_reported) + ', more than thirty days later, and the ' +
                  'tradeline still carries no note that the account is disputed. FCRA § 623(a)(3) ' +
                  'requires a furnisher who knows of a dispute to report it as disputed. That ' +
                  'omission is a violation on its own, separately from whether the account is accurate.',
          bureaus: Object.keys(per)});
      }

      // 2. DATE LAST REPORTED. If the answer was "verified", something was
      // examined on some date, and the date the account was last reported
      // should have moved to it. A tradeline that comes back verified with its
      // last-reported date still sitting before the dispute says nobody looked.
      if (mailed && reported && (r2s === 'verified' || r2s === 'frivolous') &&
          fiDaysBetween(mailed, reported) < 0) {
        out.push({rule: 'status_update_not_moved', creditor: acc.creditor, account: acc.account_number,
          reason: 'status_update', impact: FACT_IMPACT.status_update,
          label: 'Reported as verified, but the last-reported date never moved',
          detail: 'The bureau says this account was verified after your dispute of ' +
                  r2LongDate(r2MailedOn()) + ', yet it is still reporting ' +
                  fiText(acc.date_reported) + ' as the date it was last reported — before the ' +
                  'dispute was even received. A verification is an examination on a date. If ' +
                  'nothing about the date changed, nothing was examined, and that goes directly ' +
                  'to whether the reinvestigation was reasonable under FCRA § 611.',
          bureaus: Object.keys(per)});
      }
    }

    // A third-party collection is not an account you have a payment schedule"""
rep(A, B, 1, 'day-31 checks')

A = """  late_payments_on_collection:    {outcome: 'Delete',  element: 'activity after close date', defect: 'inaccurate'},"""
B = """  late_payments_on_collection:    {outcome: 'Delete',  element: 'activity after close date', defect: 'inaccurate'},
  notice_of_dispute_missing:      {outcome: 'Delete',  element: 'notice of dispute',        defect: 'missing'},
  status_update_not_moved:        {outcome: 'Delete',  element: 'status',                  defect: 'inaccurate'},"""
rep(A, B, 1, 'DR_RULE_MAP: day-31 rules')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
