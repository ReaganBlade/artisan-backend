# Artisan Backend

Monorepo for the Artisan platform's backend microservices, managed as a
[uv workspace](https://docs.astral.sh/uv/concepts/workspaces/).

| Service | Description | Schema |
| --- | --- | --- |
| `auth_service` | Identity & auth (JWT, refresh tokens) | `auth_schema` |
| `ai_discovery_service` | AI Discovery & semantic search (pgvector) | `ai_discovery_schema` |
| `commerce_service` | Commerce & cart (Stripe) | `commerce_schema` |
| `media_service` | Catalog & media (S3/Supabase Storage) | `media_schema` |
| `moderation_service` | Trust & moderation (Celery/Redis) | `moderation_schema` |
| `personalization_service` | Personalization engine | `personalization_schema` |

## Running the services

Each service is its own FastAPI app and runs on its own port during local
development (see each service's `src/<service>/__init__.py` entrypoint).
Interactive docs live at `http://localhost:<port>/docs`.

| Service | Port | API prefix |
| --- | --- | --- |
| `auth_service` | 8001 | `/api/v1` |
| `media_service` | 8002 | `/api/v1` |
| `commerce_service` | 8003 | `/api/v1` |
| `ai_discovery_service` | 8004 | `/api/v1` |
| `moderation_service` | 8005 | `/api/v1` |
| `personalization_service` | 8006 | `/api/v1` |

The frontend maps these URLs through its `.env` file (see
`artisan-frontend/.env.example`) — keep the ports in sync across both repos.

## API routes

`auth_service` ships a fully implemented auth API (`/auth/signup`, `/auth/signin`,
`/auth/refresh`, `/auth/logout`, `/auth/me`). Every other service exposes the
routes below as **dummy endpoints** returning deterministic mock data that
mirrors its SQLAlchemy models — swap the `dummy_` helpers for real repository
calls as each service is built out.

| Service | Dummy routes (under `/api/v1`) |
| --- | --- |
| `media_service` | `GET/POST /artworks`, `GET/PATCH/DELETE /artworks/{id}`, `GET/POST /artworks/{id}/media`, `GET/POST /profiles`, `GET/PATCH /profiles/{id}`, `GET /profiles/{id}/artworks` |
| `commerce_service` | `GET/DELETE /cart`, `POST /cart/items`, `PATCH/DELETE /cart/items/{id}`, `POST /checkout`, `GET /checkout/{session_id}`, `GET /orders`, `GET /orders/{id}`, `POST /webhooks/stripe` |
| `ai_discovery_service` | `GET /search`, `POST /search/vibe`, `POST /search/log`, `GET /artworks/{id}/similar` |
| `moderation_service` | `POST /artworks/{id}/moderation`, `GET /artworks/{id}/moderation`, `POST /artworks/{id}/signature`, `GET /artworks/{id}/signature`, `GET /moderation/flags`, `PATCH /moderation/flags/{id}` |
| `personalization_service` | `GET /feed`, `POST /interactions`, `GET /interactions/me` |

## Branching & Release Policy

> `main` is the single source of truth. **No release may be cut until all
> intended changes have been merged into `main`.**

- All feature, bugfix, and release-candidate work happens on **short-lived
  branches** (e.g. `feat/<name>`, `fix/<name>`, `release/<version>`).
- Branches are merged into `main` via **pull/merge request** — never by
  direct push to `main`.
- **Releases** (version bumps, tags, deployments) are created **only** from
  `main`, after all intended changes are merged and final QA passes.
- Tags and release artifacts must point at commits that are on `main`.

### Branch protection (recommended for the hosting platform)

Enable branch protection on `main` that requires:

- At least one approving pull-request review,
- Passing status checks,
- Up-to-date branches before merging, and
- Merges via PR only (no direct pushes).

### Release workflow (summary)

```text
feature/fix branch ──▶ PR ──▶ review + checks ──▶ merge into main
                                                        │
release/<version> ── cut from main ──▶ tag ──▶ deploy
```
