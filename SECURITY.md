# Security Policy

This repository is a public FlowMemory warranted-agent R&D and conformance package.

The current implementation is intentionally local:

- no custody;
- no wallet enforcement;
- no live production settlement;
- no production verifier network;
- no production bond adjudication;
- no zero-knowledge privacy claim;
- no guarantee of work quality, semantic truth, or model correctness.

## Reporting A Vulnerability

Prefer a private GitHub security advisory if the repository enables it. If not,
open a GitHub issue with a minimal description and avoid posting exploitable
live-system details until maintainers respond.

Do not include:

- private keys;
- seed phrases or mnemonics;
- funded wallet secrets;
- private RPC URLs;
- API keys;
- unpublished exploit scripts against live assets.

## What Counts As Security-Relevant

Please report:

- evidence envelopes that can be forged or mismatched;
- PolicyCard, FlowBond, PulsePass, or scoped-proof behavior that contradicts the documented claim boundaries;
- conformance checks that accept impossible machine histories;
- private-proof flows that reveal raw receipt history unexpectedly;
- release language that implies custody, fund protection, production settlement, production verifier readiness, or live Base deployment without evidence.

## Claim Boundary

FlowMemory Warranted Agents is a local deterministic framework for making agent
promises inspectable as receipt-bound machine histories. It does not claim
production custody, production settlement, production adjudication, semantic
truth, model correctness, or production verifier readiness.
