import random
import string
from typing import Generic, Optional, Type, TypedDict, TypeVar

NAME = "Widget"


class WidgetProps(TypedDict):
    pass


class PartialWidgetProps(WidgetProps, total=False):
    pass


DEFAULT_WIDGET_PROPS: WidgetProps = {}


class Widget:
    def __init__(
        self,
        props: Optional[PartialWidgetProps] = None,
    ) -> None:
        self._generate_id(NAME)

        self.children: list[Widget] = []

    def _generate_id(self, class_name: str) -> None:
        unique_string = "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
        )

        self.id = f"{class_name}_{unique_string}"
