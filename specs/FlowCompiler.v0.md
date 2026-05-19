# FlowCompiler v0

## Schemas

### AgentPlan

An `AgentPlan` declares the steps and final claims an autonomous-agent episode expects to make.

Required fields:

- `schema`: `flowmemory.agent_plan.v0`
- `planId`
- `rootfieldId`
- `declaredRootfieldHead`
- `steps`
- `finalClaims`

### FlowProgram

A `FlowProgram` is the compiled envelope requirement set.

Required fields:

- `schema`: `flowmemory.flowprogram.v0`
- `programId`
- `sourcePlanId`
- `rootfieldId`
- `compileStatus`
- `requiredPulses`
- `requiredEnvelopes`
- `requiredPasses`

### EvidenceEnvelope

An `EvidenceEnvelope` is a receipt, diff, command result, or reader-derived fact attached after execution.

Required fields:

- `schema`: `flowmemory.evidence_envelope.v0`
- `envelopeId`
- `envelopeType`
- `stepId`
- `observedSequence`
- `fields`

### FutureTrace

A `FutureTrace` combines the plan, observed envelopes, ordinary rails, current memory head, and expected conformance result.

### ForbiddenCore

A `ForbiddenCore` is a deterministic one-minimal set of atoms that keep a history impossible.

### RepairInstruction

A `RepairInstruction` tells an agent how to repair the trace or downgrade the claim.

## Non-Claims

FlowCompiler v0 is not production verification, custody, wallet enforcement, x402 settlement, code correctness proof, semantic truth proof, model correctness proof, GPU acceleration, or live chain infrastructure.

