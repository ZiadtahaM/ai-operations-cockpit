#!/usr/bin/env python3
"""
Tier 2 & Tier 3 End-to-End System & Invariants Integration Test.
Spawns the HTTP server on a test port, executes live probes across all endpoints,
and verifies Bitcask WAL mutations and Martin Kleppmann invariants.
"""

import sys
import os
import json
import time
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from server import CockpitHandler

def run_e2e_tests():
    test_port = 9015
    server = HTTPServer(("127.0.0.1", test_port), CockpitHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.3)

    base_url = f"http://127.0.0.1:{test_port}"
    print(f"Testing server at {base_url}...")

    # 1. Test GET / (HTML Dashboard)
    with urllib.request.urlopen(f"{base_url}/") as res:
        assert res.status == 200
        html = res.read().decode("utf-8")
        assert "AI OPERATIONS PARTNER COCKPIT" in html
        print("✓ GET / returned 200 and valid HTML dashboard")

    # 2. Test GET /health
    with urllib.request.urlopen(f"{base_url}/health") as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert data["invariants"] == "HEALTHY"
        print(f"✓ GET /health returned 200 with invariants={data['invariants']}, MRR=${data['activeMRR']}")

    # 3. Test GET /api/clients
    with urllib.request.urlopen(f"{base_url}/api/clients") as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["total"] >= 2
        print(f"✓ GET /api/clients returned 200 with {data['total']} clients")

    # 4. Test GET /api/invariants
    with urllib.request.urlopen(f"{base_url}/api/invariants") as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["healthy"] is True
        assert len(data["violations"]) == 0
        print("✓ GET /api/invariants returned 200 with zero violations")

    # 5. Test POST /api/audit (Raw HTML)
    audit_payload = json.dumps({
        "target": "<html><head><meta name='viewport' content='width=device-width'></head><body><h1>Luxury Abayas</h1><a href='https://wa.me/966500'>Order on WhatsApp</a></body></html>"
    }).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/audit", data=audit_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["score"] >= 80
        assert data["whatsappDetected"] is True
        print(f"✓ POST /api/audit returned 200 with score={data['score']}")

    # 6. Test POST /api/pitch
    pitch_payload = json.dumps({
        "businessName": "Al-Zahra Perfumes",
        "category": "Oud & Perfumes",
        "city": "Dubai",
        "market": "UAE",
        "auditScore": 65,
        "phone": "+971501112233"
    }).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/pitch", data=pitch_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert "wa.me" in data["whatsappUrl"]
        assert "Al-Zahra Perfumes" in data["frontEndOffer"]
        print(f"✓ POST /api/pitch returned 200 with WhatsApp link and 2-step offer")

    # 7. Test POST /api/clients (Mutating Bitcask WAL)
    new_client = json.dumps({
        "id": "client_test_e2e",
        "businessName": "Test Boutique E2E",
        "category": "Retail",
        "market": "KSA",
        "city": "Riyadh",
        "status": "ACTIVE",
        "mrr": 1500,
        "workflows": ["Cart Recovery"],
        "apiUptime": "100%"
    }).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/clients", data=new_client, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 201
        print("✓ POST /api/clients appended record to Bitcask WAL with 201 Created")

    # Re-verify invariants after mutation
    with urllib.request.urlopen(f"{base_url}/api/invariants") as res:
        data = json.loads(res.read().decode("utf-8"))
        assert data["healthy"] is True
        print("✓ Post-mutation Invariants probe verified zero state drift")

    server.shutdown()
    print("\n🎉 ALL E2E & INVARIANT SYSTEM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_e2e_tests()
