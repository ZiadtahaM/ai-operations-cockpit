#!/usr/bin/env python3
"""
DDIA Invariant Watchdog.
Martin Kleppmann DDIA Chapter 1 (Reliability & Noether State Conservation).
Enforces:
- State conservation: sum(status counts) == total records
- Legal status enum: LEAD, ONBOARDING, ACTIVE, CHURNED
- Active MRR conservation
Zero external dependencies.
"""

from typing import List, Dict, Any

LEGAL_STATUSES = {"LEAD", "ONBOARDING", "ACTIVE", "CHURNED"}

class InvariantWatchdog:
    def verify_state(self, clients: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_clients = len(clients)
        status_counts = {"LEAD": 0, "ONBOARDING": 0, "ACTIVE": 0, "CHURNED": 0}
        violations = []
        active_mrr = 0

        for client in clients:
            status = client.get("status", "")
            if status not in LEGAL_STATUSES:
                violations.append(f"Illegal client status '{status}' for client id '{client.get('id')}'. Legal: {LEGAL_STATUSES}")
            else:
                status_counts[status] += 1
                if status in {"ONBOARDING", "ACTIVE"}:
                    active_mrr += int(client.get("mrr", 0))

        # Check conservation: sum of legal statuses must equal total clients
        sum_statuses = sum(status_counts.values())
        if sum_statuses != total_clients:
            violations.append(f"Conservation Invariant Violated: sum(statuses)={sum_statuses} != total_clients={total_clients}")

        is_healthy = (len(violations) == 0)

        return {
            "healthy": is_healthy,
            "totalClients": total_clients,
            "activeMRR": active_mrr,
            "statusBreakdown": status_counts,
            "violations": violations
        }
