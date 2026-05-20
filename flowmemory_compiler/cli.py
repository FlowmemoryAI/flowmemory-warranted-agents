"""Command line interface for the local FlowCompiler proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .agent_framework import run_agent_framework_demo
from .agent_adapter import run_adapter_demo
from .adapter_conformance import run_adapter_conformance_demo
from .agent_registry import run_registry_demo
from .agent_runtime import run_runtime_demo
from .bond_ledger import run_bond_ledger_demo
from .capture import capture_command
from .checker import check_trace
from .claim_gate import scan_claims
from .compiler import compile_plan, compile_trace
from .evidence_schema import evidence_schema_report
from .flowbond import demo_cases as flowbond_demo_cases
from .policycards import demo_policy_card, public_policy_view
from .private_compute import run_private_compute_demo
from .pulsepass import demo_passport, demo_proofs
from .release_transcript import build_release_transcript


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "examples" / "flowcompiler_cases.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="flowcompiler")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run bundled conformance cases.")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--json", action="store_true")

    compile_cmd = sub.add_parser("compile", help="Compile an AgentPlan or FutureTrace into a FlowProgram.")
    compile_src = compile_cmd.add_mutually_exclusive_group(required=True)
    compile_src.add_argument("--plan")
    compile_src.add_argument("--trace")
    compile_cmd.add_argument("--pretty", action="store_true")

    check = sub.add_parser("check", help="Check one FutureTrace.")
    check.add_argument("--trace", required=True)
    check.add_argument("--pretty", action="store_true")

    capture = sub.add_parser("capture-command", help="Run a command and emit a local TestRunEnvelope.")
    capture.add_argument("--step", required=True)
    capture.add_argument("--tree-hash", required=True)
    capture.add_argument("--observed-sequence", type=int, default=1)
    capture.add_argument("run_command", nargs=argparse.REMAINDER)

    flowbond = sub.add_parser("flowbond-demo", help="Run the FlowBond warranted-action R&D demo.")
    flowbond.add_argument("--pretty", action="store_true")
    flowbond.add_argument("--json", action="store_true")

    policycard = sub.add_parser("policycard-demo", help="Show a portable PolicyCard.")
    policycard.add_argument("--pretty", action="store_true")
    policycard.add_argument("--json", action="store_true")

    pulsepass = sub.add_parser("pulsepass-demo", help="Run the PulsePass scoped-proof demo.")
    pulsepass.add_argument("--pretty", action="store_true")
    pulsepass.add_argument("--json", action="store_true")

    framework = sub.add_parser("agent-framework-demo", help="Run the full warranted-agent framework demo.")
    framework.add_argument("--pretty", action="store_true")
    framework.add_argument("--json", action="store_true")

    adapter = sub.add_parser("agent-adapter-demo", help="Run the warranted-agent adapter boundary demo.")
    adapter.add_argument("--pretty", action="store_true")
    adapter.add_argument("--json", action="store_true")

    adapter_conformance = sub.add_parser("adapter-conformance-demo", help="Run warranted-agent adapter conformance checks.")
    adapter_conformance.add_argument("--pretty", action="store_true")
    adapter_conformance.add_argument("--json", action="store_true")

    registry = sub.add_parser("agent-registry-demo", help="Run warranted-agent registry and discovery demo.")
    registry.add_argument("--pretty", action="store_true")
    registry.add_argument("--json", action="store_true")

    runtime = sub.add_parser("agent-runtime-demo", help="Run warranted-agent runtime state machine demo.")
    runtime.add_argument("--pretty", action="store_true")
    runtime.add_argument("--json", action="store_true")

    ledger = sub.add_parser("bond-ledger-demo", help="Run local bond ledger accounting demo.")
    ledger.add_argument("--pretty", action="store_true")
    ledger.add_argument("--json", action="store_true")

    private_compute = sub.add_parser("private-compute-demo", help="Run local private memory computation demo.")
    private_compute.add_argument("--pretty", action="store_true")
    private_compute.add_argument("--json", action="store_true")

    evidence_schema = sub.add_parser("evidence-schema", help="Print warranted-agent evidence envelope specs.")
    evidence_schema.add_argument("--pretty", action="store_true")
    evidence_schema.add_argument("--json", action="store_true")

    transcript = sub.add_parser("release-transcript", help="Print canonical package transcript.")
    transcript.add_argument("--pretty", action="store_true")
    transcript.add_argument("--json", action="store_true")

    claim_gate = sub.add_parser("claim-gate", help="Scan public copy for unguarded overclaims.")
    claim_gate.add_argument("--pretty", action="store_true")
    claim_gate.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "demo":
        cases = _load_cases(DEFAULT_CASES)
        results = [check_trace(case) for case in cases]
        if args.json:
            print(json.dumps(results, indent=2, sort_keys=True))
        else:
            _print_demo(results)
        return 0 if all(_matches_expected(result, case) for result, case in zip(results, cases)) else 1

    if args.command == "compile":
        if args.plan:
            program = compile_plan(_load_json(Path(args.plan)))
        else:
            program = compile_trace(_load_json(Path(args.trace)))
        if args.pretty:
            _print_compile(program)
        else:
            print(json.dumps(program, indent=2, sort_keys=True))
        return 0

    if args.command == "check":
        trace = _load_json(Path(args.trace))
        result = check_trace(trace)
        if args.pretty:
            _print_single(result)
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == trace.get("expectedStatus", result["status"]) else 1

    if args.command == "capture-command":
        command = args.run_command
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            print("capture-command requires a command after --", flush=True)
            return 2
        envelope = capture_command(
            step_id=args.step,
            tree_hash=args.tree_hash,
            command=command,
            observed_sequence=args.observed_sequence,
        )
        print(json.dumps(envelope, indent=2, sort_keys=True))
        return 0 if envelope["fields"]["exitCode"] == 0 else envelope["fields"]["exitCode"]

    if args.command == "flowbond-demo":
        cases = flowbond_demo_cases()
        if args.json:
            print(json.dumps(cases, indent=2, sort_keys=True))
        else:
            _print_flowbond_demo(cases)
        return 0

    if args.command == "policycard-demo":
        card = public_policy_view(demo_policy_card())
        if args.json:
            print(json.dumps(card, indent=2, sort_keys=True))
        else:
            _print_policycard(card)
        return 0

    if args.command == "pulsepass-demo":
        passport = demo_passport()
        proofs = demo_proofs()
        if args.json:
            print(json.dumps({"passport": passport, "proofs": proofs}, indent=2, sort_keys=True))
        else:
            _print_pulsepass(passport, proofs)
        return 0

    if args.command == "agent-framework-demo":
        demo_result = run_agent_framework_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True))
        else:
            _print_agent_framework(demo_result)
        return 0

    if args.command == "agent-adapter-demo":
        demo_result = run_adapter_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True, default=_json_default))
        else:
            _print_agent_adapter(demo_result)
        return 0

    if args.command == "adapter-conformance-demo":
        demo_result = run_adapter_conformance_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True))
        else:
            _print_adapter_conformance(demo_result)
        return 0 if demo_result["passed"] else 1

    if args.command == "agent-registry-demo":
        demo_result = run_registry_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True))
        else:
            _print_agent_registry(demo_result)
        return 0

    if args.command == "agent-runtime-demo":
        demo_result = run_runtime_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True))
        else:
            _print_agent_runtime(demo_result)
        return 0

    if args.command == "bond-ledger-demo":
        demo_result = run_bond_ledger_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True))
        else:
            _print_bond_ledger(demo_result)
        return 0

    if args.command == "private-compute-demo":
        demo_result = run_private_compute_demo()
        if args.json:
            print(json.dumps(demo_result, indent=2, sort_keys=True))
        else:
            _print_private_compute(demo_result)
        return 0

    if args.command == "evidence-schema":
        report = evidence_schema_report()
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            _print_evidence_schema(report)
        return 0

    if args.command == "release-transcript":
        cases = _load_cases(DEFAULT_CASES)
        transcript_result = build_release_transcript(cases)
        if args.json:
            print(json.dumps(transcript_result, indent=2, sort_keys=True))
        else:
            _print_release_transcript(transcript_result)
        return 0

    if args.command == "claim-gate":
        result = scan_claims(ROOT)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            _print_claim_gate(result)
        return 0 if result["passed"] else 1

    return 2


def _print_demo(results: list[dict[str, Any]]) -> None:
    valid = [result for result in results if result["caseId"].startswith("FC-OK")]
    invalid = [result for result in results if result["caseId"].startswith("FC-BAD")]
    invalid_rejected = [result for result in invalid if result["status"] == "REJECTED"]

    print("FlowCompiler v0")
    print()
    print("Valid futures:")
    for result in valid:
        print(f"  {result['caseId']:<10} {result['label']:<45} {result['status']}")
    print()
    print("Impossible futures ordinary rails would accept:")
    for result in invalid:
        fault = result["faults"][0]["fault"] if result["faults"] else "NO_FAULT"
        print(f"  {result['caseId']:<10} {result['label']:<45} {result['status']} {fault}")
    print()
    if invalid_rejected:
        exemplar = next(
            (result for result in invalid_rejected if result["caseId"] == "FC-BAD-001"),
            invalid_rejected[0],
        )
        _print_forbidden_core(exemplar)
    print("Summary:")
    print(f"  futures checked: {len(results)}")
    print(f"  valid futures accepted: {sum(r['status'] == 'ACCEPTED' for r in valid)}/{len(valid)}")
    print(f"  impossible futures rejected: {len(invalid_rejected)}/{len(invalid)}")
    print(f"  escaped impossible futures: {sum(r['status'] == 'ACCEPTED' for r in invalid)}")
    print()
    print("Result:")
    print("  A valid action surface is not a valid machine history.")
    print()
    print("Non-claims:")
    print("  no custody, no wallet enforcement, no fund protection, no semantic truth, no model correctness, no production verifier.")


def _print_single(result: dict[str, Any]) -> None:
    print(f"{result['caseId']} {result['label']} {result['status']}")
    if result["faults"]:
        _print_forbidden_core(result)


def _print_compile(program: dict[str, Any]) -> None:
    print("FlowCompiler Compile")
    print()
    print("Plan:")
    print(f"  sourcePlanId: {program.get('sourcePlanId')}")
    print(f"  rootfieldId: {program.get('rootfieldId')}")
    print(f"  compileStatus: {program.get('compileStatus')}")
    print()
    print("Derived requirements:")
    for index, item in enumerate(program.get("derivedRequirements", []), start=1):
        subject = item.get("claim") or item.get("stepId")
        print(f"  R{index} {item['requirement']} [{item['kind']}] from {subject}")
        print(f"     because: {item['because']}")
    print()
    print("Binding constraints:")
    for index, item in enumerate(program.get("bindingConstraints", []), start=1):
        print(f"  B{index} {item['constraint']}")
        print(f"     because: {item['because']}")


def _print_flowbond_demo(cases: list[dict[str, Any]]) -> None:
    print("FlowBond R&D Demo")
    print()
    print("Thesis:")
    print("  Generic agents make claims. FlowMemory agents can leave warranted receipts.")
    print()
    for case in cases:
        result = case["result"]
        passed = "PASSED" if result["passed"] else "FAILED"
        print(f"{case['caseId']:<10} {case['label']:<32} {passed} {result['settlement']}")
        print(f"  policyHash: {result['policyHash']}")
        print(f"  pulseId:    {result['flowPulse']['pulseId']}")
        if result["violations"]:
            print(f"  violations: {', '.join(result['violations'])}")
    print()
    print("Result:")
    print("  A PolicyCard turns an agent promise into a FlowPulse-settled warranty.")
    print()
    print("Non-claims:")
    print("  no profit guarantee, no custody, no fund protection, no work-quality proof, no production adjudication.")


def _print_policycard(card: dict[str, Any]) -> None:
    print("PolicyCard Demo")
    print()
    print(f"title:        {card['title']}")
    print(f"promiseType:  {card['promise_type']}")
    print(f"agentId:      {card['agent_id']}")
    print(f"bondUnits:    {card['bond_units']}")
    print(f"policyHash:   {card['policyHash']}")
    print("requires:")
    for item in card["required_evidence"]:
        print(f"  - {item}")
    print()
    print("Result:")
    print("  The user rule is portable, hashable, and bondable without exposing private fields.")


def _print_pulsepass(passport: dict[str, Any], proofs: list[dict[str, Any]]) -> None:
    print("PulsePass Demo")
    print()
    print(f"ownerHash:       {passport['ownerHash']}")
    print(f"vaultCommitment: {passport['vaultCommitment']}")
    print(f"receiptCount:    {passport['receiptCount']}")
    print()
    print("Scoped proofs:")
    for proof in proofs:
        status = "PASS" if proof["passed"] else "FAIL"
        print(f"  {proof['predicate']:<40} {status} {proof['countBucket']} proof={proof['proofHash']}")
    print()
    print("Hidden:")
    print("  raw receipts, raw user id, exact action history, private obligation ids")


def _print_agent_framework(result: dict[str, Any]) -> None:
    print("FlowMemory Warranted Agent Framework")
    print()
    print("Stack:")
    print("  AgentManifest -> WorkRequest -> PolicyCard -> AgentProposal -> FlowBond -> FlowPulse -> PulsePass -> ScopedProof")
    print()
    print("Agent:")
    print(f"  {result['agentManifest']['display_name']}")
    print(f"  manifestHash: {result['agentManifest']['manifestHash']}")
    print()
    print("Policy:")
    print(f"  {result['policyCard']['title']}")
    print(f"  policyHash: {result['policyCard']['policyHash']}")
    print()
    print("Proposal:")
    print(f"  proposalHash: {result['agentProposal']['proposal_hash']}")
    print(f"  bondUnits:    {result['agentProposal']['bond_units']}")
    print()
    print("Settlements:")
    for settlement in result["settlements"]:
        status = "PASSED" if settlement["passed"] else "FAILED"
        print(f"  {settlement['flowPulse']['actionId']:<30} {status} {settlement['settlement']}")
        if settlement["violations"]:
            print(f"    violations: {', '.join(settlement['violations'])}")
    print()
    print("PulsePass:")
    print(f"  vaultCommitment: {result['pulsePass']['vaultCommitment']}")
    print(f"  receiptCount:    {result['pulsePass']['receiptCount']}")
    print()
    print("Scoped proofs:")
    for proof in result["scopedProofs"]:
        status = "PASS" if proof["passed"] else "FAIL"
        print(f"  {proof['predicate']:<36} {status} {proof['proofHash']}")
    print()
    print("Result:")
    print("  The agent framework turns promises into warranted receipts and user-owned scoped proof.")


def _print_agent_adapter(result: dict[str, Any]) -> None:
    print("FlowMemory Warranted Agent Adapter")
    print()
    print("Interface:")
    print("  manifest() -> quote(request) -> execute(policy) -> settle(policy, outcome)")
    print()
    print(f"policyHash:   {result['policyHash']}")
    print(f"proposalHash: {result['proposalHash']}")
    print()
    print("Settlements:")
    for settlement in result["settlements"]:
        status = "PASSED" if settlement["passed"] else "FAILED"
        print(f"  {settlement['flowPulse']['actionId']:<40} {status} {settlement['settlement']}")
    print()
    print("Result:")
    print("  The adapter boundary shows where future real agents plug into FlowMemory warranties.")


def _print_adapter_conformance(result: dict[str, Any]) -> None:
    print("FlowMemory Adapter Conformance")
    print()
    print(f"adapter: {result['adapter']}")
    print(f"status:  {'PASSED' if result['passed'] else 'FAILED'}")
    print()
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  {check['checkId']:<42} {status} {check['detail']}")
    print()
    print("Result:")
    print("  A future agent adapter can be checked against the warranted-agent contract before launch.")


def _print_agent_registry(result: dict[str, Any]) -> None:
    print("FlowMemory Warranted Agent Registry")
    print()
    print("Request:")
    print(f"  {result['request']['requestId']}")
    print(f"  requestedBondUnits: {result['request']['requestedBondUnits']}")
    print()
    print("Matches:")
    for match in result["matches"]:
        status = "ELIGIBLE" if match["eligible"] else "REJECTED"
        print(f"  {match['displayName']:<32} {status} score={match['warrantabilityScore']}")
        print(f"    reasons: {', '.join(match['reasons'])}")
        if match["missingEvidence"]:
            print(f"    missing: {', '.join(match['missingEvidence'])}")
    print()
    print("Result:")
    print("  Discovery is based on warranty evidence and bond capacity, not generic profile claims.")


def _print_agent_runtime(result: dict[str, Any]) -> None:
    print("FlowMemory Warranted Agent Runtime")
    print()
    for run in result["runs"]:
        print(f"Run: {run['mode']} -> {run['finalStatus']}")
        for event in run["timeline"]:
            print(f"  {event['phase']:<20} {event['status']:<8} {event['eventHash']}")
        print(f"  settlement: {run['settlement']['settlement']}")
        print()
    print("Result:")
    print("  The runtime turns discovery, quote, bond, execution, settlement, and proof into one deterministic machine history.")


def _print_bond_ledger(result: dict[str, Any]) -> None:
    print("FlowMemory Local Bond Ledger")
    print()
    for receipt in result["ledger"]["receipts"]:
        print(f"{receipt['sequence']:<2} {receipt['eventType']:<24} {receipt['bondId']}")
        print(f"   receiptId: {receipt['receiptId']}")
    print()
    print("Accounts:")
    for account_id, balance in result["ledger"]["accounts"].items():
        print(f"  {account_id:<32} {balance}")
    print()
    print("Result:")
    print("  Local accounting shows one warranty released to the agent and one paid to the user.")
    print()
    print("Non-claims:")
    print("  local ledger only; no custody, escrow, wallet, or production settlement.")


def _print_private_compute(result: dict[str, Any]) -> None:
    print("FlowMemory Private Compute Demo")
    print()
    print(f"vaultCommitment: {result['vaultCommitment']}")
    print()
    print("Programs:")
    for program in result["programResults"]:
        status = "PASS" if program["passed"] else "FAIL"
        print(f"  {program['programId']:<38} {status}")
        print(f"    transcriptHash: {program['transcriptHash']}")
        print(f"    revealed: {', '.join(sorted(program['revealed'].keys()))}")
        print(f"    hidden: {', '.join(program['hidden'])}")
    print()
    print("Result:")
    print("  Local private computation reveals scoped predicates over PulsePass without revealing raw receipts.")
    print()
    print("Non-claims:")
    print("  local only; no zero-knowledge, TEE, full privacy, or production private compute.")


def _print_evidence_schema(result: dict[str, Any]) -> None:
    print("FlowMemory Evidence Schema")
    print()
    for spec in result["envelopes"]:
        print(spec["envelopeType"])
        print(f"  {spec['purpose']}")
        for field in spec["fields"]:
            details = [field["kind"]]
            if field["requiredValue"] is not None:
                details.append(f"required={field['requiredValue']}")
            if field["prefix"] is not None:
                details.append(f"prefix={field['prefix']}")
            print(f"  - {field['name']}: {', '.join(details)}")
    print()
    print("Result:")
    print("  Evidence envelopes are named contracts with local field checks, not arbitrary receipt labels.")


def _print_release_transcript(result: dict[str, Any]) -> None:
    print("FlowMemory Warranted Agents Release Transcript")
    print()
    print(f"coreLine:       {result['coreLine']}")
    print(f"transcriptHash: {result['transcriptHash']}")
    print()
    print("Stack:")
    print("  " + " -> ".join(result["stack"]))
    print()
    print("FlowBond:")
    print(f"  releasedToAgent: {result['flowBond']['releasedToAgent']}")
    print(f"  paidToUser:      {result['flowBond']['paidToUser']}")
    print()
    print("AdapterConformance:")
    print(f"  passed:     {result['adapterConformance']['passed']}")
    print(f"  checkCount: {result['adapterConformance']['checkCount']}")
    print()
    print("AgentRegistry:")
    print(f"  eligibleAgents: {result['agentRegistry']['eligibleAgents']}")
    print(f"  rejectedAgents: {result['agentRegistry']['rejectedAgents']}")
    print()
    print("AgentRuntime:")
    print(f"  runs:          {result['agentRuntime']['runCount']}")
    print(f"  finalStatuses: {', '.join(result['agentRuntime']['finalStatuses'])}")
    print()
    print("EvidenceSchema:")
    print(f"  envelopeCount: {result['evidenceSchema']['envelopeCount']}")
    print(f"  envelopeTypes: {', '.join(result['evidenceSchema']['envelopeTypes'])}")
    print()
    print("BondLedger:")
    print(f"  events: {', '.join(result['bondLedger']['events'])}")
    print()
    print("PulsePass:")
    print(f"  vaultCommitment: {result['pulsePass']['vaultCommitment']}")
    print(f"  receiptCount:    {result['pulsePass']['receiptCount']}")
    print()
    print("PrivateCompute:")
    for program in result["privateCompute"]["programs"]:
        status = "PASS" if program["passed"] else "FAIL"
        print(f"  {program['programId']:<38} {status} {program['transcriptHash']}")
    print()
    print("FlowCompiler:")
    compiler = result["flowCompiler"]
    print(f"  valid accepted:                 {compiler['validAccepted']}/{compiler['validTotal']}")
    print(f"  impossible histories rejected:  {compiler['invalidRejected']}/{compiler['invalidTotal']}")
    print(f"  escaped impossible histories:   {compiler['escapedImpossibleHistories']}")
    print()
    print("Non-claims:")
    print("  " + ", ".join(result["notClaims"]))


def _print_claim_gate(result: dict[str, Any]) -> None:
    print("FlowMemory Claim Gate")
    print()
    print(f"filesChecked:         {result['filesChecked']}")
    print(f"guardedRiskMentions:  {result['guardedRiskMentions']}")
    print(f"unguardedOverclaims:  {len(result['unguardedOverclaims'])}")
    print(f"status:               {'PASSED' if result['passed'] else 'FAILED'}")
    if result["unguardedOverclaims"]:
        print()
        print("Unguarded claims:")
        for item in result["unguardedOverclaims"]:
            print(f"  {item['file']}:{item['line']} [{item['phrase']}] {item['text']}")


def _print_forbidden_core(result: dict[str, Any]) -> None:
    first = result["faults"][0]
    print(f"Forbidden core for {result['caseId']} ({first['fault']}):")
    for item in first["forbiddenCore"]["minimalCore"]:
        print(f"  {item['path']} = {item['value']}")
    print()
    print("Repair:")
    for item in first["repair"]["instructions"]:
        action = item.get("action", "repair")
        reason = item.get("reason") or item.get("claimReplacement") or ""
        print(f"  {action}: {reason}")
    print()


def _matches_expected(result: dict[str, Any], case: dict[str, Any]) -> bool:
    return result["status"] == case.get("expectedStatus")


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = _load_json(path)
    return payload["cases"]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_default(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return value.__dict__
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


if __name__ == "__main__":
    raise SystemExit(main())
