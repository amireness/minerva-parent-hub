# Parent Hub Flask web design

Scope: the owner-requested local Flask application (2026-11-11).
The static Pages prototype remains unchanged. This applies the requested
features and existing repository rules; it adds no native platform scope.

## Structure

Use server-rendered Jinja pages and ordinary links and labeled HTML forms.
Home becomes the parent overview after login. A valid accepted invitation
shows a read-only synthetic timeline, the current stage, the next milestone,
and a parent preparation action. Give each linked applicant a separate
timeline. Keep planning completion on the planning screens.
Otherwise Home shows the invitation form. Personal planning has its own
signed-in page and remains available independently of invitations.
Use matching destination tiles on public and parent Home. Show verified
upcoming deadlines beside the public login or the parent's application
summary. Show Help in the shared header and keep official contacts apart
from saved questions. Use native disclosures for application stages and
guidance. Guide the parent from the current stage to one financial aid action. Group
checklist, reminders, and questions under the secondary Planning workspace.
Place additional
invitation acceptance in Account, with the existing acceptance endpoint.
Public guidance, aid,
resources, and deadlines remain readable without an account. Private
checklists, reminders, and questions require login. Create and edit forms
have their own URLs. Search and topic filters use GET query parameters.

## Appearance and content

Updated at the owner's request, 2026-11-11: Flask uses a restrained navy,
warm neutral, and gold identity, generated from Flask overrides in
design-tokens.json by tools/flask_design_tokens.mjs. Shared static tokens
and unused native templates stay unchanged. This web-only scope supersedes
the inherited all-platform palette rollout.
Use one centered content column for Home and Application progress.
Financial Aid uses the wider workspace, with document rows that stack on
small screens. Preserve the existing responsive planning layouts. Use
44px controls, compact navigation,
active-page markers, and a consistent footer. Cards organize sections;
individual list rows use spacing/dividers, not repeated tinted boxes.
Home explains the product to visitors. Serif display titles and system body text require no
external downloads. Preserve automatic light/dark themes. Gold is a brand
accent, never the sole status indicator.
Keep the original source-derived guidance and confirmation questions.
Checklist entries distinguish personal preparation from applicant duties.
Completion is personal planning, never an application status. Official
deadline month/day text is not converted into an inferred calendar year.
Countdown and calendar downloads require a verified year, time, and
timezone. When an applicant's round is recorded, favor that round and
generally applicable events.
Personal reminders have parent-selected dates and no email delivery.

Show a file list and count linked example categories. Use native disclosures
for details and an inline chooser for adding and replacing a fictional
Google Drive link. Keep application stages separate from document counts.
Sharing a document's presence is an explicit Parent Hub action. Replacing
or removing a file clears the share. Category examples come from
returning-student guidance. First-year details await the specialist interview.

## States and privacy

Browser navigation supplies loading feedback. Empty lists have a creation
link; failed validation retains entered values and displays errors.
HTTP 400/404/413/500/503 pages show a recovery link; failed writes roll back.
An offline notice disables mutations when JavaScript detects disconnection;
without JavaScript the browser reports connection failure. No offline queue,
service worker, or caching of private pages. Login gates explain sign-in.
Use CSRF-protected POST for every mutation, including logout and deletion.
Show only the signed-in user's records. No financial uploads or applicant
credentials. Maintain the independent-prototype notice on every page.

## Requested workspace and guidance

The requested progress indicator shows personal task completion, never
admissions likelihood, a score, or official status. Welcome uses the account
email. Reminder/question previews and next actions use owner-scoped queries.
Suggestions first ask for an unsaved age group, otherwise link to the first
incomplete parent preparation item. Never ask parents to do applicant work.
Guidance has five anchored sections: application, parent involvement, aid,
deadlines/planning, and official support. Consolidate uncertainty in relevant
sections and the shared footer. Preserve source-derived facts; concise
resource summaries and homepage copy are explicitly requested by the owner.
No runtime external requests, embedded official pages, or new dependencies.
