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

# ---- 1. read the filing off the report ----
A = """function computeFlags(intake, upload) {"""
B = r"""// The bankruptcy public record, read off the report rather than asked for.
// A filing carries a date, a chapter, a case reference and — the part that
// decides which letter is honest — whether it was DISCHARGED or DISMISSED.
// Those are opposite outcomes. A discharge wipes the debts; a dismissal ends
// the case with the debts intact. Jose Santiago's file shows a 2023 filing
// marked Dismissed, and the packet was offering him a letter demanding that
// furnishers report his debts as discharged. That letter would have been false.
function bankruptcyRecord(parsed) {
  const recs = (parsed && parsed.publicRecords) || [];
  const hit = recs.find(r => /bankrupt|chapter\s*(7|11|13)/i.test(
    String((r && (r.type || r.kind || r.description)) || '')));
  if (!hit) return null;
  const blob = [hit.type, hit.kind, hit.description, hit.status, hit.disposition]
    .filter(Boolean).join(' ');
  const ch = blob.match(/chapter\s*(7|11|13)\b/i) || String(hit.chapter || '').match(/(7|11|13)/);
  return {
    filingDate: hit.date_filed || hit.date || null,
    caseNumber: hit.reference || hit.case_number || hit.docket || null,
    chapter: ch ? ch[1] : null,
    discharged: /discharg/i.test(blob),
    dismissed: /dismiss/i.test(blob),
    raw: hit
  };
}

function computeFlags(intake, upload) {"""
rep(A, B, 1, 'bankruptcyRecord')

# ---- 2. a dismissal is not a discharge ----
A = """  if (f.bankruptcy) {
    packet.push(letterTemplates.bankruptcy_discharged);
    packet.push(letterTemplates.bankruptcy_automatic_stay);
    packet.push(letterTemplates.bankruptcy_pre_filing);
  }"""
B = """  if (f.bankruptcy) {
    // The post-discharge letter demands that furnishers report the debts as
    // discharged with a zero balance. That is only true after a discharge. On a
    // DISMISSED case the debts survive, and sending it would assert something
    // the court record contradicts — so it is withheld unless the filing was
    // discharged, or we cannot tell and the consumer said so themselves.
    const bkRec = (typeof bankruptcyRecord === 'function')
      ? bankruptcyRecord((state.upload && state.upload.parsed) || {}) : null;
    const saidSo = (state.intake.special_flags || []).indexOf('bankruptcy') >= 0;
    if (!bkRec || bkRec.discharged || (!bkRec.dismissed && saidSo)) {
      packet.push(letterTemplates.bankruptcy_discharged);
    }
    packet.push(letterTemplates.bankruptcy_automatic_stay);
    packet.push(letterTemplates.bankruptcy_pre_filing);
  }"""
rep(A, B, 1, 'discharge gate')

# ---- 3. fill the letters from the record, and never bracket ----
A = """  const chapter = ctx.chapter || '[7 or 13]';
  const caseNumber = ctx.caseNumber || '[Bankruptcy case number]';"""
B = """  const chapter = ctx.chapter || null;
  const caseNumber = ctx.caseNumber || null;"""
rep(A, B, 1, 'discharged letter defaults')

A = """    `• Case Number: ${caseNumber}`,"""
B = """    caseNumber ? `\\u2022 Case Number: ${caseNumber}` : '\\u2022 Case Number: ______________________',"""
rep(A, B, 1, 'case number line')

A = """    re: `Dispute — Inaccurate Post-Discharge Bankruptcy Reporting — Case ${caseNumber}`,"""
B = """    re: 'Dispute \\u2014 Inaccurate Post-Discharge Bankruptcy Reporting' + (caseNumber ? ' \\u2014 Case ' + caseNumber : ''),"""
rep(A, B, 1, 'discharged re line')

A = """  const filingDate = ctx.filingDate || '[Date of bankruptcy filing]';
  const caseNumber = ctx.caseNumber || '[Case Number]';"""
B = """  const filingDate = ctx.filingDate || null;
  const caseNumber = ctx.caseNumber || null;"""
rep(A, B, 1, 'stay letter defaults')

# ---- 4. wire the record into every letter context ----
A = """  ctx.billingErrorItems = reviewedAccounts('charges');"""
B = """  // The bankruptcy letters used to print "[Date of bankruptcy filing]" and
  // "[Bankruptcy case number]" because nothing ever handed them the filing —
  // which is on the report, in the public records section, already parsed.
  const bkr = (typeof bankruptcyRecord === 'function') ? bankruptcyRecord(parsed) : null;
  if (bkr) {
    if (bkr.filingDate && !ctx.filingDate) ctx.filingDate = bkr.filingDate;
    if (bkr.caseNumber && !ctx.caseNumber) ctx.caseNumber = bkr.caseNumber;
    if (bkr.chapter && !ctx.chapter) ctx.chapter = bkr.chapter;
    ctx.bankruptcyRecord = bkr;
  }

  ctx.billingErrorItems = reviewedAccounts('charges');"""
rep(A, B, 1, 'wire bankruptcy record')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
