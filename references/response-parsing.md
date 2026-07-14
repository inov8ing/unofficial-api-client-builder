# Response parsing

Unofficial chat clients usually deal with **JSON** or **Server-Sent Events (SSE)**.

## Detect response type

```python
ctype = response.headers.get("Content-Type", "")
if "text/event-stream" in ctype or response.text.lstrip().startswith("data:"):
    return parse_sse(response.text)
return parse_json_answer(response.json())
```

## JSON answers

Common shapes:

```json
{"completion": "Hello"}
{"answer": "Hello"}
{"content": [{"type": "text", "text": "Hello"}]}
{"message": {"content": "Hello"}}
```

Helper:

```python
def parse_json_answer(data: dict) -> str:
    for key in ("completion", "answer", "text", "message", "content"):
        val = data.get(key)
        if isinstance(val, str):
            return val
        if isinstance(val, list) and val:
            first = val[0]
            if isinstance(first, dict) and "text" in first:
                return first["text"]
    raise ValueError(f"Unrecognized JSON shape: {list(data)[:10]}")
```

## SSE (Claude-API pattern)

Wire format:

```text
data: {"completion": "Hel"}
data: {"completion": "lo"}
data: [DONE]
```

Parser:

```python
import json
import re

def parse_sse_completions(body: str, field: str = "completion") -> str:
    body = re.sub(r"\n+", "\n", body).strip()
    parts: list[str] = []
    for line in body.split("\n"):
        line = line.strip()
        if not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if not raw or raw == "[DONE]":
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if field in event:
            parts.append(str(event[field]))
        elif "delta" in event and isinstance(event["delta"], str):
            parts.append(event["delta"])
        elif "text" in event:
            parts.append(str(event["text"]))
    return "".join(parts)
```

### Streaming to the caller (optional)

For UIs, yield chunks:

```python
def iter_sse(response):
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if raw == "[DONE]":
            break
        yield json.loads(raw)
```

Requires `stream=True` on the request.

## Multipart upload responses

```python
files = {
    "file": (filename, open(path, "rb"), content_type),
    "orgUuid": (None, organization_id),
}
# Do not force Content-Type: application/json on this request
resp = session.post(url, files=files, headers={k: v for k, v in headers.items() if k.lower() != "content-type"})
meta = resp.json()  # file_name, extracted_content, etc.
```

Text files sometimes skip upload and inline `extracted_content` (Claude-API does this for `.txt`).

## Error bodies

Always include a short body prefix in exceptions:

```python
raise APIError(status, response.text[:500])
```

## Unit tests (no network)

```python
def test_sse_join():
    body = 'data: {"completion": "A"}\ndata: {"completion": "B"}\n'
    assert parse_sse_completions(body) == "AB"
```

Ship these tests in every package—the parser is pure and high-value.
