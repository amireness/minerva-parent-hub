# Minerva Parent Hub

A database-backed Flask web application for private parent planning around
Minerva admissions. It preserves the existing public guide, financial aid
guidance, official resources, light/dark design tokens, and responsive layout.
**Independent interview prototype, not an official Minerva admissions portal.**
It never accesses an applicant account or submits anything to Minerva.

## Run locally on Windows (Git Bash)

Install Python 3.10+ and Git for Windows first. Python 3.14 was used for the
recorded verification. In Git Bash:

```bash
git clone https://github.com/amireness/minerva-parent-hub.git
cd minerva-parent-hub
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python -m flask --app parenthub init-db
python -m flask --app parenthub seed-content
python -m flask --app parenthub run --host 127.0.0.1 --port 5000
```

Open http://127.0.0.1:5000. Stop with Ctrl+C. If `python` is not found, use
`py -3 -m venv .venv` for the creation command; after activation, use
`python` as shown. The interpreter must be a real Python installation,
not a Microsoft Store placeholder. macOS/Linux use
`source .venv/bin/activate` instead.

The server's database lives at `instance/parenthub.sqlite`. Restarting the
server preserves accounts and planning. The secret above exists only in
the shell environment. Keep the same value while demonstrating; changing
it invalidates sessions but does not delete records. In a new shell,
activate the venv and export a secret again before starting Flask. Never
commit a secret or database. `.env.example` documents supported settings;
a local ignored `.env` is supported by python-dotenv, but exporting secrets
avoids writing them to disk. Never use the Flask development server as a
public production service.

Run `init-db` again on an existing local database after upgrading. The
optional applicant-round table is additive. Public and signed-in Home link
to the official round dates. Countdown and calendar downloads require a
verified year, time, and timezone for a future deadline.

## Local demo account

In an activated shell with SECRET_KEY set, after init-db:

```bash
python -m flask --app parenthub seed-demo
```

The command creates `demo@example.com`, generates a random password and
prints it once, plus one saved checklist item, reminder, and question.
There are no hardcoded login credentials. This is an explicit local demo
command; it is never run automatically on startup. Repeating it refuses
to reset an existing account. To create another local demo account, use
`seed-demo --email another@example.com`. Do not use real applicant or
financial data in demonstrations.

## Try synthetic applicant onboarding

Use a disposable local SQLite database. If you already have a local
database, run `init-db` to add the three onboarding tables while preserving
accounts and planning records.

```bash
python -m flask --app parenthub --debug seed-invitations --email demo@example.com
```

Register or log in with the matching parent email, then enter the generated
code on Home. Each code is shown once, has one acceptance, and grants access
until the displayed UTC expiration date begins. Keep the code private.
Application numbers identify fictional records only. Use `--count` to
generate more than one applicant and invitation for the same email.
Guidance and resources are public. Planning remains available after login.

## Try financial aid preparation and sharing

Run `init-db` again if you already have a local database. It creates the
document-link table while preserving previous preparation records.
With the fictional application number from `seed-invitations`, create a
separate student login in the same disposable SQLite database:

```sh
python -m flask --app parenthub --debug seed-student --email student@example.com --application-number SYN-YOUR-DEMO-NUMBER
```

As the invited parent, open **Financial Aid**, choose **Add document**,
and link a fictional Google Drive example. The document count updates
automatically. Choose **Share** to show the category's presence to the demo
student, then use **Stop sharing** to revoke that access. Open previews the
fictional file locally. The prototype does not accept real links or change
Google Drive permissions.

## Verify each feature / interview walkthrough

1. Open Guidance and Financial aid while logged out. Read the preserved
   guidance and follow official links. Deadlines shows verified month/day
   text and explicitly warns that the official table omits years.
2. Register a new parent account (password length 12 to 128), then log in.
   Open Planning, select Under 18 and save, then switch to 18 or older to
   see the different parent-role guidance.
3. Open Checklist. Mark a parent preparation item and save; mark or unmark
   an applicant responsibility. Return to Planning to see the saved count.
   Explain that this does not update or reflect a Minerva application.
4. Create a personal reminder with a date. Edit its text and date; mark
   Completed in the edit form, then unmark it. Check Upcoming/overdue and
   Completed sections. Delete a spare reminder.
5. Save a question for Admissions, edit it, mark Resolved, then reopen it
   by clearing Resolved in the edit form. Delete a spare question.
   Nothing is automatically sent to Minerva.
6. Search Resources for `challenges`, filter Admissions or Financial aid,
   and try a search with no matches. Check source links and verification dates.
7. Log out, log in again, and verify age group, checklist, reminders, and
   questions remain. Restart the server and repeat to demonstrate SQLite
   persistence. Create a second account in another browser profile; it
   cannot see the first account's data or edit its record URLs.
8. Walk through the request flow and schema in
   [the architecture overview](docs/FLASK-ARCHITECTURE.md). Explain the
   tradeoffs: SQLite for a small local demo, server-rendered forms for
   simplicity, ownership checks beyond login, and reviewed content rather
   than invented admissions dates.

Reminders are in-app planning records, not scheduled notifications. Free
text must not contain confidential applicant or financial information.
There is no file upload or financial information form.

## Tests

```bash
python -m pytest -q
python -m pip check
```

Tests use isolated temporary databases; they do not modify your local
accounts. CSRF remains enabled in tests. They cover registration/login,
password hashing, protected routes, session handling, checklist progress,
reminder/question operations and validation, persistence through a new app
instance, cross-account isolation, safe text rendering, foreign keys,
constraints, public resource filters, deadlines, and seed commands.

Optional browser verification requires Node 22+ and Chrome (neither is
needed to run the application):

```bash
node tools/check_flask_browser.mjs
```

On Windows it uses Chrome's standard installation location and the local
venv. Override CHROME and PYTHON environment variables for other locations.
It starts a temporary loopback server and browser, stores a synthetic
database and screenshots under ignored `build/qa/`, then stops both.
See [verification evidence](docs/FLASK-VERIFICATION.md) for actual results.

## Content, schema, and commands

The homepage explains the product before registration. Signed-in Home opens
the invitation form or the linked synthetic dashboard. Planning shows saved checklist progress,
personal reminders, open question previews, and a next action derived only
from your parent preparation items and age-group selection. Guidance has
five anchored sections. Resources now includes six official destinations,
including the academic model and academic calendar (not admissions dates).

To refresh an existing local database after content changes:

```bash
python -m flask --app parenthub seed-content
```

This preserves account and private planning data. The layout automatically
follows your device's light/dark preference. Navigation, forms, and native
disclosure menus are keyboard-accessible and work without JavaScript;
JavaScript adds offline and submission feedback. No runtime external data
requests or new dependencies are introduced.

The Flask palette is defined under `flask` in `design-tokens.json`.
After editing it, regenerate only Flask's tokens and check contrast:

```bash
node tools/flask_design_tokens.mjs
node tools/flask_design_tokens.mjs --check
```

The generated CSS is included, so Node is not required to run Flask.
Inherited static/native tokens are intentionally unchanged for this web-only
redesign. See [web design rules](docs/WEB-DESIGN.md).

- `parenthub/content.json`: source-derived resource descriptions, shared
  checklist items, official deadline text, and last-verified date. Review
  the actual official pages before changing this date. Run `seed-content`
  to upsert by stable slug; user records and progress are preserved.
- `init-db`: creates missing tables without dropping records. It does not
  migrate existing tables; future schema changes require migrations.
- `seed-demo`: creates synthetic local data and a generated password.
- `seed-invitations`: creates fictional applicants, milestones, and pending
  parent invitations in local development.
- [Architecture and relational schema](docs/FLASK-ARCHITECTURE.md)
- [Source findings and unresolved policy questions](docs/MINERVA-SOURCES.md)

Known limits: local development hosting; no password recovery, email
verification, rate limiting, or offline writes. Source freshness requires
manual review, and intake years/cutoff times require confirmation with
Minerva. Real-parent usability validation remains open. No production
hosting or deployment is included.

## Preserved static prototype and platform templates

`index.html`, `js/app.js`, `css/styles.css`, and `css/parent-guide.css`
remain intact. `node tools/serve.mjs` previews the original static guide
at http://127.0.0.1:8080. Its Pages release is unchanged at
https://amireness.github.io/minerva-parent-hub/.
GitHub Pages cannot run Flask or private database features. This change
has not been pushed or deployed. Unused native templates are untouched.
The inherited template documentation below describes template capabilities,
not additional shipped Parent Hub apps.

<details>
<summary>Original universal template documentation</summary>

# Universal App Template

Archive Watch started on April 17, 2026, as an Apple TV app for
watching old public-domain films. By the end of September it ran on
iPhones, iPads, Macs, Apple TVs, Android phones, Google TVs, Fire TVs,
Rokus and the web, from one repository, built mostly by one person
working with Claude Code.

This template is what I learned doing that, and doing it three times
before with BOBA Playbook, Bsky Dreams and Tidbits Trivia. It is a
starting point for your own app: a web app, a native Apple app for
iPhone, iPad, Mac and Apple TV, a native Android app, and optional
Windows and smart-TV apps, all sharing one data plane and one set of
rules. And it is the method, written down where your AI agent will
read it.

## Why it exists

I want to build software that makes folks more capable, not more
passive. I want it to feel at home on every device they own, and still
open on the old one in the drawer. And I want to build it with an AI
agent without handing the agent the parts that were supposed to be
mine, or theirs.

I call that *human-shaped software*. Some problems are computer-shaped:
you can hand them to the agent and be done. Learning, community and
relationships are not, because they only happen when a person does the
work. Human-shaped software takes the mechanical work off people's hands
and leaves them the learning.

**Learning is the frame for all of it.**

It runs three ways. As a student, you learn a way of building, one stage
at a time, by bringing your work back and showing it. As a builder, you
learn what your app is by deciding, judging and using, which are the
parts the agent should never do for you. And as a human, you decide at
every step what to hand to the machine and what to keep. The app should
leave the people who use it more capable, and building it should leave
you more capable too.

Every round of every stage makes the same three moves:

1. **Write.** Values, features, feedback, and reasons go where the agent
   reads them, because an agent keeps only the values you write down.
2. **Play.** Use what came back, on a real device, and probe it. The
   agent is never the tester, and playing is how your thinking becomes
   something you can hold.
3. **Publish.** Release it so other people can play with it too. A
   human-shaped problem is rarely yours alone, and the people who use
   what you publish tell you what to write next.

Those moves shaped every choice in the template:

- **Values come first, in writing.** Every feature answers four
  questions before it is built: does it deepen understanding, invite
  participation, support agency, and stay clear rather than clever.
- **Feature parity, not design consistency.** The verbs are the same on
  every platform. The idioms are each platform's own.
- **Native apps over one shared data plane.** The data is built once and
  published. Each platform is a native consumer of it.
- **A low floor and a high ceiling.** An app should open on old
  hardware, and the newest devices should get everything they can do.

I am teaching a class on building human-shaped software with AI from
this template. The same path serves a class and a builder working alone.
`docs/research/values-based-approaches.md` sets it beside other
values-based ways of building, and says what it borrowed from each.

## Start here

The method is nine stages, in `docs/path/`. Each one says what you will
make, why it is built that way, what to do, and what to bring back.

| Stage | What you will do |
|---|---|
| [Getting set up](docs/path/setup.md) | A GitHub account, your own copy, an agent, and your app's address on your phone. |
| [00. Why we build](docs/path/00-why-we-build.md) | Write down your values where the agent will read them. |
| [01. The first prototype](docs/path/01-first-prototype.md) | One platform, real data, on a phone, this week. |
| [02. The shape of an app](docs/path/02-shape-of-an-app.md) | One data plane, native apps, and `PARITY.md`. |
| [03. Going native](docs/path/03-going-native.md) | Add Apple and Android, and choose your floors by the hardware they reach. |
| [04. Seeing it work](docs/path/04-seeing-it-work.md) | Real devices, honest instruments, and leaving the room as you found it. |
| [05. Shipping](docs/path/05-shipping.md) | Every store from the command line. |
| [06. Keeping it running](docs/path/06-keeping-it-running.md) | Pulse, the CI fleet, and loops. |
| [07. Raising the ceiling](docs/path/07-raising-the-ceiling.md) | New features on the newest devices, without raising the floor. |
| [08. Working with AI](docs/path/08-working-with-ai.md) | Make the repository remember, so the agent can. |

Keep [Talking to your agent](docs/path/talking-to-your-agent.md) open
the whole way through. It is the set of moves I actually use, in the
words I actually typed, and every stage points back to it. When a stage
asks you to be ready to show something, [Showing your
work](docs/path/showing-your-work.md) says how to get feedback on it,
in a cohort or on your own.

Teaching with it? [`COURSE.md`](COURSE.md) maps the stages to weeks,
and [`docs/teaching/`](docs/teaching/README.md) has a guide for each
live session.

<!-- Written by Claude, awaiting Ben's review (H3). -->
## The community

[humanshaped.org](https://humanshaped.org) is where people building
human-shaped software find one another. It runs the free cohorts, and
you do not need one to use it. Its [apps page](https://humanshaped.org/apps/)
follows apps in progress, including yours if you choose to show it, and
[events](https://humanshaped.org/events/) lists meetups and hackathons
you can join or start. The conversation happens in
[Discussions](https://github.com/orgs/humanshaped/discussions), and
[Connect your agent](https://humanshaped.org/connect/) shows how to let
your own Claude or Gemini read your work there, read-only, so its review
starts from your app.

## Using it for your app

1. Click **Use this template** on GitHub to make your own copy.
2. Open it with the agent you bring. I build with Claude Code, and on
   Google's side the route for now is Antigravity, which may change, or
   Gemini CLI with a paid Gemini API key. I do not recommend OpenAI's
   agents, though any agent that reads `AGENTS.md` can follow along.
   That file gives the agent the rules and the skill table, so it
   already knows how this template builds. (`CLAUDE.md` and `GEMINI.md`
   both import it, and it stays under the 24,000 bytes Antigravity
   reads.) [Getting set up](docs/path/setup.md) says what each one costs.
3. Tell it why your app exists (stage 00), then what you want and where
   the truth lives (stage 01). It will build the first version and put
   it live at an address you can open on your phone.

Everything else waits until you need it. `docs/path/talking-to-your-agent.md`
is the one page to keep open while you work.

## What is in the box

| Where | What it is |
|---|---|
| `AGENTS.md` | The agent's instructions: who the app is for, the rules, which skill to use when. `CLAUDE.md` and `GEMINI.md` both import it, so every agent reads the same file. |
| `SCRATCHPAD.md`, `DECISIONS.md`, `PARITY.md`, `DEEP_LINKS.md` | The project's memory: current state, the reasons behind choices, what exists on which platform, and the link contract. |
| `docs/path/` | The nine stages, and two companions: talking to your agent, and showing your work. |
| `COURSE.md`, `docs/teaching/` | The five-week cohort built on the stages, and a one-page guide for each of its live sessions. |
| `docs/` | The reference docs each stage points to. Map: [`docs/README.md`](docs/README.md). |
| `.claude/skills/` | 147 skills, 57 of them written from shipped apps. Catalog: [`.claude/skills/README.md`](.claude/skills/README.md). |
| `tools/` | Device testing, store submission, CI and Pulse tooling. Catalog: [`tools/README.md`](tools/README.md). |
| `index.html`, `css/`, `js/` | The web app: plain HTML, CSS and JavaScript, no build step. |
| `apple/` | Swift starter for one universal Xcode target (iPhone, iPad, Mac, Apple TV). See `apple/README.md`. |
| `android/` | Kotlin and Jetpack Compose starter. See `android/README.md`. |
| `windows/` | Optional Avalonia starter, built and tested entirely in CI. See `windows/README.md`. |
| `tv.js`, `tv.css`, `tv/`, `cast/` | The smart-TV layer over the web app (LG, Samsung) and a Google Cast receiver. |
| `pulse/` | The product-health dashboard. |
| `.github/workflows/` | Cloud builds and store submission, plus guardian workflows that ship switched off. |

Every starter compiles out of the box, and every starter opens straight to
a screen through debug-only launch doors, so testing and store
screenshots work from day one.

## Where this came from

This is the sixth generation of a template I started for BOBA Playbook, and each app since has folded its lessons
back in:

- **BOBA Playbook** gave it the parity matrix, the design-doc
  discipline, the four questions, and a set of lessons about data,
  images, and marketplaces.
- **Bsky Dreams** gave it values-based feed ranking, reader mode, and
  the share extension.
- **Tidbits Trivia** gave it cross-platform multiplayer, determinism
  across languages, Windows from a Mac, and the first device fleet.
- **Archive Watch** gave it most of the rest: the shared data plane,
  the Apple TV and smart-TV platforms, real-device testing, cloud store
  submission, the CI fleet, Pulse, and the floor-by-hardware rule.

`docs/PROVENANCE.md` records where each lesson came from.

## Contributing

`CONTRIBUTING.md` has the rules for changes to the template itself. The
short version: update `PARITY.md` with every user-facing change, lead
decisions with why, and write prose the way `docs/maintaining/WRITING.md`
describes.

MIT licensed.

Start with stage 00. It is the part most worth keeping.

</details>
