# Contributing

FlowMemory Warranted Agents is a local public proof for turning specific agent
promises into portable warranties backed by FlowPulse memory.

Contributions should preserve the core split:

```text
user rule -> bond-modeled promise -> receipt-backed memory -> scoped private proof
```

## Local Checks

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m flowmemory_compiler.cli release-transcript --pretty
python -m flowmemory_compiler.cli launch-packet --pretty
python -m flowmemory_compiler.cli production-readiness --pretty
git diff --check
```

## Technical Boundaries

Do not add claims or code paths that imply:

- custody;
- wallet enforcement;
- fund protection;
- production settlement;
- production adjudication;
- production verifier infrastructure;
- production private compute;
- zero-knowledge privacy in v0;
- semantic truth;
- model correctness;
- guaranteed fraud prevention;
- live Base deployment.

## Documentation Tone

The language should be bold but bounded.

Good:

- warranted receipts;
- PolicyCards;
- FlowBond;
- PulsePass scoped proofs;
- deterministic machine histories;
- local conformance checks;
- explicit production blockers.

Avoid:

- production custody or settlement claims;
- broad AI truth claims;
- guarantees that users are protected from loss;
- implying live verifier infrastructure exists;
- presenting local R&D demos as deployed systems.

## Pull Requests

Keep changes scoped. A good PR should explain:

- what warranty, evidence, proof, runtime, or document changed;
- how it preserves the claim boundaries;
- which tests or checks were run;
- what production claims it deliberately avoids.
