import json
import sys
import unittest
from pathlib import Path

from flowmemory_compiler.capture import capture_command
from flowmemory_compiler.checker import check_trace
from flowmemory_compiler.compiler import compile_trace
from flowmemory_compiler.flowbond import demo_cases as flowbond_demo_cases


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "examples" / "flowcompiler_cases.json").read_text(encoding="utf-8"))["cases"]


class FlowCompilerTest(unittest.TestCase):
    def test_all_expected_statuses_hold(self):
        for case in CASES:
            with self.subTest(case=case["caseId"]):
                self.assertEqual(check_trace(case)["status"], case["expectedStatus"])

    def test_three_valid_futures_are_accepted(self):
        valid = [case for case in CASES if case["caseId"].startswith("FC-OK")]
        self.assertEqual(len(valid), 3)
        self.assertTrue(all(check_trace(case)["status"] == "ACCEPTED" for case in valid))

    def test_eight_impossible_futures_are_rejected(self):
        invalid = [case for case in CASES if case["caseId"].startswith("FC-BAD")]
        self.assertEqual(len(invalid), 8)
        self.assertTrue(all(check_trace(case)["status"] == "REJECTED" for case in invalid))

    def test_compiler_derives_required_envelopes(self):
        case = _case("FC-OK-002")
        program = compile_trace(case)
        envelope_types = {item["envelopeType"] for item in program["requiredEnvelopes"]}
        self.assertIn("PaymentReceiptEnvelope", envelope_types)
        self.assertIn("DischargeEnvelope", envelope_types)
        self.assertTrue(program["derivedRequirements"])
        self.assertTrue(program["bindingConstraints"])

    def test_wrong_tree_forbidden_core_contains_patch_and_test_hashes(self):
        result = check_trace(_case("FC-BAD-001"))
        core = result["faults"][0]["forbiddenCore"]["minimalCore"]
        self.assertIn({"path": "DiffEnvelope.afterTreeHash", "value": "sha256:tree-after"}, core)
        self.assertIn({"path": "TestRunEnvelope.treeHash", "value": "sha256:tree-before"}, core)

    def test_wrong_obligation_forbidden_core_contains_payment_and_discharge(self):
        result = check_trace(_case("FC-BAD-002"))
        fault = _fault(result, "payment_receipt_wrong_obligation")
        core = fault["forbiddenCore"]["minimalCore"]
        self.assertIn({"path": "PaymentReceiptEnvelope.paymentRequirementHash", "value": "sha256:pay-req-a"}, core)
        self.assertIn({"path": "DischargeEnvelope.paymentRequirementHash", "value": "sha256:pay-req-b"}, core)

    def test_swap_receipt_without_flowpulse_is_rejected(self):
        result = check_trace(_case("FC-BAD-005"))
        self.assertEqual(result["faults"][0]["fault"], "swap_receipt_missing_flowpulse")
        self.assertEqual(_fault(result, "swap_receipt_missing_flowpulse")["fault"], "swap_receipt_missing_flowpulse")

    def test_verified_claim_requires_verification_envelope(self):
        result = check_trace(_case("FC-BAD-007"))
        self.assertEqual(_fault(result, "verified_without_envelope")["fault"], "verified_without_envelope")

    def test_payment_receipt_without_discharge_is_rejected(self):
        result = check_trace(_case("FC-BAD-008"))
        fault = _fault(result, "payment_success_without_obligation_discharge")
        self.assertEqual(result["faults"][0]["fault"], "payment_success_without_obligation_discharge")
        self.assertIn({"path": "requiredEnvelope.DischargeEnvelope", "value": "missing"}, fault["forbiddenCore"]["minimalCore"])

    def test_repairs_are_emitted_for_each_rejected_case(self):
        for case in CASES:
            if not case["caseId"].startswith("FC-BAD"):
                continue
            with self.subTest(case=case["caseId"]):
                result = check_trace(case)
                self.assertTrue(result["faults"])
                self.assertTrue(result["faults"][0]["repair"]["instructions"])

    def test_no_escaped_impossible_histories(self):
        escaped = [case["caseId"] for case in CASES if case["caseId"].startswith("FC-BAD") and check_trace(case)["status"] == "ACCEPTED"]
        self.assertEqual(escaped, [])

    def test_capture_command_emits_test_run_envelope(self):
        envelope = capture_command(
            step_id="test-1",
            tree_hash="sha256:tree-after",
            command=[sys.executable, "-c", "print('ok')"],
            observed_sequence=3,
        )
        self.assertEqual(envelope["envelopeType"], "TestRunEnvelope")
        self.assertEqual(envelope["stepId"], "test-1")
        self.assertEqual(envelope["observedSequence"], 3)
        self.assertEqual(envelope["fields"]["exitCode"], 0)
        self.assertEqual(envelope["fields"]["treeHash"], "sha256:tree-after")
        self.assertTrue(envelope["fields"]["stdoutHash"].startswith("sha256:"))

    def test_flowbond_demo_releases_or_pays_bond(self):
        cases = flowbond_demo_cases()
        self.assertEqual(len(cases), 2)
        self.assertTrue(cases[0]["result"]["passed"])
        self.assertEqual(cases[0]["result"]["settlement"], "RELEASE_BOND_TO_AGENT")
        self.assertFalse(cases[1]["result"]["passed"])
        self.assertEqual(cases[1]["result"]["settlement"], "PAY_BOND_TO_USER")
        self.assertIn("max_slippage_exceeded", cases[1]["result"]["violations"])
        self.assertTrue(cases[1]["result"]["flowPulse"]["pulseId"].startswith("sha256:"))


def _case(case_id):
    return next(case for case in CASES if case["caseId"] == case_id)


def _fault(result, fault_name):
    return next(fault for fault in result["faults"] if fault["fault"] == fault_name)


if __name__ == "__main__":
    unittest.main()
