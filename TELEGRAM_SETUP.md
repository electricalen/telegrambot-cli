# Telegram Bot Setup And Running Guide

This guide covers the runtime setup for `telegrambot-cli`: creating the bot, finding the allowed owner IDs, configuring environment variables, and running either the framework itself or the bundled sample app.

## 1. Create The Bot In Telegram

1. Open Telegram and talk to **[@BotFather](https://t.me/BotFather)**.
2. Send `/newbot` and follow the prompts.
3. Copy the **bot token** (looks like `123456:ABC...`).

Treat the token like a password; do not commit it to git.

## 2. Find Your Telegram User ID

The bot only accepts messages from users listed in `TELEGRAM_OWNER_IDS`.

- Message **[@userinfobot](https://t.me/userinfobot)** and copy the numeric `Id`.
- Use a **comma-separated list** for multiple owners, e.g. `123,456`.

## 3. Configuration

The library loads `Path.cwd() / ".env"` by default unless `TELEGRAM_ENV_FILE` is set or you call `load_settings(env_file=...)`.

1. Copy the example from the repo root:

```bash
cp .env.example .env
```

2. Edit `.env` with at least `TELEGRAM_BOT_TOKEN` and `TELEGRAM_OWNER_IDS`.

Optional alternate env file:

```bash
 export TELEGRAM_ENV_FILE="$HOME/secrets/telegram.env"
```

### Variable Reference

| Variable | Example | Meaning |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | `123:abc...` | From BotFather (required) |
| `TELEGRAM_OWNER_IDS` | `123456789` or `1,2` | Allowed user id(s) (required) |
| `TELEGRAM_ENV_FILE` | path | Alternate env file |
| `TELEGRAM_POLLING_TIMEOUT_SEC` | `30` | PTB long-poll timeout |
| `TELEGRAM_HEARTBEAT_ENABLED` | `true` | Periodic heartbeat message |
| `TELEGRAM_HEARTBEAT_INTERVAL_SEC` | `900` | Heartbeat interval (seconds) |
| `TELEGRAM_HEARTBEAT_MESSAGE` | `Heartbeat` | Heartbeat text |
| `TELEGRAM_MONITOR_INTERVAL_SEC` | `120` | Custom monitor tick interval |
| `TELEGRAM_LOG_LEVEL` | `INFO` | Logging level |

## 4. Use As A Library

Install directly from the public GitHub repository:

```bash
pip install "git+https://github.com/electricalen/telegrambot-cli.git"
```

Or with `uv`:

```toml
dependencies = ["telegrambot-cli"]
[tool.uv.sources]
telegrambot-cli = { git = "https://github.com/electricalen/telegrambot-cli.git" }
```

**Minimal app:**

```python
from telegrambot_cli import run_bot

run_bot(
    plugin_package="myapp.plugins",
    pre_import_modules=("myapp.monitors",),
)
```

- Built-in `help` and `commands` are registered unless you pass `include_builtin_commands=False`.
- Put one command per module under `myapp/plugins/` with `def register(registry): ...`.

### Integrate Into An Existing PTB App

If your project already creates the PTB application, use the lower-level API:

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

## 5. Run From This Repo

### Library Only

From repo root, `.env` in the current working directory:

```bash
uv sync
uv run telegrambot-cli
# or: uv run python -m telegrambot_cli
```

### Full Example

```bash
cd examples/sample_app
cp ../../.env.example .env
uv sync
uv run sample-telegram-bot
```

## 6. Using The Message CLI

- `commands`
- `help`
- `help echo`
- `echo hello`
- `time tz=America/New_York`

## 7. Adding Commands

1. Create a Python **package** (e.g. `myapp/plugins/`).
2. Add one file per command; each file defines `register(registry)` and uses `@telegram_command` + `register_decorated`.
3. Pass `plugin_package="myapp.plugins"` to `run_bot`.
4. Copy the pattern from `examples/sample_app/sample_app/plugins/` and `_template.py`.

## 8. Adding Proactive Monitors

1. In your app, use `from telegrambot_cli import register_monitor`.
2. Decorate async `async def myjob(context): ...` and call `context.bot.send_message(...)`.
3. Import that module **before** `run_bot` runs JobQueue setup, e.g. list it in `pre_import_modules=("myapp.monitors",)`.

See `examples/sample_app/sample_app/monitors.py` for a commented stub.

## 9. Troubleshooting

- Bot ignores you: check `TELEGRAM_OWNER_IDS` matches your Telegram user id.
- Monitors never run: ensure the module that calls `@register_monitor` is imported before `run_bot()` schedules jobs.
- JobQueue errors: install must include `python-telegram-bot[job-queue]` (already a dependency of `telegrambot-cli`).

## 10. References

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [examples](https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples)
