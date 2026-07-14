# Cookie automation (required for live unofficial clients)

Manual DevTools cookie copy is painful. **Always ship an automated cookie
collection system** with live unofficial clients (pattern from claude-web-client v0.3+).

## Goals

1. User already logged into the site in **Google Chrome** → collect without re-login
2. Default browser is **Chrome**, not Edge / IE / random Chromium
3. Never print full cookies in logs
4. Persist to a local store (`~/.{app}/session.json`) with `sessionKey`-quality auth
5. Fallback: CDP → real profile → Playwright Chrome window

## Collection pipeline (implement in this order)

```
env COOKIE / SERVICE_COOKIE
  → local session store (reject if no real session cookie)
  → Chrome cookie DB (browser_cookie3 / copy Cookies file)
  → Chrome CDP (connect_over_cdp :9222)
  → Playwright launch real Chrome User Data (profile must be unlocked)
  → Playwright channel="chrome" clean profile (user logs in once)
```

**Do not** default Playwright `channel` to `msedge`.

## Required package modules

```
{import_name}/
  cookie_collector.py   # collect_cookie_auto, from_chrome_*, save/load session
  client.py             # Client.from_browser(), from_chrome(), from_store()
usecases/
  collect_cookies.py    # CLI: --chrome --cdp --chrome-profile --playwright
docs/
  COOKIE_AUTOMATION.md
```

## CLI surface agents must provide

| Flag | Behavior |
|------|----------|
| (default) | env → store → Chrome DB → CDP |
| `--chrome` | Force Chrome DB + CDP |
| `--chrome-profile` | Real Chrome User Data (quit Chrome first) |
| `--cdp` / `--cdp-url` | Attach to running Chrome debugging port |
| `--playwright` | Open **Chrome** window; wait for `sessionKey` |
| `--channel chrome` | Explicit; never default to msedge |
| `--diagnose` | chrome path, CDP port open?, collectors installed |
| `--clear` / `--dotenv` | store hygiene |

Entry point example: `my-service-cookies = usecases.collect_cookies:main`

## Session quality gate

Only accept jars that look **logged-in**:

```python
def looks_like_session(names):
    lower = {n.lower() for n in names}
    return "sessionkey" in lower or "session_key" in lower
    # Do NOT accept only __cf_bm / activitySessionId / anthropic-device-id
```

Incomplete jars caused 403 on live APIs when collectors exited too early.

## Chrome paths (Windows)

```
%LOCALAPPDATA%\Google\Chrome\User Data\
  Default\Network\Cookies   # modern
  Default\Cookies
  Local State               # encryption key
```

Executable:

```
%PROGRAMFILES%\Google\Chrome\Application\chrome.exe
```

## CDP for already-open Chrome

```text
chrome.exe --remote-debugging-port=9222 --user-data-dir="...User Data"
playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
context.cookies() → filter domain → Cookie header
```

Do not `browser.close()` in a way that kills the user's Chrome unexpectedly;
disconnect cleanly.

## Client API agents must expose

```python
Client.from_chrome()              # preferred
Client.from_browser(channel="chrome", chrome=True, cdp=True)
Client.from_browser(chrome_profile=True)
Client.from_store()
Client(auto_cookies=True)         # optional convenience
```

## Dependencies

```toml
dependencies = [
  "requests",
  "curl_cffi",           # if site blocks plain TLS
  "browser_cookie3",     # Chrome cookie DB
]
optional = [
  "playwright",          # CDP + interactive Chrome
]
```

Note: `rookiepy` often fails to build on Python 3.13 — keep optional.

## Windows pitfalls (document in README)

| Issue | Mitigation |
|-------|------------|
| `RequiresAdminError` shadow copy | Quit Chrome; Admin terminal; or CDP |
| Profile lock | Fully quit all chrome.exe |
| Edge opens instead of Chrome | `channel="chrome"` first in order |
| Playwright downloads Chromium | Prefer `channel="chrome"` system install |
| Stale store without sessionKey | Reject store; force recollect |

## Ethics

- Only the user's own browsers/profiles
- No credential stuffing, no stealing third-party cookies
- Disclose unofficial + ToS risk
- Prefer official API keys for production

## Reference implementation

See project `claude-web-client` (if present in workspace):

- `claude_web_client/cookie_collector.py`
- `usecases/collect_cookies.py`
- `docs/COOKIE_AUTOMATION.md`
