# Threat Model

FlowMemory Warranted Agents is strongest when the failure modes are explicit.

The v0 framework is local and deterministic. It does not claim custody, wallet enforcement, production settlement, production verifier infrastructure, full privacy, zero-knowledge privacy, semantic truth, or work-quality proof.

Within that boundary, the framework targets a real problem:

```text
An agent action can look valid while the machine history behind it is incomplete, mismatched, stale, or impossible.
```

## Threat: Generic Claims Without Evidence

Risk:

```text
The agent says it completed the job, but no required evidence exists.
```

FlowMemory response:

- PolicyCard defines required evidence.
- EvidenceSchema checks local envelope fields.
- FlowBond fails missing evidence.
- PulsePass can carry the failed warranty receipt.

## Threat: Payment Without Delivery

Risk:

```text
Payment is observed, but the delivery envelope is missing.
```

FlowMemory response:

- FlowBond emits `payment_without_delivery`.
- The local bond outcome becomes `PAY_BOND_TO_USER`.
- The failed warranty becomes a FlowPulse-style memory artifact.

## Threat: Wrong Obligation Link

Risk:

```text
Evidence exists, but it belongs to a different obligation.
```

FlowMemory response:

- FlowBond checks obligation IDs.
- Mismatched envelopes produce wrong-obligation violations.
- FlowCompiler rejects analogous impossible histories.

## Threat: Arbitrary Evidence Labels

Risk:

```text
The agent submits a label named WorkDeliveryEnvelope without the required delivery fields.
```

FlowMemory response:

- EvidenceSchema defines required fields.
- Malformed local envelopes fail settlement.

## Threat: Private History Exposure

Risk:

```text
The user needs to prove a warranty state without revealing the full receipt history.
```

FlowMemory response:

- PulsePass stores receipt history.
- PrivateCompute reveals scoped predicates.
- Raw receipts, raw user ID, exact action history, and private obligation IDs remain hidden in the local proof surface.

## Threat: Overclaiming The System

Risk:

```text
Public copy must not claim live custody, production settlement, semantic truth, or proof of work quality.
```

FlowMemory response:

- ClaimGate scans README, docs, and specs.
- CI runs the claim gate.
- Risky phrases must appear only as guarded non-claims or boundary statements.

## Strongest v0 Claim

```text
FlowMemory can make an agent promise inspectable as a deterministic receipt-bound machine history.
```
