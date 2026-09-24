#!/usr/bin/env python3
"""
Trojan Horse Pitch & Offer Engine.
Generates 2-step high-converting B2B outreach:
Step 1: Front-end acute pain fix ($400-$700 one-off)
Step 2: Monthly AI Operations Retainer ($500-$1,500/mo)
Contextualized for GCC (SAR/AED) and international markets.
Pure Python standard library.
"""

import urllib.parse
from typing import Dict, Any, Optional

class TrojanPitcher:
    def generate_pitch(
        self,
        business_name: str,
        category: str,
        city: str,
        market: str = "KSA",
        audit_score: int = 70,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        market_upper = market.upper()
        
        # Pricing Tier Configuration based on market purchasing power
        if market_upper in ["KSA", "UAE", "GCC"]:
            currency = "SAR"
            front_end_price = "1,800 SAR (~$480)"
            retainer_price = "2,500 - 4,500 SAR/month (~$650 - $1,200/mo)"
            recommended_tier = "SILVER"
        elif market_upper == "EGY":
            currency = "EGP"
            front_end_price = "18,000 EGP (~$370)"
            retainer_price = "25,000 - 45,000 EGP/month (~$500 - $900/mo)"
            recommended_tier = "BRONZE"
        else:
            currency = "USD"
            front_end_price = "$500"
            retainer_price = "$800 - $1,500/month"
            recommended_tier = "SILVER"

        # Step 1: Front-End Acute Offer
        front_end_offer = (
            f"Automated WhatsApp VIP Re-Engagement & Abandoned Cart Recovery Engine for {business_name} "
            f"({front_end_price} setup). Recovers 12-18% of dropped checkouts within 14 days with zero staff effort."
        )

        # Step 2: Monthly Operations Retainer
        retainer_offer = (
            f"Dedicated AI Operations Retainer ({retainer_price}). "
            f"Includes 24/7 API uptime monitoring, monthly prompt & catalog iteration, "
            f"and active triage for up to 3 custom business workflows."
        )

        # Non-Templated 3-Sentence Cold Email
        email_subject = f"Quick question regarding {business_name} mobile checkout in {city}"
        email_body = (
            f"Assalamu Alaikum,\n\n"
            f"I came across {business_name} while researching top {category} businesses in {city} and ran a quick 60-second mobile forensic check.\n\n"
            f"I noticed a specific checkout friction point (Audit Score: {audit_score}/100) where mobile visitors drop off before completing their purchase.\n\n"
            f"We built an automated WhatsApp recovery workflow tailored for {business_name} that re-engages these customers within 15 minutes—would it be okay if I send over a 60-second video showing how it works? Zero obligation.\n\n"
            f"Best regards,\n[Your Name]\nAI Operations Partner"
        )

        # Arabic WhatsApp Direct Pitch
        wa_text = (
            f"السلام عليكم أستاذ، شفت شغلكم المميز في {business_name} فـ {city}.\n"
            f"سويت فحص فني سريع للمتجر، ولاحظت نقطة احتكاك في مسار الطلب على الجوال بتضيع عليكم طلبات مؤكدة.\n\n"
            f"قاديت لكم نموذج تجريبي يربط السلات المتروكة مع الواتساب آلياً بدون أي مجهود من موظفيكم.\n"
            f"ممكن أرسل لك رابط المعاينة السريع تشوفه بنفسك؟ (مجاناً وبلا أي التزام)"
        )

        clean_phone = (phone or "").replace("+", "").replace(" ", "").replace("-", "")
        wa_encoded = urllib.parse.quote(wa_text)
        wa_url = f"https://wa.me/{clean_phone}?text={wa_encoded}" if clean_phone else f"https://wa.me/?text={wa_encoded}"

        return {
            "businessName": business_name,
            "category": category,
            "city": city,
            "market": market_upper,
            "currency": currency,
            "recommendedTier": recommended_tier,
            "frontEndOffer": front_end_offer,
            "monthlyRetainerOffer": retainer_offer,
            "retainerPricing": retainer_price,
            "threeSentenceEmail": email_body,
            "emailSubject": email_subject,
            "whatsappText": wa_text,
            "whatsappUrl": wa_url
        }
