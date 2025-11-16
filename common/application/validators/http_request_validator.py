from typing import Optional

from django.http import HttpRequest
from expression import Option

from common.application.abc.validator_abc import ValidatorABC
from common.core.result import ContextResult, ErrorContext


class HttpRequestValidator(ValidatorABC[HttpRequest]):
    def validate(self, value: Optional[HttpRequest]) -> ContextResult[HttpRequest]:
        result = Option[HttpRequest].of_optional(value).to_result(ErrorContext.bad_request(f"{HttpRequest.__name__} is empty"))
        return ContextResult[HttpRequest].from_result(result)
