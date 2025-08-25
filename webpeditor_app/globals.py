from typing import Any, Self, override


class Unit(tuple[Any]):
    @override
    def __new__(cls) -> Self:
        return super().__new__(cls, ())


class Pair[T1, T2](tuple[T1, T2]):
    __slots__ = ()

    @override
    def __new__(cls, first: T1, second: T2) -> Self:
        return super().__new__(cls, (first, second))

    @property
    def first(self) -> T1:
        return self[0]

    @property
    def second(self) -> T2:
        return self[1]
