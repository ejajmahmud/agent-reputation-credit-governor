"""CLI for agent-reputation-credit-governor."""
import sys
import argparse
from .governor import ReputationCreditGovernor


def main():
    parser = argparse.ArgumentParser(description="Agent Reputation Credit Governor CLI")
    parser.add_argument("--demo", action="store_true", help="Run credit governor and slash demonstration")
    args = parser.parse_args()

    if args.demo:
        gov = ReputationCreditGovernor()
        acc = gov.register_agent("worker_alpha", initial_credits=50.0)

        ok, msg = gov.request_permission("worker_alpha", cost=20.0)
        print(f"Action 1 Request: Allowed={ok} ({msg}) | Credits Remaining: {acc.credits:.1f}")

        # Record a severe violation
        print("Recording security violation (severity 0.8)...")
        gov.record_outcome("worker_alpha", success=False, violation_severity=0.8)
        print(f"Post-Violation: Credits={acc.credits:.1f} | Trust={acc.trust_score:.2f} | Quarantined={acc.is_quarantined}")

        ok2, msg2 = gov.request_permission("worker_alpha", cost=5.0)
        print(f"Action 2 Request: Allowed={ok2} ({msg2})")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
