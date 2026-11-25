# Session log archive

**2026-08-24: Windows scaffold + Tidbits lessons ported.** Found: sixth-gen
template with docs/windows/ present but no `windows/` source scaffold, a
WINDOWS-STORE-SUBMISSION.md that was an unadapted Tidbits copy (real Store
IDs), a playbook describing a pre-ship layout, and no vendored Windows skill.
Done: committed the `windows/` scaffold (AppName.Core / .App / .HeadlessTests /
.Windows: the as-shipped Tidbits architecture with every version gotcha
pre-solved; builds clean, 11 headless tests pass, shell PNGs verified light +
dark at 1180×760 and the 900×680 floor, versions stamped from
AppVersion.xcconfig); generalized WINDOWS-STORE-SUBMISSION.md (placeholders +
§0 checklist, all 12 gotchas + IAP §7 kept); rewrote WINDOWS-PLAYBOOK.md to the
as-built flat layout (.NET 10, TFM-isolation, DPAPI, narrow-width shell
renders, network-race flag); added the `windows-production-gotchas` skill;
added a `## Windows app` CLAUDE.md section + Windows columns in both design
tables; appended DECISIONS 035–039 (anonymous-account deletion, query-not-load,
generator merge guards, randomness-outside-selection, per-store billing
shapes); README tree/step-12 + CONTRIBUTING now name the scaffold. Left: green;
Store assets (7 PNGs) intentionally not generated (per-app branding);
first-Windows-run baselines armed via `-f update_baselines=true` as documented.

**2026-08-24 (second pass): parity + store-approval hardening.** Found: the
scaffold wave left three lesson families unported: multi-store IAP release
choreography, Play pre-launch/publish traps, and the parity-audit method
lessons. Done: new `docs/store/IAP-RELEASE-CHOREOGRAPHY.md` (financial
paperwork as owner-only critical path, one-review-submission-per-IAP-product /
ship serially, the Ready-to-Submit trap, per-platform License Agreement,
empty-success vs thrown-error, per-store query shapes, real-provisioning-only
purchase verification, the launch-order checklist); store-submission-playbook
gained the IAP section + the internal-track-has-no-pre-launch-report /
Test-Lab-yourself / refused-to-auto-submit / all-or-nothing-submit bullets;
play-cli-submission gained Rules 7–8 (Console stalls, testlab-android.sh);
cross-platform-parity-discipline gained the degenerate-outcome audit pass
(tie/zero/empty/cold-quit), the both-directions stale-⏳ check (false docs vs
false cells), and the failure-class organization for whole-platform-port
audits; tvos-platform-patterns gained the SignInWithAppleButton-in-Form
swallowed-click gotcha; CLAUDE.md table + README tree point at the new doc.
Left: green.


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

**Deployment result:** Commit 1dfa31e pushed to main. Pages configured via
GitHub API for main/root, build status built for that commit. Public HTML,
both stylesheets, both scripts and manifest returned HTTP 200 and matched
release content. Headless Edge repeated all interaction, responsive,
offline and no-JavaScript checks against the public URL successfully.
Published: https://amireness.github.io/minerva-parent-hub/.
No private applicant information or temporary browser files were committed.
Real-parent validation and policy confirmation still remain open.


**2026-11-11: Local Flask interview application.** Found: published static
public guide, no backend; unused native templates and unvalidated Stage 00.
Done: implemented the owner-requested modular Flask/SQLite app, preserved
source-derived guidance and shared CSS, added private account planning,
reviewed content seed and generated demo credentials, CSRF and ownership
guards, persistence and security tests, and browser verification. Updated
README, design/architecture/source/parity docs and Decision 056. Rolled the
oldest session entry and clarification word for word into SESSION-LOG.
Left: local app ready for owner review, with exact checks recorded in
FLASK-VERIFICATION.md; real-parent validation and Minerva policy questions
remain. Static release unchanged; no native edits, commit, push, deployment,
or release version bump. Secrets and synthetic test databases are ignored.


**2026-11-11: Flask UI and official resource integration.** Found: functional
Flask branch with uncommitted prior work; narrow, plain, text-heavy UI.
Done: owner-requested navy/neutral/gold redesign, wider responsive workspace,
public homepage, owned dashboard previews and next actions, concise guidance,
six source-linked resources, feedback states, and expanded keyboard/browser
checks. Preserved route URLs, security, schema, and private planning. Kept
Flask palette overrides in the one JSON source without changing inherited
platform outputs. Updated source/design/architecture/parity docs, README,
and Decision 057; archived the oldest session entry word for word. Left:
65 pytest cases pass; browser checks cover 12 pages in both themes at ten
widths, with keyboard/offline/no-JavaScript flows and contrast evidence in
FLASK-VERIFICATION.md. Local missing tables initialized, public data seeded,
existing private data preserved. Existing CRLF token-check failures remain.
No commit, push, deployment, native changes, or release version bump.
Owner device review and Minerva policy confirmation remain open.


**2026-11-18: Synthetic applicant onboarding.** Found: email/password
authentication, a private planning dashboard, and public guidance. Done:
added fictional applicants and milestones, one-time email-bound invitation
codes, and per-request access checks. Moved planning to /planning and
verified the additive schema against an existing account. Left: 73 pytest
cases passed, plus the Chromium harness across 14 page states, two themes,
and ten widths. Databases used for checks were disposable. Student issuance
and revocation controls, real-device review, and deployment remain outside
this iteration.


**2026-11-18: Signed-in overview and aid preparation.** Found: the owner
verified invitation and planning flows and requested clearer navigation.
Done: introduced a synthetic timeline, grouped planning tools, placed
additional invitations under Account, and added expandable aid examples
and role-based practice tasks. Left: 77 pytest cases passed. Chromium
checked 16 screen states across ten widths and two themes, including
keyboard and no-JavaScript disclosure controls. First-year requirements,
submission roles, and privacy procedures await the specialist interview.


**2026-11-18: Parent-centered MVP.** Found: working invitation onboarding and
aid example modules. Done: guided Home and application timeline, unified
Financial Aid, local document status and preset location notes, and
explicit sharing with a separate synthetic student login. Left: 85 pytest
cases passed. Chromium checked 17 page states, two themes, and ten widths,
including 375px and 1280px. Screenshots confirmed the parent action is
visible on Home at both sizes. Existing local databases need init-db.
Official submission roles and privacy expectations await the interview.


**2026-11-18: Aid document list.** Found: document preparation relied on
manual status and location fields. Done: replaced those forms with a
fictional file chooser, automatic linked-file counts, local preview, and
explicit sharing of category presence. Kept the old rows in SQLite.
Left: 85 pytest cases passed. Chromium checked 18 page states, ten widths,
and two themes. Reviewed Financial Aid at 375px and 1280px. Run init-db on
existing local databases to create the new document table.


**2026-11-18: Public and parent UI redesign.** Found: separate public
marketing content and a working parent journey and document workflow.
Done: shared destination tiles, deadline sources, native stage
disclosures, and global Help. Added exact deadline filtering and calendar
export. Minerva published month/day round dates without exact cutoffs
in the sources reviewed, so the exact catalog remains empty. Left:
89 pytest cases passed and Chromium checked 19 page states across ten
widths and both themes. Run init-db to add the optional round table.


**2026-11-25: First-time international aid.** Found: public aid guidance,
private checklist records, and fictional document linking. Done: added
a glossary, translation samples, illustrative currency conversion, guided
checklist steps, and a browser-only student visibility preview. Left:
91 pytest cases passed and Chromium exercised the new tools at phone and
desktop widths. Run seed-content to save the new steps on existing
databases. Minerva translation and parent submission rules remain open.


**2026-11-25: Render database startup.** Found: a fresh SQLite file
reproduced Financial Aid 200 and Deadlines 503. Done: made Render startup
create missing tables and refresh public data in a SQLite transaction.
Added fresh-start, concurrency, preservation, and failed-seed tests.
Left: local verification only. Render disk settings remain unconfirmed.
Default Render SQLite storage is ephemeral.

**2026-11-25: Financial Aid UX.** Found: Chromium showed the document
manager and three equal navigation choices at entry, with the first
checklist action below the initial mobile view. Done: placed one
Start or Continue action on Financial Aid Home, added URL-based steps
and review, and made each existing tool open and return independently.
Left: 94 pytest cases passed and Chromium completed all seven steps.
Parent and applicant usability observation remains open.

**2026-11-25: Product UX redesign.** Found: repeated destinations,
long admissions panels, and a Financial Aid step detached from progress.
Done: moved Planning into primary navigation, aligned public and parent
entry points with next actions, regrouped guidance and forms, and added
a desktop checklist and native mobile selector to the aid workspace.
Kept the existing routes and saved state. Left: see PRODUCT-UX-AUDIT.md
for evidence and the parent and applicant research questions.

**2026-11-25: UI friction pass.** Found: Financial Aid repeated task
titles, counts, navigation, and states, and Planning repeated its
progress count. Done: simplified the workspace and copy across the
Flask app. Left: 94 pytest tests passed and Chromium exercised guest
and signed-in steps, persistence, and keyboard use. See the audit for
before-and-after evidence. First-use observation remains open.
