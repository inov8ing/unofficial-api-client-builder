# Reverse-engineering web UI APIs

How Claude-API-style libraries discover endpoints: **the browser is the source of truth**.

## Tools

| Tool | Use |
|------|-----|
| Chrome/Edge/Firefox DevTools → Network | Primary: XHR/Fetch capture |
| Copy as cURL | Reproduce one request quickly |
| mitmproxy / Charles | Mobile apps, non-browser clients |
| HAR export | Share captures (redact cookies first) |

## Capture procedure

1. Log into the site normally.
2. Open DevTools → **Network**.
3. Enable **Preserve log**. Filter: **Fetch/XHR**.
4. Perform one user action (e.g. send a chat message).
5. Click the new request; record:

```text
Request URL:
Request Method:
Status Code:
Request Headers:
  - cookie / authorization
  - content-type
  - referer / origin
  - any x-csrf / x-api headers
Request Payload (JSON):
Response Headers (content-type: json vs event-stream):
Response body (sample, redacted):
```

6. Repeat for: list, create, delete, rename, upload, history.

## What to look for

### REST JSON APIs (easy)

- Paths like `/api/...`, `/backend/...`, `/v1/...`
- `application/json` request and response
- UUID resource ids in path or body

### Streaming chat (Claude-API style)

- `Accept: text/event-stream` or `Content-Type: text/event-stream`
- Body lines: `data: {"completion":"..."}` or `data: {"delta":...}`
- Client must concatenate chunks

### GraphQL

- Single `/graphql` endpoint
- Different `operationName` / query strings
- Still wrap as methods on Client (`send_message` builds the query)

### WebSocket

- `ws://` / `wss://` upgrade
- Different client design (persistent connection); document clearly

## From cURL to Python

Browser “Copy as cURL” → translate:

```bash
curl 'https://example.com/api/foo' \
  -H 'cookie: session=abc' \
  -H 'content-type: application/json' \
  --data-raw '{"text":"hi"}'
```

```python
session.post(
    "https://example.com/api/foo",
    headers={"Cookie": cookie, "Content-Type": "application/json"},
    json={"text": "hi"},
    timeout=60,
)
```

## Anti-bot and fingerprinting

If plain `requests` gets 403 / empty / challenge pages:

1. Match **User-Agent**, **Referer**, **Origin**, **Accept-Language** exactly.
2. Include full **Cookie** jar (not one key only).
3. Try `curl_cffi.requests` with `impersonate="chrome110"` (TLS fingerprint).
4. Respect rate limits; backoff on 429.
5. Do **not** automate CAPTCHA solving as part of this skill.

## Organization / account bootstrap

Many apps need a tenant id first (Claude-API pattern):

```
GET /api/organizations → [ { "uuid": "..." } ]
then
GET /api/organizations/{org}/chat_conversations
```

Cache `organization_id` on the Client after `__init__`.

## Building the contract table

Before coding methods, write:

```markdown
### send_message
- POST https://host/api/append_message
- Headers: Cookie, Content-Type, Origin, Referer, Accept: text/event-stream
- Body: { organization_uuid, conversation_uuid, text, attachments? }
- Response: SSE stream of { completion: string }
- Errors: 401 expired cookie, 429 rate limit
```

## When capture is incomplete

Scaffold Client methods with:

```python
raise NotImplementedError("Capture Network tab for POST /api/... then implement")
```

Or implement **demo mode** so package installs and tests pass offline.

## Redaction checklist before sharing HAR/cURL

- [ ] Cookie header
- [ ] Authorization bearer
- [ ] CSRF tokens tied to session
- [ ] Personal message content
- [ ] Account emails / phone numbers
