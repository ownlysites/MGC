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

# The military letters had never been scanned by the mailable harness, and all
# three printed brackets — the same defect as the furnisher dispute and the
# breach notification before them. Two of them go to a creditor and can be
# fanned out to the real ones; the third goes to a court, and a court is not
# something this file can know.

# ---- 1. interest cap: real creditor, no brackets ----
A = """function compileSCRAInterest(ctx) {
  const creditor = ctx.creditor || {name:'[Creditor Name]', addr:'[Address]', account:'[XXXX]'};
  const startDate = ctx.militaryStartDate || '[Date you entered active duty / first called up]';"""
B = """function compileSCRAInterest(ctx) {
  // Fanned out per creditor (see letterFanTargets), so ctx.creditor is set per
  // copy. Blank rather than a bracket if it somehow is not.
  const creditor = ctx.creditor || {name:'', addr:'', account:''};
  // The date they entered service is theirs to write in. A letter that invents
  // one is worse than a letter with a gap the separator sheet explains.
  const startDate = ctx.militaryStartDate || null;"""
rep(A, B, 1, 'scra interest defaults')

A = """    `I entered active military service on ${startDate}. The above-referenced account was established prior to my active service and therefore qualifies for the protections of SCRA § 527 (50 U.S.C. § 3937).`,"""
B = """    (startDate
      ? `I entered active military service on ${startDate}. The above-referenced account was established prior to my active service and therefore qualifies for the protections of SCRA § 527 (50 U.S.C. § 3937).`
      : 'The above-referenced account was established prior to my active military service and therefore qualifies for the protections of SCRA § 527 (50 U.S.C. § 3937). The start date of my active service is shown on the orders enclosed with this letter.'),"""
rep(A, B, 1, 'scra interest start date')

# ---- 2. credit reporting: same ----
A = """  const creditor = ctx.creditor || {name:'[Creditor]', addr:'[Address]', account:'[XXXX]'};"""
B = """  const creditor = ctx.creditor || {name:'', addr:'', account:''};"""
rep(A, B, 1, 'scra credit reporting defaults')

# ---- 3. the court letter: a court cannot be guessed ----
A = """  const court = ctx.court || '[Court Name and Address]';
  const caseNumber = ctx.caseNumber || '[Case Number]';"""
B = """  // A court name and a case number are on the papers the servicemember was
  // served with. Nothing here can know them, and a motion filed with
  // "[Case Number]" on it is returned. Left blank, ruled, and called out on the
  // separator sheet as the one letter that must be completed before it is filed.
  const court = ctx.court || '__________________________________________';
  const caseNumber = ctx.caseNumber || '______________________';"""
rep(A, B, 1, 'scra court blanks')

A = """    'I have meritorious defenses to the underlying action that I would have raised but for my military service having prevented my appearance. These defenses include (but are not limited to): [LIST YOUR DEFENSES — e.g., disputing the debt, SOL, improper service, etc.]',"""
B = """    'I have meritorious defenses to the underlying action that I would have raised but for my military service having prevented my appearance. These defenses include, but are not limited to, the following:',
    '',
    '    ______________________________________________________________',
    '',
    '    ______________________________________________________________',"""
rep(A, B, 1, 'scra defenses blanks')

# ---- 4. the fan-out ----
A = """  // A goodwill request goes to the creditor whose late payment it is about."""
B = """  // The two SCRA creditor letters go to each creditor the person owed before
  // they went on active duty. Nothing on a credit report says which debts are
  // pre-service, so this addresses every open account and the separator sheet
  // says to send only the ones that predate the start of service — an honest
  // instruction on a page that is not mailed, rather than a guess in a letter.
  if (tmpl.id === 'scra_interest_cap' || tmpl.id === 'scra_credit_reporting') {
    const seenS = {};
    const outS = [];
    (parsed.accounts || []).forEach(a => {
      if (!a || !a.creditor) return;
      if (a.is_collection) return;
      const k = mgcNorm(a.creditor);
      if (seenS[k]) return;
      seenS[k] = 1;
      outS.push({name: a.creditor, addr: furnisherAddressFor(a.creditor),
                 account: a.account_number || '', acct: a, label: a.creditor});
    });
    return outS;
  }

  // A goodwill request goes to the creditor whose late payment it is about."""
rep(A, B, 1, 'scra fan-out')

# ---- 5. the separator sheet warns on the court filing ----
A = """        ${tmpl.id === 'idtheft_block' && !((state.ftcReportNumber || '').trim())"""
B = """        ${tmpl.id === 'scra_default_protection'
          ? `<div class="plan-divider-grid"><div><em>Fill this one in before you file it</em><p>This is a motion to a court, not a letter to a company, and three things on it are blank because nothing here can know them: the court&rsquo;s name and address, your case number, and your defences to the underlying claim. All three are on the papers you were served with. A motion filed with blanks on it is returned. If you are still serving, your installation&rsquo;s legal assistance office will help you complete and file it at no cost &mdash; that is what they are for.</p></div></div>`
          : ''}
        ${(tmpl.id === 'scra_interest_cap' || tmpl.id === 'scra_credit_reporting')
          ? `<div class="plan-divider-grid"><div><em>Only send this for debts you had BEFORE you went on active duty</em><p>The 6% cap under 50 U.S.C. &sect; 3937 applies to obligations incurred before your active service began, and nothing on a credit report says which of yours those are &mdash; so a copy has been prepared for every creditor and you choose. Sending one for a debt taken on after you started serving does not gain you anything and tells the lender you have not read the statute. Enclose a copy of your orders with each one you do send.</p></div></div>`
          : ''}
        ${tmpl.id === 'idtheft_block' && !((state.ftcReportNumber || '').trim())"""
rep(A, B, 1, 'scra separator notes')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
