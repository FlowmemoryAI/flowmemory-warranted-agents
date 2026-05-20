# Production Gate Checklist

This checklist is intentionally stricter than the launch checklist.

The current repo should pass local launch gates and fail production gates until external systems are integrated and reviewed.

Run:

```powershell
python -m flowmemory_compiler.cli production-readiness --pretty
```

Current expected result:

```text
localArchitectureReady: True
productionReady:        False
releaseMode:            LOCAL_ARCHITECTURE_READY_ONLY
```

## Blocking Production Gates

- real wallet adapter;
- real payment or bond rail;
- persistent receipt store;
- reader/verifier service;
- key management and secret rotation;
- observability and alerting;
- incident response runbook;
- security review or audit;
- load and replay testing;
- privacy backend selected.

## Candidate Release Rule

A production release candidate requires:

```text
launch packet passes
production readiness gates pass
claim gate passes
CI passes
external security review completed
```

## Non-Claims

Until every gate is satisfied, do not claim production custody, wallet enforcement, production settlement, production private compute, security audit completion, or production verifier infrastructure.
