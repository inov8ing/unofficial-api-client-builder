---
name: unofficial-api-client
description: >
  Build reusable unofficial-style HTTP client libraries (Python packages) that wrap
  private web-app endpoints the way Claude-API does: DevTools discovery, cookie/session
  auth, automated cookie collection (Chrome-first: cookie DB, CDP :9222, real profile,
  Playwright channel=chrome — not Edge), browser headers, SSE parsing, Client class
  (from_browser/from_chrome/from_store), pyproject packaging, usecases (console bot,
  cookie CLI). Use whenever the user asks for an unofficial API, reverse-engineered
  client, cookie wrapper, auto cookie collection, Chrome session export, claude.ai /
  chatgpt web UI wrap, Claude-API-like package, or runs /unofficial-api-client.
  Prefer official APIs for production.
---

# Unofficial API Client Builder

Reusable workflow for coding agents. Target outcome: an installable **Client library**
that mirrors projects like [Claude-API](https://github.com/KoushikNavuluri/Claude-API).

## When this skill applies

- User wants a **Python package** with `from pkg import Client` and methods like
  `send_message`, `create_new_chat`, `list_all_conversations`
- User references **unofficial**, **reverse-engineered**, **cookie-based**, or
  **web UI private endpoints**
- User wants to **package** HTTP wrappers for reuse across projects
- User wants a **chatbot / Discord bot** that consumes such a client

**Do not use** for building official REST APIs from scratch (use FastAPI/Django skill
patterns instead) unless they also want the client-wrapper packaging pattern.

## Non-negotiable guardrails

Read `references/ethics-and-guardrails.md` before implementing live reverse engineering.

1. **Prefer official APIs** for production (Anthropic, OpenAI, vendor docs).
2. **Never hardcode secrets** (cookies, tokens). Always env vars / secret managers.
3. **Disclose unofficial status** in README + disclaimer.
4. **Do not** help bypass paid paywalls, CAPTCHAs, or account security for abuse.
5. **Do not** steal credentials, automate account takeover, or target systems the user
   does not own / have permission to automate.
6. If the task is only learning packaging, scaffold **demo/mock mode** first (offline
   Client) so the user can run without cookies.

## Progressive disclosure (read as needed)

| File | When to load |
|------|----------------|
| `references/cookie-automation.md` | **Always for live clients** — Chrome-first auto cookies, CDP, CLI |
| `references/reverse-engineering.md` | Discovering endpoints from browser Network tab |
| `references/client-architecture.md` | Designing `Client` class, session, methods |
| `references/auth-patterns.md` | Cookie, bearer, CSRF, org-id bootstrap |
| `references/response-parsing.md` | JSON, SSE `data:`, chunked completions |
| `references/packaging-and-publishing.md` | pyproject.toml, setuptools, PyPI |
| `references/project-checklist.md` | Definition of done / QA |
| `assets/templates/*` | Copy-paste skeletons |
| `scripts/scaffold_unofficial_api.py` | Generate a full project tree |

## Default workflow (follow in order)

### Phase 0 — Clarify target

Ask only if missing:

1. **Target**: which site/service? Is there an official API? (If yes → recommend it.)
2. **Language**: default **Python 3.9+** (Claude-API style). Offer TS/Node only if asked.
3. **Auth**: cookie string, session key, or bearer token?
4. **Scope**: full CRUD chat client vs single endpoint wrapper?
5. **Mode**: live reverse-engineered vs educational demo package?

If official API exists and user needs production reliability, implement official client
*and* optionally document unofficial pattern as advanced/fragile.

### Phase 1 — Discover the HTTP contract

Load `references/reverse-engineering.md`.

Capture per action a **Endpoint Contract** table:

```markdown
| Action | Method | URL | Auth | Request body | Response type | Success codes |
|--------|--------|-----|------|--------------|---------------|---------------|
| list orgs | GET | /api/organizations | Cookie | — | JSON list | 200 |
| create chat | POST | .../chat_conversations | Cookie | `{uuid,name}` | JSON | 200/201 |
| send message | POST | /api/append_message | Cookie | prompt + ids | SSE stream | 200 |
| delete chat | DELETE | .../{id} | Cookie | optional | empty | 204 |
```

Minimum fields for each request:

- URL + method
- Required headers (`Cookie`, `User-Agent`, `Referer`, `Origin`, `Content-Type`, CSRF)
- JSON body schema
- Response shape (JSON keys or SSE event schema)
- Error shapes (401/403/429)

If the user has no captures yet, scaffold **demo mode** + mock server so work can proceed,
and leave `# TODO(network): replace with captured URL` markers.

### Phase 2 — Design the Client surface

Load `references/client-architecture.md`.

**Canonical public API** (match Claude-API naming when chat-shaped):

```python
class Client:
    def __init__(self, cookie: str, *, timeout: float = 60, base_url: str | None = None): ...
    def list_all_conversations(self) -> list[dict]: ...
    def create_new_chat(self, name: str = "") -> dict: ...  # returns {"uuid": ...}
    def send_message(self, prompt: str, conversation_id: str, attachment=None, timeout=None) -> str: ...
    def chat_conversation_history(self, conversation_id: str) -> dict: ...
    def delete_conversation(self, conversation_id: str) -> bool: ...
    def rename_chat(self, title: str, conversation_id: str) -> bool: ...
    def reset_all(self) -> bool: ...
```

Rename methods if the domain is not chat (e.g. `list_items`, `create_job`). Keep:

- One **Client** entrypoint
- **Session** with default headers
- **Bootstrap** call in `__init__` if org/account id is required
- Methods return plain Python types (str, dict, list, bool) — not raw Response

### Phase 3 — Implement Client + cookie automation

Order of implementation:

1. `__init__` + header builder + transport (`curl_cffi` if needed)
2. Bootstrap (`get_organization_id` / account)
3. `create_*` + `list_*`
4. Primary action (`send_message`) + SSE/JSON parser
5. History / delete / rename
6. **`cookie_collector.py`** — load `references/cookie-automation.md`
7. `Client.from_chrome()` / `from_browser()` / `from_store()`
8. CLI `usecases/collect_cookies.py`
9. Demo mode for offline tests

**HTTP stack defaults:**

| Need | Library |
|------|---------|
| Simple REST | `requests` or `httpx` |
| Browser TLS fingerprint | `curl_cffi` `impersonate="chrome110"` |
| Chrome cookie DB | `browser_cookie3` |
| CDP / interactive Chrome | `playwright` + `channel="chrome"` |

**Cookie rules (non-negotiable for live):**

- Default browser = **Google Chrome** (never default to Edge)
- Accept only jars with real session cookie (`sessionKey` / equivalent)
- Sources: env → store → Chrome DB → CDP :9222 → real profile → Playwright Chrome
- Persist to `~/.{app}/session.json`; never commit
- CLI flags: `--chrome`, `--cdp`, `--chrome-profile`, `--playwright`

### Phase 4 — Package layout

```
{package-name}/
├── pyproject.toml
├── README.md
├── docs/COOKIE_AUTOMATION.md
├── .env.example
├── {import_name}/
│   ├── __init__.py
│   ├── client.py             # from_chrome / from_browser / from_store
│   ├── cookie_collector.py   # REQUIRED for live
│   ├── exceptions.py
│   ├── parsing.py
│   └── constants.py          # capture revision + paths
├── usecases/
│   ├── console_chatbot.py
│   └── collect_cookies.py    # cookie CLI
├── examples/
│   ├── basic_usage.py
│   ├── live_smoke.py
│   └── show_api_working.py
├── captures/ENDPOINT_CONTRACTS.md
└── tests/
    ├── test_client_demo.py
    ├── test_parsing.py
    └── test_cookie_collector.py
```

```toml
[project.scripts]
my-chat = "usecases.console_chatbot:main"
my-cookies = "usecases.collect_cookies:main"
```

### Phase 5 — Usecases

1. **Cookie CLI** — prove auto collection (Chrome-first)
2. **Console chatbot** — uses `Client.from_browser()` / store
3. **live_smoke** — create → send → delete without printing cookies
4. Optional Discord / FastAPI gateway

### Phase 6 — Docs

README must include: disclaimer, Chrome cookie commands, `Client.from_chrome()` snippet,
capture fragility, official API alternative. Link `docs/COOKIE_AUTOMATION.md`.

### Phase 7 — Verify

```bash
pip install -e ".[dev]"
pytest -q
python examples/basic_usage.py
python -m usecases.collect_cookies --diagnose
# live (user logged into Chrome):
python -m usecases.collect_cookies --chrome
python -m examples.live_smoke
```

## Fast path: scaffold script

When the user wants a full package immediately:

```bash
python ~/.agents/skills/unofficial-api-client/scripts/scaffold_unofficial_api.py \
  --name my-service-api \
  --import-name my_service_api \
  --out ./my-service-api \
  --mode demo
```

Then customize `client.py` endpoints. Prefer the script over hand-rolling trees.

On Windows Grok paths, skill root may be:

- `C:\Users\<user>\.agents\skills\unofficial-api-client\`
- `C:\Users\<user>\.grok\skills\unofficial-api-client\`

Locate with the workspace skill list; use absolute path when running the script.

## Design patterns (cheat sheet)

### Cookie session client (Claude-API pattern)

```python
class Client:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Cookie": cookie,
            "Referer": f"{BASE}/chats",
            "Origin": BASE,
        })
        self.organization_id = self._get_organization_id()
```

### SSE completion join

```python
def parse_sse_completions(body: str) -> str:
    parts = []
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if not raw or raw == "[DONE]":
            continue
        data = json.loads(raw)
        if "completion" in data:
            parts.append(data["completion"])
    return "".join(parts)
```

### Env-based usage in apps

```python
import os
from my_service_api import Client

client = Client(os.environ["SERVICE_COOKIE"])
chat = client.create_new_chat()
print(client.send_message("Hello", chat["uuid"]))
```

### Chrome-first auto cookies (preferred live UX)

```python
from my_service_api import Client

api = Client.from_chrome()  # DB → CDP → store
cid = api.create_new_chat()["uuid"]
print(api.send_message("Hello", cid))
```

```bash
# Already logged into Chrome — quit Chrome first if DB locked:
my-cookies --chrome
# Or CDP:
# chrome.exe --remote-debugging-port=9222
my-cookies --cdp
# Interactive Google Chrome (not Edge):
my-cookies --playwright --channel chrome
```

## Decision tree: official vs unofficial

```
Is there a documented public API with keys?
  YES → implement official SDK/client first
        (mention unofficial only if user insists on free/web UI)
  NO  → unofficial Client is appropriate
        document fragility + auth source

Is this for production revenue app?
  YES → official API only
  NO  → unofficial OK for personal/learning with disclaimer
```

## Agent output expectations

When finishing a build, deliver:

1. Full package tree (not a single script dump)
2. Working `pip install -e .`
3. At least one runnable usecase
4. Tests for parsing + demo client path
5. README with disclaimer
6. Short note: how to swap demo endpoints for live captures

## Anti-patterns

| Avoid | Do instead |
|-------|------------|
| One giant `script.py` | Installable package + Client |
| Hardcoded cookie in source | `os.environ` / `.env` (gitignored) |
| Returning raw `Response` | Parse to str/dict/bool |
| No timeouts | Default timeout on every call |
| Silent failures | Typed exceptions + status text |
| Scraping HTML when XHR exists | Prefer JSON/XHR endpoints |
| Committing HAR files with cookies | Redact secrets |

## Example user intents → actions

| User says | Agent does |
|-----------|------------|
| "Build something like Claude-API" | Scaffold + Client + **cookie_collector Chrome-first** + CLI |
| "Auto collect cookies" / "use my Chrome login" | Implement `references/cookie-automation.md` fully |
| "Don't use Edge / use Chrome" | `channel="chrome"`, default browsers=`["chrome"]` |
| "Wrap this site's chat XHR" | Capture contracts → live Client → cookie auto → tests |
| "I just need packaging pattern" | Demo Client only |
| "Discord bot using unofficial Claude" | Warn ToS → official API first; else Client + cookies + bot |
| "Publish to PyPI" | Packaging ref + no secrets in package |

## Related skills

- Official AI integrations → prefer vendor SDK skill / `build-with-ai`
- HTTP API *server* design → FastAPI/Django patterns (not this skill)
- Browser automation for capture → `agent-browser` only when Network export is insufficient
