from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Type, TypeVar

from pydantic import BaseModel

from telegrambot_cli.commands.types import CommandHandler, TelegramCommandSpec

TArgs = TypeVar("TArgs", bound=BaseModel)


@dataclass
class CommandRegistry:
    _by_name: Dict[str, TelegramCommandSpec]

    def __init__(self) -> None:
        self._by_name = {}

    def register(self, spec: TelegramCommandSpec) -> None:
        key = spec.name.lower()
        if key in self._by_name:
            raise ValueError(f"Duplicate command registered: {spec.name}")
        self._by_name[key] = spec

    def get(self, name: str) -> Optional[TelegramCommandSpec]:
        return self._by_name.get(name.lower())

    def all(self) -> list[TelegramCommandSpec]:
        return sorted(self._by_name.values(), key=lambda s: s.name)


def register_decorated(registry: CommandRegistry, handler: CommandHandler) -> None:
    """Register a function that was decorated with `@telegram_command`."""
    spec = getattr(handler, "__telegram_command_spec__", None)
    if not isinstance(spec, TelegramCommandSpec):
        raise TypeError(f"{handler!r} is missing a @telegram_command decorator")
    registry.register(spec)


def telegram_command(
    *,
    name: str,
    help: str,
    args_model: Optional[Type[TArgs]] = None,
) -> Callable[[CommandHandler], CommandHandler]:
    """Decorator for command handlers. Register with ``register_decorated`` inside ``register(registry)``."""

    def decorator(func: CommandHandler) -> CommandHandler:
        setattr(
            func,
            "__telegram_command_spec__",
            TelegramCommandSpec(name=name, help=help, args_model=args_model, handler=func),
        )
        return func

    return decorator
