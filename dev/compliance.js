// Two gates that need no client data, so they run anywhere.
//
// 1. CROA. 15 U.S.C. § 1679a(3)(A) makes someone a credit repair organization
//    if they sell a service "in return for the payment of money or other
//    valuable consideration" for the express or implied purpose of improving a
//    credit record. The tool is free and sells nothing, so the definition is
//    not met — and what would break that is a free diagnosis existing to sell a
//    paid cure, or any promise of a score or a removal anywhere in the product.
//    Also § 1679b(a), which binds "no person" rather than "no CRO": nothing may
//    counsel a consumer to make an untrue statement, or to alter their
//    identification to conceal accurate adverse information.
//
// 2. Originality. Nearly every free dispute letter online is a lightly edited
//    copy of the FTC's two samples, which means a compliance desk has read
//    those sentences thousands of times. No fragment may share a long run of
//    words with one.
const H = require('./harness');
const R = H.reporter('compliance — CROA language and letter originality');
const api = H.load(['FREE_HELP', 'TOOL_LIMITS', 'renderFreeHelpSection', 'breachDatabase']);

// ---------------------------------------------------------------- CROA ----
R.section('nothing promises a score or a removal');

// These match CLAIMS, not words. An earlier version banned "guarantee" outright
// and flagged "what the Fair Credit Reporting Act guarantees is one free
// report" — a statutory guarantee, the opposite of a promise by us — and banned
// "paid version", flagging "there is no paid version of this tool". A gate that
// fires on the negation of itself trains you to ignore it.
const BANNED = [
  [/\bwe\s+(guarantee|promise)\b/i,                                    'a guarantee by us'],
  [/\bguaranteed\s+(results?|deletions?|removals?|score)/i,             'a guaranteed outcome'],
  [/\bwe (will|can) (remove|delete|erase|fix) (your|the|these)/i,       'a promise to remove'],
  [/\braise your score by\b/i,                                          'a score promise'],
  [/\byour score (will|should) (go up|increase|jump|rise)\b/i,          'a score prediction'],
  [/\b\d+\s*points? (in|within) \d+ (days?|weeks?|months?)\b/i,         'a points-in-time claim'],
  [/\bupgrade to (the |our )?(paid|premium|pro)\b/i,                    'an upgrade gate'],
  [/\b(available|included) (only )?(in|with) (the )?(paid|premium|pro)\b/i, 'a gated capability']
];

const strip = h => String(h).replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ');
const screen = typeof api.renderFreeHelpSection === 'function' ? strip(api.renderFreeHelpSection()) : '';
R.check('the free-help section renders', screen.length > 500, screen.length + ' chars');
BANNED.forEach(([rx, why]) => {
  const hit = screen.match(rx);
  R.check('no ' + why, !hit, hit ? '"' + hit[0] + '"' : 'clean');
});

R.section('the offer is honest about being optional');
R.check('says nothing is held back',       /no paid version of this tool/i.test(screen));
R.check('says it is not credit repair',    /not credit repair/i.test(screen));
R.check('says the packet works without it', /you do not need it/i.test(screen));
R.check('names the advance-fee rule',      /1679b\(b\)/.test(screen));
R.check('names the 3-day cancellation',    /three business days to cancel/i.test(screen));

R.section('the free routes are named with their current addresses');
[['annualcreditreport.com', 'the three reports'],
 ['innovis.com', 'Innovis'],
 ['consumer.risk.lexisnexis.com', 'LexisNexis'],
 ['sagestreamllc.com', 'SageStream'],
 ['chexsystems.com/request-reports', 'ChexSystems on its current path'],
 ['nctue.com', 'NCTUE'],
 ['irs.gov/identity-theft-fraud-scams/get-an-identity-protection-pin', 'the IRS IP PIN'],
 ['optoutprescreen.com', 'the prescreen opt-out'],
 ['nfcc.org', 'NFCC'],
 ['consumeradvocates.org/findanattorney', 'the NACA finder'],
 ['consumerfinance.gov/complaint', 'the CFPB portal']
].forEach(([needle, label]) => R.check('names ' + label, screen.indexOf(needle) >= 0));

R.section('the three claims that are easy to get wrong');
R.check('weekly reports called a bureau commitment, not a right',
        /not a right the statute gives you|commitment the three bureaus made/i.test(screen));
R.check('NFCC not claimed free across the board',
        /some charge for specific services/i.test(screen));
R.check('NACA attorneys not claimed to be free', !/free (lawyer|attorney)s?\b/i.test(screen));
R.check('fee-shifting cited instead', /1681n\(a\)\(3\)/.test(screen) && /1692k\(a\)\(3\)/.test(screen));

R.section('nothing is captured from the visitor');
const src = api.SRC;
R.check('no email input',    !/type=["']email["']/i.test(src));
R.check('no password input', !/type=["']password["']/i.test(src));
R.check('no off-origin form post', !/<form[^>]+action=["']https?:/i.test(src));
const posts = (src.match(/fetch\([^)]*method:\s*['"]POST['"]/gi) || []).length;
R.check('the only POST is the plan counter', posts <= 1, posts + ' POST call(s)');

// --------------------------------------------------------- originality ----
R.section('no fragment reads like a template anyone can download');

// The FTC's two sample dispute letters, transcribed from consumer.ftc.gov, plus
// the stock phrasings that recur across the template sites.
const CORPUS = [
  'I am writing to dispute the following information in my file.',
  'This item is inaccurate or incomplete because',
  'I am requesting that this item be removed or request another specific change to correct the information.',
  'Enclosed is documentation supporting my request',
  'Please investigate this matter and delete or correct the disputed item as soon as possible.',
  'I am writing to dispute the following information that your company supplied to',
  'I have circled the items I dispute on the attached copy of my credit report.',
  'Enclosed are copies of my credit report and any other documents supporting my request.',
  'Please reinvestigate this matter and contact the nationwide credit bureaus to have them delete or correct the disputed items as soon as possible.',
  'Under the Fair Credit Reporting Act you are required to investigate this dispute within 30 days.',
  'Please send me written confirmation that the item has been deleted from my credit report.',
  'I am exercising my right under the Fair Credit Reporting Act to dispute inaccurate information.',
  'This letter is a formal complaint that you are reporting inaccurate credit information.',
  'I demand that you validate this debt pursuant to the Fair Debt Collection Practices Act.'
];
const words = s => String(s).toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim().split(' ');
const corp = CORPUS.map(words);
function longestRun(a, b) {
  let best = 0;
  for (let i = 0; i < a.length; i++) for (let j = 0; j < b.length; j++) {
    let n = 0;
    while (i + n < a.length && j + n < b.length && a[i + n] === b[j + n]) n++;
    if (n > best) best = n;
  }
  return best;
}
const THRESHOLD = parseInt(process.env.RUN || '7', 10);
let checked = 0; const flagged = [];
Object.keys(api.fragments || {}).forEach(pool => {
  if (!Array.isArray(api.fragments[pool])) return;
  api.fragments[pool].forEach((frag, i) => {
    if (typeof frag !== 'string') return;
    checked++;
    const w = words(frag);
    let worst = {n: 0, src: ''};
    corp.forEach((c, ci) => { const n = longestRun(w, c); if (n > worst.n) worst = {n: n, src: CORPUS[ci]}; });
    if (worst.n >= THRESHOLD) flagged.push({pool, i, n: worst.n, frag: frag.slice(0, 90), src: worst.src.slice(0, 60)});
  });
});
flagged.forEach(f => {
  console.log('        ours:   ' + f.frag);
  console.log('        theirs: ' + f.src);
});
R.check(checked + ' fragments share fewer than ' + THRESHOLD + ' consecutive words with a public template',
        flagged.length === 0, flagged.length ? flagged.map(f => f.pool + '[' + f.i + ']').join(', ') : 'clean');

// ------------------------------------------------------ breach honesty ----
R.section('the breach data does not repeat the numbers the press got wrong');
const db = api.breachDatabase || [];
const find = id => db.find(b => b.id === id) || {};
R.check('every entry declares an SSN answer',
        db.every(b => ['yes', 'no', 'partial', 'varies', 'unknown'].indexOf(b.ssn) >= 0));
R.check('every entry declares its provenance',
        db.every(b => ['confirmed', 'contested', 'unverified'].indexOf(b.v) >= 0));
R.check('every confirmed entry cites a source',
        db.filter(b => b.v === 'confirmed').every(b => /^https?:\/\//.test(b.src || '')));
R.check('NPD is not asserted at 2.9 billion people', !/2\.9 billion/.test(find('npd_2024').affected || ''));
R.check('Ticketmaster does not repeat 560 million', !/560/.test(find('ticketmaster_2024').affected || ''));
R.check('Capital One is not sold as an SSN breach', find('capital_one_2019').ssn === 'partial');
R.check('the AT&T call records carry no SSN', find('att_2024_records').ssn === 'no');

R.done();
