# First-time international financial aid

Sources checked November 25, 2026. Scope is prospective undergraduate
applicants and their parents. Parent Hub is an independent research prototype.

## Confirmed and comparative findings

| Source | What it supports | Design implication |
| --- | --- | --- |
| [Minerva undergraduate financial aid](https://www.minerva.edu/undergraduate/financial-aid/) and [admissions](https://www.minerva.edu/undergraduate/admissions/) | The published need-based aid process lists the CSS Profile, Minerva's Financial Aid Questionnaire, and supporting income and bank documents. Aid has a round-specific deadline during the admissions cycle. The page gives local income-record examples and describes an early-application case where the latest available income records may be used. | Separate admissions from the two aid forms and supporting records. Link to the current instructions for the exact documents and dates. |
| [College Board home-currency guidance](https://cssprofile.collegeboard.org/help-center/do-i-complete-css-profile-my-home-countrys-currency) | CSS Profile asks for home currency and converts information after submission. | Distinguish currency practice from data entry. Minerva's separate forms may have their own instructions. |
| [MIT international aid](https://sfs.mit.edu/undergraduate-students/apply-for-aid/international/) | MIT asks for local parent tax documentation or income evidence and applicable English translations, permits informal translations, and uses IDOC. Its portal shows supplemental requests and messages. | Use originals and translations side by side and separate the preparation list from institutional receipt. MIT's translation policy applies to MIT. |
| [Yale prospective aid](https://finaid.yale.edu/apply/prospective) and [Yale aid FAQs](https://finaid.yale.edu/faq) | Yale uses a personalized checklist and contacts international applicants with further instructions. Its FAQ distinguishes missing documents, non-filing statements, and waiver review. | Make “ask about a missing document” a visible route and leave exceptions to the institution. |
| [CFPB glossary](https://www.consumerfinance.gov/consumer-tools/educator-tools/youth-financial-education/glossary/), [Canada Revenue Agency T4 guide](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/tax-slips/understand-your-tax-slips/t4-slips/t4-statement-remuneration-paid.html), [UK P60](https://www.gov.uk/paye-forms-p45-p60-p11d/p60), and [MoneyHelper current accounts](https://www.moneyhelper.org.uk/en/everyday-money/banking/current-account.html) | Plain-language definitions and specific evidence that labels, deduction categories, periods, and bank terminology differ. | Canada and UK examples are brief annotations. Test whether parents need a country selector before adding one. A T4 or P60 is not a blanket substitute for a US form. |
| [ECB reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.em.html) and [Bank of Canada Valet](https://www.bankofcanada.ca/valet-api-how-to/) | Official sources for indicative, dated reference-rate data. Coverage, base currency, and publication times differ. | If useful after validation, publish a cached table with provider, base, observation date, and missing/stale states. Send only public currency-series requests. Convert example amounts locally. Confirm reporting policy before suggesting any provider or date for a Minerva form. |

Minerva's public aid page linked to a Financial Aid Handbook, but the
linked file returned HTTP 401 during this review. Translation acceptance,
certification, and the terms of any separate parent submission could not
be confirmed from the accessible pages. The fictional document excerpts
and the fixed November 25 demo rates are educational. They carry no
institutional acceptance or market-rate claim.

## Prototype and privacy

- Financial Aid groups the glossary, translation examples, calculator,
  and seven preparation steps. The checklist uses existing account-owned
  completion rows. Marks describe preparation only.
- Glossary searches and calculator amounts are local browser interactions.
  The calculator uses fixed USD, EUR, GBP, and CAD factors authored for
  this demo. It neither sends nor saves entered amounts.
- The student visibility preview starts with public guides only. Toggling
  mock milestones or preparation categories changes a local preview.
  It has no save action or permission effect. The existing invitation
  and sharing checks continue to control the synthetic records.
- A document link currently stores a category, fixed fictional sample
  ID, ownership keys, and a sharing flag in SQLite. Document previews
  are local labels. Parent Hub never stores file contents, accepts real
  URLs, or talks to Google Drive. Replacing a sample clears its share.
- The repository supplies Gunicorn and has no checked-in Render Blueprint.
  The connector did not return live service configuration. No deployment
  setting was changed.

## Questions for the Financial Aid Coordinator

1. For a first-time applicant, which period and household members apply to
   each income, tax, pension, and bank record? Does the cycle differ by round?
2. What should families provide when there is no tax-return system, the
   return was not filed, an employer cannot supply a statement, or an
   account has no monthly statement? Which alternatives need approval first?
3. Is a parent- or student-prepared translation accepted? Is certification
   needed for some documents? Are excerpts accepted, and should the original
   and translation be submitted together? May identifiers be redacted?
4. How should applicants explain local terms for employer pension
   contributions, pension payments, government benefits, payroll deductions,
   and everyday bank accounts when no US term fits?
5. Which of Minerva's separate forms require original currency versus USD?
   If conversion is requested, which provider, observation date, and rounding
   should the applicant use? How should mixed currencies be handled?
6. Who can provide each household member's information, including a
   noncustodial parent? Can a parent submit privately? Who can see the record
   after upload and who can replace or correct it?
7. Where can an applicant see whether a record was received, reviewed,
   missing, or waived? What is the escalation path near a deadline?
8. What information should a student be able to reveal or revoke for an
   invited parent, and which details should always remain private?

## Next iteration

Run a synthetic parent walkthrough and ask the coordinator to review the
terms, sample format, and checklist. Prioritize approved document examples,
missing-document routes, and two-way visibility expectations. Consider a
dated reference-rate table only if the need survives testing. File
retention, access logs, encryption, deletion, and version history need a
separate privacy design before any real storage is considered.

Related issues are [#4](https://github.com/amireness/minerva-parent-hub/issues/4),
[#5](https://github.com/amireness/minerva-parent-hub/issues/5),
[#7](https://github.com/amireness/minerva-parent-hub/issues/7), and
[#8](https://github.com/amireness/minerva-parent-hub/issues/8). The visibility
preview informs [#3](https://github.com/amireness/minerva-parent-hub/issues/3)
and [#6](https://github.com/amireness/minerva-parent-hub/issues/6).
Real storage and versioning in [#1](https://github.com/amireness/minerva-parent-hub/issues/1)
and [#2](https://github.com/amireness/minerva-parent-hub/issues/2) remain out of scope.
