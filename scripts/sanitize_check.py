#!/usr/bin/env python3
"""Repository sanitization checker for smart-home examples.

The goal is to catch accidental leaks before publishing: tokens, captured payloads,
real IPs/domains, serial numbers, and full HAR/storage exports. It is deliberately
conservative; allowlist false positives in code comments instead of weakening the
patterns globally.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

DEFAULT_EXCLUDES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("JWT-like token", re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{30,}\b")),
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Chinese mainland phone number", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("private IPv4 address", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b")),
    ("payload_hex assignment", re.compile(r"(?i)\bpayload[_-]?hex\b\s*[:=]")),
    ("long hex payload", re.compile(r"\b[0-9a-fA-F]{80,}\b")),
    ("authorization header/value", re.compile(r"(?i)\bAuthorization\b\s*[:=]")),
    ("device SN placeholder accidentally replaced", re.compile(r"\b(?:FB485|SN)[A-Za-z0-9_-]{6,}\b")),
]

BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in DEFAULT_EXCLUDES for part in path.parts):
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="scan repo for common sensitive smart-home leaks")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings: list[str] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(root)
        for line_no, line in enumerate(text.splitlines(), 1):
            # Allow documentation to mention these labels without showing values.
            if "# sanitize-check: ignore" in line:
                continue
            for name, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{line_no}: {name}: {line.strip()[:160]}")

    if findings:
        print("Potential sensitive content found:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("OK: no common sensitive smart-home leaks detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
