
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

A = """    const sub = [acc.account_number, acc.date_opened ? 'opened ' + acc.date_opened : null,
                 acc.balance != null ? 'balance $' + acc.balance.toLocaleString() : null]
                .filter(Boolean).join(' · ');"""
B = """    // acc.balance is a number out of the columnar parser and a string like
    // "$1,412" out of the three-bureau one. Prefixing "$" to both printed
    // "balance $$1,412" on every three-bureau report — which is most of them —
    // on the one screen where the person is deciding whether an account is
    // theirs. toLocaleString() on a string returns the string, so it hid.
    const sub = [acc.account_number, acc.date_opened ? 'opened ' + acc.date_opened : null,
                 acc.balance != null ? 'balance ' + reviewMoney(acc.balance) : null]
                .filter(Boolean).join(' · ');"""
rep(A, B, 1, 'item review balance')

A = """  const acctRows = acctPairs.map(function (pair) {"""
B = """  // One money formatter for whatever the parsers hand over: a number, a string
  // that already carries its own "$", or something unreadable, which is printed
  // as it came rather than mangled into a figure.
  function reviewMoney(v) {
    if (typeof v === 'number' && isFinite(v)) return '$' + v.toLocaleString();
    const raw = String(v).trim();
    const n = parseFloat(raw.replace(/[$,]/g, ''));
    if (!isFinite(n)) return raw;
    return '$' + n.toLocaleString(undefined, {maximumFractionDigits: 2});
  }

  const acctRows = acctPairs.map(function (pair) {"""
rep(A, B, 1, 'reviewMoney()')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
