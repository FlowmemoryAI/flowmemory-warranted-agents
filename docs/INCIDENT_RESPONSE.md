# Incident Response

This document defines response paths for FlowMemory Warranted Agents as a production candidate.

It does not claim production deployment.

## Severity Classes

### SEV-1: Public Safety Or Funds-Risk Claim Drift

Examples:

- public copy must not imply custody or fund protection;
- public copy must not imply production settlement;
- public copy must not imply production verifier readiness;
- release notes must not imply zero-knowledge privacy in v0.

Response:

1. Stop publication.
2. Run claim gate.
3. Correct public copy.
4. Publish correction if the claim was public.
5. Re-run claim gate and CI.

### SEV-2: Adapter Evidence Failure

Examples:

- adapter emits malformed evidence;
- adapter passes a success path without required envelopes;
- duplicate idempotency key appears;
- runtime reaches an invalid state transition.

Response:

1. Disable adapter discovery.
2. Preserve runtime transcript.
3. Run adapter conformance.
4. Add regression fixture.
5. Re-run launch packet.

### SEV-3: Readiness Gate Failure

Examples:

- launch packet fails;
- claim gate fails;
- production readiness packet reports unexpected status;
- CI fails after release candidate.

Response:

1. Freeze release.
2. Inspect failing gate.
3. Patch code, docs, or claim copy.
4. Re-run all readiness commands.

## Compromised Signer Or Secret

The local framework should not hold production signing keys.

If a future integration introduces keys:

1. Rotate affected key immediately.
2. Disable affected adapter.
3. Invalidate pending proposals tied to that signer.
4. Publish incident note if public claims or user evidence are affected.

## False Evidence Handling

If evidence is discovered to be false or malformed:

1. Mark the evidence envelope invalid.
2. Recompute settlement.
3. Preserve the original transcript.
4. Add a regression test.
5. Update production readiness gate if the failure came from an external dependency.

## Disclosure Template

```text
We identified an issue in [component].
Affected scope: [local demo / adapter / evidence / public copy].
Production funds at risk: not claimed by this package.
Action taken: [disabled / corrected / patched / re-run].
Current status: [blocked / restored].
Evidence: [packet hash / CI run / release transcript].
```

## Non-Claims

This incident response plan does not claim custody, wallet enforcement, production settlement, production private compute, security audit completion, or production verifier infrastructure.
