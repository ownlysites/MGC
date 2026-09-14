
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

A = """  const itemsList = items.length > 0 ? items.map((it, i) => {
    const reason = it.reason || 'The information is inaccurate as reported.';
    return `${i+1}. Account ending ${it.account || '[XXXX]'} — ${it.creditor || '[Creditor]'}\\n   Issue: ${reason}`;
  }).join('\\n\\n') : '[Describe each disputed item: account number, what is inaccurate, and what the correct information should be]';"""
B = """  // Not every report carries an account number for every tradeline, and a
  // § 623(b) letter reading "Account ending [XXXX]" is a bracket in an envelope.
  // The creditor already knows which of their accounts is mine; the number
  // narrows it where we have one and is simply left out where we do not.
  const itemsList = items.length > 0 ? items.map((it, i) => {
    const reason = it.reason || 'The information is inaccurate as reported.';
    const who = it.creditor || 'the account below';
    const num = it.account ? ' — account ending ' + it.account : '';
    return `${i+1}. ${who}${num}\\n   Issue: ${reason}`;
  }).join('\\n\\n') : [
    'Each item I am disputing, with what is wrong about it:',
    '',
    '    ______________________________________________________________',
    '',
    '    ______________________________________________________________'
  ].join('\\n');"""
rep(A, B, 1, 'furnisher dispute item line')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
