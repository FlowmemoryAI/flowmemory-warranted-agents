# FlowMemory Warranted Agents Release Transcript

The release transcript is the canonical local object for the package.

It summarizes:

- PolicyCard;
- AgentManifest;
- WorkRequest;
- AgentProposal;
- AdapterConformance;
- AgentRegistry;
- AgentRuntime;
- EvidenceSchema;
- FlowBond;
- BondLedger;
- FlowPulse;
- PulsePass;
- PrivateCompute;
- FlowCompiler.

Run:

```powershell
python -m flowmemory_compiler.cli release-transcript --pretty
```

Or JSON:

```powershell
python -m flowmemory_compiler.cli release-transcript --json
```

Expected summary:

```text
FlowBond:
  releasedToAgent: 1
  paidToUser:      2

AdapterConformance:
  passed:     True
  checkCount: 8

AgentRegistry:
  eligibleAgents: 1
  rejectedAgents: 1

AgentRuntime:
  runs:          2
  finalStatuses: WARRANTY_RELEASED, USER_PAID_FROM_BOND

EvidenceSchema:
  envelopeCount: 4
  envelopeTypes: PaymentReceiptEnvelope, WorkDeliveryEnvelope, AcceptanceEnvelope, FlowPulseReceiptEnvelope

FlowCompiler:
  valid accepted:                 3/3
  impossible histories rejected:  8/8
  escaped impossible histories:   0
```

The transcript is local evidence only. It does not claim custody, wallet enforcement, production bond adjudication, zero-knowledge privacy, TEE privacy, or production verifier infrastructure.
