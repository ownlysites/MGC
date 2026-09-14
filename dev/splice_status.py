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

A = """function statusClass(v) {
  const k = String(v || '').toLowerCase();
  if (!k) return null;
  if (TB_CLEAN_WORDS.includes(k)) return 'clean';
  if (TB_NEUTRAL_WORDS.includes(k)) return 'neutral';
  return (TB_STATUS_RANK[k] !== undefined && TB_STATUS_RANK[k] >= 2) ? 'derogatory' : null;
}"""

B = r"""// Exact membership was too brittle to do its job. The three bureaus write the
// same fact a dozen ways — "Pays account as agreed", "Open/Never late.", "Paid
// or paying as agreed" are all one status and none of them was in the list, so
// every one classified as null and the cross-bureau comparison silently had
// nothing to compare. On Michael Gibson's three reports that meant 27 accounts
// carrying a status from every bureau and zero contradictions found.
//
// Still deliberately conservative, because the answer ends up in a letter. An
// unrecognised status returns null and is ignored rather than guessed at, and
// "closed" is a state rather than a payment claim — Closed-versus-Late is not
// treated as a disagreement, because an account really can be closed and have
// had a late payment.
function statusClass(v) {
  const k = String(v || '').toLowerCase().trim();
  if (!k) return null;
  if (TB_CLEAN_WORDS.includes(k)) return 'clean';
  if (TB_NEUTRAL_WORDS.includes(k)) return 'neutral';

  // Derogatory wins wherever it appears: "Paid, was a charge-off" is derogatory.
  if (/charge[\s-]?off|charged off|collection|repossess|foreclos|deed in lieu|short sale|bankrupt|settled for less|paid settle|default(ed)?\b|profit and loss|write[\s-]?off/.test(k)) return 'derogatory';
  if (/\b(30|60|90|120|150|180)\b\s*(days?|d)?\s*(late|past due)/.test(k)) return 'derogatory';
  if (/past due|delinquen|late\b/.test(k) && !/never late|not late|no late/.test(k)) return 'derogatory';

  // Clean: an explicit statement that it is being paid, or was never late.
  if (/never late|not late|no late/.test(k)) return 'clean';
  if (/pays?\b.{0,16}as agreed|paying as agreed|paid or paying|as agreed|current|in good standing|paid on time/.test(k)) return 'clean';
  if (/^paid\b/.test(k) && !/charge|collection|settle/.test(k)) return 'clean';

  // A state rather than a payment claim.
  if (/^(open|closed|former|transferred|re.?financed|no data|too new|unrated)/.test(k)) return 'neutral';

  const ranked = TB_STATUS_RANK[k];
  return (ranked !== undefined && ranked >= 2) ? 'derogatory' : null;
}"""
rep(A, B, 1, 'statusClass patterns')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
