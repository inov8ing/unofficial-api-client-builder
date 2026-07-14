# Project checklist (definition of done)

## Structure

- [ ] `{import_name}/__init__.py` exports `Client` and `__version__`
- [ ] `{import_name}/client.py` implements public methods + `from_chrome` / `from_browser` / `from_store`
- [ ] `{import_name}/cookie_collector.py` Chrome-first auto collection (live packages)
- [ ] `{import_name}/exceptions.py` has `AuthError`, `APIError` (and optionally `RateLimitError`)
- [ ] `pyproject.toml` with deps and scripts (`*-chat`, `*-cookies`)
- [ ] `usecases/console_chatbot.py` runs end-to-end in demo mode
- [ ] `usecases/collect_cookies.py` CLI: `--chrome --cdp --chrome-profile --playwright --diagnose`
- [ ] `docs/COOKIE_AUTOMATION.md`
- [ ] `examples/basic_usage.py` + `live_smoke.py`
- [ ] `tests/` for parser + demo client + cookie helpers
- [ ] `.env.example` and `.gitignore` (session.json, .env, *.har)
- [ ] `README.md` with disclaimer + Chrome cookie commands

## Behavior

- [ ] `Client(cookie)` does not print the cookie
- [ ] All HTTP calls use a timeout
- [ ] SSE/JSON parsing covered by unit tests
- [ ] `create_*` returns an id usable by `send_*`
- [ ] Delete returns bool; failures don't crash the process silently
- [ ] Demo mode works offline (CI-friendly)

## Security

- [ ] No hardcoded secrets
- [ ] `.env` gitignored
- [ ] Exceptions truncate response bodies
- [ ] README warns about ToS / fragility

## Verification commands

```bash
pip install -e ".[dev]"
pytest -q
python examples/basic_usage.py
python -m usecases.console_chatbot   # interactive; smoke manually
```

## Live mode (optional)

- [ ] `API_BASE_URL` or hardcoded real host documented
- [ ] User supplied cookie via env only
- [ ] One successful `create` + `send` + `delete` smoke test
- [ ] “Last verified” date updated

## Handoff note to user

Write 5–10 lines:

1. Where the package lives
2. How to install
3. How to set auth
4. How to swap demo endpoints for live captures
5. Official API alternative if any
