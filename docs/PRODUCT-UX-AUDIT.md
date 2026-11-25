# Parent Hub product UX audit

Baseline: commit `c4a8357`, Chromium at 375px and 1280px, light and dark.
The baseline evidence was captured under
`build/qa/flask-1795633070862/` using synthetic accounts.

| Journey | Observed problem | Revision |
| --- | --- | --- |
| Public Home | The mobile deadline card separates the opening action from a second set of links that repeats the header. | Start with Admissions and keep invited-parent login beside it. Retain verified dates on Home and compact the unavailable-cutoff state. |
| Admissions and Resources | The desktop guide opens several large panels at once. Jump links duplicate card titles. Results repeat the same search flow around a card wall. | Give Admissions a short topic index on desktop with expandable topics at all widths. Keep the existing topic anchors. Present resource results as rows. |
| Financial Aid and tools | The task screen hides seven-step progress behind a separate review link. Opening a contextual tool loses the visual step position. | Keep the current task and checklist together. Use a desktop sidebar and mobile disclosure. Contextual tools retain the selected step. |
| Deadlines | A large unavailable-cutoff card precedes the useful round dates on a phone. | Put the published rounds first when no exact cutoff exists. Retain the distinction between published month/day values and verified exact events. |
| Help and planning | Help uses nested navigation cards. Planning sits behind a generic More menu. | Keep official contact options separate from Parent Hub tools. Give signed-in parents a labeled Planning destination. |
| Parent Home and Application | Home repeats Application, Aid, Guides, and Help links. The stage is repeated above the detailed snapshot, which follows a long tile row. | Put the next aid action and authorized application snapshot together. Leave the full journey and its disclosures under Application. |
| Login, registration, and invitations | The mobile login starts with an account-creation prompt before the fields. The invite page competes with a deadline panel. | Put the form and its primary action first. Keep account switching and help adjacent to the form. |
| Demo documents and student sharing | Multiple document operations wrap underneath a single linked file. The student view mixes received documents and the preview without a clear grouping. | Keep Open and Share easy to find. Group Replace and Remove under File options. Visibly group the student’s received records, apart from the visibility preview. |

## Information architecture

- Public visitors use Admissions, Financial Aid, Deadlines, and Help.
  The brand returns to Home. Log in and account creation remain available.
- Invited parents use Home, Application, Financial Aid, Planning, and
  Help. Planning groups Checklist, Reminders, and Questions. Account
  handles invitations. Public guides, official resources, and deadlines
  remain accessible from Home, Help, or their contextual links.
- Students continue to start at Shared documents. Financial Aid and
  Help remain accessible. The visibility preview stays a local demo.
- Financial Aid retains its direct tools and document links. Start or
  Continue opens the current task with a step navigator. Links, native
  disclosures, and the existing checklist forms support keyboard use
  and browser history.

## Usability questions

Browser checks can verify navigation and state, but first-use comprehension
still needs observation. Ask a parent and an applicant to start with no
walkthrough. Watch whether they find the first aid action, understand the
difference between prepared and officially submitted, discover the mobile
step selector, and find the file options after sharing a demo document.

## Verification and visual evidence

All 94 pytest checks passed. Chromium tested 27 page states at ten
widths in light and dark themes, including keyboard navigation, the
mobile step selector, saved progress after re-login, contextual help,
and synthetic document sharing. The after captures are in
`build/qa/flask-1795633464908/`. The two local capture directories
contain matching mobile and desktop filenames for Home, parent Home,
Admissions, the aid task, the checklist and tools, documents and the
chooser, Deadlines, Help, login and registration, invitations, and the
student view. Captures use disposable test data and are ignored by Git.
