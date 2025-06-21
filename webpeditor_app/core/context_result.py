from typing import TYPE_CHECKING, Union, Optional, Callable, override, Awaitable

from expression import Result
from types_linq import Enumerable

from webpeditor_app.core.decorators import acontext_result, aenumerable_context_result
from webpeditor_app.core.error_context import ErrorContext


if TYPE_CHECKING:
    from webpeditor_app.core.enumerable_context_result import EnumerableContextResult


class ContextResult[TOut](Result[TOut, ErrorContext]):
    @staticmethod
    def success(value: TOut) -> "ContextResult[TOut]":
        return ContextResult(tag="ok", ok=value)

    @staticmethod
    def failure(error: ErrorContext) -> "ContextResult[TOut]":
        return ContextResult[TOut].failure2(error.error_code, error.message, error.reasons)

    @staticmethod
    def failure2(
        error_code: ErrorContext.ErrorCode,
        message: Optional[str] = None,
        reasons: Optional[list[str]] = None,
    ) -> "ContextResult[TOut]":
        return ContextResult(
            tag="error",
            error=ErrorContext(
                error_code=error_code,
                message=message or "",
                reasons=reasons or [],
            ),
        )

    @staticmethod
    def failures(*errors: ErrorContext) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](Enumerable(errors).select(ContextResult[TOut].failure))

    @classmethod
    def from_result(cls, result: Result[TOut, ErrorContext]) -> "ContextResult[TOut]":
        match result:
            case Result(tag="ok", ok=value):
                return cls.success(value)
            case Result(tag="error", error=error):
                return cls.failure(error)
            case _:
                return cls.unexpected()

    def match(
        self,
        success_func: Callable[[TOut], TOut],
        error_func: Callable[[ErrorContext], ErrorContext],
    ) -> "ContextResult[TOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return self.success(success_func(value))
            case ContextResult(tag="error", error=error):
                return self.failure(error_func(error))
            case _:
                return self.unexpected()

    @override
    def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @override
    def bind[TNewOut](self, mapper: Callable[[TOut], Result[TNewOut, ErrorContext]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    def bind2[TNewOut](self, mapper: Callable[[TOut], "ContextResult[TNewOut]"]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @override
    def or_else(self, other: Result[TOut, ErrorContext]) -> "ContextResult[TOut]":
        return self if self.is_ok() else ContextResult[TOut].from_result(other)

    @acontext_result
    async def aor_else(self, other: Awaitable["ContextResult[TOut]"]) -> "ContextResult[TOut]":
        return self if self.is_ok() else await other

    def if_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
        else_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return then_mapper(value) if predicate(value) else else_mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @acontext_result
    async def abind[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @acontext_result
    async def amap[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @acontext_result
    async def amap2[TOutOther, TNewOut](
        self,
        other: "ContextResult[TOutOther]",
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return other.map(lambda value_: mapper(value, value_))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @aenumerable_context_result
    async def abind_many[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "EnumerableContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return await mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failures(error)
            case _:
                return ContextResult[TNewOut].unexpected_many()

    @acontext_result
    async def aif_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], Union[bool, Awaitable[bool]]],
        then_mapper: Callable[[TOut], Union["ContextResult[TNewOut]", Awaitable["ContextResult[TNewOut]"]]],
        else_mapper: Callable[[TOut], Union["ContextResult[TNewOut]", Awaitable["ContextResult[TNewOut]"]]],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                pred_result = predicate(value)
                if isinstance(pred_result, Awaitable):
                    pred_result = await pred_result

                if pred_result:
                    mapper_result = then_mapper(value)
                else:
                    mapper_result = else_mapper(value)

                if isinstance(mapper_result, Awaitable):
                    return await mapper_result
                return mapper_result
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @staticmethod
    def unexpected() -> "ContextResult[TOut]":
        return ContextResult[TOut].failure(ErrorContext.server_error("Unexpected error"))

    @staticmethod
    def unexpected_many() -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut]([ContextResult[TOut].unexpected()])
