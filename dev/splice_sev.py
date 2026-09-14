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

# ---- 1. severity by category, not by string ----
A = """function statusClass(v) {
  const k = String(v || '').toLowerCase().trim();"""
B = r"""// How bad, on one coarse scale, regardless of wording. Ranking by the raw
// string made three bureaus that all said "collection" look like a
// disagreement — "Collection", "Collection account. $3,927" and "Collection
// account" are three spellings of one fact, and the tool generated a letter
// telling the bureaus they disagreed about how far behind the account went.
// That is a false statement in an envelope, which is worse than a missed
// dispute. Compare the category.
function statusSeverity(v) {
  const k = String(v || '').toLowerCase().trim();
  if (!k) return null;
  if (/charge[\s-]?off|charged off|profit and loss|write[\s-]?off/.test(k)) return 9;
  if (/collection/.test(k)) return 9;
  if (/repossess|foreclos|deed in lieu|short sale/.test(k)) return 9;
  if (/bankrupt/.test(k)) return 9;
  if (/settled for less|paid settle|settlement accepted/.test(k)) return 8;
  if (/\b(120|150|180)\b/.test(k)) return 6;
  if (/\b90\b/.test(k)) return 5;
  if (/\b60\b/.test(k)) return 4;
  if (/\b30\b/.test(k)) return 3;
  if (/past due|delinquen|late\b/.test(k) && !/never late|not late|no late/.test(k)) return 2;
  return 0;
}

function statusClass(v) {
  const k = String(v || '').toLowerCase().trim();"""
rep(A, B, 1, 'statusSeverity')

A = """    } else {
      const ranks = derog.map(e => e.rank).filter((v, i, arr) => arr.indexOf(v) === i);
      if (ranks.length > 1) kind = 'severity_mismatch';
    }"""
B = """    } else {
      // Compare the category, not the sentence. Three bureaus all reporting a
      // collection agree with each other however differently they word it.
      const sev = derog.map(e => statusSeverity(e.status)).filter(v => v !== null);
      const distinct = sev.filter((v, i, arr) => arr.indexOf(v) === i);
      if (distinct.length > 1) kind = 'severity_mismatch';
    }"""
rep(A, B, 1, 'severity comparison')

# ---- 2. one finding per account per rule ----
A = """function findFactualInconsistencies(parsed) {
  const out = [];"""
B = """// One row per account per rule. The per-bureau loop below is right — each
// bureau really is reporting the defect — but three identical lines in a letter
// about one account reads as padding, and the bureaus belong on one line.
function dedupeFactual(list) {
  const byKey = {};
  const out = [];
  (list || []).forEach(f => {
    const k = String(f.creditor || '').toUpperCase() + '|' + f.rule;
    if (byKey[k]) {
      (f.bureaus || []).forEach(b => {
        if (byKey[k].bureaus.indexOf(b) < 0) byKey[k].bureaus.push(b);
      });
      return;
    }
    const copy = Object.assign({}, f);
    copy.bureaus = (f.bureaus || []).slice();
    byKey[k] = copy;
    out.push(copy);
  });
  return out;
}

function findFactualInconsistencies(parsed) {
  const out = [];"""
rep(A, B, 1, 'dedupeFactual')

A = """  analysis.factual = findFactualInconsistencies(parsed);"""
B = """  analysis.factual = dedupeFactual(findFactualInconsistencies(parsed));"""
rep(A, B, 1, 'use dedupe')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
