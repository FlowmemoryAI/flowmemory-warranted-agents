# Reviewer Walkthrough

This walkthrough is the shortest path for a technical reviewer.

## 1. Run The Full Test Suite

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Expected:

```text
Ran all tests
OK
```

What this proves:

- bundled valid histories are accepted;
- bundled impossible histories are rejected;
- FlowBond success and failure settlements hold;
- PulsePass hides raw receipt history;
- AgentRegistry matches warrantable agents;
- AgentRuntime records terminal machine histories;
- RuntimeStateMachine rejects invalid transitions and replay keys;
- EvidenceSchema rejects malformed evidence fields;
- ClaimGate passes public copy.

## 2. Inspect The Canonical Launch Object

```powershell
python -m flowmemory_compiler.cli release-transcript --pretty
```

Look for:

```text
AgentRegistry:
  eligibleAgents: 1
  rejectedAgents: 1

AgentRuntime:
  runs:          2
  finalStatuses: WARRANTY_RELEASED, USER_PAID_FROM_BOND

FlowCompiler:
  valid accepted:                 3/3
  impossible histories rejected:  8/8
  escaped impossible histories:   0
```

What this proves:

```text
The repo has one local transcript that ties together discovery, runtime, evidence, settlement, private proof, and impossible-history rejection.
```

## 3. Inspect Runtime Behavior

```powershell
python -m flowmemory_compiler.cli agent-runtime-demo --pretty
```

Look for:

```text
Run: success -> WARRANTY_RELEASED
Run: payment_without_delivery -> USER_PAID_FROM_BOND
```

What this proves:

```text
The same runtime handles both a completed warranty and a failed warranty path.
```

## 4. Inspect Discovery

```powershell
python -m flowmemory_compiler.cli agent-registry-demo --pretty
```

Look for:

```text
FlowMemory Warranted Research Agent ELIGIBLE score=100
Cheap Claim Agent                REJECTED score=29
```

What this proves:

```text
Discovery is based on warrantability, not generic availability.
```

## 5. Inspect Evidence Contracts

```powershell
python -m flowmemory_compiler.cli evidence-schema --pretty
```

What this proves:

```text
Evidence envelopes have required local fields.
```

## 6. Inspect Claim Boundaries

```powershell
python -m flowmemory_compiler.cli claim-gate --pretty
```

Expected:

```text
unguardedOverclaims:  0
status:               PASSED
```

What this proves:

```text
The public copy must not contain unsupported custody, wallet, privacy, semantic-truth, or production-verifier claims.
```

## Bottom Line

The strongest technically bounded claim is:

```text
FlowMemory Warranted Agents is a local deterministic framework for turning agent promises into receipt-bound machine histories with bond-modeled settlement and scoped private proof.
```
