"""Unit tests for agent-reputation-credit-governor."""
import unittest
from agent_reputation_credit_governor.governor import ReputationCreditGovernor


class TestReputationCreditGovernor(unittest.TestCase):
    def setUp(self):
        self.gov = ReputationCreditGovernor(quarantine_threshold=0.3)
        self.acc = self.gov.register_agent("test_agent", initial_credits=100.0)

    def test_permission_and_deduction(self):
        ok, _ = self.gov.request_permission("test_agent", 40.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(self.acc.credits, 60.0, places=1)

    def test_insufficient_credits(self):
        ok, _ = self.gov.request_permission("test_agent", 150.0)
        self.assertFalse(ok)

    def test_slash_and_quarantine(self):
        self.gov.record_outcome("test_agent", success=False, violation_severity=1.0)
        self.assertTrue(self.acc.is_quarantined)
        ok, msg = self.gov.request_permission("test_agent", 5.0)
        self.assertFalse(ok)
        self.assertIn("quarantine", msg)
