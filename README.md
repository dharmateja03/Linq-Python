# Linq API V3 Python API Library

<!-- x-release-please-start-version -->

The Linq API V3 Python library provides convenient access to the Linq API V3 REST API from Python applications.

<!-- x-release-please-end -->

## Installation

```bash
pip install linq-python
```

## Requirements

Python 3.10+

## Usage

```python
from linq import Client

client = Client(api_key="My API Key")

chat = client.chats.create(
    {
        "from": "+12052535597",
        "to": ["+12052532136"],
        "message": {
            "parts": [{"type": "text", "value": "Hello! How can I help you today?"}]
        },
    }
)

print(chat)
```

Environment variables are supported:

- `LINQ_API_V3_API_KEY`
- `LINQ_API_V3_BASE_URL` (defaults to `https://api.linqapp.com/api/partner/`)

## Pagination

```python
page = client.chats.list({"limit": 20})
print(page.items)

next_page = page.get_next_page()

for chat in client.chats.list_auto_paging({"limit": 20}):
    print(chat["id"])
```

## Webhook Signature Verification

```python
valid = client.webhooks.verify_signature(
    signing_secret="whsec_...",
    payload=raw_body_bytes,
    timestamp=headers["X-Webhook-Timestamp"],
    signature=headers["X-Webhook-Signature"],
)
```

## Request Options

Each method accepts `options=RequestOptions(...)` for per-request overrides:

- `headers`
- `query`
- `timeout`
- `max_retries`
- `raw_body` + `content_type`

## Development

```bash
./scripts/bootstrap
./scripts/lint
./scripts/test
```
