class AppError(Exception):
    """Base application error."""

    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "Internal server error.", detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class PaymentError(AppError):
    status_code = 402
    code = "payment_error"
