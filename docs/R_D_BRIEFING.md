# FlowCompiler R&D Briefing

## Current Status

FlowCompiler is a separate local R&D package at:

```text
E:\FlowMemory\flowmemory-compiler
```

It is intentionally outside the Uniswap v4 hook launch repo.

The Uniswap repo remains the public launch package for:

```text
afterSwap -> FlowPulse -> transaction proof envelope -> reader metadata -> local FMM-0 conformance
```

FlowCompiler is the next architecture track:

```text
agent plan -> derived evidence requirements -> future trace -> forbidden core -> repair
```

## Core Claim

A valid action surface is not a valid machine history.

Wallets can sign. Payments can settle. Tests can run. Transactions can land.

FlowCompiler asks whether the claimed history is admissible under the evidence envelopes the plan required.

## Why This Is Different

FlowCompiler is not a log viewer, tracer, RAG memory layer, workflow engine, wallet, x402 replacement, policy engine, or agent framework.

Those systems can answer local questions:

- did a command run;
- did a signature validate;
- did a payment settle;
- did a trace emit;
- did a transaction receipt exist;
- did a workflow step execute.

FlowCompiler asks a cross-boundary question:

```text
Can these observed envelopes legally support the final machine history being claimed?
```

That is the useful novelty.

## What GPT Red-Team Identified

The weakest point in the first prototype was the word `compiler`.

A checker can reject hand-authored bad traces. A compiler must derive required evidence from the plan before checking the trace.

The hardening added:

- a compile view that derives requirements from an `AgentPlan`;
- binding constraints such as `TestRunEnvelope.treeHash == DiffEnvelope.afterTreeHash`;
- a stronger commerce case: `payment_receipt_without_discharge`.

## Current Demo

Compile view:

```powershell
python -m flowmemory_compiler.cli compile --plan examples/plans/coding_tests_passed_plan.json --pretty
```

Conformance demo:

```powershell
python -m flowmemory_compiler.cli demo --pretty
```

Current result:

```text
futures checked: 11
valid futures accepted: 3/3
impossible futures rejected: 8/8
escaped impossible futures: 0
```

## Most Important Cases

### tests_passed_on_wrong_tree

Ordinary surface:

```text
test command ran
exit code 0
```

FlowCompiler rejects:

```text
TestRunEnvelope.treeHash != DiffEnvelope.afterTreeHash
```

### payment_receipt_without_discharge

Ordinary surface:

```text
payment requirement satisfied
payment receipt observed
```

FlowCompiler rejects:

```text
PaymentReceiptEnvelope present != obligation_closed
DischargeEnvelope missing
```

### swap_receipt_without_flowpulse

Ordinary surface:

```text
transaction receipt observed
swap succeeded
```

FlowCompiler rejects:

```text
swap receipt != FlowPulse memory artifact
FlowPulseReceiptEnvelope missing
```

## Launch-Safe Language

Use:

```text
FlowCompiler is a local deterministic conformance proof for autonomous-agent histories.
```

Use:

```text
FlowCompiler derives required evidence envelopes from agent plans and rejects futures that cannot support the claimed machine history.
```

Use:

```text
A valid action surface is not a valid machine history.
```

## Overclaims To Avoid

Do not claim FlowCompiler:

- enforces wallets;
- protects funds;
- replaces x402;
- verifies semantic truth;
- proves work quality;
- proves code correctness;
- proves model correctness;
- prevents fraud;
- runs on Base;
- is production verifier infrastructure.

## Next Build Step

The next credibility improvement is one real local capture command:

```powershell
python -m flowmemory_compiler.cli capture-command --step test-1 --tree-hash sha256:tree-after -- npm test
```

That command should emit a `TestRunEnvelope` with:

- command;
- exit code;
- tree hash;
- stdout hash;
- stderr hash;
- observed sequence.

This would move FlowCompiler from fixture-only conformance into locally captured evidence without becoming an agent framework.

