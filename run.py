#!/usr/bin/env python3
"""
AI Operations Partner Cockpit Unified CLI Runner.
Provides 1-click execution for server, tests, audits, and DDIA invariants.
"""

import sys
import os
import argparse
import subprocess

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def main():
    parser = argparse.ArgumentParser(description="⚡ AI Operations Partner Cockpit Unified Runner")
    parser.add_argument("--port", type=int, default=9000, help="Port to run cockpit server on")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")
    parser.add_argument("--audit", help="Audit target URL or local HTML file")
    parser.add_argument("--invariants", action="store_true", help="Run DDIA Invariant Watchdog")
    
    args = parser.parse_args()
    
    if args.test:
        test_file = os.path.join(BASE_DIR, "tests", "test_cockpit.py")
        e2e_file = os.path.join(BASE_DIR, "tests", "test_e2e_server.py")
        rc1 = subprocess.run([sys.executable, test_file]).returncode
        rc2 = subprocess.run([sys.executable, e2e_file]).returncode
        sys.exit(rc1 if rc1 != 0 else rc2)

        
    if args.invariants:
        from core.storage import BitcaskStorage
        from core.watchdog import InvariantWatchdog
        storage = BitcaskStorage(os.path.join(BASE_DIR, "data", "events.wal"))
        storage.seed_defaults_if_empty()
        clients = list(storage.get_all().values())
        report = InvariantWatchdog().verify_state(clients)
        print("=" * 75)
        print("🛡️ DDIA STATE CONSERVATION INVARIANT WATCHDOG PROBE")
        print("=" * 75)
        print(f"• Status: {'✓ HEALTHY' if report['healthy'] else '🚨 VIOLATIONS DETECTED'}")
        print(f"• Total Retainers in WAL: {report['totalClients']}")
        print(f"• Active Recurring MRR: ${report['activeMRR']:,}/month")
        print(f"• Breakdown: {report['statusBreakdown']}")
        if report['violations']:
            print(f"• Violations: {report['violations']}")
        return
        
    if args.audit:
        from core.auditor import ForensicAuditor
        auditor = ForensicAuditor()
        if args.audit.startswith("http://") or args.audit.startswith("https://"):
            res = auditor.audit_url(args.audit)
        else:
            local_path = os.path.join(BASE_DIR, args.audit)
            if not os.path.exists(local_path):
                local_path = args.audit
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            res = auditor.audit_html(html, target_url=args.audit)
            
        print("=" * 75)
        print("🔍 INSTANT FORENSIC AUDIT RESULT")
        print("=" * 75)
        print(f"Target: {res['targetUrl']} | Score: {res['score']}/100")
        print(f"H1: {res['h1Headline']}")
        print(f"Mobile Viewport: {'✓ Ready' if res['mobileReady'] else '❌ Failed'}")
        print(f"WhatsApp Button: {'✓ Detected' if res['whatsappDetected'] else '❌ Missing'}")
        print("\nFindings:")
        for f in res['findings']:
            print(f"  • {f}")
        return

    # Default: launch server
    from server import run_server
    run_server(args.port)

if __name__ == "__main__":
    main()
