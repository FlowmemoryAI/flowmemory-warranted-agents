"""Local bond ledger for warranted-agent demos.

The ledger models bond accounting for development and tests. It is not custody,
escrow, production settlement, or a wallet.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from .agent_framework import run_agent_framework_demo


@dataclass(frozen=True)
class BondAccount:
    account_id: str
    balance_units: int


@dataclass(frozen=True)
class OpenBond:
    bond_id: str
    policy_hash: str
    agent_id: str
    user_id: str
    bond_units: int
    status: str


class LocalBondLedger:
    def __init__(self, accounts: list[BondAccount]) -> None:
        self.accounts = {account.account_id: account.balance_units for account in accounts}
        self.open_bonds: dict[str, OpenBond] = {}
        self.receipts: list[dict[str, Any]] = []

    def open_bond(self, *, policy_hash: str, agent_id: str, user_id: str, bond_units: int) -> dict[str, Any]:
        if self.accounts.get(agent_id, 0) < bond_units:
            raise ValueError("agent balance too low for requested bond")
        bond_id = "bond:" + _hash_dict(
            {
                "policyHash": policy_hash,
                "agentId": agent_id,
                "userId": user_id,
                "bondUnits": bond_units,
                "nonce": len(self.open_bonds),
            }
        ).split(":", 1)[1][:16]
        self.accounts[agent_id] -= bond_units
        self.open_bonds[bond_id] = OpenBond(
            bond_id=bond_id,
            policy_hash=policy_hash,
            agent_id=agent_id,
            user_id=user_id,
            bond_units=bond_units,
            status="LOCKED",
        )
        receipt = self._receipt("BOND_LOCKED", bond_id, {"bondUnits": bond_units})
        self.receipts.append(receipt)
        return receipt

    def settle_bond(self, *, bond_id: str, settlement: dict[str, Any]) -> dict[str, Any]:
        bond = self.open_bonds[bond_id]
        if bond.status != "LOCKED":
            raise ValueError("bond is not locked")
        action = settlement["settlement"]
        if action == "RELEASE_BOND_TO_AGENT":
            self.accounts[bond.agent_id] = self.accounts.get(bond.agent_id, 0) + bond.bond_units
        elif action == "PAY_BOND_TO_USER":
            self.accounts[bond.user_id] = self.accounts.get(bond.user_id, 0) + bond.bond_units
        else:
            raise ValueError(f"unknown settlement action: {action}")
        self.open_bonds[bond_id] = OpenBond(
            bond_id=bond.bond_id,
            policy_hash=bond.policy_hash,
            agent_id=bond.agent_id,
            user_id=bond.user_id,
            bond_units=bond.bond_units,
            status="SETTLED",
        )
        receipt = self._receipt(
            action,
            bond_id,
            {
                "bondUnits": bond.bond_units,
                "settlementPulseId": settlement["flowPulse"]["pulseId"],
                "policyHash": settlement["policyHash"],
            },
        )
        self.receipts.append(receipt)
        return receipt

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "flowmemory.local_bond_ledger_snapshot.v0",
            "accounts": dict(sorted(self.accounts.items())),
            "openBonds": {key: asdict(value) for key, value in sorted(self.open_bonds.items())},
            "receipts": list(self.receipts),
            "notClaims": [
                "not_custody",
                "not_escrow",
                "not_wallet",
                "not_production_settlement",
            ],
        }

    def _receipt(self, event_type: str, bond_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "schema": "flowmemory.bond_ledger_receipt.v0",
            "eventType": event_type,
            "bondId": bond_id,
            "sequence": len(self.receipts) + 1,
            "fields": fields,
        }
        payload["receiptId"] = _hash_dict(payload)
        return payload


def run_bond_ledger_demo() -> dict[str, Any]:
    framework = run_agent_framework_demo()
    agent_id = framework["agentManifest"]["agent_id"]
    user_id = "user:local-demo"
    ledger = LocalBondLedger(
        [
            BondAccount(agent_id, 100_00),
            BondAccount(user_id, 0),
        ]
    )
    lock_receipt = ledger.open_bond(
        policy_hash=framework["policyCard"]["policyHash"],
        agent_id=agent_id,
        user_id=user_id,
        bond_units=framework["agentProposal"]["bond_units"],
    )
    success_receipt = ledger.settle_bond(
        bond_id=lock_receipt["bondId"],
        settlement=framework["settlements"][0],
    )
    lock_receipt_2 = ledger.open_bond(
        policy_hash=framework["policyCard"]["policyHash"],
        agent_id=agent_id,
        user_id=user_id,
        bond_units=framework["agentProposal"]["bond_units"],
    )
    failure_receipt = ledger.settle_bond(
        bond_id=lock_receipt_2["bondId"],
        settlement=framework["settlements"][1],
    )
    return {
        "schema": "flowmemory.bond_ledger_demo.v0",
        "lockReceipt": lock_receipt,
        "successReceipt": success_receipt,
        "failureLockReceipt": lock_receipt_2,
        "failureReceipt": failure_receipt,
        "ledger": ledger.snapshot(),
    }


def _hash_dict(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()

