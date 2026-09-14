
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

A = """        <h3 style="margin-top:var(--space-8);">Step 5: Send your § 605B block letters</h3>
        <p>For each fraudulent item, mail the § 605B Block letter we\\'ve generated (above). Enclose:</p>"""
B = """        <h3 style="margin-top:var(--space-8);">Step 5: Send your § 605B block letters</h3>
        ${(function () {
          // The block letter is built from the accounts marked "never mine" in
          // the review above, and from nothing else — a sworn statement is not
          // something to assemble out of the derogatory list on someone's
          // behalf. That is right, but this step used to promise a letter
          // "we've generated (above)" whether or not one existed, and nothing
          // anywhere told the person that the marking is what creates it. A
          // victim could read all seven steps and never learn why their
          // strongest letter was missing.
          const never = (typeof reviewedAccounts === 'function') ? reviewedAccounts('never') : [];
          if (!never.length) {
            return `<div class="alert alert-critical" style="margin:var(--space-4) 0;">
              <h4 style="color:var(--danger-dark);margin-bottom:var(--space-2);">Your § 605B letter is not built yet — here is why</h4>
              <p style="margin:0 0 var(--space-2);">This letter is sworn under penalty of perjury, so it is written only from accounts <strong>you</strong> have identified as not yours. Nothing here guesses at that from your report, because a sworn statement about an account you did open is the one mistake in this whole process you cannot take back.</p>
              <p style="margin:0;">Go up to <strong>&ldquo;Check what&rsquo;s actually yours&rdquo;</strong> and mark every fraudulent account <em>Never mine</em>. The letter appears the moment you do, naming exactly those accounts. <button type="button" class="btn btn-sm btn-primary" style="margin-left:var(--space-2);" onclick="var el=document.getElementById('item-review'); if(el) el.scrollIntoView({behavior:'smooth', block:'start'});">Take me there</button></p>
            </div>`;
          }
          const names = never.map(a => planEsc ? planEsc(a.creditor || 'an account') : (a.creditor || 'an account'));
          return `<div class="alert" style="margin:var(--space-4) 0;background:var(--surface-2,#f6f7f9);">
            <p style="margin:0;"><strong>Built from what you marked:</strong> ${names.length} account${names.length === 1 ? '' : 's'} you identified as never yours — ${names.join(', ')}. Mark more in the review above and the letter rewrites itself.${(state.ftcReportNumber || '').trim() ? '' : ' <strong>No FTC report number entered yet</strong>, so none is printed — add it in Step 1 above and the letter rebuilds.'}</p>
          </div>`;
        })()}
        <p>For each fraudulent item, mail the § 605B Block letter we\\'ve generated (above). Enclose:</p>"""
rep(A, B, 1, 'Step 5 says what builds the letter')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
