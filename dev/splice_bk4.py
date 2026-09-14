
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

A = """  const dischargeDate = ctx.dischargeDate || '[Discharge date]';
  const chapter = ctx.chapter || null;
  const caseNumber = ctx.caseNumber || null;
  const u = userHeader();"""
B = """  // The discharge order carries the date, the chapter and the case number. A
  // report that names the filing often carries none of them, and the intake
  // tick carries nothing at all — so these are ruled blanks the person copies
  // off the order, not brackets. The separator sheet says so.
  const dischargeDate = ctx.dischargeDate || '______________________';
  const chapter = ctx.chapter || null;
  const caseNumber = ctx.caseNumber || null;
  const chapLabel = chapter ? 'Chapter ' + chapter : 'Chapter ______';
  const chapPhrase = chapter ? 'Chapter ' + chapter + ' Bankruptcy' : 'Bankruptcy';
  const u = userHeader();"""
rep(A, B, 1, 'discharged: blanks not brackets')

A = """  const itemsList = items.length > 0 ? items.map((it, i) => 
    `${i+1}. ${it.creditor || '[Creditor]'}${it.account ? ' — Account #' + it.account : ''}\\n   Current reporting: ${it.status || '[How it currently appears]'}\\n   Correct reporting should be: "Discharged in Chapter ${chapter} Bankruptcy" with $0 balance`
  ).join('\\n\\n') : '[List each discharged debt that is still being reported with a balance or as delinquent]';"""
B = """  // Nothing invented. An item whose current status the report does not carry
  // simply does not get a "Current reporting" line, and a packet with no items
  // gets ruled lines to write them on rather than an instruction in brackets.
  const itemsList = items.length > 0 ? items.map((it, i) => {
    const lines = [`${i+1}. ${it.creditor || ''}${it.account ? ' — Account #' + it.account : ''}`];
    if (it.status) lines.push(`   Current reporting: ${it.status}`);
    lines.push(`   Correct reporting should be: "Discharged in ${chapPhrase}" with $0 balance`);
    return lines.join('\\n');
  }).join('\\n\\n') : ['    ______________________________________________________________', '',
                      '    ______________________________________________________________', '',
                      '    ______________________________________________________________'].join('\\n');"""
rep(A, B, 1, 'discharged: item list')

A = """    `• Chapter: ${chapter}`,"""
B = """    `• ${chapLabel}`,"""
rep(A, B, 1, 'discharged: chapter line')

A = """    '(a) Status: "Discharged in Chapter ' + chapter + ' Bankruptcy" (or equivalent);',"""
B = """    '(a) Status: "Discharged in ' + chapPhrase + '" (or equivalent);',"""
rep(A, B, 1, 'discharged: correct-status line')

A = """  const portal = `Inaccurate post-discharge bankruptcy reporting. Chapter ${chapter}, Case ${caseNumber}, Discharged ${dischargeDate}."""
B = """  const portal = `Inaccurate post-discharge bankruptcy reporting. ${chapLabel}, Case ${caseNumber || '(see discharge order)'}, Discharged ${ctx.dischargeDate || '(see discharge order)'}."""
rep(A, B, 1, 'discharged: portal')

A = """  const short = `Post-discharge bankruptcy reporting violation — Ch. ${chapter} case ${caseNumber} discharged ${dischargeDate}."""
B = """  const short = `Post-discharge bankruptcy reporting violation — ${chapLabel} case ${caseNumber || '(see order)'} discharged ${ctx.dischargeDate || '(see order)'}."""
rep(A, B, 1, 'discharged: short')

# the separator sheet earns the exemption
A = """        ${tmpl.id === 'bankruptcy_automatic_stay'"""
B = """        ${tmpl.id === 'bankruptcy_discharged'
          ? `<div class="plan-divider-grid"><div><em>Copy these off your discharge order before you send it</em><p>The chapter, the case number and the discharge date are blank on this letter wherever your report did not carry them, because nothing here can read a court file. All three are on the first page of the discharge order the court mailed you. A bureau that receives a bankruptcy dispute with no case on it has nothing to check the filing against, and the dispute goes nowhere.</p></div></div>`
          : ''}
        ${tmpl.id === 'bankruptcy_automatic_stay'"""
rep(A, B, 1, 'separator sheet: discharge letter')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
