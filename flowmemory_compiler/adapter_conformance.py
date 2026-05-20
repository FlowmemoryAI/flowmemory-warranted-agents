"""Conformance checks for warranted-agent adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent_adapter import DemoWarrantedAgentAdapter, WarrantedAgentAdapter
from .agent_framework import WorkRequest, demo_request
from .policycards import policy_hash


@dataclass(frozen=True)
class AdapterCheck:
    check_id: str
    passed: bool
    detail: str


def check_adapter_conformance(adapter: WarrantedAgentAdapter, request: WorkRequest | None = None) -> dict[str, Any]:
    request = request or demo_request()
    checks: list[AdapterCheck] = []

    manifest = adapter.manifest()
    missing = sorted(set(request.required_evidence) - set(manifest.supported_evidence))
    checks.append(AdapterCheck("manifest_supports_required_evidence", not missing, ",".join(missing) or "ok"))
    checks.append(
        AdapterCheck(
            "manifest_supports_requested_bond",
            request.requested_bond_units <= manifest.max_bond_units,
            f"requested={request.requested_bond_units}; max={manifest.max_bond_units}",
        )
    )

    policy, proposal = adapter.quote(request)
    checks.append(AdapterCheck("proposal_binds_policy_hash", proposal.policy_hash == policy_hash(policy), proposal.policy_hash))
    checks.append(AdapterCheck("proposal_bond_matches_policy", proposal.bond_units == policy.bond_units, str(proposal.bond_units)))

    success = adapter.settle(policy, adapter.execute(policy, mode="success"))
    checks.append(AdapterCheck("success_releases_bond", success["settlement"] == "RELEASE_BOND_TO_AGENT", success["settlement"]))
    checks.append(AdapterCheck("success_emits_pulse", success["flowPulse"]["pulseId"].startswith("sha256:"), success["flowPulse"]["pulseId"]))

    failure = adapter.settle(policy, adapter.execute(policy, mode="payment_without_delivery"))
    checks.append(AdapterCheck("failure_pays_user", failure["settlement"] == "PAY_BOND_TO_USER", failure["settlement"]))
    checks.append(
        AdapterCheck(
            "failure_records_delivery_violation",
            "payment_without_delivery" in failure["violations"],
            ",".join(failure["violations"]),
        )
    )

    return {
        "schema": "flowmemory.adapter_conformance.v0",
        "adapter": manifest.agent_id,
        "requestId": request.request_id,
        "passed": all(item.passed for item in checks),
        "checks": [check_to_public(item) for item in checks],
        "notClaims": [
            "not_external_agent_certification",
            "not_security_audit",
            "not_work_quality_proof",
            "not_production_verifier",
        ],
    }


def run_adapter_conformance_demo() -> dict[str, Any]:
    return check_adapter_conformance(DemoWarrantedAgentAdapter())


def check_to_public(check: AdapterCheck) -> dict[str, Any]:
    return {
        "checkId": check.check_id,
        "passed": check.passed,
        "detail": check.detail,
    }
