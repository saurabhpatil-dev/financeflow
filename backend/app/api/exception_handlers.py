"""Translate application exceptions into JSON HTTP responses."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _error_response(status_code: int, detail: str, error_code: str, **extra: Any) -> JSONResponse:
    payload: Dict[str, Any] = {
        "error": error_code,
        "detail": detail,
    }
    if extra:
        payload.update(extra)
    return JSONResponse(status_code=status_code, content=payload)


def _sanitize_errors(errors: List[Any]) -> List[Dict[str, Any]]:
    """Make Pydantic validation errors JSON-serializable."""
    safe: List[Dict[str, Any]] = []
    for err in errors:
        if not isinstance(err, dict):
            continue
        item: Dict[str, Any] = {}
        for key, value in err.items():
            if key == "ctx" and isinstance(value, dict):
                item[key] = {
                    ctx_key: (
                        str(ctx_val)
                        if not isinstance(ctx_val, (str, int, float, bool, type(None)))
                        else ctx_val
                    )
                    for ctx_key, ctx_val in value.items()
                }
            elif isinstance(value, (str, int, float, bool, type(None))):
                item[key] = value
            else:
                item[key] = str(value)
        safe.append(item)
    return safe


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers for known app exceptions + FastAPI validation errors."""

    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.status_code, exc.detail, exc.error_code)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            status_code=422,
            detail="Validation failed",
            error_code="validation_error",
            fields=_sanitize_errors(exc.errors()),
        )
