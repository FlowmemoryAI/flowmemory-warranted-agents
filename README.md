# FlowMemory Compiler

FlowCompiler is the history compiler for autonomous agents: it turns proposed actions into required evidence envelopes and rejects futures that cannot become legal machine histories.

A valid action surface is not a valid machine history.

This local v0 package is not a wallet, payment rail, tracing system, RAG memory store, workflow engine, or production verifier. It is a deterministic conformance proof for a narrower claim:

```text
Actions can look valid to ordinary rails while the machine history behind them is impossible.
```

## What It Proves

FlowCompiler compiles an `AgentPlan` into a `FlowProgram`, then checks a `FutureTrace` against the proof envelopes that the plan requires.

It rejects traces with:

- missing required envelopes;
- stale memory heads;
- mismatched payment obligations;
- tests that passed on the wrong tree;
- compute reuse with invalid memory lineage;
- Uniswap swap receipts without a FlowPulse receipt envelope;
- session-key actions that ignore an AxiomPatch downgrade;
- final verification claims without verification evidence.

## Demo

Compile a plan into derived evidence requirements:

```powershell
python -m flowmemory_compiler.cli compile --plan examples/plans/coding_tests_passed_plan.json --pretty
```

Run the bundled future-trace conformance cases:

```powershell
python -m flowmemory_compiler.cli demo --pretty
```

Capture one real local command as a `TestRunEnvelope`:

```powershell
python -m flowmemory_compiler.cli capture-command --step test-1 --tree-hash sha256:tree-after -- python -c "print('ok')"
```

Expected shape:

```text
FlowCompiler v0

Valid futures:
  FC-OK-001  valid_coding_patch_test_close              ACCEPTED
  FC-OK-002  valid_x402_obligation_discharge            ACCEPTED
  FC-OK-003  valid_compute_reuse_discharge              ACCEPTED

Impossible futures ordinary rails would accept:
  FC-BAD-001 tests_passed_on_wrong_tree                 REJECTED tests_passed_on_wrong_tree
  ...

Summary:
  futures checked: 11
  valid futures accepted: 3/3
  impossible futures rejected: 8/8
  escaped impossible futures: 0
```

## Non-Claims

FlowCompiler v0 does not claim:

- custody;
- wallet enforcement;
- x402 replacement;
- fund protection;
- code correctness;
- work quality;
- semantic truth;
- model correctness;
- GPU acceleration;
- live Base deployment;
- production verifier readiness.

The local `capture-command` helper records command exit code and output hashes. It still does not prove code correctness, semantic truth, or production provenance.

## Positioning

Wallets can sign. Payments can settle. Tests can run.

FlowCompiler asks whether the resulting history is admissible under declared evidence envelopes.
