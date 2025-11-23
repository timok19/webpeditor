from typing import Self, override


class Pair[T1, T2](tuple[T1, T2]):
    __slots__ = ()

    @override
    def __new__(cls, item1: T1, item2: T2) -> Self:
        return super().__new__(cls, (item1, item2))

    @classmethod
    def from_tuple(cls, items: tuple[T1, T2]) -> Self:
        return cls(items[0], items[1])

    @property
    def item1(self) -> T1:
        return self[0]

    @property
    def item2(self) -> T2:
        return self[1]
