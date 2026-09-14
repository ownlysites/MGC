
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

# "Under penalty of perjury" out of every line the consumer reads.
#
# Dave's call, and the reasoning holds: it is not our oath to invoke and we
# enforce nothing. What the phrase was carrying — that this letter is a sworn
# statement rather than an ordinary dispute, and that a false one has a
# consequence — is carried by the § 1028 sentence and by the word "sworn",
# which are facts rather than posture. The comments in the source keep it,
# because they explain to the next developer why these gates exist.

# 1. the warning block
A = """<strong>You sign this affidavit under penalty of perjury, and we build the letter from whatever you mark — we cannot tell which accounts are really yours.</strong>"""
B = """<strong>You sign an affidavit at IdentityTheft.gov, and we build the letter from whatever you mark — we cannot tell which accounts are really yours.</strong>"""
rep(A, B, 1, 'warning block')

# 2. Step 5, where the phrase was the REASON the letter is built only from
#    marked accounts. The reason survives; the phrase goes.
A = """This letter is sworn under penalty of perjury, so it is written only from accounts <strong>you</strong> have identified as not yours."""
B = """This letter is a sworn statement, so it is written only from accounts <strong>you</strong> have identified as not yours."""
rep(A, B, 1, 'Step 5 reason')

# 3. the separator sheet that gates mailing without an FTC number
A = """This letter is sworn under penalty of perjury and it runs on your FTC Identity Theft Report number."""
B = """This letter is a sworn statement and it runs on your FTC Identity Theft Report number."""
rep(A, B, 1, 'separator sheet')

# 4. the identity-answers check on the plan
A = """An identity theft report is sworn under penalty of perjury &mdash; 18 U.S.C. &sect; 1028 makes a false one a federal crime"""
B = """18 U.S.C. &sect; 1028 makes a false identity theft report a federal crime"""
rep(A, B, 1, 'plan identity check')

# 5. the disclosures page
A = """The identity theft affidavit required for a §605B block is signed under penalty of perjury. Proceed with honesty.</p>"""
B = """A §605B block obtained by a material misrepresentation may be rescinded under 15 U.S.C. § 1681c-2(c), and every item put back.</p>"""
rep(A, B, 1, 'disclosures page')

# 6. the action-plan detail line
A = """The identity theft affidavit is sworn under penalty of perjury. Proceed with honesty.'"""
B = """A block obtained by a material misrepresentation may be rescinded under 15 U.S.C. § 1681c-2(c).'"""
rep(A, B, 1, 'action plan detail')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
