# Client architecture

## Design goals

1. **One class** is the public surface (`Client`)
2. Methods map 1:1 to user-visible actions
3. Callers never touch raw HTTP unless debugging
4. Package is installable and importable from any project
5. Demo/mock path exists for offline tests

## Class responsibilities

```
Client
├── auth state (cookie/token)
├── session + default headers
├── bootstrap ids (org, user, device)
├── resource methods (CRUD + send)
└── private helpers (_parse_sse, _request, _upload)
```

Keep parsing and exceptions in separate modules when `client.py` exceeds ~300 lines.

## Suggested module split

```
pkg/
  __init__.py      # export Client, __version__, exceptions
  client.py        # Client
  exceptions.py    # AuthError, RateLimitError, APIError
  parsing.py       # parse_sse, parse_json_message
  models.py        # optional TypedDict / dataclass for responses
  constants.py     # BASE_URL, USER_AGENT, DEFAULT_TIMEOUT
```

## Session and headers

```python
def _default_headers(self) -> dict[str, str]:
    return {
        "User-Agent": self.user_agent,
        "Accept": "application/json, text/event-stream",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Cookie": self.cookie,
        "Origin": self.base_url,
        "Referer": f"{self.base_url}/",
    }
```

Use `session.headers.update(...)` once. Override per-call only when needed (multipart upload often drops/overrides Content-Type).

## Core request helper

```python
def _request(self, method: str, path: str, **kwargs) -> requests.Response:
    url = path if path.startswith("http") else f"{self.base_url}{path}"
    kwargs.setdefault("timeout", self.timeout)
    resp = self.session.request(method, url, **kwargs)
    if resp.status_code in (401, 403):
        raise AuthError(resp.status_code, resp.text[:500])
    if resp.status_code == 429:
        raise RateLimitError(resp.status_code, resp.text[:500])
    if resp.status_code >= 400:
        raise APIError(resp.status_code, resp.text[:500])
    return resp
```

## Method design rules

| Rule | Why |
|------|-----|
| Accept domain args, not raw headers | UX of Claude-API |
| Return plain types | Easy usecases |
| `send_message` → `str` answer | Chat ergonomics |
| create → `dict` with `uuid` | Pass id into next call |
| delete → `bool` | Simple success check |
| Optional `timeout` on long ops | Streams can hang |
| Optional `attachment` path | File flows |

## UUID generation

Some UIs require client-generated UUIDs for new chats:

```python
import uuid
chat_id = str(uuid.uuid4())
payload = {"uuid": chat_id, "name": name}
```

## Dual mode (recommended for scaffolds)

```python
def __init__(self, cookie: str, *, base_url: str | None = None, demo: bool = False):
    self.demo = demo or base_url is None
    ...
```

- **demo**: in-memory store; no network; tests pass CI
- **live**: real endpoints

## Thread safety

`requests.Session` is not fully thread-safe for concurrent use. Document:

- One Client per thread, or
- Use a lock around `_request`, or
- Prefer httpx with care

## Async variant (optional)

If user needs async:

```python
class AsyncClient:
    def __init__(...):
        self.session = httpx.AsyncClient(headers=..., timeout=...)
    async def send_message(...): ...
```

Do not mix sync and async in one class without clear naming.

## Versioning the library

- Bump minor when site endpoints change in breaking ways
- Pin nothing to “site version”; document last verified date in README:

```markdown
Last verified against site UI: 2026-07-12
```

## Mapping Claude-API methods

| Claude-API | Generic name | Notes |
|------------|--------------|-------|
| `get_organization_id` | `_bootstrap` | private |
| `list_all_conversations` | `list_*` | |
| `create_new_chat` | `create_*` | returns uuid |
| `send_message` | primary action | parse stream |
| `chat_conversation_history` | `get_*` | |
| `delete_conversation` | `delete_*` | bool |
| `rename_chat` | `rename_*` | bool |
| `reset_all` | bulk delete | |
| `upload_attachment` | private helper | |

## Minimal Client skeleton

See `assets/templates/client.py.tmpl`.
