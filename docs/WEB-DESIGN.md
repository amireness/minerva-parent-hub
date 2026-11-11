# Parent Hub Flask web design

Scope: the owner-requested local Flask application (2026-11-11).
The static Pages prototype remains unchanged. This applies the requested
features and existing repository rules; it adds no native platform scope.

## Structure

Use server-rendered Jinja pages and ordinary links and labeled HTML forms.
Home becomes the parent's dashboard after login. Public guidance, aid,
resources, and deadlines remain readable without an account. Private
checklists, reminders, and questions require login. Create and edit forms
have their own URLs. Search and topic filters use GET query parameters.

## Appearance and content

Updated at the owner's request, 2026-11-11: Flask uses a restrained navy,
warm neutral, and gold identity, generated from Flask overrides in
design-tokens.json by tools/flask_design_tokens.mjs. Shared static tokens
and unused native templates stay unchanged. This web-only scope supersedes
the inherited all-platform palette rollout.
Use a single column at phone width and a centered 1200px workspace with
two or three columns on desktop. Use 44px controls, compact navigation,
active-page markers, and a consistent footer. Cards organize sections;
individual list rows use spacing/dividers, not repeated tinted boxes.
Home explains the product to visitors; authenticated Home remains the
planning dashboard. Serif display titles and system body text require no
external downloads. Preserve automatic light/dark themes. Gold is a brand
accent, never the sole status indicator.
Keep the original source-derived guidance and confirmation questions.
Checklist entries distinguish personal preparation from applicant duties.
Completion is personal planning, never an application status. Official
deadline month/day text is not converted into an inferred calendar year.
Personal reminders have parent-selected dates and no email delivery.

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
