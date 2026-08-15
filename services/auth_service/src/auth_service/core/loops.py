import asyncio
import sys


def selector_loop_factory(use_subprocess: bool = False) -> asyncio.AbstractEventLoop:
    """Uvicorn custom-loop entry point that returns a selector-based loop.

    uvicorn 0.52+ hard-codes ``asyncio.ProactorEventLoop`` on Windows, which
    psycopg's async driver refuses to run on. When ``loop`` is set to an
    import path (``--loop auth_service.core.loops:selector_loop_factory``),
    uvicorn treats the callable as asyncio's ``loop_factory``: it calls it
    with no arguments and uses the result as the event loop.
    """
    del use_subprocess  # selector loop is used unconditionally
    if sys.platform == "win32":
        # SelectorEventLoop requires an explicit SelectSelector on Windows.
        import selectors

        return asyncio.SelectorEventLoop(selectors.SelectSelector())
    return asyncio.SelectorEventLoop()
