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

# The cover page is the one the person reads first, and it was making the same
# mistake as the findings list: deciding "nothing to dispute" from the
# derogatory accounts alone, while the letters behind it are built from the
# contradictions as well. So the front page said the file was clean and page
# nine disputed six things on it. One count, used by both.
# Two functions compute `derog` identically — the findings builder and the plan
# builder. The plan one is the one on the cover, so the anchor carries the line
# above it to pick it out.
A = """  const phases = analysis.action_plan || [];
  const derog = accounts.filter(a => a.has_late_payments || a.is_charge_off || a.is_collection || a.is_repossession || a.in_bankruptcy);"""
B = """  const phases = analysis.action_plan || [];
  const derog = accounts.filter(a => a.has_late_payments || a.is_charge_off || a.is_collection || a.is_repossession || a.in_bankruptcy);
  // Everything this packet actually writes about, not just the bad tradelines.
  const coverFact = (analysis.factual || []).length;
  const coverXB   = (analysis.contradictions || []).length;
  const coverPub  = (parsed.publicRecords || []).length;
  const disputable = derog.length + coverFact + coverXB + coverPub;"""
rep(A, B, 1, 'cover counts everything')

A = """  const headline = derog.length
    ? 'A clear plan for<br>your credit file'
    : (accounts.length ? 'Your file is clean.<br>Here is what to build' : 'A clear plan for<br>your credit file');
  const summaryTitle = derog.length
    ? `${derog.length} item${derog.length === 1 ? '' : 's'} worth working on`
    : (accounts.length ? 'Nothing derogatory to dispute' : 'Plan built from your intake answers');
  const summaryBody = derog.length
    ? `Your report shows ${derog.length} account${derog.length === 1 ? '' : 's'} carrying a late payment, charge-off, collection or public record. This plan works them in order, starting with the ones that come off on the calendar rather than on argument.`
    : (accounts.length
      ? 'Every account read from your report is reporting without a late payment, charge-off or collection. There is nothing here to dispute on accuracy grounds, so this plan is about building positive history rather than removing negatives.'
      : 'No credit report was uploaded, so this plan is built from your intake answers. Pull all three reports and come back — the plan gets far more specific once it can read them.');"""

B = """  const headline = disputable
    ? 'A clear plan for<br>your credit file'
    : (accounts.length ? 'Your file is clean.<br>Here is what to build' : 'A clear plan for<br>your credit file');

  const summaryTitle = derog.length
    ? `${derog.length} item${derog.length === 1 ? '' : 's'} worth working on`
    : (disputable
      ? `${disputable} thing${disputable === 1 ? '' : 's'} on this report are wrong`
      : (accounts.length ? 'Nothing derogatory to dispute' : 'Plan built from your intake answers'));

  const summaryBody = derog.length
    ? `Your report shows ${derog.length} account${derog.length === 1 ? '' : 's'} carrying a late payment, charge-off, collection or public record. This plan works them in order, starting with the ones that come off on the calendar rather than on argument.`
    : (disputable
      // No bad tradelines, and still plenty to write about. This used to print
      // "nothing here to dispute" on the cover of a packet containing letters.
      ? `Nothing on your report is derogatory — no late payments, no charge-offs, no collections. That is good news and it is not the same as the report being correct. There ${disputable === 1 ? 'is one place' : 'are ' + disputable + ' places'} where it contradicts itself, and those are the strongest disputes there are: a bureau can check a contradiction against its own record without asking the furnisher anything. Your letters name each one.`
      : (accounts.length
        ? 'Every account read from your report is reporting without a late payment, charge-off or collection, and nothing on it contradicts itself. There is nothing here to dispute on accuracy grounds, so this plan is about building positive history rather than removing negatives.'
        : 'No credit report was uploaded, so this plan is built from your intake answers. Pull all three reports and come back — the plan gets far more specific once it can read them.'));"""
rep(A, B, 1, 'cover copy')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
