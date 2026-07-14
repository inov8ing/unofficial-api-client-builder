# Auth patterns for unofficial clients

## 1. Full Cookie header (Claude-API style)

**Source:** DevTools → Network → any authenticated request → Request Headers → `cookie`.

```python
Client(cookie=os.environ["SERVICE_COOKIE"])
# session.headers["Cookie"] = cookie
```

Notes:

- Often a long string with multiple key=value pairs separated by `; `
- Cookies expire; 401 means “refresh cookie from browser”
- Never commit; use env / secret manager

## 2. Single session key

Some docs say “sessionKey=... only”. Prefer full cookie if requests fail.

```python
cookie = f"sessionKey={os.environ['SESSION_KEY']}"
```

## 3. Bearer token (official or semi-official)

```python
headers["Authorization"] = f"Bearer {token}"
# omit Cookie
```

## 4. CSRF / anti-forgery

Look for:

- `x-csrf-token`
- `x-xsrf-token`
- cookie `csrf` + matching header

Flow:

1. GET a page or bootstrap endpoint
2. Read token from cookie or HTML/JSON
3. Send header on mutating requests

## 5. Organization / workspace scope

After login cookie works:

```python
orgs = session.get("/api/organizations").json()
self.organization_id = orgs[0]["uuid"]
```

Pass `organization_uuid` in bodies or path segments.

## 6. Device / client identifiers

Some apps require:

- `x-device-id`
- `anthropic-client` style headers
- fixed client version strings

Copy from a successful browser request; parameterize if they rotate.

## 7. OAuth refresh (advanced)

If Network shows refresh token calls:

- Store refresh token securely
- Implement `_ensure_access_token()` before each request
- Still document unofficial status

## Env conventions

```bash
# .env.example
SERVICE_COOKIE=
# or
SERVICE_TOKEN=
API_BASE_URL=https://example.com
```

```python
import os
cookie = os.environ.get("SERVICE_COOKIE") or os.environ["COOKIE"]
```

## Failure modes

| Symptom | Likely cause |
|---------|----------------|
| 401/403 | Expired cookie / missing CSRF |
| 200 HTML login page | Not authenticated; following redirects to login |
| 429 | Rate limited |
| Empty SSE | Wrong Accept header or model payload |
| Cloudflare challenge body | Bot detection — try curl_cffi, or stop |

## Security for agents

- If user pastes a cookie in chat, warn them to rotate after
- Strip cookies from exception messages
- `.gitignore` must include `.env`, `*.har`, `cookies.txt`
