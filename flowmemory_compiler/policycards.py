"""PolicyCards for FlowMemory warranted agents."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyCard:
    """A portable user rule that an agent can bond against."""

    card_id: str
    user_id: str
    agent_id: str
    title: str
    promise_type: str
    obligation_id: str
    required_evidence: tuple[str, ...]
    allowed_spend_units: int
    bond_units: int
    expires_at: int
    private_fields: tuple[str, ...] = ("user_id", "obligation_id")


def policy_hash(policy: PolicyCard) -> str:
    payload = asdict(policy)
    payload["required_evidence"] = list(policy.required_evidence)
    payload["private_fields"] = list(policy.private_fields)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def public_policy_view(policy: PolicyCard) -> dict[str, Any]:
    """Return the public/card-shareable view without private fields."""

    payload = asdict(policy)
    for field in policy.private_fields:
        payload.pop(field, None)
    payload["policyHash"] = policy_hash(policy)
    payload["required_evidence"] = list(policy.required_evidence)
    payload["private_fields"] = list(policy.private_fields)
    return payload


def demo_policy_card() -> PolicyCard:
    return PolicyCard(
        card_id="policycard-work-warranty-001",
        user_id="user:local-demo",
        agent_id="agent:work-warranty-demo",
        title="Deliver the requested research artifact",
        promise_type="obligation_completion",
        obligation_id="obligation:research-artifact-001",
        required_evidence=(
            "PaymentReceiptEnvelope",
            "WorkDeliveryEnvelope",
            "AcceptanceEnvelope",
            "FlowPulseReceiptEnvelope",
        ),
        allowed_spend_units=50_00,
        bond_units=25_00,
        expires_at=1_900_000_000,
    )

