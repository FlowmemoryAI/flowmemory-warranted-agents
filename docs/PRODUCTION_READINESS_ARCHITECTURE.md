# Production Readiness Architecture

FlowMemory Warranted Agents is production-shaped, but this repository does not claim a production deployment.

The current package is a local deterministic framework. Production readiness requires external adapters, operational controls, durable evidence infrastructure, and independent security review.

## Production Candidate Stack

```text
Agent adapter
  -> PolicyCard
  -> AgentProposal
  -> Production bond/payment rail
  -> Runtime state machine
  -> Evidence schema validator
  -> Reader/verifier service
  -> Durable receipt store
  -> FlowPulse memory artifact
  -> PulsePass / private proof backend
  -> Observability and incident response
```

## Deployable Components

Production candidates:

- external agent adapter;
- adapter conformance harness;
- runtime state machine;
- evidence schema validator;
- reader/verifier service;
- durable receipt store;
- observability exporter;
- launch and production readiness gates.

Local-only in this repo:

- `LocalBondLedger`;
- demo adapters;
- local private compute;
- demo PulsePass vault;
- bundled fixture histories.

## Trust Boundaries

The framework must keep these boundaries separate:

| Boundary | Production owner | Notes |
| --- | --- | --- |
| Agent execution | Agent operator | The framework checks receipts; it does not host all agent work. |
| Wallet signing | Wallet/key infrastructure | The framework must not custody user or agent keys. |
| Bond/payment rail | External payment or settlement system | Local ledger is only a model. |
| Evidence verification | Reader/verifier service | Must attach receipt facts and finality metadata. |
| Private proof | Selected privacy backend | Local private compute is not production privacy. |
| Public claims | Release operator | Claim gate must pass before publication. |

## Production Blockers

Production is blocked until all external gates are satisfied:

- real wallet adapter;
- real payment or bond rail;
- persistent receipt store;
- reader/verifier service;
- key management and secret rotation;
- observability and alerting;
- incident response runbook;
- security review or audit;
- load and replay testing;
- privacy backend selection.

Run:

```powershell
python -m flowmemory_compiler.cli production-readiness --pretty
```

Expected current status:

```text
localArchitectureReady: True
productionReady:        False
releaseMode:            LOCAL_ARCHITECTURE_READY_ONLY
```

## Non-Claims

This architecture does not claim production custody, wallet enforcement, production settlement, production private compute, security audit completion, or production verifier infrastructure.
