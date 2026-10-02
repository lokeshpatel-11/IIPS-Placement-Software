# IIPS PlaceIQ

**Placement Management & Employability Analytics System** for IIPS.

PlaceIQ replaces Excel sheets, Google Forms and WhatsApp groups with one system for the whole placement process: student registration, company drives, interview tracking, offers, statistics, and (later) employability analytics.

> Status: **Phase 1 (MVP) in progress.** Foundation (Docker, backend skeleton, first migration) is done.

---

## Table of Contents

1. [Tech stack](#1-tech-stack)
2. [Project structure](#2-project-structure)
3. [Getting started (first-time setup)](#3-getting-started-first-time-setup)
4. [Daily development workflow](#4-daily-development-workflow)
5. [Useful commands](#5-useful-commands)
6. [Database and migrations](#6-database-and-migrations)
7. [Backend guide (FastAPI)](#7-backend-guide-fastapi)
8. [Frontend guide (React)](#8-frontend-guide-react)
9. [Testing](#9-testing)
10. [Git workflow](#10-git-workflow)
11. [Code review rules](#11-code-review-rules)
12. [Definition of Done](#12-definition-of-done)
13. [Team roles and ownership](#13-team-roles-and-ownership)
14. [Roadmap (phases)](#14-roadmap-phases)
15. [Troubleshooting](#15-troubleshooting)
16. [Documentation](#16-documentation)
17. [Security rules](#17-security-rules)

---

## 1. Tech stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite) + TypeScript + Tailwind CSS (+ shadcn/ui, Recharts, TanStack Query) |
| Backend | FastAPI (Python 3.12) + Pydantic |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic (migrations) |
| Auth | JWT with role-based access (Student / Admin / Super Admin) |
| Background jobs | Celery + Redis *(Phase 2)* |
| Automation | n8n *(Phase 2)* |
| AI / ML | scikit-learn + LLM API *(Phase 3)* |
| DevOps | Docker Compose, GitHub Actions |
| Code quality | Ruff, pytest, ESLint, Prettier, pre-commit |

**Golden rule:** all important logic (eligibility, placement policy, status transitions, permissions) lives in the **FastAPI backend**. The frontend only displays and collects data. n8n only sends messages. The backend must stay correct even if the frontend or n8n misbehaves.

---

## 2. Project structure

```
IIPS-Placement-Software/
├─ backend/
│  ├─ app/
│  │  ├─ api/v1/          # API routers (thin: parse request, call a service)
│  │  ├─ core/            # config, database connection, security
│  │  ├─ models/          # SQLAlchemy models (database tables)
│  │  ├─ schemas/         # Pydantic models (request/response shapes)
│  │  ├─ services/        # business logic: eligibility, policy, rules  <- most important
│  │  ├─ tasks/           # background jobs (Phase 2)
│  │  └─ main.py          # FastAPI app entry point
│  ├─ alembic/            # database migrations
│  ├─ tests/              # pytest tests
│  ├─ alembic.ini
│  ├─ pyproject.toml      # Ruff + pytest config
│  ├─ requirements.txt
│  ├─ requirements-dev.txt
│  └─ Dockerfile
├─ frontend/
│  └─ src/
│     ├─ pages/           # route-level screens
│     ├─ components/      # shared UI components
│     ├─ features/        # feature folders (drives, applications, ...)
│     ├─ api/             # API client and calls
│     ├─ hooks/           # custom hooks
│     └─ lib/             # utilities
├─ automation/            # n8n workflow exports (Phase 2)
├─ docs/                  # SRS, ER diagram, business rules, API notes
├─ .github/               # CI workflow, PR and issue templates, CODEOWNERS
├─ docker-compose.yml
├─ .env.example           # template for your local .env
└─ README.md
```

**How a request flows:** React page → API call → FastAPI router → service (rules) → SQLAlchemy model → PostgreSQL.

---

## 3. Getting started (first-time setup)

### 3.1 Prerequisites

Install these on your machine:

| Tool | Version | Notes |
|---|---|---|
| Git | any recent | |
| Docker + Docker Compose | recent | Linux: add yourself to the docker group (below) |
| VS Code (recommended) | | Extensions: Python, Ruff, ESLint, Prettier, Docker |
| Node.js | 20 LTS | Only needed if you run frontend commands outside Docker |
| Python | 3.12 | Only needed for pre-commit and local tooling |

**Linux only:** let your user run Docker without `sudo`, then log out and back in:

```bash
sudo usermod -aG docker $USER
```

### 3.2 Clone the repo

```bash
git clone https://github.com/sudobhavik/IIPS-Placement-Software.git
cd IIPS-Placement-Software
git checkout dev
```

### 3.3 Create your `.env`

```bash
cp .env.example .env
```

Open `.env` and set your own values. They are **not** copied from anywhere. You choose them:

| Variable | What to put |
|---|---|
| `POSTGRES_USER` | Any name, e.g. `placeiq` |
| `POSTGRES_PASSWORD` | Any password (letters and numbers only for now) |
| `POSTGRES_DB` | Any name, e.g. `placeiq` |
| `DATABASE_URL` | `postgresql+psycopg://USER:PASSWORD@db:5432/DBNAME` using the three values above |
| `SECRET_KEY` | Generate with `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `FRONTEND_ORIGIN` | `http://localhost:5173` |

Rules:
- `.env` is **never committed**. Only `.env.example` (with fake values) is committed.
- The user and password must match inside `DATABASE_URL`. The host is `db` (the Docker service name), not `localhost`.
- Postgres sets its password only the first time the database volume is created. If you change credentials later, reset with `docker compose down -v`.

### 3.4 Start the project

```bash
docker compose up -d --build
docker compose ps
```

You should see `db` (healthy), `backend` and `frontend` running. The first run takes a few minutes.

### 3.5 Apply database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 3.6 Check that everything works

| Check | URL / command | Expected |
|---|---|---|
| API health | `curl http://localhost:8000/api/v1/health` | `{"status":"ok","database":"connected"}` |
| API docs (Swagger) | http://localhost:8000/docs | Interactive API docs |
| Frontend | http://localhost:5173 | "PlaceIQ: API ok, DB connected" |
| Tests | `docker compose exec backend pytest` | All tests pass |

### 3.7 Install pre-commit hooks (once per machine)

```bash
pipx install pre-commit      # or: pip install --user pre-commit
pre-commit install
```

This runs lint and secret checks automatically before every commit.

### Ports used

| Service | Host port | Notes |
|---|---|---|
| Frontend | 5173 | |
| Backend API | 8000 | |
| PostgreSQL | 5433 | Mapped to 5433 on your machine to avoid clashing with a local Postgres. Inside Docker the backend still uses `db:5432`. |

---

## 4. Daily development workflow

```bash
# 1. Start your day: update dev
git checkout dev
git pull

# 2. Create a branch for your task
git checkout -b feature/<area>-<short-name>     # e.g. feature/drives-eligibility

# 3. Start the stack (if not already running)
docker compose up -d

# 4. Code, test, lint (see commands below)

# 5. Commit often with clear messages
git add .
git commit -m "feat(drives): add eligibility filter"

# 6. Push and open a Pull Request into dev
git push -u origin feature/<area>-<short-name>
```

Rules of thumb:
- One task = one branch = one small PR.
- Pull `dev` at least once a day to avoid big merge conflicts.
- Never work directly on `main` or `dev`.
- Never edit the same file as a teammate at the same time without telling them.

---

## 5. Useful commands

### Docker
```bash
docker compose up -d                  # start everything in the background
docker compose up -d --build          # rebuild images and start
docker compose ps                     # see what's running
docker compose logs -f backend        # follow backend logs
docker compose logs -f frontend       # follow frontend logs
docker compose restart backend        # restart one service
docker compose down                   # stop everything (keeps data)
docker compose down -v                # stop and DELETE local database data
```

### Backend
```bash
docker compose exec backend pytest                    # run tests
docker compose exec backend ruff check . --fix        # lint (auto-fix)
docker compose exec backend ruff format .             # format code
docker compose exec backend bash                      # shell inside container
```

### Database
```bash
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB>      # open psql
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "\dt"   # list tables
```
Optional GUI tools (DBeaver, TablePlus): host `localhost`, port `5433`, with the credentials from your `.env`.

### Frontend
```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
docker compose exec frontend npm install <package>    # add a dependency
```

---

## 6. Database and migrations

We use **Alembic**. **Never change the database by hand**, and never edit a migration that is already merged.

**When you change a model:**

```bash
# 1. Edit or add the model in backend/app/models/
# 2. Make sure it is imported in backend/app/models/__init__.py
# 3. Generate a migration
docker compose exec backend alembic revision --autogenerate -m "short description"
# 4. READ the generated file in backend/alembic/versions/ and check it is correct
# 5. Apply it
docker compose exec backend alembic upgrade head
# 6. Commit the model AND the migration file together
```

Other useful commands:
```bash
docker compose exec backend alembic current          # which version is applied
docker compose exec backend alembic history          # list migrations
docker compose exec backend alembic downgrade -1     # undo the last migration (local only)
```

**Two people changed the schema at once?** Alembic can end up with two "heads". Pull `dev`, delete your unmerged migration file, and regenerate it on top of the latest `dev`.

**After pulling teammates' changes, always run** `alembic upgrade head`.

---

## 7. Backend guide (FastAPI)

### Layers (keep them separate)

| Layer | Folder | Responsibility |
|---|---|---|
| Router | `api/v1/` | Receive request, check permissions, call a service, return response. **No business logic.** |
| Service | `services/` | Business rules (eligibility, policy, status transitions). Pure and easy to unit test. |
| Model | `models/` | Database tables only |
| Schema | `schemas/` | Pydantic request/response shapes. Never return password hashes or internal fields. |

### Conventions
- API is versioned under `/api/v1/`.
- Use proper HTTP codes: `401` not logged in, `403` not allowed, `404` not found, `422` invalid input.
- All list endpoints support **pagination, sorting and filtering**.
- Permissions are enforced **in the backend**, using a role dependency (for example `require_role("admin")`) plus object-level checks (a student can only read their own data).
- Store time in **UTC**; the UI shows IST.
- Application status changes go through **one** function that validates allowed transitions.
- Sensitive changes must write to the **audit log**.
- Business rules (tiers, thresholds, policy) live in **settings tables**, not hard-coded.
- Add type hints everywhere.

### Adding a new endpoint (checklist)
1. Model and migration (if new data)
2. Pydantic schemas (create / read)
3. Service function with the logic
4. Router that calls the service
5. Permission check
6. Tests (success, validation error, permission denied)

---

## 8. Frontend guide (React)

- Organize by **feature** (`features/drives/`, `features/applications/`), not by file type.
- Server data: **TanStack Query**. Forms: **React Hook Form + Zod**. Routing: **React Router** with role-protected routes.
- Reuse the shared components in `components/` (Button, Table, Modal, form fields). Don't make one-off copies.
- Every screen must handle **loading, empty and error** states.
- **Mobile-first**: students will use phones. Test at 360px width.
- Hiding a button is for convenience only. The backend is what actually enforces permissions.
- Prefer generating the API client types from FastAPI's OpenAPI schema (`/openapi.json`) so frontend and backend never disagree.
- Don't hard-code API URLs in many places. Keep them in `src/api/`.

---

## 9. Testing

| What | Tool | Where |
|---|---|---|
| Business logic (eligibility, policy, status rules) | pytest unit tests | `backend/tests/` |
| API endpoints incl. permissions | pytest + httpx | `backend/tests/` |
| Main user flows | Playwright *(from Phase 1 end)* | `e2e/` |

Priorities:
1. **Eligibility engine, policy rules and status transitions get the most tests.** This is the heart of the system.
2. Every endpoint needs at least: a success case, a bad-input case, and a permission-denied case.
3. New bugs get a test that reproduces them before the fix.

Run backend tests: `docker compose exec backend pytest`

---

## 10. Git workflow

### Branches

| Branch | Purpose |
|---|---|
| `main` | Always stable and demo-ready. Protected. Updated only from `dev` for milestones. |
| `dev` | Integration branch. Protected. All PRs merge here. |
| `feature/<area>-<name>` | New functionality, e.g. `feature/auth-login` |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Tooling, config, dependencies |
| `docs/<name>` | Documentation only |

### Commit messages (Conventional Commits)

```
feat(drives): add eligibility filter
fix(auth): handle expired refresh token
docs(srs): update phase 2 table
test(apps): add duplicate-application test
chore(ci): add frontend build step
refactor(students): split import service
```

Format: `type(scope): short description`, in the present tense, under about 70 characters.

### Pull requests
- Target branch: **`dev`**.
- Keep them small (under about 400 lines) and focused on one purpose.
- Fill in the PR template and link the issue (`Closes #12`).
- Attach a screenshot for UI changes.
- CI must be green and at least **1 teammate must approve**.
- Use **Squash and merge** to keep history clean.
- Delete the branch after merging.

### Issues and board
- Every task is a GitHub issue with a phase label (`P1`, `P2`, `P3`) and an area label (`backend`, `frontend`, `infra`, `docs`).
- Board columns: **Backlog → Ready → In Progress → In Review → Done**.
- Move your card yourself. Don't start a task that's not in *Ready*.
- New ideas go into the Backlog with a phase label. **Don't add them to the current phase without a team decision.**

---

## 11. Code review rules

**As an author:**
- Review your own diff first.
- Explain *why*, not just *what*, in the PR description.
- Respond to every comment (fix it, or explain).

**As a reviewer:**
- Review within 24 hours so nobody is blocked.
- Check: logic correct? Permissions enforced? Tests present? Migration included? Secrets absent? Naming clear?
- Be specific and kind. Suggest, don't command.
- Don't approve what you haven't read.

**Nobody merges their own PR without a review.**

---

## 12. Definition of Done

A task is **done** only when all of these are true:

- [ ] Merged through a reviewed pull request
- [ ] CI passes (lint, tests, build)
- [ ] Tests exist for the new logic
- [ ] Migration included if the schema changed
- [ ] Permissions checked for each role
- [ ] Works on mobile (for UI changes)
- [ ] Loading, empty and error states handled (for UI changes)
- [ ] Docs or README updated if setup or API changed

---

## 13. Team roles and ownership

> Replace the placeholders with your team's names and GitHub usernames.

| Role | Person | Owns |
|---|---|---|
| Backend / DB lead | `@username` | FastAPI, models, migrations, auth, eligibility and policy engine |
| Frontend lead | `@username` | React app, UI components, API integration |
| DevOps / QA / Docs lead | `@username` | Docker, CI, testing, n8n, deployment, documentation, project board |

Everyone should deliver at least one complete feature end to end (database → API → UI → tests), and should review PRs outside their own area at least once in a while so knowledge is shared.

**Weekly rhythm**
- **Monday (20 min):** planning. Choose tasks from the board.
- **Mid-week (async):** short chat update: done / doing / blocked.
- **Friday (15 min):** demo what works, then merge to `dev`.

---

## 14. Roadmap (phases)

### Phase 1: MVP (working system)
Login and roles, bulk student import (Excel/CSV), student profiles and admin verification, company management, drives with the eligibility engine, applications, round-wise interview tracking (with bulk result upload), offers, basic dashboard, in-app and email notifications, audit log.

### Phase 2: Practical polish
Placement policy engine, interview conflict detection, Excel/PDF reports, Faculty/HOD dashboard, n8n automations (alerts, reminders, calendar invites, Sheets backup), announcements, employability score, skill gap analysis, drive recommendations, risk flags, resume generation.

### Phase 3: Advanced (stretch)
LLM resume parsing, placement prediction (only if past data is available), company portal, QR attendance, alumni module, grievance tickets, WhatsApp alerts, 2FA / Google login, training tracking.

Full details: see `docs/` (SRS).

**Current focus:** Week 1 foundation → Week 2 auth + first end-to-end feature (student import).

---

## 15. Troubleshooting

| Problem | Fix |
|---|---|
| `permission denied ... docker.sock` | Run `sudo usermod -aG docker $USER`, then log out and back in. |
| `env file ... .env not found` | Create it: `cp .env.example .env` and fill in the values. |
| `port is already allocated / address already in use` | Another service uses the port. Change the **host** side in `docker-compose.yml` (for example `5433:5432`), or stop the other service. |
| `password authentication failed for user` | Database was created with different credentials. Make `.env` consistent, then `docker compose down -v` and `docker compose up -d --build`. **This deletes local DB data.** |
| `.env` changes not picked up | `docker compose down && docker compose up -d` (a plain restart isn't enough). |
| Backend: `No module named 'app'` | A folder is missing `__init__.py`, or `main.py` is in the wrong place. |
| Alembic doesn't detect my model | Import it in `app/models/__init__.py`; confirm `alembic/env.py` imports `app.models`. |
| Frontend shows "API unreachable" / CORS error | `FRONTEND_ORIGIN` in `.env` must exactly match the browser URL (`http://localhost:5173`). Recreate the backend: `docker compose up -d --force-recreate backend`. |
| Files created by Docker are owned by root | `sudo chown -R $USER:$USER .` from the repo root. |
| Frontend packages missing | `docker compose exec frontend npm install`. |
| Migration conflict ("multiple heads") | Pull `dev`, delete your unmerged migration, regenerate it. |
| Everything is broken and I want a clean slate | `docker compose down -v && docker compose up -d --build` then `alembic upgrade head`. |

Still stuck? Post in the team chat with: what you ran, the full error, and the output of `docker compose ps`.

---

## 16. Documentation

| Document | Location |
|---|---|
| Software Requirements Specification (detailed) | `docs/IIPS_PlaceIQ_SRS.md` |
| Simple SRS (phase-wise) | `docs/IIPS_PlaceIQ_SRS_Simple.md` |
| Business rules | `docs/business-rules.md` |
| ER diagram | `docs/er-diagram.png` |
| API docs | http://localhost:8000/docs (auto-generated) |

If you change behavior, update the matching document in the same PR.

---

## 17. Security rules

- **Never commit** `.env`, passwords, API keys or tokens. `pre-commit` has a private-key check, but don't rely on it alone.
- Never use dev secrets in production.
- Never return password hashes or internal fields in API responses.
- Validate all input with Pydantic schemas.
- Student data (marks, phone, documents) is personal data. Only expose it to roles that need it, as defined in the access matrix in the SRS.
- Report any suspected leak to the team immediately.

---

## License

MIT (or as decided by the team and college).
