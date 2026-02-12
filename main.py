import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from config import settings
from logging_config import setup_logging
from request_context import request_id_var
from routers.health import router as health_router
from routers.drivers import router as drivers_router
from routers.trucks import router as trucks_router


logger = setup_logging()

app = FastAPI(title=settings.app_name)


# -------------------------
# Middleware: Request IDs + timing + logging
# -------------------------
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    incoming = request.headers.get("x-request-id")
    req_id = incoming.strip() if incoming else str(uuid.uuid4())

    token = request_id_var.set(req_id)
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        # Let exception handlers format response; still log here
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "request_failed method=%s path=%s duration_ms=%s",
            request.method,
            request.url.path,
            duration_ms,
        )
        request_id_var.reset(token)
        raise exc

    duration_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Request-ID"] = req_id

    logger.info(
        "request_complete method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    request_id_var.reset(token)
    return response


# -------------------------
# Error handlers: include request_id in body + header
# -------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = request.headers.get("x-request-id") or request_id_var.get() or ""
    return JSONResponse(
        status_code=422,
        content={
            "request_id": req_id,
            "error": {
                "code": "validation_error",
                "message": "Validation failed",
                "details": exc.errors(),
            },
        },
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    req_id = request.headers.get("x-request-id") or request_id_var.get() or ""
    return JSONResponse(
        status_code=500,
        content={
            "request_id": req_id,
            "error": {
                "code": "internal_server_error",
                "message": "Unexpected error",
            },
        },
        headers={"X-Request-ID": req_id},
    )


# -------------------------
# Routers
# -------------------------
app.include_router(health_router)
app.include_router(drivers_router)
app.include_router(trucks_router)