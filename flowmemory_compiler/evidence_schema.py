"""Evidence envelope schema registry for warranted-agent receipts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceFieldSpec:
    name: str
    kind: str
    required_value: Any | None = None
    prefix: str | None = None


@dataclass(frozen=True)
class EvidenceEnvelopeSpec:
    envelope_type: str
    purpose: str
    fields: tuple[EvidenceFieldSpec, ...]


EVIDENCE_SPECS: dict[str, EvidenceEnvelopeSpec] = {
    "PaymentReceiptEnvelope": EvidenceEnvelopeSpec(
        envelope_type="PaymentReceiptEnvelope",
        purpose="Proves a payment-like obligation event was observed by the local model.",
        fields=(EvidenceFieldSpec("receiptStatus", "str", required_value="settled"),),
    ),
    "WorkDeliveryEnvelope": EvidenceEnvelopeSpec(
        envelope_type="WorkDeliveryEnvelope",
        purpose="Binds the claimed work delivery to a content commitment.",
        fields=(EvidenceFieldSpec("artifactHash", "str", prefix="sha256:"),),
    ),
    "AcceptanceEnvelope": EvidenceEnvelopeSpec(
        envelope_type="AcceptanceEnvelope",
        purpose="Records that the user-side acceptance condition closed.",
        fields=(EvidenceFieldSpec("accepted", "bool", required_value=True),),
    ),
    "FlowPulseReceiptEnvelope": EvidenceEnvelopeSpec(
        envelope_type="FlowPulseReceiptEnvelope",
        purpose="Binds the action to a FlowPulse-style memory receipt.",
        fields=(EvidenceFieldSpec("pulseObserved", "bool", required_value=True),),
    ),
}


def validate_evidence_envelope(envelope_type: str, fields: dict[str, Any]) -> list[str]:
    spec = EVIDENCE_SPECS.get(envelope_type)
    if spec is None:
        return ["unknown_evidence_type"]
    violations: list[str] = []
    for field in spec.fields:
        if field.name not in fields:
            violations.append(f"missing_field_{field.name}")
            continue
        value = fields[field.name]
        if not _matches_kind(value, field.kind):
            violations.append(f"field_{field.name}_wrong_type")
            continue
        if field.required_value is not None and value != field.required_value:
            violations.append(f"field_{field.name}_unexpected_value")
        if field.prefix is not None and isinstance(value, str) and not value.startswith(field.prefix):
            violations.append(f"field_{field.name}_bad_prefix")
    return violations


def evidence_schema_report() -> dict[str, Any]:
    return {
        "schema": "flowmemory.evidence_schema_report.v0",
        "envelopes": [
            {
                "envelopeType": spec.envelope_type,
                "purpose": spec.purpose,
                "fields": [
                    {
                        "name": field.name,
                        "kind": field.kind,
                        "requiredValue": field.required_value,
                        "prefix": field.prefix,
                    }
                    for field in spec.fields
                ],
            }
            for spec in EVIDENCE_SPECS.values()
        ],
        "notClaims": [
            "not_semantic_truth",
            "not_work_quality_proof",
            "not_external_verifier",
            "not_production_schema_registry",
        ],
    }


def _matches_kind(value: Any, kind: str) -> bool:
    if kind == "str":
        return isinstance(value, str)
    if kind == "bool":
        return isinstance(value, bool)
    if kind == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    raise ValueError(f"unknown evidence field kind: {kind}")
