#!/usr/bin/env python3
"""
Zero-Dependency Hostable HTTP Server & REST API for AI Operations Cockpit.
Martin Kleppmann DDIA Compliant.
Serves the cybernetic glassmorphic frontend and provides full REST endpoints.
Zero external libraries.
"""

import sys
import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.storage import BitcaskStorage
from core.auditor import ForensicAuditor
from core.trojan_pitcher import TrojanPitcher
from core.watchdog import InvariantWatchdog

WAL_PATH = os.path.join(BASE_DIR, "data", "events.wal")
storage = BitcaskStorage(WAL_PATH)
auditor = ForensicAuditor()
pitcher = TrojanPitcher()
watchdog = InvariantWatchdog()

storage.seed_defaults_if_empty()


class CockpitHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            web_file = os.path.join(BASE_DIR, "web", "index.html")
            if os.path.exists(web_file):
                with open(web_file, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Web dashboard file not found")
            return

        elif path == "/health":
            all_clients = list(storage.get_all().values())
            audit = watchdog.verify_state(all_clients)
            self._send_json({
                "status": "ok",
                "version": "1.0.0",
                "timestamp": time.time(),
                "invariants": "HEALTHY" if audit["healthy"] else "DEGRADED",
                "activeMRR": audit["activeMRR"]
            })
            return

        elif path == "/api/clients":
            clients = list(storage.get_all().values())
            self._send_json({"clients": clients, "total": len(clients)})
            return

        elif path == "/api/invariants":
            all_clients = list(storage.get_all().values())
            report = watchdog.verify_state(all_clients)
            self._send_json(report)
            return

        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        
        try:
            body = json.loads(post_data)
        except Exception:
            body = {}

        if path == "/api/audit":
            target = body.get("target", "").strip()
            if not target:
                self._send_json({"error": "Missing target URL or HTML parameter"}, 400)
                return
            
            if target.startswith("http://") or target.startswith("https://"):
                report = auditor.audit_url(target)
            else:
                report = auditor.audit_html(target, target_url="Raw Input")
            
            self._send_json(report)
            return

        elif path == "/api/pitch":
            bname = body.get("businessName", "Local Business")
            cat = body.get("category", "E-Commerce")
            city = body.get("city", "Riyadh")
            market = body.get("market", "KSA")
            score = int(body.get("auditScore", 70))
            phone = body.get("phone", "")

            pitch = pitcher.generate_pitch(bname, cat, city, market, score, phone)
            self._send_json(pitch)
            return

        elif path == "/api/clients":
            client_id = body.get("id") or f"client_{int(time.time()*1000)}"
            body["id"] = client_id
            storage.put(client_id, body)
            self._send_json({"message": "Client saved successfully", "client": body}, 201)
            return

        else:
            self.send_error(404, "Endpoint Not Found")

def run_server(port: int = 9000):
    server = HTTPServer(("0.0.0.0", port), CockpitHandler)
    print("=" * 75)
    print("🚀 AI OPERATIONS PARTNER COCKPIT (DDIA HOSTABLE SERVER)")
    print(f"Local Cockpit Dashboard: http://localhost:{port}")
    print(f"REST Endpoints Active: /health, /api/audit, /api/pitch, /api/clients, /api/invariants")
    print(f"Bitcask WAL Storage: {WAL_PATH}")
    print("=" * 75)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly.")
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    run_server(port)
