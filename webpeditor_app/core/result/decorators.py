from functools import wraps
from typing import TYPE_CHECKING, Awaitable, Callable, ParamSpec, TypeVar

if TYPE_CHECKING:
    from webpeditor_app.core.result.awaitable_context_result import AwaitableContextResult
    from webpeditor_app.core.result.awaitable_enumerable_context_result import AwaitableEnumerableContextResult
    from webpeditor_app.core.result.context_result import ContextResult
    from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult


P = ParamSpec("P")
T = TypeVar("T")


def as_awaitable_result(func: Callable[P, Awaitable["ContextResult[T]"]]) -> Callable[P, "AwaitableContextResult[T]"]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> "AwaitableContextResult[T]":
        from webpeditor_app.core.result.awaitable_context_result import AwaitableContextResult

        return AwaitableContextResult[T](func(*args, **kwargs))

    return wrapper


def as_awaitable_enumerable_result(
    func: Callable[P, Awaitable["EnumerableContextResult[T]"]],
) -> Callable[P, "AwaitableEnumerableContextResult[T]"]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> "AwaitableEnumerableContextResult[T]":
        from webpeditor_app.core.result.awaitable_enumerable_context_result import AwaitableEnumerableContextResult

        return AwaitableEnumerableContextResult[T](func(*args, **kwargs))

    return wrapper
