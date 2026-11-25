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

## Follow-up: interface friction

The Chromium baseline in `build/qa/flask-1795633867540/` showed two
headings for each Financial Aid task, multiple step counts, a written
state beside each visual state, and a checklist shortcut alongside
ongoing navigation. Planning also repeated its progress count.

- Financial Aid uses one task heading and short step names. A ring,
  selected state, and checkmark show what remains, where the user is,
  and what is prepared. Screen readers retain position and saved status.
- Guests move through the steps with Next and Back. The save-progress
  prompt appears on Financial Aid Home and review. Signed-in parents
  see a single progress count and confirmation after saving, and can
  skip or mark a step incomplete. Step-specific tools and role guidance
  remain available under Help.
- Home and parent Home rely on their destination tiles and next action.
  Planning, Help, Admissions, Deadlines, sign-in, invitations, and demo
  documents use shorter labels or consolidate repeated explanations.

The updated captures are in `build/qa/flask-1795634272163/`. In both
directories, compare `aid-step-light-375.png` and
`aid-step-dark-1280.png` at the same saved step. All 94 pytest tests
passed. Chromium exercised every step as a guest at both widths,
saved all seven steps on mobile, followed them again on desktop, and
verified persistence after signing back in. The visual sweep covered
28 page states in both themes at ten widths.

In the next observed session, check whether guests notice that progress
is temporary and whether mobile parents discover the Steps control.

## Beginner Financial Aid journey

The old entry asked families to decide whether to apply before explaining
what aid is. The new default opens five short topics: Understand, How it
works, Your role, Forms, and Aid offer. Parents can learn before opening
Preparation, jump between topics, or resume their saved checklist directly.
The desktop sidebar and mobile Topics control share the same links.
Reading a topic never marks a preparation task complete. Existing checklist
keys and saved records are retained, with no database migration.

The journey helps families interpret the process, discuss their respective
roles, and choose their own next steps. The student retains control of
their application. The guide links to official services and leaves the
aid decision to Minerva. This addresses the learning, participation,
agency, and simplicity checks without a calculator for eligibility.

### Policy verification, November 25, 2026

- [Minerva undergraduate aid guide](https://www.minerva.edu/undergraduate/financial-aid/)
  confirms demonstrated need, limited funding, need-aware admissions,
  family contribution, and the first-time forms and supporting documents.
- [Minerva FAQ](https://www.minerva.edu/faqs/) confirms that Minerva uses
  forms and supporting records, including local income equivalents, and
  that the College Board form and Minerva process apply to international
  applicants. It describes a loan-first offer, while the undergraduate
  guide describes a possible combination with no specified order. The
  journey presents possible components without promising their order,
  amounts, or coverage. The FAQ also gives exceptions to its general
  dependent-applicant guidance. The journey makes no determination of
  dependency or which exceptions apply to a particular household.
- The [admissions page](https://www.minerva.edu/undergraduate/admissions/),
  [College Board CSS Profile](https://cssprofile.collegeboard.org/), and
  [Minerva Financial Aid Center](https://www.minerva.edu/financial-aid-center/)
  were checked separately. The Center redirects to Minerva's applicant
  login, so instructions visible only after login were outside this check.

Returning-student demo document examples remain labeled separately from
first-time requirements. Confirm unavailable records, translation formats,
and individual circumstances with Minerva Financial Aid.

Chromium captures are in `build/qa/flask-1795635211133/`. The
`aid-learn-*` files cover each topic across mobile and desktop in both
themes. At 375px the first topic's Next button fits on screen, and the
Topics control opens and closes with the keyboard. Chromium followed
the introduction at 375px and 1280px and exercised saved checklist
progress and contextual tools. First-time parent comprehension still
needs observation.

## Financial Aid navigation and tools

The five learning topics remain the main journey. How it works uses
numbered headings inside the cards. Forms links to the official Minerva
aid guide through one resource card. Useful Tools is available from
Financial Aid Home, the topic selector, and the Aid offer screen.

All seven retired preparation topics were reviewed:

| Retired topic | Where the guidance is now |
| --- | --- |
| Start | Understand introduces need-based aid. Forms explains when to apply and links to the official guide. |
| Forms | Forms keeps the separate admissions, College Board, and Minerva responsibilities. |
| Dates | Forms links to Deadlines and directs the student to confirm the cutoff in the Financial Aid Center. |
| Records | Your role links to Financial document guidance, which separates current Minerva requests from returning-student demo examples. |
| Translations | Translation examples retain the advice on keeping the original and confirming the accepted format. |
| Review amounts | Financial document guidance covers names and periods. The calculator separates original amounts from conversions. |
| Submission | Forms points to outstanding requests in the Financial Aid Center and Minerva Financial Aid for questions about who can submit and see parent records. |

Old Financial Aid checklist and step URLs redirect. The existing private
checklist tables, seeded item identifiers, and saved progress remain.
Planning retains its separate checklist. Demo document access and sharing
continue to use the existing authorization rules.
