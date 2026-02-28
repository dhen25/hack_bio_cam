from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from coolsense.api.schemas import ErrorResponse


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def build_error(
    code: str,
    message: str,
    trace_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ErrorResponse(code=code, message=message, details=details or {}, trace_id=trace_id).model_dump()


def trace_id_for_request(request: Request) -> str:
    return getattr(request.state, "trace_id", str(uuid4()))


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    trace_id = trace_id_for_request(request)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error(exc.code, exc.message, trace_id, exc.details),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    trace_id = trace_id_for_request(request)
    return JSONResponse(
        status_code=422,
        content=build_error("VALIDATION_ERROR", "Request validation failed", trace_id, {"errors": exc.errors()}),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = trace_id_for_request(request)
    return JSONResponse(
        status_code=500,
        content=build_error("INTERNAL_ERROR", "Unexpected internal error", trace_id, {}),
    )


def unauthorized_http_exception(trace_id: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail=build_error("UNAUTHORIZED", "Missing or invalid API key", trace_id),
    )
