# Changelog

## 0.3.0

Outcome-settled AI and PulseRouter launch slice.

- Added PulseRouter local router for provider selection by expected successful outcome, not raw token price.
- Added ComputePulse, ToolCallPulse, ActionPulse, FlowPulseLink, OutcomePulse, ProviderQuote, OutcomePolicy, and RouteScore local data model.
- Added `pulserouter-demo` and `pulserouter-adversary` CLI commands.
- Added 26-case adversarial suite for route manipulation, privacy drift, FlowPulse link drift, settlement drift, cost-accounting drift, policy drift, unconfirmed FlowPulse evidence, and raw model-content leakage.
- Added Outcome-Settled AI and PulseRouter architecture docs plus `PulseRouter.v0` spec.
- Added PulseRouter checks to release transcript, launch packet, CI demos, and local tests.

## 0.2.1

Launch packet and adapter conformance hardening.

- Added adapter conformance harness and CLI.
- Added launch packet CLI and CI check.
- Added reviewer walkthrough.
- Enabled default `python -m unittest` discovery.
- Added compact integration artifacts after the initial 0.2.0 framework release.

## 0.2.0

Warranted-agent framework build-out.

- Added AgentRegistry with warrantability scoring.
- Added AgentRuntime with explicit runtime state machine.
- Added runtime transition hashes and idempotency-key replay rejection.
- Added EvidenceSchema checks for warranted receipt envelopes.
- Added adapter contract docs, developer handoff, launch checklist, threat model, claim boundaries, architecture diagrams, and marketing positioning.
- Added compact warranted-agent example artifacts.
- Added claim gate CLI and CI check for public overclaim protection.
- Expanded release transcript to include registry, runtime, and evidence schema.
- Expanded local tests to 29 passing cases.

## 0.1.0

Initial local proof package for PolicyCards, FlowBond, PulsePass, private compute, FlowCompiler conformance, release transcript, and adapter boundary.
