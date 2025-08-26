from typing import Self, cast


class Vector:
    def __init__(self, *args) -> None:
        if len(args) == 1:
            value = args[0]
            self.x = value
            self.y = value

        if len(args) == 2:
            self.x, self.y = args

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0)

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other: Self) -> Self:
        result = Vector(0)
        result.x = self.x + other.x
        result.y = self.y + other.y
        return cast(Self, result)


class Rectangle:
    def __init__(self, *args) -> None:
        if len(args) == 1:
            value = args[0]
            self._left = value
            self._right = value
            self._top = value
            self._bottom = value

        if len(args) == 4:
            self._left, self._right, self._top, self._bottom = args

        self._x = self._left + self._right
        self._y = self._top + self._bottom

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def top(self):
        return self._top

    @property
    def bottom(self):
        return self._bottom

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @left.setter
    def left(self, value: int) -> None:
        self._left = value
        self._x = self._left + self._right

    @right.setter
    def right(self, value: int) -> None:
        self._right = value
        self._x = self._left + self._right

    @top.setter
    def top(self, value: int) -> None:
        self._top = value
        self._y = self._top + self._bottom

    @bottom.setter
    def bottom(self, value: int) -> None:
        self._bottom = value
        self._y = self._top + self._bottom

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0, 0, 0)

    def __repr__(self) -> str:
        return f"Rectangle({self.left}, {self.right}, {self.top}, {self.bottom})"

    def __eq__(self, other: object) -> bool:
        other = cast(Rectangle, other)

        if (
            self.left == other.left
            and self.right == other.right
            and self.top == other.top
            and self.bottom == other.bottom
        ):
            return True

        return False
