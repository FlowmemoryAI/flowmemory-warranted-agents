# Adapter Contract

The adapter is the narrow boundary where a real agent plugs into FlowMemory Warranted Agents.

```text
manifest() -> quote(request) -> execute(policy) -> settle(policy, outcome)
```

## `manifest()`

Returns the agent's warrantable surface.

The manifest must declare:

- agent ID;
- developer ID;
- capabilities;
- supported evidence envelopes;
- maximum bond units;
- privacy modes;
- settlement modes.

The manifest is not a reputation profile. It is the agent's machine-readable warranty surface.

## `quote(request)`

Accepts a `WorkRequest` and returns:

- `PolicyCard`;
- `AgentProposal`.

The adapter must reject the quote if:

- the request requires unsupported evidence;
- the requested bond exceeds the manifest limit;
- the promise type is unsupported.

The quote binds the agent to a policy hash before execution.

## `execute(policy)`

Runs the agent work and returns an `AgentWorkOutcome`.

The outcome must include:

- action ID;
- spend units;
- completion timestamp;
- transaction or receipt reference when available;
- evidence envelopes.

The outcome is not trusted just because the adapter returned it. It must still pass FlowBond settlement and EvidenceSchema checks.

## `settle(policy, outcome)`

Evaluates the outcome against the PolicyCard.

The settlement returns:

- pass/fail;
- violations;
- settlement action;
- FlowPulse-style memory artifact;
- policy hash.

## Idempotency

The runtime wraps adapter output in a state machine with idempotency keys.

Duplicate transition keys are rejected in the local model.

## Boundary

The adapter contract does not claim wallet execution, custody, production settlement, production adjudication, semantic truth, work-quality proof, zero-knowledge privacy, or production verifier infrastructure.

It defines where future real agents plug into warranted receipts.
