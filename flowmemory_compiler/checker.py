"""Check FutureTrace objects against compiled FlowPrograms."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .compiler import compile_trace
from .forbidden_core import atom, forbidden_core
from .repairs import repair_instruction


def check_trace(trace: dict[str, Any]) -> dict[str, Any]:
    program = compile_trace(trace)
    faults: list[dict[str, Any]] = []

    by_type = _envelopes_by_type(trace)
    by_step = _envelopes_by_step(trace)

    _check_required_envelopes(program, by_step, faults)
    _check_rootfield_head(trace, faults)
    _check_coding_tree(trace, by_type, faults)
    _check_payment_without_discharge(trace, by_type, faults)
    _check_payment_discharge(by_type, faults)
    _check_compute_reuse(by_type, faults)
    _check_swap_flowpulse(trace, by_type, faults)
    _check_axiom_patch(trace, faults)
    _check_verified_claim(trace, by_type, faults)

    status = "ACCEPTED" if not faults else "REJECTED"
    return {
        "schema": "flowmemory.future_result.v0",
        "caseId": trace.get("caseId"),
        "label": trace.get("label"),
        "ordinaryRails": trace.get("ordinaryRails", []),
        "status": status,
        "faults": faults,
        "program": program,
    }


def _check_required_envelopes(
    program: dict[str, Any],
    by_step: dict[str, list[dict[str, Any]]],
    faults: list[dict[str, Any]],
) -> None:
    for required in program.get("requiredEnvelopes", []):
        step_id = required["stepId"]
        envelope_type = required["envelopeType"]
        if envelope_type in {"DischargeEnvelope", "FlowPulseReceiptEnvelope"}:
            continue
        if step_id == "final":
            continue
        if not any(env.get("envelopeType") == envelope_type for env in by_step.get(step_id, [])):
            faults.append(
                _fault(
                    "missing_required_envelope",
                    [atom("requiredEnvelope", envelope_type), atom("stepId", step_id)],
                    {"envelopeType": envelope_type},
                )
            )


def _check_rootfield_head(trace: dict[str, Any], faults: list[dict[str, Any]]) -> None:
    plan = trace["plan"]
    current = trace.get("currentRootfieldHead")
    declared = plan.get("declaredRootfieldHead")
    if current and declared and current != declared:
        faults.append(
            _fault(
                "stale_memory_head_spend",
                [
                    atom("plan.declaredRootfieldHead", declared),
                    atom("trace.currentRootfieldHead", current),
                ],
            )
        )


def _check_coding_tree(
    trace: dict[str, Any],
    by_type: dict[str, list[dict[str, Any]]],
    faults: list[dict[str, Any]],
) -> None:
    if "tests_passed" not in trace["plan"].get("finalClaims", []):
        return
    diff = _first(by_type, "DiffEnvelope")
    test = _first(by_type, "TestRunEnvelope")
    if not diff or not test:
        return
    diff_fields = diff.get("fields", {})
    test_fields = test.get("fields", {})
    if test_fields.get("exitCode") != 0:
        faults.append(
            _fault(
                "tests_passed_without_success",
                [atom("TestRunEnvelope.exitCode", test_fields.get("exitCode"))],
            )
        )
    if diff_fields.get("afterTreeHash") != test_fields.get("treeHash"):
        faults.append(
            _fault(
                "tests_passed_on_wrong_tree",
                [
                    atom("finalClaims.tests_passed", True),
                    atom("DiffEnvelope.afterTreeHash", diff_fields.get("afterTreeHash")),
                    atom("TestRunEnvelope.treeHash", test_fields.get("treeHash")),
                ],
                {"targetTreeHash": diff_fields.get("afterTreeHash")},
            )
        )
    if _sequence(test) <= _sequence(diff):
        faults.append(
            _fault(
                "test_ran_before_patch",
                [
                    atom("PatchPulse.sequence", _sequence(diff)),
                    atom("TestPulse.sequence", _sequence(test)),
                ],
            )
        )


def _check_payment_discharge(by_type: dict[str, list[dict[str, Any]]], faults: list[dict[str, Any]]) -> None:
    payment = _first(by_type, "PaymentReceiptEnvelope")
    discharge = _first(by_type, "DischargeEnvelope")
    if not payment or not discharge:
        return
    payment_fields = payment.get("fields", {})
    discharge_fields = discharge.get("fields", {})
    if payment_fields.get("paymentRequirementHash") != discharge_fields.get("paymentRequirementHash"):
        faults.append(
            _fault(
                "payment_receipt_wrong_obligation",
                [
                    atom("PaymentReceiptEnvelope.paymentRequirementHash", payment_fields.get("paymentRequirementHash")),
                    atom("DischargeEnvelope.paymentRequirementHash", discharge_fields.get("paymentRequirementHash")),
                    atom("DischargeEnvelope.obligationId", discharge_fields.get("obligationId")),
                ],
            )
        )


def _check_payment_without_discharge(
    trace: dict[str, Any],
    by_type: dict[str, list[dict[str, Any]]],
    faults: list[dict[str, Any]],
) -> None:
    if "obligation_closed" not in trace["plan"].get("finalClaims", []):
        return
    payment = _first(by_type, "PaymentReceiptEnvelope")
    if payment and "DischargeEnvelope" not in by_type:
        faults.append(
            _fault(
                "payment_success_without_obligation_discharge",
                [
                    atom("ordinaryRails.paymentReceiptObserved", "payment_receipt_observed" in trace.get("ordinaryRails", [])),
                    atom("envelopes.PaymentReceiptEnvelope", "present"),
                    atom("requiredEnvelope.DischargeEnvelope", "missing"),
                    atom("finalClaims.obligation_closed", True),
                ],
            )
        )


def _check_compute_reuse(by_type: dict[str, list[dict[str, Any]]], faults: list[dict[str, Any]]) -> None:
    envelope = _first(by_type, "ComputeReuseEnvelope")
    if not envelope:
        return
    fields = envelope.get("fields", {})
    if fields.get("sourceFmmState") != "FMM_CONFORMING":
        faults.append(
            _fault(
                "compute_reuse_memory_inconsistent",
                [
                    atom("ComputeReuseEnvelope.fingerprintMatch", fields.get("fingerprintMatch")),
                    atom("ComputeReuseEnvelope.sourceFmmState", fields.get("sourceFmmState")),
                ],
            )
        )


def _check_swap_flowpulse(
    trace: dict[str, Any],
    by_type: dict[str, list[dict[str, Any]]],
    faults: list[dict[str, Any]],
) -> None:
    if not any(step.get("type") == "uniswap_swap" for step in trace["plan"].get("steps", [])):
        return
    if "FlowPulseReceiptEnvelope" not in by_type:
        faults.append(
            _fault(
                "swap_receipt_missing_flowpulse",
                [
                    atom("ordinaryReceipt.present", True),
                    atom("requiredEnvelope.FlowPulseReceiptEnvelope", "missing"),
                ],
            )
        )


def _check_axiom_patch(trace: dict[str, Any], faults: list[dict[str, Any]]) -> None:
    for step in trace["plan"].get("steps", []):
        if step.get("type") != "session_action":
            continue
        if step.get("axiomPatch") == "propose_unsigned_action" and step.get("attemptedAction") == "wallet_submission":
            faults.append(
                _fault(
                    "axiompatch_downgrade_ignored",
                    [
                        atom("sessionAction.axiomPatch", step.get("axiomPatch")),
                        atom("sessionAction.attemptedAction", step.get("attemptedAction")),
                    ],
                )
            )


def _check_verified_claim(
    trace: dict[str, Any],
    by_type: dict[str, list[dict[str, Any]]],
    faults: list[dict[str, Any]],
) -> None:
    if "verified" in trace["plan"].get("finalClaims", []) and "VerificationEnvelope" not in by_type:
        faults.append(
            _fault(
                "verified_without_envelope",
                [
                    atom("finalClaims.verified", True),
                    atom("requiredEnvelope.VerificationEnvelope", "missing"),
                ],
            )
        )


def _fault(
    name: str,
    core_atoms: list[dict[str, Any]],
    repair_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "fault": name,
        "forbiddenCore": forbidden_core(name, core_atoms),
        "repair": repair_instruction(name, repair_context),
    }


def _envelopes_by_type(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for envelope in trace.get("envelopes", []):
        grouped[envelope["envelopeType"]].append(envelope)
    return grouped


def _envelopes_by_step(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for envelope in trace.get("envelopes", []):
        grouped[envelope.get("stepId", "")].append(envelope)
    return grouped


def _first(grouped: dict[str, list[dict[str, Any]]], envelope_type: str) -> dict[str, Any] | None:
    items = grouped.get(envelope_type)
    return items[0] if items else None


def _sequence(envelope: dict[str, Any]) -> int:
    return int(envelope.get("observedSequence", 0))
