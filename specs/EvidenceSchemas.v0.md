# Evidence Schemas v0

## Purpose

Define the local evidence envelope shapes used by FlowMemory Warranted Agents.

Evidence names are not enough. Each envelope type carries required fields.

## Envelopes

### `PaymentReceiptEnvelope`

Purpose:

```text
Proves a payment-like obligation event was observed by the local model.
```

Required fields:

- `receiptStatus`: string, must equal `settled`.

### `WorkDeliveryEnvelope`

Purpose:

```text
Binds the claimed work delivery to a content commitment.
```

Required fields:

- `artifactHash`: string, must begin with `sha256:`.

### `AcceptanceEnvelope`

Purpose:

```text
Records that the user-side acceptance condition closed.
```

Required fields:

- `accepted`: boolean, must equal `true`.

### `FlowPulseReceiptEnvelope`

Purpose:

```text
Binds the action to a FlowPulse-style memory receipt.
```

Required fields:

- `pulseObserved`: boolean, must equal `true`.

## Boundary

These schemas are local field checks. They do not claim semantic truth, work-quality proof, external verification, production private compute, or production verifier infrastructure.
