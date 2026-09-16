
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

# The guides also live at the bottom of every screen, including the landing
# page. Someone who came for the reading and not the letters should not have to
# walk an intake, an upload and an analysis to reach a PDF. Static markup rather
# than built from MGC_GUIDES on load, because a footer that depends on script
# timing is a footer that is sometimes empty; dev/checks.js asserts these hrefs
# match the array so the two cannot drift.
A = """      <div>
        <h5>Free official resources</h5>"""
B = """      <div>
        <h5>Free field guides</h5>
        <ul style="list-style:none;font-size:0.875rem;" id="footer-guides">
          <li><a href="/guides/ownly-once-01-credit-card-pull-guide.pdf" download>Credit card pulls</a></li>
          <li><a href="/guides/ownly-once-02-whats-holding-your-score-back.pdf" download>What&rsquo;s holding your score back</a></li>
          <li><a href="/guides/ownly-once-03-90-day-readiness-workbook.pdf" download>90-day readiness workbook</a></li>
          <li><a href="/guides/ownly-once-04-charge-off-dispute-kit.pdf" download>Charge-off dispute kit</a></li>
          <li><a href="/guides/ownly-once-05-eviction-reporting-dispute-guide.pdf" download>Eviction &amp; tenant screening</a></li>
          <li><a href="/guides/ownly-once-06-different-bureau-results-guide.pdf" download>Different bureau results</a></li>
          <li style="margin-top:var(--space-2);color:var(--warm-gray-400);font-size:0.8125rem;">PDFs, free, no email asked for. Nothing to fill in first.</li>
        </ul>
      </div>
      <div>
        <h5>Free official resources</h5>"""
rep(A, B, 1, 'footer: field guides column')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
