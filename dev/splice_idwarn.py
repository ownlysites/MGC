
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

# The identity-theft path had four places saying a version of "be careful":
# this block, the item review, the separator sheet, and Step 5. The last three
# are operational — they tell you what to do next. This one was the only pure
# warning, and it ran ninety words to say one thing four ways.
#
# Short now, and it earns its length by saying what the long version never did:
# that we build from whatever is marked and cannot tell what is true, and that
# a block on an account you did open is reversed by the same section that
# grants it. Anyone unsure gets a person to talk to rather than another lecture.
A = """          <h4 style="color:var(--danger-dark);margin-bottom:var(--space-2);">⚠ Read this before anything else</h4>
          <p><strong>Identity theft is a federal crime. So is falsely claiming identity theft to remove accurate information from a credit report.</strong> Both are punishable by up to 5 years in prison under 18 U.S.C. § 1028. The identity theft affidavit you\\'ll sign at IdentityTheft.gov is sworn under penalty of perjury. Every item you claim is fraudulent will be scrutinized. Proceed only if you are truly a victim, and only with items that are truly the product of fraud.</p>"""
B = """          <h4 style="color:var(--danger-dark);margin-bottom:var(--space-2);">⚠ This one is sworn</h4>
          <p><strong>You sign this affidavit under penalty of perjury, and we build the letter from whatever you mark — we cannot tell which accounts are really yours.</strong> A block on an account you did open gets reversed under 15 U.S.C. § 1681c-2(c), and a false claim carries up to 5 years under 18 U.S.C. § 1028. Unsure about an item? Leave it off, or ask a consumer attorney — the <a href="https://www.consumeradvocates.org/findanattorney" target="_blank" rel="noopener">NACA directory</a> is free to search and most work on contingency.</p>"""
rep(A, B, 1, 'identity theft warning: short, and says what we do not know')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
