# Build Test Verify Loop

Use this loop for every FlowMemory warranted-agent and PulseRouter slice.

## Loop

```text
1. Build one narrow primitive.
2. Add the public schema or doc boundary.
3. Add positive tests.
4. Add adversarial tests.
5. Run the local commands.
6. Run the claim gate.
7. Update release transcript and launch packet.
8. Push only after CI-shaped verification passes locally.
```

## Required Commands

```powershell
python -m unittest
python -m flowmemory_compiler.cli pulserouter-demo --pretty
python -m flowmemory_compiler.cli pulserouter-adversary --pretty
python -m flowmemory_compiler.cli release-transcript --pretty
python -m flowmemory_compiler.cli launch-packet --pretty
python -m flowmemory_compiler.cli production-readiness --pretty
python -m flowmemory_compiler.cli claim-gate --pretty
git diff --check
```

## Exit Criteria

A slice is launch-ready when:

- unit tests pass;
- demo command exits zero;
- adversarial suite exits zero;
- release transcript includes the new primitive;
- launch packet readiness is `PASSED`;
- production readiness stays honest about external blockers;
- claim gate reports zero unguarded overclaims;
- no whitespace errors are present.

## PulseRouter-Specific Loop

For the outcome layer:

```text
ProviderQuote -> RouteScore -> ComputePulse -> ToolCallPulse -> ActionPulse -> FlowPulseLink -> OutcomePulse -> adversarial validation
```

Every new provider adapter must prove:

- policy eligibility;
- route score;
- request/response hash;
- privacy tier;
- prompt retention claim;
- canary status;
- output schema status;
- bond coverage;
- x402/payment reference when applicable;
- outcome settlement link.
- no raw prompt or raw response leakage in public pulse records;
- confirmed reader-derived FlowPulse evidence before final settlement claims.

## Non-Claims

This loop does not claim production custody, wallet enforcement, production
settlement, production provider routing, full privacy, zero-knowledge privacy,
TEE attestation, model correctness, semantic truth, or profit guarantee.
