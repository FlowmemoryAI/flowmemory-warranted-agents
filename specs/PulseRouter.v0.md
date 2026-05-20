# PulseRouter.v0

Draft local schema for outcome-settled AI routing.

PulseRouter is the local receipt router for proving cost per successful outcome.

## OutcomePolicy

```json
{
  "schema": "flowmemory.outcome_policy.v0",
  "policyId": "policy:swap-outcome-001",
  "userHash": "sha256:...",
  "actionType": "uniswap_v4_swap",
  "allowedTaskClass": "defi_swap_recommendation",
  "maxSpendUnits": 10000,
  "maxSlippageBps": 50,
  "maxLatencyMs": 4000,
  "minPrivacyTier": "private",
  "requireBondedRoute": true,
  "requireCanaryPass": true,
  "expectedActionValueUnits": 100,
  "userRiskUnits": 80,
  "agentRewardUnits": 25
}
```

## ComputePulse

```json
{
  "schema": "flowmemory.compute_pulse.v0",
  "pulseId": "sha256:...",
  "providerId": "provider:private-bonded",
  "model": "private-action-model",
  "modelHash": "sha256:...",
  "requestHash": "sha256:...",
  "responseHash": "sha256:...",
  "quotedPriceUnits": 4,
  "latencyBucket": "1-3s",
  "privacyTier": "private",
  "promptRetained": false,
  "canaryPassed": true,
  "outputSchemaValid": true,
  "bondCoverageUnits": 500,
  "x402PaymentHash": "sha256:..."
}
```

The raw prompt and raw response do not need to be public. Their hashes are the
portable evidence handles.

## ToolCallPulse

```json
{
  "schema": "flowmemory.tool_call_pulse.v0",
  "pulseId": "sha256:...",
  "parentPulseId": "sha256:compute",
  "toolName": "x402.quote",
  "fieldsHash": "sha256:...",
  "x402PaymentHash": "sha256:..."
}
```

## ActionPulse

```json
{
  "schema": "flowmemory.action_pulse.v0",
  "pulseId": "sha256:...",
  "parentPulseId": "sha256:compute",
  "toolPulseId": "sha256:tool",
  "policyHash": "sha256:...",
  "actionType": "uniswap_v4_swap",
  "actionHash": "sha256:...",
  "spendUnits": 9500,
  "slippageBps": 35
}
```

## FlowPulseLink

```json
{
  "schema": "flowmemory.flowpulse_link.v0",
  "source": "reader_derived",
  "actionPulseId": "sha256:action",
  "rootfieldId": "sha256:...",
  "commitment": "sha256:actionHash",
  "txHash": "0x...",
  "logIndex": 7,
  "finality": "confirmed",
  "flowPulseId": "sha256:..."
}
```

`txHash` and `logIndex` are reader-derived evidence fields. They are not
hook-time fields.

## OutcomePulse

```json
{
  "schema": "flowmemory.outcome_pulse.v0",
  "pulseId": "sha256:...",
  "providerId": "provider:private-bonded",
  "computePulseId": "sha256:compute",
  "actionPulseId": "sha256:action",
  "flowPulseId": "sha256:flowpulse",
  "passed": true,
  "settlement": "PAY_PROVIDER_RELEASE_BOND",
  "providerPaidUnits": 4,
  "agentRewardUnits": 25,
  "effectiveCostPerSuccessfulOutcomeUnits": 29
}
```

## RouteScore

```json
{
  "schema": "flowmemory.route_score.v0",
  "providerId": "provider:private-bonded",
  "eligible": true,
  "reasons": [],
  "expectedValueUnits": 82,
  "failurePenaltyUnits": 14,
  "latencyPenaltyUnits": 7,
  "privacyPenaltyUnits": 0,
  "bondBonusUnits": 20,
  "quotedPriceUnits": 4,
  "scoreUnits": 77
}
```

## Required Validation

A PulseRouter trace is invalid when:

- the selected provider is missing or ineligible;
- a higher eligible route exists;
- the route violates bond, canary, privacy, schema, task, latency, or x402
  requirements;
- the action is not parented to selected compute;
- the action violates spend or slippage policy;
- the FlowPulse link is not reader-derived;
- the FlowPulse commitment does not match the action hash;
- the outcome is not linked to compute, action, and FlowPulse;
- settlement or cost accounting conflicts with the pass/fail status.
- route metrics are negative;
- raw prompt or raw response content is stored in public pulse records;
- FlowPulse evidence is unconfirmed when final settlement is claimed.

## Non-Claims

This draft schema does not claim production provider marketplace status,
production x402 settlement, custody, wallet enforcement, full privacy,
zero-knowledge privacy, TEE attestation, model correctness, or guaranteed profit.
