# Outcome-Settled AI

Outcome-settled AI is the FlowMemory category for agents and model providers
paid by receipt-backed successful work, not raw token volume.

The market already has cheap inference, private model access, autonomous agent
loops, payment rails, and identity rails.

The missing layer is the outcome layer:

```text
Which intelligence should an agent trust with money?
```

FlowMemory answers with pulses, policies, bonds, and portable user memory.

## Category Claim

FlowMemory makes AI work receipt-native: model calls, tool calls, proposed
actions, on-chain execution, and outcome settlement become one inspectable memory
trail.

PulsePods package that trail into a pod-level product primitive: a memory-native
compute pod that chooses routes by successful FlowPulse outcomes instead of raw
token price.

## PulseMesh

```text
User Policy
  -> Provider Route
  -> ComputePulse
  -> ToolCallPulse
  -> ActionPulse
  -> FlowPulse evidence
  -> OutcomePulse
  -> FlowBond settlement
  -> PulsePass scoped proof
```

## PulsePods

PulsePods turn PulseMesh into a launchable agent pod shape:

```text
PulsePodManifest
  -> ProviderPromise
  -> PulseRouter route
  -> FlowPulse-linked OutcomePulse
  -> PulsePass scoped claim
  -> x402-compatible federation offer
```

The market line is:

```text
Pod systems route compute. FlowMemory routes memory-backed outcomes.
```

The demo command is:

```powershell
python -m flowmemory_compiler.cli pulsepod-demo --pretty
python -m flowmemory_compiler.cli pulsepod-adversary --pretty
```

The important shift is economic:

```text
The cheapest model is not the cheapest successful route.
```

PulseRouter does not ask only which provider has the lowest token price. It asks
which provider has the highest expected successful outcome under the user's
policy.

## Incentive Loop

| Participant | What they get |
| --- | --- |
| User | Private portable proof that a bonded, policy-safe agent route produced a successful action. |
| Developer | A local harness for proving their agent is warrantable before asking users to trust it. |
| Provider | Better routing when its compute reliably produces successful downstream outcomes. |
| Agent builder | Higher spend limits and better trust if the agent leaves clean receipts. |
| Protocol | Memory of which agent/provider routes actually created valid protocol actions. |

## Why It Is Different

Cheap inference markets optimize for raw supply.

FlowMemory optimizes for useful inference:

- did the route satisfy the user policy;
- did the route meet privacy and canary requirements;
- did the provider have bond coverage;
- did the proposed action stay inside spend and slippage limits;
- did reader-derived FlowPulse evidence link the action to the proof envelope;
- did the final outcome settle correctly.

That is the difference between buying tokens and buying useful agent work.

## What Is Local Today

The launch MVP is a deterministic local proof:

- `python -m flowmemory_compiler.cli pulserouter-demo --pretty`
- `python -m flowmemory_compiler.cli pulserouter-adversary --pretty`

It emits local JSON pulses, deterministic hashes, route scores, an outcome
pulse, and an adversarial validation suite.

## What Is Simulated Today

- provider APIs;
- production x402 payment;
- wallet signing;
- future bond payment rail;
- real Uniswap execution;
- production reader/verifier service.

The simulated parts are explicit. The local proof is still useful because it
locks the architecture, data model, incentives, validation rules, and launch
claim before production integrations are added.

## What Not To Claim

Do not claim production settlement, custody, wallet enforcement, x402
replacement, full privacy, zero-knowledge privacy, TEE attestation, model
correctness, guaranteed profit, or live provider marketplace status from this
local package.
