#!/usr/bin/env python3
"""
MSME AI Cash Flow Forecaster - Starter Demo
============================================

Practical cash flow analysis and working capital estimation tool
for Indian Micro, Small and Medium Enterprises (MSMEs).

Features demonstrated:
- Sample invoices, UPI transactions, and expenses (Indian context)
- Net cash position calculation
- 30/60/90-day cash flow projection
- Working capital gap estimation
- GST input credit tracking reminder
- Financing recommendations (invoice discounting candidates)

No external dependencies required.
Run with: python cashflow_forecaster.py
"""

from datetime import datetime, timedelta
from collections import defaultdict
import json

# ---------------------------------------------------------------------------
# Sample Data — Indian MSME context (amounts in INR)
# ---------------------------------------------------------------------------

# Outstanding invoices (receivables)
INVOICES = [
    {"id": "INV-2026-001", "customer": "Reliance Retail", "amount": 285000, "due_date": "2026-12-05", "gst_rate": 18, "status": "pending"},
    {"id": "INV-2026-002", "customer": "Tata Motors Supplier", "amount": 142000, "due_date": "2026-11-28", "gst_rate": 18, "status": "pending"},
    {"id": "INV-2026-003", "customer": "Local Distributor", "amount": 67500, "due_date": "2026-12-15", "gst_rate": 5, "status": "pending"},
    {"id": "INV-2026-004", "customer": "Amazon Seller Central", "amount": 198000, "due_date": "2026-11-20", "gst_rate": 18, "status": "overdue"},
]

# Recent UPI / bank inflows and outflows
TRANSACTIONS = [
    {"date": "2026-11-01", "type": "inflow", "desc": "UPI from customer", "amount": 45000},
    {"date": "2026-11-05", "type": "outflow", "desc": "Raw material purchase", "amount": 82000},
    {"date": "2026-11-08", "type": "inflow", "desc": "UPI payment received", "amount": 32000},
    {"date": "2026-11-10", "type": "outflow", "desc": "Electricity + rent", "amount": 18500},
    {"date": "2026-11-10", "type": "outflow", "desc": "GST payment", "amount": 24000},
]

# Fixed monthly expenses (approx)
MONTHLY_EXPENSES = 95000  # rent, salaries, utilities, etc.

# Current bank balance
CURRENT_BALANCE = 186500

# ---------------------------------------------------------------------------
# Core Logic
# ---------------------------------------------------------------------------

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def calculate_cash_position():
    """Calculate current net cash and pending receivables."""
    total_receivables = sum(inv["amount"] for inv in INVOICES if inv["status"] in ["pending", "overdue"])
    overdue = sum(inv["amount"] for inv in INVOICES if inv["status"] == "overdue")
    
    net_recent = sum(
        t["amount"] if t["type"] == "inflow" else -t["amount"]
        for t in TRANSACTIONS
    )
    
    return {
        "current_balance": CURRENT_BALANCE,
        "total_pending_receivables": total_receivables,
        "overdue_amount": overdue,
        "recent_net_cashflow": net_recent,
    }

def project_cashflow(days=90):
    """Simple projection: assume receivables collected on due date, monthly expenses pro-rated."""
    today = datetime(2026, 11, 11)  # fixed demo date
    end_date = today + timedelta(days=days)
    
    daily_expense = MONTHLY_EXPENSES / 30
    projections = []
    running_balance = CURRENT_BALANCE
    
    for i in range(days + 1):
        current_day = today + timedelta(days=i)
        day_inflows = 0
        day_outflows = daily_expense
        
        # Collect invoices due on this day
        for inv in INVOICES:
            if parse_date(inv["due_date"]) == current_day and inv["status"] != "paid":
                day_inflows += inv["amount"]
        
        running_balance += day_inflows - day_outflows
        projections.append({
            "date": current_day.strftime("%Y-%m-%d"),
            "inflows": day_inflows,
            "outflows": round(day_outflows, 2),
            "balance": round(running_balance, 2),
        })
    
    return projections

def estimate_working_capital(projections):
    """Estimate shortfall over next 30/60/90 days."""
    periods = [30, 60, 90]
    results = {}
    
    for p in periods:
        min_balance = min(p["balance"] for p in projections[:p+1])
        shortfall = max(0, -min_balance)
        results[f"{p}_days"] = {
            "lowest_projected_balance": min_balance,
            "estimated_working_capital_need": round(shortfall, 2),
            "recommendation": "Consider invoice discounting" if shortfall > 0 else "Healthy position"
        }
    return results

def gst_notes():
    """Basic GST input credit and compliance reminders."""
    total_gst_on_invoices = sum(inv["amount"] * inv["gst_rate"] / 100 for inv in INVOICES)
    return {
        "total_output_gst_on_pending_invoices": round(total_gst_on_invoices, 2),
        "reminder": "Ensure all purchase invoices are recorded for ITC. File GSTR-1 and GSTR-3B on time to avoid interest."
    }

def financing_candidates():
    """Invoices suitable for early financing (invoice discounting / factoring)."""
    candidates = [
        inv for inv in INVOICES
        if inv["status"] in ["pending", "overdue"] and inv["amount"] >= 50000
    ]
    candidates.sort(key=lambda x: x["amount"], reverse=True)
    return candidates

# ---------------------------------------------------------------------------
# Main Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("MSME AI CASH FLOW FORECASTER  |  Demo for Indian MSMEs")
    print("Date: 11 November 2026")
    print("=" * 70)
    
    # Current position
    position = calculate_cash_position()
    print("\n📊 CURRENT CASH POSITION")
    print(f"  Bank Balance          : ₹{position['current_balance']:,.0f}")
    print(f"  Pending Receivables   : ₹{position['total_pending_receivables']:,.0f}")
    print(f"  Overdue Amount        : ₹{position['overdue_amount']:,.0f}")
    print(f"  Recent Net Cash Flow  : ₹{position['recent_net_cashflow']:,.0f}")
    
    # Projections
    projections = project_cashflow(90)
    print("\n📈 90-DAY CASH FLOW PROJECTION (sample)")
    print("  Date         Inflows      Outflows     Projected Balance")
    for p in projections[::15]:  # every 15 days for readability
        print(f"  {p['date']}   ₹{p['inflows']:>8,.0f}   ₹{p['outflows']:>8,.0f}   ₹{p['balance']:>12,.0f}")
    
    # Working capital
    wc = estimate_working_capital(projections)
    print("\n💰 WORKING CAPITAL ESTIMATE")
    for period, data in wc.items():
        print(f"  Next {period.replace('_', ' '):<10}: Lowest balance ₹{data['lowest_projected_balance']:,.0f} | "
              f"Need: ₹{data['estimated_working_capital_need']:,.0f} | {data['recommendation']}")
    
    # Financing candidates
    candidates = financing_candidates()
    print("\n🎯 TOP INVOICES FOR FINANCING (Discounting / Factoring)")
    for inv in candidates[:3]:
        print(f"  {inv['id']} | {inv['customer']:<25} | ₹{inv['amount']:,.0f} | Due: {inv['due_date']} | {inv['status'].upper()}")
    
    # GST
    gst = gst_notes()
    print("\n🇮🇳 GST NOTES")
    print(f"  Output GST on pending invoices: ₹{gst['total_output_gst_on_pending_invoices']:,.0f}")
    print(f"  Reminder: {gst['reminder']}")
    
    print("\n" + "=" * 70)
    print("Demo complete. Extend with real AI models, bank APIs, and GSTN integration.")
    print("=" * 70)

if __name__ == "__main__":
    main()
