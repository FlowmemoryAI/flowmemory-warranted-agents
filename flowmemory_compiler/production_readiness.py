"""Production-readiness gates for FlowMemory Warranted Agents."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .launch_packet import build_launch_packet


PRODUCTION_GATES: tuple[dict[str, str], ...] = (
    {
        "gate": "real_wallet_adapter",
        "why": "A production system must bind user and agent actions to real wallet infrastructure.",
    },
    {
        "gate": "real_payment_or_bond_rail",
        "why": "The local BondLedger is not production custody, escrow, settlement, or wallet execution.",
    },
    {
        "gate": "persistent_receipt_store",
        "why": "Production receipts need durable storage, retention policy, backup, and replay protection.",
    },
    {
        "gate": "reader_verifier_service",
        "why": "Production evidence needs a reader/verifier that attaches receipt facts and finality metadata.",
    },
    {
        "gate": "key_management_and_secret_rotation",
        "why": "Production adapters need key isolation, secret rotation, and signer boundaries.",
    },
    {
        "gate": "observability_and_alerting",
        "why": "Runtime failures, adapter failures, settlement anomalies, and claim-gate failures need alerts.",
    },
    {
        "gate": "incident_response_runbook",
        "why": "Production operation needs an owner, escalation path, freeze path, and postmortem process.",
    },
    {
        "gate": "security_review_or_audit",
        "why": "A production release needs independent review of adapter boundaries, funds paths, and privacy claims.",
    },
    {
        "gate": "load_and_replay_testing",
        "why": "The runtime state machine needs stress, replay, duplicate, and recovery tests beyond local fixtures.",
    },
    {
        "gate": "privacy_backend_selected",
        "why": "The local PrivateCompute layer is not zero-knowledge, TEE-backed, or production private compute.",
    },
)


def build_production_readiness_packet(
    flowcompiler_cases: list[dict[str, Any]],
    root: Path,
    *,
    satisfied_gates: set[str] | None = None,
) -> dict[str, Any]:
    satisfied_gates = satisfied_gates or set()
    launch = build_launch_packet(flowcompiler_cases, root)
    gates = []
    for gate in PRODUCTION_GATES:
        passed = gate["gate"] in satisfied_gates
        gates.append(
            {
                "gate": gate["gate"],
                "passed": passed,
                "status": "SATISFIED" if passed else "BLOCKING",
                "why": gate["why"],
            }
        )
    local_ready = launch["readiness"]["passed"]
    production_ready = local_ready and all(gate["passed"] for gate in gates)
    packet = {
        "schema": "flowmemory.production_readiness_packet.v0",
        "package": "flowmemory-warranted-agents",
        "localArchitectureReady": local_ready,
        "productionReady": production_ready,
        "releaseMode": "PRODUCTION_READY" if production_ready else "LOCAL_ARCHITECTURE_READY_ONLY",
        "launchPacketHash": launch["packetHash"],
        "blockingGateCount": sum(1 for gate in gates if not gate["passed"]),
        "productionGates": gates,
        "nextRequiredMilestone": "external_adapter_and_operations_validation" if not production_ready else "production_release_candidate",
        "notClaims": [
            "not_production_custody",
            "not_wallet_enforcement",
            "not_production_settlement",
            "not_production_private_compute",
            "not_security_audit",
            "not_production_verifier",
        ],
    }
    packet["packetHash"] = _hash_dict(packet)
    return packet


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
