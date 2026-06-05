# PROJECT_ARCHITECTURE.md

## Purpose

This file documents the development, source-control, deployment, and hosting architecture for JobGarden.

It is intended to be referenced from `AGENTS.md`.

Agents should read this file before making infrastructure, deployment, credential, GitHub, or portfolio-site changes.

---

## Public Portfolio Site

The public portfolio page for this project will live at:

```text
https://lozknowles.com
```

This site is hosted by the user on `cottageserver`.

The portfolio page may eventually showcase:

* selected public CV/profile material
* project work
* application-support tooling
* selected public examples
* links to relevant projects

Private job applications, personal profile notes, tracker data, generated CVs, and statements of interest must not be published without explicit approval.

---

## Machine Roles

### Dell XPS 13 9310

Role:

* Windows development machine
* Codex Desktop / browser-based working environment
* GitHub coordination
* project planning and review

Known user:

```text
lozkn
```

The Dell 9310 may connect to `hpubuntu`, GitHub, and `cottageserver` by SSH, but it is not the live server.

---

### hpubuntu

Role:

* main Ubuntu development workstation
* local repository host
* heavier AI/dev work
* staging and build environment before deployment

Known user:

```text
loz
```

Likely project path:

```bash
/fast/repos/JobGarden
```

Use `hpubuntu` for:

* repo editing
* local testing
* document generation
* preparing commits
* pushing to GitHub
* preparing deployments to `cottageserver`

---

### GitHub

Role:

* remote source control
* durable project history
* backup and handoff point between machines and chat sessions

GitHub rules:

* make small working commits
* use clear commit messages
* push only intentional changes
* never commit secrets
* keep generated/private files out of Git where appropriate

Recommended private or ignored patterns:

```text
.env
.env.*
*.key
*.pem
*.ppk
id_ed25519*
credentials/
secrets/
private/
outputs/private/
```

---

### cottageserver

Role:

* live environment
* Apache web host
* public hosting for `lozknowles.com`
* possible future host for a public JobGarden portfolio page

Known details:

```text
Host alias: cottageserver
SSH port: 2222
Web server: Apache
Primary portfolio domain: lozknowles.com
```

Existing live domains may include:

```text
collingham.org
lozknowles.com
```

`cottageserver` is the live environment. Do not deploy to it unless explicitly requested.

---

## Default Development Flow

The default project flow is:

```text
Dell XPS 13 9310 / Codex
        ↓
hpubuntu development repo
        ↓
GitHub remote
        ↓
cottageserver live web host
        ↓
lozknowles.com public portfolio page
```

Agents should preserve this flow unless the user explicitly requests otherwise.

---

## Deployment Rules

Before deploying to `cottageserver`:

1. Check `git status`.
2. Confirm the current branch.
3. Build or test locally.
4. Confirm which files are public.
5. Exclude private profile data, application drafts, trackers, credentials, and generated private documents.
6. Back up any live files being replaced.
7. Deploy only the intended static/public files.
8. Verify the public URL afterwards.

---

## SSH and Credentials Policy

Never store secrets directly in this repository.

Allowed documentation examples:

```bash
ssh cottageserver
ssh -p 2222 cottageserver
```

Allowed credential path references:

```text
~/.ssh/config
~/.ssh/id_ed25519_cottage
~/.ssh/id_ed25519_cottage.pub
.env.example
```

Never include:

* private key contents
* SSH passphrases
* API keys
* passwords
* real `.env` values
* GitHub tokens
* server sudo passwords

Use placeholders only:

```env
GITHUB_TOKEN=replace_me
OPENAI_API_KEY=replace_me
SERVER_HOST=cottageserver
SERVER_PORT=2222
DEPLOY_PATH=/var/www/lozknowles.com
```

---

## Agent Behaviour

When infrastructure is involved, agents should:

1. Read `AGENTS.md`.
2. Read this file.
3. Avoid making assumptions about live paths.
4. Ask for confirmation before deploying.
5. Never expose or commit credentials.
6. Update `NEXT_STEPS.md` after changes.
7. Update `DECISIONS.md` if a durable architecture decision changes.
