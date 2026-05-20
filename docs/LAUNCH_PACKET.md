# Launch Packet

The launch packet is the single public readiness object for FlowMemory Warranted Agents.

Run:

```powershell
python -m flowmemory_compiler.cli launch-packet --pretty
```

It summarizes:

- package version;
- release transcript hash;
- packet hash;
- claim gate status;
- adapter conformance status;
- runtime success/failure coverage;
- bundled impossible-history rejection status;
- PulseRouter outcome-routing validation;
- PulseRouter adversarial validation;
- PulsePods memory-native pod validation;
- PulsePods adversarial validation;
- reviewer commands.

Expected shape:

```text
FlowMemory Warranted Agents Launch Packet

readiness:              PASSED

Checks:
  claim_gate_passed                                      PASS
  adapter_conformance_passed                             PASS
  runtime_has_success_and_failure_paths                  PASS
  flowcompiler_rejects_all_bundled_impossible_histories  PASS
  pulserouter_demo_has_no_validation_faults              PASS
  pulserouter_adversary_suite_passed                     PASS
  pulsepod_demo_has_no_validation_faults                 PASS
  pulsepod_adversary_suite_passed                        PASS
```

## Why This Matters

The launch packet gives the public repo one compact answer to:

```text
What should I run first, and is the local package internally consistent?
```

## Boundary

The launch packet is local readiness evidence. It does not claim custody, wallet enforcement, production settlement, production verifier infrastructure, semantic truth, zero-knowledge privacy, or work-quality proof.
