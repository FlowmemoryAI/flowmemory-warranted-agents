# Runtime State Machine v0

## Purpose

Define the local deterministic state contract for a FlowMemory warranted-agent action.

## States

- `INITIAL`
- `MANIFEST_LOADED`
- `POLICY_QUOTED`
- `BOND_LOCKED`
- `ACTION_EXECUTED`
- `FLOWBOND_SETTLED`
- `PRIVATE_PROOF_READY`
- `WARRANTY_RELEASED`
- `USER_PAID_FROM_BOND`

## Terminal States

- `WARRANTY_RELEASED`
- `USER_PAID_FROM_BOND`

## Allowed Transitions

| From | To |
| --- | --- |
| `INITIAL` | `MANIFEST_LOADED` |
| `MANIFEST_LOADED` | `POLICY_QUOTED` |
| `POLICY_QUOTED` | `BOND_LOCKED` |
| `BOND_LOCKED` | `ACTION_EXECUTED` |
| `ACTION_EXECUTED` | `FLOWBOND_SETTLED` |
| `FLOWBOND_SETTLED` | `PRIVATE_PROOF_READY` |
| `PRIVATE_PROOF_READY` | `WARRANTY_RELEASED` |
| `PRIVATE_PROOF_READY` | `USER_PAID_FROM_BOND` |

## Transition Fields

Each transition includes:

- `fromState`
- `toState`
- `phase`
- `status`
- `idempotencyKey`
- `fields`
- `transitionHash`

## Rejection Rules

The local state machine rejects:

- transitions not listed above;
- duplicate idempotency keys;
- transitions after a terminal state.

## Boundary

This spec does not define wallet execution, custody, distributed consensus, production settlement, or production verifier infrastructure.
