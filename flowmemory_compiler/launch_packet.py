"""Public launch packet for FlowMemory Warranted Agents."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import __version__
from .claim_gate import scan_claims
from .release_transcript import build_release_transcript


def build_launch_packet(flowcompiler_cases: list[dict[str, Any]], root: Path) -> dict[str, Any]:
    transcript = build_release_transcript(flowcompiler_cases)
    claims = scan_claims(root)
    readiness_checks = [
        {
            "check": "claim_gate_passed",
            "passed": claims["passed"],
            "detail": f"unguardedOverclaims={len(claims['unguardedOverclaims'])}",
        },
        {
            "check": "adapter_conformance_passed",
            "passed": transcript["adapterConformance"]["passed"],
            "detail": f"checks={transcript['adapterConformance']['checkCount']}",
        },
        {
            "check": "runtime_has_success_and_failure_paths",
            "passed": set(transcript["agentRuntime"]["finalStatuses"]) == {"WARRANTY_RELEASED", "USER_PAID_FROM_BOND"},
            "detail": ",".join(transcript["agentRuntime"]["finalStatuses"]),
        },
        {
            "check": "flowcompiler_rejects_all_bundled_impossible_histories",
            "passed": transcript["flowCompiler"]["escapedImpossibleHistories"] == 0,
            "detail": f"rejected={transcript['flowCompiler']['invalidRejected']}/{transcript['flowCompiler']['invalidTotal']}",
        },
    ]
    packet = {
        "schema": "flowmemory.warranted_agents_launch_packet.v0",
        "package": "flowmemory-warranted-agents",
        "version": __version__,
        "coreLine": transcript["coreLine"],
        "releaseTranscriptHash": transcript["transcriptHash"],
        "readiness": {
            "passed": all(item["passed"] for item in readiness_checks),
            "checks": readiness_checks,
        },
        "commands": [
            "python -m unittest",
            "python -m flowmemory_compiler.cli release-transcript --pretty",
            "python -m flowmemory_compiler.cli adapter-conformance-demo --pretty",
            "python -m flowmemory_compiler.cli claim-gate --pretty",
        ],
        "notClaims": transcript["notClaims"],
    }
    packet["packetHash"] = _hash_dict(packet)
    return packet


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
