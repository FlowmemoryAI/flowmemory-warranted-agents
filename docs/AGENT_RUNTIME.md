# Agent Runtime

The Agent Runtime is the launch-critical state machine for FlowMemory Warranted Agents.

Generic agent platforms usually stop at:

```text
prompt -> tool call -> payment -> log
```

FlowMemory adds the missing warranty path:

```text
manifest -> quote -> bond -> action -> settlement -> memory -> private proof
```

## Runtime Phases

The local runtime emits a deterministic timeline:

```text
manifest_loaded
policy_quoted
bond_locked
action_executed
flowbond_settled
private_proof_ready
```

Each phase has an event hash. The point is not to host the agent. The point is to make the action history inspectable, reproducible, and rejectable.

## Why This Is Different

Most agent frameworks optimize execution.

FlowMemory makes the promise auditable.

The user does not have to trust a profile page, a chat transcript, or a vague reputation score. The agent either produces the required evidence and gets the bond back, or the user gets paid from the bond in the local model.

## Demo

```powershell
python -m flowmemory_compiler.cli agent-runtime-demo --pretty
```

Expected shape:

```text
Run: success -> WARRANTY_RELEASED
  manifest_loaded
  policy_quoted
  bond_locked
  action_executed
  flowbond_settled
  private_proof_ready

Run: payment_without_delivery -> USER_PAID_FROM_BOND
  manifest_loaded
  policy_quoted
  bond_locked
  action_executed
  flowbond_settled
  private_proof_ready
```

## Boundary

This is a local deterministic runtime model. It does not claim custody, wallet execution, production settlement, production adjudication, zero-knowledge privacy, or work-quality proof.

The v0 claim is narrower and stronger:

```text
FlowMemory can represent an agent promise as a warranted machine history from quote to scoped proof.
```
