"""FlowBond local R&D proof.

FlowBond models a warranted agent action: an agent posts a bond against a
deterministic policy, and a FlowPulse-like receipt settles whether the bond is
released to the agent or paid to the user.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BondedSwapPolicy:
    bond_id: str
    agent_id: str
    user_id: str
    pair: str
    max_spend_units: int
    min_out_units: int
    max_slippage_bps: int
    bond_units: int
    expiry: int


@dataclass(frozen=True)
class SwapOutcome:
    spend_units: int
    out_units: int
    slippage_bps: int
    executed_at: int
    tx_hash: str


def settle_bonded_swap(policy: BondedSwapPolicy, outcome: SwapOutcome) -> dict[str, Any]:
    violations = _violations(policy, outcome)
    passed = not violations
    settlement = "RELEASE_BOND_TO_AGENT" if passed else "PAY_BOND_TO_USER"
    pulse = _flowpulse(policy, outcome, passed, violations)
    return {
        "schema": "flowmemory.flowbond_settlement.v0",
        "bondId": policy.bond_id,
        "agentId": policy.agent_id,
        "userId": policy.user_id,
        "policyHash": _policy_hash(policy),
        "passed": passed,
        "violations": violations,
        "settlement": settlement,
        "bondUnits": policy.bond_units,
        "flowPulse": pulse,
        "notClaims": [
            "not_profit_guarantee",
            "not_swap_control",
            "not_fund_protection",
            "not_semantic_truth",
            "not_production_adjudication",
        ],
    }


def demo_cases() -> list[dict[str, Any]]:
    policy = BondedSwapPolicy(
        bond_id="bond-001",
        agent_id="agent:flowbond-demo",
        user_id="user:local-demo",
        pair="USDC/WETH",
        max_spend_units=100_00,
        min_out_units=29_000_000_000_000_000,
        max_slippage_bps=75,
        bond_units=25_00,
        expiry=1_900_000_000,
    )
    good = SwapOutcome(
        spend_units=100_00,
        out_units=29_500_000_000_000_000,
        slippage_bps=42,
        executed_at=1_800_000_000,
        tx_hash="0x" + "11" * 32,
    )
    bad = SwapOutcome(
        spend_units=100_00,
        out_units=28_000_000_000_000_000,
        slippage_bps=140,
        executed_at=1_800_000_001,
        tx_hash="0x" + "22" * 32,
    )
    return [
        {"caseId": "FB-OK-001", "label": "bonded_swap_policy_passed", "result": settle_bonded_swap(policy, good)},
        {"caseId": "FB-BAD-001", "label": "bonded_swap_policy_violated", "result": settle_bonded_swap(policy, bad)},
    ]


def _violations(policy: BondedSwapPolicy, outcome: SwapOutcome) -> list[str]:
    violations: list[str] = []
    if outcome.spend_units > policy.max_spend_units:
        violations.append("max_spend_exceeded")
    if outcome.out_units < policy.min_out_units:
        violations.append("min_out_missed")
    if outcome.slippage_bps > policy.max_slippage_bps:
        violations.append("max_slippage_exceeded")
    if outcome.executed_at > policy.expiry:
        violations.append("policy_expired")
    return violations


def _flowpulse(
    policy: BondedSwapPolicy,
    outcome: SwapOutcome,
    passed: bool,
    violations: list[str],
) -> dict[str, Any]:
    payload = {
        "schema": "flowmemory.flowpulse.flowbond.v0",
        "pulseType": "BondedActionPulse",
        "bondId": policy.bond_id,
        "agentId": policy.agent_id,
        "policyHash": _policy_hash(policy),
        "actionType": "uniswap_v4_swap",
        "pair": policy.pair,
        "amountBucket": _bucket(policy.max_spend_units),
        "slippageBucketBps": _bucket(outcome.slippage_bps),
        "passed": passed,
        "violations": violations,
        "txHash": outcome.tx_hash,
        "outcomeHash": _hash_dict(
            {
                "spendUnits": outcome.spend_units,
                "outUnits": outcome.out_units,
                "slippageBps": outcome.slippage_bps,
                "executedAt": outcome.executed_at,
            }
        ),
    }
    payload["pulseId"] = _hash_dict(payload)
    return payload


def _policy_hash(policy: BondedSwapPolicy) -> str:
    return _hash_dict(
        {
            "agentId": policy.agent_id,
            "userId": policy.user_id,
            "pair": policy.pair,
            "maxSpendUnits": policy.max_spend_units,
            "minOutUnits": policy.min_out_units,
            "maxSlippageBps": policy.max_slippage_bps,
            "bondUnits": policy.bond_units,
            "expiry": policy.expiry,
        }
    )


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _bucket(value: int) -> str:
    if value < 100:
        return "0-99"
    if value < 1_000:
        return "100-999"
    if value < 10_000:
        return "1k-9k"
    if value < 100_000:
        return "10k-99k"
    return "100k+"

