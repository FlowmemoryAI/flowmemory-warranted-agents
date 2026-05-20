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
from .runtime_state_machine import (
    ACTION_EXECUTED,
    BOND_LOCKED,
    FLOWBOND_SETTLED,
    MANIFEST_LOADED,
    POLICY_QUOTED,
    PRIVATE_PROOF_READY,
    USER_PAID_FROM_BOND,
    WARRANTY_RELEASED,
    RuntimeStateMachine,
)


@dataclass(frozen=True)
class RuntimeEvent:
    phase: str
    status: str
    event_hash: str
    from_state: str
    to_state: str
    idempotency_key: str
    fields: dict[str, Any]


class WarrantedAgentRuntime:
    """Runs the adapter, bond ledger, FlowPulse settlement, and proof layers."""

    def __init__(self, adapter: WarrantedAgentAdapter, *, agent_balance_units: int = 100_00) -> None:
        self.adapter = adapter
        self.agent_balance_units = agent_balance_units

    def run(self, request: WorkRequest, *, mode: str) -> dict[str, Any]:
        timeline: list[RuntimeEvent] = []
        state_machine = RuntimeStateMachine()
        run_id = "run:" + _hash_dict({"requestId": request.request_id, "mode": mode}).split(":", 1)[1][:16]
        manifest = self.adapter.manifest()
        timeline.append(
            _transition(
                state_machine,
                MANIFEST_LOADED,
                phase="manifest_loaded",
                status="OK",
                fields={"agentId": manifest.agent_id},
                run_id=run_id,
            )
        )

        policy, proposal = self.adapter.quote(request)
        timeline.append(
            _transition(
                state_machine,
                POLICY_QUOTED,
                phase="policy_quoted",
                status="OK",
                fields={
                    "requestId": request.request_id,
                    "policyHash": policy_hash(policy),
                    "proposalHash": proposal.proposal_hash,
                    "bondUnits": proposal.bond_units,
                },
                run_id=run_id,
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
        timeline.append(
            _transition(
                state_machine,
                BOND_LOCKED,
                phase="bond_locked",
                status="OK",
                fields={"bondId": lock["bondId"], "receiptId": lock["receiptId"]},
                run_id=run_id,
            )
        )

        outcome = self.adapter.execute(policy, mode=mode)
        timeline.append(
            _transition(
                state_machine,
                ACTION_EXECUTED,
                phase="action_executed",
                status="OK",
                fields={
                    "actionId": outcome.action_id,
                    "evidenceTypes": [item.envelope_type for item in outcome.evidence],
                    "spentUnits": outcome.spent_units,
                },
                run_id=run_id,
            )
        )

        settlement = self.adapter.settle(policy, outcome)
        settlement_receipt = ledger.settle_bond(bond_id=lock["bondId"], settlement=settlement)
        timeline.append(
            _transition(
                state_machine,
                FLOWBOND_SETTLED,
                phase="flowbond_settled",
                status="PASSED" if settlement["passed"] else "FAILED",
                fields={
                    "settlement": settlement["settlement"],
                    "pulseId": settlement["flowPulse"]["pulseId"],
                    "ledgerReceiptId": settlement_receipt["receiptId"],
                },
                run_id=run_id,
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
            _transition(
                state_machine,
                PRIVATE_PROOF_READY,
                phase="private_proof_ready",
                status="OK" if private_result["passed"] else "FAILED",
                fields={
                    "vaultCommitment": passport["vaultCommitment"],
                    "transcriptHash": private_result["transcriptHash"],
                },
                run_id=run_id,
            )
        )
        final_status = WARRANTY_RELEASED if settlement["passed"] else USER_PAID_FROM_BOND
        timeline.append(
            _transition(
                state_machine,
                final_status,
                phase="runtime_finalized",
                status=final_status,
                fields={"finalStatus": final_status, "settlement": settlement["settlement"]},
                run_id=run_id,
            )
        )

        return {
            "schema": "flowmemory.warranted_agent_runtime.v0",
            "runId": run_id,
            "mode": mode,
            "agentId": manifest.agent_id,
            "requestId": request.request_id,
            "policyHash": policy_hash(policy),
            "proposalHash": proposal.proposal_hash,
            "timeline": [event_to_public(event) for event in timeline],
            "stateMachine": state_machine.snapshot(),
            "settlement": settlement,
            "ledger": ledger.snapshot(),
            "pulsePass": {
                "ownerHash": passport["ownerHash"],
                "vaultCommitment": passport["vaultCommitment"],
                "receiptCount": passport["receiptCount"],
            },
            "privateCompute": private_result,
            "finalStatus": final_status,
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
        "fromState": event.from_state,
        "toState": event.to_state,
        "idempotencyKey": event.idempotency_key,
        "fields": event.fields,
    }


def _transition(
    state_machine: RuntimeStateMachine,
    to_state: str,
    *,
    phase: str,
    status: str,
    fields: dict[str, Any],
    run_id: str,
) -> RuntimeEvent:
    transition = state_machine.transition(
        to_state,
        phase=phase,
        status=status,
        idempotency_key=f"{run_id}:{phase}",
        fields=fields,
    )
    return RuntimeEvent(
        phase=phase,
        status=status,
        event_hash=transition.transition_hash,
        from_state=transition.from_state,
        to_state=transition.to_state,
        idempotency_key=transition.idempotency_key,
        fields=fields,
    )


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
