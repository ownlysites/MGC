# dev — harnesses, fixtures and splice scripts

These live in the repo on purpose. An earlier set lived in `/tmp/mgc-diag` and
was destroyed when the Mac restarted: twelve harnesses, every splice script and
the report fixtures, gone in one reboot. Nothing that guards this product goes
in a temp directory again.

## Running

    sh dev/all.sh          # everything, exits non-zero on any failure
    node dev/parsers.js    # or one at a time

Each harness evaluates the page's own `<script>` blocks in Node against a stub
DOM (`harness.js`), so it tests the shipped file rather than a copy of it.
`MGC_INDEX` overrides which file.

## Fixtures — client data, never committed

    cd dev && npm install && node extract.cjs

That reads the client PDFs from `~/Downloads/Funding Clients` (override with
`MGC_PDF_DIR`) and writes text into `dev/fixtures/`, which is **gitignored and
must stay that way**. Real credit reports must never reach a commit, a
screenshot or a served directory.

`extract.cjs` deliberately uses the same pdf.js version and the same
line-reconstruction algorithm as `extractTextFromPDF` in `index.html`. This is
not a detail. Extracting with pypdf instead produced text where `Account info`
never sat alone on a line, the Experian printable parser found zero accounts,
three of the reports fell through to the low-confidence heuristic, and it looked
exactly like a parser regression. It was the fixture. **A fixture extracted
differently from the way the product extracts is a document the product will
never see.**

| Fixture | Format | Notable |
|---|---|---|
| `michelle.txt` | columnar_tri_merge | the format most clients arrive with |
| `smartcredit3.txt` | columnar_tri_merge | a collection carrying a late grid |
| `mg_experian.txt` | experian_printable | single bureau |
| `mg_equifax.txt` | experian_printable | single bureau, names truncated at 20 chars |
| `mg_transunion.txt` | experian_printable | single bureau |
| `jose_santiago.txt` | three_bureau | the only one with a public record |
| `gibson_james.txt` | generic_heuristic | a 3-page extract, low confidence by design |

## What each harness guards

| File | Guards |
|---|---|
| `compliance.js` | CROA: no promise of a score or a removal, no upgrade gate, the offer says the packet works without it, the advance-fee rule and 3-day cancellation are stated, every free route carries its current address, nothing is captured from the visitor. Plus originality — no fragment shares seven consecutive words with the FTC's sample letters — and the breach data's provenance and SSN fields. No fixtures needed. |
| `consistent.js` | The packet never says one thing and does another: no "nothing to dispute" on a cover page above letters that dispute things. Also the plan counter's failure handling. Builds its own synthetic reports; no fixtures needed. |
| `parsers.js` | Every real report lands on the parser that claims it and yields what it actually contains. This is the one that would have caught the extraction problem above. |
| `mailable.js` | Every letter in every packet is ready to sign and post: no brackets, no instructions to the consumer, no unfilled blanks, every fan-out copy addressed to a real company. 14 scenarios, ~130 templates, ~440 copies. |

### The one deliberate exception

`scra_default_protection` is allowed to carry ruled blanks. It is a motion to a
court, not a letter to a company — the court's name, the case number and the
servicemember's defences are on the papers they were served with, and nothing
here can know them. The exemption is only defensible because the separator sheet
says so in terms, and `mailable.js` asserts that separately so the exemption
cannot become a hiding place.

## Harnesses still to rebuild

Lost with `/tmp` and worth restoring: `r2test.js` (round two prints round two,
not round one again), `intake.js` (no letter states a claim the person never
made), `breach.js` (the exposure-versus-misuse gate on § 605B), `unique.js`
(distinct letters per person), plus `regress.js`, `lawtest.js`, `angles.js`,
`resolved.js`, `optout.js`, `aptest.js`, `check1.js` and the three browser
harnesses (`design.js`, `layout.js`, `layout2.js`).

The behaviours those guarded are all shipped and were verified when they landed;
what is missing is the standing gate against regression.

## Writing a new one

Copy the shape of `parsers.js`. Two rules learned the hard way:

- **Assert on the claim, not the word.** A gate that banned "guarantee" flagged
  "what the Fair Credit Reporting Act guarantees is one free report" — a
  statutory guarantee, the opposite of a promise by us. A check that fires on
  the negation of itself trains you to ignore it.
- **Make the fixture trigger the thing.** The first draft of `consistent.js`
  omitted `per_bureau_fields`, found zero contradictions, and passed against a
  build that was broken. A fixture that triggers nothing tests nothing.
