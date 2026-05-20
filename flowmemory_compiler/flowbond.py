"""FlowBond local R&D proof for agent work warranties.

FlowBond models a warranted agent promise: an agent posts a bond against a
PolicyCard, acts, and a FlowPulse-like receipt settles whether the promise was
completed or the user receives the bond.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .policycards import PolicyCard, demo_policy_card, policy_hash, public_policy_view


@dataclass(frozen=True)
class EvidenceEnvelope:
    envelope_type: str
    envelope_id: str
    obligation_id: str
    fields: dict[str, Any]


@dataclass(frozen=True)
class AgentWorkOutcome:
    action_id: str
    spent_units: int
    completed_at: int
    tx_hash: str
    evidence: tuple[EvidenceEnvelope, ...]


def settle_warranted_action(policy: PolicyCard, outcome: AgentWorkOutcome) -> dict[str, Any]:
    violations = _violations(policy, outcome)
    passed = not violations
    settlement = "RELEASE_BOND_TO_AGENT" if passed else "PAY_BOND_TO_USER"
    pulse = _flowpulse(policy, outcome, passed, violations)
    return {
        "schema": "flowmemory.flowbond_settlement.v0",
        "bondId": f"bond:{policy.card_id}",
        "agentId": policy.agent_id,
        "userId": policy.user_id,
        "policyHash": policy_hash(policy),
        "policyCard": public_policy_view(policy),
        "passed": passed,
        "violations": violations,
        "settlement": settlement,
        "bondUnits": policy.bond_units,
        "flowPulse": pulse,
        "notClaims": [
            "not_profit_guarantee",
            "not_custody",
            "not_fund_protection",
            "not_work_quality_proof",
            "not_semantic_truth",
            "not_production_adjudication",
        ],
    }


def demo_cases() -> list[dict[str, Any]]:
    policy = demo_policy_card()
    good = AgentWorkOutcome(
        action_id="action:research-delivery-ok",
        spent_units=20_00,
        completed_at=1_800_000_000,
        tx_hash="0x" + "11" * 32,
        evidence=(
            _envelope("PaymentReceiptEnvelope", policy.obligation_id, {"receiptStatus": "settled"}),
            _envelope("WorkDeliveryEnvelope", policy.obligation_id, {"artifactHash": "sha256:artifact-ok"}),
            _envelope("AcceptanceEnvelope", policy.obligation_id, {"accepted": True}),
            _envelope("FlowPulseReceiptEnvelope", policy.obligation_id, {"pulseObserved": True}),
        ),
    )
    paid_but_not_delivered = AgentWorkOutcome(
        action_id="action:payment-without-delivery",
        spent_units=20_00,
        completed_at=1_800_000_001,
        tx_hash="0x" + "22" * 32,
        evidence=(
            _envelope("PaymentReceiptEnvelope", policy.obligation_id, {"receiptStatus": "settled"}),
            _envelope("FlowPulseReceiptEnvelope", policy.obligation_id, {"pulseObserved": True}),
        ),
    )
    orphan_spend = AgentWorkOutcome(
        action_id="action:orphan-spend",
        spent_units=12_00,
        completed_at=1_800_000_002,
        tx_hash="0x" + "33" * 32,
        evidence=(
            _envelope("PaymentReceiptEnvelope", "obligation:unrelated", {"receiptStatus": "settled"}),
            _envelope("WorkDeliveryEnvelope", policy.obligation_id, {"artifactHash": "sha256:artifact-late"}),
            _envelope("AcceptanceEnvelope", policy.obligation_id, {"accepted": True}),
            _envelope("FlowPulseReceiptEnvelope", policy.obligation_id, {"pulseObserved": True}),
        ),
    )
    return [
        {"caseId": "FB-OK-001", "label": "warranted_work_completed", "result": settle_warranted_action(policy, good)},
        {
            "caseId": "FB-BAD-001",
            "label": "payment_without_delivery",
            "result": settle_warranted_action(policy, paid_but_not_delivered),
        },
        {"caseId": "FB-BAD-002", "label": "orphan_spend", "result": settle_warranted_action(policy, orphan_spend)},
    ]


def _violations(policy: PolicyCard, outcome: AgentWorkOutcome) -> list[str]:
    violations: list[str] = []
    if outcome.spent_units > policy.allowed_spend_units:
        violations.append("allowed_spend_exceeded")
    if outcome.completed_at > policy.expires_at:
        violations.append("policy_expired")

    evidence_by_type = {item.envelope_type: item for item in outcome.evidence}
    for required in policy.required_evidence:
        if required not in evidence_by_type:
            violations.append(f"missing_{required}")

    for envelope in outcome.evidence:
        if envelope.obligation_id != policy.obligation_id:
            violations.append(f"{envelope.envelope_type}_wrong_obligation")

    acceptance = evidence_by_type.get("AcceptanceEnvelope")
    if acceptance and acceptance.fields.get("accepted") is not True:
        violations.append("work_not_accepted")

    if "PaymentReceiptEnvelope" in evidence_by_type and "WorkDeliveryEnvelope" not in evidence_by_type:
        violations.append("payment_without_delivery")
    return sorted(set(violations))


def _flowpulse(
    policy: PolicyCard,
    outcome: AgentWorkOutcome,
    passed: bool,
    violations: list[str],
) -> dict[str, Any]:
    payload = {
        "schema": "flowmemory.flowpulse.flowbond.v0",
        "pulseType": "BondedActionPulse",
        "actionId": outcome.action_id,
        "agentId": policy.agent_id,
        "policyHash": policy_hash(policy),
        "actionType": policy.promise_type,
        "obligationHash": _hash_value(policy.obligation_id),
        "evidenceTypes": sorted(item.envelope_type for item in outcome.evidence),
        "passed": passed,
        "violations": violations,
        "txHash": outcome.tx_hash,
        "outcomeHash": _hash_dict(
            {
                "spentUnits": outcome.spent_units,
                "completedAt": outcome.completed_at,
                "evidence": [_envelope_payload(item) for item in outcome.evidence],
            }
        ),
    }
    payload["pulseId"] = _hash_dict(payload)
    return payload


def _envelope(envelope_type: str, obligation_id: str, fields: dict[str, Any]) -> EvidenceEnvelope:
    payload = {"envelopeType": envelope_type, "obligationId": obligation_id, "fields": fields}
    return EvidenceEnvelope(
        envelope_type=envelope_type,
        envelope_id=_hash_dict(payload),
        obligation_id=obligation_id,
        fields=fields,
    )


def _envelope_payload(envelope: EvidenceEnvelope) -> dict[str, Any]:
    return {
        "envelopeType": envelope.envelope_type,
        "envelopeId": envelope.envelope_id,
        "obligationHash": _hash_value(envelope.obligation_id),
        "fieldsHash": _hash_dict(envelope.fields),
    }


def _hash_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()

