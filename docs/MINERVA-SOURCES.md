# Minerva public information: research note

## Resource integration review — 2026-11-11

For the requested redesign, inspected both primary official pages and
followed their links rather than using search snippets as source facts:

| Parent need | Linked official destination | How the Hub uses it |
|---|---|---|
| Understand admissions | https://www.minerva.edu/undergraduate/admissions/ | Existing process summary, responsibility distinction, date caveat |
| Find family information | https://www.minerva.edu/parents-families/ | Overview and route to existing support |
| Prepare aid questions | https://www.minerva.edu/undergraduate/financial-aid/ | Preserved source steps, no financial data collection |
| Clarify admissions questions | https://www.minerva.edu/faqs/ | Existing FAQ/contact resource |
| Understand the academic model | https://www.minerva.edu/academics/ | New summary of active, discussion-based learning |
| Look ahead to academic events | https://www.minerva.edu/academic-calendar/ | Academic calendar, explicitly distinct from admissions deadlines |

All six destinations were opened. The family page also links handbooks,
emergency resources, and a request-information form. Those links were
identified but are not summarized as verified new resources in this change.
No handbook policy or private portal content is inferred. No pages are
copied wholesale, embedded, or fetched at runtime. Summaries are explicitly
owner-requested and source-based; they establish no new parent permissions.
Intake years, cutoff times, minor consent duties, and separate financial
submission privacy remain questions for Minerva and owner review. The
academic calendar does not resolve them.

## Local Flask application recheck — 2026-11-11

Reopened the official admissions, financial aid, Parents & Families, and
FAQ pages for the owner's requested database-backed prototype. The
under-18 contact-details requirement and existing application/aid guidance
remain supported. Admissions and aid tables still show the same month/day
deadlines without calendar years. The local app displays those published
values with a warning; it does not infer a year, cutoff, or personalized
deadline. `parenthub/content.json` contains the reviewed public seed data.
Original prototype wording is reused; parent preparation items are personal
planning suggestions, not new claims about required parent duties.
No private portal was accessed and no staff were contacted. Existing
questions about parent access and separate financial submission remain open.
The historical findings below retain their original check date.

Checked 2026-11-04 against official public Minerva pages. This is research
for Stage 00, not product copy or a personalized admissions timeline.
No applicant account was accessed. No Admissions staff were contacted.
Verification means the public page said this on the check date; it does
not resolve unclear policy or guarantee the page will remain current.

## Sources and findings

### S1. Undergraduate admissions

[Official admissions page](https://www.minerva.edu/undergraduate/admissions/)

The process covers background and academic information, online challenges,
and accomplishments. Applicants can start directly or through Common App.
Applicants under 18 provide parent or guardian contact details. Challenges
require a desktop or laptop. Academic records cover the most recent three
years and require school-official verification.

The following dates are printed on both the admissions and financial aid
pages. Their tables do not state years. Do not infer a personalized
deadline or countdown from them.

| Round | Admissions | Financial aid | Decision by |
|---|---|---|---|
| Early Action, binding optional | November 1 | November 8 | December 18 |
| Regular Decision I | January 5 | January 12 | February 26 |
| Regular Decision II | March 2 | March 9 | April 12 |

### S2. Undergraduate financial aid

[Official financial aid page](https://www.minerva.edu/undergraduate/financial-aid/)

The page gives 2027/2028 cost estimates and an October 1, 2026 CSS Profile
opening date, but its deadline table omits years. The aid process requires
the CSS Profile (school code 6033), Minerva's questionnaire, and supporting
income and parent/guardian bank documents. Questions go to
newstudentaid@minerva.edu. Aid must be requested during the admissions
cycle before the admissions decision. Minerva describes aid as need-aware;
packages may include scholarships, loans, and work-study. It says no
full rides are offered. This does not establish who can view each upload.

The page links a Financial Aid Handbook. Its contents were not reviewed
in this session; no claims about its privacy rules are verified here.

### S3. FAQs

[Official FAQs](https://www.minerva.edu/faqs/)

The FAQ says applicants must be over 16. Confirm exactly how this applies
to a 16-year-old. It lists admissions@minerva.edu for admissions questions.
Binding Early Action applicants must complete financial aid within five
days of submitting their application. It describes aid deadlines as
midnight US Pacific Time, using the label PST, on the date shown in the
student's Financial Aid Center. It requires a non-custodial parent form
even when that parent will not contribute. None of these statements
verifies a separate confidential parent login or submission route.

### S4. Parents & Families

[Official Parents & Families page](https://www.minerva.edu/parents-families/)

Reviewed in detail on 2026-11-04. The page provides general information,
student support and global-city guidance, links to admissions and aid,
and an After Admissions section describing updates sent to students.

## Existing page compared with the proposal

| Area | Verified on Parents & Families | Relationship to our proposal |
|---|---|---|
| General understanding | Explains Minerva and links to its academic model. | Already covered; do not duplicate the overview. |
| Support and rotations | Covers advising, wellbeing, city support, orientation, and contacts. | Already covered; use existing guidance. |
| Admissions resources | Links to admissions and tuition/aid pages. | Already provides public information routes. |
| After admission | Describes student checklists, deadlines, travel, and housing updates. | Does not establish parent delivery or access. |
| Parent participation | No parent task workflow or parent deadline view is described on this page. | Possible gap to investigate, not proof none exists. |
| Separate financial submission | No confidential parent submission workflow is described here. | Unconfirmed; later exploration only. |

The hypothesis concerns admissions participation, not missing parent
resources. Reviewing a public page cannot establish what staff emails,
private portals, or other parent processes provide. No usability
conversations have been supplied.

## Questions for Admissions and Financial Aid

These are unsent questions, not requests already made or promises of policy.

1. Which intake and calendar years apply to the published deadline table?
   What are the admissions and aid cutoff times, including daylight saving?
2. How does the binding five-day aid rule interact with the round's fixed
   aid date? What should parents do if the dates appear to disagree?
3. Does "over 16" include an applicant who is currently 16? Is age measured
   at application, admission, or enrollment? What extra steps apply to minors?
4. What parent actions, consent, and communications are required for
   under-18 applicants? What changes when the applicant turns 18?
5. Which parent resources and communication channels already exist? Can
   parents receive general guidance without access to student records?
   Is there a parent invitation, deadline view, task list, or communication
   route during application, distinct from updates after admission? What
   happens after an under-18 applicant supplies parent contact details?
6. What information can staff share with a parent, and what student
   permission is needed? Providing contact details alone proves no access right.
7. For later exploration: can each parent submit financial documents
   separately? Can the student or another parent see forms, uploads, or
   financial figures in Minerva's systems or the CSS Profile workflow?
   What is the route for separated parents or unsafe family situations?
8. Which team should review the Hub's factual wording, source reuse,
   update process, and presentation? No Minerva endorsement is established.

## Handling uncertainty in a later prototype

**Stage 01 use (2026-11-04):** Admissions, financial aid, and FAQ pages
were rechecked for the local guide. It uses the under-18 contact-details
requirement, application and aid process summaries, and published contact
addresses. It links to deadlines rather than copying unconfirmed years.
The Parents & Families link remains a route to existing resources.
Open policy questions below are not resolved by building the prototype.

Link to the official page rather than guessing. Do not label a date
"your deadline" without confirming the intake and relevant rules. If a
public source and an account-specific instruction differ, direct the family
to Minerva for clarification; the Hub cannot resolve the discrepancy.
Any future data pipeline, refresh schedule, and human review process
remain undecided. Do not use old handbooks or search snippets as current
policy, and do not promise financial confidentiality based on public text.
