"""Local envelope capture helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from typing import Any


def capture_command(
    *,
    step_id: str,
    tree_hash: str,
    command: list[str],
    observed_sequence: int = 1,
) -> dict[str, Any]:
    """Run a local command and return a TestRunEnvelope.

    This is intentionally small: it captures command identity, exit code, stdout
    hash, stderr hash, and the tree hash supplied by the caller. It does not
    claim to prove code correctness or production provenance.
    """

    completed = subprocess.run(command, capture_output=True, text=False, check=False)
    fields = {
        "command": command,
        "exitCode": completed.returncode,
        "treeHash": tree_hash,
        "stdoutHash": _sha256(completed.stdout),
        "stderrHash": _sha256(completed.stderr),
    }
    envelope_id = _envelope_id(step_id, observed_sequence, fields)
    return {
        "schema": "flowmemory.evidence_envelope.v0",
        "envelopeId": envelope_id,
        "envelopeType": "TestRunEnvelope",
        "stepId": step_id,
        "observedSequence": observed_sequence,
        "fields": fields,
        "notClaims": [
            "not_code_correctness",
            "not_semantic_truth",
            "not_model_correctness",
            "not_production_provenance",
        ],
    }


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _envelope_id(step_id: str, observed_sequence: int, fields: dict[str, Any]) -> str:
    payload = {
        "stepId": step_id,
        "observedSequence": observed_sequence,
        "fields": fields,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256(encoded)

