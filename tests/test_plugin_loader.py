from __future__ import annotations

import sys
from textwrap import dedent

from telegrambot_cli.commands.plugin_loader import load_plugins
from telegrambot_cli.commands.registry import CommandRegistry


def test_load_plugins_is_deterministic_and_skips_private_modules(tmp_path) -> None:
    package_dir = tmp_path / "demo_plugins"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "_template.py").write_text("IGNORED = True\n", encoding="utf-8")
    (package_dir / "beta.py").write_text(
        dedent(
            """
            def register(registry):
                registry._load_order.append("beta")
            """
        ),
        encoding="utf-8",
    )
    (package_dir / "alpha.py").write_text(
        dedent(
            """
            def register(registry):
                registry._load_order.append("alpha")
            """
        ),
        encoding="utf-8",
    )

    sys.path.insert(0, str(tmp_path))
    try:
        package = __import__("demo_plugins", fromlist=["demo_plugins"])
        registry = CommandRegistry()
        registry._load_order = []

        load_plugins(package, registry)

        assert registry._load_order == ["alpha", "beta"]
    finally:
        sys.path.remove(str(tmp_path))
