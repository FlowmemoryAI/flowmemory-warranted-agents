"""Local registry and discovery for warranted agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent_framework import AgentManifest, WorkRequest, demo_manifest, demo_request, manifest_to_public


@dataclass(frozen=True)
class AgentMatch:
    agent_id: str
    display_name: str
    manifest_hash: str
    eligible: bool
    matched_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    requested_bond_units: int
    max_bond_units: int
    reasons: tuple[str, ...]


class AgentRegistry:
    """Deterministic in-memory registry for launch demos and tests."""

    def __init__(self) -> None:
        self._manifests: dict[str, AgentManifest] = {}

    def register(self, manifest: AgentManifest) -> None:
        if manifest.agent_id in self._manifests:
            raise ValueError(f"agent already registered: {manifest.agent_id}")
        self._manifests[manifest.agent_id] = manifest

    def list_agents(self) -> list[dict[str, Any]]:
        return [manifest_to_public(manifest) for manifest in self._manifests.values()]

    def match(self, request: WorkRequest) -> list[AgentMatch]:
        matches = [_match_manifest(manifest, request) for manifest in self._manifests.values()]
        return sorted(matches, key=lambda item: (not item.eligible, item.display_name))


def run_registry_demo() -> dict[str, Any]:
    registry = AgentRegistry()
    registry.register(demo_manifest())
    registry.register(
        AgentManifest(
            agent_id="agent:cheap-claim-demo",
            developer_id="developer:demo",
            display_name="Cheap Claim Agent",
            capabilities=("research_delivery",),
            supported_evidence=("PaymentReceiptEnvelope",),
            max_bond_units=10_00,
            privacy_modes=("public_log",),
            settlement_modes=("status_only",),
        )
    )
    request = demo_request()
    matches = registry.match(request)
    return {
        "schema": "flowmemory.agent_registry_demo.v0",
        "request": {
            "requestId": request.request_id,
            "requiredEvidence": list(request.required_evidence),
            "requestedBondUnits": request.requested_bond_units,
        },
        "agents": registry.list_agents(),
        "matches": [match_to_public(match) for match in matches],
        "notClaims": [
            "not_agent_marketplace",
            "not_identity_attestation",
            "not_reputation_system",
            "not_wallet_enforcement",
        ],
    }


def match_to_public(match: AgentMatch) -> dict[str, Any]:
    return {
        "agentId": match.agent_id,
        "displayName": match.display_name,
        "manifestHash": match.manifest_hash,
        "eligible": match.eligible,
        "matchedEvidence": list(match.matched_evidence),
        "missingEvidence": list(match.missing_evidence),
        "requestedBondUnits": match.requested_bond_units,
        "maxBondUnits": match.max_bond_units,
        "reasons": list(match.reasons),
    }


def _match_manifest(manifest: AgentManifest, request: WorkRequest) -> AgentMatch:
    manifest_public = manifest_to_public(manifest)
    supported = set(manifest.supported_evidence)
    required = set(request.required_evidence)
    missing = tuple(sorted(required - supported))
    matched = tuple(sorted(required & supported))
    reasons: list[str] = []
    if missing:
        reasons.append("missing_required_evidence")
    if request.requested_bond_units > manifest.max_bond_units:
        reasons.append("bond_request_exceeds_manifest_limit")
    if request.promise_type not in {"obligation_completion", "work_warranty"}:
        reasons.append("unsupported_promise_type")
    if not reasons:
        reasons.append("eligible_for_warranted_quote")
    return AgentMatch(
        agent_id=manifest.agent_id,
        display_name=manifest.display_name,
        manifest_hash=manifest_public["manifestHash"],
        eligible=reasons == ["eligible_for_warranted_quote"],
        matched_evidence=matched,
        missing_evidence=missing,
        requested_bond_units=request.requested_bond_units,
        max_bond_units=manifest.max_bond_units,
        reasons=tuple(reasons),
    )
