# FlowMemory Agent Framework Architecture

## Core Line

FlowMemory agents should not just act. They should leave warranted receipts.

## Framework Pipeline

```text
AgentManifest
  -> WorkRequest
  -> PolicyCard
  -> AgentProposal
  -> FlowBond
  -> FlowPulse
  -> PulsePass
  -> ScopedProof
```

## Layer 1: AgentManifest

The `AgentManifest` is the agent's warranty surface.

It declares:

- agent ID;
- developer ID;
- capabilities;
- supported evidence envelopes;
- maximum bond;
- privacy modes;
- settlement modes.

This is not a marketplace profile. It is a machine-readable statement of what an agent is willing to bond.

## Layer 2: WorkRequest

The `WorkRequest` is the user's desired outcome.

It declares:

- request ID;
- promise type;
- private obligation ID;
- required evidence;
- maximum spend;
- requested bond;
- expiration.

The public view hides private user and obligation fields while preserving a hashable request.

## Layer 3: PolicyCard

The `PolicyCard` is the negotiated rule.

It is portable, hashable, and bondable.

The PolicyCard is the thing the agent commits to.

## Layer 4: AgentProposal

The `AgentProposal` binds the agent to the PolicyCard.

It includes:

- proposal ID;
- agent ID;
- request ID;
- policy hash;
- bond amount;
- promised evidence.

The proposal is not execution. It is a pre-action warranty offer.

## Layer 5: FlowBond

FlowBond settles the warranty.

If the required evidence closes the obligation, the bond releases to the agent.

If payment happened without delivery, acceptance, or the correct obligation link, the bond pays the user.

## Layer 6: FlowPulse

The FlowPulse is the memory artifact.

It records:

- action ID;
- agent ID;
- policy hash;
- obligation hash;
- evidence types;
- pass/fail;
- violations;
- outcome hash.

The action is not the memory. The FlowPulse is the memory artifact.

## Layer 7: PulsePass

PulsePass is the user's private receipt passport.

It stores receipts and exposes scoped proofs.

The local v0 reveals:

- owner hash;
- vault commitment;
- predicate;
- threshold;
- pass/fail;
- count bucket.

It hides:

- raw receipts;
- raw user ID;
- exact action history;
- private obligation IDs.

## Why This Matters

Wallets prove that a key can act.

Payments prove that money moved.

Logs prove that an event happened.

FlowMemory asks a different question:

```text
Did the agent close the promise it bonded?
```

## Local Demo

```powershell
python -m flowmemory_compiler.cli agent-framework-demo --pretty
```

Expected output shape:

```text
AgentManifest -> WorkRequest -> PolicyCard -> AgentProposal -> FlowBond -> FlowPulse -> PulsePass -> ScopedProof

Settlements:
  action:framework-success   PASSED RELEASE_BOND_TO_AGENT
  action:framework-failure   FAILED PAY_BOND_TO_USER

Scoped proofs:
  has_completed_warranted_action PASS
  has_failed_warranty            PASS
```

## Non-Claims

This framework does not claim:

- custody;
- wallet enforcement;
- live x402 integration;
- production bond adjudication;
- work-quality proof;
- semantic truth;
- full privacy;
- zero-knowledge privacy;
- production verifier infrastructure.

The v0 claim is:

```text
The framework can model a warranted-agent action from manifest to private scoped proof, using deterministic local receipts.
```

