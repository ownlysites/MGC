
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

A = """function tbParsePublicRecords(blk) {
  const out = [];
  const kinds = ['Bankruptcies', 'Judgments', 'Liens'];
  const present = kinds.filter(k =>
    blk.some(l => new RegExp('^' + k + '$', 'i').test(l)) &&
    !blk.some(l => new RegExp('you currently have no ' + k, 'i').test(l))
  );
  if (!present.length) return out;"""
B = """// Which bureau reports a public record, and which court it was filed in.
//
// Both are on the page and neither was being read. On Jose Santiago's report
// the Bankruptcies heading is followed by the single line "TransUnion" — that
// is the bureau reporting it, and the other two are not — and the detail table
// header reads "Date Filed | Reference Number | Status | Court | Liability |
// Exempt Amount | Asset Amount", with his row carrying N/A in the Court column.
//
// A public record with no court on it is the clearest defect on his whole file:
// a bankruptcy is a court proceeding, the court is the one fact that makes the
// record verifiable, and a bureau reporting the record without it cannot have
// checked it against anything.
//
// One sample is one sample, so this reads what is demonstrably there and leaves
// anything else null. The bureau is taken only when exactly one bureau name
// sits between the kind heading and the next heading; the court only when the
// header row actually declares a Court column.
const TB_PR_BUREAUS = ['TransUnion', 'Experian', 'Equifax'];
const TB_PR_STATUSES = ['Dismissed', 'Discharged', 'Satisfied', 'Released', 'Vacated', 'Filed', 'Withdrawn'];

function tbPrBureauFor(blk, kind) {
  const start = blk.findIndex(l => new RegExp('^' + kind + '$', 'i').test(l));
  if (start < 0) return null;
  const found = [];
  for (let i = start + 1; i < blk.length; i++) {
    const l = String(blk[i]).trim();
    if (/^(Bankruptcies|Judgments|Liens|Date Filed)/i.test(l)) break;
    const hit = TB_PR_BUREAUS.find(b => new RegExp('^' + b + '$', 'i').test(l));
    if (hit && found.indexOf(hit) < 0) found.push(hit);
  }
  return found.length === 1 ? found[0] : null;
}

function tbPrHasCourtColumn(blk) {
  return blk.some(l => /\\bStatus\\b[\\s\\S]*\\bCourt\\b/i.test(String(l)));
}

// The row is "date ref status court liability exempt asset". The three trailing
// money columns are each a figure or N/A, so the court is whatever sits between
// the status word and them — one token or several, since a real court name is
// several. Nothing there, or N/A, means no court was reported.
function tbPrCourt(rowRest) {
  let r = String(rowRest || '').trim();
  const st = TB_PR_STATUSES.find(w => new RegExp('\\\\b' + w + '\\\\b', 'i').test(r));
  if (st) r = r.replace(new RegExp('^[\\\\s\\\\S]*?\\\\b' + st + '\\\\b', 'i'), '').trim();
  const toks = r.split(/\\s+/).filter(Boolean);
  const isAmount = t => /^N\\/A$/i.test(t) || /^\\$?-?[\\d,]+(?:\\.\\d{2})?$/.test(t);
  let end = toks.length;
  let trailing = 0;
  while (end > 0 && trailing < 3 && isAmount(toks[end - 1])) { end--; trailing++; }
  const courtToks = toks.slice(0, end).filter(t => !/^N\\/A$/i.test(t));
  const court = courtToks.join(' ').trim();
  return court || null;
}

function tbParsePublicRecords(blk) {
  const out = [];
  const kinds = ['Bankruptcies', 'Judgments', 'Liens'];
  const present = kinds.filter(k =>
    blk.some(l => new RegExp('^' + k + '$', 'i').test(l)) &&
    !blk.some(l => new RegExp('you currently have no ' + k, 'i').test(l))
  );
  if (!present.length) return out;
  const prBureau = present.length === 1 ? tbPrBureauFor(blk, present[0]) : null;
  const hasCourt = tbPrHasCourtColumn(blk);"""
rep(A, B, 1, 'public record: bureau + court helpers')

A = """    const status = tbWord(context, ['Dismissed', 'Discharged', 'Satisfied', 'Released', 'Vacated', 'Filed', 'Withdrawn']);
    out.push({
      type: kind,
      date_filed: m[1],
      status: status || null,
      reference: tbCleanRef(m[2]),
      ambiguous_kind: present.length > 1
    });"""
B = """    const status = tbWord(context, TB_PR_STATUSES);
    out.push({
      type: kind,
      date_filed: m[1],
      status: status || null,
      reference: tbCleanRef(m[2]),
      // Null and "not reported" are different facts. court stays null when the
      // layout has no Court column at all; court_reported records whether the
      // column existed, so a missing court can be told apart from a format
      // that never carried one.
      court: hasCourt ? tbPrCourt(m[2]) : null,
      court_column: hasCourt,
      bureau: prBureau,
      ambiguous_kind: present.length > 1
    });"""
rep(A, B, 1, 'public record: carry court + bureau')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
