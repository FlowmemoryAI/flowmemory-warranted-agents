# PulsePods Architecture

PulsePods are memory-native compute pods for agents.

The point is not to copy private compute clusters, pooled keys, or generic
agent workspaces. A PulsePod is a pod that routes work by the memory it can
prove after execution.

```text
PolicyCard
  -> provider promises
  -> PulseRouter
  -> ComputePulse candidates
  -> selected ActionPulse
  -> reader-derived FlowPulseLink
  -> OutcomePulse
  -> PulsePass scoped claim
  -> x402-compatible federation offer
```

## Category Claim

Generic pods pool agents, models, credits, and compute.

PulsePods add the missing outcome layer:

```text
Which route produced a successful receipt-backed action under the user's policy?
```

The launch claim is narrow:

```text
PulsePods route agent compute by successful FlowPulse outcomes, not raw token price.
```

## What A PulsePod Contains

| Component | Role |
| --- | --- |
| `PulsePodManifest` | Local pod identity, policy hash, routing objective, evidence requirements, and logging defaults. |
| `ProviderPromise` | Provider commitment to policy-safe work, bond coverage, canary status, and public-pulse privacy discipline. |
| `PulseRouter` | Chooses the route with the best expected successful outcome, not the cheapest raw inference quote. |
| `ComputePulse` | Receipt that a provider produced a committed response without storing raw prompt or response text in the public pulse. |
| `ActionPulse` | Receipt that a bounded action proposal was created under a policy. |
| `FlowPulseLink` | Reader-derived link to transaction memory; the hook does not know receipt metadata at execution time. |
| `OutcomePulse` | Settlement receipt that records whether the action became a successful outcome. |
| `PulsePassClaim` | Private scoped user proof that reveals a predicate instead of raw history. |
| `FederationOffer` | Local x402-compatible reference object for future pod-to-pod work buying. |

## Why This Is Better Than A Generic Pod

Generic pods answer:

```text
Where does the model run?
```

PulsePods answer:

```text
Which model route can prove useful work after execution?
```

That gives FlowMemory a sharper position:

- not raw inference routing;
- not generic agent reputation;
- not screenshots of activity;
- not a dashboard after the fact;
- receipt-backed outcome memory.

## Demo

Run:

```powershell
python -m flowmemory_compiler.cli pulsepod-demo --pretty
python -m flowmemory_compiler.cli pulsepod-adversary --pretty
```

The demo seeds three routes:

| Route | Raw price | Result |
| --- | ---: | --- |
| cheap unbonded route | 1 unit | blocked by policy and missing bond |
| private bonded route | 4 units | selected |
| frontier unbonded route | 12 units | blocked by policy and missing bond |

The reveal:

```text
The cheapest route lost. The useful bonded route won.
```

## Local Validation

`pulsepod-adversary` currently catches drift across:

- pod identity;
- routing objective;
- raw logging defaults;
- selected route;
- provider promise;
- FlowPulse source and finality;
- OutcomePulse linkage;
- PulsePass privacy;
- federation evidence;
- demo memory credit boundaries;
- public copy overclaims.

The adversary suite is intentionally local. It is a launch proof that the
architecture has deterministic failure modes before external integrations are
added.

## Non-Claims

PulsePods do not claim a live compute marketplace, production settlement, full
privacy, zero-knowledge privacy, TEE attestation, cheaper inference, model
correctness, real user earnings, custody, wallet enforcement, or fund
protection.
