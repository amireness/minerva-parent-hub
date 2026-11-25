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

- **Published state**: Static Pages release 1.0.1 remains unchanged.
- **Local work (2026-11-11)**: Owner-requested Flask/SQLite interview app
  implemented in parenthub/, with authentication, private planning, reviewed
  public content, initialization/seed commands, pytest suite, and docs.
- **UI follow-up (2026-11-11)**: Wider navy/neutral/gold Flask UI, public
  landing page, data-backed dashboard, five-section guidance, and six
  official resources. 65 pytest cases and the expanded browser check pass.
- **Local onboarding (2026-11-18)**: Invitation acceptance unlocks read-only
  synthetic milestones. Personal planning is at /planning and public pages
  remain accessible. Run init-db on existing local databases before trying
  the workflow. Verification is recorded in the session entry below.
- **Owner verification**: The owner manually tested invitation login,
  synthetic applicant display, planning, checklist, reminders, and questions
  before requesting a clearer signed-in overview.
- **Signed-in overview**: Application timeline, planning tools, aid
  preparation, and account invitations have distinct locations. Aid examples
  are scoped to returning-student reference material. The specialist
  interview will clarify first-year requirements and submission privacy.
- **Parent MVP**: Home, Application progress, and Financial aid are the
  primary destinations. The two new tables support local category
  preparation and explicit sharing with CLI-provisioned demo students.
  Existing local databases need init-db before running this version.
- **Document tracking**: Financial Aid now derives progress from fictional
  file links. The prior manual records remain in SQLite. Run init-db to
  create the document-link table.
- **Owner feedback (2026-11-11)**: The first UI was too plain, text-heavy,
  narrow, and difficult to navigate. **Why:** The parent workspace should
  be intuitive and professional, with official facts kept separate from
  private planning. See docs/WEB-DESIGN.md and Decision 057.
- **UI redesign**: Public and parent Home share destination tiles. Help is
  global. The exact deadline catalog awaits verified round cutoffs.
- **Scope**: Web only. Native templates untouched. No push or deployment.
- **Privacy**: Milestones are fictional. Official application records,
  applicant credentials, financial details, and documents stay outside the
  app. Questions and reminders stay local to each account.
- **Owner clarification (2026-11-04)**: Do not suggest Minerva lacks parent
  resources. **Why:** Its Parents & Families page already covers general
  information and links to admissions; the question is participation in
  admissions itself, including the parent's own steps.
- **Verification**: See docs/FLASK-VERIFICATION.md for commands and actual
  results. Engineering checks do not establish real-parent usability.
- **Open content limits**: Official deadlines omit years; parent access,
  consent duties, and separate financial submission remain unconfirmed.
- **Next**: Owner follows README setup and interview walkthrough, probes
  the app on their own devices, and reviews the diff. Stage 00 validation
  and real-parent feedback remain open. No release version bump until ship.

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
| Google Sign-In, student-managed invitations, and revocation controls | First iteration uses existing authentication and local development issuance | Owner scopes a later iteration |
| Official application integration | Owner limited this iteration to synthetic data | Owner explicitly authorizes a separate scope |

---

## Session log

<!-- Append-only. Format: state found → work done → state left.
     Keep entries short: one paragraph per session. -->

**2026-11-25: Beginner Financial Aid.** Found: the first task asked
families to decide whether to apply. Done: added a five-topic introduction
based on official sources and retained existing checklist records and
tools. Left: see PRODUCT-UX-AUDIT.md for source differences and validation.
First-use comprehension still needs parent observation.

**2026-11-25: Financial Aid navigation.** Found: five useful learning
topics followed by an extra checklist workflow. Done: grouped links to
existing tools, relocated essential guidance, and redirected old steps.
Left: saved checklist records remain in the database. Individual tool
redesign and real document storage remain outside this iteration.
