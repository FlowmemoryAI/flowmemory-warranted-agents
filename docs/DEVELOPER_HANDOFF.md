# Developer Handoff

This document is for a developer reviewing FlowMemory Warranted Agents as an architecture, not just as a demo.

## One Sentence

FlowMemory Warranted Agents turns an agent promise into a deterministic machine history: manifest, request, policy, proposal, registry match, runtime phases, evidence schema checks, bond settlement, FlowPulse memory, PulseRouter outcome routing, private receipt proof, and conformance checks.

## Plain English

A normal agent can say:

```text
I can do this.
```

A FlowMemory warranted agent has to say:

```text
Here is the promise.
Here is the evidence I must produce.
Here is the bond behind the promise.
Here is the memory receipt after the action.
Here is a private proof the user can carry later.
Here is why the selected provider was useful, not just cheap.
```

That is the framework.

## Integration Boundary

A real agent integration should implement the adapter:

```text
manifest() -> quote(request) -> execute(policy) -> settle(policy, outcome)
```

### `manifest()`

Returns the agent's warranty surface:

- capabilities;
- supported evidence envelopes;
- maximum bond;
- privacy modes;
- settlement modes.

### `quote(request)`

Negotiates a `PolicyCard` and `AgentProposal`.

The quote must fail if:

- required evidence is unsupported;
- requested bond exceeds the manifest limit;
- promise type is unsupported.

### `execute(policy)`

Runs the actual agent work and returns an `AgentWorkOutcome`.

The outcome is not trusted by itself. It is only input to settlement.

### `settle(policy, outcome)`

Evaluates the evidence against the PolicyCard and emits the FlowBond settlement.

The settlement contains the FlowPulse-style memory artifact for the action.

## Runtime State Machine

The local runtime records:

```text
manifest_loaded
policy_quoted
bond_locked
action_executed
flowbond_settled
private_proof_ready
```

The success path ends in:

```text
WARRANTY_RELEASED
```

The failure path ends in:

```text
USER_PAID_FROM_BOND
```

## What To Inspect First

Code:

- `flowmemory_compiler/agent_framework.py`
- `flowmemory_compiler/agent_adapter.py`
- `flowmemory_compiler/adapter_conformance.py`
- `flowmemory_compiler/agent_registry.py`
- `flowmemory_compiler/agent_runtime.py`
- `flowmemory_compiler/evidence_schema.py`
- `flowmemory_compiler/flowbond.py`
- `flowmemory_compiler/pulsepass.py`
- `flowmemory_compiler/private_compute.py`
- `flowmemory_compiler/outcome_router.py`
- `flowmemory_compiler/claim_gate.py`
- `flowmemory_compiler/production_readiness.py`

Docs:

- `docs/AGENT_FRAMEWORK_ARCHITECTURE.md`
- `docs/ADAPTER_CONFORMANCE.md`
- `docs/AGENT_RUNTIME.md`
- `docs/RUNTIME_STATE_MACHINE.md`
- `docs/AGENT_REGISTRY.md`
- `docs/EVIDENCE_SCHEMA.md`
- `docs/CLAIM_GATE.md`
- `docs/RELEASE_TRANSCRIPT.md`
- `docs/OUTCOME_SETTLED_AI.md`
- `docs/PULSEROUTER_ARCHITECTURE.md`
- `docs/PRODUCTION_READINESS_ARCHITECTURE.md`
- `docs/PRODUCTION_GATE_CHECKLIST.md`
- `docs/OPERATOR_RUNBOOK.md`
- `docs/INCIDENT_RESPONSE.md`
- `docs/SIGNER_CUSTODY_BOUNDARIES.md`

Spec:

- `specs/WarrantedAgentFramework.v0.md`
- `specs/PulseRouter.v0.md`

## Verification Commands

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m flowmemory_compiler.cli agent-registry-demo --pretty
python -m flowmemory_compiler.cli agent-runtime-demo --pretty
python -m flowmemory_compiler.cli evidence-schema --pretty
python -m flowmemory_compiler.cli release-transcript --pretty
python -m flowmemory_compiler.cli pulserouter-demo --pretty
python -m flowmemory_compiler.cli pulserouter-adversary --pretty
python -m flowmemory_compiler.cli claim-gate --pretty
python -m flowmemory_compiler.cli production-readiness --pretty
```

## Strong Claim

```text
Generic agents make claims. FlowMemory agents can leave warranted receipts.
```

## Boundary

This package is local deterministic architecture. It does not claim custody, wallet enforcement, production settlement, production adjudication, full privacy, zero-knowledge proof generation, semantic truth, or work-quality proof.

The point is narrower:

```text
Make the agent promise machine-checkable before, during, and after execution.
```

PulseRouter adds the outcome layer:

```text
Route intelligence by receipt-backed successful outcomes, not raw token price.
```

Production status:

```text
Local architecture ready; production gates block live deployment until external adapters, payment rails, durable evidence, observability, incident response, and security review are complete.
```
