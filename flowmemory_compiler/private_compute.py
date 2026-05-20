"""Private computation layer for PulsePass scoped proofs.

The local v0 computes predicates over a PulsePass vault and returns a proof-like
transcript hash. It is not zero-knowledge, TEE-backed, or production privacy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .pulsepass import ScopedProofRequest, demo_passport, scoped_proof


@dataclass(frozen=True)
class PrivateMemoryProgram:
    program_id: str
    predicate: str
    threshold: int
    reveal: tuple[str, ...]


def run_private_memory_program(passport: dict[str, Any], program: PrivateMemoryProgram) -> dict[str, Any]:
    proof = scoped_proof(passport, ScopedProofRequest(program.predicate, threshold=program.threshold))
    revealed = {key: proof["revealed"][key] for key in program.reveal if key in proof["revealed"]}
    transcript = {
        "programId": program.program_id,
        "vaultCommitment": passport["vaultCommitment"],
        "predicate": program.predicate,
        "threshold": program.threshold,
        "revealed": revealed,
        "hidden": proof["hidden"],
    }
    return {
        "schema": "flowmemory.private_memory_result.v0",
        "programId": program.program_id,
        "passed": proof["passed"],
        "revealed": revealed,
        "hidden": proof["hidden"],
        "transcriptHash": _hash_dict(transcript),
        "notClaims": [
            "not_zero_knowledge",
            "not_tee",
            "not_full_privacy",
            "not_identity_attestation",
        ],
    }


def demo_programs() -> list[PrivateMemoryProgram]:
    return [
        PrivateMemoryProgram(
            program_id="private-program:completed-warranty",
            predicate="has_completed_warranted_action",
            threshold=1,
            reveal=("ownerHash", "vaultCommitment", "predicate", "passed"),
        ),
        PrivateMemoryProgram(
            program_id="private-program:failed-warranty",
            predicate="has_failed_warranty",
            threshold=1,
            reveal=("vaultCommitment", "predicate", "passed", "countBucket"),
        ),
    ]


def run_private_compute_demo() -> dict[str, Any]:
    passport = demo_passport()
    results = [run_private_memory_program(passport, program) for program in demo_programs()]
    return {
        "schema": "flowmemory.private_compute_demo.v0",
        "vaultCommitment": passport["vaultCommitment"],
        "programResults": results,
        "notClaims": [
            "not_zero_knowledge",
            "not_tee",
            "not_full_privacy",
            "not_production_private_compute",
        ],
    }


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()

