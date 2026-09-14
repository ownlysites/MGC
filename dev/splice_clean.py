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

# ---- 1. "no derogatory" is not the same claim as "nothing to dispute" ----
A = """  // Nothing derogatory is itself a finding worth stating plainly.
  const derog = accounts.filter(a => a.has_late_payments || a.is_charge_off || a.is_collection || a.is_repossession || a.in_bankruptcy);
  if (accounts.length > 0 && derog.length === 0 && collections.length === 0) {
    analysis.findings.push({
      type: 'clean',
      severity: 'low',
      title: 'No derogatory items found on this report',
      detail: 'Every account read from this report is reporting without late payments, charge-offs, collections or public records. There is nothing here to dispute on accuracy grounds — your work is building positive history, not removing negatives.'
    });
  }"""

B = r"""  // "No derogatory items" and "there is nothing to dispute" are two different
  // claims, and this used to make the second one on the strength of the first.
  //
  // A report can carry no late payment anywhere and still contradict itself a
  // dozen times over — a closed account still reporting a monthly payment, a
  // balance higher than the highest balance ever recorded, two bureaus
  // describing the same account differently. Those contradictions are what the
  // letters are built from, so a file like that produced a page saying there
  // was nothing here to dispute and, a few inches further down, a packet of
  // letters disputing things. Public records were missing from the test as
  // well, so a judgment with no derogatory tradeline beside it read as clean.
  //
  // Both branches below are true statements. The second one is also the more
  // useful thing this tool can tell anybody, because a contradiction on the
  // face of a report is the dispute a bureau has to work rather than answer
  // with "verified".
  const derog = accounts.filter(a => a.has_late_payments || a.is_charge_off || a.is_collection || a.is_repossession || a.in_bankruptcy);
  const cleanPub  = ((parsed.publicRecords || []).length);
  const cleanFact = ((analysis.factual || []).length);
  const cleanXB   = ((analysis.contradictions || []).length);
  const noDerog = accounts.length > 0 && derog.length === 0 && collections.length === 0 && cleanPub === 0;

  if (noDerog && !cleanFact && !cleanXB) {
    analysis.findings.push({
      type: 'clean',
      severity: 'low',
      title: 'No derogatory items found on this report',
      detail: 'Every account read from this report is reporting without late payments, charge-offs, collections or public records, and nothing on it contradicts itself. There is nothing here to dispute on accuracy grounds — your work is building positive history, not removing negatives.'
    });
  } else if (noDerog) {
    const cleanBits = [];
    if (cleanFact) cleanBits.push(cleanFact + (cleanFact === 1 ? ' place where the report contradicts itself' : ' places where the report contradicts itself'));
    if (cleanXB)   cleanBits.push(cleanXB + (cleanXB === 1 ? ' account the bureaus describe differently' : ' accounts the bureaus describe differently'));
    analysis.findings.push({
      type: 'clean_but_inaccurate',
      severity: 'medium',
      title: 'No late payments — but this report still is not accurate',
      detail: 'Nothing on this report is derogatory: no late payments, no charge-offs, no collections, no public records. That is worth knowing and it is genuinely good news. It is not the same as the report being correct. ' +
        'There ' + ((cleanFact + cleanXB) === 1 ? 'is ' : 'are ') + cleanBits.join(' and ') +
        ', and those are the strongest disputes on any file — a bureau can check a contradiction against its own record without asking the furnisher anything, which is why they get worked rather than answered with "verified". Your letters name each one specifically. Nothing in this packet asks for a good account to be removed.'
    });
  }"""
rep(A, B, 1, 'clean-report claim')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
