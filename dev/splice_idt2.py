
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

# ---- 1. the button was dead ----
# The walkthrough renders on the LETTERS step. The item review lives on the
# ANALYSIS step, which is display:none at that moment, and scrollIntoView on a
# hidden element does nothing at all. Driving the live page is the only way this
# shows up: the harness renders the HTML and never has two steps to switch
# between. Change the step first, then scroll.
A = """onclick="var el=document.getElementById('item-review'); if(el) el.scrollIntoView({behavior:'smooth', block:'start'});\""""
B = """onclick="goToItemReview()\""""
rep(A, B, 1, 'button calls a real function')

A = """// ========== IDENTITY THEFT WALKTHROUGH =========="""
B = """// The item review is on the analysis step and the identity-theft walkthrough is
// on the letters step, so getting from one to the other is a step change and
// not a scroll. The first version of this button scrolled to a hidden element
// and did nothing, which is worse than no button — it tells a victim the route
// exists and then does not take them.
function goToItemReview() {
  if (typeof showStep === 'function') showStep('analysis');
  setTimeout(function () {
    const el = document.getElementById('item-review');
    if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
  }, 60);
}

// ========== IDENTITY THEFT WALKTHROUGH =========="""
rep(A, B, 1, 'goToItemReview()')

# ---- 2. the enclosure list contradicted the block above it ----
A = """        <p>For each fraudulent item, mail the § 605B Block letter we\\'ve generated (above). Enclose:</p>
        <ul>
          <li>Your FTC Identity Theft Report</li>
          <li>The completed Identity Theft Affidavit</li>
          <li>A copy of your government-issued photo ID</li>
          <li>Proof of your current address (utility bill, etc.)</li>
          <li>Police report (if filed)</li>
        </ul>"""
B = """        ${((typeof reviewedAccounts === 'function') ? reviewedAccounts('never') : []).length
          ? `<p>Mail the § 605B Block letter above. Enclose:</p>`
          : `<p>Once it is built, you will mail it with these enclosed:</p>`}
        <ul>
          <li>Your FTC Identity Theft Report</li>
          <li>The completed Identity Theft Affidavit</li>
          <li>A copy of your government-issued photo ID</li>
          <li>Proof of your current address (utility bill, etc.)</li>
          <li>Police report (if filed)</li>
        </ul>"""
rep(A, B, 1, 'enclosure line stops promising a letter that is not there')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
