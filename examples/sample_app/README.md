# Sample App

This example shows the intended project shape for a bot built on `telegrambot-cli`. It keeps the application code thin and pushes the reusable framework concerns into the package at the repository root.

## Run

From `examples/sample_app/`:

```bash
cp ../../.env.example .env
uv sync
uv run sample-telegram-bot
```

You can also start it with:

```bash
uv run python -m sample_app
```

## Included Commands

- `ping`
- `echo text`
- `time tz=Europe/Madrid`

## Layout

| Path | Purpose |
| --- | --- |
| `sample_app/__main__.py` | Entrypoint that calls `run_bot(...)` |
| `sample_app/plugins/` | Command modules loaded through plugin discovery |
| `sample_app/plugins/_template.py` | Starter template for a new command |
| `sample_app/monitors.py` | Optional monitor module imported for side effects |

The sample is intentionally small, but it demonstrates the contract expected by the framework: explicit command registration, typed arguments, and startup-driven monitor loading.
