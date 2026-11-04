# Project Scratchpad: Minerva Parent Hub

> Active working notes, loaded into every session, so keep it small.
> Keep only the two most recent session-log entries; roll older ones
> word for word into `docs/SESSION-LOG.md` (create it on the first roll).
>
> See `PARITY.md` for the cross-platform feature matrix (the single
> source of truth; don't duplicate rows here).
>
> New to this template? Start with `docs/path/00-why-we-build.md` and
> `docs/path/01-first-prototype.md` before filling anything in.
>
> The Current State block below is injected at every session start.
> If it drifts behind the code, fix it FIRST, then work. A stale
> scratchpad is worse than none.

## Current state

- **Status**: Owner authorized Pages release 1.0.1; deployment in progress.
- **Active milestone**: M1, parent admissions guide. Stage 00 validation remains open.
- **Last session**: 2026-11-04.
- **Owner's aim**: Help parents, especially of applicants aged 16 or 17,
  participate appropriately in admissions without the applicant account.
- **Owner clarification (2026-11-04)**: Do not suggest Minerva lacks parent
  resources. **Why:** Its Parents & Families page already covers general
  information and links to admissions; the question is participation in
  admissions itself, including the parent's own steps.
- **Evidence**: Owner framing and official public sources; no supplied log,
  critique, named interviewees, conversations, or user testing.
- **Notes**: `docs/STAGE-00.md`, `docs/STAGE-01.md`, and `docs/MINERVA-SOURCES.md`.
- **Next actions**: Owner reviews the why and boundary; completes the log,
  candidate tests, critique and two conversations; revises and posts the
  problem; confirms deadline and parent-role questions with Admissions.
  Publish the reviewed prototype to Pages, then verify the live project URL.
- **Platform scope**: Week 1 web only; later platform choices undecided.
  Native scaffolds stay untouched. The inherited setup checklist below
  is not authorization to build native apps now.
- **Verification**: Official sources rechecked; headless Edge branches, widths, offline and no-JavaScript checked.
  See docs/STAGE-01.md for evidence and the CRLF-only token-check failure.
---

## Milestones

### M0: Project setup

- [ ] Platform set decided + logged in DECISIONS.md
- [ ] AGENTS.md filled in with project identity (app name, what it
      does, tech-stack specifics, design tokens)
- [ ] PARITY.md skeleton sections filled in with intended verbs
- [ ] **Web**: runs locally out of the box
      (`python3 -m http.server 8080`, then http://localhost:8080);
      `index.html`, `css/styles.css`, `js/app.js` render your first
      view; GitHub Pages enabled
- [ ] **Apple (universal)**: the project is generated from
      `project.yml` by the agent, never clicked through Xcode. Rename
      `AppName` and the bundle ids in `project.yml` (no spaces), run
      `xcodegen generate`, then build unsigned for iOS Simulator,
      tvOS Simulator, and macOS and run the Core tests, per
      `apple/README.md`. ONE target, four destinations; sources stay
      in `apple/`; `AppVersion.xcconfig` is already wired
- [ ] **Android**: `cd android && ./gradlew :app:assembleDebug`
      builds out of the box; open `android/` in Android Studio; rename
      the package from `com.example.appname` to your reverse-DNS and
      rebuild; smoke-test on a device or emulator
- [ ] **CI / submission**: `.github/workflows/appstore-build.yml`
      (one workflow covers iOS + macOS + tvOS) with the seven signing
      secrets seeded per `docs/CLOUD-SUBMISSION.md`;
      `.github/workflows/android-build.yml` for CI builds and
      `.github/workflows/play-release.yml` to publish to Play (internal
      track first, then promote)
- [ ] First commit pushed

### M1: [First user-visible capability]

<!-- One sentence: what can a user DO after this milestone? -->

Before implementing, run the `learning-orientation-design` skill:

- [ ] Deepens understanding
- [ ] Invites participation
- [ ] Supports agency
- [ ] Clarity over cleverness

**Acceptance criteria** (observable by users, not developers):

- [ ] Web: …
- [ ] iOS: …
- [ ] macOS: …
- [ ] tvOS: …
- [ ] Android: …

**Parity check**: update PARITY.md row(s) for this capability in
the same change set. Reject the PR if PARITY.md is silent.

### M2: [Second user-visible capability]

- Learning-orientation check passed
- **Acceptance**:
  - [ ] Web: …
  - [ ] iOS: …
  - [ ] macOS: …
  - [ ] tvOS: …
  - [ ] Android: …

---

## When to add a binding design doc

When a platform crosses ~5 views OR you find yourself making
inconsistent UI choices, create that platform's binding doc
(`tvOS-DESIGN.md`, `iOS-DESIGN.md`, `macOS-DESIGN.md`, `WEB-DESIGN.md`,
`ANDROID-DESIGN.md`), seeded from the matching per-platform template
in `docs/templates/` (start from `PLATFORM-DESIGN-template.md`, the
index). Invoke
`binding-design-doc-discipline` for the workflow. Treat as binding
from the moment it exists.

The sibling docs share a shape: the **principles** are identical;
the **idioms** they reference diverge per platform. Deliberate
rule inversions between platforms (tvOS auto-focuses Play; iOS
never steals focus) are stated explicitly so they don't get
"harmonized" away.

---

## Open questions

- Which two people will the owner talk to, and what do their stories show?
- Does the owner's noticing log support the leading candidate?
- Do existing official resources already solve the information problem?
- Which parent participation routes exist beyond the public page, and
  what does providing under-18 parent contact details trigger?
- Which cycle years, cutoff times, and binding aid rules apply?
- What parent actions and communications are required for minors?
- Would a real parent find the proposed activity useful?
- Who will review source wording and keep it current? See the source note
  for unsent Admissions and Financial Aid questions.
---

## Out of scope (intentionally)

Document explicitly-rejected ideas so future sessions don't
re-litigate them. "We thought about this and chose not to design it
now" is far more useful than silently re-arriving at the same answer.

When a request gets declined, write a row. Format:
`**Idea**: Why declined. Revisit when …` (revisit condition lets
the entry retire when circumstances change).

| Idea | Why declined | Revisit when |
|---|---|---|
| Separate parent financial aid submission | Owner excluded it from Week 1; confidentiality unconfirmed | Owner authorizes later exploration and Minerva confirms the workflow |

---

## Session log

<!-- Append-only. Format: state found → work done → state left.
     Keep entries short: one paragraph per session. -->

**2026-11-04: Minerva Parent Hub Stage 00.** Found: uncustomized template
without project-specific problem evidence. Done: documented the owner's
person, problem, wish, privacy boundary, five provisional framings and ten
tests; official source findings and unsent Admissions questions; the three
idea questions, case against the idea, and one proposed activity. Updated
AGENTS.md and Decision 054. Archived the oldest template session word for
word in docs/SESSION-LOG.md. Left: Stage 00 not yet complete; owner review,
log, critique, two conversations, revised statement and cohort post remain.
No website code, builds, tests, installs, deployment, or messages to
Admissions. Public research is not user validation.

**Same-day clarification:** Found: the initial framing emphasized access
to information. Reviewed the official Parents & Families page in detail
and compared its coverage with the proposal. Updated the Stage 00 note,
source note, AGENTS.md, and Decision 054 to focus on parent participation
in admissions. Saved the owner's correction and why above. Left: existing
parent workflows, minor-specific steps, and confidential submission remain
unconfirmed; no website changes or messages to Admissions.

**2026-11-04: Stage 01 local prototype.** Found: documented parent
participation problem with Stage 00 validation still open. Done: built
the owner-authorized age-group guide, source-derived admissions and aid
steps, explicit confirmation questions, official links and optional
Admissions email action. Added a loopback-only Node preview server.
Updated README, AGENTS, parity and stage/source notes and Decision 055.
Checked the actual page in headless Edge and inspected screenshots.
Left: local review at http://127.0.0.1:8080; no commit, deployment, private
data, uploads or submissions. Interviews, phone feedback and Admissions
confirmation remain. Standard token drift check finds only line endings;
no token values changed and unrelated native files were left untouched.

**Pages release follow-up:** The owner authorized commit, main push and
Pages main/root publication. Reviewed all project changes; temporary browser
artifacts and credential tooling remain outside the repository. Verified
the guide under /minerva-parent-hub/ with Edge, added explicit manifest
scope and a path regression check, and set version 1.0.1/build 2. Six web
suites passed; the full token test passed in an LF-normalized temporary
copy. GitHub admin credentials are available; Pages was initially absent.
Left: commit/push and live verification pending, no new product scope.
