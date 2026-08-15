import asyncio
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# psycopg's async driver can't run on Windows' default ProactorEventLoop.
# Force the selector-based loop so DB-backed tests work on Windows.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import auth_service.models  # noqa: F401  (register all models on Base.metadata)
from auth_service.db.base import SCHEMA, Base
from auth_service.db.session import get_db
from auth_service.main import app

# Point at a local Postgres for tests. Override via TEST_DATABASE_URL when needed.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/artisan",
)


def _run(coro):
    """Run an async coroutine to completion in a fresh event loop."""
    return asyncio.run(coro)


async def _init_schema(engine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}'))
        await conn.run_sync(Base.metadata.create_all)


async def _drop_schema(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text(f'DROP SCHEMA IF EXISTS {SCHEMA} CASCADE'))


async def _clean_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                f"TRUNCATE TABLE {SCHEMA}.refresh_tokens, {SCHEMA}.users RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture(scope="session")
def db_engine():
    """Engine against the test database; skips the whole session when unreachable."""
    engine = create_async_engine(TEST_DATABASE_URL)
    try:
        _run(_init_schema(engine))
    except Exception as exc:  # noqa: BLE001 — any connection failure => skip
        pytest.skip(
            f"Postgres unreachable at {TEST_DATABASE_URL} ({exc}). "
            "DB-backed tests skipped — start a local Postgres or set TEST_DATABASE_URL."
        )
    yield engine
    _run(_drop_schema(engine))
    _run(engine.dispose())


@pytest.fixture()
def _clean_tables_between_tests(db_engine):
    """Empty users + refresh_tokens before each test for isolation.

    Applied via pytestmark in the DB-backed test modules only, so the
    pure unit tests keep running without a database.
    """
    _run(_clean_tables(db_engine))
    yield


@pytest.fixture()
def session_factory(db_engine):
    return async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture()
def run_async(session_factory):
    """Return a callable that runs `async fn(db)` in a fresh session + loop."""

    def _run_with_session(fn):
        async def _inner():
            async with session_factory() as db:
                return await fn(db)

        return _run(_inner())

    return _run_with_session


@pytest.fixture()
def client(db_engine):
    """TestClient with get_db overridden to use the test database."""
    factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
