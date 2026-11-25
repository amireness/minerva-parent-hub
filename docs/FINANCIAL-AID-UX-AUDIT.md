# Financial Aid UX audit

Reviewed the pre-change Flask interface at commit `637d449` in Chromium,
including the invited parent flow at 375px and 1280px. These are engineering
observations. Parent and applicant usability sessions are pending.

| Original experience | Problem observed |
| --- | --- |
| Financial Aid opens on the demo document manager. Three equal jump links sit above it. | No clear first action. Demo document controls dominate before users understand the preparation process. |
| The checklist opens with the full process explanation and all seven tasks. | At 375px, the first Save control falls below the fold. Find the next task and saving it are separate decisions. |
| Glossary, translation examples, calculator, and document manager share one scrolling page. | Context links can move users a long way from their task. The next or previous step is difficult to recover. |
| Desktop places two large panels side by side. Mobile stacks the panels. | Desktop gives guidance and unrelated controls similar weight. Mobile magnifies the scroll required to switch tasks. |

## Revised journey

Financial Aid Home gives Start or Continue priority. Checklist and Demo
documents have stable direct links. The Preparation tools disclosure
links to each complete tool.

Preparation shows one existing step per URL. Signed-in parents can mark
it prepared and advance, continue without marking, or reopen it and mark
it incomplete. Signed-out users can read and move through the steps.
Previous, the checklist review, and ordinary browser navigation are
available throughout. The review distinguishes prepared and remaining
tasks. Context links open the relevant tool with an explicit return to the
same step. Continuing from Home selects the first remaining step.

Tools have their own view. The glossary initially lists terms in
disclosures. The translation view leads with the existing side-by-side
example, followed by optional instructions. Demo document operations
remain separate from preparation and use the existing sharing checks.
The shared Parent Hub header, Help, and policy wording remain in place.

## Remaining questions for usability review

- Can first-time parents distinguish saved preparation from official
  submission status without prompting?
- Can an applicant find translation or currency help and resume the same
  step on a phone?
- Do returning parents spot Checklist, Demo documents, and Preparation
  tools quickly enough? Observe shortcut discovery before promoting
  additional links.
