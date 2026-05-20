import json
import sys
import unittest
from pathlib import Path

from flowmemory_compiler.agent_adapter import DemoWarrantedAgentAdapter, run_adapter_demo
from flowmemory_compiler.agent_framework import demo_request, run_agent_framework_demo
from flowmemory_compiler.adapter_conformance import run_adapter_conformance_demo
from flowmemory_compiler.agent_registry import run_registry_demo
from flowmemory_compiler.agent_runtime import run_runtime_demo
from flowmemory_compiler.bond_ledger import run_bond_ledger_demo
from flowmemory_compiler.capture import capture_command
from flowmemory_compiler.checker import check_trace
from flowmemory_compiler.claim_gate import scan_claims
from flowmemory_compiler.compiler import compile_trace
from flowmemory_compiler.evidence_schema import evidence_schema_report, validate_evidence_envelope
from flowmemory_compiler.flowbond import AgentWorkOutcome, EvidenceEnvelope, demo_cases as flowbond_demo_cases, settle_warranted_action
from flowmemory_compiler.policycards import demo_policy_card, policy_hash, public_policy_view
from flowmemory_compiler.private_compute import run_private_compute_demo
from flowmemory_compiler.pulsepass import ScopedProofRequest, build_pulsepass, demo_passport, scoped_proof
from flowmemory_compiler.release_transcript import build_release_transcript
from flowmemory_compiler.runtime_state_machine import ACTION_EXECUTED, MANIFEST_LOADED, RuntimeStateMachine


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
        self.assertEqual(len(cases), 3)
        self.assertTrue(cases[0]["result"]["passed"])
        self.assertEqual(cases[0]["result"]["settlement"], "RELEASE_BOND_TO_AGENT")
        self.assertFalse(cases[1]["result"]["passed"])
        self.assertEqual(cases[1]["result"]["settlement"], "PAY_BOND_TO_USER")
        self.assertIn("payment_without_delivery", cases[1]["result"]["violations"])
        self.assertIn("missing_WorkDeliveryEnvelope", cases[1]["result"]["violations"])
        self.assertFalse(cases[2]["result"]["passed"])
        self.assertIn("PaymentReceiptEnvelope_wrong_obligation", cases[2]["result"]["violations"])
        self.assertTrue(cases[1]["result"]["flowPulse"]["pulseId"].startswith("sha256:"))

    def test_evidence_schema_validates_local_envelopes(self):
        self.assertEqual(validate_evidence_envelope("PaymentReceiptEnvelope", {"receiptStatus": "settled"}), [])
        self.assertIn(
            "field_artifactHash_bad_prefix",
            validate_evidence_envelope("WorkDeliveryEnvelope", {"artifactHash": "artifact-ok"}),
        )
        report = evidence_schema_report()
        self.assertEqual(len(report["envelopes"]), 4)

    def test_flowbond_rejects_malformed_evidence_fields(self):
        card = demo_policy_card()
        outcome = AgentWorkOutcome(
            action_id="action:bad-evidence-schema",
            spent_units=10_00,
            completed_at=1_800_000_000,
            tx_hash="0x" + "88" * 32,
            evidence=(
                EvidenceEnvelope("PaymentReceiptEnvelope", "local:1", card.obligation_id, {"receiptStatus": "settled"}),
                EvidenceEnvelope("WorkDeliveryEnvelope", "local:2", card.obligation_id, {"artifactHash": "artifact-ok"}),
                EvidenceEnvelope("AcceptanceEnvelope", "local:3", card.obligation_id, {"accepted": True}),
                EvidenceEnvelope("FlowPulseReceiptEnvelope", "local:4", card.obligation_id, {"pulseObserved": True}),
            ),
        )
        result = settle_warranted_action(card, outcome)
        self.assertFalse(result["passed"])
        self.assertIn("WorkDeliveryEnvelope_field_artifactHash_bad_prefix", result["violations"])

    def test_policycard_public_view_hides_private_fields(self):
        card = demo_policy_card()
        public = public_policy_view(card)
        self.assertEqual(public["policyHash"], policy_hash(card))
        self.assertNotIn("user_id", public)
        self.assertNotIn("obligation_id", public)
        self.assertIn("WorkDeliveryEnvelope", public["required_evidence"])

    def test_pulsepass_scoped_proofs_hide_raw_receipts(self):
        passport = demo_passport()
        proof = scoped_proof(passport, ScopedProofRequest("has_completed_warranted_action", threshold=1))
        self.assertTrue(proof["passed"])
        self.assertIn("raw_receipts", proof["hidden"])
        self.assertNotIn("receipts", proof["revealed"])

    def test_pulsepass_can_fail_threshold_without_revealing_history(self):
        receipts = [case["result"] for case in flowbond_demo_cases()]
        passport = build_pulsepass("user:local-demo", receipts)
        proof = scoped_proof(passport, ScopedProofRequest("has_three_completed_warranted_actions", threshold=3))
        self.assertFalse(proof["passed"])
        self.assertEqual(proof["countBucket"], "1")

    def test_agent_framework_runs_end_to_end(self):
        result = run_agent_framework_demo()
        self.assertEqual(result["schema"], "flowmemory.agent_framework_demo.v0")
        self.assertTrue(result["agentManifest"]["manifestHash"].startswith("sha256:"))
        self.assertTrue(result["policyCard"]["policyHash"].startswith("sha256:"))
        self.assertEqual(len(result["settlements"]), 2)
        self.assertTrue(result["settlements"][0]["passed"])
        self.assertFalse(result["settlements"][1]["passed"])
        self.assertEqual(result["pulsePass"]["receiptCount"], 2)
        self.assertEqual(len(result["scopedProofs"]), 2)
        self.assertTrue(all(proof["proofHash"].startswith("sha256:") for proof in result["scopedProofs"]))

    def test_bond_ledger_releases_and_pays(self):
        result = run_bond_ledger_demo()
        receipts = result["ledger"]["receipts"]
        event_types = [receipt["eventType"] for receipt in receipts]
        self.assertEqual(event_types, ["BOND_LOCKED", "RELEASE_BOND_TO_AGENT", "BOND_LOCKED", "PAY_BOND_TO_USER"])
        accounts = result["ledger"]["accounts"]
        self.assertEqual(accounts["agent:work-warranty-demo"], 75_00)
        self.assertEqual(accounts["user:local-demo"], 25_00)
        self.assertTrue(all(receipt["receiptId"].startswith("sha256:") for receipt in receipts))

    def test_private_compute_returns_scoped_transcripts(self):
        result = run_private_compute_demo()
        self.assertEqual(result["schema"], "flowmemory.private_compute_demo.v0")
        self.assertEqual(len(result["programResults"]), 2)
        self.assertTrue(all(item["transcriptHash"].startswith("sha256:") for item in result["programResults"]))
        self.assertTrue(all("raw_receipts" in item["hidden"] for item in result["programResults"]))
        self.assertTrue(result["programResults"][0]["passed"])

    def test_release_transcript_summarizes_all_layers(self):
        result = build_release_transcript(CASES)
        self.assertEqual(result["schema"], "flowmemory.warranted_agents_release_transcript.v0")
        self.assertIn("AgentManifest", result["stack"])
        self.assertIn("PrivateCompute", result["stack"])
        self.assertTrue(result["transcriptHash"].startswith("sha256:"))
        self.assertEqual(result["flowBond"]["releasedToAgent"], 1)
        self.assertEqual(result["flowBond"]["paidToUser"], 2)
        self.assertEqual(result["flowCompiler"]["validAccepted"], 3)
        self.assertEqual(result["flowCompiler"]["invalidRejected"], 8)
        self.assertEqual(result["flowCompiler"]["escapedImpossibleHistories"], 0)

    def test_agent_adapter_boundary_quotes_and_executes(self):
        adapter = DemoWarrantedAgentAdapter()
        policy, proposal = adapter.quote(demo_request())
        self.assertEqual(proposal.policy_hash, policy_hash(policy))
        success = adapter.execute(policy, mode="success")
        failure = adapter.execute(policy, mode="payment_without_delivery")
        self.assertEqual(success.action_id, "action:adapter-success")
        self.assertEqual(failure.action_id, "action:adapter-payment-without-delivery")

    def test_agent_adapter_demo_settles_success_and_failure(self):
        result = run_adapter_demo()
        self.assertEqual(result["schema"], "flowmemory.agent_adapter_demo.v0")
        self.assertEqual(len(result["settlements"]), 2)
        self.assertTrue(result["settlements"][0]["passed"])
        self.assertFalse(result["settlements"][1]["passed"])

    def test_adapter_conformance_demo_passes(self):
        result = run_adapter_conformance_demo()
        self.assertEqual(result["schema"], "flowmemory.adapter_conformance.v0")
        self.assertTrue(result["passed"])
        self.assertTrue(all(check["passed"] for check in result["checks"]))
        self.assertEqual(len(result["checks"]), 8)

    def test_agent_registry_matches_warranted_agent(self):
        result = run_registry_demo()
        self.assertEqual(result["schema"], "flowmemory.agent_registry_demo.v0")
        self.assertEqual(len(result["matches"]), 2)
        self.assertTrue(result["matches"][0]["eligible"])
        self.assertEqual(result["matches"][0]["warrantabilityScore"], 100)
        self.assertEqual(result["matches"][0]["reasons"], ["eligible_for_warranted_quote"])
        self.assertFalse(result["matches"][1]["eligible"])
        self.assertLess(result["matches"][1]["warrantabilityScore"], 100)
        self.assertIn("missing_required_evidence", result["matches"][1]["reasons"])

    def test_agent_runtime_runs_success_and_failure_histories(self):
        result = run_runtime_demo()
        self.assertEqual(result["schema"], "flowmemory.warranted_agent_runtime_demo.v0")
        self.assertEqual(result["summary"]["successFinalStatus"], "WARRANTY_RELEASED")
        self.assertEqual(result["summary"]["failureFinalStatus"], "USER_PAID_FROM_BOND")
        self.assertEqual(result["summary"]["timelineLength"], 7)
        self.assertEqual(result["runs"][0]["settlement"]["settlement"], "RELEASE_BOND_TO_AGENT")
        self.assertEqual(result["runs"][1]["settlement"]["settlement"], "PAY_BOND_TO_USER")
        self.assertTrue(all(event["eventHash"].startswith("sha256:") for event in result["runs"][0]["timeline"]))
        self.assertTrue(result["runs"][0]["stateMachine"]["terminal"])

    def test_runtime_state_machine_rejects_invalid_transition(self):
        machine = RuntimeStateMachine()
        with self.assertRaises(ValueError):
            machine.transition(
                ACTION_EXECUTED,
                phase="action_executed",
                status="OK",
                idempotency_key="run:test:bad",
                fields={},
            )

    def test_runtime_state_machine_rejects_replay_key(self):
        machine = RuntimeStateMachine()
        machine.transition(
            MANIFEST_LOADED,
            phase="manifest_loaded",
            status="OK",
            idempotency_key="run:test:manifest",
            fields={},
        )
        with self.assertRaises(ValueError):
            machine.transition(
                ACTION_EXECUTED,
                phase="action_executed",
                status="OK",
                idempotency_key="run:test:manifest",
                fields={},
            )

    def test_claim_gate_passes_public_copy(self):
        result = scan_claims(ROOT)
        self.assertTrue(result["filesChecked"] > 0)
        self.assertEqual(result["unguardedOverclaims"], [])
        self.assertTrue(result["passed"])


def _case(case_id):
    return next(case for case in CASES if case["caseId"] == case_id)


def _fault(result, fault_name):
    return next(fault for fault in result["faults"] if fault["fault"] == fault_name)


if __name__ == "__main__":
    unittest.main()
