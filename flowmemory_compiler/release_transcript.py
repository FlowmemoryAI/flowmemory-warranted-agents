"""Canonical release transcript for FlowMemory Warranted Agents."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .agent_framework import run_agent_framework_demo
from .agent_registry import run_registry_demo
from .agent_runtime import run_runtime_demo
from .bond_ledger import run_bond_ledger_demo
from .checker import check_trace
from .flowbond import demo_cases as flowbond_demo_cases
from .policycards import demo_policy_card, public_policy_view
from .private_compute import run_private_compute_demo
from .pulsepass import demo_passport, demo_proofs


def build_release_transcript(flowcompiler_cases: list[dict[str, Any]]) -> dict[str, Any]:
    framework = run_agent_framework_demo()
    flowbond_cases = flowbond_demo_cases()
    pulsepass = demo_passport()
    pulsepass_proofs = demo_proofs()
    private_compute = run_private_compute_demo()
    bond_ledger = run_bond_ledger_demo()
    registry = run_registry_demo()
    runtime = run_runtime_demo()
    flowcompiler_results = [check_trace(case) for case in flowcompiler_cases]

    valid = [item for item in flowcompiler_results if item["caseId"].startswith("FC-OK")]
    invalid = [item for item in flowcompiler_results if item["caseId"].startswith("FC-BAD")]
    transcript = {
        "schema": "flowmemory.warranted_agents_release_transcript.v0",
        "package": "flowmemory-warranted-agents",
        "coreLine": "Generic agents make claims. FlowMemory agents can leave warranted receipts.",
        "stack": [
            "AgentManifest",
            "WorkRequest",
            "PolicyCard",
            "AgentProposal",
            "AgentRegistry",
            "AgentRuntime",
            "FlowBond",
            "BondLedger",
            "FlowPulse",
            "PulsePass",
            "PrivateCompute",
            "ScopedProof",
            "FlowCompiler",
        ],
        "policyCard": public_policy_view(demo_policy_card()),
        "agentFramework": _framework_summary(framework),
        "agentRegistry": _registry_summary(registry),
        "agentRuntime": _runtime_summary(runtime),
        "flowBond": _flowbond_summary(flowbond_cases),
        "bondLedger": _bond_ledger_summary(bond_ledger),
        "pulsePass": {
            "vaultCommitment": pulsepass["vaultCommitment"],
            "receiptCount": pulsepass["receiptCount"],
            "proofs": [_proof_summary(proof) for proof in pulsepass_proofs],
        },
        "privateCompute": {
            "vaultCommitment": private_compute["vaultCommitment"],
            "programs": [
                {
                    "programId": item["programId"],
                    "passed": item["passed"],
                    "transcriptHash": item["transcriptHash"],
                    "revealed": sorted(item["revealed"].keys()),
                    "hidden": item["hidden"],
                }
                for item in private_compute["programResults"]
            ],
        },
        "flowCompiler": {
            "validAccepted": sum(item["status"] == "ACCEPTED" for item in valid),
            "validTotal": len(valid),
            "invalidRejected": sum(item["status"] == "REJECTED" for item in invalid),
            "invalidTotal": len(invalid),
            "escapedImpossibleHistories": sum(item["status"] == "ACCEPTED" for item in invalid),
        },
        "notClaims": [
            "not_custody",
            "not_wallet_enforcement",
            "not_x402_replacement",
            "not_fund_protection",
            "not_work_quality_proof",
            "not_semantic_truth",
            "not_full_privacy",
            "not_zero_knowledge",
            "not_tee",
            "not_live_base_deployment",
            "not_production_verifier",
            "not_production_bond_adjudication",
        ],
    }
    transcript["transcriptHash"] = _hash_dict(transcript)
    return transcript


def _framework_summary(framework: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifestHash": framework["agentManifest"]["manifestHash"],
        "policyHash": framework["policyCard"]["policyHash"],
        "proposalHash": framework["agentProposal"]["proposal_hash"],
        "settlements": [
            {
                "actionId": item["flowPulse"]["actionId"],
                "passed": item["passed"],
                "settlement": item["settlement"],
                "pulseId": item["flowPulse"]["pulseId"],
                "violations": item["violations"],
            }
            for item in framework["settlements"]
        ],
        "pulsePass": framework["pulsePass"],
        "scopedProofs": [_proof_summary(proof) for proof in framework["scopedProofs"]],
    }


def _flowbond_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "cases": [
            {
                "caseId": case["caseId"],
                "label": case["label"],
                "passed": case["result"]["passed"],
                "settlement": case["result"]["settlement"],
                "pulseId": case["result"]["flowPulse"]["pulseId"],
                "violations": case["result"]["violations"],
            }
            for case in cases
        ],
        "releasedToAgent": sum(1 for case in cases if case["result"]["settlement"] == "RELEASE_BOND_TO_AGENT"),
        "paidToUser": sum(1 for case in cases if case["result"]["settlement"] == "PAY_BOND_TO_USER"),
    }


def _registry_summary(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "agentCount": len(registry["agents"]),
        "eligibleAgents": sum(1 for item in registry["matches"] if item["eligible"]),
        "rejectedAgents": sum(1 for item in registry["matches"] if not item["eligible"]),
        "matches": registry["matches"],
    }


def _runtime_summary(runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "runCount": len(runtime["runs"]),
        "finalStatuses": [run["finalStatus"] for run in runtime["runs"]],
        "timelineLength": runtime["summary"]["timelineLength"],
        "settlements": [run["settlement"]["settlement"] for run in runtime["runs"]],
    }


def _bond_ledger_summary(bond_ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "receiptCount": len(bond_ledger["ledger"]["receipts"]),
        "events": [receipt["eventType"] for receipt in bond_ledger["ledger"]["receipts"]],
        "accounts": bond_ledger["ledger"]["accounts"],
    }


def _proof_summary(proof: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicate": proof["predicate"],
        "passed": proof["passed"],
        "proofHash": proof["proofHash"],
        "countBucket": proof.get("countBucket"),
    }


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
