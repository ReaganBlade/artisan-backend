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
