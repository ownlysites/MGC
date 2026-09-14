// Turn the client PDFs into the text fixtures the harnesses read.
//
// This uses the SAME pdf.js version and the SAME line-reconstruction algorithm
// as extractTextFromPDF in index.html. That is not a detail. Extracting with
// pypdf instead produced text where "Account info" never sat alone on a line,
// the Experian printable parser found zero accounts, three of Dave's reports
// fell through to the low-confidence heuristic, and it looked exactly like a
// parser bug. It was not — it was the fixture. A fixture extracted differently
// from the way the product extracts is a document the product will never see.
//
//   cd dev && npm install       (once)
//   node extract.cjs            (regenerates dev/fixtures/)
//
// The PDFs stay where they are. Nothing here copies them, and dev/fixtures/ is
// gitignored, so no client report can reach a commit or a served directory.

const fs = require('fs');
const path = require('path');
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf.js');

const SRC = process.env.MGC_PDF_DIR ||
  path.join(process.env.HOME, 'Downloads', 'Funding Clients');
const OUT = path.join(__dirname, 'fixtures');

// name -> path relative to SRC
const JOBS = {
  'michelle.txt':      'Michelle Ivery/Michelle Ivery Credit Report.pdf',
  'smartcredit3.txt':  'Mike Gibson/M Gibson SmartCredit 3.pdf',
  'mg_experian.txt':   'Mike Gibson/MG-Experian.pdf',
  'mg_equifax.txt':    'Mike Gibson/MiG-Equifax.pdf',
  'mg_transunion.txt': 'Mike Gibson/TransunionMG.pdf',
  'jose_santiago.txt': 'Gio/jose_santiago.pdf',
  'gibson_james.txt':  '2026-09-09-james-gibson.pdf'
};

async function extract(file) {
  const data = new Uint8Array(fs.readFileSync(file));
  const pdf = await pdfjsLib.getDocument({ data, useSystemFonts: true }).promise;
  let text = '';
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const lines = []; let line = ''; let lastY = null;
    for (const item of content.items) {
      if (typeof item.str !== 'string') continue;
      const y = (item.transform && item.transform.length > 5) ? item.transform[5] : null;
      if (line && lastY !== null && y !== null && Math.abs(y - lastY) > 2) {
        lines.push(line.trim()); line = '';
      }
      if (line && !line.endsWith(' ') && !item.str.startsWith(' ')) line += ' ';
      line += item.str;
      if (item.hasEOL) { lines.push(line.trim()); line = ''; lastY = null; }
      else if (y !== null) { lastY = y; }
    }
    if (line.trim()) lines.push(line.trim());
    text += lines.filter(l => l.length > 0).join('\n') + '\n';
  }
  return text;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  let made = 0, missing = 0;
  for (const [out, rel] of Object.entries(JOBS)) {
    const p = path.join(SRC, rel);
    if (!fs.existsSync(p)) { console.log(out.padEnd(20) + 'SOURCE NOT FOUND  ' + rel); missing++; continue; }
    try {
      const t = await extract(p);
      fs.writeFileSync(path.join(OUT, out), t);
      console.log(out.padEnd(20) + String(t.length).padStart(7) + ' chars');
      made++;
    } catch (e) { console.log(out.padEnd(20) + 'FAILED  ' + e.message); missing++; }
  }
  console.log('\n' + made + ' fixture(s) written to dev/fixtures/' + (missing ? ', ' + missing + ' missing' : ''));
})();
