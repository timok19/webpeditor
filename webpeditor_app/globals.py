class Unit(tuple[object]): ...


class Pair[T1, T2](tuple[T1, T2]):
    __slots__ = ()

    def __new__(cls, item1: T1, item2: T2):
        return super().__new__(cls, (item1, item2))

    @property
    def item1(self) -> T1:
        return self[0]

    @property
    def item2(self) -> T2:
        return self[1]
