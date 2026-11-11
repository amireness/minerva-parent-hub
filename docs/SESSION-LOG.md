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
