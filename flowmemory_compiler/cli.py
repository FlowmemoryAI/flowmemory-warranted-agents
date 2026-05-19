"""Command line interface for the local FlowCompiler proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .checker import check_trace
from .compiler import compile_trace


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "examples" / "flowcompiler_cases.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="flowcompiler")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run bundled conformance cases.")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--json", action="store_true")

    compile_cmd = sub.add_parser("compile", help="Compile one FutureTrace into a FlowProgram.")
    compile_cmd.add_argument("--trace", required=True)

    check = sub.add_parser("check", help="Check one FutureTrace.")
    check.add_argument("--trace", required=True)
    check.add_argument("--pretty", action="store_true")

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
        trace = _load_json(Path(args.trace))
        print(json.dumps(compile_trace(trace), indent=2, sort_keys=True))
        return 0

    if args.command == "check":
        trace = _load_json(Path(args.trace))
        result = check_trace(trace)
        if args.pretty:
            _print_single(result)
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == trace.get("expectedStatus", result["status"]) else 1

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


if __name__ == "__main__":
    raise SystemExit(main())

