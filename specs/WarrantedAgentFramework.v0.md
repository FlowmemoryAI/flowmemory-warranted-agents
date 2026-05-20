# Warranted Agent Framework v0

## Objects

### AgentManifest

Machine-readable warranty surface for an agent.

Required fields:

- `agent_id`
- `developer_id`
- `display_name`
- `capabilities`
- `supported_evidence`
- `max_bond_units`
- `privacy_modes`
- `settlement_modes`

### WorkRequest

User-authored request for a warranted action.

Required fields:

- `request_id`
- `user_id`
- `title`
- `promise_type`
- `obligation_id`
- `required_evidence`
- `max_spend_units`
- `requested_bond_units`
- `expires_at`

### PolicyCard

Negotiated user rule an agent can bond against.

### AgentProposal

Agent's pre-action warranty offer against a PolicyCard.

### FlowBondSettlement

Settlement result after evidence is evaluated.

### PulsePass

User-owned receipt vault and scoped proof surface.

## Valid Local Flow

```text
AgentManifest supports required evidence.
WorkRequest asks for a supported promise.
PolicyCard is derived.
AgentProposal commits bond to policy hash.
Action emits evidence envelopes.
FlowBond settles pass/fail.
FlowPulse-style receipt records outcome.
PulsePass stores receipt.
ScopedProof reveals only a predicate.
```

## Failure Cases

The framework rejects or pays the user when:

- required evidence is missing;
- payment exists but delivery is missing;
- evidence attaches to the wrong obligation;
- acceptance is missing or false;
- action exceeds allowed spend;
- action happens after expiry.

## Non-Claims

This spec does not define custody, live wallet execution, production x402 integration, production arbitration, zero-knowledge proof generation, work-quality verification, semantic truth, or production verifier infrastructure.

