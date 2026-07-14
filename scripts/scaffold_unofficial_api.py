#!/usr/bin/env python3
"""
Scaffold an installable unofficial-style API client package.

Usage:
  python scaffold_unofficial_api.py --name my-service-api --out ./my-service-api
  python scaffold_unofficial_api.py --name demo-api --import-name demo_api --mode demo
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


def to_import_name(project_name: str) -> str:
    name = project_name.strip().lower().replace("-", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    if not name or name[0].isdigit():
        raise SystemExit(f"Invalid import name derived from {project_name!r}")
    return name


def to_script_name(project_name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", project_name.strip().lower()) + "-chat"


def read_template(skill_root: Path, name: str) -> str:
    path = skill_root / "assets" / "templates" / name
    if not path.exists():
        raise SystemExit(f"Missing template: {path}")
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  + {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold unofficial API client package")
    parser.add_argument("--name", required=True, help="Project/distribution name (e.g. my-service-api)")
    parser.add_argument("--import-name", default=None, help="Python package import name")
    parser.add_argument("--out", default=None, help="Output directory (default: ./<name>)")
    parser.add_argument("--service-name", default="Example Service", help="Human service name for README")
    parser.add_argument(
        "--mode",
        choices=("demo", "live"),
        default="demo",
        help="demo: works offline; live: expects SERVICE_COOKIE",
    )
    parser.add_argument(
        "--skill-root",
        default=None,
        help="Path to unofficial-api-client skill (auto-detected if omitted)",
    )
    args = parser.parse_args()

    import_name = args.import_name or to_import_name(args.name)
    script_name = to_script_name(args.name)
    out = Path(args.out or args.name).resolve()
    skill_root = Path(args.skill_root) if args.skill_root else Path(__file__).resolve().parents[1]

    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"Refusing to write into non-empty directory: {out}")

    print(f"Scaffolding {args.name} → {out}")
    out.mkdir(parents=True, exist_ok=True)

    # pyproject
    pyproject = read_template(skill_root, "pyproject.toml.tmpl")
    pyproject = (
        pyproject.replace("{{PROJECT_NAME}}", args.name)
        .replace("{{IMPORT_NAME}}", import_name)
        .replace("{{SCRIPT_NAME}}", script_name)
    )
    write(out / "pyproject.toml", pyproject)

    # package files
    client = read_template(skill_root, "client.py.tmpl")
    if args.mode == "demo":
        # default Client(demo=True) when no cookie — already in template
        pass
    write(out / import_name / "client.py", client)
    write(out / import_name / "exceptions.py", read_template(skill_root, "exceptions.py.tmpl"))
    write(out / import_name / "parsing.py", read_template(skill_root, "parsing.py.tmpl"))
    write(
        out / import_name / "__init__.py",
        f'''"""Unofficial client package for {args.service_name}."""\n'''
        f"from .client import Client\n"
        f"from .exceptions import APIError, AuthError, RateLimitError\n\n"
        f'__all__ = ["Client", "APIError", "AuthError", "RateLimitError"]\n'
        f'__version__ = "0.1.0"\n',
    )

    # usecases
    chatbot = read_template(skill_root, "console_chatbot.py.tmpl").replace(
        "IMPORT_NAME", import_name
    )
    write(out / "usecases" / "__init__.py", "# usecases\n")
    write(out / "usecases" / "console_chatbot.py", chatbot)

    # examples + tests
    write(
        out / "examples" / "basic_usage.py",
        f'''from {import_name} import Client\n\n'''
        f"api = Client(demo=True)\n"
        f'chat = api.create_new_chat()\n'
        f'cid = chat["uuid"]\n'
        f'print(api.send_message("Hello!", cid))\n'
        f"print(api.list_all_conversations())\n"
        f"api.delete_conversation(cid)\n",
    )
    write(
        out / "tests" / "test_parsing.py",
        f'''from {import_name}.parsing import parse_sse_completions\n\n'''
        f"def test_sse():\n"
        f'    body = \'data: {{"completion": "Hel"}}\\ndata: {{"completion": "lo"}}\\n\'\n'
        f'    assert parse_sse_completions(body) == "Hello"\n',
    )
    write(
        out / "tests" / "test_client_demo.py",
        f'''from {import_name} import Client\n\n'''
        f"def test_demo_chat():\n"
        f"    c = Client(demo=True)\n"
        f'    cid = c.create_new_chat()["uuid"]\n'
        f'    assert isinstance(c.send_message("hi", cid), str)\n'
        f"    assert len(c.chat_conversation_history(cid)[\"chat_messages\"]) == 2\n",
    )

    # docs / meta
    readme = (
        read_template(skill_root, "README.md.tmpl")
        .replace("{{PROJECT_NAME}}", args.name)
        .replace("{{IMPORT_NAME}}", import_name)
        .replace("{{SCRIPT_NAME}}", script_name)
        .replace("{{SERVICE_NAME}}", args.service_name)
        .replace("{{DATE}}", date.today().isoformat())
    )
    write(out / "README.md", readme)
    write(
        out / ".env.example",
        "SERVICE_COOKIE=\n# API_BASE_URL=https://example.com\n",
    )
    write(
        out / ".gitignore",
        "\n".join(
            [
                ".venv/",
                "venv/",
                "__pycache__/",
                "*.py[cod]",
                "*.egg-info/",
                "dist/",
                "build/",
                ".env",
                "*.har",
                "cookies.txt",
                ".pytest_cache/",
                "",
            ]
        ),
    )
    write(
        out / "LICENSE",
        "MIT License\n\nCopyright (c) "
        + str(date.today().year)
        + "\n\nPermission is hereby granted, free of charge, to any person obtaining a copy "
        "of this software and associated documentation files (the \"Software\"), to deal "
        "in the Software without restriction...\n",
    )
    write(
        out / "setup.py",
        'from setuptools import setup\n\nsetup()\n',
    )

    print("\nDone. Next:")
    print(f"  cd {out}")
    print("  python -m venv .venv")
    print("  # activate venv, then:")
    print('  pip install -e ".[dev]"')
    print("  pytest -q")
    print("  python examples/basic_usage.py")
    if args.mode == "live":
        print("  # set SERVICE_COOKIE and replace TODO paths in client.py")


if __name__ == "__main__":
    main()
