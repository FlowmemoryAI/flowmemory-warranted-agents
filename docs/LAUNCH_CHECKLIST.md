# Launch Checklist

This checklist keeps the warranted-agent package launchable without overstating what v0 proves.

## Required Before Public Share

- `python -m unittest discover -s tests -p "test_*.py"` passes.
- `python -m flowmemory_compiler.cli release-transcript --pretty` prints the current stack.
- `python -m flowmemory_compiler.cli pulserouter-demo --pretty` selects the private bonded provider and reports no validation faults.
- `python -m flowmemory_compiler.cli pulserouter-adversary --pretty` catches every bundled adversarial route/outcome manipulation.
- `python -m flowmemory_compiler.cli claim-gate --pretty` passes with `unguardedOverclaims: 0`.
- GitHub Actions CI passes on `main`.
- README opening still explains the category in one screen.
- Non-claims remain visible.

## Public Demo Path

Use this order:

```powershell
python -m flowmemory_compiler.cli release-transcript --pretty
python -m flowmemory_compiler.cli pulserouter-demo --pretty
python -m flowmemory_compiler.cli pulserouter-adversary --pretty
python -m flowmemory_compiler.cli agent-runtime-demo --pretty
python -m flowmemory_compiler.cli agent-registry-demo --pretty
python -m flowmemory_compiler.cli evidence-schema --pretty
python -m flowmemory_compiler.cli demo --pretty
```

The story is:

```text
1. Here is the full stack.
2. Here is outcome routing by successful work, not token price.
3. Here are adversarial route manipulations rejected.
4. Here is the runtime history.
5. Here is warranty-based discovery.
6. Here are the evidence contracts.
7. Here are impossible histories rejected.
```

## Public Positioning

Lead with:

```text
Generic agents make claims. FlowMemory agents can leave warranted receipts.
```

Then explain:

```text
Available is not enough. Warrantable is the standard.
```

Then show the framework:

```text
manifest -> quote -> bond -> action -> settlement -> memory -> private proof
```

Then show the outcome layer:

```text
compute -> tool -> action -> FlowPulse -> outcome -> portable user memory
```

## Reviewer-Safe Claims

Safe:

- local deterministic warranted-agent framework;
- PolicyCards turn promises into hashable rules;
- FlowBond models bond-backed pass/fail settlement;
- AgentRegistry filters agents by warranty evidence and bond capacity;
- AgentRuntime records the state machine from quote to private proof;
- EvidenceSchema checks required local fields for evidence envelopes;
- PulsePass exposes scoped proofs without raw receipt history;
- PulseRouter routes providers by expected successful outcome, not raw token price;
- PulseRouter catches bundled route/outcome manipulation cases;
- FlowCompiler rejects impossible machine histories in the bundled cases.

Not safe to claim:

- live production custody;
- live wallet enforcement;
- live x402 replacement;
- production private compute;
- production verifier infrastructure;
- work-quality proof;
- semantic truth;
- zero-knowledge privacy in v0;
- guaranteed fraud prevention.
- live provider marketplace;
- production x402 service;

## Final Confidence Gate

The launch package is ready to share when:

```text
tests pass
claim gate passes
CI passes
release transcript reflects the current stack
```
