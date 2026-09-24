#!/usr/bin/env python3
"""
Contract and Integration Tests for AI Operations Partner Cockpit.
Pure Python standard library (unittest). Zero external dependencies.
Tests storage, forensic auditor, pitch engine, and DDIA invariants.
"""

import sys
import os
import unittest
import tempfile
import json
import shutil

# Windows UTF-8 console output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

class TestStorageEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.wal_path = os.path.join(self.temp_dir, "test_events.wal")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_bitcask_put_and_get(self):
        from core.storage import BitcaskStorage
        storage = BitcaskStorage(self.wal_path)
        storage.put("client_101", {"name": "Abaya Boutique", "mrr": 500, "status": "ACTIVE"})
        
        record = storage.get("client_101")
        self.assertIsNotNone(record)
        self.assertEqual(record["name"], "Abaya Boutique")
        self.assertEqual(record["mrr"], 500)
        self.assertEqual(record["status"], "ACTIVE")

    def test_bitcask_crash_recovery_rebuilds_keydir(self):
        from core.storage import BitcaskStorage
        storage1 = BitcaskStorage(self.wal_path)
        storage1.put("client_A", {"status": "LEAD"})
        storage1.put("client_A", {"status": "ACTIVE"})  # Overwrite
        storage1.put("client_B", {"status": "CHURNED"})

        # Reopen storage without in-memory state, recovering from WAL
        storage2 = BitcaskStorage(self.wal_path)
        rec_a = storage2.get("client_A")
        rec_b = storage2.get("client_B")
        
        self.assertEqual(rec_a["status"], "ACTIVE")
        self.assertEqual(rec_b["status"], "CHURNED")
        self.assertEqual(len(storage2.list_keys()), 2)

class TestForensicAuditor(unittest.TestCase):
    def test_auditor_scores_healthy_page(self):
        from core.auditor import ForensicAuditor
        auditor = ForensicAuditor()
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Store</title></head>
        <body>
            <h1>Luxury Abayas & Perfumes</h1>
            <p>Rated 4.9 stars by 1,200+ verified customers</p>
            <a href="/checkout" class="btn-primary">Shop Now</a>
            <a href="https://wa.me/966500000000" class="whatsapp-btn">WhatsApp Support</a>
        </body>
        </html>
        """
        report = auditor.audit_html(html, target_url="https://test-store.sa")
        self.assertGreaterEqual(report["score"], 80)
        self.assertTrue(report["mobileReady"])
        self.assertTrue(report["whatsappDetected"])
        self.assertEqual(report["h1Headline"], "Luxury Abayas & Perfumes")

    def test_auditor_penalizes_broken_mobile_experience(self):
        from core.auditor import ForensicAuditor
        auditor = ForensicAuditor()
        broken_html = "<html><body><div>Just some text without tags or CTAs</div></body></html>"
        report = auditor.audit_html(broken_html, target_url="https://broken-store.com")
        self.assertLess(report["score"], 60)
        self.assertFalse(report["mobileReady"])
        self.assertFalse(report["whatsappDetected"])

class TestTrojanPitcher(unittest.TestCase):
    def test_pitch_generation_for_ksa_market(self):
        from core.trojan_pitcher import TrojanPitcher
        pitcher = TrojanPitcher()
        pitch = pitcher.generate_pitch(
            business_name="Al-Rehab Dental Clinic",
            category="Medical Clinic",
            city="Riyadh",
            market="KSA",
            audit_score=55,
            phone="+966512345678"
        )
        self.assertIn("Riyadh", pitch["whatsappText"])
        self.assertIn("wa.me", pitch["whatsappUrl"])
        self.assertIn("SAR", pitch["retainerPricing"])
        self.assertEqual(pitch["recommendedTier"], "SILVER")

    def test_pitch_generates_two_step_trojan_horse(self):
        from core.trojan_pitcher import TrojanPitcher
        pitcher = TrojanPitcher()
        pitch = pitcher.generate_pitch(
            business_name="Cairo Fashion Hub",
            category="E-commerce",
            city="Cairo",
            market="EGY",
            audit_score=60
        )
        self.assertIn("frontEndOffer", pitch)
        self.assertIn("monthlyRetainerOffer", pitch)
        self.assertGreater(len(pitch["threeSentenceEmail"]), 30)

class TestDDIAInvariantWatchdog(unittest.TestCase):
    def test_watchdog_verifies_state_conservation(self):
        from core.watchdog import InvariantWatchdog
        watchdog = InvariantWatchdog()
        clients = [
            {"id": "1", "status": "LEAD", "mrr": 0},
            {"id": "2", "status": "ONBOARDING", "mrr": 500},
            {"id": "3", "status": "ACTIVE", "mrr": 1500},
            {"id": "4", "status": "CHURNED", "mrr": 0}
        ]
        result = watchdog.verify_state(clients)
        self.assertTrue(result["healthy"])
        self.assertEqual(result["totalClients"], 4)
        self.assertEqual(result["activeMRR"], 2000)

    def test_watchdog_catches_invalid_status_transition(self):
        from core.watchdog import InvariantWatchdog
        watchdog = InvariantWatchdog()
        clients = [
            {"id": "1", "status": "INVALID_ZOMBIE_STATE", "mrr": 100}
        ]
        result = watchdog.verify_state(clients)
        self.assertFalse(result["healthy"])
        self.assertGreater(len(result["violations"]), 0)

if __name__ == "__main__":
    unittest.main()
