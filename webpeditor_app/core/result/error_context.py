from enum import IntEnum
from http import HTTPStatus
from typing import Optional

from ninja import Field, Schema
from pydantic import ConfigDict


class ErrorContext(Schema):
    class ErrorCode(IntEnum):
        BAD_REQUEST = HTTPStatus.BAD_REQUEST
        UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
        FORBIDDEN = HTTPStatus.FORBIDDEN
        NOT_FOUND = HTTPStatus.NOT_FOUND
        INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    error_code: ErrorCode
    message: str = Field(default_factory=str)
    reasons: list[str] = Field(default_factory=list[str])

    @classmethod
    def bad_request(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.BAD_REQUEST, message, reasons)

    @classmethod
    def unauthorized(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.UNAUTHORIZED, message, reasons)

    @classmethod
    def forbidden(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.FORBIDDEN, message, reasons)

    @classmethod
    def not_found(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.NOT_FOUND, message, reasons)

    @classmethod
    def server_error(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.INTERNAL_SERVER_ERROR, message, reasons)

    @classmethod
    def create(
        cls,
        error_code: ErrorCode,
        message: Optional[str] = None,
        reasons: Optional[list[str]] = None,
    ) -> "ErrorContext":
        return cls(error_code=error_code, message=message or "", reasons=reasons or [])

    def to_str(self) -> str:
        return f"Error code: {self.error_code}, Message: {self.message}, Reasons: [{self.reasons if any(self.reasons) else ''}]"
