# telegrambot-cli

`telegrambot-cli` is a small framework for building owner-only Telegram bots that behave like a message-driven CLI. It is designed for bots that need a clean command surface, predictable plugin loading, and optional scheduled background jobs without introducing a larger web stack.

It is built on [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and exposes a compact API:

- CLI-style command parsing from plain Telegram messages
- Declarative command registration with Pydantic-backed argument models
- Built-in `help` and `commands` discovery
- Optional repeating jobs for heartbeats and custom monitors
- A sample app that demonstrates a multi-command project layout

Distribution name: `telegrambot-cli`  
Import package: `telegrambot_cli`

## Install

Install from PyPI:

```bash
pip install telegrambot-cli
```

With `uv`:

```bash
uv add telegrambot-cli
```

Use GitHub only if you need an unreleased revision:

```bash
pip install "git+https://github.com/electricalen/telegrambot-cli.git"
```

With `uv`, add it as a Git dependency:

```toml
dependencies = ["telegrambot-cli"]

[tool.uv.sources]
telegrambot-cli = { git = "https://github.com/electricalen/telegrambot-cli.git" }
```

For local development against this repository:

```bash
uv sync --group dev
```

For release checks:

```bash
uv sync --group dev --group release
uv run python -m build
uv run twine check dist/*
```

## What It Looks Like

Message the bot as an allowed owner:

```text
commands
help time
echo hello from telegram
time tz=Europe/Madrid
```

Command handlers stay small and explicit:

```python
from pydantic import BaseModel, Field

from telegrambot_cli import CommandRegistry, register_decorated, telegram_command


class EchoArgs(BaseModel):
    text: str = Field(..., description="Text to echo back")


def register(registry: CommandRegistry) -> None:
    @telegram_command(
        name="echo",
        help="Echo text back to the sender.",
        args_model=EchoArgs,
    )
    def echo_cmd(args: EchoArgs) -> str:
        return args.text

    register_decorated(registry, echo_cmd)
```

## Quick Start

Create a `.env` file:

```bash
cp .env.example .env
```

Run the library directly:

```bash
telegrambot-cli
```

Run the example app:

```bash
cd examples/sample_app
cp ../../.env.example .env
uv sync
uv run sample-telegram-bot
```

Detailed bot setup, configuration, and troubleshooting live in [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md).

## Publishing

Releases are intended to be published with GitHub Actions Trusted Publishing:

- `test.yml` runs the test suite on pushes and pull requests.
- tags matching `v*` publish to PyPI
- manual runs can publish to TestPyPI
- `release.yml` builds distributions, validates them with `twine check`, and publishes to the selected index

Before the first publish, configure PyPI and TestPyPI Trusted Publishing for this repository's GitHub Actions workflow.

Local release smoke test:

```bash
uv sync --group dev --group release
uv run pytest -q
uv run python -m build
uv run twine check dist/*
```

## Minimal App

```python
from telegrambot_cli import run_bot


def main() -> None:
    run_bot(
        plugin_package="myapp.plugins",
        pre_import_modules=("myapp.monitors",),
    )


if __name__ == "__main__":
    main()
```

By default, `run_bot()` loads settings from `Path.cwd() / ".env"`. You can also set `TELEGRAM_ENV_FILE` or pass `settings=load_settings(...)` directly.

## Integration Modes

The library supports three adoption levels:

1. `run_bot(...)`
   The highest-level entrypoint. Use this when the library should own PTB setup and polling.
2. `build_application(...)`
   Builds a PTB `Application` with the framework wired in, but does not start polling.
3. `prepare_runtime(...)` + `configure_application(...)`
   Use these when your project already owns PTB builder configuration, persistence, webhook setup, or lifecycle management.

### Greenfield Bot

Use `run_bot(...)` if you want the library to manage everything:

```python
from telegrambot_cli import run_bot


run_bot(
    plugin_package="myapp.plugins",
    pre_import_modules=("myapp.monitors",),
)
```

### Custom PTB Builder

Use `build_application(...)` when you need PTB customization before the app is started:

```python
from telegram.ext import PicklePersistence

from telegrambot_cli import build_application


application = build_application(
    plugin_package="myapp.plugins",
    pre_import_modules=("myapp.monitors",),
    configure_builder=lambda builder: builder.persistence(
        PicklePersistence(filepath="bot-data.pkl")
    ),
)

application.run_polling()
```

### Existing PTB Application

Use `prepare_runtime(...)` and `configure_application(...)` when your project already creates the PTB app:

```python
from telegram.ext import Application

from telegrambot_cli import configure_application, prepare_runtime


settings, registry = prepare_runtime(
    plugin_package="myapp.plugins",
    pre_import_modules=("myapp.monitors",),
)

application = Application.builder().token(settings.bot_token).build()
configure_application(application, settings=settings, registry=registry)
application.run_polling(timeout=settings.polling_timeout_sec)
```

## Architecture

The framework has three main pieces:

1. Message routing
   Incoming text messages from approved owners are parsed as CLI input and dispatched to a registered command.
2. Command catalog
   Commands are loaded from built-ins, plugin packages, and optional inline registration hooks.
3. Scheduled jobs
   PTB `JobQueue` can send heartbeats and run user-defined async monitor callbacks on a fixed interval.

Repository layout:

| Path | Purpose |
| --- | --- |
| `telegrambot_cli/` | Core framework package |
| `examples/sample_app/` | Example application using the package |
| `tests/` | Parser, dispatch, configuration, and plugin loader coverage |
| `TELEGRAM_SETUP.md` | Setup guide, env reference, and troubleshooting |

## Extension Model

### Command Plugins

Point `run_bot()` at a package and define one command per module:

```python
def register(registry: CommandRegistry) -> None:
    @telegram_command(name="hello", help="Say hello.")
    def hello_cmd() -> str:
        return "hello"

    register_decorated(registry, hello_cmd)
```

Plugin discovery skips files whose module name starts with `_`, which makes `_template.py` a safe starter for new commands.

### Monitors

Monitors are async callbacks registered with `@register_monitor` and scheduled through PTB's `JobQueue`.

```python
from telegrambot_cli import register_monitor


@register_monitor
async def tick(context) -> None:
    owner_ids = context.application.bot_data["owner_ids"]
    for chat_id in owner_ids:
        await context.bot.send_message(chat_id=chat_id, text="tick")
```

Import monitor modules through `pre_import_modules` so decorators run before job scheduling begins.

### Inline Commands

For small projects, commands can be registered without a plugin package:

```python
from telegrambot_cli import CommandRegistry, run_bot, register_decorated, telegram_command


def register_commands(registry: CommandRegistry) -> None:
    @telegram_command(name="ping", help="Health check.")
    def ping() -> str:
        return "pong"

    register_decorated(registry, ping)


run_bot(register_commands=register_commands)
```

## Configuration

Key environment variables:

| Variable | Description |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_OWNER_IDS` | Comma-separated Telegram user IDs allowed to use the bot |
| `TELEGRAM_POLLING_TIMEOUT_SEC` | PTB long-poll timeout |
| `TELEGRAM_HEARTBEAT_ENABLED` | Enables the built-in repeating heartbeat |
| `TELEGRAM_HEARTBEAT_INTERVAL_SEC` | Heartbeat interval in seconds |
| `TELEGRAM_MONITOR_INTERVAL_SEC` | Interval for custom registered monitors |
| `TELEGRAM_LOG_LEVEL` | Standard Python logging level |

Settings are modeled with Pydantic and normalized on load, which keeps validation close to startup instead of failing later in message handling.

## Public API

### `run_bot(...)`

High-level entrypoint that builds a PTB application and starts long polling.

Arguments:

| Parameter | Purpose |
| --- | --- |
| `settings` | Pre-built `Settings` instance. Defaults to `load_settings()`. |
| `register_commands` | Optional callback for inline command registration. |
| `plugin_package` | String package name or imported module containing command plugins. |
| `pre_import_modules` | Modules imported before scheduling jobs, usually to trigger `@register_monitor`. |
| `include_builtin_commands` | Enables built-in `help` and `commands`. |
| `builder` | Optional PTB `ApplicationBuilder` instance. |
| `configure_builder` | Optional callback to customize the PTB builder before `build()`. |
| `configure_logging` | Enables library logging setup from `Settings.log_level`. |
| `add_default_handlers` | Adds the owner-only text command handler. |
| `enable_jobs` | Schedules heartbeat and registered monitors. |

### `build_application(...)`

Builds and configures a PTB `Application`, but leaves lifecycle control to the caller.

### `prepare_runtime(...)`

Loads settings, imports monitor modules, and creates the `CommandRegistry`.

### `configure_application(...)`

Attaches telegrambot-cli state, handlers, and jobs to an existing PTB `Application`.

## Development

Install dev dependencies and run tests:

```bash
uv sync --group dev
uv run pytest
```

Typecheck and linting are intentionally not prescribed here, but the project includes deterministic plugin loading, configuration validation, and unit tests around the framework's core behavior.

## Example App

The sample app in [`examples/sample_app/`](examples/sample_app/) demonstrates:

- a clean `run_bot()` entrypoint
- multiple command modules under `plugins/`
- typed arguments with Pydantic
- a monitor module wired via `pre_import_modules`

That example is small enough to copy into a new project while still reflecting the expected package structure.

## Security

This framework is intentionally owner-scoped. Only users in `TELEGRAM_OWNER_IDS` can execute commands through the message interface. Treat the Telegram bot token like any other production secret and avoid committing `.env` files or hard-coded credentials.
