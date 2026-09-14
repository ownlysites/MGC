
import io

P = '/Users/daveivery/Documents/Claude/Projects/MGC/index.html'
s = io.open(P, encoding='utf-8').read()
orig = len(s)

def rep(anchor, new, count=1, label=''):
    global s
    n = s.count(anchor)
    assert n == count, 'anchor %r found %d times (expected %d) :: %s' % (anchor[:90], n, count, label)
    s = s.replace(anchor, new, count)
    print('  ok  ' + (label or anchor[:50]))

# A shared shape for "the list is empty". Ruled lines the consumer writes on,
# never a bracketed instruction sitting in a mailed letter.
RULED = ("['', '    ______________________________________________________________', '',\n"
         "     '    ______________________________________________________________', '',\n"
         "     '    ______________________________________________________________'].join('\\n')")

# ---- 1. initial bureau dispute: the item list, and the creditor name ----
A = """    return `${i+1}. ${it.creditor || '[Creditor Name]'}${acctLine ? ' — ' + acctLine : ''}\\n   Reason: ${reason}`;"""
B = """    return `${i+1}. ${it.creditor || 'the account below'}${acctLine ? ' — ' + acctLine : ''}\\n   Reason: ${reason}`;"""
rep(A, B, 1, 'bureau dispute: creditor name')

A = """    items.length > 0 ? items.map((it, i) => `${i+1}) ${it.creditor} - ${it.reason || 'Inaccurate/unverifiable'}`).join('\\n') : '[Fill in each item]',"""
B = """    items.length > 0 ? items.map((it, i) => `${i+1}) ${it.creditor} - ${it.reason || 'Inaccurate/unverifiable'}`).join('\\n') : 'See the numbered list in the letter accompanying this dispute.',"""
rep(A, B, 1, 'bureau dispute: portal fallback')

# ---- 2. mixed file ----
A = """    (flagged.addresses || []).length ? (flagged.addresses || []).map((a, i) => `${i + 1}) ${String(a.address || a).replace(/\\n/g, ', ')}`).join('\\n') : '[list them]',"""
B = """    (flagged.addresses || []).length ? (flagged.addresses || []).map((a, i) => `${i + 1}) ${String(a.address || a).replace(/\\n/g, ', ')}`).join('\\n') : """ + RULED + ""","""
rep(A, B, 1, 'mixed file: address list')

# ---- 3. personal information correction ----
A = """    lines.length ? lines.map((l, i) => `${i + 1}) ${l}`).join('\\n') : '[list the incorrect details]',"""
B = """    lines.length ? lines.map((l, i) => `${i + 1}) ${l}`).join('\\n') : """ + RULED + ""","""
rep(A, B, 1, 'personal info: detail list')

# ---- 4. 609 request ----
A = """    `${i+1}. ${it.creditor || '[Creditor Name]'}${it.account ? ' — Account #' + it.account : ''}`
  ).join('\\n') : '[List each account/item you want full disclosure on]';"""
B = """    `${i+1}. ${it.creditor || 'the account below'}${it.account ? ' — Account #' + it.account : ''}`
  ).join('\\n') : """ + RULED + """;"""
rep(A, B, 1, '609: item list')

# ---- 5. method of verification ----
A = ("""    `${i+1}. ${it.creditor || '[Creditor Name]'}${it.account ? ' — Account #' + it.account : ''}`\n"""
     """  ).join('\\n') : '[List each "verified" item from your last dispute response]';""")
B = ("""    `${i+1}. ${it.creditor || 'the account below'}${it.account ? ' — Account #' + it.account : ''}`\n"""
     """  ).join('\\n') : """ + RULED + ";")
rep(A, B, 1, 'MOV: item list')

# ---- 6. inquiry dispute ----
A = """  ).join('\\n') : '[List each unauthorized inquiry: company name and date]';"""
B = """  ).join('\\n') : """ + RULED + """;"""
rep(A, B, 1, 'inquiry dispute: list')

A = """${inquiries.length > 0 ? inquiries.map(i=>i.creditor).slice(0,3).join(', ') : '[list]'}. Please remove."""
B = """${inquiries.length > 0 ? inquiries.map(i=>i.creditor).slice(0,3).join(', ') : 'the inquiries listed in my letter'}. Please remove."""
rep(A, B, 1, 'inquiry dispute: short')

# ---- 7. permissible purpose demand ----
A = """  const company = q.creditor || '[Company that pulled your report]';
  const companyAddr = q.address || '[Company address — printed beside the inquiry on your report]';
  const inqDateStr = q.date || '[Date of the inquiry]';
  const bureauSeen = q.bureau || '[Bureau where the inquiry appears]';"""
B = """  // This letter goes to the company that pulled the report, so it cannot be
  // built at all without knowing who they are — and the packet only reaches
  // here once an inquiry has been flagged. Where the report gave us less than
  // the whole picture, the gap is a ruled blank taken off their own report,
  // never a bracket.
  const company = q.creditor || 'The company named below';
  const companyAddr = q.address || '____________________________________________';
  const inqDateStr = q.date || '________________';
  const bureauSeen = q.bureau || '________________';"""
rep(A, B, 1, 'permissible purpose: company/date/bureau')

# ---- 8. identity theft block ----
A = """  ).join('\\n') : '[List each fraudulent account, inquiry, or item]';"""
B = """  ).join('\\n') : """ + RULED + """;"""
rep(A, B, 1, 'idtheft block: item list')

# ---- 9. medical itemization ----
A = """  const name = c.name || '[Collection agency name]';"""
B = """  const name = c.name || 'The collection agency named below';"""
rep(A, B, 1, 'medical itemization: agency name')

A = """  const mail = mailEnvelope(body, `${name}\\n${c.addr || '[Collector address — from their letter]'}`, {"""
B = """  const mail = mailEnvelope(body, `${name}\\n${c.addr || '____________________________________________'}`, {"""
rep(A, B, 1, 'medical itemization: agency address')

# ---- 10. privacy opt-out ----
A = """  const creditor = ctx.creditor || {name: '[Creditor Name]', addr: '[Creditor Address]'};"""
B = """  // Fanned out per creditor (see letterFanTargets). Blank, never a bracket —
  // the separator sheet already tells them when an address is theirs to fill in.
  const creditor = ctx.creditor || {name: '', addr: ''};"""
rep(A, B, 1, 'privacy opt-out: creditor')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
