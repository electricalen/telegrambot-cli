# telegrambot-cli

Reusable **Python** library for an **owner-only** Telegram bot built on **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** (PTB):

- **Reactive**: incoming text is parsed as a small **CLI** (`help`, `commands`, and your plugins).
- **Proactive**: optional **JobQueue** heartbeats and **`@register_monitor`** hooks that can `send_message` anytime.

Distribution name: **`telegrambot-cli`**. Import package: **`telegrambot_cli`**.

---

## Install

**From this repo (editable dev install):**

```bash
cd /path/to/telegrambot
uv sync
```

**In another project**, add a path or Git dependency (see [`examples/sample_app/pyproject.toml`](examples/sample_app/pyproject.toml)):

```toml
dependencies = ["telegrambot-cli"]

[tool.uv.sources]
telegrambot-cli = { path = "../telegrambot", editable = true }
```

---

## Minimal app

```python
# myapp/__main__.py
from telegrambot_cli import run_bot

if __name__ == "__main__":
    run_bot(
        plugin_package="myapp.plugins",
        pre_import_modules=("myapp.monitors",),
    )
```

- Put **`TELEGRAM_BOT_TOKEN`** and **`TELEGRAM_OWNER_IDS`** in a `.env` file in the **process working directory**, or set `TELEGRAM_ENV_FILE`, or call `run_bot(settings=load_settings(env_file=...))`.
- **`help`** and **`commands`** are built into the library (`include_builtin_commands=False` to disable).

### `run_bot` parameters

| Parameter | Purpose |
| --- | --- |
| `settings` | Optional pre-built `Settings`; default loads from env / `.env`. |
| `plugin_package` | Package to scan for command plugins (each submodule with `register(registry)`). |
| `register_commands` | Extra `def register_commands(registry):` for inline registration. |
| `pre_import_modules` | Tuple of module names imported first (for `@register_monitor` side effects). |
| `include_builtin_commands` | Default `True` — registers library `help` / `commands`. |

---

## Command plugins (your code)

Convention: a package (e.g. `myapp/plugins/`) containing one module per command.

Each module must define:

```python
def register(registry: CommandRegistry) -> None:
    @telegram_command(name="hello", help="Say hi.")
    def hello_cmd() -> str:
        return "Hi!"

    register_decorated(registry, hello_cmd)
```

Discovery skips submodule names starting with **`_`** (use `_template.py` as a copy-paste starter).

**Public API:** `telegram_command`, `register_decorated`, `CommandRegistry`, or simply import from `telegrambot_cli`.

Full example: [`examples/sample_app/sample_app/plugins/`](examples/sample_app/sample_app/plugins/).

---

## Proactive monitors (your code)

Use `register_monitor` from **`telegrambot_cli`** and import the module via **`pre_import_modules`** so decorators run before JobQueue scheduling.

```python
# myapp/monitors.py
from telegrambot_cli import register_monitor

@register_monitor
async def tick(context):
    # owner_ids = context.application.bot_data["owner_ids"]
    # await context.bot.send_message(chat_id=..., text="...")
    pass
```

Interval: **`TELEGRAM_MONITOR_INTERVAL_SEC`** in `.env`. Heartbeat: **`TELEGRAM_HEARTBEAT_*`**.

---

## Repo layout

| Path | Role |
| --- | --- |
| [`telegrambot_cli/`](telegrambot_cli/) | Library source |
| [`examples/sample_app/`](examples/sample_app/) | Example dependency + `echo` / `ping` / `time` plugins |
| [`TELEGRAM_SETUP.md`](TELEGRAM_SETUP.md) | BotFather, `.env`, running, troubleshooting |

### Run example bot

```bash
cd examples/sample_app
cp ../../.env.example .env   # edit
uv sync
uv run sample-telegram-bot
```

### Run library alone (only built-in `help` / `commands`)

```bash
uv sync
uv run telegrambot-cli
```

---

## Security note

Only **`TELEGRAM_OWNER_IDS`** may use the text command path. Protect your **bot token** and any code you add in plugins or monitors. See `TELEGRAM_SETUP.md` for details.
