
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

# ---- 1. an intake option the pre-filing letter can honestly run on ----
A = """      {v:'bankruptcy', t:'I\\'ve filed bankruptcy in the last 10 years'},"""
B = """      {v:'bankruptcy', t:'I\\'ve filed bankruptcy in the last 10 years'},
      {v:'bankruptcy_considering', t:'I\\'m considering filing bankruptcy'},"""
rep(A, B, 1, 'intake: considering bankruptcy')

A = """    scra: intake.special_flags && intake.special_flags.includes('scra'),"""
B = """    // Separate from having filed. The pre-filing notice says "I intend to
    // file", which is false for someone who already has — and the only
    // bankruptcy question asked was about a filing in the past ten years, so
    // that letter had no honest trigger at all until this one existed.
    bankruptcy_considering: intake.special_flags &&
      intake.special_flags.includes('bankruptcy_considering'),
    scra: intake.special_flags && intake.special_flags.includes('scra'),"""
rep(A, B, 1, 'flag: bankruptcy_considering')

# ---- 2. the packet stops asserting things the court record contradicts ----
A = """    if (!bkRec || bkRec.discharged || (!bkRec.dismissed && saidSo)) {
      packet.push(letterTemplates.bankruptcy_discharged);
    }
    packet.push(letterTemplates.bankruptcy_automatic_stay);
    packet.push(letterTemplates.bankruptcy_pre_filing);
  }"""
B = """    if (!bkRec || bkRec.discharged || (!bkRec.dismissed && saidSo)) {
      packet.push(letterTemplates.bankruptcy_discharged);
    }
    // The automatic stay exists between filing and the end of the case. Under
    // 11 U.S.C. § 362(c)(2) it terminates when the case is closed or dismissed
    // or when a discharge is granted — so on Jose Santiago's dismissed filing
    // there is no stay to enforce, and after a discharge the instrument is the
    // § 524 discharge injunction, not the stay. Either way a letter demanding
    // compliance with a stay that has ended is one the collector can dismiss on
    // sight, and it makes everything else in the envelope look unread.
    if (!bkRec || (!bkRec.dismissed && !bkRec.discharged)) {
      packet.push(letterTemplates.bankruptcy_automatic_stay);
    }
    // And the pre-filing notice announces an intent to file, which contradicts
    // both a filing on the report and the intake box that says they already
    // filed. It goes out only for someone who said they are considering it.
    if (f.bankruptcy_considering && !bkRec) {
      packet.push(letterTemplates.bankruptcy_pre_filing);
    }
  }

  // Considering bankruptcy without having filed is its own route into the
  // pre-filing notice — f.bankruptcy is about a filing that already happened.
  if (f.bankruptcy_considering && !f.bankruptcy &&
      !packet.includes(letterTemplates.bankruptcy_pre_filing)) {
    packet.push(letterTemplates.bankruptcy_pre_filing);
  }"""
rep(A, B, 1, 'packet: stay/pre-filing gating')

# ---- 3. the stay letter ----
A = """function compileBKStay(ctx) {
  const collector = ctx.collector || {name:'[Collector]', addr:'[Address]'};
  const filingDate = ctx.filingDate || null;
  const caseNumber = ctx.caseNumber || null;
  // These go to a collector, so they fan out like every other collector letter
  // rather than printing "[Collector]" into an envelope.
  const bkCollector = ctx.collector || {name: '', addr: ''};
  const bkCollName = typeof bkCollector === 'string' ? bkCollector : (bkCollector.name || '');
  const bkCollAddr = typeof bkCollector === 'object' ? (bkCollector.addr || '') : '';
  const u = userHeader();"""
B = """function compileBKStay(ctx) {
  // Fanned out per collector (see letterFanTargets), so ctx.collector is set
  // per copy. Blank rather than a bracket if it somehow is not — "[Collector]"
  // in an address block is a letter addressed to nobody.
  const collector = ctx.collector || {name:'', addr:''};
  // The court's name and the filing details come off the petition, and the
  // collection activity comes out of the person's own log of the calls. None of
  // it is on a credit report. Ruled blanks, called out on the separator sheet,
  // rather than brackets that read as a form.
  const filingDate = ctx.filingDate || null;
  const caseNumber = ctx.caseNumber || null;
  const courtLine  = ctx.court || '________________________________________';
  const filedPhr   = filingDate ? 'on ' + filingDate : 'on the date shown on my petition';
  const casePhr    = caseNumber
    ? 'The case number is ' + caseNumber + '.'
    : 'The case number is on the notice of filing enclosed with this letter.';
  const reCase     = caseNumber ? ' \\u2014 Case ' + caseNumber : '';
  const reFiled    = filingDate ? ' \\u2014 Bankruptcy Filed ' + filingDate : '';
  const u = userHeader();"""
rep(A, B, 1, 'stay: collector + blanks')

A = """    `I filed a petition for bankruptcy on ${filingDate} in the [COURT]. The case number is ${caseNumber}. The automatic stay under 11 U.S.C. § 362 took effect immediately upon filing and prohibits any act to collect, assess, or recover a claim against me that arose before the commencement of the case.`,
    '',
    'Despite my filing, your agency has continued to attempt collection of an alleged debt. Specifically:',
    '[DESCRIBE THE COLLECTION ACTIVITY — calls, letters, credit reporting, lawsuits, etc., AND DATES]',"""
B = """    `I filed a petition for bankruptcy ${filedPhr} in the following court:`,
    '',
    '    ' + courtLine,
    '',
    `${casePhr} The automatic stay under 11 U.S.C. § 362 took effect immediately upon filing and prohibits any act to collect, assess, or recover a claim against me that arose before the commencement of the case.`,
    '',
    'Despite my filing, your agency has continued to attempt collection of an alleged debt. Each contact, with its date:',
    '',
    '    ______________________________________________________________',
    '',
    '    ______________________________________________________________',
    '',
    '    ______________________________________________________________',"""
rep(A, B, 1, 'stay: court + activity log')

A = """    'Please direct all further communication to my bankruptcy attorney [IF REPRESENTED] or to the Bankruptcy Court directly.'"""
B = """    'Please direct all further communication about this account to the Bankruptcy Court, or to counsel of record in the case if you have been served with an appearance.'"""
rep(A, B, 1, 'stay: attorney line')

A = """  const mail = mailEnvelope(body, `${collectorName}\\n${collectorAddr}`, {
    re: `Automatic Stay Violation — Case ${caseNumber} — Bankruptcy Filed ${filingDate}`,
    ssnLine: false
  });
  
  const portal = `Automatic stay violation notice. Bankruptcy filed ${filingDate}, Case ${caseNumber}."""
B = """  const mail = mailEnvelope(body, `${collectorName}\\n${collectorAddr}`, {
    re: `Automatic Stay Violation${reCase}${reFiled}`,
    ssnLine: false
  });
  
  const portal = `Automatic stay violation notice. Bankruptcy filed ${filingDate || '(see petition)'}, Case ${caseNumber || '(see petition)'}."""
rep(A, B, 1, 'stay: subject + portal nulls')

A = """  const short = `Automatic stay violation — BK filed ${filingDate}, case ${caseNumber}. Cease ALL collection."""
B = """  const short = `Automatic stay violation — BK filed ${filingDate || '(see petition)'}, case ${caseNumber || '(see petition)'}. Cease ALL collection."""
rep(A, B, 1, 'stay: short nulls')

# ---- 4. the pre-filing letter ----
A = """function compileBKPreFiling(ctx) {
  const collector = ctx.collector || {name:'[Collector]', addr:'[Address]'};"""
B = """function compileBKPreFiling(ctx) {
  // Fanned out per collector (see letterFanTargets). Blank, never a bracket.
  const collector = ctx.collector || {name:'', addr:''};"""
rep(A, B, 1, 'pre-filing: collector default')

# ---- 5. both bankruptcy letters go to each collector, one envelope each ----
A = """  // A breach notification is a warning to each company that holds an account of"""
B = """  // Both bankruptcy letters are addressed to a collection agency, and there is
  // never only one. Fanned out the same way the settlement offer is, so each
  // agency gets its own envelope instead of one letter naming "[Collector]".
  if (tmpl.id === 'bankruptcy_automatic_stay' || tmpl.id === 'bankruptcy_pre_filing') {
    const seenB = {};
    const outB = [];
    const addB = (name, ref) => {
      if (!name) return;
      const k = mgcNorm(name);
      if (seenB[k]) return;
      seenB[k] = 1;
      outB.push({name: name, addr: furnisherAddressFor(name),
                 refNumber: ref || '', label: name});
    };
    (parsed.collections || []).forEach(c => addB(c.agency || c.creditor, c.account_number));
    if (!outB.length) {
      (parsed.accounts || []).filter(a => a && a.is_collection)
        .forEach(a => addB(a.creditor, a.account_number));
    }
    return outB;
  }

  // A breach notification is a warning to each company that holds an account of"""
rep(A, B, 1, 'fan targets: bankruptcy letters')

# ---- 6. the fan target actually reaches the compiler ----
A = """  } else if (tmpl.id === 'privacy_opt_out') {
    c.creditor = {name: t.name, addr: t.addr || ''};
    c.accountLines = t.name + (t.account ? '   Account #: ' + t.account : '');
    c.alsoSendTo = [];        // each copy is complete on its own now
  }"""
B = """  } else if (tmpl.id === 'privacy_opt_out') {
    c.creditor = {name: t.name, addr: t.addr || ''};
    c.accountLines = t.name + (t.account ? '   Account #: ' + t.account : '');
    c.alsoSendTo = [];        // each copy is complete on its own now
  } else if (tmpl.id === 'bankruptcy_automatic_stay' || tmpl.id === 'bankruptcy_pre_filing') {
    c.collector = {name: t.name, addr: t.addr || '', refNumber: t.refNumber || ''};
  } else if (tmpl.id === 'scra_interest_cap' || tmpl.id === 'scra_credit_reporting' ||
             tmpl.id === 'breach_notification') {
    // These three fanned out into copies that were never given their target,
    // so every copy compiled with an empty creditor and the address block came
    // out blank. The fan-out was only half wired.
    c.creditor = {name: t.name, addr: t.addr || '', account: t.account || ''};
  }"""
rep(A, B, 1, 'apply fan target: bk + scra + breach')

# ---- 7. the separator sheet says what to fill in ----
A = """        ${(tmpl.id === 'scra_interest_cap' || tmpl.id === 'scra_credit_reporting')"""
B = """        ${tmpl.id === 'bankruptcy_automatic_stay'
          ? `<div class="plan-divider-grid"><div><em>Fill this one in before you send it</em><p>Two things on this letter are blank because nothing here can know them: the name of the court you filed in, and the dates of the calls, letters or filings that came after you filed. The court is on the first page of your petition. The contact log is yours &mdash; write each date and what happened, because that list is the evidence a &sect; 362(k) claim runs on and a letter that alleges violations without dating them is easy to ignore.</p></div></div>`
          : ''}
        ${tmpl.id === 'bankruptcy_pre_filing'
          ? `<div class="plan-divider-grid"><div><em>Only send this before you file</em><p>This letter says a filing is coming. Once you have filed, it is the wrong letter &mdash; the automatic stay notice replaces it, and sending this one afterwards tells the collector you are not tracking your own case.</p></div></div>`
          : ''}
        ${(tmpl.id === 'scra_interest_cap' || tmpl.id === 'scra_credit_reporting')"""
rep(A, B, 1, 'separator sheet: bk letters')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
