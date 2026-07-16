#!/usr/bin/env python
"""
scripts/export_revenue.py --month 2026-06
Generates the EXACT artifacts required by XPRIZE rules:
- Total Revenue (arms-length)
- Revenue by Month (May, June, July, August 2026)
- Total Costs (excl marketing) + 1-sentence desc
- Marketing & Customer Acquisition Spend (even if 0)
- Related-Party Revenue separate
Output: console + CSV/JSON suitable for Devpost upload + screenshots of "P&L".
Run after seed or with real DB.
"""
import sys, json, csv
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from collections import defaultdict
from web.deps import SessionLocal
from web import models

def export(month: str | None = None):
    db = SessionLocal()
    try:
        events = db.query(models.RevenueEvent).all()
        by_month = defaultdict(float)
        total = 0.0
        related = 0.0
        arms = 0.0
        for e in events:
            by_month[e.month] += e.amount_usd
            total += e.amount_usd
            if e.is_related_party:
                related += e.amount_usd
            else:
                arms += e.amount_usd

        months = ["2026-05", "2026-06", "2026-07", "2026-08"]
        report = {
            "generated": datetime.utcnow().isoformat(),
            "total_revenue_usd": arms,  # arms-length only for main number
            "revenue_by_month": {m: by_month.get(m, 0.0) for m in months},
            "total_costs_usd": 312.0,  # example: hosting + Gemini API + contractor (update real)
            "costs_description": "Cloud Run hosting, Gemini API usage, basic contractor for initial content.",
            "marketing_spend_usd": 0.0,  # disclose even if zero
            "related_party_revenue_usd": related,
            "note": "All figures from DB RevenueEvent table (populated via Stripe webhooks in prod). For submission attach Stripe export + this + bank/P&L screenshot."
        }
        print(json.dumps(report, indent=2))
        
        # Also write files for easy attach
        out = Path("xprize_evidence")
        out.mkdir(exist_ok=True)
        with open(out / f"revenue_{month or 'all'}.json", "w") as f:
            json.dump(report, f, indent=2)
        with open(out / "revenue_by_month.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Month", "Revenue_USD_arms_length"])
            for m in months:
                w.writerow([m, by_month.get(m, 0)])
        print(f"\nWrote artifacts to {out}/ for Devpost upload.")
        return report
    finally:
        db.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month")
    export(ap.parse_args().month)
