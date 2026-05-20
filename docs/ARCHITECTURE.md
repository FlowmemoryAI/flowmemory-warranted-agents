# FlowCompiler Architecture

FlowCompiler is a future FlowMemory package. It should not live inside the Uniswap v4 hook repo.

The Uniswap repo proves the first public boundary:

```text
afterSwap -> FlowPulse -> transaction receipt -> reader metadata -> FMM-0 checks
```

FlowCompiler generalizes the same idea to autonomous agents:

```text
agent plan -> required evidence envelopes -> future trace -> forbidden cores -> repair
```

## Core Thesis

A valid action surface is not a valid machine history.

Wallet signatures, x402 payment receipts, passing test logs, compute-cache fingerprints, and transaction receipts can all look locally valid. FlowCompiler checks a different property: whether the claimed history is admissible under the evidence envelopes the plan required.

## V0 Boundary

V0 is local and deterministic.

It does not enforce wallets, settle payments, run agents, prove semantic truth, prove code correctness, or verify production chains. It demonstrates that ordinary rails can accept an action surface while FlowCompiler rejects the impossible history behind it.

The compiler claim depends on one concrete behavior:

```text
FlowCompiler derives required envelopes from plans; it does not merely inspect logs after the fact.
```

Run the derivation view:

```powershell
python -m flowmemory_compiler.cli compile --plan examples/plans/coding_tests_passed_plan.json --pretty
```

Capture one local command envelope:

```powershell
python -m flowmemory_compiler.cli capture-command --step test-1 --tree-hash sha256:tree-after -- python -c "print('ok')"
```

The capture helper emits command and output hashes. It does not claim production provenance or code correctness.

## Passes

1. `SurfacePass`: maps plan steps to action surfaces.
2. `EnvelopeRequirementPass`: derives required evidence envelopes.
3. `HappensBeforePass`: rejects impossible ordering.
4. `EnvelopeBindingPass`: checks envelopes bind to the right state.
5. `ClaimAdmissibilityPass`: requires final claims to have evidence.
6. `ForbiddenCorePass`: extracts one deterministic minimal failing core.
7. `RepairPass`: returns a concrete repair or downgrade path.

## Category Cases

The v0 demo includes 11 futures:

- 3 valid futures accepted;
- 8 impossible futures rejected;
- 0 escaped impossible histories.

The most important commerce case is `payment_receipt_without_discharge`: payment settlement can be observed while the obligation remains unclosed because no `DischargeEnvelope` exists.

## Strong Line

FlowCompiler is the history compiler for autonomous agents: it turns proposed actions into required proof envelopes and rejects futures that cannot become legal machine histories.
