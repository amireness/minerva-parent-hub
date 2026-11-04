# Stage 01: local parent admissions guide

2026-11-04. Initially built for local owner review. The owner subsequently
authorized committing, pushing main, and publishing the unchanged scope
through GitHub Pages. Deployment status is recorded below.
Stage 00's missing interviews and other evidence remain open. The owner
explicitly authorized this prototype; that is not proof the problem is
validated or either stage is complete.

## What is implemented

- A native select for under 18 or 18 and older, with a neutral starting state.
- Under-18 guidance about parent contact details, linked to Minerva.
- Published application and financial aid steps derived from official sources.
- Separate confirmation questions about parent responsibilities, permissions,
  deadlines, and confidential financial submission.
- One optional next action: contact Admissions using the published address.
- Links to existing Parents & Families resources, admissions, aid, and FAQs.

No credentials, names, exact ages, documents, applicant status, database,
analytics, uploads, or submissions. The age-group choice is not stored or
sent anywhere. Email links contain no personal details or generated message
and never send automatically. External navigation may use the normal
browser/network behavior of the destination; the Hub adds no tracking.

Source facts are static, source-derived summaries, not invented policies.
Functional labels and confirmation questions are prototype wording for owner
review. Facts were rechecked against the official admissions, aid and FAQ
pages on 2026-11-04; see `MINERVA-SOURCES.md`. No deadline dates or eligibility
promises are shown. No claim of official Minerva endorsement is made.

## Design check

The Stage 00 case against duplicating official resources still applies.
This prototype tests whether separating published steps from questions
helps a parent identify their own role. Parents choose a context and a
question; the guide neither acts for a student nor decides their duties.
It makes the process visible, invites discussion, preserves agency, and
uses native controls. Those are the four learning-orientation design
checks at implementation review, not observed learning outcomes.

The existing template provides HTML, JavaScript, CSS and design tokens.
The guide uses those tokens unchanged. `js/api.js` is preserved but unused;
there are no runtime data calls. CSS specific to the guide is separate
from the template's generated token block. TV additions remain in the
repository but are not loaded by this phone/browser prototype.

## Review locally

Run `node tools/serve.mjs` from the repository and open
http://127.0.0.1:8080. The server binds to this computer only. No install
or build step is required. Ctrl+C stops it. A phone cannot reach this
loopback address; real-phone review needs a separately arranged local
network preview or later authorized hosting. Nothing is published now.

1. Start with no age group selected. Both conditional panels should be hidden.
2. Choose under 18. Read the published contact-details requirement and the
   separate question for Admissions. Choose 18 or older; only that panel
   should remain. Reset to Choose an option to return to the initial state.
3. Read the application and aid sections. Confirm that applicant steps are
   not presented as permissions or assigned parent tasks.
4. Tab through the control and links. Check focus visibility and browser zoom.
5. Open official resources. Review the email address before choosing to
   open an email app; sending a message is your decision, outside the guide.
6. Try light and dark appearance and narrow/mobile browser sizes.
7. Turn the network off after opening. The guide should remain readable,
   with an offline notice. Links need a connection. Offline reopening is
   not supported because there is no service worker or cache guarantee.
8. Disable JavaScript and reload. Static facts and links remain; a fallback
   explains that the age control needs JavaScript.

## Verification and limits

Headless Edge exercised the actual page: no selection, both age branches,
reset, offline notice, online recovery, and no-JavaScript fallback passed.
No third-party resource loads were observed. Width checks at 320, 375,
640, 768, 900, 1280 and 1600 pixels found no horizontal scroll. Mobile and
desktop screenshots were opened for inspection; dark theme was checked.
These are engineering checks, not real-parent or real-phone validation.

`node --check js/app.js` passed. The standard design-token check reported
13 mismatches; a read-only comparison showed all 13 were CRLF/LF-only,
including untouched native files. Contrast and negative controls passed.
No unrelated generated platform files were rewritten to clear this result.
All scripts in `js/` passed syntax checks; both guide stylesheets passed
brace-balance checks. Existing API, TV focus, TV user-agent, packaged-origin,
Pulse chart and Pulse render suites exited 0 (the packaged-origin suite
reported five skips). `git diff --check` passed. A read-only normalized
token comparison passed without changing generated files.

Browser checks used a temporary Node script over Edge's debugging protocol,
not an installed browser-testing package. Screenshots for this session are
in the system temporary directory as `minerva-guide-375.png`,
`minerva-guide-1280.png`, `minerva-guide-dark.png`, and `minerva-guide-lower.png`.

Content is bundled, so there is no asynchronous loading or empty data
request. The initial unselected state is explicit. Static guidance works
if script execution fails; network unavailability is reported. The browser
handles errors at external destinations; this page cannot verify their
availability. No parent account or confidential submission capability is
offered, and its absence is stated rather than implied to be available.

Still needed: owner wording review; two real conversations; at least two
feedback rounds from the owner's phone; one parent using the guide without
an explanation; Admissions confirmation of roles, permissions, minor-specific
requirements and deadline interpretation; and a source refresh/review process.
The current manual snapshot is not Stage 01's completed data pipeline.
No release version bump, commit, deployment, or live-address validation yet.

## Pages release 1.0.1

The owner authorized publication on 2026-11-04. This supersedes the earlier
local-only instructions above. Version is 1.0.1, build 2. Target:
https://amireness.github.io/minerva-parent-hub/.

All five local resource URLs resolve under the project directory. Manifest
start URL and scope are `./`; official Minerva links remain absolute.
Added `.nojekyll` and a path regression check with a failing root-path
negative control. No browser profiles, screenshots, credential helpers,
or temporary verification scripts are included in the project commit.

The actual page passed the earlier Edge checks again while served at
`http://127.0.0.1:8081/minerva-parent-hub/`. The six existing web test suites
exited 0 again (five packaged-origin skips). Syntax and diff checks passed.
The stock Windows token check still reports 13 CRLF-only differences;
the unmodified full token test passed in an isolated LF-normalized copy:
all 14 token files match; contrast holds in light and dark.
Release values and Android's shared-version reference were checked.
Native build toolchains were not run for this web release; native apps
remain unadopted scaffolds and their runtime behavior is not verified.

GitHub authentication and repository admin permission were confirmed.
Pages was initially absent. Publication and live verification are pending
the release push; they are not implied by the local browser results.
