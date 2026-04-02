# Sample bot (`telegrambot-cli`)

Minimal application that depends on the **`telegrambot-cli`** library from the repo root.

## Run

From this directory:

```bash
cp ../../.env.example .env
# edit .env — same TELEGRAM_* variables as the main docs

uv sync
uv run sample-telegram-bot
```

Or: `uv run python -m sample_app`.

## Layout

| Path | Role |
| --- | --- |
| `sample_app/__main__.py` | Calls `run_bot(plugin_package=..., pre_import_modules=...)` |
| `sample_app/plugins/` | One module per command (`register` + `@telegram_command`) |
| `sample_app/monitors.py` | Optional `@register_monitor` hooks (imported for side effects) |

Copy `_template.py` in `plugins/` to add commands.
