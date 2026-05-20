"""PulseRouter local proof for outcome-settled agent work.

PulseRouter routes model/provider work by expected successful outcomes, not raw
token price. It emits receipt-like pulses for compute, tool use, proposed action,
FlowPulse evidence, and final outcome settlement.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


PRIVACY_RANK = {
    "public": 0,
    "third_party": 1,
    "private": 2,
    "tee_private": 3,
    "local": 4,
}


@dataclass(frozen=True)
class OutcomePolicy:
    policy_id: str
    user_id: str
    action_type: str
    allowed_task_class: str
    max_spend_units: int
    max_slippage_bps: int
    max_latency_ms: int
    min_privacy_tier: str
    require_bonded_route: bool
    require_canary_pass: bool
    expected_action_value_units: int
    user_risk_units: int
    agent_reward_units: int


@dataclass(frozen=True)
class ProviderQuote:
    provider_id: str
    model: str
    model_class: str
    task_class: str
    privacy_tier: str
    quoted_price_units: int
    latency_ms: int
    expected_success_bps: int
    bond_coverage_units: int
    canary_passed: bool
    output_schema_valid: bool
    prompt_retained: bool
    x402_payment_hash: str = ""


def demo_policy() -> OutcomePolicy:
    return OutcomePolicy(
        policy_id="policy:swap-outcome-001",
        user_id="user:local-demo",
        action_type="uniswap_v4_swap",
        allowed_task_class="defi_swap_recommendation",
        max_spend_units=10_000,
        max_slippage_bps=50,
        max_latency_ms=4_000,
        min_privacy_tier="private",
        require_bonded_route=True,
        require_canary_pass=True,
        expected_action_value_units=100,
        user_risk_units=80,
        agent_reward_units=25,
    )


def demo_quotes() -> list[ProviderQuote]:
    return [
        ProviderQuote(
            provider_id="provider:cheap-unbonded",
            model="cheap-local-router",
            model_class="small",
            task_class="defi_swap_recommendation",
            privacy_tier="third_party",
            quoted_price_units=1,
            latency_ms=900,
            expected_success_bps=3_500,
            bond_coverage_units=0,
            canary_passed=False,
            output_schema_valid=True,
            prompt_retained=True,
            x402_payment_hash="sha256:x402-cheap",
        ),
        ProviderQuote(
            provider_id="provider:private-bonded",
            model="private-action-model",
            model_class="mid",
            task_class="defi_swap_recommendation",
            privacy_tier="private",
            quoted_price_units=4,
            latency_ms=1_800,
            expected_success_bps=8_200,
            bond_coverage_units=500,
            canary_passed=True,
            output_schema_valid=True,
            prompt_retained=False,
            x402_payment_hash="sha256:x402-private",
        ),
        ProviderQuote(
            provider_id="provider:frontier-unbonded",
            model="frontier-general",
            model_class="frontier",
            task_class="defi_swap_recommendation",
            privacy_tier="third_party",
            quoted_price_units=12,
            latency_ms=2_400,
            expected_success_bps=8_700,
            bond_coverage_units=0,
            canary_passed=True,
            output_schema_valid=True,
            prompt_retained=True,
            x402_payment_hash="sha256:x402-frontier",
        ),
    ]


def route_score(policy: OutcomePolicy, quote: ProviderQuote) -> dict[str, Any]:
    reasons = _eligibility_reasons(policy, quote)
    eligible = not reasons
    expected_value = quote.expected_success_bps * policy.expected_action_value_units // 10_000
    failure_penalty = (10_000 - quote.expected_success_bps) * policy.user_risk_units // 10_000
    latency_penalty = quote.latency_ms // 250
    privacy_penalty = max(0, PRIVACY_RANK[policy.min_privacy_tier] - PRIVACY_RANK[quote.privacy_tier]) * 25
    bond_bonus = min(quote.bond_coverage_units, policy.user_risk_units) // 4
    score = expected_value - quote.quoted_price_units - latency_penalty - privacy_penalty - failure_penalty + bond_bonus
    if not eligible:
        score -= 1_000
    return {
        "schema": "flowmemory.route_score.v0",
        "providerId": quote.provider_id,
        "eligible": eligible,
        "reasons": reasons,
        "expectedValueUnits": expected_value,
        "failurePenaltyUnits": failure_penalty,
        "latencyPenaltyUnits": latency_penalty,
        "privacyPenaltyUnits": privacy_penalty,
        "bondBonusUnits": bond_bonus,
        "quotedPriceUnits": quote.quoted_price_units,
        "scoreUnits": score,
    }


def run_pulserouter_demo() -> dict[str, Any]:
    policy = demo_policy()
    quotes = demo_quotes()
    route_scores = [route_score(policy, quote) for quote in quotes]
    selected_score = max(route_scores, key=lambda item: item["scoreUnits"])
    selected_quote = next(quote for quote in quotes if quote.provider_id == selected_score["providerId"])

    prompt = "Use my policy to prepare a safe USDC to ETH swap."
    response = {
        "recommendation": "swap_usdc_to_eth",
        "spendUnits": 9_500,
        "slippageBps": 35,
        "pool": "uniswap-v4-demo-pool",
    }
    compute_pulses = [compute_pulse(policy, quote, prompt, response if quote == selected_quote else {"recommendation": "candidate"}) for quote in quotes]
    selected_compute = next(pulse for pulse in compute_pulses if pulse["providerId"] == selected_quote.provider_id)
    tool_pulse = tool_call_pulse(selected_compute, "x402.quote", {"paymentHash": selected_quote.x402_payment_hash})
    action = action_pulse(policy, selected_compute, tool_pulse, response)
    flowpulse = flowpulse_link(policy, action, tx_hash="0x" + "ab" * 32, log_index=7)
    outcome = outcome_pulse(policy, selected_score, selected_compute, action, flowpulse, passed=True)
    report = {
        "schema": "flowmemory.pulserouter_demo.v0",
        "categoryClaim": "Outcome-settled AI routes intelligence by receipt-backed success, not token price.",
        "policy": _public_policy(policy),
        "quotes": [_public_quote(quote) for quote in quotes],
        "routeScores": route_scores,
        "selectedProviderId": selected_quote.provider_id,
        "computePulses": compute_pulses,
        "toolPulse": tool_pulse,
        "actionPulse": action,
        "flowPulseLink": flowpulse,
        "outcomePulse": outcome,
        "effectiveCostPerSuccessfulOutcomeUnits": outcome["effectiveCostPerSuccessfulOutcomeUnits"],
        "portableUserMemory": {
            "pulsePassPredicate": "has_private_bonded_successful_defi_action",
            "earned": True,
            "reveals": ["ownerHash", "predicate", "countBucket", "proofHash"],
            "hides": ["raw_prompt", "raw_wallet_history", "all_provider_routes", "private_obligation_ids"],
        },
        "validationFaults": [],
        "notClaims": [
            "not_live_provider_marketplace",
            "not_production_wallet",
            "not_production_settlement",
            "not_full_privacy",
            "not_zero_knowledge",
            "not_tee_attestation",
            "not_model_correctness",
            "not_profit_guarantee",
        ],
    }
    report["validationFaults"] = validate_outcome_report(report)
    return report


def run_pulserouter_adversary_suite() -> dict[str, Any]:
    base = run_pulserouter_demo()
    cases = _adversarial_cases(base)
    results = []
    for case in cases:
        report = copy.deepcopy(base)
        case["mutate"](report)
        faults = validate_outcome_report(report)
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
        "schema": "flowmemory.pulserouter_adversary_suite.v0",
        "cases": [{key: value for key, value in item.items() if key != "mutate"} for item in cases],
        "results": results,
        "caught": sum(1 for item in results if item["caught"]),
        "total": len(results),
        "passed": all(item["caught"] for item in results),
    }


def compute_pulse(policy: OutcomePolicy, quote: ProviderQuote, prompt: str, response: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": "flowmemory.compute_pulse.v0",
        "providerId": quote.provider_id,
        "model": quote.model,
        "modelClass": quote.model_class,
        "taskClass": quote.task_class,
        "policyHash": _hash_dict(_public_policy(policy)),
        "modelHash": _hash_value(quote.model),
        "requestHash": _hash_value(prompt),
        "responseHash": _hash_dict(response),
        "quotedPriceUnits": quote.quoted_price_units,
        "latencyMs": quote.latency_ms,
        "latencyBucket": _latency_bucket(quote.latency_ms),
        "privacyTier": quote.privacy_tier,
        "promptRetained": quote.prompt_retained,
        "canaryPassed": quote.canary_passed,
        "outputSchemaValid": quote.output_schema_valid,
        "bondCoverageUnits": quote.bond_coverage_units,
        "x402PaymentHash": quote.x402_payment_hash,
    }
    payload["pulseId"] = _hash_dict(payload)
    return payload


def tool_call_pulse(parent: dict[str, Any], tool_name: str, fields: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": "flowmemory.tool_call_pulse.v0",
        "parentPulseId": parent["pulseId"],
        "toolName": tool_name,
        "fieldsHash": _hash_dict(fields),
        "x402PaymentHash": fields.get("paymentHash", ""),
    }
    payload["pulseId"] = _hash_dict(payload)
    return payload


def action_pulse(policy: OutcomePolicy, compute: dict[str, Any], tool: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": "flowmemory.action_pulse.v0",
        "parentPulseId": compute["pulseId"],
        "toolPulseId": tool["pulseId"],
        "policyHash": _hash_dict(_public_policy(policy)),
        "actionType": policy.action_type,
        "actionHash": _hash_dict(action),
        "spendUnits": action["spendUnits"],
        "slippageBps": action["slippageBps"],
    }
    payload["pulseId"] = _hash_dict(payload)
    return payload


def flowpulse_link(policy: OutcomePolicy, action: dict[str, Any], *, tx_hash: str, log_index: int) -> dict[str, Any]:
    payload = {
        "schema": "flowmemory.flowpulse_link.v0",
        "source": "reader_derived",
        "actionPulseId": action["pulseId"],
        "rootfieldId": _hash_value(policy.user_id),
        "commitment": action["actionHash"],
        "txHash": tx_hash,
        "logIndex": log_index,
        "finality": "confirmed",
    }
    payload["flowPulseId"] = _hash_dict(payload)
    return payload


def outcome_pulse(
    policy: OutcomePolicy,
    score: dict[str, Any],
    compute: dict[str, Any],
    action: dict[str, Any],
    flowpulse: dict[str, Any],
    *,
    passed: bool,
) -> dict[str, Any]:
    total_cost = compute["quotedPriceUnits"] + policy.agent_reward_units
    payload = {
        "schema": "flowmemory.outcome_pulse.v0",
        "providerId": compute["providerId"],
        "computePulseId": compute["pulseId"],
        "actionPulseId": action["pulseId"],
        "flowPulseId": flowpulse["flowPulseId"],
        "policyHash": action["policyHash"],
        "passed": passed,
        "settlement": "PAY_PROVIDER_RELEASE_BOND" if passed else "PAY_USER_FROM_BOND",
        "agentRewardUnits": policy.agent_reward_units if passed else 0,
        "providerPaidUnits": compute["quotedPriceUnits"] if passed else 0,
        "userBondPaymentUnits": 0 if passed else min(compute["bondCoverageUnits"], policy.user_risk_units),
        "routeScoreUnits": score["scoreUnits"],
        "effectiveCostPerSuccessfulOutcomeUnits": total_cost if passed else None,
    }
    payload["pulseId"] = _hash_dict(payload)
    return payload


def validate_outcome_report(report: dict[str, Any]) -> list[str]:
    faults: list[str] = []
    policy = report["policy"]
    selected_provider = report.get("selectedProviderId")
    scores = report.get("routeScores", [])
    selected_score = next((item for item in scores if item.get("providerId") == selected_provider), None)
    eligible_scores = [item for item in scores if item.get("eligible")]
    compute_pulses = report.get("computePulses", [])
    selected_compute = next((item for item in compute_pulses if item.get("providerId") == selected_provider), None)
    action = report.get("actionPulse", {})
    flowpulse = report.get("flowPulseLink", {})
    outcome = report.get("outcomePulse", {})

    if not compute_pulses:
        faults.append("missing_compute_pulses")
    if selected_score is None:
        faults.append("selected_route_score_missing")
    elif not selected_score.get("eligible"):
        faults.append("selected_route_ineligible")
    if eligible_scores and selected_score and selected_score["scoreUnits"] != max(item["scoreUnits"] for item in eligible_scores):
        faults.append("selected_route_not_highest_score")
    if selected_compute is None:
        faults.append("selected_compute_missing")
        return sorted(set(faults))

    if policy["requireBondedRoute"] and selected_compute["bondCoverageUnits"] <= 0:
        faults.append("selected_route_unbonded")
    if policy["requireCanaryPass"] and not selected_compute["canaryPassed"]:
        faults.append("selected_route_failed_canary")
    if not selected_compute["outputSchemaValid"]:
        faults.append("selected_output_schema_invalid")
    if _privacy_rank(selected_compute["privacyTier"]) < _privacy_rank(policy["minPrivacyTier"]):
        faults.append("selected_privacy_below_policy")
    if selected_compute["privacyTier"] in {"private", "tee_private", "local"} and selected_compute["promptRetained"]:
        faults.append("private_route_retained_prompt")
    if selected_compute["taskClass"] != policy["allowedTaskClass"]:
        faults.append("selected_task_class_mismatch")
    if selected_compute["latencyMs"] > policy["maxLatencyMs"]:
        faults.append("selected_latency_above_policy")
    if not selected_compute.get("x402PaymentHash", "").startswith("sha256:"):
        faults.append("x402_payment_hash_missing")

    if action.get("parentPulseId") != selected_compute["pulseId"]:
        faults.append("action_not_parented_to_selected_compute")
    if action.get("policyHash") != selected_compute.get("policyHash"):
        faults.append("action_policy_hash_mismatch")
    if action.get("spendUnits", 0) > policy["maxSpendUnits"]:
        faults.append("action_spend_above_policy")
    if action.get("slippageBps", 10_000) > policy["maxSlippageBps"]:
        faults.append("action_slippage_above_policy")
    if flowpulse.get("actionPulseId") != action.get("pulseId"):
        faults.append("flowpulse_not_linked_to_action")
    if flowpulse.get("source") != "reader_derived":
        faults.append("flowpulse_receipt_source_not_reader_derived")
    if not flowpulse.get("txHash"):
        faults.append("flowpulse_txhash_missing")
    if flowpulse.get("finality") != "confirmed":
        faults.append("flowpulse_unconfirmed")
    if flowpulse.get("commitment") != action.get("actionHash"):
        faults.append("flowpulse_commitment_mismatch")
    if outcome.get("computePulseId") != selected_compute["pulseId"]:
        faults.append("outcome_not_linked_to_compute")
    if outcome.get("actionPulseId") != action.get("pulseId"):
        faults.append("outcome_not_linked_to_action")
    if outcome.get("flowPulseId") != flowpulse.get("flowPulseId"):
        faults.append("outcome_not_linked_to_flowpulse")

    policy_passed = not any(
        fault
        in faults
        for fault in {
            "selected_route_ineligible",
            "selected_route_unbonded",
            "selected_route_failed_canary",
            "selected_output_schema_invalid",
            "selected_privacy_below_policy",
            "private_route_retained_prompt",
            "selected_task_class_mismatch",
            "selected_latency_above_policy",
            "action_spend_above_policy",
            "action_slippage_above_policy",
            "flowpulse_not_linked_to_action",
            "flowpulse_commitment_mismatch",
        }
    )
    if outcome.get("passed") and not policy_passed:
        faults.append("outcome_passed_despite_policy_fault")
    if outcome.get("passed") and outcome.get("settlement") != "PAY_PROVIDER_RELEASE_BOND":
        faults.append("passed_outcome_wrong_settlement")
    if not outcome.get("passed") and outcome.get("providerPaidUnits", 0) > 0:
        faults.append("failed_outcome_paid_provider")
    if outcome.get("passed"):
        expected_cost = selected_compute["quotedPriceUnits"] + policy["agentRewardUnits"]
        if outcome.get("effectiveCostPerSuccessfulOutcomeUnits") != expected_cost:
            faults.append("effective_cost_mismatch")
    if not outcome.get("passed") and outcome.get("effectiveCostPerSuccessfulOutcomeUnits") is not None:
        faults.append("failed_outcome_has_success_cost")
    if _has_negative_metric(report):
        faults.append("negative_route_metric")
    if _has_raw_model_content(report):
        faults.append("raw_model_content_stored")
    return sorted(set(faults))


def _adversarial_cases(base: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _case("PR-BAD-001", "missing compute pulses", "missing_compute_pulses", lambda r: r.update({"computePulses": []})),
        _case("PR-BAD-002", "selected unknown provider", "selected_route_score_missing", lambda r: r.update({"selectedProviderId": "provider:ghost"})),
        _case("PR-BAD-003", "selected lower route", "selected_route_not_highest_score", lambda r: r.update({"selectedProviderId": "provider:cheap-unbonded"})),
        _case("PR-BAD-004", "unbonded selected route", "selected_route_unbonded", lambda r: _mut_selected_compute(r, "bondCoverageUnits", 0)),
        _case("PR-BAD-005", "failed canary selected", "selected_route_failed_canary", lambda r: _mut_selected_compute(r, "canaryPassed", False)),
        _case("PR-BAD-006", "invalid output schema", "selected_output_schema_invalid", lambda r: _mut_selected_compute(r, "outputSchemaValid", False)),
        _case("PR-BAD-007", "privacy below policy", "selected_privacy_below_policy", lambda r: _mut_selected_compute(r, "privacyTier", "third_party")),
        _case("PR-BAD-008", "private route retained prompt", "private_route_retained_prompt", lambda r: _mut_selected_compute(r, "promptRetained", True)),
        _case("PR-BAD-009", "wrong task class", "selected_task_class_mismatch", lambda r: _mut_selected_compute(r, "taskClass", "generic_chat")),
        _case("PR-BAD-010", "latency above policy", "selected_latency_above_policy", lambda r: _mut_selected_compute(r, "latencyMs", 9_000)),
        _case("PR-BAD-011", "missing x402 payment hash", "x402_payment_hash_missing", lambda r: _mut_selected_compute(r, "x402PaymentHash", "")),
        _case("PR-BAD-012", "action parent drift", "action_not_parented_to_selected_compute", lambda r: r["actionPulse"].update({"parentPulseId": "sha256:other"})),
        _case("PR-BAD-013", "spend above policy", "action_spend_above_policy", lambda r: r["actionPulse"].update({"spendUnits": 20_000})),
        _case("PR-BAD-014", "slippage above policy", "action_slippage_above_policy", lambda r: r["actionPulse"].update({"slippageBps": 400})),
        _case("PR-BAD-015", "FlowPulse action mismatch", "flowpulse_not_linked_to_action", lambda r: r["flowPulseLink"].update({"actionPulseId": "sha256:wrong"})),
        _case("PR-BAD-016", "FlowPulse source not reader derived", "flowpulse_receipt_source_not_reader_derived", lambda r: r["flowPulseLink"].update({"source": "hook_time"})),
        _case("PR-BAD-017", "FlowPulse txHash missing", "flowpulse_txhash_missing", lambda r: r["flowPulseLink"].update({"txHash": ""})),
        _case("PR-BAD-018", "FlowPulse commitment mismatch", "flowpulse_commitment_mismatch", lambda r: r["flowPulseLink"].update({"commitment": "sha256:wrong"})),
        _case("PR-BAD-019", "outcome compute mismatch", "outcome_not_linked_to_compute", lambda r: r["outcomePulse"].update({"computePulseId": "sha256:wrong"})),
        _case("PR-BAD-020", "wrong pass settlement", "passed_outcome_wrong_settlement", lambda r: r["outcomePulse"].update({"settlement": "PAY_USER_FROM_BOND"})),
        _case("PR-BAD-021", "failed outcome paid provider", "failed_outcome_paid_provider", lambda r: r["outcomePulse"].update({"passed": False, "providerPaidUnits": 4})),
        _case("PR-BAD-022", "effective cost mismatch", "effective_cost_mismatch", lambda r: r["outcomePulse"].update({"effectiveCostPerSuccessfulOutcomeUnits": 999})),
        _case("PR-BAD-023", "negative route metric", "negative_route_metric", lambda r: _mut_selected_compute(r, "quotedPriceUnits", -10)),
        _case("PR-BAD-024", "policy hash drift", "action_policy_hash_mismatch", lambda r: r["actionPulse"].update({"policyHash": "sha256:wrong"})),
        _case("PR-BAD-025", "raw prompt stored", "raw_model_content_stored", lambda r: _mut_selected_compute(r, "rawPrompt", "secret prompt")),
        _case("PR-BAD-026", "unconfirmed FlowPulse", "flowpulse_unconfirmed", lambda r: r["flowPulseLink"].update({"finality": "pending"})),
    ]


def _case(case_id: str, label: str, expected_fault: str, mutate) -> dict[str, Any]:
    return {"caseId": case_id, "label": label, "expectedFault": expected_fault, "mutate": mutate}


def _mut_selected_compute(report: dict[str, Any], field: str, value: Any) -> None:
    selected = report["selectedProviderId"]
    for pulse in report["computePulses"]:
        if pulse["providerId"] == selected:
            pulse[field] = value


def _has_negative_metric(report: dict[str, Any]) -> bool:
    metric_fields = {
        "quotedPriceUnits",
        "latencyMs",
        "bondCoverageUnits",
        "providerPaidUnits",
        "agentRewardUnits",
        "userBondPaymentUnits",
        "effectiveCostPerSuccessfulOutcomeUnits",
    }
    for value in _walk(report):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in metric_fields and isinstance(item, int) and item < 0:
                    return True
    return False


def _has_raw_model_content(report: dict[str, Any]) -> bool:
    forbidden = {"rawPrompt", "rawResponse", "promptText", "responseText", "messages"}
    for value in _walk(report):
        if isinstance(value, dict) and any(key in value for key in forbidden):
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


def _eligibility_reasons(policy: OutcomePolicy, quote: ProviderQuote) -> list[str]:
    reasons = []
    if policy.require_bonded_route and quote.bond_coverage_units <= 0:
        reasons.append("unbonded_route")
    if policy.require_canary_pass and not quote.canary_passed:
        reasons.append("canary_failed")
    if not quote.output_schema_valid:
        reasons.append("output_schema_invalid")
    if quote.task_class != policy.allowed_task_class:
        reasons.append("task_class_mismatch")
    if quote.latency_ms > policy.max_latency_ms:
        reasons.append("latency_above_policy")
    if _privacy_rank(quote.privacy_tier) < _privacy_rank(policy.min_privacy_tier):
        reasons.append("privacy_below_policy")
    if quote.privacy_tier in {"private", "tee_private", "local"} and quote.prompt_retained:
        reasons.append("private_route_retained_prompt")
    return reasons


def _public_policy(policy: OutcomePolicy) -> dict[str, Any]:
    payload = asdict(policy)
    payload["policyHash"] = _hash_dict(payload)
    payload["userHash"] = _hash_value(policy.user_id)
    payload.pop("user_id", None)
    return _camelize(payload)


def _public_quote(quote: ProviderQuote) -> dict[str, Any]:
    return _camelize(asdict(quote))


def _camelize(payload: dict[str, Any]) -> dict[str, Any]:
    return {(_to_camel(key)): value for key, value in payload.items()}


def _to_camel(key: str) -> str:
    head, *tail = key.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in tail)


def _latency_bucket(latency_ms: int) -> str:
    if latency_ms <= 1_000:
        return "0-1s"
    if latency_ms <= 3_000:
        return "1-3s"
    return "3s+"


def _privacy_rank(tier: str) -> int:
    return PRIVACY_RANK.get(tier, -1)


def _hash_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
