# Claim Gate

FlowMemory Warranted Agents uses a public claim gate to keep the launch package bold without drifting into unsupported claims.

The gate scans `README.md`, `docs/`, and `specs/` for risky phrases that should only appear as guarded non-claims or boundary statements.

Run it locally:

```powershell
python -m flowmemory_compiler.cli claim-gate --pretty
```

Expected result:

```text
FlowMemory Claim Gate

filesChecked:         ...
guardedRiskMentions:  ...
unguardedOverclaims:  0
status:               PASSED
```

## What It Protects

The framework can say, clearly:

- generic agents make claims;
- FlowMemory agents can leave warranted receipts;
- PolicyCards make promises portable and hashable;
- FlowBond models money-on-the-line warranty outcomes;
- PulsePass gives users scoped private proof;
- FlowCompiler rejects impossible machine histories.

It must not drift into unsupported claims about custody, wallet enforcement, production settlement, production verification, full privacy, semantic truth, model correctness, or guaranteed work quality.

## Why This Matters

The category claim is stronger when the boundary is explicit:

```text
FlowMemory does not replace wallets, payments, custody, settlement, or agent execution.
FlowMemory adds receipt-bound memory and deterministic conformance around agent work.
```

That is the public architecture line. The claim gate keeps the repo aligned with it.
