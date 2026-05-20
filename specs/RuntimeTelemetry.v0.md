# Runtime Telemetry v0

## Purpose

Define telemetry events for production-candidate FlowMemory Warranted Agents.

## Event Types

### `ClaimGateRun`

Fields:

- `filesChecked`
- `guardedRiskMentions`
- `unguardedOverclaims`
- `passed`

### `AdapterConformanceRun`

Fields:

- `adapter`
- `checkCount`
- `passed`

### `RuntimeTransitionObserved`

Fields:

- `runId`
- `fromState`
- `toState`
- `phase`
- `status`
- `transitionHash`
- `idempotencyKey`

### `ProductionReadinessRun`

Fields:

- `localArchitectureReady`
- `productionReady`
- `releaseMode`
- `blockingGateCount`
- `packetHash`

## Non-Claims

This spec defines telemetry shape only. It does not claim production telemetry deployment, production settlement, wallet enforcement, custody, or production verifier infrastructure.
