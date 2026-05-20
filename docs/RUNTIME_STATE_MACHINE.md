# Runtime State Machine

The warranted-agent runtime is an explicit state machine.

It is not just a log. It has allowed transitions, terminal states, event hashes, and idempotency keys.

## States

```text
INITIAL
MANIFEST_LOADED
POLICY_QUOTED
BOND_LOCKED
ACTION_EXECUTED
FLOWBOND_SETTLED
PRIVATE_PROOF_READY
WARRANTY_RELEASED
USER_PAID_FROM_BOND
```

Terminal states:

```text
WARRANTY_RELEASED
USER_PAID_FROM_BOND
```

## Allowed Transitions

```text
INITIAL -> MANIFEST_LOADED
MANIFEST_LOADED -> POLICY_QUOTED
POLICY_QUOTED -> BOND_LOCKED
BOND_LOCKED -> ACTION_EXECUTED
ACTION_EXECUTED -> FLOWBOND_SETTLED
FLOWBOND_SETTLED -> PRIVATE_PROOF_READY
PRIVATE_PROOF_READY -> WARRANTY_RELEASED
PRIVATE_PROOF_READY -> USER_PAID_FROM_BOND
```

Any other transition is rejected by the local state machine.

## Replay Boundary

Each transition carries an idempotency key.

A duplicate idempotency key is rejected. This makes the local runtime harder to confuse with repeated phase submissions.

## Why This Matters

Agent systems usually produce messy histories:

```text
claim, payment, tool call, log, maybe a receipt
```

FlowMemory Warranted Agents gives the history a shape:

```text
state, transition, evidence, settlement, memory, proof
```

That shape is what makes the framework inspectable.

## Boundary

The state machine is local and deterministic. It does not claim distributed consensus, wallet execution, custody, production settlement, or production verifier infrastructure.
