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

Install the repo locally with `uv`:

```bash
uv sync
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Run the library directly:

```bash
uv run telegrambot-cli
```

Run the example app:

```bash
cd examples/sample_app
cp ../../.env.example .env
uv sync
uv run sample-telegram-bot
```

Detailed bot setup, configuration, and troubleshooting live in [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md).

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
