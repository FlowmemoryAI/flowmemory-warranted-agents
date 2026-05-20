"""Adapter boundary for warranted agents."""

from __future__ import annotations

from typing import Any, Protocol

from .agent_framework import (
    AgentManifest,
    AgentProposal,
    WorkRequest,
    create_agent_proposal,
    demo_manifest,
    demo_request,
    negotiate_policy_card,
)
from .flowbond import AgentWorkOutcome, EvidenceEnvelope, settle_warranted_action
from .policycards import PolicyCard


class WarrantedAgentAdapter(Protocol):
    """Minimal interface a future real agent integration should satisfy."""

    def manifest(self) -> AgentManifest:
        ...

    def quote(self, request: WorkRequest) -> tuple[PolicyCard, AgentProposal]:
        ...

    def execute(self, policy: PolicyCard, *, mode: str) -> AgentWorkOutcome:
        ...


class DemoWarrantedAgentAdapter:
    """Deterministic local adapter used by tests and demos."""

    def manifest(self) -> AgentManifest:
        return demo_manifest()

    def quote(self, request: WorkRequest) -> tuple[PolicyCard, AgentProposal]:
        manifest = self.manifest()
        policy = negotiate_policy_card(manifest, request)
        proposal = create_agent_proposal(manifest, request, policy)
        return policy, proposal

    def execute(self, policy: PolicyCard, *, mode: str) -> AgentWorkOutcome:
        if mode == "success":
            return AgentWorkOutcome(
                action_id="action:adapter-success",
                spent_units=20_00,
                completed_at=1_800_000_000,
                tx_hash="0x" + "66" * 32,
                evidence=(
                    _envelope("PaymentReceiptEnvelope", policy.obligation_id, {"receiptStatus": "settled"}),
                    _envelope("WorkDeliveryEnvelope", policy.obligation_id, {"artifactHash": "sha256:artifact-ok"}),
                    _envelope("AcceptanceEnvelope", policy.obligation_id, {"accepted": True}),
                    _envelope("FlowPulseReceiptEnvelope", policy.obligation_id, {"pulseObserved": True}),
                ),
            )
        if mode == "payment_without_delivery":
            return AgentWorkOutcome(
                action_id="action:adapter-payment-without-delivery",
                spent_units=20_00,
                completed_at=1_800_000_001,
                tx_hash="0x" + "77" * 32,
                evidence=(
                    _envelope("PaymentReceiptEnvelope", policy.obligation_id, {"receiptStatus": "settled"}),
                    _envelope("FlowPulseReceiptEnvelope", policy.obligation_id, {"pulseObserved": True}),
                ),
            )
        raise ValueError(f"unknown adapter execution mode: {mode}")


def run_adapter_demo() -> dict[str, Any]:
    adapter = DemoWarrantedAgentAdapter()
    request = demo_request()
    policy, proposal = adapter.quote(request)
    success = settle_warranted_action(policy, adapter.execute(policy, mode="success"))
    failure = settle_warranted_action(policy, adapter.execute(policy, mode="payment_without_delivery"))
    return {
        "schema": "flowmemory.agent_adapter_demo.v0",
        "manifest": adapter.manifest(),
        "policyHash": proposal.policy_hash,
        "proposalHash": proposal.proposal_hash,
        "settlements": [success, failure],
        "notClaims": [
            "not_agent_marketplace",
            "not_external_agent_integration",
            "not_wallet_execution",
            "not_production_runtime",
        ],
    }


def _envelope(envelope_type: str, obligation_id: str, fields: dict[str, Any]) -> EvidenceEnvelope:
    return EvidenceEnvelope(
        envelope_type=envelope_type,
        envelope_id=f"local:{envelope_type}:{len(fields)}",
        obligation_id=obligation_id,
        fields=fields,
    )

