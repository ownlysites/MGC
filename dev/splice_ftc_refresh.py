
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

# ---- the helper ----
A = """function goToItemReview() {"""
B = """// Entering the FTC report number rebuilt the letters and nothing else.
//
// Typing it in put the number into the § 605B letter correctly — and left the
// walkthrough above it still reading "No FTC report number entered yet", and
// left an already-built plan whose separator sheet still says "Do not mail this
// one yet — you have not entered one". That sheet is the one that tells a
// victim to hold the letter. Once the number is in, holding it is exactly wrong
// and costs them the four-business-day clock under § 605B(a).
//
// This runs on change rather than on input: re-rendering a panel while someone
// is still typing in it destroys the field they are typing into.
function refreshIdentityTheftViews() {
  if (typeof regenerateAllLetters === 'function') regenerateAllLetters();
  if (!state.analysis) return;
  const vis = id => { const e = document.getElementById(id); return e && e.offsetParent !== null; };
  if (vis('step-letters') && typeof renderLetterPacket === 'function') renderLetterPacket(state.analysis);
  else if (vis('step-analysis') && typeof renderAnalysis === 'function') renderAnalysis(state.analysis);
  // The printable plan is a snapshot taken when it was built. Leaving a stale
  // one behind means the next print carries separator sheets that contradict
  // the letters they sit in front of.
  if (state.planHtml && typeof buildActionPlanDoc === 'function') buildActionPlanDoc();
}

function goToItemReview() {"""
rep(A, B, 1, 'refreshIdentityTheftViews()')

# ---- wire the FTC input ----
A = """oninput="state.ftcReportNumber = this.value; regenerateAllLetters();\">"""
B = """oninput="state.ftcReportNumber = this.value; regenerateAllLetters();" onchange="refreshIdentityTheftViews()">"""
rep(A, B, 1, 'FTC input refreshes the views on change')

# ---- and the police-report toggle, which has the same problem ----
A = """function setPoliceReport(v) {
  state.policeReportFiled = v;
  regenerateAllLetters();
  if (state.analysis) renderAnalysis(state.analysis);
}"""
B = """function setPoliceReport(v) {
  state.policeReportFiled = v;
  // Same defect as the FTC number: this changes the enclosure list in the
  // § 605B letter, and re-rendering only the analysis step left the
  // walkthrough — which lives on the letters step — and any built plan stale.
  if (typeof refreshIdentityTheftViews === 'function') refreshIdentityTheftViews();
  else { regenerateAllLetters(); if (state.analysis) renderAnalysis(state.analysis); }
}"""
rep(A, B, 1, 'police report toggle refreshes too')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
