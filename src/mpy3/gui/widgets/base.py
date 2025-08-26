import random
import string
from typing import Optional, TypedDict


class WidgetProps(TypedDict, total=False):
    pass


class Widget:
    def __init__(
        self,
        props: Optional[WidgetProps] = None,
    ) -> None:
        self._class_name = "Widget"
        self._generate_id(self._class_name)

        if props is None:
            props = {}

        self.children: list[Widget] = []

    def _generate_id(self, class_name: str) -> None:
        unique_string = "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
        )

        self.id = f"{class_name}_{unique_string}"
