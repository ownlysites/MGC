// Build every letter template with NOTHING in its context and list what comes
// out bracketed.
//
// This is an inventory, not a pass/fail gate. Most of these placeholders are
// unreachable in a real packet because determineLetterPacket only pushes a
// letter once the data behind it exists — mailable.js proves that across
// sixteen scenarios on real reports and finds no brackets at all.
//
// It exists because one of them WAS reachable. The § 623(b) direct dispute
// printed "Account ending [XXXX]" for a tradeline whose report carried no
// account number, and no fixture had ever been missing one. A parser that
// misses a single field on a single account is all it takes, so knowing which
// letters have a bracket waiting behind a missing field is worth having
// written down.
//
//   node dev/emptyctx.js
//
// Needs no client data.
const H = require('./harness');
const api = H.load();

const st = H.session(api, {});
st.userInfo = {name: 'PAT MORGAN', address: '1 Main St', city: 'Sarasota, FL 34236',
               dob: '', ssnLast4: ''};

const ids = Object.keys(api.letterTemplates);
const rows = [];

ids.forEach(id => {
  const t = api.letterTemplates[id];
  let out;
  try { out = t.compile({}); }
  catch (e) { rows.push({id: id, threw: e.message.slice(0, 70)}); return; }
  const found = {};
  ['mail', 'portal', 'short'].forEach(k => {
    const b = String((out && out[k]) || '').match(/\[[^\]]{2,60}\]/g);
    if (b) found[k] = [...new Set(b)];
  });
  if (Object.keys(found).length) rows.push({id: id, found: found});
});

console.log('\n  ' + ids.length + ' templates; ' + rows.length +
            ' carry a bracket when handed an empty context\n');
rows.forEach(r => {
  console.log('  ' + r.id);
  if (r.threw) { console.log('      threw: ' + r.threw); return; }
  Object.keys(r.found).forEach(k => {
    console.log('      .' + k + ': ' + r.found[k].map(s => s.length > 46 ? s.slice(0, 44) + '…]' : s).join('  '));
  });
});
console.log('\n  Reachability is the question, not presence. A letter only\n' +
            '  reaches a packet once its data exists — so these matter where a\n' +
            '  REPORT can be missing the field, and matter much less where the\n' +
            '  person types it in themselves.\n');
