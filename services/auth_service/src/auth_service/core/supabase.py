from functools import lru_cache

from supabase import Client, create_client

from .config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return a cached Supabase client bound to the configured project.

    The client is created lazily on first use, so importing the package or
    starting the FastAPI app never requires Supabase to be configured.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in the auth_service "
            ".env to use the Supabase client."
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
