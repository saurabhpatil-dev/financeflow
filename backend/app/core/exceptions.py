"""Application-level exceptions used by the service layer.

These are translated to HTTP responses by the API exception handlers in
``app.api.exception_handlers``.
"""
from __future__ import annotations


class AppException(Exception):
    """Base class for application-level errors."""

    status_code: int = 400
    detail: str = "Application error"
    error_code: str = "app_error"

    def __init__(self, detail: str | None = None, error_code: str | None = None) -> None:
        self.detail = detail or self.__class__.detail
        self.error_code = error_code or self.__class__.error_code
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = 404
    detail = "Resource not found"
    error_code = "not_found"


class ConflictError(AppException):
    status_code = 409
    detail = "Conflict with existing resource"
    error_code = "conflict"


class ValidationError(AppException):
    status_code = 422
    detail = "Validation failed"
    error_code = "validation_error"


class AuthenticationError(AppException):
    status_code = 401
    detail = "Could not validate credentials"
    error_code = "authentication_error"


class AuthorizationError(AppException):
    status_code = 403
    detail = "Not permitted to perform this action"
    error_code = "authorization_error"


class BusinessRuleError(AppException):
    status_code = 422
    detail = "Operation violates a business rule"
    error_code = "business_rule"
