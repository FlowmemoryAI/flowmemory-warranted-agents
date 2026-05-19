"""Compile agent plans into required FlowMemory evidence envelopes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


REQUIRED_ENVELOPES_BY_STEP = {
    "patch_files": ["DiffEnvelope"],
    "run_tests": ["TestRunEnvelope"],
    "x402_payment": ["PaymentReceiptEnvelope"],
    "compute_reuse": ["ComputeReuseEnvelope"],
    "uniswap_swap": ["FlowPulseReceiptEnvelope"],
    "close_obligation": ["DischargeEnvelope"],
    "final_answer": ["ClaimEnvelope"],
    "session_action": [],
}

SURFACES_BY_STEP = {
    "patch_files": "coding",
    "run_tests": "coding",
    "x402_payment": "payment",
    "compute_reuse": "compute",
    "uniswap_swap": "onchain",
    "close_obligation": "discharge",
    "final_answer": "claim",
    "session_action": "wallet",
}

CLAIM_REQUIREMENTS = {
    "tests_passed": ["TestRunEnvelope"],
    "obligation_closed": ["DischargeEnvelope"],
    "swap_observed": ["FlowPulseReceiptEnvelope"],
    "compute_reused": ["ComputeReuseEnvelope"],
    "verified": ["VerificationEnvelope"],
}


def compile_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic FlowProgram for an AgentPlan dictionary."""

    required_envelopes: list[dict[str, Any]] = []
    required_pulses: list[dict[str, Any]] = []
    surfaces: list[str] = []
    faults: list[dict[str, Any]] = []

    for step in plan.get("steps", []):
        step_type = step.get("type")
        if step_type not in REQUIRED_ENVELOPES_BY_STEP:
            faults.append(
                {
                    "fault": "unknown_step_type",
                    "stepId": step.get("stepId"),
                    "stepType": step_type,
                }
            )
            continue

        surface = SURFACES_BY_STEP[step_type]
        if surface not in surfaces:
            surfaces.append(surface)

        pulse_type = _pulse_for_step(step_type)
        if pulse_type:
            required_pulses.append({"stepId": step["stepId"], "pulseType": pulse_type})

        for envelope_type in REQUIRED_ENVELOPES_BY_STEP[step_type]:
            required_envelopes.append(
                {
                    "stepId": step["stepId"],
                    "envelopeType": envelope_type,
                }
            )

    for claim in plan.get("finalClaims", []):
        for envelope_type in CLAIM_REQUIREMENTS.get(claim, []):
            if not any(item["envelopeType"] == envelope_type for item in required_envelopes):
                required_envelopes.append({"stepId": "final", "envelopeType": envelope_type})

    return {
        "schema": "flowmemory.flowprogram.v0",
        "programId": f"flowprogram:{plan.get('planId', 'unknown')}",
        "sourcePlanId": plan.get("planId"),
        "rootfieldId": plan.get("rootfieldId"),
        "declaredRootfieldHead": plan.get("declaredRootfieldHead"),
        "compileStatus": "REJECTED" if faults else "COMPILED",
        "surfaces": surfaces,
        "requiredPulses": required_pulses,
        "requiredEnvelopes": required_envelopes,
        "requiredPasses": [
            "SurfacePass",
            "EnvelopeRequirementPass",
            "HappensBeforePass",
            "EnvelopeBindingPass",
            "ClaimAdmissibilityPass",
            "ForbiddenCorePass",
            "RepairPass",
        ],
        "forbiddenClaims": [
            "tests_passed_without_TestRunEnvelope",
            "payment_success_without_obligation_discharge",
            "swap_observed_without_FlowPulseReceiptEnvelope",
            "verified_without_required_envelope",
            "model_correctness",
            "semantic_truth",
        ],
        "faults": faults,
    }


def compile_trace(trace: dict[str, Any]) -> dict[str, Any]:
    compiled = compile_plan(trace["plan"])
    program = deepcopy(compiled)
    program["traceId"] = trace.get("traceId")
    return program


def _pulse_for_step(step_type: str) -> str | None:
    return {
        "patch_files": "PatchPulse",
        "run_tests": "TestPulse",
        "x402_payment": "PaymentPulse",
        "compute_reuse": "ComputePulse",
        "uniswap_swap": "FlowPulse",
        "close_obligation": "DischargePulse",
        "final_answer": "ClaimPulse",
        "session_action": "ActionPulse",
    }.get(step_type)

