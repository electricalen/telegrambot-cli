from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Type

from pydantic import BaseModel


CommandHandler = Callable[..., str]


@dataclass(frozen=True)
class TelegramCommandSpec:
    name: str
    help: str
    args_model: Optional[Type[BaseModel]]
    handler: CommandHandler

    def usage(self, prefix: str = "") -> str:
        """
        Render a CLI-like usage line.

        Example: `/echo text=<text>`
        """
        cmd = f"{prefix}{self.name}".strip()
        if not self.args_model:
            return cmd

        parts: list[str] = []
        for field_name, field_info in self.args_model.model_fields.items():
            required = field_info.is_required()
            annotation = field_info.annotation
            type_name = getattr(annotation, "__name__", str(annotation))
            if required:
                parts.append(f"{field_name}=<{type_name}>")
            else:
                parts.append(f"[{field_name}=<{type_name}>]")
        return " ".join([cmd, *parts]).strip()
