"""PulsePods local proof for memory-native agent compute pods.

PulsePods are FlowMemory's answer to generic private compute pods: a pod does
not merely pool models, keys, and billing. It routes agent work by the memory it
can prove after execution.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Callable

from .outcome_router import run_pulserouter_demo, validate_outcome_report


REQUIRED_POD_EVIDENCE = {
    "PolicyCard",
    "ComputePulse",
    "ActionPulse",
    "FlowPulseLink",
    "OutcomePulse",
    "PulsePassPredicate",
}

FORBIDDEN_PUBLIC_CLAIM_FRAGMENTS = (
    "live compute marketplace",
    "production settlement",
    "full privacy",
    "zero-knowledge",
    "tee verified",
    "cheaper inference",
    "guaranteed outcome",
    "model correctness",
)

PRIVATE_REVEAL_FIELDS = {
    "rawPrompt",
    "rawResponse",
    "fullWalletHistory",
    "exactAmount",
    "txList",
    "privateObligationIds",
}


def run_pulsepod_demo() -> dict[str, Any]:
    """Build the canonical local PulsePod launch demo."""

    route = run_pulserouter_demo()
    selected_compute = _selected_compute(route)
    outcome = route["outcomePulse"]
    action = route["actionPulse"]
    flowpulse = route["flowPulseLink"]

    manifest = {
        "schema": "flowmemory.pulsepod_manifest.v0",
        "podId": "pulsepod:memory-native-defi-demo",
        "displayName": "Memory-Native DeFi PulsePod",
        "category": "memory_native_compute_pod",
        "mode": "local_demo",
        "ownerHash": _hash_value("user:local-demo"),
        "policyHash": route["policy"]["policyHash"],
        "routingObjective": "cost_per_successful_flowpulse_outcome",
        "providerPromiseRequired": True,
        "rawPromptLogging": False,
        "rawResponseLogging": False,
        "evidenceRequired": sorted(REQUIRED_POD_EVIDENCE),
    }
    manifest["manifestHash"] = _hash_dict(manifest)

    provider_promise = {
        "schema": "flowmemory.pulsepod_provider_promise.v0",
        "providerId": selected_compute["providerId"],
        "policyHash": route["policy"]["policyHash"],
        "promise": "produce policy-safe agent work with receipt-backed outcome memory",
        "bondCoverageUnits": selected_compute["bondCoverageUnits"],
        "canaryPassed": selected_compute["canaryPassed"],
        "privacyTier": selected_compute["privacyTier"],
        "privacyPromise": "no_raw_prompt_or_response_in_public_pulses",
        "settlementMode": "local_demo_only",
    }
    provider_promise["promiseHash"] = _hash_dict(provider_promise)

    pulse_graph = _pulse_graph(route)
    pulsepass_claim = {
        "schema": "flowmemory.pulsepod_pulsepass_claim.v0",
        "predicate": "has_successful_private_bonded_pulsepod_action",
        "passed": True,
        "countBucket": "1",
        "sourcePulseSetHash": _hash_dict({"pulseIds": sorted(item["id"] for item in pulse_graph)}),
        "reveals": ["ownerHash", "predicate", "countBucket", "sourcePulseSetHash"],
        "hides": ["rawPrompt", "rawResponse", "fullWalletHistory", "exactAmount", "txList", "privateObligationIds"],
    }
    pulsepass_claim["claimId"] = _hash_dict(pulsepass_claim)

    federation_offer = {
        "schema": "flowmemory.pulsepod_federation_offer.v0",
        "offerId": "offer:pulsepod-defi-outcome-route",
        "podId": manifest["podId"],
        "paymentRail": "x402_compatible_reference",
        "settlementMode": "local_demo_only",
        "acceptedEvidence": sorted(REQUIRED_POD_EVIDENCE),
        "routeMetric": "cost_per_successful_outcome",
        "productionSettlement": False,
    }
    federation_offer["offerHash"] = _hash_dict(federation_offer)

    memory_credit = {
        "schema": "flowmemory.pulsepod_memory_credit.v0",
        "creditType": "demo_memory_credit",
        "units": 1,
        "notMoney": True,
        "earnedByOutcomePulseId": outcome["pulseId"],
    }
    memory_credit["creditId"] = _hash_dict(memory_credit)

    report = {
        "schema": "flowmemory.pulsepod_demo.v0",
        "categoryClaim": "PulsePods are memory-native compute pods: agents and providers route by receipt-backed successful outcomes, not raw token price.",
        "manifest": manifest,
        "providerPromise": provider_promise,
        "route": route,
        "pulseGraph": pulse_graph,
        "federationOffer": federation_offer,
        "pulsePassClaim": pulsepass_claim,
        "memoryCredit": memory_credit,
        "scoreboard": _scoreboard(route),
        "launchDemo": {
            "title": "Cheap Tokens vs Useful Outcomes",
            "selectedProviderId": selected_compute["providerId"],
            "reveal": "The cheapest route lost. The useful bonded route won.",
            "flowPulseId": flowpulse["flowPulseId"],
            "outcomePulseId": outcome["pulseId"],
            "effectiveCostPerSuccessfulOutcomeUnits": outcome["effectiveCostPerSuccessfulOutcomeUnits"],
        },
        "publicClaims": [
            "PulsePods route agent work by successful FlowPulse outcomes, not raw token price.",
            "Every useful agent action should leave a receipt.",
            "Users carry private scoped proof of safe agent history.",
            "Providers earn better routing by producing successful receipt-backed outcomes.",
        ],
        "notClaims": [
            "not_live_compute_marketplace",
            "not_production_settlement",
            "not_full_privacy",
            "not_zero_knowledge",
            "not_tee_attestation",
            "not_cheaper_inference",
            "not_model_correctness",
            "not_real_user_earnings",
        ],
    }
    report["validationFaults"] = validate_pulsepod_report(report)
    report["podDemoHash"] = _hash_dict({key: value for key, value in report.items() if key not in {"validationFaults", "podDemoHash"}})
    return report


def run_pulsepod_adversary_suite() -> dict[str, Any]:
    base = run_pulsepod_demo()
    cases = _adversarial_cases()
    results = []
    for case in cases:
        report = copy.deepcopy(base)
        case["mutate"](report)
        faults = validate_pulsepod_report(report)
        expected = case["expectedFault"]
        results.append(
            {
                "caseId": case["caseId"],
                "label": case["label"],
                "expectedFault": expected,
                "caught": expected in faults,
                "faults": faults,
            }
        )
    return {
        "schema": "flowmemory.pulsepod_adversary_suite.v0",
        "cases": [{key: value for key, value in item.items() if key != "mutate"} for item in cases],
        "results": results,
        "caught": sum(1 for item in results if item["caught"]),
        "total": len(results),
        "passed": all(item["caught"] for item in results),
    }


def validate_pulsepod_report(report: dict[str, Any]) -> list[str]:
    faults: list[str] = []

    manifest = report.get("manifest", {})
    route = report.get("route", {})
    provider_promise = report.get("providerPromise", {})
    federation = report.get("federationOffer", {})
    pulsepass = report.get("pulsePassClaim", {})
    memory_credit = report.get("memoryCredit", {})
    pulse_graph = report.get("pulseGraph", [])

    if report.get("schema") != "flowmemory.pulsepod_demo.v0":
        faults.append("pulsepod_schema_mismatch")
    if not manifest.get("podId"):
        faults.append("pod_id_missing")
    if manifest.get("mode") != "local_demo":
        faults.append("pulsepod_mode_not_local_demo")
    if manifest.get("routingObjective") != "cost_per_successful_flowpulse_outcome":
        faults.append("routing_objective_not_outcome_settled")
    if manifest.get("rawPromptLogging") is not False or manifest.get("rawResponseLogging") is not False:
        faults.append("pulsepod_raw_logging_enabled")

    policy = route.get("policy", {})
    if manifest.get("policyHash") != policy.get("policyHash"):
        faults.append("pulsepod_policy_hash_mismatch")

    for route_fault in validate_outcome_report(route) if route else ["route_missing"]:
        faults.append(f"route_validation_fault:{route_fault}")

    selected_compute = _selected_compute(route) if route else None
    outcome = route.get("outcomePulse", {})
    flowpulse = route.get("flowPulseLink", {})
    if not selected_compute:
        faults.append("selected_compute_missing")
    else:
        if provider_promise.get("providerId") != selected_compute.get("providerId"):
            faults.append("provider_promise_provider_mismatch")
        if provider_promise.get("policyHash") != policy.get("policyHash"):
            faults.append("provider_promise_policy_mismatch")
        if provider_promise.get("bondCoverageUnits", 0) <= 0:
            faults.append("provider_promise_unbonded")
        if provider_promise.get("canaryPassed") is not True:
            faults.append("provider_promise_canary_failed")
        if provider_promise.get("privacyPromise") != "no_raw_prompt_or_response_in_public_pulses":
            faults.append("provider_privacy_promise_missing")

    if outcome.get("passed") is not True:
        faults.append("pulsepod_outcome_not_successful")
    if flowpulse.get("source") != "reader_derived":
        faults.append("pulsepod_flowpulse_not_reader_derived")

    graph_kinds = {item.get("kind") for item in pulse_graph}
    if not REQUIRED_POD_EVIDENCE.issubset(graph_kinds):
        faults.append("pulsepod_evidence_set_incomplete")
    sequences = [item.get("sequence") for item in pulse_graph]
    if sequences != list(range(1, len(sequences) + 1)):
        faults.append("pulsepod_sequence_not_monotonic")
    if any(not item.get("id") for item in pulse_graph):
        faults.append("pulsepod_graph_id_missing")

    if federation.get("paymentRail") != "x402_compatible_reference":
        faults.append("federation_payment_rail_not_x402_compatible")
    if federation.get("settlementMode") != "local_demo_only" or federation.get("productionSettlement") is not False:
        faults.append("federation_overclaims_production")
    if not REQUIRED_POD_EVIDENCE.issubset(set(federation.get("acceptedEvidence", []))):
        faults.append("federation_evidence_set_incomplete")
    if federation.get("routeMetric") != "cost_per_successful_outcome":
        faults.append("federation_route_metric_not_outcome_based")

    if pulsepass.get("predicate") != "has_successful_private_bonded_pulsepod_action":
        faults.append("pulsepass_predicate_mismatch")
    if pulsepass.get("passed") is not True:
        faults.append("pulsepass_claim_not_passed")
    if not str(pulsepass.get("sourcePulseSetHash", "")).startswith("sha256:"):
        faults.append("pulsepass_source_set_uncommitted")
    if PRIVATE_REVEAL_FIELDS.intersection(set(pulsepass.get("reveals", []))):
        faults.append("pulsepass_reveals_private_fields")

    if memory_credit.get("units", 0) < 0:
        faults.append("negative_memory_credit")
    if memory_credit.get("notMoney") is not True:
        faults.append("memory_credit_marketed_as_money")

    if _has_raw_model_content(report):
        faults.append("raw_model_content_stored")
    if _has_public_overclaim(report):
        faults.append("public_claim_overclaim")

    return sorted(set(faults))


def _pulse_graph(route: dict[str, Any]) -> list[dict[str, Any]]:
    graph = [
        {"sequence": 1, "kind": "PolicyCard", "id": route["policy"]["policyHash"]},
    ]
    sequence = 2
    for pulse in route["computePulses"]:
        graph.append({"sequence": sequence, "kind": "ComputePulse", "id": pulse["pulseId"], "providerId": pulse["providerId"]})
        sequence += 1
    graph.extend(
        [
            {"sequence": sequence, "kind": "ActionPulse", "id": route["actionPulse"]["pulseId"]},
            {"sequence": sequence + 1, "kind": "FlowPulseLink", "id": route["flowPulseLink"]["flowPulseId"]},
            {"sequence": sequence + 2, "kind": "OutcomePulse", "id": route["outcomePulse"]["pulseId"]},
            {"sequence": sequence + 3, "kind": "PulsePassPredicate", "id": route["portableUserMemory"]["pulsePassPredicate"]},
        ]
    )
    return graph


def _scoreboard(route: dict[str, Any]) -> list[dict[str, Any]]:
    selected_provider = route["selectedProviderId"]
    outcome = route["outcomePulse"]
    rows = []
    for score in route["routeScores"]:
        selected = score["providerId"] == selected_provider
        rows.append(
            {
                "providerId": score["providerId"],
                "eligible": score["eligible"],
                "selected": selected,
                "rawPriceUnits": score["quotedPriceUnits"],
                "scoreUnits": score["scoreUnits"],
                "costPerSuccessfulOutcomeUnits": outcome["effectiveCostPerSuccessfulOutcomeUnits"] if selected else None,
            }
        )
    return rows


def _selected_compute(route: dict[str, Any]) -> dict[str, Any] | None:
    selected_provider = route.get("selectedProviderId")
    return next((pulse for pulse in route.get("computePulses", []) if pulse.get("providerId") == selected_provider), None)


def _adversarial_cases() -> list[dict[str, Any]]:
    return [
        _case("PP-BAD-001", "missing pod id", "pod_id_missing", lambda r: r["manifest"].update({"podId": ""})),
        _case("PP-BAD-002", "mode overclaims deployment", "pulsepod_mode_not_local_demo", lambda r: r["manifest"].update({"mode": "live_network"})),
        _case("PP-BAD-003", "policy hash drift", "pulsepod_policy_hash_mismatch", lambda r: r["manifest"].update({"policyHash": "sha256:wrong"})),
        _case("PP-BAD-004", "raw token routing objective", "routing_objective_not_outcome_settled", lambda r: r["manifest"].update({"routingObjective": "raw_token_price"})),
        _case("PP-BAD-005", "raw prompt logging enabled", "pulsepod_raw_logging_enabled", lambda r: r["manifest"].update({"rawPromptLogging": True})),
        _case("PP-BAD-006", "selected cheap route", "route_validation_fault:selected_route_not_highest_score", lambda r: r.update({"route": _with_route_field(r["route"], "selectedProviderId", "provider:cheap-unbonded")})),
        _case("PP-BAD-007", "selected route unbonded", "route_validation_fault:selected_route_unbonded", lambda r: _mut_selected_compute(r, "bondCoverageUnits", 0)),
        _case("PP-BAD-008", "selected route failed canary", "route_validation_fault:selected_route_failed_canary", lambda r: _mut_selected_compute(r, "canaryPassed", False)),
        _case("PP-BAD-009", "selected route privacy below policy", "route_validation_fault:selected_privacy_below_policy", lambda r: _mut_selected_compute(r, "privacyTier", "third_party")),
        _case("PP-BAD-010", "private route retained prompt", "route_validation_fault:private_route_retained_prompt", lambda r: _mut_selected_compute(r, "promptRetained", True)),
        _case("PP-BAD-011", "wrong task class", "route_validation_fault:selected_task_class_mismatch", lambda r: _mut_selected_compute(r, "taskClass", "generic_chat")),
        _case("PP-BAD-012", "latency above policy", "route_validation_fault:selected_latency_above_policy", lambda r: _mut_selected_compute(r, "latencyMs", 9_000)),
        _case("PP-BAD-013", "missing payment hash", "route_validation_fault:x402_payment_hash_missing", lambda r: _mut_selected_compute(r, "x402PaymentHash", "")),
        _case("PP-BAD-014", "action spend above policy", "route_validation_fault:action_spend_above_policy", lambda r: r["route"]["actionPulse"].update({"spendUnits": 20_000})),
        _case("PP-BAD-015", "action slippage above policy", "route_validation_fault:action_slippage_above_policy", lambda r: r["route"]["actionPulse"].update({"slippageBps": 500})),
        _case("PP-BAD-016", "FlowPulse not reader derived", "pulsepod_flowpulse_not_reader_derived", lambda r: r["route"]["flowPulseLink"].update({"source": "hook_time"})),
        _case("PP-BAD-017", "FlowPulse unconfirmed", "route_validation_fault:flowpulse_unconfirmed", lambda r: r["route"]["flowPulseLink"].update({"finality": "pending"})),
        _case("PP-BAD-018", "outcome compute mismatch", "route_validation_fault:outcome_not_linked_to_compute", lambda r: r["route"]["outcomePulse"].update({"computePulseId": "sha256:wrong"})),
        _case("PP-BAD-019", "outcome not successful", "pulsepod_outcome_not_successful", lambda r: r["route"]["outcomePulse"].update({"passed": False})),
        _case("PP-BAD-020", "provider promise mismatch", "provider_promise_provider_mismatch", lambda r: r["providerPromise"].update({"providerId": "provider:ghost"})),
        _case("PP-BAD-021", "provider promise unbonded", "provider_promise_unbonded", lambda r: r["providerPromise"].update({"bondCoverageUnits": 0})),
        _case("PP-BAD-022", "provider promise canary failed", "provider_promise_canary_failed", lambda r: r["providerPromise"].update({"canaryPassed": False})),
        _case("PP-BAD-023", "provider privacy promise missing", "provider_privacy_promise_missing", lambda r: r["providerPromise"].update({"privacyPromise": "unspecified"})),
        _case("PP-BAD-024", "missing graph evidence", "pulsepod_evidence_set_incomplete", lambda r: r["pulseGraph"].pop()),
        _case("PP-BAD-025", "graph sequence drift", "pulsepod_sequence_not_monotonic", lambda r: r["pulseGraph"][1].update({"sequence": 99})),
        _case("PP-BAD-026", "federation wrong payment rail", "federation_payment_rail_not_x402_compatible", lambda r: r["federationOffer"].update({"paymentRail": "card_only"})),
        _case("PP-BAD-027", "federation overclaims production", "federation_overclaims_production", lambda r: r["federationOffer"].update({"productionSettlement": True})),
        _case("PP-BAD-028", "federation evidence incomplete", "federation_evidence_set_incomplete", lambda r: r["federationOffer"].update({"acceptedEvidence": ["ComputePulse"]})),
        _case("PP-BAD-029", "PulsePass private reveal", "pulsepass_reveals_private_fields", lambda r: r["pulsePassClaim"]["reveals"].append("rawPrompt")),
        _case("PP-BAD-030", "PulsePass source uncommitted", "pulsepass_source_set_uncommitted", lambda r: r["pulsePassClaim"].update({"sourcePulseSetHash": "uncommitted"})),
        _case("PP-BAD-031", "negative memory credit", "negative_memory_credit", lambda r: r["memoryCredit"].update({"units": -1})),
        _case("PP-BAD-032", "memory credit marketed as money", "memory_credit_marketed_as_money", lambda r: r["memoryCredit"].update({"notMoney": False})),
        _case("PP-BAD-033", "raw prompt stored", "raw_model_content_stored", lambda r: _mut_selected_compute(r, "rawPrompt", "secret")),
        _case("PP-BAD-034", "public overclaim", "public_claim_overclaim", lambda r: r["publicClaims"].append("FlowMemory is a live compute marketplace.")),
    ]


def _case(case_id: str, label: str, expected_fault: str, mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    return {"caseId": case_id, "label": label, "expectedFault": expected_fault, "mutate": mutate}


def _with_route_field(route: dict[str, Any], field: str, value: Any) -> dict[str, Any]:
    copied = copy.deepcopy(route)
    copied[field] = value
    return copied


def _mut_selected_compute(report: dict[str, Any], field: str, value: Any) -> None:
    selected = report["route"]["selectedProviderId"]
    for pulse in report["route"]["computePulses"]:
        if pulse["providerId"] == selected:
            pulse[field] = value


def _has_raw_model_content(report: dict[str, Any]) -> bool:
    forbidden = {"rawPrompt", "rawResponse", "promptText", "responseText", "messages"}
    for value in _walk(report):
        if isinstance(value, dict) and any(key in value for key in forbidden):
            return True
    return False


def _has_public_overclaim(report: dict[str, Any]) -> bool:
    for claim in report.get("publicClaims", []):
        lower = str(claim).lower()
        if any(fragment in lower for fragment in FORBIDDEN_PUBLIC_CLAIM_FRAGMENTS):
            return True
    return False


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _hash_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
