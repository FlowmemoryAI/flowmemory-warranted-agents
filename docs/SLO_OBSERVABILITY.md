# SLO And Observability

Production readiness requires observable runtime behavior.

This repo defines the telemetry model but does not claim a production telemetry deployment.

## Core Metrics

| Metric | Purpose |
| --- | --- |
| `claim_gate_pass_rate` | Detect public copy drift. |
| `adapter_conformance_pass_rate` | Detect adapter contract regressions. |
| `evidence_rejection_rate` | Track malformed, missing, or mismatched evidence. |
| `invalid_transition_count` | Detect runtime state-machine violations. |
| `duplicate_idempotency_key_count` | Detect replay or repeated transition submissions. |
| `warranty_release_count` | Count successful warranty closures. |
| `user_paid_from_bond_count` | Count failed warranty outcomes in the local model. |
| `production_gate_blocking_count` | Track remaining production blockers. |
| `release_transcript_age_seconds` | Detect stale public release evidence. |

## Suggested SLOs For Production Candidate

- claim gate: 100% pass before public release;
- adapter conformance: 100% pass for enabled adapters;
- invalid transitions: 0 accepted;
- duplicate idempotency keys: 0 accepted;
- release transcript: regenerated for every release candidate;
- incident response: SEV-1 public-claim correction started within 1 hour.

## Alert Conditions

Alert when:

- claim gate fails;
- production readiness status changes unexpectedly;
- adapter conformance fails;
- evidence rejection rate spikes;
- duplicate idempotency keys appear;
- release transcript is stale before public publication.

## Non-Claims

This document does not claim production observability is deployed. It defines the metrics required before a production claim is supportable.
