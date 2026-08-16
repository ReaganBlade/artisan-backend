def main() -> None:
    """Console entrypoint: run the FastAPI app with uvicorn.

    uvicorn 0.52+ hard-codes the ProactorEventLoop on Windows, which psycopg's
    async driver refuses to run on. ``core.loops`` provides a selector-based
    loop factory for uvicorn to use instead (see core/loops.py).
    """
    import uvicorn

    uvicorn.run(
        "personalization_service.main:app",
        host="127.0.0.1",
        port=8006,
        loop="personalization_service.core.loops:selector_loop_factory",
    )
