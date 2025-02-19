from enum import IntEnum, auto
from typing import Optional

from pydantic import BaseModel, ConfigDict
from returns.result import Result


class FailureContext(BaseModel):
    class ErrorCode(IntEnum):
        BAD_REQUEST = auto()
        UNAUTHORIZED = auto()
        FORBIDDEN = auto()
        NOT_FOUND = auto()
        INTERNAL_SERVER_ERROR = auto()

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    message: Optional[str] = None
    error_code: ErrorCode


type ValueResult[T: object] = Result[T, FailureContext]
