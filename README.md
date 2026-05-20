# FlowMemory Warranted Agents

Generic agents make claims. FlowMemory agents can leave warranted receipts.

FlowMemory Warranted Agents is a local public proof for a new agent primitive:

```text
AgentManifest -> WorkRequest -> PolicyCard -> AgentProposal -> FlowBond -> FlowPulse -> PulsePass -> ScopedProof
```

The user defines the promise. The agent bonds the promise. The action emits receipt-backed memory. The user privately carries proof of what happened.

This is not a generic agent marketplace, RAG memory layer, wallet, x402 replacement, tracing stack, or production verifier.

It is a buildable proof for a narrower and more marketable claim:

```text
Specific agent promises can become portable warranties backed by FlowPulse memory.
```

## Why This Exists

Most AI-agent infrastructure answers local questions:

- can the wallet sign;
- did the payment settle;
- did the tool call run;
- did the transaction land;
- did a log exist.

FlowMemory asks the product question users actually understand:

```text
If the agent breaks the promise, what pays me back?
```

FlowBond gives the agent money on the line.

PulsePass gives the user portable private proof.

PolicyCards let the user's rules travel between agents.

## Product Stack

### AgentManifest

An agent declares what it can warrant:

- capabilities;
- supported evidence;
- maximum bond;
- privacy modes;
- settlement modes.

This is not a normal profile or reputation score. It is a machine-readable warranty surface.

### WorkRequest

The user declares what outcome they want and what evidence must close the obligation.

The request can be shared as a hashable public view while keeping private user and obligation fields hidden.

### PolicyCard

A portable user rule that an agent can bond against.

Example:

```text
Deliver the requested research artifact.
Required evidence:
  PaymentReceiptEnvelope
  WorkDeliveryEnvelope
  AcceptanceEnvelope
  FlowPulseReceiptEnvelope
Bond:
  25.00 units
```

### FlowBond

A bond posted against the PolicyCard.

If the agent closes the obligation with the required evidence, the bond releases back to the agent.

If payment happened but delivery, acceptance, or the correct obligation link is missing, the bond pays the user.

### FlowPulse

The receipt-backed memory artifact.

The action itself is not the memory. The receipt trail is the proof envelope. The FlowPulse is the memory artifact.

### PulsePass

The user's private receipt passport.

PulsePass stores receipts and exposes scoped proofs like:

```text
I completed at least one warranted agent action.
I have a failed warranty receipt.
I have FlowPulse memory from this agent.
```

It does not expose the raw receipt history.

### FlowCompiler

FlowCompiler is the conformance engine underneath the stack. It turns proposed actions into required evidence envelopes and rejects futures that cannot become legal machine histories.

## Demos

Run the warranted-agent stack:

```powershell
python -m flowmemory_compiler.cli agent-framework-demo --pretty
python -m flowmemory_compiler.cli policycard-demo --pretty
python -m flowmemory_compiler.cli flowbond-demo --pretty
python -m flowmemory_compiler.cli pulsepass-demo --pretty
python -m flowmemory_compiler.cli bond-ledger-demo --pretty
python -m flowmemory_compiler.cli private-compute-demo --pretty
python -m flowmemory_compiler.cli release-transcript --pretty
```

Expected shape:

```text
AgentFramework:
  manifest, request, policy, proposal, settlement, PulsePass, scoped proofs

PolicyCard:
  portable, hashable, bondable promise

FlowBond:
  warranted_work_completed     PASSED RELEASE_BOND_TO_AGENT
  payment_without_delivery     FAILED PAY_BOND_TO_USER
  orphan_spend                 FAILED PAY_BOND_TO_USER

PulsePass:
  scoped proofs reveal predicates, not raw history

BondLedger:
  local accounting releases one warranty to the agent and pays one warranty to the user

PrivateCompute:
  scoped predicates over PulsePass without exposing raw receipts

ReleaseTranscript:
  one canonical offline object that summarizes the full framework
```

Run the conformance engine:

FlowCompiler compiles an `AgentPlan` into a `FlowProgram`, then checks a `FutureTrace` against the proof envelopes that the plan requires.

It rejects traces with:

- missing required envelopes;
- stale memory heads;
- mismatched payment obligations;
- tests that passed on the wrong tree;
- compute reuse with invalid memory lineage;
- Uniswap swap receipts without a FlowPulse receipt envelope;
- session-key actions that ignore an AxiomPatch downgrade;
- final verification claims without verification evidence.

Compile a plan into derived evidence requirements:

```powershell
python -m flowmemory_compiler.cli compile --plan examples/plans/coding_tests_passed_plan.json --pretty
```

Run the bundled future-trace conformance cases:

```powershell
python -m flowmemory_compiler.cli demo --pretty
```

Capture one real local command as a `TestRunEnvelope`:

```powershell
python -m flowmemory_compiler.cli capture-command --step test-1 --tree-hash sha256:tree-after -- python -c "print('ok')"
```

Run the market-facing FlowBond R&D demo:

```powershell
python -m flowmemory_compiler.cli flowbond-demo --pretty
```

Expected shape:

```text
FlowCompiler v0

Valid futures:
  FC-OK-001  valid_coding_patch_test_close              ACCEPTED
  FC-OK-002  valid_x402_obligation_discharge            ACCEPTED
  FC-OK-003  valid_compute_reuse_discharge              ACCEPTED

Impossible futures ordinary rails would accept:
  FC-BAD-001 tests_passed_on_wrong_tree                 REJECTED tests_passed_on_wrong_tree
  ...

Summary:
  futures checked: 11
  valid futures accepted: 3/3
  impossible futures rejected: 8/8
  escaped impossible futures: 0
```

## Non-Claims

This v0 does not claim:

- custody;
- wallet enforcement;
- x402 replacement;
- fund protection;
- code correctness;
- work-quality proof;
- semantic truth;
- model correctness;
- GPU acceleration;
- live Base deployment;
- full privacy;
- zero-knowledge privacy;
- production bond adjudication;
- production verifier readiness.

The local `capture-command` helper records command exit code and output hashes. It still does not prove code correctness, semantic truth, or production provenance.

## Positioning Lines

```text
Generic agents make claims. FlowMemory agents can leave warranted receipts.
```

```text
Agents with money on the line.
```

```text
The user owns the rule. The agent bonds the promise. The FlowPulse carries the memory.
```

```text
Actions can look valid to ordinary rails while the machine history behind them is impossible.
```
