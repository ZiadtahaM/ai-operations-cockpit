#!/usr/bin/env python3
"""
Bitcask Append-Only Storage Engine.
Martin Kleppmann DDIA Chapter 3 Compliant.
Features:
- Append-only write-ahead log (WAL)
- In-memory hash index (keydir) for O(1) reads
- CRC32 data integrity checks
- Crash recovery on initialization
Zero external dependencies.
"""

import os
import sys
import json
import time
import struct
import zlib
from typing import Dict, Any, Optional, List, Tuple

# Binary Record Header Format:
# CRC32 (4 bytes unsigned int) + Timestamp (8 bytes double) + KeyLen (4 bytes uint) + ValLen (4 bytes uint)
HEADER_FORMAT = "<IdII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

class BitcaskStorage:
    def __init__(self, wal_path: str):
        self.wal_path = wal_path
        os.makedirs(os.path.dirname(os.path.abspath(self.wal_path)), exist_ok=True)
        # in-memory keydir: key -> (offset, val_size, timestamp)
        self.keydir: Dict[str, Tuple[int, int, float]] = {}
        self._rebuild_keydir()

    def _rebuild_keydir(self):
        """Rebuilds the in-memory keydir index from the append-only log upon startup."""
        if not os.path.exists(self.wal_path):
            return

        with open(self.wal_path, "rb") as f:
            offset = 0
            while True:
                header_bytes = f.read(HEADER_SIZE)
                if not header_bytes or len(header_bytes) < HEADER_SIZE:
                    break

                crc, ts, key_len, val_len = struct.unpack(HEADER_FORMAT, header_bytes)
                data_bytes = f.read(key_len + val_len)
                if len(data_bytes) < (key_len + val_len):
                    break  # Truncated write at end of log

                # Verify checksum
                actual_crc = zlib.crc32(data_bytes) & 0xffffffff
                if crc != actual_crc:
                    break  # Corrupted record, stop recovery

                key = data_bytes[:key_len].decode("utf-8")
                # Record in keydir: points directly to where value bytes begin
                val_offset = offset + HEADER_SIZE + key_len
                self.keydir[key] = (val_offset, val_len, ts)
                offset += HEADER_SIZE + key_len + val_len

    def put(self, key: str, value: Any) -> bool:
        """Appends a key-value record to the end of the log and updates the in-memory index."""
        key_bytes = key.encode("utf-8")
        val_bytes = json.dumps(value, ensure_ascii=False).encode("utf-8")
        ts = time.time()
        
        key_len = len(key_bytes)
        val_len = len(val_bytes)
        payload = key_bytes + val_bytes
        crc = zlib.crc32(payload) & 0xffffffff
        header = struct.pack(HEADER_FORMAT, crc, ts, key_len, val_len)

        with open(self.wal_path, "ab") as f:
            f.seek(0, os.SEEK_END)
            current_offset = f.tell()
            f.write(header + payload)
            f.flush()

        val_offset = current_offset + HEADER_SIZE + key_len
        self.keydir[key] = (val_offset, val_len, ts)
        return True

    def get(self, key: str) -> Optional[Any]:
        """O(1) read from log using the in-memory keydir offset."""
        if key not in self.keydir:
            return None

        val_offset, val_len, _ = self.keydir[key]
        if not os.path.exists(self.wal_path):
            return None

        with open(self.wal_path, "rb") as f:
            f.seek(val_offset)
            val_bytes = f.read(val_len)
            try:
                return json.loads(val_bytes.decode("utf-8"))
            except Exception:
                return None

    def list_keys(self) -> List[str]:
        return list(self.keydir.keys())

    def get_all(self) -> Dict[str, Any]:
        result = {}
        for k in self.list_keys():
            v = self.get(k)
            if v is not None:
                result[k] = v
        return result

    def seed_defaults_if_empty(self):
        """Seeds demo retainers if the storage WAL is empty."""
        if not self.list_keys():
            self.put("client_001", {
                "id": "client_001",
                "businessName": "Al-Boutique Abayas Riyadh",
                "category": "E-Commerce Luxury",
                "market": "KSA",
                "city": "Riyadh",
                "phone": "+966501234567",
                "status": "ACTIVE",
                "mrr": 1200,
                "workflows": ["WhatsApp Abandoned Cart", "24/7 VIP Concierge"],
                "apiUptime": "99.98%",
                "lastAuditScore": 88
            })
            self.put("client_002", {
                "id": "client_002",
                "businessName": "Dr. Nour Aesthetic Clinic",
                "category": "Medical & Aesthetics",
                "market": "KSA",
                "city": "Jeddah",
                "phone": "+966549876543",
                "status": "ONBOARDING",
                "mrr": 850,
                "workflows": ["24/7 Appointment Booking"],
                "apiUptime": "100.0%",
                "lastAuditScore": 65
            })

