# FlowMemory Warranted Agents Stack

## Core Line

Generic agents make claims. FlowMemory agents can leave warranted receipts.

## What This Builds

FlowMemory Warranted Agents is a product stack for autonomous actions that should not be trusted on final-answer text alone.

The user defines a promise.

The agent bonds the promise.

The action produces FlowPulse memory.

The user privately carries the receipt.

The user selectively proves what matters later.

```text
PolicyCard -> FlowBond -> FlowPulse -> PulsePass -> Scoped Proof
```

## Layer 1: PolicyCard

A `PolicyCard` is the portable rule the user asks an agent to satisfy.

Example:

```text
Deliver the requested research artifact.
Required evidence:
  PaymentReceiptEnvelope
  WorkDeliveryEnvelope
  AcceptanceEnvelope
  FlowPulseReceiptEnvelope
Bond:
  25.00 units
```

The card is hashable and shareable without exposing private fields such as the raw user ID or private obligation ID.

## Layer 2: FlowBond

FlowBond is the bond posted against the PolicyCard.

If the agent closes the obligation with the required evidence, the bond releases back to the agent.

If payment happened but delivery, acceptance, or the correct obligation link is missing, the bond pays the user.

This is not a reputation score. It is a narrow warranty on a specific action.

## Layer 3: FlowPulse

The FlowPulse is the memory artifact.

It carries:

- policy hash;
- agent ID;
- obligation hash;
- evidence types;
- pass/fail result;
- violation list;
- outcome hash.

The action itself is not the memory. The receipt trail is the proof envelope. The FlowPulse is the memory artifact.

## Layer 4: PulsePass

PulsePass is the user's private receipt passport.

It stores FlowPulse receipts locally or in an encrypted vault.

The user can later prove scoped facts without exposing the full history.

Example scoped proofs:

```text
I have completed at least one warranted agent action.
I have a failed warranty receipt.
I have a FlowPulse receipt from this agent.
```

The proof reveals a predicate, threshold, result, and vault commitment. It hides the raw receipts, raw user ID, exact action history, and private obligation IDs.

## Why Users Care

Users get recourse.

Users can choose agents who put money behind promises.

Users privately carry proof of safe completed actions into other agents or apps.

## Why Developers Care

Small agent developers can compete with larger brands by bonding specific outcomes.

Apps can request scoped proofs instead of scraping wallet histories.

Developers can emit useful FlowPulse memories that become portable trust assets.

## Why This Is Different

Wallets prove a key can act.

Payments prove money moved.

Agent identities prove who an agent claims to be.

Logs prove an event happened.

FlowMemory asks whether the promised action produced the required memory receipt and whether the user has a portable proof of that outcome.

## Local Demos

```powershell
python -m flowmemory_compiler.cli policycard-demo --pretty
python -m flowmemory_compiler.cli flowbond-demo --pretty
python -m flowmemory_compiler.cli pulsepass-demo --pretty
```

Expected result:

```text
PolicyCard: portable, hashable, bondable promise
FlowBond: completed promise releases bond; failed promise pays user
PulsePass: scoped proofs reveal only predicates, not raw history
```

## Non-Claims

This v0 does not claim:

- production adjudication;
- custody;
- fund protection;
- work-quality proof;
- semantic truth;
- full privacy;
- zero-knowledge privacy;
- live Base deployment;
- production verifier infrastructure.

The claim is narrower:

```text
Specific agent promises can be turned into hashable PolicyCards, settled into FlowPulse-style receipts, and carried privately through PulsePass scoped proofs.
```

