# Evidence Schema

FlowMemory Warranted Agents treats evidence as named local contracts, not arbitrary labels.

## Why This Exists

An agent should not be able to say:

```text
trust me, I delivered
```

It should have to produce an envelope whose fields match the promised evidence path.

## Local Envelope Specs

The current local schema defines:

- `PaymentReceiptEnvelope` with `receiptStatus = settled`;
- `WorkDeliveryEnvelope` with `artifactHash` beginning with `sha256:`;
- `AcceptanceEnvelope` with `accepted = true`;
- `FlowPulseReceiptEnvelope` with `pulseObserved = true`.

## Demo

```powershell
python -m flowmemory_compiler.cli evidence-schema --pretty
```

Expected shape:

```text
FlowMemory Evidence Schema

PaymentReceiptEnvelope
  - receiptStatus: str, required=settled

WorkDeliveryEnvelope
  - artifactHash: str, prefix=sha256:
```

## Boundary

The evidence schema is a local field check. It does not claim semantic truth, work-quality proof, external verification, production private compute, or production verifier infrastructure.

The v0 claim is:

```text
Evidence names must carry the fields the warranted path requires.
```
