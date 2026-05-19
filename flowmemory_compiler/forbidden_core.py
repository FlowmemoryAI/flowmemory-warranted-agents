"""Minimal deterministic forbidden cores for FlowCompiler faults."""

from __future__ import annotations

from typing import Any


def forbidden_core(fault: str, atoms: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "flowmemory.forbidden_core.v0",
        "fault": fault,
        "minimalCore": atoms,
        "oneMinimal": True,
    }


def atom(path: str, value: Any) -> dict[str, Any]:
    return {"path": path, "value": value}

