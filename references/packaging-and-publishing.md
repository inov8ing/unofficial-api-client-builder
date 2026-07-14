# Packaging and publishing

## Modern default: pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "my-service-api"
version = "0.1.0"
description = "Unofficial client for Example Service (not affiliated)"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
dependencies = [
  "requests>=2.28.0",
  # "curl_cffi>=0.5.0",  # if browser impersonation needed
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[project.scripts]
my-service-chat = "usecases.console_chatbot:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["my_service_api*", "usecases*"]
```

## Local install

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
```

## Using from another project

```bash
pip install -e /path/to/my-service-api
# or later
pip install my-service-api
```

```python
from my_service_api import Client
```

## setup.py (optional compatibility)

```python
from setuptools import setup
setup()  # defers to pyproject.toml
```

## Version policy

- `0.x` while reverse-engineered and unstable
- Changelog entry when site breaks client
- Tag “last verified” date in README

## PyPI publish checklist

```bash
pip install build twine
python -m build
twine check dist/*
# twine upload dist/*
```

Before upload:

- [ ] Unique project name on PyPI
- [ ] Disclaimer in long description
- [ ] No secrets in package data
- [ ] LICENSE file present
- [ ] `python_requires` set

## Git hygiene

```gitignore
.venv/
__pycache__/
*.egg-info/
dist/
build/
.env
*.har
cookies.txt
.pytest_cache/
```

## README sections (required)

1. Title + unofficial badge/disclaimer
2. Install
3. Auth setup (env var)
4. Quickstart
5. API method reference
6. Usecases
7. Limitations / official alternative
8. License

## Optional monorepo note

If user only wants a module inside an existing app, still use package layout:

```
app/
  integrations/
    example_client/
      __init__.py
      client.py
```

Prefer full installable package when they say “like Claude-API” or “reusable library”.
