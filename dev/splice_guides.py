
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

# ---- the data and the two renderers ----
A = """// The same content on screen as in the packet, built from the same two arrays
// so the two cannot drift. Placed at the end of the analysis, after every
// letter, because it is the part that says what the letters cannot do.
function renderFreeHelpSection() {"""
B = """// ========== THE FIELD GUIDES ==========
// Six PDFs, free, no email asked for. They are Dave's own — the Ownly ONCE
// Credit Readiness Kit — and they are served from this domain rather than
// linked off-site so that nobody loses their place mid-packet.
//
// Two of them cover ground this tool does not: tenant screening reports are a
// different consumer file with a different dispute route, and the card-pull
// guide is about the decision before an inquiry ever lands. The rest sit
// alongside features here, which is why each one also appears at the moment it
// is relevant rather than only in the list at the end.
//
// PRIVACY. Every other byte of this tool stays in the browser. A PDF download
// is a request to the server like any other file on the page — it carries no
// report data and nothing about the person, but it is a request, and the copy
// says so rather than letting "nothing leaves your device" quietly cover it.
const MGC_GUIDES = [
  {n: '01', file: 'ownly-once-01-credit-card-pull-guide.pdf',
   title: 'Credit Card Pull Guide', pages: 16,
   blurb: 'Which report an issuer may pull, what to ask before you apply, and whether the account fits the budget. Read it before the inquiry, not after.'},
  {n: '02', file: 'ownly-once-02-whats-holding-your-score-back.pdf',
   title: 'What\\'s Holding Your Credit Score Back?', pages: 9,
   blurb: 'The report behind the score. Name the goal and the date, then work out which account to look at first.'},
  {n: '03', file: 'ownly-once-03-90-day-readiness-workbook.pdf',
   title: 'Your 90-Day Credit Readiness Workbook', pages: 18,
   blurb: 'A workbook for the next three months: a baseline, an evidence file per issue, the disputes, and a record of what came back.'},
  {n: '04', file: 'ownly-once-04-charge-off-dispute-kit.pdf',
   title: 'Charge-Off Dispute Kit', pages: 19,
   blurb: 'Twelve letters and, before them, what actually makes a charge-off wrong — balance, ownership, the payment-history months, the dates.'},
  {n: '05', file: 'ownly-once-05-eviction-reporting-dispute-guide.pdf',
   title: 'Eviction Reporting Dispute Guide', pages: 12,
   blurb: 'Tenant screening is a separate consumer file from your credit report. Adverse action, the free copy you are owed within 60 days, and how to dispute the record.'},
  {n: '06', file: 'ownly-once-06-different-bureau-results-guide.pdf',
   title: 'Different Bureau Results Dispute Guide', pages: 10,
   blurb: 'One bureau deleted it and another did not. How to use that difference honestly — and what it does not prove.'}
];

function mgcGuide(n) { return MGC_GUIDES.find(g => g.n === n); }

// One line, where the guide matches what is already on the screen.
function guideLink(n, lead) {
  const g = mgcGuide(n);
  if (!g) return '';
  return '<p style="margin:var(--space-4) 0 0;font-size:0.9375rem;">' +
         '<a href="/guides/' + g.file + '" download style="font-weight:600;">' +
         planEsc(g.title) + ' (PDF, ' + g.pages + ' pages, free)</a>' +
         (lead ? ' — ' + planEsc(lead) : '') + '</p>';
}

function renderGuidesSection() {
  let html = '<section style="margin-top:var(--space-16);">';
  html += '<div class="module-card">';
  html += '<div class="module-header"><p class="eyebrow">Yours to keep</p>' +
          '<h2>Six field guides, free</h2>' +
          '<p style="margin-top:var(--space-3);">No email, no account, no upsell — the same as everything else here. Two of them cover ground this tool does not.</p></div>';
  html += '<div class="id-list">';
  MGC_GUIDES.forEach(g => {
    html += '<div class="id-row" style="flex-direction:column;align-items:stretch;">' +
            '<div class="id-row-label"><a href="/guides/' + g.file + '" download>' +
            planEsc(g.title) + '</a> <span style="font-weight:400;color:var(--text-tertiary);">· PDF · ' + g.pages + ' pages</span></div>' +
            '<p style="font-size:0.9375rem;color:var(--text-secondary);margin:var(--space-2) 0 0;">' + planEsc(g.blurb) + '</p>' +
            '</div>';
  });
  html += '</div>';
  html += '<p style="font-size:0.875rem;color:var(--text-tertiary);margin-top:var(--space-6);">' +
          'Downloading a guide is a normal file request to this site — it sends nothing about you and nothing from your report. Your report never leaves your browser, guides or no guides.</p>';
  html += '</div></section>';
  return html;
}

// The same content on screen as in the packet, built from the same two arrays
// so the two cannot drift. Placed at the end of the analysis, after every
// letter, because it is the part that says what the letters cannot do.
function renderFreeHelpSection() {"""
rep(A, B, 1, 'MGC_GUIDES + renderers')

# ---- the section itself, before the closing "what this cannot do" ----
A = """  html += renderFreeHelpSection();

  // Footer in the step"""
B = """  // Before the closing limits, because two of the guides are the answer to a
  // limit rather than a bonus on top of the letters.
  html += renderGuidesSection();

  html += renderFreeHelpSection();

  // Footer in the step"""
rep(A, B, 1, 'guides section on the letters screen')

# ---- contextual: one line under the finding a guide actually covers ----
# Keyed off the finding TYPE rather than edited into each push site, so a new
# finding of an existing type picks the guide up for free and nothing has to be
# kept in sync by hand.
A = """      if (f.letter) {
        const tmpl = letterTemplates[f.letter];
        if (tmpl) html += `<p class="finding-letter-ref">→ We'll include the <strong>${tmpl.title}</strong> letter in your packet.</p>`;
      }"""
B = """      if (f.letter) {
        const tmpl = letterTemplates[f.letter];
        if (tmpl) html += `<p class="finding-letter-ref">→ We'll include the <strong>${tmpl.title}</strong> letter in your packet.</p>`;
      }
      // And where one of the guides is about exactly this, offer it here
      // rather than only in the list at the bottom of the packet.
      const gn = GUIDE_FOR_FINDING[f.type];
      if (gn) html += guideLink(gn, GUIDE_LEAD[f.type] || '');"""
rep(A, B, 1, 'findings carry a contextual guide link')

A = """function mgcGuide(n) { return MGC_GUIDES.find(g => g.n === n); }"""
B = """function mgcGuide(n) { return MGC_GUIDES.find(g => g.n === n); }

// Which finding earns which guide. Deliberately sparse — a link under every
// finding is wallpaper, and the point is that it shows up where it is the
// actual next thing to read.
const GUIDE_FOR_FINDING = {
  cross_bureau_conflict: '06',
  charge_off: '04',
  score_factors: '02',
  score_factors_tri: '02',
  inquiry_no_account: '01',
  inquiry_scoring_window: '01'
};
const GUIDE_LEAD = {
  cross_bureau_conflict: 'how to use one bureau\\'s deletion against another, and what it does not prove',
  charge_off: 'what actually makes a charge-off wrong, before you write about it',
  score_factors: 'working from the report behind the score',
  score_factors_tri: 'working from the report behind the score',
  inquiry_no_account: 'what an issuer pulls, and what to ask before the next one',
  inquiry_scoring_window: 'what an issuer pulls, and what to ask before the next one'
};"""
rep(A, B, 1, 'GUIDE_FOR_FINDING map')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
