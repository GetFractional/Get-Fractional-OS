#!/usr/bin/env python3
# =============================================================================
# Get Fractional OS — Airtable Base Populator (Python)
# =============================================================================
# Populates an EXISTING Airtable base with all 12 tables, fields,
# relationships, views, and seed data via the Airtable REST API.
#
# This script skips base creation — use it when you've already created
# the base manually (e.g., via the Airtable UI).
#
# Prerequisites:
#   - Python 3.7+
#   - requests library  →  pip3 install requests
#   - AIRTABLE_API_KEY env var (Personal Access Token starting with "pat")
#
# Usage:
#   export AIRTABLE_API_KEY="patXXXXXXXXXXXXXX"
#   python3 setup/airtable-populate.py appXXXXXXXXXXXXXX
#
# The script is idempotent: it skips tables, fields, and views that
# already exist, so you can safely re-run after a partial failure.
# =============================================================================
from __future__ import annotations  # Python 3.7+ compat for type hints

import os
import sys
import time
import requests

# ── Configuration ────────────────────────────────────────────────────────────

API = "https://api.airtable.com/v0"
RATE_LIMIT_SEC = 0.25  # 4 req/sec keeps us under Airtable's 5/sec limit

# ── Colors ───────────────────────────────────────────────────────────────────

GREEN  = "\033[1;32m"
RED    = "\033[1;31m"
BLUE   = "\033[1;34m"
YELLOW = "\033[1;33m"
RESET  = "\033[0m"

def log(msg):  print(f"{BLUE}[INFO]{RESET}  {msg}")
def ok(msg):   print(f"{GREEN}[OK]{RESET}    {msg}")
def err(msg):  print(f"{RED}[ERR]{RESET}   {msg}", file=sys.stderr)
def warn(msg): print(f"{YELLOW}[WARN]{RESET}  {msg}")

# ── Table Definitions (non-link fields only) ─────────────────────────────────

TABLES = [
    {
        "name": "Accounts",
        "description": "Companies/brands that are clients or prospects",
        "fields": [
            {"name": "Account Name", "type": "singleLineText", "description": "Company or brand name"},
            {"name": "Website URL", "type": "url"},
            {"name": "Industry", "type": "singleSelect", "options": {"choices": [
                {"name": "DTC Skincare", "color": "blueLight2"},
                {"name": "DTC Supplements", "color": "cyanLight2"},
                {"name": "DTC Food & Bev", "color": "tealLight2"},
                {"name": "DTC Apparel", "color": "greenLight2"},
                {"name": "SaaS", "color": "yellowLight2"},
                {"name": "Other", "color": "grayLight2"},
            ]}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Prospect", "color": "yellowLight2"},
                {"name": "Active Client", "color": "greenLight2"},
                {"name": "Past Client", "color": "blueLight2"},
                {"name": "Churned", "color": "redLight2"},
            ]}},
            {"name": "Source", "type": "singleSelect", "options": {"choices": [
                {"name": "LinkedIn", "color": "blueLight2"},
                {"name": "Referral", "color": "greenLight2"},
                {"name": "Inbound", "color": "cyanLight2"},
                {"name": "Cold Outreach", "color": "grayLight2"},
                {"name": "Other", "color": "grayLight2"},
            ]}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Contacts",
        "description": "Individual people at accounts",
        "fields": [
            {"name": "Full Name", "type": "singleLineText", "description": "Contact full name"},
            {"name": "Email", "type": "email"},
            {"name": "Phone", "type": "phoneNumber"},
            {"name": "LinkedIn URL", "type": "url"},
            {"name": "Role/Title", "type": "singleLineText"},
            {"name": "Is Decision Maker", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
            {"name": "Lead Score", "type": "number", "options": {"precision": 0}},
            {"name": "Lead Source", "type": "singleSelect", "options": {"choices": [
                {"name": "LinkedIn Comment", "color": "blueLight2"},
                {"name": "DM", "color": "cyanLight2"},
                {"name": "Lead Magnet", "color": "tealLight2"},
                {"name": "Tripwire", "color": "greenLight2"},
                {"name": "Referral", "color": "yellowLight2"},
                {"name": "Fit Check", "color": "orangeLight2"},
                {"name": "Other", "color": "grayLight2"},
            ]}},
            {"name": "Tags", "type": "multipleSelects", "options": {"choices": [
                {"name": "TEARDOWN", "color": "blueLight2"},
                {"name": "SNAPSHOT", "color": "cyanLight2"},
                {"name": "SPRINT", "color": "greenLight2"},
                {"name": "SCOPE", "color": "tealLight2"},
                {"name": "Hook Pack Buyer", "color": "yellowLight2"},
                {"name": "Fit Check Booked", "color": "orangeLight2"},
                {"name": "Email Subscriber", "color": "grayLight2"},
            ]}},
            {"name": "Engagement Notes", "type": "multilineText"},
            {"name": "Last Contacted", "type": "date", "options": {"dateFormat": {"name": "local"}}},
        ],
    },
    {
        "name": "Deals",
        "description": "Pipeline tracking for all offers",
        "fields": [
            {"name": "Deal Name", "type": "singleLineText", "description": "Format: Account - Offer Type"},
            {"name": "Offer", "type": "singleSelect", "options": {"choices": [
                {"name": "Fit Check ($97)", "color": "yellowLight2"},
                {"name": "Creative Sprint ($3500-$8000)", "color": "greenLight2"},
                {"name": "Monthly Retainer", "color": "blueLight2"},
                {"name": "Hook Pack ($7)", "color": "cyanLight2"},
                {"name": "Custom", "color": "grayLight2"},
            ]}},
            {"name": "Stage", "type": "singleSelect", "options": {"choices": [
                {"name": "Lead", "color": "grayLight2"},
                {"name": "Qualified", "color": "yellowLight2"},
                {"name": "Fit Check Scheduled", "color": "orangeLight2"},
                {"name": "Fit Check Complete", "color": "orangeLight2"},
                {"name": "Proposal Sent", "color": "cyanLight2"},
                {"name": "Scope Signed", "color": "blueLight2"},
                {"name": "Deposit Paid", "color": "tealLight2"},
                {"name": "In Progress", "color": "greenLight2"},
                {"name": "Delivered", "color": "greenLight2"},
                {"name": "Closed Won", "color": "greenBright"},
                {"name": "Closed Lost", "color": "redLight2"},
            ]}},
            {"name": "Amount", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
            {"name": "Deposit Paid", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
            {"name": "Final Paid", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
            {"name": "Close Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Lost Reason", "type": "singleSelect", "options": {"choices": [
                {"name": "Price", "color": "redLight2"},
                {"name": "Timing", "color": "yellowLight2"},
                {"name": "Scope Mismatch", "color": "orangeLight2"},
                {"name": "Went with Agency", "color": "blueLight2"},
                {"name": "No Response", "color": "grayLight2"},
                {"name": "Other", "color": "grayLight2"},
            ]}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Sprints",
        "description": "Active and completed sprint engagements",
        "fields": [
            {"name": "Sprint Name", "type": "singleLineText", "description": "Format: Account - Sprint #N"},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Intake Pending", "color": "grayLight2"},
                {"name": "In Progress", "color": "blueLight2"},
                {"name": "Day 3 Review", "color": "cyanLight2"},
                {"name": "Day 10 Review", "color": "tealLight2"},
                {"name": "Revision 1", "color": "yellowLight2"},
                {"name": "Revision 2", "color": "orangeLight2"},
                {"name": "Delivered", "color": "greenLight2"},
                {"name": "Paused", "color": "redLight2"},
            ]}},
            {"name": "Start Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Day 3 Milestone", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Day 10 Milestone", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Due Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Intake Received", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
            {"name": "Intake Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Not Sent", "color": "grayLight2"},
                {"name": "Sent", "color": "yellowLight2"},
                {"name": "Partial", "color": "orangeLight2"},
                {"name": "Complete", "color": "greenLight2"},
            ]}},
            {"name": "QA Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Not Started", "color": "grayLight2"},
                {"name": "In Progress", "color": "blueLight2"},
                {"name": "Passed", "color": "greenLight2"},
                {"name": "Failed", "color": "redLight2"},
            ]}},
            {"name": "Proof Permission", "type": "singleSelect", "options": {"choices": [
                {"name": "Full Public", "color": "greenLight2"},
                {"name": "Anonymized", "color": "yellowLight2"},
                {"name": "Process Only", "color": "grayLight2"},
            ]}},
            {"name": "Pause Reason", "type": "multilineText"},
            {"name": "Client Satisfaction", "type": "rating", "options": {"max": 5, "color": "yellowBright", "icon": "star"}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Deliverables",
        "description": "Individual deliverable items within sprints",
        "fields": [
            {"name": "Deliverable Name", "type": "singleLineText"},
            {"name": "Type", "type": "singleSelect", "options": {"choices": [
                {"name": "ICP Brief", "color": "blueLight2"},
                {"name": "Objection Map", "color": "cyanLight2"},
                {"name": "Ad Angles", "color": "tealLight2"},
                {"name": "Hooks", "color": "greenLight2"},
                {"name": "Ad Concepts", "color": "yellowLight2"},
                {"name": "LP Copy Kit", "color": "orangeLight2"},
                {"name": "Testing Plan", "color": "redLight2"},
                {"name": "Other", "color": "grayLight2"},
            ]}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Not Started", "color": "grayLight2"},
                {"name": "In Progress", "color": "blueLight2"},
                {"name": "Draft", "color": "yellowLight2"},
                {"name": "QA Review", "color": "orangeLight2"},
                {"name": "Delivered", "color": "greenLight2"},
                {"name": "Revised", "color": "tealLight2"},
            ]}},
            {"name": "Version", "type": "number", "options": {"precision": 0}},
            {"name": "File Link", "type": "url"},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Content Calendar",
        "description": "Track all content across platforms",
        "fields": [
            {"name": "Post Title", "type": "singleLineText"},
            {"name": "Platform", "type": "singleSelect", "options": {"choices": [
                {"name": "LinkedIn", "color": "blueLight2"},
                {"name": "Facebook", "color": "cyanLight2"},
                {"name": "Instagram", "color": "orangeLight2"},
                {"name": "Email", "color": "tealLight2"},
                {"name": "Blog", "color": "greenLight2"},
            ]}},
            {"name": "Pillar", "type": "singleSelect", "options": {"choices": [
                {"name": "Teardown", "color": "redLight2"},
                {"name": "URL to Brief", "color": "blueLight2"},
                {"name": "Proof Object", "color": "greenLight2"},
                {"name": "Systems", "color": "yellowLight2"},
                {"name": "Offer/Story", "color": "orangeLight2"},
            ]}},
            {"name": "Series", "type": "singleSelect", "options": {"choices": [
                {"name": "From URL to Campaign", "color": "blueLight2"},
                {"name": "General", "color": "grayLight2"},
                {"name": "Guest/Collab", "color": "cyanLight2"},
            ]}},
            {"name": "Journey Stage", "type": "singleSelect", "options": {"choices": [
                {"name": "Problem-Aware", "color": "yellowLight2"},
                {"name": "Solution-Aware", "color": "blueLight2"},
                {"name": "Most-Aware", "color": "greenLight2"},
            ]}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Idea", "color": "grayLight2"},
                {"name": "Draft", "color": "yellowLight2"},
                {"name": "Review", "color": "orangeLight2"},
                {"name": "Scheduled", "color": "blueLight2"},
                {"name": "Published", "color": "greenLight2"},
            ]}},
            {"name": "Publish Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Post Copy", "type": "multilineText"},
            {"name": "CTA Type", "type": "singleSelect", "options": {"choices": [
                {"name": "Comment Trigger", "color": "blueLight2"},
                {"name": "DM Trigger", "color": "cyanLight2"},
                {"name": "Link", "color": "greenLight2"},
                {"name": "None", "color": "grayLight2"},
            ]}},
            {"name": "CTA Text", "type": "singleLineText"},
            {"name": "Engagement", "type": "number", "options": {"precision": 0}},
            {"name": "Leads Generated", "type": "number", "options": {"precision": 0}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Leads",
        "description": "All inbound leads before they become contacts/deals",
        "fields": [
            {"name": "Name", "type": "singleLineText"},
            {"name": "Email", "type": "email"},
            {"name": "URL Submitted", "type": "url"},
            {"name": "Trigger Word", "type": "singleSelect", "options": {"choices": [
                {"name": "TEARDOWN", "color": "blueLight2"},
                {"name": "SNAPSHOT", "color": "cyanLight2"},
                {"name": "SPRINT", "color": "greenLight2"},
                {"name": "SCOPE", "color": "tealLight2"},
                {"name": "Hook Pack", "color": "yellowLight2"},
                {"name": "Fit Check", "color": "orangeLight2"},
                {"name": "Email Opt-in", "color": "grayLight2"},
            ]}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "New", "color": "blueLight2"},
                {"name": "Contacted", "color": "cyanLight2"},
                {"name": "Responded", "color": "tealLight2"},
                {"name": "Qualified", "color": "greenLight2"},
                {"name": "Converted", "color": "greenBright"},
                {"name": "Dead", "color": "grayLight2"},
            ]}},
            {"name": "Response Sent", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
            {"name": "Response Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Proof Objects",
        "description": "Track proof/social proof for marketing use",
        "fields": [
            {"name": "Proof Title", "type": "singleLineText"},
            {"name": "Type", "type": "singleSelect", "options": {"choices": [
                {"name": "Deliverable Count", "color": "blueLight2"},
                {"name": "Timeline", "color": "cyanLight2"},
                {"name": "Client Quote", "color": "greenLight2"},
                {"name": "Result Metric", "color": "tealLight2"},
                {"name": "Process Demo", "color": "yellowLight2"},
                {"name": "Before/After", "color": "orangeLight2"},
            ]}},
            {"name": "Permission Level", "type": "singleSelect", "options": {"choices": [
                {"name": "Full Public", "color": "greenLight2"},
                {"name": "Anonymized", "color": "yellowLight2"},
                {"name": "Process Only", "color": "grayLight2"},
            ]}},
            {"name": "Content", "type": "multilineText"},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Draft", "color": "yellowLight2"},
                {"name": "Approved", "color": "blueLight2"},
                {"name": "Published", "color": "greenLight2"},
            ]}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Invoices",
        "description": "Track all payments and invoicing",
        "fields": [
            {"name": "Invoice ID", "type": "singleLineText", "description": "Format: INV-YYYY-NNN"},
            {"name": "Type", "type": "singleSelect", "options": {"choices": [
                {"name": "Deposit", "color": "blueLight2"},
                {"name": "Final Payment", "color": "greenLight2"},
                {"name": "Add-on", "color": "cyanLight2"},
                {"name": "Tripwire", "color": "yellowLight2"},
                {"name": "Fit Check", "color": "orangeLight2"},
            ]}},
            {"name": "Amount", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Draft", "color": "grayLight2"},
                {"name": "Sent", "color": "blueLight2"},
                {"name": "Paid", "color": "greenLight2"},
                {"name": "Overdue", "color": "redLight2"},
                {"name": "Cancelled", "color": "grayLight2"},
            ]}},
            {"name": "Sent Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Due Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Paid Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Payment Method", "type": "singleSelect", "options": {"choices": [
                {"name": "Stripe", "color": "blueLight2"},
                {"name": "Bank Transfer", "color": "greenLight2"},
                {"name": "Other", "color": "grayLight2"},
            ]}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Email Sequences",
        "description": "Track email automation sequences and performance",
        "fields": [
            {"name": "Sequence Name", "type": "singleLineText"},
            {"name": "Trigger", "type": "singleSelect", "options": {"choices": [
                {"name": "Lead Magnet Download", "color": "blueLight2"},
                {"name": "Tripwire Purchase", "color": "greenLight2"},
                {"name": "Fit Check Booked", "color": "yellowLight2"},
                {"name": "Sprint Complete", "color": "tealLight2"},
                {"name": "Comment Trigger", "color": "cyanLight2"},
            ]}},
            {"name": "Email Count", "type": "number", "options": {"precision": 0}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Draft", "color": "yellowLight2"},
                {"name": "Active", "color": "greenLight2"},
                {"name": "Paused", "color": "grayLight2"},
            ]}},
            {"name": "Open Rate", "type": "percent", "options": {"precision": 1}},
            {"name": "Click Rate", "type": "percent", "options": {"precision": 1}},
            {"name": "Conversion Rate", "type": "percent", "options": {"precision": 1}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Templates",
        "description": "Master list of all templates and SOPs",
        "fields": [
            {"name": "Template Name", "type": "singleLineText"},
            {"name": "Category", "type": "singleSelect", "options": {"choices": [
                {"name": "Client-Facing", "color": "blueLight2"},
                {"name": "Internal SOP", "color": "greenLight2"},
                {"name": "Content Template", "color": "yellowLight2"},
                {"name": "Email Template", "color": "cyanLight2"},
                {"name": "Automation", "color": "orangeLight2"},
            ]}},
            {"name": "Version", "type": "number", "options": {"precision": 0}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": [
                {"name": "Draft", "color": "yellowLight2"},
                {"name": "Active", "color": "greenLight2"},
                {"name": "Deprecated", "color": "grayLight2"},
            ]}},
            {"name": "File Link", "type": "url"},
            {"name": "Last Updated", "type": "date", "options": {"dateFormat": {"name": "local"}}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
    {
        "name": "Metrics Dashboard",
        "description": "Weekly/monthly KPI tracking",
        "fields": [
            {"name": "Period", "type": "singleLineText", "description": "Format: W01-2026 or Jan-2026"},
            {"name": "Period Type", "type": "singleSelect", "options": {"choices": [
                {"name": "Weekly", "color": "blueLight2"},
                {"name": "Monthly", "color": "greenLight2"},
            ]}},
            {"name": "New Leads", "type": "number", "options": {"precision": 0}},
            {"name": "Fit Checks Booked", "type": "number", "options": {"precision": 0}},
            {"name": "Fit Checks Completed", "type": "number", "options": {"precision": 0}},
            {"name": "Sprints Sold", "type": "number", "options": {"precision": 0}},
            {"name": "Revenue", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
            {"name": "Content Published", "type": "number", "options": {"precision": 0}},
            {"name": "Total Engagement", "type": "number", "options": {"precision": 0}},
            {"name": "Email Subscribers", "type": "number", "options": {"precision": 0}},
            {"name": "Tripwire Sales", "type": "number", "options": {"precision": 0}},
            {"name": "Active Sprints", "type": "number", "options": {"precision": 0}},
            {"name": "Notes", "type": "multilineText"},
        ],
    },
]

# ── Relationships ────────────────────────────────────────────────────────────
# (source_table, field_name, target_table, prefers_single_record_link)

LINKS = [
    # Accounts → many
    ("Accounts",        "Contacts",        "Contacts",         False),
    ("Accounts",        "Deals",           "Deals",            False),
    ("Accounts",        "Sprints",         "Sprints",          False),
    # Deals → single
    ("Deals",           "Account",         "Accounts",         True),
    ("Deals",           "Contact",         "Contacts",         True),
    ("Deals",           "Sprint",          "Sprints",          True),
    # Sprints → mixed
    ("Sprints",         "Account",         "Accounts",         True),
    ("Sprints",         "Deal",            "Deals",            True),
    ("Sprints",         "Deliverables",    "Deliverables",     False),
    # Deliverables → single
    ("Deliverables",    "Sprint",          "Sprints",          True),
    # Leads → single
    ("Leads",           "Source Post",     "Content Calendar", True),
    ("Leads",           "Contact",         "Contacts",         True),
    # Proof Objects → mixed
    ("Proof Objects",   "Sprint",          "Sprints",          True),
    ("Proof Objects",   "Account",         "Accounts",         True),
    ("Proof Objects",   "Used In",         "Content Calendar", False),
    # Invoices → single
    ("Invoices",        "Deal",            "Deals",            True),
    ("Invoices",        "Account",         "Accounts",         True),
    # Content Calendar → self-link
    ("Content Calendar","Repurposed From", "Content Calendar", False),
]

# ── Views ────────────────────────────────────────────────────────────────────
# (table_name, view_name, view_type)

VIEWS = [
    ("Accounts",         "Active Clients",   "grid"),
    ("Accounts",         "Pipeline",          "grid"),
    ("Deals",            "Pipeline Board",    "kanban"),
    ("Deals",            "Won This Month",    "grid"),
    ("Sprints",          "Active Sprints",    "grid"),
    ("Sprints",          "Sprint Board",      "kanban"),
    ("Content Calendar", "Publishing Queue",  "grid"),
    ("Content Calendar", "Content Board",     "kanban"),
    ("Content Calendar", "By Pillar",         "grid"),
    ("Leads",            "New Leads",         "grid"),
    ("Leads",            "By Trigger",        "grid"),
    ("Metrics Dashboard","Weekly View",       "grid"),
]

# ── Seed Data ────────────────────────────────────────────────────────────────

SEED_CONTENT = [
    {
        "Post Title":     "Why Your Hooks All Sound the Same",
        "Platform":       "LinkedIn",
        "Pillar":         "Teardown",
        "Series":         "From URL to Campaign",
        "Journey Stage":  "Problem-Aware",
        "Status":         "Draft",
        "CTA Type":       "Comment Trigger",
        "CTA Text":       "Comment TEARDOWN",
    },
    {
        "Post Title":     "3 Things I Pull From Any URL",
        "Platform":       "LinkedIn",
        "Pillar":         "URL to Brief",
        "Series":         "From URL to Campaign",
        "Journey Stage":  "Problem-Aware",
        "Status":         "Draft",
        "CTA Type":       "Comment Trigger",
        "CTA Text":       "Comment SNAPSHOT + your URL",
    },
    {
        "Post Title":     "What a 14-Day Sprint Produces",
        "Platform":       "LinkedIn",
        "Pillar":         "Proof Object",
        "Series":         "From URL to Campaign",
        "Journey Stage":  "Solution-Aware",
        "Status":         "Draft",
        "CTA Type":       "DM Trigger",
        "CTA Text":       "DM SPRINT",
    },
    {
        "Post Title":     "Why Creative Projects Fail Before Delivery",
        "Platform":       "LinkedIn",
        "Pillar":         "Systems",
        "Series":         "From URL to Campaign",
        "Journey Stage":  "Solution-Aware",
        "Status":         "Draft",
        "CTA Type":       "Comment Trigger",
        "CTA Text":       "Comment SCOPE",
    },
    {
        "Post Title":     "I Built This Because I Kept Seeing 3 Problems",
        "Platform":       "LinkedIn",
        "Pillar":         "Offer/Story",
        "Series":         "From URL to Campaign",
        "Journey Stage":  "Solution-Aware",
        "Status":         "Draft",
        "CTA Type":       "Comment Trigger",
        "CTA Text":       "Comment SPRINT",
    },
]

SEED_TEMPLATES = [
    {"Template Name": "Sprint Scope Agreement",  "Category": "Client-Facing",    "Version": 1, "Status": "Active"},
    {"Template Name": "Sprint Intake Checklist",  "Category": "Client-Facing",    "Version": 1, "Status": "Active"},
    {"Template Name": "Revision Policy",          "Category": "Client-Facing",    "Version": 1, "Status": "Active"},
    {"Template Name": "QA Checklist",             "Category": "Internal SOP",     "Version": 1, "Status": "Active"},
    {"Template Name": "Proof Capture Checklist",  "Category": "Internal SOP",     "Version": 1, "Status": "Active"},
    {"Template Name": "Case Study Skeleton",      "Category": "Content Template", "Version": 1, "Status": "Active"},
    {"Template Name": "URL to ICP Snapshot",      "Category": "Content Template", "Version": 1, "Status": "Active"},
    {"Template Name": "7 Hooks Guide",            "Category": "Content Template", "Version": 1, "Status": "Active"},
    {"Template Name": "Hook Pack ($7)",           "Category": "Content Template", "Version": 1, "Status": "Active"},
]


# =============================================================================
# API Client
# =============================================================================

class AirtableClient:
    """Thin, rate-limited wrapper around the Airtable REST + Metadata APIs."""

    def __init__(self, api_key: str, base_id: str):
        self.base_id = base_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        # name → table_id
        self.table_ids: dict[str, str] = {}
        # table_id → set of field names already present
        self.table_fields: dict[str, set] = {}

    # ── low-level ────────────────────────────────────────────────────────

    MAX_RETRIES = 4
    RETRY_BACKOFF = [2, 4, 8, 16]  # seconds between retries

    def _throttle(self):
        time.sleep(RATE_LIMIT_SEC)

    def _is_retryable(self, status_code: int) -> bool:
        """Returns True for status codes worth retrying (server errors + rate limits)."""
        return status_code in (429, 500, 502, 503)

    def get(self, path: str) -> dict:
        for attempt in range(self.MAX_RETRIES + 1):
            self._throttle()
            r = self.session.get(f"{API}{path}")
            if r.status_code < 400:
                return r.json()
            if self._is_retryable(r.status_code) and attempt < self.MAX_RETRIES:
                wait = self.RETRY_BACKOFF[attempt]
                warn(f"GET {path} → {r.status_code} (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            err(f"GET {path} → {r.status_code}: {r.text[:300]}")
            r.raise_for_status()
        return {}  # unreachable, but keeps type checkers happy

    def post(self, path: str, payload: dict) -> dict:
        for attempt in range(self.MAX_RETRIES + 1):
            self._throttle()
            r = self.session.post(f"{API}{path}", json=payload)
            if r.status_code < 400:
                return r.json()
            if self._is_retryable(r.status_code) and attempt < self.MAX_RETRIES:
                wait = self.RETRY_BACKOFF[attempt]
                warn(f"POST {path} → {r.status_code} (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            err(f"POST {path} → {r.status_code}: {r.text[:300]}")
            r.raise_for_status()
        return {}

    def post_safe(self, path: str, payload: dict) -> dict | None:
        """POST that returns None on 422 (conflict / already exists) instead of raising."""
        for attempt in range(self.MAX_RETRIES + 1):
            self._throttle()
            r = self.session.post(f"{API}{path}", json=payload)
            if r.status_code < 400:
                return r.json()
            if r.status_code == 422:
                # Any 422 means this entity can't be created — likely already
                # exists or conflicts with existing data.  In an idempotent
                # script this is always safe to skip.
                return None
            if self._is_retryable(r.status_code) and attempt < self.MAX_RETRIES:
                wait = self.RETRY_BACKOFF[attempt]
                warn(f"POST {path} → {r.status_code} (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            err(f"POST {path} → {r.status_code}: {r.text[:300]}")
            r.raise_for_status()
        return {}

    def patch(self, path: str, payload: dict) -> dict:
        for attempt in range(self.MAX_RETRIES + 1):
            self._throttle()
            r = self.session.patch(f"{API}{path}", json=payload)
            if r.status_code < 400:
                return r.json()
            if self._is_retryable(r.status_code) and attempt < self.MAX_RETRIES:
                wait = self.RETRY_BACKOFF[attempt]
                warn(f"PATCH {path} → {r.status_code} (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            err(f"PATCH {path} → {r.status_code}: {r.text[:300]}")
            r.raise_for_status()
        return {}

    # ── discovery ────────────────────────────────────────────────────────

    def discover(self):
        """Load the base's current tables + field names into memory."""
        log("Discovering existing tables in base...")
        data = self.get(f"/meta/bases/{self.base_id}/tables")
        for t in data.get("tables", []):
            name, tid = t["name"], t["id"]
            self.table_ids[name] = tid
            self.table_fields[tid] = {f["name"] for f in t.get("fields", [])}
            ok(f"Found: {name} ({tid}) — {len(self.table_fields[tid])} fields")
        if not self.table_ids:
            log("No custom tables found yet.")
        print()

    # ── table creation ───────────────────────────────────────────────────

    def create_table(self, name: str, description: str, fields: list[dict]):
        if name in self.table_ids:
            warn(f"Table '{name}' already exists — skipping")
            return
        log(f"Creating table: {name}...")
        resp = self.post(f"/meta/bases/{self.base_id}/tables", {
            "name": name,
            "description": description,
            "fields": fields,
        })
        tid = resp["id"]
        self.table_ids[name] = tid
        self.table_fields[tid] = {f["name"] for f in resp.get("fields", [])}
        ok(f"{name}: {tid}")

    # ── link fields ──────────────────────────────────────────────────────

    def _find_link_field(self, on_table_id: str, pointing_to_table_id: str, tables_data: list | None = None) -> dict | None:
        """Find a link field on on_table_id that points to pointing_to_table_id."""
        if tables_data is None:
            data = self.get(f"/meta/bases/{self.base_id}/tables")
            tables_data = data.get("tables", [])
        for t in tables_data:
            if t["id"] == on_table_id:
                for f in t.get("fields", []):
                    if f.get("type") == "multipleRecordLinks":
                        opts = f.get("options", {})
                        if opts.get("linkedTableId") == pointing_to_table_id:
                            return f
        return None

    def _try_rename_field(self, fld_path: str, new_name: str, single: bool) -> bool:
        """Try to PATCH-rename a field. Returns True on success."""
        attempts = []
        if single:
            attempts.append({"name": new_name, "options": {"prefersSingleRecordLink": True}})
        attempts.append({"name": new_name})
        for i, payload in enumerate(attempts):
            self._throttle()
            pr = self.session.patch(f"{API}{fld_path}", json=payload)
            if pr.status_code < 400:
                return True
            if i < len(attempts) - 1:
                warn(f"  PATCH with options failed ({pr.status_code}) — retrying name-only")
        return False

    def add_link(self, src_table: str, field_name: str, tgt_table: str, single: bool):
        tid = self.table_ids.get(src_table)
        linked_tid = self.table_ids.get(tgt_table)
        if not tid:
            err(f"Source table '{src_table}' not found — skipping link")
            return
        if not linked_tid:
            err(f"Target table '{tgt_table}' not found — skipping link")
            return

        # Already present?
        if field_name in self.table_fields.get(tid, set()):
            warn(f"{src_table}.{field_name} already exists — skipping")
            return

        options = {"linkedTableId": linked_tid}
        if single:
            options["prefersSingleRecordLink"] = True

        # Try creating the link field
        self._throttle()
        r = self.session.post(
            f"{API}/meta/bases/{self.base_id}/tables/{tid}/fields",
            json={"name": field_name, "type": "multipleRecordLinks", "options": options},
        )

        if r.status_code < 400:
            ok(f"Link: {src_table}.{field_name} → {tgt_table}" + (" (single)" if single else ""))
            self.table_fields.setdefault(tid, set()).add(field_name)
            return

        if r.status_code == 422 and "isReversed" in r.text:
            # A link already exists between these tables (Airtable auto-created
            # a reverse field). Fetch fresh schema and search both tables.
            schema = self.get(f"/meta/bases/{self.base_id}/tables")
            tables_data = schema.get("tables", [])

            # 1) Look on the SOURCE table for a field pointing to target
            reverse = self._find_link_field(tid, linked_tid, tables_data)
            if reverse:
                old_name = reverse["name"]
                fld_path = f"/meta/bases/{self.base_id}/tables/{tid}/fields/{reverse['id']}"
                renamed = self._try_rename_field(fld_path, field_name, single)
                if renamed:
                    self.table_fields.get(tid, set()).discard(old_name)
                    ok(f"Link: {src_table}.{field_name} → {tgt_table} (renamed '{old_name}')" + (" (single)" if single else ""))
                    self.table_fields.setdefault(tid, set()).add(field_name)
                else:
                    warn(f"Link {src_table} → {tgt_table} exists as '{old_name}' (rename failed — keeping)")
                    self.table_fields.setdefault(tid, set()).add(old_name)
                return

            # 2) Look on the TARGET table for a field pointing back to source
            tgt_reverse = self._find_link_field(linked_tid, tid, tables_data)
            if tgt_reverse:
                # The link relationship already exists (field is on the other table).
                # The source table should also have an auto-reverse — refresh and find it.
                self.discover()
                if field_name in self.table_fields.get(tid, set()):
                    ok(f"Link: {src_table}.{field_name} → {tgt_table} (already present after refresh)")
                else:
                    warn(f"Link {src_table} → {tgt_table} exists (via '{tgt_reverse['name']}' on {tgt_table}) — field on {src_table} has auto-generated name")
                return

            # 3) Last resort: try POST without prefersSingleRecordLink
            if single:
                self._throttle()
                r2 = self.session.post(
                    f"{API}/meta/bases/{self.base_id}/tables/{tid}/fields",
                    json={"name": field_name, "type": "multipleRecordLinks", "options": {"linkedTableId": linked_tid}},
                )
                if r2.status_code < 400:
                    ok(f"Link: {src_table}.{field_name} → {tgt_table} (without single-record preference)")
                    self.table_fields.setdefault(tid, set()).add(field_name)
                    return

            # Nothing worked — warn and continue (never crash)
            warn(f"Link {src_table}.{field_name} → {tgt_table}: could not create or find ({r.status_code}) — skipping")
            return

        if r.status_code == 422:
            warn(f"Link {src_table}.{field_name} → {tgt_table}: 422 — likely already exists, skipping")
            return

        err(f"POST → {r.status_code}: {r.text[:300]}")
        r.raise_for_status()

    # ── views ────────────────────────────────────────────────────────────

    def create_view(self, table_name: str, view_name: str, view_type: str = "grid"):
        tid = self.table_ids.get(table_name)
        if not tid:
            err(f"Table '{table_name}' not found — cannot create view")
            return
        result = self.post_safe(
            f"/meta/bases/{self.base_id}/tables/{tid}/views",
            {"name": view_name, "type": view_type},
        )
        if result:
            ok(f"View: {table_name} / {view_name} ({view_type})")
        else:
            warn(f"View '{view_name}' on {table_name} may already exist — skipped")

    # ── seed data ────────────────────────────────────────────────────────

    def seed_record(self, table_name: str, fields: dict):
        tid = self.table_ids.get(table_name)
        if not tid:
            err(f"Table '{table_name}' not found — cannot seed record")
            return
        self.post(f"/{self.base_id}/{tid}", {"fields": fields})


# =============================================================================
# Main Execution
# =============================================================================

def main():
    # ── Parse args ───────────────────────────────────────────────────────
    api_key = os.environ.get("AIRTABLE_API_KEY", "")
    if not api_key:
        err("Missing AIRTABLE_API_KEY environment variable.")
        err("  export AIRTABLE_API_KEY=\"patXXXXXXXXXXXXXX\"")
        sys.exit(1)

    if len(sys.argv) < 2:
        err("Usage: python3 setup/airtable-populate.py <BASE_ID>")
        err("  Example: python3 setup/airtable-populate.py appLNVSPTouzO8z1B")
        sys.exit(1)

    base_id = sys.argv[1]
    if not base_id.startswith("app"):
        err(f"Base ID should start with 'app', got: {base_id}")
        sys.exit(1)

    print()
    print("=" * 60)
    log("Get Fractional OS — Airtable Base Populator")
    log(f"Base ID: {base_id}")
    print("=" * 60)
    print()

    client = AirtableClient(api_key, base_id)

    # ── Step 0: Discover what already exists ─────────────────────────────
    client.discover()

    # ── Step 1: Create all 12 tables ─────────────────────────────────────
    print("=" * 60)
    log("STEP 1/4 — Creating tables")
    print("=" * 60)
    for tbl in TABLES:
        client.create_table(tbl["name"], tbl["description"], tbl["fields"])
    print()

    # Quick sanity check
    missing = [t["name"] for t in TABLES if t["name"] not in client.table_ids]
    if missing:
        err(f"These tables are missing and could not be created: {missing}")
        err("Fix the issue above and re-run. The script will pick up where it left off.")
        sys.exit(1)
    ok(f"All {len(TABLES)} tables present.")
    print()

    # ── Step 2: Add link fields ──────────────────────────────────────────
    print("=" * 60)
    log("STEP 2/4 — Adding relationships (linked record fields)")
    print("=" * 60)
    for src, field, tgt, single in LINKS:
        client.add_link(src, field, tgt, single)
    print()
    ok(f"All {len(LINKS)} relationship fields processed.")
    print()

    # ── Step 3: Create views ─────────────────────────────────────────────
    print("=" * 60)
    log("STEP 3/4 — Creating views")
    print("=" * 60)
    for tbl, vname, vtype in VIEWS:
        client.create_view(tbl, vname, vtype)
    print()
    ok(f"All {len(VIEWS)} views processed.")
    print()

    # ── Step 4: Seed data ────────────────────────────────────────────────
    print("=" * 60)
    log("STEP 4/4 — Seeding starter data")
    print("=" * 60)

    log("Seeding Content Calendar (5 cornerstone posts)...")
    for post in SEED_CONTENT:
        client.seed_record("Content Calendar", post)
        ok(f"  Post: {post['Post Title']}")

    log("Seeding Templates (9 records)...")
    for tmpl in SEED_TEMPLATES:
        client.seed_record("Templates", tmpl)
        ok(f"  Template: {tmpl['Template Name']}")

    print()

    # ── Done ─────────────────────────────────────────────────────────────
    print("=" * 60)
    ok("Get Fractional OS — base is populated!")
    print("=" * 60)
    print()
    print(f"  Base ID:  {base_id}")
    print(f"  Base URL: https://airtable.com/{base_id}")
    print()
    print(f"  Tables:         {len(TABLES)}")
    print(f"  Relationships:  {len(LINKS)} linked fields")
    print(f"  Views:          {len(VIEWS)} custom views")
    print(f"  Seed data:      {len(SEED_CONTENT)} cornerstone posts + {len(SEED_TEMPLATES)} templates")
    print()

    # Check for leftover default table
    if "Table 1" in client.table_ids:
        warn("Your base still has the default 'Table 1'.")
        warn("You can delete it manually in Airtable (right-click the tab → Delete table).")
        print()

    print("  Next steps:")
    print("    1. Open your base and delete 'Table 1' if it exists")
    print("    2. Configure view filters/sorts (see setup/airtable-go-live.md Phase 2)")
    print("    3. Create automations with Omni (Phase 3)")
    print("    4. Create interfaces with Omni (Phase 4)")
    print()


if __name__ == "__main__":
    main()
