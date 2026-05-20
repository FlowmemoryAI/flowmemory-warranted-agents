"""Explicit state machine for warranted-agent runtime histories."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


INITIAL = "INITIAL"
MANIFEST_LOADED = "MANIFEST_LOADED"
POLICY_QUOTED = "POLICY_QUOTED"
BOND_LOCKED = "BOND_LOCKED"
ACTION_EXECUTED = "ACTION_EXECUTED"
FLOWBOND_SETTLED = "FLOWBOND_SETTLED"
PRIVATE_PROOF_READY = "PRIVATE_PROOF_READY"
WARRANTY_RELEASED = "WARRANTY_RELEASED"
USER_PAID_FROM_BOND = "USER_PAID_FROM_BOND"

TERMINAL_STATES = {WARRANTY_RELEASED, USER_PAID_FROM_BOND}

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    INITIAL: {MANIFEST_LOADED},
    MANIFEST_LOADED: {POLICY_QUOTED},
    POLICY_QUOTED: {BOND_LOCKED},
    BOND_LOCKED: {ACTION_EXECUTED},
    ACTION_EXECUTED: {FLOWBOND_SETTLED},
    FLOWBOND_SETTLED: {PRIVATE_PROOF_READY},
    PRIVATE_PROOF_READY: {WARRANTY_RELEASED, USER_PAID_FROM_BOND},
    WARRANTY_RELEASED: set(),
    USER_PAID_FROM_BOND: set(),
}


@dataclass(frozen=True)
class StateTransition:
    from_state: str
    to_state: str
    phase: str
    status: str
    idempotency_key: str
    fields: dict[str, Any]
    transition_hash: str


class RuntimeStateMachine:
    """Small deterministic state machine with replay-key rejection."""

    def __init__(self) -> None:
        self.current_state = INITIAL
        self.transitions: list[StateTransition] = []
        self._seen_idempotency_keys: set[str] = set()

    def transition(
        self,
        to_state: str,
        *,
        phase: str,
        status: str,
        idempotency_key: str,
        fields: dict[str, Any],
    ) -> StateTransition:
        if idempotency_key in self._seen_idempotency_keys:
            raise ValueError(f"duplicate idempotency key: {idempotency_key}")
        allowed = ALLOWED_TRANSITIONS[self.current_state]
        if to_state not in allowed:
            raise ValueError(f"invalid transition: {self.current_state} -> {to_state}")
        payload = {
            "fromState": self.current_state,
            "toState": to_state,
            "phase": phase,
            "status": status,
            "idempotencyKey": idempotency_key,
            "fields": fields,
        }
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            phase=phase,
            status=status,
            idempotency_key=idempotency_key,
            fields=fields,
            transition_hash=_hash_dict(payload),
        )
        self._seen_idempotency_keys.add(idempotency_key)
        self.current_state = to_state
        self.transitions.append(transition)
        return transition

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "flowmemory.runtime_state_machine.v0",
            "currentState": self.current_state,
            "terminal": self.current_state in TERMINAL_STATES,
            "transitionCount": len(self.transitions),
            "transitions": [transition_to_public(item) for item in self.transitions],
            "notClaims": [
                "not_external_runtime",
                "not_distributed_consensus",
                "not_wallet_execution",
                "not_production_settlement",
            ],
        }


def transition_to_public(transition: StateTransition) -> dict[str, Any]:
    return {
        "fromState": transition.from_state,
        "toState": transition.to_state,
        "phase": transition.phase,
        "status": transition.status,
        "idempotencyKey": transition.idempotency_key,
        "transitionHash": transition.transition_hash,
        "fields": transition.fields,
    }


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
