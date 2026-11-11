# Local Flask verification — 2026-11-11

## UI/UX and resource integration follow-up

The final complete pytest suite passed: **65 tests in 14.23s**, including all prior
authentication, persistence, CSRF, CRUD, and ownership tests. Eight added
cases cover the public homepage, authenticated home, owner-specific next
actions, owned/open question previews, zero-item progress, guidance anchors,
new resource provenance/search, and accessible validation/success feedback.
The existing seed-content expectation now reflects six resources instead
of four; checklist definitions, IDs, and schema are unchanged.

The expanded `node tools/check_flask_browser.mjs` passed real browser form
flows for registration/login, saved age/checklist/reminder/question data,
logout/login persistence, reminder editing/deletion, question editing,
resolution/deletion, resource search and the correct academic-model link.
It verified skip-link focus, keyboard activation of the native Explore
menu, visible focus, submission busy feedback, offline warning/disabled
writes, and an actual checklist update with JavaScript disabled.

The final browser run stored screenshots under ignored
`build/qa/flask-1794429424494/` and passed all flows above, including the
expanded-menu geometry check at every width. Final mobile dark homepage
and desktop light dashboard captures were inspected after template cleanup.

It checked **12 pages × 2 themes × 10 widths** (240 viewport/theme samples):
public home, login, registration, dashboard, guidance, aid, checklist,
reminders, questions, resources, deadlines, reminder creation. Widths were
375, 640, 800, 1280, 1600, 900, 768, 480, 320, and 375 pixels. No document
or main-container horizontal overflow was found. Each page had one h1.
Screenshots were captured at 375px and 1280px in both themes and inspected
for home, dashboard, guidance, resources, and registration. Screenshot review
caught and corrected wrapping step numbers on the mobile homepage; the
harness now checks that they stay on one line.

`node tools/flask_design_tokens.mjs --check` passed generated-file freshness
and **38 text/control contrast pairs** in light/dark (4.5:1 for normal text,
3:1 for control boundaries). A read-only comparison against HEAD's base
tokens confirmed that all 14 inherited platform outputs remain unchanged.
No new frontend framework, dependency, runtime API, or schema change.

The preserved web checks were rerun: parent guide PASS; API 2 passed; TV
focus 18 passed; TV UA 5 passed; packaged origin 1 passed/5 skipped; Pulse
charts 53 passed; Pulse rendering 39 passed. pip check, node syntax checks,
US-English check, and git diff whitespace checks passed. The inherited token
test still reports the same 13 CRLF-only failures documented below; inherited
color contrast and token negative controls pass. Native template files and
the original static prototype remain unchanged.

During development, one existing test caught a verification-date text
format change; the template was corrected rather than relaxing the test.
The first sandboxed pytest attempt was blocked by temporary-directory
permissions; the authorized run passed. An initial keyboard harness event
omitted Enter's text event, preventing native summary activation; sending
the complete keyboard event sequence fixed the instrument without custom
menu code. These initial failures are not outstanding application defects.

The existing local SQLite file had no user table. Missing tables were
initialized and reviewed public content seeded. An in-memory before/after
comparison verified that existing private-table records were unchanged;
new private tables were empty. No account credentials were created.

Remaining limits: Chromium checks are not Safari/Firefox, screen-reader,
real-device, or parent usability validation. Intake years, cutoff times,
parent consent/access, and aid-submission privacy still require Minerva's
confirmation. No commit, push, or deployment was performed.

## Original Flask build evidence

Engineering checks were run on Windows with Python 3.14, Node 24.14.1,
and headless Chrome. They do not constitute parent usability validation.
No commit, push, deployment, or native-template edit was performed.

## Application tests

```text
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
57 passed in 22.68s

.venv/Scripts/python.exe -m pip check
No broken requirements found.
```

CSRF was enabled. Tests exercised registration, scrypt hashing, login and
logout, missing/forged CSRF rejection for all mutations, protected reads
and writes, cookie properties, session tampering, age selection,
checklist toggling and uniqueness, reminder/question CRUD and validation,
cross-account denial including guessed edit/delete IDs, escaped text and
ignored owner-ID input, foreign keys and constraints, public search/filter
and source dates, deadline uncertainty, CLI initialization and idempotent
seeding, generated demo password hashing, database failure HTTP 503, and
HTTP 400/404/405/413/422 behavior. Persistence was tested through a second
application factory/client reading the same on-disk SQLite file.

The first sandboxed pytest attempt failed before database fixtures could
run: Windows denied access to pytest's default temporary directory. An
authorized rerun passed all 57 cases with a concurrent cache-directory
warning. The final run above disabled pytest's optional cache and passed
without warnings. This does not disable or relax any application safeguard.

## Actual browser

```text
node tools/check_flask_browser.mjs
PASS: browser register/login, saved age/checklist/reminder/question,
logout/login persistence; 9 pages × 2 themes × 10 widths;
offline notice/disabled writes; no-JavaScript checklist update.
```

The harness created a fresh synthetic account through real forms, saved
age and checklist marks, created and edited a reminder, created and
resolved a question, logged out and back in, and observed saved data on
the dashboard. It loaded dashboard, guidance, aid, checklist, reminders,
questions, resources, deadlines, and reminder creation at 375, 640, 800,
1280, 1600, 900, 768, 480, 320, and 375 pixels, in light and dark themes.
No document or main-container horizontal overflow was found. It also
observed the offline warning and disabled POST buttons, then updated a
checklist with JavaScript disabled and observed the changed dashboard count.

Screenshots and the synthetic database are in ignored
`build/qa/flask-1794426106427/`. Inspected dashboard light/375 and dark/1280,
questions light/375, checklist light/375, and reminder creation dark/375.
Labels, controls, source links, and privacy boundaries were visible and
readable. This is automated Chromium evidence, not a claim that Safari,
screen readers, or real parent devices have been tested.

## Preserved web checks

| Command | Actual result |
|---|---|
| `node tools/test_parent_guide.mjs` | PASS: original prototype links/assets remain under the Pages project path |
| `node js/api.test.js` | 2 passed |
| `node tools/test_tv_focus.mjs` | 18 passed |
| `node tools/test_tv_ua.mjs` | 5 passed |
| `node tools/test_packaged_origin.mjs` | 1 passed, 5 skipped for unused template features |
| `node tools/test_pulse_charts.mjs` | 53 passed |
| `node tools/test_pulse_render.mjs` | 39 passed |
| `.venv/Scripts/python.exe tools/test_us_english.py` | PASS: US English strings |
| Python compileall; node --check on new JS/harness | Exit 0 |
| `git diff --check` | Exit 0 |

## Existing checkout check failures

- `node tools/test_design_tokens.mjs`: 13 generated-file comparisons
  failed. A read-only comparison of each plan's current/expected text
  confirmed all 13 become identical after CRLF-to-LF normalization. Color
  contrast and negative controls passed. These files and the generator are
  unchanged in this task; the source note in Stage 01 already records this
  Windows line-ending issue. No native token file was rewritten.
- `.venv/Scripts/python.exe -X utf8 tools/test_agent_files.py`: three
  failures for `.agents/skills/human-shaped-review`,
  `learning-orientation-design`, and `make-it-look-like-itself`. Git tracks
  them as symlinks (mode 120000), but this Windows checkout contains ordinary
  pointer files, so their SKILL.md paths do not resolve. The actual skills
  were read from `.claude/skills/`. These pointer files are unchanged.
  Without `-X utf8`, that existing test first encounters Windows cp1252
  decoding of AGENTS.md. Neither failure is an application test failure.

`git diff --exit-code` for the original static HTML/CSS/manifest, native
folders, skill pointers, and the relevant generator/check scripts returned
0, confirming they were not changed to address these existing issues.

## Remaining review

No requested application feature is knowingly left as a placeholder.
Owner/device review and real-parent feedback remain; Minerva must clarify
intake years, cutoff times, parent permissions, and financial submission
privacy. The app intentionally does not resolve those questions itself.
Production hosting/security operations and unrelated template repairs are
outside this local-demo task. See README for the interview walkthrough.
