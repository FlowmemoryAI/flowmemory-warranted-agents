"""PulsePass private receipt passport primitives."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScopedProofRequest:
    predicate: str
    threshold: int = 1


def build_pulsepass(user_id: str, receipts: list[dict[str, Any]]) -> dict[str, Any]:
    private_payload = {
        "userId": user_id,
        "receiptIds": [receipt["flowPulse"]["pulseId"] for receipt in receipts],
        "receipts": receipts,
    }
    return {
        "schema": "flowmemory.pulsepass.v0",
        "ownerHash": _hash_value(user_id),
        "receiptCount": len(receipts),
        "vaultCommitment": _hash_dict(private_payload),
        "receipts": receipts,
        "notClaims": [
            "not_full_privacy",
            "not_zero_knowledge",
            "not_identity_attestation",
            "not_reputation_score",
        ],
    }


def scoped_proof(passport: dict[str, Any], request: ScopedProofRequest) -> dict[str, Any]:
    receipts = passport["receipts"]
    count = _count(predicate=request.predicate, receipts=receipts)
    passed = count >= request.threshold
    proof_payload = {
        "ownerHash": passport["ownerHash"],
        "vaultCommitment": passport["vaultCommitment"],
        "predicate": request.predicate,
        "threshold": request.threshold,
        "countBucket": _count_bucket(count),
        "passed": passed,
    }
    return {
        "schema": "flowmemory.scoped_pulsepass_proof.v0",
        "predicate": request.predicate,
        "threshold": request.threshold,
        "passed": passed,
        "countBucket": _count_bucket(count),
        "proofHash": _hash_dict(proof_payload),
        "revealed": {
            "ownerHash": passport["ownerHash"],
            "vaultCommitment": passport["vaultCommitment"],
            "predicate": request.predicate,
            "threshold": request.threshold,
            "passed": passed,
            "countBucket": _count_bucket(count),
        },
        "hidden": [
            "raw_receipts",
            "raw_user_id",
            "exact_action_history",
            "private_obligation_ids",
        ],
    }


def demo_passport() -> dict[str, Any]:
    from .flowbond import demo_cases

    receipts = [case["result"] for case in demo_cases()]
    return build_pulsepass("user:local-demo", receipts)


def demo_proofs() -> list[dict[str, Any]]:
    passport = demo_passport()
    return [
        scoped_proof(passport, ScopedProofRequest("has_completed_warranted_action", threshold=1)),
        scoped_proof(passport, ScopedProofRequest("has_failed_warranty", threshold=1)),
        scoped_proof(passport, ScopedProofRequest("has_three_completed_warranted_actions", threshold=3)),
    ]


def _count(*, predicate: str, receipts: list[dict[str, Any]]) -> int:
    if predicate in {"has_completed_warranted_action", "has_three_completed_warranted_actions"}:
        return sum(1 for receipt in receipts if receipt.get("passed") is True)
    if predicate == "has_failed_warranty":
        return sum(1 for receipt in receipts if receipt.get("passed") is False)
    if predicate == "has_flowpulse_receipt":
        return len(receipts)
    return 0


def _count_bucket(count: int) -> str:
    if count == 0:
        return "0"
    if count == 1:
        return "1"
    if count <= 5:
        return "2-5"
    if count <= 25:
        return "6-25"
    return "26+"


def _hash_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
