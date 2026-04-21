# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Product

An LLM leaderboard service. The backend catalogs AI language model providers and their models (pricing, context window, arena ELO, release metadata) and exposes them over a JSON API. The frontend renders a browsable list and per-model detail views.

## Running the stack

The canonical workflow is Docker Compose, which brings up three services: `db` (Postgres 16), `backend` (Django 5 + DRF on :8000), and `frontend` (Vite + React 19 on :5173). The frontend waits on the backend's `/api/health/` healthcheck before starting.

```bash
docker compose up
```

The backend `entrypoint.sh` runs migrations and the `seed` management command on every container start. The seed command is idempotent (`get_or_create`), so restarting the stack is always safe.

Bare-metal instructions are in `SETUP_LOCAL.md`. Note that `frontend/vite.config.ts` proxies `/api` to `http://backend:8000` (the Docker service name) — for non-Docker development, change the proxy target to `http://localhost:8000`.

## Common commands

Run commands inside the relevant container:

- Backend tests: `docker compose exec backend pytest`
- Single backend test: `docker compose exec backend pytest app/tests.py::LLMModelListViewTest::test_list_returns_200_with_models`
- Django management: `docker compose exec backend python manage.py <createsuperuser|makemigrations|migrate|shell|seed>`
- Frontend tests: `docker compose exec frontend npm test` (one-shot) or `npm run test:watch`
- Frontend build / typecheck: `docker compose exec frontend npm run build` (runs `tsc -b && vite build`)

After creating a **new** Python file (e.g. `admin.py`), Django's autoreloader on WSL2 + Docker volume mounts sometimes misses it. If changes don't appear, run `docker compose restart backend`.

## Architecture

### Backend (`backend/`)

Django project package is `config/` (settings, root urls, wsgi). All domain code lives in a single Django app named `app`, wired into `/api/` via `config/urls.py` → `app/urls.py`.

Current domain models (`app/models.py`):
- `Provider` — name (unique), website.
- `LLMModel` — FK to `Provider`, name, description, context window, input/output pricing (DecimalField), arena ELO, release date, open-source flag. Default ordering is `-arena_elo_score`; `unique_together = (provider, name)`.

Views (`app/views.py`) are DRF generic CBVs (`ListAPIView`, `RetrieveAPIView`, `CreateAPIView`). Two serializers exist by design:
- `LLMModelListSerializer` — trimmed payload for list responses (omits `description`).
- `LLMModelSerializer` — full detail; writes accept `provider_id`, reads nest the full `provider` object.

`DEFAULT_PERMISSION_CLASSES` is `AllowAny` — the public API is unauthenticated. Django admin at `/admin/` uses the standard staff login.

The database layer falls back to SQLite when `POSTGRES_DB` is unset. Under Docker, Postgres env vars are always set, so the `backend/db.sqlite3` file is ignored. Be aware of the fallback if you ever invoke `manage.py` outside the container without those env vars.

Tests are in `backend/app/tests.py` (pytest-django; `DJANGO_SETTINGS_MODULE=config.settings`), mixing Django's `TestCase` with direct `pytest.raises`.

### Frontend (`frontend/src/`)

React 19, React Router v7, TanStack Query, Tailwind, shadcn/ui, axios. Path alias `@/` → `src/`.

- `App.tsx` instantiates the `QueryClient` (30s `staleTime`, 1 retry) and mounts routes under a single `Layout` outlet.
- `pages/` — route components (`ModelsList`, `ModelDetail`).
- `hooks/` — TanStack Query wrappers (`useModels`, `useModel`) over `api/client.ts`.
- `types/index.ts` mirrors the API shape — keep it in sync when serializers change.
- Both Tailwind and SCSS (`styles/_mixins.scss`, `styles/_variables.scss`, `styles/globals.css`) are wired up; use either.

Axios has no base URL — relative paths flow through the Vite proxy. Backend CORS only allows `http://localhost:5173`.

## Project conventions

These are enforced standards, not suggestions. Apply them to every change you make.

### Git commits

Every logical change gets its own commit. Follow the Chris Beams standard (https://cbea.ms/git-commit/):
- Subject line ≤50 characters, capitalized, imperative mood, no trailing period.
- Blank line between subject and body.
- Body wrapped at 72 columns, explaining **what** and **why** (not how).

**Do not include a `Co-Authored-By: Claude` trailer or any Claude attribution** in commit messages on this repository.

**Every commit must be explicitly approved by the user before it is created.** Draft the full commit message (subject and body) and present it for review first. Do not run `git commit` until the user gives the go-ahead. This applies to every commit, including follow-ups and amendments — prior approval does not carry forward.

### Testing

Every new behavior ships with a test. Extend `backend/app/tests.py` for backend changes and colocate `*.test.tsx` files next to components for frontend changes. If a change legitimately does not need a test (e.g. a pure config tweak), say so explicitly rather than omitting silently.

### API design

New and modified REST endpoints follow a canonical noun-resource pattern:
- Plural resource nouns: `/api/models/`, `/api/benchmarks/`, `/api/benchmarks/:id/results/`.
- No verb endpoints. `POST /api/models/` creates a model — not `/api/models/create/`.
- Use HTTP methods semantically (GET / POST / PATCH / PUT / DELETE) and return appropriate status codes.
- Nest resources where the hierarchy is real; prefer filters/query params otherwise.

### Architecture artifacts

The `architecture/` directory is the source of truth for two visualizations of
the backend:

- `architecture/ERD.md` — mermaid ERD of the current data model.
- `architecture/openapi.yaml` — OpenAPI 3 spec generated by drf-spectacular.

These files are **not** generated at runtime; they are committed and must be
refreshed as part of any change that touches the data model or the API
surface. For every PR that modifies `backend/app/models.py`, serializers,
views, URL routes, or DRF schema annotations:

1. Update `architecture/ERD.md` to reflect the new tables, fields, FKs, and
   indexes.
2. Regenerate `architecture/openapi.yaml` via
   `docker compose exec backend python manage.py spectacular --file /tmp/openapi.yaml --validate`
   and copy it out with
   `docker compose cp backend:/tmp/openapi.yaml architecture/openapi.yaml`.

The live spec and a Swagger UI are also exposed by the running backend, but
restricted to authenticated staff users:

- `GET /api/schema/` — raw OpenAPI YAML (admin only).
- `GET /api/schema/swagger-ui/` — Swagger UI (admin only).

Log in via `/admin/` first; both endpoints return 403 without a staff session.

### Data modeling

New tables and fields are **normalized** and **designed for scale**:
- No duplicated data across tables — use foreign keys and through-tables.
- Add indexes on fields used for filtering, ordering, or joining at query time, not "later."
- For growth-prone data (e.g. historical run tables), think about query patterns and retention up front. The leaderboard and per-model-summary views are read-heavy — index accordingly.
