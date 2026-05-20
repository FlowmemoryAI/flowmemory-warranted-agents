# Operator Runbook

This runbook is for operating the warranted-agent framework as a production candidate.

It does not claim production deployment.

## Daily Checks

Run:

```powershell
python -m unittest
python -m flowmemory_compiler.cli claim-gate --pretty
python -m flowmemory_compiler.cli launch-packet --pretty
python -m flowmemory_compiler.cli production-readiness --pretty
```

Expected current production mode:

```text
LOCAL_ARCHITECTURE_READY_ONLY
```

## Adapter Onboarding

Before accepting a new agent adapter:

1. Read the adapter manifest.
2. Confirm supported evidence envelopes.
3. Confirm maximum bond units.
4. Run adapter conformance checks.
5. Run success and failure runtime paths.
6. Add adapter-specific fixture histories.
7. Re-run claim gate and launch packet.

Required command:

```powershell
python -m flowmemory_compiler.cli adapter-conformance-demo --pretty
```

## Evidence Export

For every release candidate, export:

- release transcript;
- launch packet;
- production readiness packet;
- adapter conformance output;
- claim gate output.

Commands:

```powershell
python -m flowmemory_compiler.cli release-transcript --json
python -m flowmemory_compiler.cli launch-packet --json
python -m flowmemory_compiler.cli production-readiness --json
```

## Emergency Disable

If evidence, adapter, claim, or settlement behavior is wrong:

1. Stop publishing new launch claims.
2. Disable the affected adapter from registry discovery.
3. Mark production readiness as blocked.
4. Preserve logs, transcripts, and packet hashes.
5. Publish a correction if public copy overstated the system.
6. Re-run claim gate after correction.

## Release Regeneration

Before each public release:

```powershell
python -m unittest
python -m flowmemory_compiler.cli release-transcript --pretty
python -m flowmemory_compiler.cli launch-packet --pretty
python -m flowmemory_compiler.cli production-readiness --pretty
```

## Non-Claims

This runbook does not claim custody, wallet enforcement, production settlement, production private compute, security audit completion, or production verifier infrastructure.
