# PulseRouter Architecture

PulseRouter is the first buildable slice of outcome-settled AI.

It routes model/provider work by expected successful outcome, not raw inference
price.

## Architecture

```text
PolicyCard-like OutcomePolicy
  -> ProviderQuote[]
  -> RouteScore[]
  -> selected provider
  -> ComputePulse
  -> ToolCallPulse
  -> ActionPulse
  -> reader-derived FlowPulseLink
  -> OutcomePulse
  -> PulsePass predicate
```

## Local Module

Implementation:

```text
flowmemory_compiler/outcome_router.py
```

Commands:

```powershell
python -m flowmemory_compiler.cli pulserouter-demo --pretty
python -m flowmemory_compiler.cli pulserouter-adversary --pretty
```

Tests:

```powershell
python -m unittest
```

## Scoring

The local route score is:

```text
expected value
- quoted provider price
- latency penalty
- privacy penalty
- failure penalty
+ bond bonus
```

Ineligible routes are penalized. A route can be blocked for:

- missing bond coverage;
- failed canary;
- invalid output schema;
- privacy below policy;
- retained prompt on a private route;
- task-class mismatch;
- latency above policy.

## Demo Outcome

The demo compares three routes:

| Route | Raw price | Result |
| --- | ---: | --- |
| cheap unbonded provider | 1 unit | blocked for no bond, failed canary, privacy below policy |
| private bonded provider | 4 units | selected |
| frontier unbonded provider | 12 units | blocked for no bond and privacy below policy |

The selected route emits:

- `ComputePulse`;
- `ToolCallPulse`;
- `ActionPulse`;
- reader-derived `FlowPulseLink`;
- `OutcomePulse`.

The user earns a portable memory predicate:

```text
has_private_bonded_successful_defi_action
```

## Adversarial Suite

The local adversary suite currently catches 26 failure modes:

- missing compute pulses;
- selected unknown provider;
- selected non-highest route;
- selected unbonded route;
- failed canary;
- invalid output schema;
- privacy below policy;
- private route retained prompt;
- task-class mismatch;
- latency above policy;
- missing x402 payment hash;
- action parent drift;
- spend above policy;
- slippage above policy;
- FlowPulse/action mismatch;
- FlowPulse source not reader-derived;
- missing txHash;
- commitment mismatch;
- outcome/compute mismatch;
- wrong pass settlement;
- failed outcome paid provider;
- effective-cost mismatch.
- negative route metric;
- action policy hash mismatch;
- raw model content stored in a pulse;
- unconfirmed FlowPulse evidence.

## Production Path

The next production-candidate layers are:

1. OpenAI-compatible proxy endpoint.
2. Real provider adapters.
3. MCP server tools.
4. Reader/verifier service for FlowPulse evidence.
5. Bond payment rail, without claiming production escrow or custody.
6. PulseVault for encrypted local user memory.
7. Dashboard for route P&L and cost per successful outcome.

## Non-Claims

PulseRouter local proof does not claim production provider routing, wallet
execution, custody, fund protection, x402 replacement, production settlement,
full privacy, zero-knowledge privacy, TEE attestation, model correctness, or
profit guarantee.
