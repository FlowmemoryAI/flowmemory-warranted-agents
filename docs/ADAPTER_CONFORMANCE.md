# Adapter Conformance

The conformance harness checks whether an adapter satisfies the warranted-agent contract.

Run:

```powershell
python -m flowmemory_compiler.cli adapter-conformance-demo --pretty
```

The local demo checks:

- manifest supports required evidence;
- manifest supports requested bond;
- proposal binds the PolicyCard hash;
- proposal bond matches policy bond;
- success path releases the bond;
- success path emits a FlowPulse-style pulse;
- failure path pays the user from the bond in the local model;
- failure path records `payment_without_delivery`.

## Why This Matters

The adapter contract is where future real agents plug into FlowMemory.

The conformance harness gives that boundary teeth:

```text
Do not just say the agent supports warranties. Check the adapter.
```

## Boundary

This is not an external agent certification, security audit, custody system, production verifier, or work-quality proof.

It is a local launch harness for checking that an adapter follows the warranted-agent protocol shape.
