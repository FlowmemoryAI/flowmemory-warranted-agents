# Agent Registry

The Agent Registry is not a marketplace profile page.

It is a warranty-eligibility layer.

## Core Question

```text
Can this agent actually quote the user's warranted request?
```

The registry checks:

- required evidence support;
- requested bond amount;
- promise type.

If an agent cannot provide the evidence path or cannot support the requested bond, it is rejected before the user treats the agent as warrantable.

The local registry also emits a `warrantabilityScore`.

That score is not reputation. It is a deterministic fit score for this request:

- evidence support;
- bond capacity.

## Why This Matters

Agent marketplaces can make every agent look available.

FlowMemory needs a stricter surface:

```text
Available is not enough. Warrantable is the standard.
```

That is the category difference.

## Demo

```powershell
python -m flowmemory_compiler.cli agent-registry-demo --pretty
```

Expected shape:

```text
FlowMemory Warranted Agent Registry

Matches:
  FlowMemory Warranted Research Agent ELIGIBLE score=100
    reasons: eligible_for_warranted_quote
  Cheap Claim Agent                 REJECTED score=29
    reasons: missing_required_evidence, bond_request_exceeds_manifest_limit
```

## Boundary

The registry does not claim identity attestation, reputation, wallet enforcement, custody, or production marketplace infrastructure.

It is the local discovery contract for warranted agents:

```text
match by evidence, bond, and promise support.
```
