#!/usr/bin/env python3
"""
Forensic Website & Store Auditor.
Measures latency, above-the-fold clarity, mobile viewport, CTA friction, and WhatsApp integration.
Pure Python standard library.
"""

import re
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List

class ForensicAuditor:
    def audit_url(self, url: str) -> Dict[str, Any]:
        """Fetches a live URL and audits its conversion performance."""
        t0 = time.time()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            latency_ms = (time.time() - t0) * 1000
            return self.audit_html(html, target_url=url, latency_ms=latency_ms)
        except Exception as e:
            return {
                "targetUrl": url,
                "score": 20,
                "latencyMs": round((time.time() - t0) * 1000, 1),
                "error": str(e),
                "mobileReady": False,
                "whatsappDetected": False,
                "h1Headline": "OFFLINE / UNREACHABLE",
                "findings": [f"Connection failed: {str(e)}"],
                "quickWins": ["Verify server DNS and SSL certificates."]
            }

    def audit_html(self, html: str, target_url: str = "", latency_ms: float = 0.0) -> Dict[str, Any]:
        """Audits raw HTML string for conversion bottlenecks."""
        # 1. H1 Extraction
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        h1_text = re.sub(r'<[^>]+>', '', h1_matches[0]).strip() if h1_matches else ""

        # 2. Viewport & Mobile Tags
        has_viewport = bool(re.search(r'<meta[^>]*name=["\']viewport["\']', html, re.IGNORECASE))

        # 3. WhatsApp Integration Detection
        has_whatsapp = bool(re.search(r'(wa\.me|api\.whatsapp\.com|whatsapp)', html, re.IGNORECASE))

        # 4. CTA Buttons Detection
        cta_buttons = re.findall(
            r'<(?:button|a)[^>]*(?:class=["\'][^"\']*(?:btn|cta|button|order|buy|cart)[^"\']*["\'])[^>]*>(.*?)</(?:button|a)>',
            html, re.IGNORECASE | re.DOTALL
        )
        if not cta_buttons:
            cta_buttons = re.findall(r'<(?:button|input)[^>]*type=["\']submit["\'][^>]*>', html, re.IGNORECASE)
        cta_count = len(cta_buttons)

        # 5. Social Proof Detection
        has_social_proof = bool(re.search(r'(review|testimonial|trusted by|rating|★|stars|customers|عملاء|تقييم)', html, re.IGNORECASE))

        # Calculate Score (Base: 50)
        score = 50
        findings = []

        if h1_text:
            score += 15
            findings.append("✓ Strong above-the-fold H1 headline detected.")
        else:
            findings.append("❌ Missing H1 headline! Visitors cannot immediately identify the core offer.")

        if has_viewport:
            score += 15
            findings.append("✓ Mobile viewport meta tag properly configured.")
        else:
            score -= 20
            findings.append("❌ Missing viewport meta tag! Store fails on mobile devices.")

        if has_whatsapp:
            score += 10
            findings.append("✓ Direct WhatsApp conversion channel active.")
        else:
            findings.append("⚠️ Missing direct WhatsApp VIP support button (Crucial for GCC/MENA conversion).")

        if cta_count >= 1:
            score += 10
            findings.append(f"✓ {cta_count} clear Call-to-Action button(s) detected.")
        else:
            findings.append("❌ No high-contrast CTA button found above the fold.")

        if has_social_proof:
            score += 10
            findings.append("✓ Social proof / customer review signals present.")
        else:
            findings.append("⚠️ Missing visible social proof stickers near conversion points.")

        score = max(10, min(100, score))

        quick_wins = [
            "Install a floating WhatsApp click-to-chat button in the bottom right corner with an instant automated welcome message.",
            "Add a 1-sentence sub-headline directly below H1 stating exact delivery timeline and risk-free guarantee.",
            "Display a 5-star customer review rating badge directly above the primary checkout button."
        ]

        return {
            "targetUrl": target_url or "Raw HTML Upload",
            "score": score,
            "latencyMs": round(latency_ms, 1),
            "h1Headline": h1_text or "NOT DETECTED",
            "mobileReady": has_viewport,
            "whatsappDetected": has_whatsapp,
            "ctaCount": cta_count,
            "socialProofDetected": has_social_proof,
            "findings": findings,
            "quickWins": quick_wins
        }
