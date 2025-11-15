from typing import Optional

from django.http import HttpRequest
from expression import Option

from webpeditor_app.application.common.abc.validator_abc import ValidatorABC
from webpeditor_app.core.result import ContextResult, ErrorContext


class HttpRequestValidator(ValidatorABC[HttpRequest]):
    def validate(self, value: Optional[HttpRequest]) -> ContextResult[HttpRequest]:
        result = Option[HttpRequest].of_optional(value).to_result(ErrorContext.bad_request(f"{HttpRequest.__name__} is empty"))
        return ContextResult[HttpRequest].from_result(result)
