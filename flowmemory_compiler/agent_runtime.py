"""Deterministic runtime state machine for warranted-agent actions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .agent_adapter import DemoWarrantedAgentAdapter, WarrantedAgentAdapter
from .agent_framework import WorkRequest, demo_request
from .bond_ledger import BondAccount, LocalBondLedger
from .policycards import policy_hash
from .private_compute import PrivateMemoryProgram, run_private_memory_program
from .pulsepass import build_pulsepass


@dataclass(frozen=True)
class RuntimeEvent:
    phase: str
    status: str
    event_hash: str
    fields: dict[str, Any]


class WarrantedAgentRuntime:
    """Runs the adapter, bond ledger, FlowPulse settlement, and proof layers."""

    def __init__(self, adapter: WarrantedAgentAdapter, *, agent_balance_units: int = 100_00) -> None:
        self.adapter = adapter
        self.agent_balance_units = agent_balance_units

    def run(self, request: WorkRequest, *, mode: str) -> dict[str, Any]:
        timeline: list[RuntimeEvent] = []
        manifest = self.adapter.manifest()
        timeline.append(_event("manifest_loaded", "OK", {"agentId": manifest.agent_id}))

        policy, proposal = self.adapter.quote(request)
        timeline.append(
            _event(
                "policy_quoted",
                "OK",
                {
                    "requestId": request.request_id,
                    "policyHash": policy_hash(policy),
                    "proposalHash": proposal.proposal_hash,
                    "bondUnits": proposal.bond_units,
                },
            )
        )

        ledger = LocalBondLedger(
            [
                BondAccount(manifest.agent_id, self.agent_balance_units),
                BondAccount(request.user_id, 0),
            ]
        )
        lock = ledger.open_bond(
            policy_hash=policy_hash(policy),
            agent_id=manifest.agent_id,
            user_id=request.user_id,
            bond_units=proposal.bond_units,
        )
        timeline.append(_event("bond_locked", "OK", {"bondId": lock["bondId"], "receiptId": lock["receiptId"]}))

        outcome = self.adapter.execute(policy, mode=mode)
        timeline.append(
            _event(
                "action_executed",
                "OK",
                {
                    "actionId": outcome.action_id,
                    "evidenceTypes": [item.envelope_type for item in outcome.evidence],
                    "spentUnits": outcome.spent_units,
                },
            )
        )

        settlement = self.adapter.settle(policy, outcome)
        settlement_receipt = ledger.settle_bond(bond_id=lock["bondId"], settlement=settlement)
        timeline.append(
            _event(
                "flowbond_settled",
                "PASSED" if settlement["passed"] else "FAILED",
                {
                    "settlement": settlement["settlement"],
                    "pulseId": settlement["flowPulse"]["pulseId"],
                    "ledgerReceiptId": settlement_receipt["receiptId"],
                },
            )
        )

        passport = build_pulsepass(request.user_id, [settlement])
        private_result = run_private_memory_program(
            passport,
            PrivateMemoryProgram(
                program_id="private-program:runtime-warranty-state",
                predicate="has_completed_warranted_action" if settlement["passed"] else "has_failed_warranty",
                threshold=1,
                reveal=("vaultCommitment", "predicate", "passed", "countBucket"),
            ),
        )
        timeline.append(
            _event(
                "private_proof_ready",
                "OK" if private_result["passed"] else "FAILED",
                {
                    "vaultCommitment": passport["vaultCommitment"],
                    "transcriptHash": private_result["transcriptHash"],
                },
            )
        )

        return {
            "schema": "flowmemory.warranted_agent_runtime.v0",
            "mode": mode,
            "agentId": manifest.agent_id,
            "requestId": request.request_id,
            "policyHash": policy_hash(policy),
            "proposalHash": proposal.proposal_hash,
            "timeline": [event_to_public(event) for event in timeline],
            "settlement": settlement,
            "ledger": ledger.snapshot(),
            "pulsePass": {
                "ownerHash": passport["ownerHash"],
                "vaultCommitment": passport["vaultCommitment"],
                "receiptCount": passport["receiptCount"],
            },
            "privateCompute": private_result,
            "finalStatus": "WARRANTY_RELEASED" if settlement["passed"] else "USER_PAID_FROM_BOND",
            "notClaims": [
                "not_agent_host",
                "not_wallet_runtime",
                "not_custody",
                "not_production_settlement",
                "not_zero_knowledge",
                "not_work_quality_proof",
            ],
        }


def run_runtime_demo() -> dict[str, Any]:
    runtime = WarrantedAgentRuntime(DemoWarrantedAgentAdapter())
    request = demo_request()
    success = runtime.run(request, mode="success")
    failure = runtime.run(request, mode="payment_without_delivery")
    return {
        "schema": "flowmemory.warranted_agent_runtime_demo.v0",
        "runs": [success, failure],
        "summary": {
            "successFinalStatus": success["finalStatus"],
            "failureFinalStatus": failure["finalStatus"],
            "timelineLength": len(success["timeline"]),
        },
        "notClaims": [
            "not_external_agent_runtime",
            "not_wallet_execution",
            "not_custody",
            "not_production_adjudication",
        ],
    }


def event_to_public(event: RuntimeEvent) -> dict[str, Any]:
    return {
        "phase": event.phase,
        "status": event.status,
        "eventHash": event.event_hash,
        "fields": event.fields,
    }


def _event(phase: str, status: str, fields: dict[str, Any]) -> RuntimeEvent:
    payload = {"phase": phase, "status": status, "fields": fields}
    return RuntimeEvent(phase=phase, status=status, event_hash=_hash_dict(payload), fields=fields)


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
