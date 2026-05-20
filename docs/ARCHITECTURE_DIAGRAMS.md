# Architecture Diagrams

## Framework Stack

```mermaid
flowchart LR
  A[AgentManifest] --> B[WorkRequest]
  B --> C[PolicyCard]
  C --> D[AgentProposal]
  D --> E[AgentRegistry]
  E --> F[AgentRuntime]
  F --> G[EvidenceSchema]
  G --> H[FlowBond]
  H --> I[BondLedger]
  H --> J[FlowPulse]
  J --> K[PulsePass]
  K --> L[PrivateCompute]
  L --> M[ScopedProof]
  H --> N[FlowCompiler]
```

Core idea:

```text
The agent promise becomes a warranted machine history.
```

## Runtime Sequence

```mermaid
sequenceDiagram
  participant U as User
  participant R as AgentRegistry
  participant A as AgentAdapter
  participant T as AgentRuntime
  participant B as FlowBond
  participant P as PulsePass

  U->>R: WorkRequest
  R-->>U: eligible warranted agents
  U->>A: quote(request)
  A-->>U: PolicyCard + AgentProposal
  U->>T: run(policy)
  T->>T: lock local bond
  T->>A: execute(policy)
  A-->>T: evidence envelopes
  T->>B: settle(policy, outcome)
  B-->>T: FlowPulse settlement
  T->>P: store receipt
  P-->>U: scoped proof
```

## Success Path

```mermaid
flowchart TD
  A[Required evidence exists] --> B[Evidence fields pass schema]
  B --> C[Obligation links match]
  C --> D[Acceptance is true]
  D --> E[FlowBond passes]
  E --> F[Bond releases to agent]
  F --> G[PulsePass stores success receipt]
```

## Failure Path

```mermaid
flowchart TD
  A[Payment exists] --> B{Delivery evidence present?}
  B -- No --> C[FlowBond fails]
  B -- Yes --> D{Acceptance present?}
  D -- No --> C
  D -- Yes --> E{Obligation links match?}
  E -- No --> C
  C --> F[Bond pays user]
  F --> G[PulsePass stores failed warranty receipt]
```

## Boundary

These diagrams describe the local deterministic framework. They do not claim production custody, wallet enforcement, production verifier infrastructure, production settlement, zero-knowledge privacy, or work-quality proof.
