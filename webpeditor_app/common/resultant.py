from dataclasses import dataclass
from enum import IntEnum

from rest_framework import status
from returns.pipeline import is_successful
from returns.result import Result


type ResultantValue[T: object] = Result[T, ResultantError]
type ResultantEmpty = Result[None, ResultantError]


class ErrorCode(IntEnum):
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR


@dataclass(frozen=True)
class ResultantError:
    message: str
    error_code: ErrorCode


class Resultant[TValue: object](Result[TValue, ResultantError]):
    @classmethod
    def success(cls, value: TValue) -> ResultantValue[TValue]:
        return cls.from_value(value)

    @classmethod
    def error(cls, message: str, error_code: ErrorCode) -> ResultantValue[TValue]:
        return cls.from_failure(ResultantError(message=message, error_code=error_code))

    @classmethod
    def empty(cls) -> ResultantEmpty:
        return cls.from_value(None)

    @classmethod
    def is_successful(cls, resultant: ResultantValue[TValue]) -> bool:
        return is_successful(resultant)
