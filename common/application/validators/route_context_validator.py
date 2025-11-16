from typing import Optional

from expression import Option
from ninja_extra.context import RouteContext

from common.application.abc.validator_abc import ValidatorABC
from common.core.result import ContextResult, ErrorContext


class RouteContextValidator(ValidatorABC[RouteContext]):
    def validate(self, value: Optional[RouteContext]) -> ContextResult[RouteContext]:
        result = Option[RouteContext].of_optional(value).to_result(ErrorContext.bad_request(f"{RouteContext.__name__} is empty"))
        return ContextResult[RouteContext].from_result(result)
