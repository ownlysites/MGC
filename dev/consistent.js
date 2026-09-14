// The packet must never say one thing and do another.
//
// Dave: "the produced plan is saying no negatives but then showing negatives
// in the letters." It did. "No derogatory items" was decided from the accounts
// alone, while the letters are built from the accounts AND the field-level
// contradictions AND the cross-bureau disagreements. A file with no late
// payment anywhere but a closed account still reporting a monthly payment got
// a page saying there was nothing to dispute, above a packet disputing things.
//
// This drives the analysis from synthetic parsed reports rather than PDFs, so
// it needs no client data to run.
const fs = require('fs');
const src = fs.readFileSync(process.env.MGC_INDEX || '/Users/daveivery/Documents/Claude/Projects/MGC/index.html', 'utf8');
const blocks = []; const re = /<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/gi; let m;
while ((m = re.exec(src)) !== null) blocks.push(m[1]);
const stub = new Proxy(function(){}, {get(t,k){if(k==='style'||k==='classList'||k==='dataset')return stub;if(k==='value'||k==='innerHTML'||k==='textContent'||k==='id')return '';if(k==='children'||k==='childNodes')return [];if(k===Symbol.toPrimitive||k==='toString')return()=>'';return stub;},set(){return true;},apply(){return stub;}});
global.document={getElementById:()=>stub,querySelector:()=>stub,querySelectorAll:()=>[],createElement:()=>stub,addEventListener:()=>{},body:stub,head:stub,documentElement:stub};
global.window={addEventListener:()=>{},matchMedia:()=>({matches:false,addListener:()=>{}}),location:{href:'http://localhost/'},print:()=>{}};
global.navigator={userAgent:'node'};global.localStorage={getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
global.sessionStorage={getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
global.alert=()=>{};global.requestAnimationFrame=f=>setTimeout(f,0);
eval(blocks.join('\n;\n') + ';global.__a={state,runAnalysis,determineLetterPacket,regenerateAllLetters,buildLetterContext,letterTemplates,buildActionPlanDoc};');
const A = global.__a, st = A.state;
let fails = 0; const check = (n,c,d)=>{console.log((c?'  PASS  ':'  FAIL  ')+n+(d?'  ['+d+']':''));if(!c)fails++;};

// The contradiction detector reads acc.per_bureau_fields, not the flat fields —
// it is comparing what each bureau says. A fixture without it produces zero
// findings and tests nothing, which is exactly how my first draft of this file
// "passed" the broken build.
function perBureau(o) {
  const one = Object.assign({
    account_status: 'Open', account_rating: 'Pays as agreed', payment_status: 'Current',
    creditor_remarks: '', payment_amount: '$50', balance_owed: '$1,000',
    high_balance: '$2,000', past_due: '$0', date_opened: '01/2015',
    date_last_active: '08/2026', date_last_paid: '08/2026'
  }, o);
  return {Equifax: one, Experian: one, TransUnion: one};
}

function acct(o) {
  return Object.assign({
    creditor: 'GOOD BANK', account_number: '1234567890123456', account_type: 'Credit Card',
    date_opened: '01/2015', date_closed: null, date_reported: '08/2026', date_last_payment: '08/2026',
    open_closed: 'Open', status: 'Pays as agreed', balance: '$1,000', high_balance: '$2,000',
    credit_limit: '$5,000', monthly_payment: '$50', past_due: '$0', responsibility: 'Individual',
    terms: null, address: null, phone: null, comments: null, dofd: null,
    reported_by: ['Equifax','Experian','TransUnion'],
    is_collection: false, is_charge_off: false, has_late_payments: false,
    is_repossession: false, in_bankruptcy: false,
    per_bureau_fields: perBureau({})
  }, o);
}

function run(parsed) {
  st.upload = {}; st.analysis = null; st.letterOutputs = {}; st.letterVariants = {}; st.r2Dropped = [];
  st.actionPlan = null; st.roundTwo = null; st.mode = null; st.selectedBreach = null;
  st.itemReview = {inquiries:{},accounts:{},resolved:{},reviewed:false};
  st.identityReview = {addresses:{},aka:{},employers:{},au_explains:null,reviewed:false};
  st.userInfo = {name:'PAT MORGAN', address:'1 Main St', city:'Sarasota, FL 34236'};
  st.intake = {situation:'cleanup', special_flags:[], state:'FL', voice:'plain', prior_dispute:'no',
    recent_move:'no', primary_goal:'peace', hardship:[], channel:[], breach_which:[], breach_misuse:[]};
  st.upload = {parsed: parsed};
  A.runAnalysis();
  st.analysis.letters = A.determineLetterPacket(st.analysis);
  A.regenerateAllLetters();
  A.buildActionPlanDoc();
  const ctx = A.buildLetterContext(A.letterTemplates.initial_bureau_dispute);
  const plan = String(st.planHtml || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
  return {items: ctx.items || [], plan: plan, findings: st.analysis.findings || [],
          factual: st.analysis.factual || [], contra: st.analysis.contradictions || []};
}

const base = {format:'three_bureau', bureaus:['Equifax','Experian','TransUnion'],
  inquiries:[], collections:[], publicRecords:[], personal:{}, scores:[], creditorContacts:[]};

// ---------- 1. genuinely clean ----------
console.log('\n== a genuinely clean report ==');
const clean = run(Object.assign({}, base, {accounts:[acct({}), acct({creditor:'SECOND BANK', account_number:'9999888877776666'})]}));
console.log('   factual: ' + clean.factual.length + ', cross-bureau: ' + clean.contra.length + ', letter items: ' + clean.items.length);
check('says no derogatory items',        /No derogatory items found/.test(clean.plan));
check('and it is telling the truth',     clean.items.length === 0, clean.items.map(i=>i.creditor).join(', ') || 'no items');
check('no contradiction claim made',     !/still is not accurate/.test(clean.plan));

// ---------- 2. Dave's case: clean-looking, but the report contradicts itself ----------
// A closed account still reporting a monthly payment, and a balance above the
// highest balance ever recorded. No late payment anywhere.
console.log('\n== no late payments, but the report contradicts itself ==');
const tricky = run(Object.assign({}, base, {accounts:[
  acct({creditor:'CLOSED CARD CO', account_number:'4444333322221111',
        open_closed:'Closed', date_closed:'03/2024', status:'Closed', monthly_payment:'$75', balance:'$0',
        per_bureau_fields: perBureau({account_status:'Closed', account_rating:'Paid, closed',
                                      payment_status:'Current', payment_amount:'$75', balance_owed:'$0'})}),
  acct({creditor:'TRANSFERRED CO', account_number:'5555666677778888',
        status:'Transferred', balance:'$2,400',
        per_bureau_fields: perBureau({account_status:'Transferred', account_rating:'Transferred',
                                      balance_owed:'$2,400', payment_amount:'$0'})})
]}));
console.log('   factual: ' + tricky.factual.length + ', cross-bureau: ' + tricky.contra.length + ', letter items: ' + tricky.items.length);
check('there IS something to dispute',        tricky.items.length > 0, tricky.items.length + ' item(s)');
check('the plan does NOT claim nothing to dispute',
      !/There is nothing here to dispute/.test(tricky.plan));
check('it does not say "No derogatory items found"',
      !/No derogatory items found/.test(tricky.plan));
check('it says there are no late payments',   /No late payments/.test(tricky.plan));
check('and that the report is still wrong',   /still is not accurate/.test(tricky.plan));
check('and it counts them',                  /place(s)? where the report contradicts itself/.test(tricky.plan));

// ---------- 3. a public record with no bad tradeline ----------
console.log('\n== a public record and nothing else ==');
const pub = run(Object.assign({}, base, {
  accounts:[acct({})],
  publicRecords:[{type:'Civil judgment', creditor:'COUNTY COURT', amount:'$3,200', date_filed:'05/2023', bureau:'Equifax'}]
}));
check('a public record is not a clean report', !/No derogatory items found/.test(pub.plan));

// ---------- 4. the general invariant, on every shape above ----------
console.log('\n== the invariant ==');
[['clean',clean],['contradicted',tricky],['public record',pub]].forEach(([label, r]) => {
  const saysNothing = /There is nothing here to dispute/.test(r.plan);
  check('"' + label + '": never claims nothing to dispute while disputing something',
        !(saysNothing && r.items.length > 0),
        saysNothing ? ('claims clean with ' + r.items.length + ' item(s)') : 'consistent');
});

// ---------- 5. the counter cannot mark itself counted before it counts ----------
console.log('\n== the plan counter ==');
const body = src;
check('does not mark counted before the request',
      !/planCounted = true;\s*\n\s*\/\/ One per browser session/.test(body));
check('marks counted inside the success path',
      /planCountInFlight = false;\s*\n\s*planCounted = true;/.test(body));
check('a failure is logged, not swallowed',
      /plan not counted/.test(body));
check('and retries are bounded',
      /planCountAttempts >= 2/.test(body));

console.log(fails ? '\n' + fails + ' CHECK(S) FAILED\n' : '\nall clear\n');
process.exit(fails ? 1 : 0);
