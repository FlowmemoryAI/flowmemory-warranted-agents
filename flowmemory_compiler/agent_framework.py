"""FlowMemory warranted-agent framework.

This module wires the primitives together:

AgentManifest -> WorkRequest -> PolicyCard -> AgentProposal -> FlowBond -> FlowPulse -> PulsePass

It is deliberately local and deterministic. It does not run a wallet, custody
funds, call x402, or verify production chain data.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from .flowbond import AgentWorkOutcome, EvidenceEnvelope, settle_warranted_action
from .policycards import PolicyCard, policy_hash, public_policy_view
from .pulsepass import ScopedProofRequest, build_pulsepass, scoped_proof


@dataclass(frozen=True)
class AgentManifest:
    agent_id: str
    developer_id: str
    display_name: str
    capabilities: tuple[str, ...]
    supported_evidence: tuple[str, ...]
    max_bond_units: int
    privacy_modes: tuple[str, ...]
    settlement_modes: tuple[str, ...]


@dataclass(frozen=True)
class WorkRequest:
    request_id: str
    user_id: str
    title: str
    promise_type: str
    obligation_id: str
    required_evidence: tuple[str, ...]
    max_spend_units: int
    requested_bond_units: int
    expires_at: int


@dataclass(frozen=True)
class AgentProposal:
    proposal_id: str
    agent_id: str
    request_id: str
    policy_hash: str
    bond_units: int
    promised_evidence: tuple[str, ...]
    proposal_hash: str


def demo_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id="agent:work-warranty-demo",
        developer_id="developer:flowmemory-demo",
        display_name="FlowMemory Warranted Research Agent",
        capabilities=("research_delivery", "receipt_memory", "warranted_action"),
        supported_evidence=(
            "PaymentReceiptEnvelope",
            "WorkDeliveryEnvelope",
            "AcceptanceEnvelope",
            "FlowPulseReceiptEnvelope",
        ),
        max_bond_units=50_00,
        privacy_modes=("local_vault", "scoped_proof"),
        settlement_modes=("release_bond_to_agent", "pay_bond_to_user"),
    )


def demo_request() -> WorkRequest:
    return WorkRequest(
        request_id="request:research-artifact-001",
        user_id="user:local-demo",
        title="Deliver the requested research artifact",
        promise_type="obligation_completion",
        obligation_id="obligation:research-artifact-001",
        required_evidence=(
            "PaymentReceiptEnvelope",
            "WorkDeliveryEnvelope",
            "AcceptanceEnvelope",
            "FlowPulseReceiptEnvelope",
        ),
        max_spend_units=50_00,
        requested_bond_units=25_00,
        expires_at=1_900_000_000,
    )


def negotiate_policy_card(manifest: AgentManifest, request: WorkRequest) -> PolicyCard:
    missing = sorted(set(request.required_evidence) - set(manifest.supported_evidence))
    if missing:
        raise ValueError(f"agent does not support required evidence: {', '.join(missing)}")
    if request.requested_bond_units > manifest.max_bond_units:
        raise ValueError("requested bond exceeds agent manifest maximum")
    if request.promise_type not in {"obligation_completion", "work_warranty"}:
        raise ValueError("unsupported promise type")
    return PolicyCard(
        card_id="policycard:" + request.request_id.split(":", 1)[-1],
        user_id=request.user_id,
        agent_id=manifest.agent_id,
        title=request.title,
        promise_type=request.promise_type,
        obligation_id=request.obligation_id,
        required_evidence=request.required_evidence,
        allowed_spend_units=request.max_spend_units,
        bond_units=request.requested_bond_units,
        expires_at=request.expires_at,
    )


def create_agent_proposal(manifest: AgentManifest, request: WorkRequest, policy: PolicyCard) -> AgentProposal:
    payload = {
        "agentId": manifest.agent_id,
        "requestId": request.request_id,
        "policyHash": policy_hash(policy),
        "bondUnits": policy.bond_units,
        "promisedEvidence": list(policy.required_evidence),
    }
    return AgentProposal(
        proposal_id="proposal:" + _hash_dict(payload).split(":", 1)[1][:16],
        agent_id=manifest.agent_id,
        request_id=request.request_id,
        policy_hash=policy_hash(policy),
        bond_units=policy.bond_units,
        promised_evidence=policy.required_evidence,
        proposal_hash=_hash_dict(payload),
    )


def run_agent_framework_demo() -> dict[str, Any]:
    manifest = demo_manifest()
    request = demo_request()
    policy = negotiate_policy_card(manifest, request)
    proposal = create_agent_proposal(manifest, request, policy)

    success = AgentWorkOutcome(
        action_id="action:framework-success",
        spent_units=20_00,
        completed_at=1_800_000_000,
        tx_hash="0x" + "44" * 32,
        evidence=(
            _envelope("PaymentReceiptEnvelope", request.obligation_id, {"receiptStatus": "settled"}),
            _envelope("WorkDeliveryEnvelope", request.obligation_id, {"artifactHash": "sha256:artifact-ok"}),
            _envelope("AcceptanceEnvelope", request.obligation_id, {"accepted": True}),
            _envelope("FlowPulseReceiptEnvelope", request.obligation_id, {"pulseObserved": True}),
        ),
    )
    failure = AgentWorkOutcome(
        action_id="action:framework-failure",
        spent_units=20_00,
        completed_at=1_800_000_001,
        tx_hash="0x" + "55" * 32,
        evidence=(
            _envelope("PaymentReceiptEnvelope", request.obligation_id, {"receiptStatus": "settled"}),
            _envelope("FlowPulseReceiptEnvelope", request.obligation_id, {"pulseObserved": True}),
        ),
    )

    success_settlement = settle_warranted_action(policy, success)
    failure_settlement = settle_warranted_action(policy, failure)
    pulsepass = build_pulsepass(request.user_id, [success_settlement, failure_settlement])
    proofs = [
        scoped_proof(pulsepass, ScopedProofRequest("has_completed_warranted_action", threshold=1)),
        scoped_proof(pulsepass, ScopedProofRequest("has_failed_warranty", threshold=1)),
    ]
    return {
        "schema": "flowmemory.agent_framework_demo.v0",
        "agentManifest": manifest_to_public(manifest),
        "workRequest": request_to_public(request),
        "policyCard": public_policy_view(policy),
        "agentProposal": proposal_to_public(proposal),
        "settlements": [success_settlement, failure_settlement],
        "pulsePass": {
            "ownerHash": pulsepass["ownerHash"],
            "vaultCommitment": pulsepass["vaultCommitment"],
            "receiptCount": pulsepass["receiptCount"],
        },
        "scopedProofs": proofs,
        "notClaims": [
            "not_agent_runtime",
            "not_wallet_enforcement",
            "not_custody",
            "not_production_adjudication",
            "not_full_privacy",
        ],
    }


def manifest_to_public(manifest: AgentManifest) -> dict[str, Any]:
    payload = asdict(manifest)
    payload["capabilities"] = list(manifest.capabilities)
    payload["supported_evidence"] = list(manifest.supported_evidence)
    payload["privacy_modes"] = list(manifest.privacy_modes)
    payload["settlement_modes"] = list(manifest.settlement_modes)
    payload["manifestHash"] = _hash_dict(payload)
    return payload


def request_to_public(request: WorkRequest) -> dict[str, Any]:
    payload = asdict(request)
    payload["required_evidence"] = list(request.required_evidence)
    payload["userHash"] = _hash_value(request.user_id)
    payload.pop("user_id", None)
    payload.pop("obligation_id", None)
    payload["requestHash"] = _hash_dict(payload)
    return payload


def proposal_to_public(proposal: AgentProposal) -> dict[str, Any]:
    payload = asdict(proposal)
    payload["promised_evidence"] = list(proposal.promised_evidence)
    return payload


def _envelope(envelope_type: str, obligation_id: str, fields: dict[str, Any]) -> EvidenceEnvelope:
    payload = {"envelopeType": envelope_type, "obligationId": obligation_id, "fields": fields}
    return EvidenceEnvelope(
        envelope_type=envelope_type,
        envelope_id=_hash_dict(payload),
        obligation_id=obligation_id,
        fields=fields,
    )


def _hash_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
