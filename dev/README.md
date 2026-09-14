# dev — harnesses and splice scripts

These live in the repo on purpose. An earlier set lived in `/tmp/mgc-diag`
and was destroyed when the Mac restarted: twelve harnesses, every splice
script, and the anonymised report fixtures, all gone in one reboot. Nothing
that guards this product belongs in a temp directory again.

## Running

    node dev/consistent.js

Every harness reads `index.html` from the project root unless `MGC_INDEX`
points elsewhere. They evaluate the page's own script blocks in Node against
a stub DOM, so they test the shipped code rather than a copy of it.

## Fixtures

`dev/fixtures/` is gitignored and must stay that way — real client credit
reports go in it and must never reach a commit, a screenshot, or a served
directory. Harnesses that need one take `MGC_REPORT`; harnesses that can
build their own synthetic `parsed` object do that instead and need no
fixture at all. Prefer the second kind.

`consistent.js` is the model: it constructs accounts directly, including
`per_bureau_fields`, which is what the contradiction detector actually
reads. An early draft of it omitted that field, found zero contradictions,
and passed against a broken build — a fixture that triggers nothing tests
nothing.

## What each one is for

| File | Guards |
|---|---|
| `consistent.js` | The packet never says one thing and does another — no "nothing to dispute" on a cover page above letters that dispute things. Also the plan counter's failure handling. |

## Harnesses to rebuild

Lost with `/tmp` and worth restoring when a report fixture is available
again: `mailable.js` (no brackets, no placeholders, every letter addressed),
`croa.js` (no promise language, free resources present, nothing captured),
`r2test.js` (round two prints round two), `intake.js` (no claim the person
did not make), `breach.js` (breach data and the misuse gate), `unique.js`
(distinct letters per person), `original.js` (no fragment matches a public
template), plus `regress.js`, `lawtest.js`, `angles.js`, `resolved.js`,
`optout.js`, `aptest.js`, `check1.js` and the three browser harnesses.

`croa.js` and `original.js` need no client data and should be rebuilt first.
