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

A = """let planCounterValue = null;
let planCounted = false;"""
B = """let planCounterValue = null;
let planCounted = false;
let planCountInFlight = false;
let planCountAttempts = 0;"""
rep(A, B, 1, 'counter state')

A = """function bumpPlanCounter() {
  if (planCounted) return;
  planCounted = true;
  // One per browser session, so re-reading your own letters does not inflate it.
  try {
    if (sessionStorage.getItem('mgc_plan_counted')) return;
    sessionStorage.setItem('mgc_plan_counted', '1');
  } catch (e) { /* private mode: fall through, the session flag above still holds */ }
  if (typeof fetch !== 'function') return;
  fetch(PLAN_COUNTER_ENDPOINT, {method: 'POST', cache: 'no-store'})
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (d && typeof d.count === 'number') { planCounterValue = d.count; renderPlanCounter(d.count); }
    })
    .catch(function () {});
}"""
B = """function bumpPlanCounter() {
  // The old version set planCounted = true and wrote the session flag BEFORE
  // the request went out, then swallowed every failure. So a POST that never
  // landed — an offline visit, a blocked request, a bad gateway — looked
  // exactly like one that did, and the count silently stopped counting with
  // nothing anywhere to say so. Mark it counted when it is counted.
  if (planCounted || planCountInFlight) return;

  // One per browser session, so re-reading your own letters does not inflate it.
  try {
    if (sessionStorage.getItem('mgc_plan_counted')) { planCounted = true; return; }
  } catch (e) { /* private mode: the in-memory flag below still holds */ }

  if (typeof fetch !== 'function') return;
  planCountInFlight = true;
  fetch(PLAN_COUNTER_ENDPOINT, {method: 'POST', cache: 'no-store'})
    .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)); })
    .then(function (d) {
      planCountInFlight = false;
      planCounted = true;
      try { sessionStorage.setItem('mgc_plan_counted', '1'); } catch (e) {}
      if (d && typeof d.count === 'number') { planCounterValue = d.count; renderPlanCounter(d.count); }
    })
    .catch(function (err) {
      planCountInFlight = false;
      planCountAttempts++;
      // Two attempts, then stop. Retrying forever would put a request on every
      // navigation for somebody whose network refuses it, which is worse than
      // an undercount.
      if (planCountAttempts >= 2) planCounted = true;
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('[MGC] plan not counted (' + err.message + '). Attempt ' + planCountAttempts + ' of 2.');
      }
    });
}"""
rep(A, B, 1, 'bumpPlanCounter')

A = """    .catch(function () { /* offline, or the route is not deployed yet */ });"""
B = """    .catch(function (err) {
      // Saying so beats a silent fallback to the seed. A number that is simply
      // the seed, on a page that never reached its own API, is indistinguishable
      // from a real count of zero.
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('[MGC] plan counter unreachable (' + (err && err.message) + '); showing the seed.');
      }
    });"""
rep(A, B, 1, 'loadPlanCounter logging')

io.open(P, 'w', encoding='utf-8').write(s)
print('bytes %d -> %d (+%d)' % (orig, len(s), len(s) - orig))
