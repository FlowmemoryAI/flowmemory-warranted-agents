"""Public claim gate for FlowMemory Warranted Agents copy."""

from __future__ import annotations

from pathlib import Path
from typing import Any


RISK_PHRASES = (
    "custody",
    "escrow",
    "fund protection",
    "protects funds",
    "wallet enforcement",
    "x402 replacement",
    "production adjudication",
    "production settlement",
    "production verifier",
    "production private compute",
    "full privacy",
    "zero-knowledge",
    "work-quality proof",
    "semantic truth",
    "profit guarantee",
    "guarantees profit",
    "prevents fraud",
    "live base",
)

GUARD_WORDS = (
    "not",
    "no ",
    "does not",
    "do not",
    "must not",
    "without",
    "non-claim",
    "non-claims",
    "not_",
    "boundary",
    "boundaries",
)

GUARD_SECTION_MARKERS = (
    "non-claims",
    "non-claims:",
    "does not claim",
    "do not claim",
    "not safe to claim",
    "what not to claim",
    "overclaims to avoid",
    "the framework must not sign",
    "must not sign",
)


DEFAULT_SCAN_PATHS = (
    "README.md",
    "docs",
    "specs",
)


def scan_claims(root: Path) -> dict[str, Any]:
    files = _files(root)
    guarded: list[dict[str, Any]] = []
    unguarded: list[dict[str, Any]] = []
    for path in files:
        relative = str(path.relative_to(root)).replace("\\", "/")
        in_guarded_section = False
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lower = _strip_inline_code(line).lower()
            stripped = lower.strip()
            if stripped.startswith("#") and not _is_guard_section_marker(lower):
                in_guarded_section = False
            if _is_guard_section_marker(lower):
                in_guarded_section = True
            for phrase in RISK_PHRASES:
                if phrase not in lower:
                    continue
                item = {
                    "file": relative,
                    "line": line_number,
                    "phrase": phrase,
                    "text": line.strip(),
                }
                if in_guarded_section or _is_guarded(lower):
                    guarded.append(item)
                else:
                    unguarded.append(item)
    return {
        "schema": "flowmemory.claim_gate.v0",
        "filesChecked": len(files),
        "guardedRiskMentions": len(guarded),
        "unguardedOverclaims": unguarded,
        "passed": not unguarded,
    }


def _files(root: Path) -> list[Path]:
    results: list[Path] = []
    for entry in DEFAULT_SCAN_PATHS:
        path = root / entry
        if path.is_file():
            results.append(path)
        elif path.is_dir():
            results.extend(sorted(item for item in path.rglob("*") if item.suffix.lower() in {".md", ".txt"}))
    return sorted(results)


def _is_guarded(line: str) -> bool:
    return any(word in line for word in GUARD_WORDS)


def _is_guard_section_marker(line: str) -> bool:
    return any(marker in line for marker in GUARD_SECTION_MARKERS)


def _strip_inline_code(line: str) -> str:
    parts = line.split("`")
    return "".join(part for index, part in enumerate(parts) if index % 2 == 0)
