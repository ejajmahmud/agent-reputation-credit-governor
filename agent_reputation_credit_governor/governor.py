"""Core Reputation Credit Governor implementation."""
import time
from typing import Dict, Optional, Any


class AgentAccount:
    def __init__(self, agent_id: str, initial_credits: float = 100.0, trust_score: float = 1.0):
        self.agent_id = agent_id
        self.credits = initial_credits
        self.max_credits = initial_credits
        self.trust_score = trust_score  # 0.0 to 1.0
        self.is_quarantined = False
        self.last_updated = time.time()
        self.total_actions = 0
        self.successful_actions = 0
        self.violations = 0


class ReputationCreditGovernor:
    def __init__(self, replenishment_rate_per_sec: float = 0.5, quarantine_threshold: float = 0.25):
        self.replenishment_rate = replenishment_rate_per_sec
        self.quarantine_threshold = quarantine_threshold
        self.accounts: Dict[str, AgentAccount] = {}

    def register_agent(self, agent_id: str, initial_credits: float = 100.0) -> AgentAccount:
        acc = AgentAccount(agent_id, initial_credits)
        self.accounts[agent_id] = acc
        return acc

    def update_credits(self, acc: AgentAccount):
        now = time.time()
        elapsed = now - acc.last_updated
        if elapsed > 0 and not acc.is_quarantined:
            acc.credits = min(acc.max_credits, acc.credits + (elapsed * self.replenishment_rate))
        acc.last_updated = now

    def request_permission(self, agent_id: str, cost: float) -> Tuple_Result:
        if agent_id not in self.accounts:
            return False, "Unregistered agent"
        acc = self.accounts[agent_id]
        self.update_credits(acc)

        if acc.is_quarantined:
            return False, "Agent is in quarantine"
        if acc.trust_score < self.quarantine_threshold:
            acc.is_quarantined = True
            return False, f"Trust score {acc.trust_score:.2f} fell below quarantine threshold"
        if acc.credits < cost:
            return False, f"Insufficient credits ({acc.credits:.1f} < {cost:.1f})"

        acc.credits -= cost
        acc.total_actions += 1
        return True, "Approved"

    def record_outcome(self, agent_id: str, success: bool, violation_severity: float = 0.0):
        if agent_id not in self.accounts:
            return
        acc = self.accounts[agent_id]
        if success:
            acc.successful_actions += 1
            # Boost trust slightly
            acc.trust_score = min(1.0, acc.trust_score + 0.05)
        else:
            if violation_severity > 0:
                acc.violations += 1
                # Slash penalty: reduce credits by severity fraction
                acc.credits = max(0.0, acc.credits * (1.0 - violation_severity))
                # Slash trust score
                acc.trust_score = max(0.0, acc.trust_score * (1.0 - violation_severity))
                if acc.trust_score < self.quarantine_threshold:
                    acc.is_quarantined = True


Tuple_Result = Any
