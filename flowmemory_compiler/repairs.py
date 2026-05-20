"""Repair instructions for FlowCompiler faults."""

from __future__ import annotations

from typing import Any


REPAIR_MAP = {
    "missing_required_envelope": [
        {
            "action": "attach_required_envelope",
            "reason": "the plan requires this envelope before the claim is admissible",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "required evidence envelope is not present",
        },
    ],
    "tests_passed_on_wrong_tree": [
        {
            "action": "rerun_tests",
            "reason": "tests_passed must bind to the patched tree",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "I changed the code, but tests were not verified on the final tree.",
        },
    ],
    "test_ran_before_patch": [
        {
            "action": "rerun_tests",
            "reason": "tests must run after the patch they are claimed to verify",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "tests ran, but not after the claimed patch",
        },
    ],
    "payment_receipt_wrong_obligation": [
        {
            "action": "attach_matching_discharge_envelope",
            "reason": "payment settlement does not prove this obligation closed",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "payment observed; obligation discharge not established",
        },
    ],
    "payment_success_without_obligation_discharge": [
        {
            "action": "attach_discharge_envelope",
            "reason": "payment receipt does not by itself close the declared obligation",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "payment observed; obligation discharge not established",
        },
    ],
    "stale_memory_head_spend": [
        {
            "action": "refresh_rootfield_head",
            "reason": "the action used a stale memory head",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "signature observed; current memory-head admissibility not established",
        },
    ],
    "compute_reuse_memory_inconsistent": [
        {
            "action": "recompute_or_attach_fmm_conforming_reuse",
            "reason": "cache reuse is not admissible when the source memory state is inconsistent",
        }
    ],
    "swap_receipt_missing_flowpulse": [
        {
            "action": "attach_flowpulse_receipt_envelope",
            "reason": "a swap receipt alone is not a FlowMemory memory artifact",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "swap receipt observed; FlowPulse memory evidence not established",
        },
    ],
    "axiompatch_downgrade_ignored": [
        {
            "action": "respect_axiom_patch",
            "reason": "the declared patch only permits proposing an unsigned action",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "wallet submission not admissible under declared action patch",
        },
    ],
    "verified_without_envelope": [
        {
            "action": "attach_verification_envelope",
            "reason": "verified claims require explicit verification evidence",
        },
        {
            "action": "downgrade_claim",
            "claimReplacement": "result produced; verification evidence not attached",
        },
    ],
}


def repair_instruction(fault: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    instructions = [dict(item) for item in REPAIR_MAP.get(fault, [])]
    context = context or {}
    if fault == "tests_passed_on_wrong_tree" and context.get("targetTreeHash"):
        instructions[0]["targetTreeHash"] = context["targetTreeHash"]
    if fault == "missing_required_envelope" and context.get("envelopeType"):
        instructions[0]["requiredEnvelope"] = context["envelopeType"]
    return {
        "schema": "flowmemory.repair_instruction.v0",
        "fault": fault,
        "instructions": instructions,
    }
