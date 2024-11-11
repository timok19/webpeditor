from typing import NotRequired, TypedDict
from rest_framework import status
from rest_framework.response import Response

from webpeditor_app.common.resultant import ErrorCode, ResultantValue, ResultantError, Resultant


class ResultantData[TValue](TypedDict):
    value: NotRequired[TValue]
    message: NotRequired[str]


class ResultantResponse[TValue](Response):
    @classmethod
    def error(cls, message: str, error_code: ErrorCode) -> "ResultantResponse[TValue]":
        return cls(data=ResultantData(message=message), status=error_code)

    @classmethod
    def from_resultant(cls, resultant: ResultantValue[TValue]) -> "ResultantResponse[TValue]":
        if not cls.is_successful(resultant):
            return cls.from_error(resultant.failure())

        return cls.from_success(resultant.unwrap())

    @classmethod
    def from_success(cls, value: TValue) -> "ResultantResponse[TValue]":
        return cls(data=ResultantData(value=value), status=status.HTTP_200_OK)

    @classmethod
    def from_error(cls, error: ResultantError) -> "ResultantResponse[TValue]":
        return cls(data=ResultantData(message=error.message), status=error.error_code)

    @classmethod
    def is_successful(cls, resultant: ResultantValue[TValue]) -> bool:
        return Resultant.is_successful(resultant)
