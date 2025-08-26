import random
import string
from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, Mapping, Optional, Type, TypeVar

T = TypeVar("T")


@dataclass
class WidgetProps:
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class Widget:
    def __init__(
        self,
        props: Optional[WidgetProps] = None,
    ) -> None:
        props = self._init_props(WidgetProps, props)

        self._class_name = "Widget"
        self._generate_id(self._class_name)

        self.children: list[Widget] = []

    def _init_props(self, C: Type[T], props: Optional[Any] = None) -> T:
        if not is_dataclass(C):
            raise TypeError("C must be a dataclass")

        if props is None:
            return C()

        if is_dataclass(props) and not isinstance(props, type):
            raw_props = asdict(props)
        elif isinstance(props, Mapping):
            raw_props = dict(props)
        else:
            raise TypeError("props must be a dataclass instance or mapping")

        valid_fields = {f.name for f in fields(C)}
        str_fields = {k: v for k, v in raw_props.items() if k in valid_fields}

        return C(**str_fields) if props else C()

    def _generate_id(self, class_name: str) -> None:
        unique_string = "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
        )

        self.id = f"{class_name}_{unique_string}"
