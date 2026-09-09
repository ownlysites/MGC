# MGC — Making Good Choices — Session Handoff

**Written:** 2026-08-26. **Refreshed:** 2026-09-08 — current as of commit `4bf7e0f`.

> **Read § 7a and § 6g before touching the parsers or the letters.** The 2026-09-08 session found that three of four recent client reports were not being read structurally at all, and that every letter naming a specific item was being built without the consumer confirming anything. Both are fixed; the traps that caused them are recorded there. Everything below was verified live against the Vercel API, the GitHub repo, the deployed page, or the code itself. Nothing is guessed. Items that could not be verified are marked **UNVERIFIED**.

Supplements the existing `VERCEL_PROJECTS_HANDOFF.md` — that document covers the whole team; this one covers the MGC project and the working setup that was actually used.

---

## 1. What the site is

A self-guided credit-rights tool. Single-file HTML, ~814 KB / 11,218 lines (≈230 KB over the wire, Vercel serves it brotli-compressed), everything runs client-side. No backend, no `fetch()`, no `localStorage`, no analytics. The consumer's credit report never leaves their browser.

Live: **https://mgc-orpin.vercel.app/**

Flow: intake questions → upload a credit report PDF (optional) → analysis → letter packet + phased action plan → answer a short details prompt → download the whole thing as one branded PDF (the "MGC Action Plan"). A consumer who has already mailed letters can come back and use the **round two** path instead (§ 6c).

An overview video sits under the logo on the landing page. It is the only asset in the repo other than `index.html`.

Positioning, which matters for every copy decision: **information-only, self-service, explicitly not a credit repair organization.** The consumer keeps their report and mails their own letters. Do not add anything that reads as doing the work on their behalf.

---

## 2. Where everything lives

| Thing | Location |
|---|---|
| Vercel project | `mgc` — `prj_3nB7tIpma6JlZL4J38NX3GMvr3t1` |
| Vercel team | David Ivery's projects — `team_lRKkCWFxHlHGmGVMjxyU6KSB`, slug `david-iverys-projects`, plan hobby |
| GitHub repo | `ownlysites/MGC` (public), branch `main` |
| Live alias | `mgc-orpin.vercel.app` (also `mgc-david-iverys-projects.vercel.app`, `mgc-git-main-…`) |
| Local working copy | `~/Documents/Claude/Projects/MGC/index.html` |
| Overview video | `Credit_Report_Blueprint.mp4` — in the repo root, served at `/Credit_Report_Blueprint.mp4` |

The local folder is **Vercel-linked but is not a git clone**. It contains `.vercel/` and `.env.local` (holds a `VERCEL_OIDC_TOKEN`; already gitignored — never commit it).

The git clone used across these sessions is at `/tmp/mgc-sync/MGC`. **That is temporary and will be gone after a reboot.** A new session should check for it and re-clone if missing — do not assume it exists.

The repo holds exactly two tracked files: `index.html` and `Credit_Report_Blueprint.mp4` (20,520,835 bytes). There is no build step, no framework, no `package.json`.

---

## 3. How to deploy — the pattern that actually worked

Both credentials already exist on the Mac. Neither needed to be entered.

- **GitHub:** no `gh` CLI, no SSH key. `git push` over HTTPS authenticates through the macOS keychain credential (`username=oauth2`). Verified working — nine pushes this session.
- **Vercel:** no global `vercel` binary on PATH, but the CLI auth token is at `~/Library/Application Support/com.vercel.cli/auth.json`, so `npx --yes vercel@latest …` runs authenticated.

**Preferred deploy — push to GitHub, let the git integration build:**

```bash
cd /tmp/mgc-sync && git clone https://github.com/ownlysites/MGC.git && cd MGC
cp ~/Documents/Claude/Projects/MGC/index.html index.html
git config user.name "ownlysites"
git config user.email "admin@ownly1nce.com"
git add index.html && git commit -F <message-file>
git push origin main
```

Keeps repo and live in sync. Build takes roughly 40–60 seconds.

**Direct CLI deploy** (used once, works, but creates a non-git deployment that leaves the repo behind — avoid unless the repo is deliberately being bypassed):

```bash
cd ~/Documents/Claude/Projects/MGC
npx --yes vercel@latest deploy --prod --yes
```

**Always verify after deploying.** The live page, the repo copy, and the local copy should hash identically:

```bash
curl -s -o /tmp/live.html "https://mgc-orpin.vercel.app/?cb=$RANDOM"
shasum -a 256 /tmp/live.html ~/Documents/Claude/Projects/MGC/index.html
```

As of this refresh all three are `a3927fd6…2df3` (MD5 `110ddf4c9829902cc767e15115eb3991`), 764,157 bytes / 10,136 lines, commit `0b9ac84`.

**Faster path, used on 2026-08-28:** Desktop Commander runs commands directly on the Mac, so the copy-commit-push is a single call against the existing clone rather than a fresh clone each time:

```bash
cp ~/Documents/Claude/Projects/MGC/index.html /tmp/mgc-sync/MGC/index.html
cd /tmp/mgc-sync/MGC && md5 index.html && git add index.html && git commit -q -m "…" && git push -q origin main
```

A cloud container cannot reach `mgc-orpin.vercel.app` from a *browser* context (the egress proxy resets the connection), though `curl` works. To exercise the live page in a real browser, drive Chrome on the Mac — `Claude_Browser__preview_start` + `javascript_tool` worked; `Control_Chrome__execute_javascript` kept executing against an `about:blank` tab and ignoring `tab_id`.

Note: the project's deployment-protection setting reads `ssoProtection: enabled / all_except_custom_domains`, but the `.vercel.app` production alias is **publicly reachable** — confirmed by unauthenticated fetch. No action needed.

---

## 4. Commits — full history since the site was handed over

Base was `c9703b4` (2026-04-24, "Add files via upload"). Everything below is work from the 2026-08-26 to 2026-08-28 sessions, oldest first.

| Commit | What |
|---|---|
| `46ae541` | Fix PDF upload — `state.upload` never initialized, plus text extraction and account parsing |
| `5930c4a` | Parse tri-merge reports structurally instead of by heuristic |
| `1c8b89a` | Parse inquiries, collections and public records; PDF-only upload; report signup links |
| `a16e265` | Add IdentityIQ as the third report option |
| `99fc4b0` | Remove inline affiliate disclosure |
| `b93dd6e` | Fastest-path inquiry handling |
| `6a2f314` | Letter voice, consumer's own statement, state medical debt laws, CFPB gate fix |
| `4acfeab` | Star every state the tool has law for |
| `5ceccef` | Address disputes to the bureaus holding the data, not the brand that sold the report |
| `3692750` | Parse single-bureau reports; upload one, two or three at once |
| `cdf83d3` | Booking option for people who want a human |
| `6bd06c4` | MGC Action Plan document; live-help CTA routed to the booking link |
| `4691160` | Make the Action Plan an actual prepared packet, and wire every print path to it |
| `a596c59` | Letter pages carry nothing but the letter |
| `de75833` | Cover led by the logo, branded back cover, and two fixes found on the way |
| `4120882` | Separator sheet before every letter |
| `6a5417f` | Replace the generated document reference with the prepared date |
| `d8767cc` | Add the overview video to the landing page, under the logo |
| `aff59db` | Drop the hero dedication line |
| `1ff0a84` | Ask for name and address before building the Action Plan |
| `c89a62c` | Drop the empty poster attribute on the hero video |
| `c07e68b` | Read the identity section; judge authorized-user accounts before disputing an address |
| `b6fa9dc` | Read the tri-column money and status rows; rank what to do first |
| `9958f6e` | Work out when every negative item comes off; read the score's own reason codes |
| `a343ce9` | Say what each report format reveals; work out the age of the file |
| `715878d` | Work out how many collections are actually the same debt |
| `31f57aa` | Date the public records; cross the statute of limitations against the debts |
| `c7f2b4e` | Carry the law for all fifty states and DC, not ten |
| `d389553` | Handle round two, and fix what a fresh report exposed |
| `0b9ac84` | Stop the page sliding sideways on a phone |

Commit messages are long and explain *why*. Keep that convention — they are the real record of what each parser quirk was.

---

## 5. Code map

Single file, 10,136 lines. Line numbers are as of `0b9ac84` — they drift with every edit, so search by name.

**Upload and parsing**

| Line | Symbol |
|---|---|
| 3033 | `mergeParsedReports` — merges separately-uploaded bureau reports |
| 3237 | `classifyDocument` |
| 3272 / 3450 | `tbIsThreeBureauReport` / `parseThreeBureauReport` — tri-merge |
| 3305 / 3321 | `tbDateTripleLatest` / `tbMoneyTriple` — tri-column dates and money |
| 3387 / 3401 | `tbStatusTripleFromBlock` / `tbSplitTriple` — tri-column status |
| 3708 | `tbParseAddresses` — the consumer's own addresses, mapped to bureaus |
| 3786 / 3841 | tri-merge inquiries / collections |
| 3930 / 4098 | `isExperianPrintable` / `parseExperianPrintable` — single-bureau |
| 4003–4078 | `expParseGrid`, `expDeriveDofd`, `expLateMarks`, `expFallOff` — the payment grid and the seven-year clock |
| 4417 | `parseCreditReport` — dispatcher, then generic fallback heuristics |

**Data tables**

| Line | Symbol |
|---|---|
| 2126 | `intakeQuestions` |
| 2287 | `stateLaws` — **all 50 states plus DC** |
| 2805 | `bureauAddresses` |
| 4765 | `letterTemplates` — 25 letters |
| 5103 | `medicalDebtStates` |
| 5156 | `voiceFragments` |

**Analysis**

| Line | Symbol |
|---|---|
| 5198 / 5205 | `enclosureLine` / `mailEnvelope` — every mailed letter passes through here |
| 6555 | `computeFlags` |
| 6661 | `buildPriorityActions` — the top three, ranked by leverage |
| 6977 | `findContradictions` — cross-bureau disagreement |
| 7054 | `analyzeSol` — statute of limitations crossed against the debts |
| 7182 | `analyzePublicRecords` |
| 7235 | `groupCollections` — how many entries are actually one debt |
| 7267 | `analyzeFileAge` |
| 7337 | `analyzeUtilization` |
| 7522 | `analyzeAuthorizedUsers` |
| 7533 | `analyzeReport` — the orchestrator; findings are pushed in display order |
| 8294 | `determineLetterPacket` |
| 8399 | `buildActionPlan` |

**Render**

| Line | Symbol |
|---|---|
| 6784 | `renderPrioritySection` |
| 6851 | `renderResponseGuide` — reading the bureau's reply |
| 8530 | `renderUtilizationSection` |
| 8662 | `renderBankruptcyChapterAsk` |
| 8700 | `renderRoundTwoSection` |
| 8752 | `renderIdentitySection` |
| 8857 | `renderAnalysis` |
| 9033 | `renderLetterPacket` |
| 9253 / 9264 | `updateUserInfo` / `regenerateAllLetters` |
| 9283 | `buildLetterContext` |

**Action Plan document**

| Line | Symbol |
|---|---|
| 429 | `@media print` — reshapes the app for printing |
| ~436–760 | the document's own styling, deliberately **outside** `@media print` |
| 9617 | `buildActionPlanDoc` |
| 9991 / 10004 | `downloadActionPlan` / `buildAndPrintPlan` |
| 10051 | `promptPlanDetails` |

**New letters:** `compileMixedFile` (5317), `compilePersonalInfoCorrection` (5400).

External dependencies: Google Fonts and `cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/`. Images are inline base64 (184 KB, 25% of the raw file).

---

## 6. The MGC Action Plan document

The whole packet as one branded document, produced the same way as everything
else here — in the browser. **No PDF library.** A purpose-built print document
plus the browser's own Save as PDF.

How it works: `downloadActionPlan()` checks that the consumer's details are in
hand (section 6a), then `buildAndPrintPlan()` calls `buildActionPlanDoc()`,
which fills a `#action-plan-doc` div appended to `<body>`, adds
`body.printing-plan` and calls `window.print()`. The print stylesheet hides
every direct child of body except that div. The class is cleared on
`afterprint`, with a 60-second timeout fallback because Safari and iOS do not
always fire it.

**Five entry points** all funnel through `downloadActionPlan()`: the analysis
screen, two buttons on the letters screen, the nav button (hidden until an
analysis exists), and a `beforeprint` handler so ⌘P builds the packet instead of
printing the app. `wired_test.py` asserts the count is 5 and that zero raw
`window.print()` buttons remain.

Contents, in order: cover (large logo, prepared-for name, date, bureaus
reviewed, scores, letter count) → index with real page numbers → what we found →
warnings → phased action plan → where to send disputes with bureau addresses →
**for each letter: a separator sheet, then the letter alone on the next page** →
mailing checklist → tracking log → closing page with the booking link and free
resources → a blank branded back cover, so the packet can be printed as a
booklet and mailed. Cover and closing both carry the information-only,
self-service statement.

Print-craft details that are deliberate, not decoration:

- The document's styling lives **outside** `@media print` (line ~436). Only the
  rules that reshape the app for printing stay inside it. This is what lets the
  same rules apply during off-screen measurement.
- The logo is read from the nav `<img>` already in the page. Do **not** embed a
  second copy — the JPEG is ~70 KB and is already in the file twice.
- That JPEG sits on a `254,254,254` ground, which reads as a faint grey box on a
  pure-white page. It is composited with `mix-blend-mode: multiply`; a browser
  that ignores the property just falls back to the box.
- The cover logo needs `width: 100%` and **nothing else setting width.** A
  leftover `width: auto` won on specificity order once and rendered the logo at
  its intrinsic 1254 px, spilling the cover across three pages.
- Letter bodies use a **left rule**, not a border box. A bordered rectangle
  splits into half-rectangles across page breaks.
- **Running footers were tried twice and abandoned.** `position: fixed` does not
  reserve space and negative offsets wrap to the top of the page;
  `display: table-footer-group` rendered once at the very end. The date rides in
  `planHead` instead.
- **Page-number estimation was abandoned.** Off-screen measurement did not track
  real pagination (a 1580 px letter took one page, a 1536 px letter took two).
  The index carries real page numbers now because the separator sheets make the
  pagination deterministic — each letter starts on a known page.

**Letter pages carry nothing but the letter.** No headers, no borders, no
reference numbers, no notes — anything printed there would go in an envelope to
a bureau. All the guidance lives on the separator sheet in front of it, which
says *"Do not mail this page — remove it before sending."*

Note for testing: the browser's Save-as-PDF has a **Background graphics**
checkbox, usually off by default. The design does not depend on it.

---

## 6a. The details prompt — added `1ff0a84`

**The bug it fixes:** the personalization form (`#ui-name`, `#ui-address`,
`#ui-city`, `#ui-dob`, `#ui-ssn`) lives on the letters screen — step 4 — but the
plan is buildable from the analysis screen and the nav button. A consumer could
therefore print a whole packet whose every letter still said
`[YOUR FULL NAME]`. Letters with placeholders in them are not worth printing.

`downloadActionPlan()` now gates on `planDetailsComplete()` — name **and**
street address **and** city/state/ZIP. Missing any of them opens
`promptPlanDetails()`: five fields prefilled from `state.userInfo`, an inline
error on `#pd-error`, and a pink card that says, in these words, **"None of this
leaves your computer."** — no account, no server, nothing saved, close the tab
and it is gone — plus the reminder never to put a full SSN in a letter. Two
buttons: *Use these details →* validates and builds; *Print blanks — I'll fill
them in by hand* builds anyway. Asked once; after that the plan builds straight
through.

Three things that had to be fixed to make it hold, all easy to reintroduce:

1. The modal CSS is `.modal-backdrop.active`. The pre-existing `closeModal()`
   used `.show`, which had never surfaced because nothing had ever opened the
   modal. **Use `active`.**
2. `renderLetterPacket()` used to run `state.userInfo = {}` on every render.
   Visiting the letters screen after answering the prompt wiped the details and
   pushed placeholders back into all eight letters. It now preserves what is
   there.
3. The `ui-*` inputs had no `value` attributes, so a re-render blanked them and
   the next `updateUserInfo()` wrote the blanks back over the letters. They
   prefill from `state.userInfo` now, and `applyPlanDetails()` syncs them
   directly as well. Both halves are needed.

---

## 6b. The landing-page video

`Credit_Report_Blueprint.mp4`, in the repo root, served at
`/Credit_Report_Blueprint.mp4`. Verified 2026-08-28 on the live site in Chrome
on the Mac: `readyState` 4, duration 434.05 s (7:14), 1280×720, no media error.

Facts worth keeping:

- H.264 High profile, level 3.1, yuv420p, 24 fps + AAC-LC mono 44.1 kHz.
  Universally playable; do not re-encode without a reason.
- **`moov` is at byte 24, before `mdat`** — the file is already faststart, so it
  streams and seeks without downloading 20 MB first. Any replacement must keep
  that (`ffmpeg -movflags +faststart`).
- Vercel serves it with `accept-ranges: bytes` and answers a range request with
  `206`. Seeking works.
- `preload="metadata"` is deliberate — a 20 MB file must not be pulled on every
  page load.
- The element carries **no `poster` attribute**. It had `poster=""`, which
  resolves against the document URL and can make a browser fetch the page itself
  as an image. Removed in `c89a62c`. Leave it absent unless a real poster frame
  is added.
- The wrapper is `class="hero-video no-print"` — it must never appear in a
  printed Action Plan.
- **Playwright's bundled Chromium cannot decode H.264** (no proprietary codecs).
  It aborts the request and reports `readyState 0` with a null error. That is a
  false negative — verify video in Chrome on the Mac, not in the container.

---

## 6c. Round two — added `d389553`

The tool used to handle day one and stop. A dispute is a campaign: you mail, you wait thirty days, an answer comes back, and what you do next depends entirely on **which** answer it was. Someone returning on day thirty-five got the same first-round plan again — worse than useless, because resending an identical dispute with nothing new is the frivolous resubmission 12 CFR § 1022.43 lets a furnisher refuse.

`DISPUTE_OUTCOMES` (near `renderRoundTwoSection`, 8700) maps seven outcomes to a next letter and an explanation. `roundTwoTargets()` builds the list of things they plausibly disputed — derogatory accounts, collections and contradictions — keyed by creditor name so an answer survives a re-upload, since nothing is stored between visits.

**One routing decision is deliberate and must not be "fixed":** a no-response does **not** trigger a CFPB complaint. Silence at day thirty is not a resolved dispute and is inside the 45 days, which is exactly the premature filing the CFPB discontinues. It routes to a deletion demand under § 611(a)(1)(A) and tells them to wait out the 45 days. The existing `cfpb_gate_open` flag (in `computeFlags`, 6555) still decides the CFPB letter.

`renderResponseGuide` (6851) sits alongside it because bureau replies are written to be skimmed past. The pair that matters: **"verified" and "unable to verify your identity" read almost identically** to someone seeing one for the first time and mean opposite things — one says they investigated and disagreed, the other says nobody ever looked and thirty days were lost to an address mismatch.

---

## 6d. The analysis engine — what it computes and why

Added across `c07e68b` … `c7f2b4e`. Findings are pushed in display order inside `analyzeReport`.

- **Cross-bureau contradictions** (`findContradictions`, 6977) — the strongest dispute on any report and only visible on a tri-merge. An ordinary dispute is the consumer's word against the furnisher's; a contradiction is on the face of the report, so at least one entry is wrong by arithmetic. Detection is deliberately conservative because it ends in a letter: "Closed" is a state, not a payment claim, so Closed-versus-Late does **not** qualify.
- **The seven-year clock** (`expDeriveDofd` / `expFallOff`, 4045/4078) — the DOFD field is blank on every sample report we have, so the date is derived from the month-by-month payment grid. Items already out of time go to the top of the priority list; items falling off within a year come with a warning not to spend a letter on what the calendar is about to hand over. Also flags re-aging where a stated DOFD is later than the grid's own first delinquency.
- **Utilization** (`analyzeUtilization`, 7337) — per card and per bureau, in dollars, with the statement-closing-date rule. Cards with no reported balance are excluded **and disclosed**, because silently dropping a large limit makes the ratio look worse than it is. No projected point gain is ever printed.
- **Statute of limitations** (`analyzeSol`, 7054) — measured from derived DOFD → stated DOFD → date of last activity. Leads with the distinction people get wrong (the reporting clock and the suing clock are different clocks) and the revival warning. 16 states carry `sol_contested`.
- **Identity review** (`renderIdentitySection`, 8752) and **authorized users** (`analyzeAuthorizedUsers`, 7522) — see § 6e.
- **Collections grouping** (`groupCollections`, 7235) — ten entries on one sample resolve to six actual debts. Needs two agreeing signals and never groups within one bureau.
- **Score factors** — the model's own reason codes. Single-bureau has them under "What's hurting"; tri-merge has them per bureau under "Factors affecting your credit score", **which earlier work wrongly concluded did not exist**.
- **Priority actions** (`buildPriorityActions`, 6661) — three, ranked by leverage rather than severity, at the head of both the analysis and the packet.

---

## 6e. Authorized-user accounts and the identity review

An unfamiliar address is **not** automatically a stranger's data. It may have arrived with an account the consumer is an authorized user on. Disputing the address and splitting the file can take that tradeline with it — and if it is the oldest account with a clean history, that costs more than anything else on the page.

So the AU accounts get judged before anything is disputed: clean/old/limit-carrying → *keep it*; delinquent or maxed → *removing it helps*, and the fast route is the primary holder calling the issuer, not a dispute. Only the single-bureau format carries a `Responsibility` field; tri-merge has none anywhere, so there the consumer is asked rather than told.

The rule stated on screen before anything else: **an old address you really did live at is not an error.** It is history, it belongs there, and disputing it is the form-letter behaviour that gets a dispute dismissed under § 1022.43.

---

## 6f. Mobile — fixed `0b9ac84`, and how to test it

It was broken until 2026-08-29 for anyone who reached an analysis, which is everyone the tool is for. The nav is a flex row that will not shrink below its content; with the wordmark and three buttons it ran 56 px past a 390 px viewport the moment the Action Plan button unhid itself, taking the whole document sideways. The landing page was fine, so nothing showed until someone actually used it.

Now: `min-width: 0` on the flex items; below 640 px the wordmark and the Disclosures button step aside; below 360 px button labels wrap and padding tightens.

**The testing trap that hid it.** `skipToAnalysis()` renders the analysis but does not switch the view, so `#view-flow` stays `display:none` and every geometry measurement comes back zero. Call `showView('flow')` and `showStep('analysis')` before measuring anything, or you will measure the nav and nothing else — which is what happened here first time round. Verified clean at 390 px and 320 px across the analysis, round two and the letters screen, with the utilization table scrolling inside its own container.

---

---

## 6g. The item review — the consumer confirms before we accuse (added `4bf7e0f`)

**The bug it fixes, and it was the root of three separate reported failures.**
Three letters name a company and allege something against it: the
permissible-purpose demand (§ 604, no permissible purpose), the inquiry
dispute, and the § 605B block, which is sworn under penalty of perjury. All
three were built from parsed data with nothing asked of the consumer.

- `compileInquiryPermissiblePurpose` used `inquiries[0]` — whichever inquiry
  happened to parse first. It accused a company of an FCRA violation for
  sorting first in a list.
- `compileInquiryDispute` listed every parsed inquiry under "I did not apply
  for credit with any of these companies." On a report with fourteen
  inquiries, most of which the consumer did authorise, that is a false
  statement in a mailed legal letter.
- `compile605B` received the generic `disputableItems` list — every derogatory
  account on the file — as the items to swear were fraudulent.

`renderItemReview()` now sits on the analysis screen directly under the
priorities. One item per row, one question, three buttons, **nothing
pre-selected**. Inquiries: *I applied here / I never applied here / I'm not
sure*. Accounts: *This is mine / Mine — but some charges aren't / I never
opened this*. Answers live in `state.itemReview`.

What flows from it:

- `unauthorizedInquiries()` feeds `ctx.inquiries`. With nothing flagged,
  **neither inquiry letter is built at all**.
- `reviewedAccounts('never')` feeds `ctx.items` for the § 605B block, and the
  block is not built until something is flagged.
- `reviewedAccounts('charges')` feeds the new FCBA letter (below).

**Do not "restore" the old behaviour of building these from parsed data.** The
suppression is the feature.

### The FCBA billing-error letter

An account that genuinely belongs to the consumer but carries transactions
they did not make is **not** a § 605B case. Blocking it asks the bureau to
delete a tradeline that is theirs, under a sworn affidavit, and if it is an
old clean account that costs them more than the charges do.

`compileFcbaBillingError` runs to the **creditor**, not the bureau, under the
Fair Credit Billing Act, 15 U.S.C. § 1666, and it is on a clock the FCRA does
not have: written notice must reach the creditor **within 60 days of the first
statement showing the error**. It also invokes § 1666(d) (no closing the
account over a dispute), § 1666a (no reporting the disputed amount as
delinquent without noting the dispute) and FCRA § 623(a)(3).

### Identity theft ordering and the FTC number

- Confirmed identity theft used to put the § 605B block **ninth** in the
  packet, behind eight generic letters. It now leads, after the fraud alert.
- `buildLetterContext` hardcoded `ctx.ftcReportNumber` to the placeholder and
  never read `state.ftcReportNumber`. The walkthrough input writes that field
  and calls `regenerateAllLetters()`, so typing the number **actively erased
  it**. It is the one field the four-business-day block depends on.
- **A police report is not required for the block and never was.** The FTC
  Identity Theft Report is the identity theft report; § 605B(a) does not
  condition the block on a police report. Step 2 of the walkthrough now says
  so, names the only three situations where one is worth getting (a furnisher
  demands it, a named suspect, a large or ongoing loss), and asks
  `state.policeReportFiled`. The § 605B enclosure list follows the answer
  instead of the old catch-all "Any police report, if filed."

### Letter dating

`userHeader()` stamped `new Date()` on every letter in the packet, including
the ones mailed thirty and sixty days later. `DAY_ONE_LETTERS` now holds the
letters that genuinely go out immediately; everything else gets
`Date: ______________________`. A second-round dispute carrying the same date
as the first reads as a batch mailing from a form mill — the § 1022.43
frivolous-resubmission trigger the fragment randomisation exists to avoid.
The compile sites set `state._letterBeingCompiled` so `letterDateLine()` knows
which letter it is writing.

### The low-confidence guard

A document neither structured parser claims now comes back with
`format: 'generic_heuristic'` and `low_confidence: true`. The upload screen
says we could not read the format and names the two we read completely, and
`determineLetterPacket` builds **no letter that names a specific item**. See
§ 7a for what the heuristics actually produced before this existed.

---

## 7a. The columnar tri-merge — a third layout (added `4bf7e0f`)

Three of the four most recent client reports were **not recognised by either
structured parser** and fell through to the generic heuristics.
`tbIsThreeBureauReport` requires the literal string `Three Bureau Credit
Report`; the 117-page report contains it 116 times and these files do not
contain it once.

What the heuristics produced from them, measured through the app's own
dispatcher:

| | `M Gibson 3B` | `Michelle Ivery` | `SmartCredit 3` |
|---|---|---|---|
| Bureaus | Equifax only | Equifax only | Equifax only |
| Accounts | 28 | 30 | 29 |
| Inquiries | 0 (report says 14) | 0 | 0 |
| Collections | 0 | 0 | 0 |

All three are tri-merges. The "accounts" included
`"MICHELLE LYNN IVERY MICHELLE IVERY MICHELLE L IVERY"`,
`"PORT CHARLOTTE, FL 33952"`, `"GREEN FAIRWAYS WEALTH MANAGEME"`,
`"TOTAL CREDIT USED TOTAL AVAILABLE CREDIT OVERALL UTILIZATION"` and
`"THERE ARE THINGS ON MY CREDIT"` — the consumer's name, home address,
employer, a summary table header, and their own consumer statement chopped
mid-word. A dispute built from that asks Equifax to delete the client's own
address.

`ctIsColumnarTriMerge` / `parseColumnarTriMerge` read this layout. Detection is
**structural, not by brand** — these exports carry no vendor string anywhere in
their text. It keys on a bare `TransUnion Experian Equifax` column-header line,
a `Creditor Contacts` section and a bare `Inquiries` heading, and explicitly
excludes anything carrying `Three Bureau Credit Report`.

Layout notes worth keeping:

- **Inquiries are three-line records**: a date-only line, the creditor, then
  `<Bureau> ®`. The section also carries stray tri-column rows from a tradeline
  that wrapped into it, so the date line must be a date and nothing else —
  `07/07/2026 —— ——` is a tradeline row, not an inquiry.
- **Mailing addresses live in a separate `Creditor Contacts` section**, not
  beside the inquiry. They are matched back by normalised name, conservatively:
  a six-character shared prefix or the whole shorter name inside the longer.
  Heavily abbreviated names (`HCA`, `CAP1`, `HMF`) deliberately return nothing
  rather than guess — a wrong address means a legal demand posted to a company
  that never pulled the report.
- **This vendor pre-sorts inquiries** into "have matching accounts on your
  credit report" and "likely not approved since no matching account shows".
  That second group is carried through as `matched_account: false` and the
  review pass leads with it.

### Three traps, all of which cost real time

1. **Masked account numbers are a BIN prefix, not an identifier.** They are the
   first six digits plus stars, so `444796****` is both `CREDIT ONE BANK NA`
   and `LVNV FUNDING` on the same report, and `546630****` collides on another.
   A creditor lookup keyed on them filed Capital One's balances under Merrick
   Bank. Where the number is ambiguous the block is marked `creditor_uncertain`
   and surfaced to the consumer rather than guessed. **This also undermines the
   rule in § 7 that merges accounts across separately-uploaded bureaus on
   masked account number alone — that deserves a second look.**
2. **The two exports of this same layout are structurally different.** In one,
   each creditor name sits directly above its own bureau header. In the other,
   names and values arrive in separate streams and a block's name can be forty
   lines above it with another account's values in between — adjacency there
   shifts every name by one, silently. They are mutually exclusive on whether a
   roster section (`CREDITOR 123456****`) exists, which is what
   `ctParseAccountsV2` keys on.
3. **Column order is not the analysis's column order.** This report prints
   TransUnion / Experian / Equifax; `findContradictions` and friends read a
   positional array in `TB_BUREAU_COLS` order — Equifax / Experian /
   TransUnion. `ctTriple` re-orders. Passing the report's own order through
   reported every contradiction against the wrong bureau, and the dispute letter
   would then tell Equifax what TransUnion said.

Values are paired against the fixed field list by **shape**, not position: a row
that does not match the shape its label expects advances the label rather than
the row, so one dropped line at a page break cannot shift every field after it.

---

## 7b. The dispute-reason grammar and the second field (added `b630650`)

Three sources Dave sent turn out to be one idea, and it now shapes every disputed
item in the packet.

**The grammar.** The Airtable base "The Perfect Dispute Reason Creator" (Kristin
Vargas / 45daycreditsweep) is a single formula field over four single-selects:

    {OUTCOME} & " this " & {TYPE} & " because the " & {ELEMENT} & " is " & {DEFECT}

Five outcomes, twenty-three elements, nine defects, three types. All four lists
are copied into `DR_OUTCOMES` / `DR_ELEMENTS` / `DR_DEFECTS` / `DR_TYPES` verbatim
and unedited, and **they must stay closed**. `drSentence()` refuses to build a
sentence out of any value not in them, so a new rule that invents an element
produces no lead line rather than a plausible-looking wrong one. If you add a
factual rule, add its `DR_RULE_MAP` entry using an existing element — do not
extend the list to fit.

Why the constraint matters: a free-text reason drifts into argument (why the debt
is unfair, what the collector said), and an argument is what comes back
"verified", because there is nothing in it a clerk can check. A sentence in this
grammar can only name one field and one defect.

Independent confirmation worth knowing about: the base's ELEMENT list matches
`FACT_IMPACT` in this file almost exactly — date last active, date last paid and
notice of dispute at the top, "not mine" absent from the base entirely.

**The second field.** The companion Genially deck's argument is that one bad
tradeline is several disputes, not one repeated. `drAngles()` groups the factual
findings per account and deduplicates them **by element**, ordered by impact.
Round one leads on the first; a second letter must name a different one or it can
be refused as a repeat under 12 CFR § 1022.43.

`renderNextAngle()` shows this in the round-two tracker, and the gating is
deliberate — `DR_ROTATE_ON` covers **verified, corrected and frivolous only**.
Never rotate on `no_response` or `identity`: nobody worked those disputes, so
resending the same reason is correct, and rotating throws away the strongest
argument on the file. When an account has only one field, the panel says so and
sends the person to method of verification rather than inventing a second reason.
That silence is the feature, not a gap in it.

**Round two now tracks what was actually sent.** `roundTwoTargets()` was built
from derogatory findings alone, which left two whole classes of letter
untrackable: accounts disputed on a factual inconsistency and nothing else —
which are the FIRST items in every bureau letter, 14 of them on Michelle's report
— and accounts the consumer flagged themselves in the item review.
Action-plan-protected accounts stay out, matching the letters.

---

## 7c. "I already paid or settled this" (added `9e615b2`)

From the Top 12 Errors deck. Three of the twelve errors McCarthy Law litigates
are **invisible to any parser**: an account paid in full still reporting a
balance, one settled for less still reporting the full one, and a debt discharged
in bankruptcy still reporting as owed. An account paid off last year and still
showing a balance is field-for-field identical to one that was never paid.

I tried to detect them first. Across all five real reports there is not one
account whose status says paid, settled or discharged while carrying a balance,
and the loose status match flagged sixteen ordinary "Pays as Agreed" tradelines on
mi117 — sixteen false accusations in a legal letter. So it is **asked**:
`setAccountAnswer(key,'resolved')` on any row the report claims money is owed on,
then one follow-up (`setResolvedHow`) choosing paid / settled / bk.

Each answer writes a **correction, not a deletion**, which is why this is the one
dispute that runs even on action-plan-protected accounts — a paid account
reporting zero is worth keeping for its age and history. `RESOLVED_LABELS` holds
the sentence, the claim, the demand and the document to bring, per answer.

Statutes, both read verbatim from the U.S. Code this session rather than recalled:

- **§ 623(a)(1)(B)** — a furnisher shall not furnish information if the consumer
  has notified it, at the address it specified for such notices, that specific
  information is inaccurate, and the information is in fact inaccurate.
- **§ 623(a)(2)** — a furnisher that determines what it reported is not complete
  or accurate must promptly notify the CRA, provide the correction, "and shall not
  thereafter furnish to the agency any of the information that remains not
  complete or accurate."

**The trap, which cost time.** The gate was `acc.balance > 0` and it was invisible
on two of the three formats. The columnar parsers put a NUMBER on `acc.balance`;
the old tri-merge puts the string `"$0"` there with the real per-bureau figures in
`per_bureau_balance`; the Experian printable puts `"$432"` or nothing.
`accountBalanceOwed()` reads all three shapes and takes the highest figure across
bureaus — one bureau at zero while another shows a balance is exactly the case
worth asking about. **Any new per-account money check must use it**, not
`acc.balance`.

**Not imported from that deck:** its "10 items not eligible" list. That is a list
of weak LAWSUITS, not weak disputes — importing it as a dispute stop-list would
gut inquiries, personal information and public records, all of which work here.
Its "identity theft without a police report" entry is also wrong for this tool: an
FTC Identity Theft Report stands with or without one, which is settled and is
already how the § 605B letter reads.

---

## 7d. The privacy opt-out letter (added `8e48cdf`)

Rebuilt from the "CREDITOR OPT OUT FORM" in the Dispute Plan folder. Three
rights, each read verbatim from the U.S. Code before it went in the letter:

- **15 U.S.C. § 6802(b)(1)** (GLBA § 502) — a financial institution may not
  disclose nonpublic personal information to a nonaffiliated third party unless
  it disclosed that it may, gave the consumer the opportunity to direct that it
  not be, and explained how. The letter is that direction.
- **§ 1681a(d)(2)(A)(iii)** — communicating "other information" among affiliated
  companies is excluded from the definition of "consumer report" ONLY IF the
  consumer was told and given the chance to say no first. Saying no removes the
  exclusion, so a communication afterwards is the furnishing of a consumer
  report. The letter states that consequence, because it is the leverage.
- **§ 1681s-3(a)(1)** (FCRA § 624) — no affiliate-sourced marketing once
  prohibited; at least five years under (a)(3)(A).

Plus, below the signature and not addressed to the creditor, the **§ 604(e)**
prescreen opt-out: optoutprescreen.com / 1-888-5-OPT-OUT, five years by phone or
web (starting five business days after), permanent only if the signed Permanent
Opt-Out Election form is returned.

**Two claims from the source form are deliberately absent. Do not put them back.**
Demanding that a creditor not share *transaction and experience* information with
its affiliates has no basis — § 1681a(d)(2)(A)(i) and (ii) exclude that outright,
no opt-out attached. And "if I hear nothing in thirty days I will assume you
complied" invents a deadline; the elections take effect on receipt regardless,
which is both true and stronger.

**Prefill.** Open accounts come from the report; addresses from its Creditor
Contacts section through `ctFindAddress`, which returns only a confident match.
The other open accounts are listed as separate sends — never merged into one
letter, because a letter naming two companies tells each about the other's
account, which is the exact information movement it exists to stop. Government
and self-reported tradelines are filtered out: all three rights run against a
private company, and the first draft addressed one to the U.S. Department of
Education.

**Two envelope fixes this exposed.** `mailEnvelope` closed every letter with
"Please confirm in writing what action you have taken" and an enclosure line
listing a photo ID. Both are right for a dispute and wrong for an instruction
that says no response is required and exists to move less personal information.
Pass `closing: false` / `enclosures: false` to suppress either; only this letter
does, and the harness checks every other letter still carries both.

**Timing.** Recipient is `creditor`, which would have scheduled it fourteen days
out with the furnisher disputes. A template can now declare its own
`send_class`; this one is `privacy`, day zero, its own group. Nothing has to
happen before an instruction, and every day it waits is another day the
information is still moving.

---

## 7e. The layout, and the rules it now has (added `565a2e4`)

Ten commits of law and parsing went in before anyone took a screenshot. When one
was finally taken the biggest problem in the product was structural and had been
there since launch.

**Both working screens rendered in `container-narrow` — 560px, centred, at every
viewport.** On a 1280px monitor that is 44% of the screen working and 56% idle,
and it is why everything read as a phone app on a desktop: review buttons
wrapping with 700px free beside them, headings breaking mid-phrase, body copy at
48 characters. They now render into `.workspace`: a sticky section rail from
1080px up and a 768px content column. Below 1080px it collapses to what it was.

`buildSectionRail()` reads the rendered DOM rather than each section builder,
because the sections come from a dozen functions and threading an id through all
of them is a dozen chances to miss one. **If you add a section, give it an `h2`
and it appears in the rail for free.**

### Rules this pass established, which a harness now enforces

`design.js` runs six widths across two screens and fails on any of these:

1. **No side-stripes.** A `border-left` of 3px or more in a different colour
   from the other borders. Six components had one; all six are gone. It is the
   most recognisable machine-generated tic in a UI and it does nothing a full
   border and a tinted ground do not do better.
2. **No gradient text.** `background-clip:text` was on the site's own headline,
   where the middle stop ran about 2:1 on cream.
3. **No emoji as UI.** Severity was 🟢 Low. Emoji cannot be styled, render
   differently per platform, and read aloud as "large green circle".
4. **Prose within 80 characters.** `.workspace-main p` is capped at 72ch; rows,
   tables and buttons keep the full column.
5. **Zero horizontal overflow**, at 375 through 1680.

### Two near-misses worth keeping in mind

The first attempt at the findings CSS anchored on `/* ===== ALERTS ===== */`,
which occurs **twice** — the second is the screen stylesheet, the first is
inside the print stylesheet. The span it selected was 1,200 lines. It was caught
only because a later assertion in the same script failed before anything was
written. **Splice scripts against this file must count occurrences and bound the
span**, not just `index()` the first hit.

And `design.js` first reported a compliant 72ch paragraph as 91ch, because it
assumed a character is half an em. Inter's zero is about 0.63em. It measures the
real glyph now. A harness that is wrong in the safe direction wastes a fix; one
that is wrong the other way ships a bug.

### Screenshots without client data

`anon.py` rewrites a real columnar report into `demo.txt` — creditor names from
a fixed pool, account digits reshuffled, addresses and the personal-information
block replaced — and it parses identically (32 accounts, 29 findings). **Use it
for anything that produces an image.** No client report should ever appear in a
screenshot, a commit, or a served directory.

---

## 7f. Test harnesses in `/tmp/mgc-diag`

Not in the repo — they read `index.html` directly and are driven against real
client reports, which must never be committed. Recreate them if the machine is
wiped. All of them concatenate **every** inline `<script>` block and eval it with
DOM stubs; taking only the largest block silently garbles the parsers, which are
spread across six.

| Harness | What it proves |
|---|---|
| `regress.js` | Parser counts on all four reports, plus the no-flag guarantees: no inquiry letter, no § 605B, no FCBA and no placeholders until the consumer flags something, and no later-phase letter stamped today. |
| `angles.js` | The grammar vocabulary is closed; no account repeats a field; angles ordered by impact; round two never equals round one; no wrap past the last angle; lead sentences reach the bureau letter; every disputed account is trackable. |
| `resolved.js` | The paid/settled/discharged path end to end, including that the button alone writes nothing and that changing the answer clears the letter text. |
| `ap-e2e.js` | Action plan reconciliation, and that no protected account leaks into a letter. |
| `optout.js` | The privacy opt-out letter: gating, all three citations, neither dropped claim, no SSN, the prescreen details, creditor prefill on both formats, the envelope suppressions scoped to that one letter, and its day-zero mailing slot. |
| `layout.js` | Drives the Mac's own Chrome headless (`puppeteer-core`, `/Applications/Google Chrome.app/…`) at 375 / 320 / 414px against a local server: zero horizontal overflow, both new panels inside the viewport, no page errors. **Use this when the browser pane is unavailable** — it is faster and it measures the same thing. |
| `layout2.js` | Same, over the LETTERS screen with the identity-theft packet — where the opt-out letter appears. |
| `design.js` | Six widths across the landing and analysis screens: overflow, the four banned patterns, prose measure, and whether the rail appears at the right breakpoint. **Run this before any commit that touches CSS.** |
| `anon.py` / `demo.txt` | Turns a real report into a screenshot-safe one that parses identically. Use it for anything that produces an image. |
| `extract.js` | Replicates the app's pdf.js text extraction exactly, for reading source PDFs. |

Serving a real report to test means copying it into a temp directory. **Delete
the directory and kill the server afterwards, every time.**

---

## 7. Report formats the parser handles

**Tri-merge** — "Three Bureau Credit Report powered by Equifax". The IdentityIQ / SmartCredit / MyFreeScoreNow layout. Numbered sections (`4. Installment Accounts`), numbered tradelines (`4.1 Conn Credit Corp (CLOSED)`), tri-column `Label EQ EX TU` rows, explicit `You currently have no X on your credit file.` markers.

**Single-bureau** — Experian's printable-report viewer, which serves the **same layout for all three bureaus** at `usa.experian.com/mfe/credit/printable-report/{experian|equifax|transunion}/`. Labelled `Account info` blocks.

**Anything else** — falls through to the original generic heuristics. Weak but functional; leave the fallback alone when changing the structured parsers.

### Parser quirks that cost real debugging time

Do not "simplify" these away:

- Tri-column values are pulled **by shape** (money / date / integer / status vocabulary), not by position. pdf.js collapses column spacing, so positional splitting fails.
- Payment-grid cells include **`150` and `CO`**, not just 30/60/90/120. Missing them undercounts delinquency.
- Equifax puts the derogatory label in **Comments** under a `Status` of `-`. A status-only read misses collections entirely.
- The **last** account block runs to end-of-document unless stopped at the next section heading — otherwise the final tradeline inherits "Collection accounts" as a comment and is flagged a collection.
- `Status updated` must match before `Status`; `Original balance` / `Balance updated` before `Balance`.
- Every page of a single-bureau file is stamped **"Experian"** regardless of whose data it holds. Take the bureau from the URL path, never the branding. This previously caused a TransUnion report to be read as Experian.
- `"powered by X"` is the **reseller**, not the bureau holding the data. `parsed.provider` vs `parsed.bureaus` exist for exactly this reason.
- Collection balances are paired to agencies **only when the counts in a bureau group match exactly.** Page breaks reorder detail blocks; a mispaired balance would go out in a legal letter.
- Accounts merge across separately-uploaded bureaus **only on masked account number.** No fuzzy creditor-name matching — merging two accounts that are not the same would hide a tradeline only one bureau reports.

---

## 8. Verified accuracy

Checked against each report's own summary tables.

| Report | Accounts | Inquiries | Collections | Other |
|---|---|---|---|---|
| Tri-merge, 96pp | 39 ✓ | 17 ✓ (EX 6, TU 11) | 10 ✓ (3/3/4) | 3 bankruptcy ✓ |
| Tri-merge, 17pp | 2 ✓ | 0 ✓ | 0 ✓ | scores 655/647/no-file ✓ |
| Experian single | 33 ✓ | 5 | 1 | score 554 ✓ |
| Equifax single | 32 ✓ | 5 | 1 | score 566 ✓ |
| TransUnion single | 32 ✓ | 4 | 1 | score 618 ✓ |
| All three merged | 51 (23 matched across bureaus) | 14 (5/5/4) | 3 | all three scores ✓ |
| Tri-merge, 117pp (2026-08-29) | 43 ✓ | 12 ✓ (EQ 3, EX 4, TU 5) | 27 ✓ (9/6/12) → 19 distinct debts | 0 public records ✓ |

The 117-page report was run **before** the features it paid for, and it earned its keep: it exposed the inquiry-region bug (zero parsed where the report said twelve), the "3 years 12 months" rounding, the tri-merge score factors we had wrongly concluded did not exist, and the inquiry-obsolescence error in § 11.

**Action Plan document**, built from the 96-page tri-merge with the
personalization form filled through the real input path (typed into the fields,
not set in code): all 8 letters present, **zero empty letter bodies**, the
consumer's name / address / own statement all carried into the letter text,
5 phases, 23 findings, logo renders on the cover, and the print stylesheet
hides the app while showing the document.

**Details prompt** (`gate_test.py`, `blanks_test.py`, 2026-08-28, all passing):
prompt opens instead of printing when details are missing; blank submit shows
the inline error and does not print; filled details produce a packet with the
consumer's name and address in it and **no `[YOUR FULL NAME]` anywhere**; the
"print blanks" path still builds; the letters screen prefills from what the
prompt collected and `updateUserInfo()` no longer clobbers it; a second build
does not re-prompt; no page errors.

**Full regression after that change:** tri-merge (39 accounts / 17 inquiries /
10 collections / 3 bankruptcies), Experian single-bureau, image rejection, all
five print entry points, the ⌘P path. Clean.

---

## 9. Known gaps — disclosed, not fixed

1. **Nobody outside this project has used it.** Everything is verified against parsers, four real reports and Playwright. No letter this tool generated has been mailed and answered, as far as anyone here knows. That is the largest remaining unknown and no amount of code closes it — it needs one real dispute cycle.
2. **Only two report formats are parsed structurally.** Tri-merge and the Experian-style printable. Everything else falls to the generic heuristic, which over-captures (it read an inquiry line as an account in testing). **That very likely includes AnnualCreditReport.com — the free federal option this tool itself recommends.** Unverified either way; a sample was promised for 2026-09-01.
3. **Populated collections / public records in the single-bureau format are UNVERIFIED.** Every sample says "No collection accounts reported". The code records presence rather than inventing an entry shape. Needs one real single-bureau report that has one.
4. **Seven state-law items need verbatim verification** — listed in `MGC_BACKLOG.md`. West Virginia's SOL is the weakest; published summaries genuinely disagree on whether card debt is 5 or 10 years.
5. **Experian delinquency count reads 8; the model says 9.** Both numbers are now shown to the user rather than ours asserted alone. Cause still unfound.
6. **No OCR.** Images are rejected with a clear message. Adding it would feed misread account numbers into legal letters. Deliberate — keep it.
7. **Near-duplicate creditor names stay separate rows** when bureaus mask account numbers differently. Deliberate.
8. **Never audited for accessibility.** No screen-reader, contrast or keyboard-navigation pass. For an audience that includes people in financial distress, some with disabilities, that is a real gap and nobody has looked at it.
9. **The monthly law review runs cloud-only.** It was created without a device binding, so it can research and report but cannot write its findings to `MGC_BACKLOG.md` on the Mac until Dave approves a binding.

---

## 10. Decisions already made — do not re-litigate

- **No affiliate disclosures** anywhere unless Dave explicitly asks. The inline one was removed on request. A separate page-level disclosure block still exists in the disclosures section — Dave was told about it and left it as-is.
- **Existing site copy came out of Dave's own prior research.** Do not reword it on your own initiative. This includes the inquiry finding that states an unauthorized inquiry is "an FCRA violation worth $100–$1,000" — flagged to him as a strong legal claim, and he chose to keep it.
- **Report-signup links, in this order:** MyFreeScoreNow (`app.myfreescorenow.com/enroll/C01C8009`) → SmartCredit (`smartcredit.com/?PID=38321`) → IdentityIQ (`identityiq.com/sc-securepreferred.aspx?offercode=431299Z5`), with AnnualCreditReport.com kept below as the always-free option.
- **Booking link:** `https://ownlyfunds.myfundalytics.com/book`, on the analysis and letter-packet screens. Dave describes himself as a certified credit score consultant who can read a report with someone or connect them with a certified partner.
- **Stars in the state dropdown** mark the union of `stateLaws` and `medicalDebtStates` — 22 states.
- **5YearPlans is gone.** Every link and reference was replaced with the booking link on Dave's instruction — the big "bigger than DIY" CTA card, the inline critical-warning button, and the warning copy. The flag is now `cta: 'see_consult'`. Zero `5YearPlans` references remain in the file. SoloSuit and the "consult an attorney" advice were kept — separate free resources, not the handoff Dave asked to change.
- **The packet document is called the "MGC Action Plan."** Dave named it. Use that name.
- **Nothing on a letter page.** No borders, no reference numbers, no wording that would be sent to a bureau or creditor. Rewriting in the consumer's own words is still highly recommended on the separator sheet, but the letter itself must be print-and-sign ready.
- **The reference number is gone.** The `MGC-YYYYMMDD-NNNNNN` string on the last page was replaced with the prepared date (`6a5417f`). Dave asked what it was and chose to drop it. Do not reintroduce an identifier.
- **No hero dedication line.** The "♡ in loving dedication" line was removed from the hero (`aff59db`) because it already appears in the footer. The logo itself is a dedication — treat it with reverence, but do not repeat the line.
- **All 51 jurisdictions are covered, and the ★ markers are gone from the state dropdown.** They meant "we hold law for this state", which is now everywhere, so they distinguished nothing.
- **Where a credit-card SOL is contested, the stored number is the period a court is most likely to APPLY, not the friendliest reading.** Telling someone a debt is time-barred when it is not is the dangerous error — they ignore a suit they could still lose. The analysis says on screen that it is unsettled.
- **No projected point gain is ever printed.** The models are proprietary and nobody outside them can honestly predict a file. Thresholds are stated as thresholds.
- **Anything the consumer types stays on their machine, and the tool says so.** The details prompt says it in plain words. Never add anything that uploads, stores or transmits what they enter.

---

## 11. Current-law notes used this session

- **CFPB complaint gate.** A credit-reporting complaint is discontinued unless the consumer disputed with the CRA first AND either 45 days have passed **or the dispute is no longer pending**. The tool gates on both triggers. Source: CFPB's own credit-and-consumer-reporting complaint notice.
- **CFPB is targeting tools like this one.** The June 2026 complaint-system overhaul names "credit repair organizations and credit clinics", influencers, and "new technologies (e.g. 'AI tools')" as the abuse it is designed to stop.
- **12 CFR § 1022.43** lets a furnisher treat a direct dispute as frivolous when it was *prepared on the consumer's behalf by, or submitted on a form supplied by, a credit repair organization*. This is why the tool has fragment randomization, voice selection, the consumer's own statement, and an on-screen instruction to rewrite before sending. Keep all four.
- **Inquiries: the FCRA sets NO time limit on reporting one.** § 605 is silent, and the two-year figure everyone repeats is bureau practice — reports do not even state it consistently, one of ours says three years. The tool used to call a two-year-old inquiry "simply out of time" and tell people to dispute on obsolescence; that was wrong and was corrected in `d389553`. It is now framed as a request against the bureaus' own retention practice, demoted in the priority ranking, and the real inquiry claim — a pull without permissible purpose under § 604, with § 1681n damages — is named as the one worth fighting.
- **12 CFR § 1006.26(b): suing or threatening to sue on time-barred debt is strict liability** — the collector's knowledge is irrelevant. Mississippi, North Carolina and Wisconsin extinguish a time-barred debt rather than merely barring the remedy; in Mississippi and Wisconsin a later payment cannot revive it.
- **CFPB medical debt rule was vacated** 2025-07-11 (E.D. Tex.). The bureaus' voluntary NCAP policies still stand. The court's remark that FCRA preempts state medical-debt laws was dicta; the 15 state statutes remain on the books. The tool cites them and warns to expect an argument.

---

## 12. What is NOT carried over

The test harness lived in an ephemeral cloud container and **is gone**: the Playwright scripts, the extracted report text files, and the sample PDFs. A new session that needs to verify parser changes will have to re-extract from PDFs Dave provides.

The six sample reports are Dave's and his family's real credit data — including a 117-page tri-merge for Michelle Ivery added 2026-08-29. They were never committed to the repo, never deployed, and must not be.

Testing approach that worked, if it needs rebuilding: serve the file over `http://localhost`, drive it with Playwright + headless Chromium, point pdf.js at a local copy of `pdf.min.js` / `pdf.worker.min.js` (some sandboxes cannot reach cdnjs from the browser context), feed real PDFs through the actual `#file-input`, and check parsed counts against each report's own summary tables. Watch `pageerror` — several bugs surfaced only there.

Two harness traps that cost time and will cost it again:

- **Playwright calls a function-valued `evaluate` result.** `pg.evaluate("window.print = () => {…}")` returns the function, and Playwright then invokes it — which looked exactly like a spurious print call. End such a snippet with a non-function expression (`…; 1`).
- **`body.printing-plan` stays on** when `window.print` is stubbed, because `afterprint` never fires. Every element on the page then reports as not visible and `page.fill` times out. Remove the class between assertions, or set values through JS and dispatch an `input` event.

Three harness traps, all of which have already cost time here:

- **Playwright calls a function-valued `evaluate` result.** `pg.evaluate("window.print = () => {…}")` returns the function and Playwright then invokes it, which looks exactly like a spurious print. End such a snippet with a non-function expression (`…; 1`).
- **`body.printing-plan` stays on** when `window.print` is stubbed, because `afterprint` never fires. Every element then reports as not visible and `page.fill` times out.
- **`skipToAnalysis()` does not switch the view.** `#view-flow` stays `display:none` and every geometry measurement returns zero. Call `showView('flow')` and `showStep('analysis')` first — this is what hid the mobile bug through a whole session.

The scripts that existed at the end of the 2026-08-29 session — `full_test.py`, `img_test.py`, `wired_test.py`, `gate_test.py`, `blanks_test.py`, `vid_test.py`, `mobile_test.py`, `r2_test.py`, `st_test.py` — are gone with the container.

---

## 13. To pick this up in a new chat

Paste or upload this file, then:

```bash
# the clone at /tmp is temporary — check first, re-clone only if it is gone
ls /tmp/mgc-sync/MGC || { rm -rf /tmp/mgc-sync && mkdir -p /tmp/mgc-sync && cd /tmp/mgc-sync && git clone https://github.com/ownlysites/MGC.git; }

# confirm repo, local copy and live are still in sync
cd /tmp/mgc-sync/MGC && git pull -q && shasum -a 256 index.html ~/Documents/Claude/Projects/MGC/index.html
curl -s -o /tmp/live.html "https://mgc-orpin.vercel.app/?cb=$RANDOM" && shasum -a 256 /tmp/live.html
```

All three should read `a3927fd6c32ba9b4bbdcb068813c89a4d773f191074a852bc381913c97d62df3` at commit `0b9ac84`.

If the three hashes disagree, find out why before editing anything. The live production site is the source of truth.

**Read `MGC_BACKLOG.md` in the same folder before planning anything.** It holds the open work list, what shipped with commit hashes, the gaps being lived with deliberately, the seven state-law items awaiting verbatim verification, and the dated log of monthly law reviews. This handoff explains how the thing works; the backlog says what is left.

Working note: Dave's standing instruction is **do anything you can do so he does not have to.** Deploy, verify and report; do not hand back manual steps he did not ask for. Desktop Commander on the Mac is the fast path for git and for anything that needs a real browser.
