# PulsePods v0

PulsePods v0 defines a local memory-native pod primitive for outcome-settled
agent work.

## Primitive

```text
PulsePodManifest
  -> ProviderPromise
  -> PulseRouter route
  -> ComputePulse[]
  -> ActionPulse
  -> FlowPulseLink
  -> OutcomePulse
  -> PulsePassClaim
  -> FederationOffer
```

## Required Evidence

A valid local PulsePod demo must contain:

- `PolicyCard`
- `ComputePulse`
- `ActionPulse`
- `FlowPulseLink`
- `OutcomePulse`
- `PulsePassPredicate`

## Valid Local State

The local PulsePod state is valid when:

- the pod is in `local_demo` mode;
- the routing objective is `cost_per_successful_flowpulse_outcome`;
- raw prompt and raw response logging are disabled in the public pulse path;
- the pod policy hash matches the route policy hash;
- the selected PulseRouter route validates;
- the selected provider has a provider promise with bond coverage;
- the FlowPulse link is reader-derived;
- the OutcomePulse is successful;
- the PulsePass claim reveals a predicate, not raw history;
- the federation offer is x402-compatible by reference;
- demo memory credits are explicitly not money.

## Failure Codes

The adversarial suite must catch at least:

- `pod_id_missing`
- `pulsepod_mode_not_local_demo`
- `pulsepod_policy_hash_mismatch`
- `routing_objective_not_outcome_settled`
- `pulsepod_raw_logging_enabled`
- `route_validation_fault:*`
- `pulsepod_flowpulse_not_reader_derived`
- `pulsepod_outcome_not_successful`
- `provider_promise_provider_mismatch`
- `provider_promise_unbonded`
- `provider_promise_canary_failed`
- `provider_privacy_promise_missing`
- `pulsepod_evidence_set_incomplete`
- `pulsepod_sequence_not_monotonic`
- `federation_payment_rail_not_x402_compatible`
- `federation_overclaims_production`
- `federation_evidence_set_incomplete`
- `pulsepass_reveals_private_fields`
- `pulsepass_source_set_uncommitted`
- `negative_memory_credit`
- `memory_credit_marketed_as_money`
- `raw_model_content_stored`
- `public_claim_overclaim`

## Non-Claims

PulsePods v0 does not claim production settlement, production verifier status,
production private compute, full privacy, zero-knowledge privacy, TEE
attestation, custody, wallet enforcement, fund protection, cheaper inference,
model correctness, or real user earnings.
