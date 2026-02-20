#!/usr/bin/env bash
# =============================================================================
# Get Fractional OS — Airtable Base Builder
# =============================================================================
# Creates the complete Airtable base with all 12 tables, fields, relationships,
# and views via the Airtable REST API.
#
# Prerequisites:
#   - bash 4+, curl, jq
#   - AIRTABLE_API_KEY env var set to your Personal Access Token (pat...)
#   - AIRTABLE_WORKSPACE_ID env var set to your workspace ID (wsp...)
#
# Usage:
#   export AIRTABLE_API_KEY="patXXXXXXXXXXXXXX"
#   export AIRTABLE_WORKSPACE_ID="wspXXXXXXXXXXXXXX"
#   bash setup/airtable-build.sh
#
# To find your workspace ID:
#   curl -s https://api.airtable.com/v0/meta/workspaces \
#     -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq '.workspaces[0].id'
# =============================================================================

set -euo pipefail

# --- Config ---
API="https://api.airtable.com/v0"
TOKEN="${AIRTABLE_API_KEY:?Set AIRTABLE_API_KEY to your Airtable Personal Access Token}"
WORKSPACE="${AIRTABLE_WORKSPACE_ID:?Set AIRTABLE_WORKSPACE_ID to your workspace ID}"

# Rate limit: 5 req/sec per base. We stay safe at 1 req/250ms.
RATE_LIMIT_MS=300

# --- Helpers ---
log()  { printf "\033[1;34m[INFO]\033[0m  %s\n" "$*"; }
ok()   { printf "\033[1;32m[OK]\033[0m    %s\n" "$*"; }
err()  { printf "\033[1;31m[ERR]\033[0m   %s\n" "$*" >&2; }
warn() { printf "\033[1;33m[WARN]\033[0m  %s\n" "$*"; }

rate_limit() { sleep "$(echo "$RATE_LIMIT_MS / 1000" | bc -l)"; }

api_post() {
  local url="$1"
  local data="$2"
  local response
  response=$(curl -s -w "\n%{http_code}" "$url" \
    -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$data")
  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')
  if [[ "$http_code" -ge 400 ]]; then
    err "HTTP $http_code from $url"
    err "Response: $body"
    return 1
  fi
  echo "$body"
  rate_limit
}

api_get() {
  local url="$1"
  local response
  response=$(curl -s -w "\n%{http_code}" "$url" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")
  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')
  if [[ "$http_code" -ge 400 ]]; then
    err "HTTP $http_code from $url"
    err "Response: $body"
    return 1
  fi
  echo "$body"
  rate_limit
}

extract_id() { echo "$1" | jq -r '.id'; }
extract_table_id() { echo "$1" | jq -r '.id'; }

# Store table IDs for linking
declare -A TABLE_IDS

# =============================================================================
# STEP 1: Create the base with the first table (Accounts)
# =============================================================================
log "Creating base: Get Fractional OS..."

BASE_RESPONSE=$(api_post "$API/meta/bases" "$(cat <<'ENDJSON'
{
  "name": "Get Fractional OS",
  "workspaceId": "WORKSPACE_PLACEHOLDER",
  "tables": [
    {
      "name": "Accounts",
      "description": "Companies/brands that are clients or prospects",
      "fields": [
        {
          "name": "Account Name",
          "type": "singleLineText",
          "description": "Company or brand name"
        },
        {
          "name": "Website URL",
          "type": "url"
        },
        {
          "name": "Industry",
          "type": "singleSelect",
          "options": {
            "choices": [
              {"name": "DTC Skincare", "color": "blueLight2"},
              {"name": "DTC Supplements", "color": "cyanLight2"},
              {"name": "DTC Food & Bev", "color": "tealLight2"},
              {"name": "DTC Apparel", "color": "greenLight2"},
              {"name": "SaaS", "color": "yellowLight2"},
              {"name": "Other", "color": "grayLight2"}
            ]
          }
        },
        {
          "name": "Status",
          "type": "singleSelect",
          "options": {
            "choices": [
              {"name": "Prospect", "color": "yellowLight2"},
              {"name": "Active Client", "color": "greenLight2"},
              {"name": "Past Client", "color": "blueLight2"},
              {"name": "Churned", "color": "redLight2"}
            ]
          }
        },
        {
          "name": "Source",
          "type": "singleSelect",
          "options": {
            "choices": [
              {"name": "LinkedIn", "color": "blueLight2"},
              {"name": "Referral", "color": "greenLight2"},
              {"name": "Inbound", "color": "cyanLight2"},
              {"name": "Cold Outreach", "color": "grayLight2"},
              {"name": "Other", "color": "grayLight2"}
            ]
          }
        },
        {
          "name": "Notes",
          "type": "multilineText"
        }
      ]
    }
  ]
}
ENDJSON
)" | sed "s/WORKSPACE_PLACEHOLDER/$WORKSPACE/")

BASE_ID=$(echo "$BASE_RESPONSE" | jq -r '.id')
if [[ -z "$BASE_ID" || "$BASE_ID" == "null" ]]; then
  err "Failed to create base. Response: $BASE_RESPONSE"
  exit 1
fi
ok "Base created: $BASE_ID"

# Get the Accounts table ID from the base creation response
ACCOUNTS_TABLE_ID=$(echo "$BASE_RESPONSE" | jq -r '.tables[0].id')
TABLE_IDS[Accounts]="$ACCOUNTS_TABLE_ID"
ok "Accounts table: ${TABLE_IDS[Accounts]}"

# Save base ID for other scripts
echo "$BASE_ID" > .airtable-base-id
log "Base ID saved to .airtable-base-id"

# =============================================================================
# STEP 2: Create remaining tables (without linked fields — added later)
# =============================================================================

# --- Contacts ---
log "Creating table: Contacts..."
CONTACTS_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
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
      {"name": "Other", "color": "grayLight2"}
    ]}},
    {"name": "Tags", "type": "multipleSelects", "options": {"choices": [
      {"name": "TEARDOWN", "color": "blueLight2"},
      {"name": "SNAPSHOT", "color": "cyanLight2"},
      {"name": "SPRINT", "color": "greenLight2"},
      {"name": "SCOPE", "color": "tealLight2"},
      {"name": "Hook Pack Buyer", "color": "yellowLight2"},
      {"name": "Fit Check Booked", "color": "orangeLight2"},
      {"name": "Email Subscriber", "color": "grayLight2"}
    ]}},
    {"name": "Engagement Notes", "type": "multilineText"},
    {"name": "Last Contacted", "type": "date", "options": {"dateFormat": {"name": "local"}}}
  ]
}')
TABLE_IDS[Contacts]=$(extract_table_id "$CONTACTS_RESP")
ok "Contacts table: ${TABLE_IDS[Contacts]}"

# --- Deals ---
log "Creating table: Deals..."
DEALS_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
  "name": "Deals",
  "description": "Pipeline tracking for all offers",
  "fields": [
    {"name": "Deal Name", "type": "singleLineText", "description": "Format: Account - Offer Type"},
    {"name": "Offer", "type": "singleSelect", "options": {"choices": [
      {"name": "Fit Check ($97)", "color": "yellowLight2"},
      {"name": "Creative Sprint ($3500-$8000)", "color": "greenLight2"},
      {"name": "Monthly Retainer", "color": "blueLight2"},
      {"name": "Hook Pack ($7)", "color": "cyanLight2"},
      {"name": "Custom", "color": "grayLight2"}
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
      {"name": "Closed Lost", "color": "redLight2"}
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
      {"name": "Other", "color": "grayLight2"}
    ]}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[Deals]=$(extract_table_id "$DEALS_RESP")
ok "Deals table: ${TABLE_IDS[Deals]}"

# --- Sprints ---
log "Creating table: Sprints..."
SPRINTS_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
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
      {"name": "Paused", "color": "redLight2"}
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
      {"name": "Complete", "color": "greenLight2"}
    ]}},
    {"name": "QA Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Not Started", "color": "grayLight2"},
      {"name": "In Progress", "color": "blueLight2"},
      {"name": "Passed", "color": "greenLight2"},
      {"name": "Failed", "color": "redLight2"}
    ]}},
    {"name": "Proof Permission", "type": "singleSelect", "options": {"choices": [
      {"name": "Full Public", "color": "greenLight2"},
      {"name": "Anonymized", "color": "yellowLight2"},
      {"name": "Process Only", "color": "grayLight2"}
    ]}},
    {"name": "Pause Reason", "type": "multilineText"},
    {"name": "Client Satisfaction", "type": "rating", "options": {"max": 5, "color": "yellowBright"}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[Sprints]=$(extract_table_id "$SPRINTS_RESP")
ok "Sprints table: ${TABLE_IDS[Sprints]}"

# --- Deliverables ---
log "Creating table: Deliverables..."
DELIVERABLES_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
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
      {"name": "Other", "color": "grayLight2"}
    ]}},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Not Started", "color": "grayLight2"},
      {"name": "In Progress", "color": "blueLight2"},
      {"name": "Draft", "color": "yellowLight2"},
      {"name": "QA Review", "color": "orangeLight2"},
      {"name": "Delivered", "color": "greenLight2"},
      {"name": "Revised", "color": "tealLight2"}
    ]}},
    {"name": "Version", "type": "number", "options": {"precision": 0}},
    {"name": "File Link", "type": "url"},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[Deliverables]=$(extract_table_id "$DELIVERABLES_RESP")
ok "Deliverables table: ${TABLE_IDS[Deliverables]}"

# --- Content Calendar ---
log "Creating table: Content Calendar..."
CONTENT_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
  "name": "Content Calendar",
  "description": "Track all content across platforms",
  "fields": [
    {"name": "Post Title", "type": "singleLineText"},
    {"name": "Platform", "type": "singleSelect", "options": {"choices": [
      {"name": "LinkedIn", "color": "blueLight2"},
      {"name": "Facebook", "color": "cyanLight2"},
      {"name": "Instagram", "color": "orangeLight2"},
      {"name": "Email", "color": "tealLight2"},
      {"name": "Blog", "color": "greenLight2"}
    ]}},
    {"name": "Pillar", "type": "singleSelect", "options": {"choices": [
      {"name": "Teardown", "color": "redLight2"},
      {"name": "URL to Brief", "color": "blueLight2"},
      {"name": "Proof Object", "color": "greenLight2"},
      {"name": "Systems", "color": "yellowLight2"},
      {"name": "Offer/Story", "color": "orangeLight2"}
    ]}},
    {"name": "Series", "type": "singleSelect", "options": {"choices": [
      {"name": "From URL to Campaign", "color": "blueLight2"},
      {"name": "General", "color": "grayLight2"},
      {"name": "Guest/Collab", "color": "cyanLight2"}
    ]}},
    {"name": "Journey Stage", "type": "singleSelect", "options": {"choices": [
      {"name": "Problem-Aware", "color": "yellowLight2"},
      {"name": "Solution-Aware", "color": "blueLight2"},
      {"name": "Most-Aware", "color": "greenLight2"}
    ]}},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Idea", "color": "grayLight2"},
      {"name": "Draft", "color": "yellowLight2"},
      {"name": "Review", "color": "orangeLight2"},
      {"name": "Scheduled", "color": "blueLight2"},
      {"name": "Published", "color": "greenLight2"}
    ]}},
    {"name": "Publish Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
    {"name": "Post Copy", "type": "multilineText"},
    {"name": "CTA Type", "type": "singleSelect", "options": {"choices": [
      {"name": "Comment Trigger", "color": "blueLight2"},
      {"name": "DM Trigger", "color": "cyanLight2"},
      {"name": "Link", "color": "greenLight2"},
      {"name": "None", "color": "grayLight2"}
    ]}},
    {"name": "CTA Text", "type": "singleLineText"},
    {"name": "Engagement", "type": "number", "options": {"precision": 0}},
    {"name": "Leads Generated", "type": "number", "options": {"precision": 0}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[ContentCalendar]=$(extract_table_id "$CONTENT_RESP")
ok "Content Calendar table: ${TABLE_IDS[ContentCalendar]}"

# --- Leads ---
log "Creating table: Leads..."
LEADS_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
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
      {"name": "Email Opt-in", "color": "grayLight2"}
    ]}},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "New", "color": "blueLight2"},
      {"name": "Contacted", "color": "cyanLight2"},
      {"name": "Responded", "color": "tealLight2"},
      {"name": "Qualified", "color": "greenLight2"},
      {"name": "Converted", "color": "greenBright"},
      {"name": "Dead", "color": "grayLight2"}
    ]}},
    {"name": "Response Sent", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
    {"name": "Response Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[Leads]=$(extract_table_id "$LEADS_RESP")
ok "Leads table: ${TABLE_IDS[Leads]}"

# --- Proof Objects ---
log "Creating table: Proof Objects..."
PROOF_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
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
      {"name": "Before/After", "color": "orangeLight2"}
    ]}},
    {"name": "Permission Level", "type": "singleSelect", "options": {"choices": [
      {"name": "Full Public", "color": "greenLight2"},
      {"name": "Anonymized", "color": "yellowLight2"},
      {"name": "Process Only", "color": "grayLight2"}
    ]}},
    {"name": "Content", "type": "multilineText"},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Draft", "color": "yellowLight2"},
      {"name": "Approved", "color": "blueLight2"},
      {"name": "Published", "color": "greenLight2"}
    ]}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[ProofObjects]=$(extract_table_id "$PROOF_RESP")
ok "Proof Objects table: ${TABLE_IDS[ProofObjects]}"

# --- Invoices ---
log "Creating table: Invoices..."
INVOICES_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
  "name": "Invoices",
  "description": "Track all payments and invoicing",
  "fields": [
    {"name": "Invoice ID", "type": "singleLineText", "description": "Format: INV-YYYY-NNN"},
    {"name": "Type", "type": "singleSelect", "options": {"choices": [
      {"name": "Deposit", "color": "blueLight2"},
      {"name": "Final Payment", "color": "greenLight2"},
      {"name": "Add-on", "color": "cyanLight2"},
      {"name": "Tripwire", "color": "yellowLight2"},
      {"name": "Fit Check", "color": "orangeLight2"}
    ]}},
    {"name": "Amount", "type": "currency", "options": {"precision": 2, "symbol": "$"}},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Draft", "color": "grayLight2"},
      {"name": "Sent", "color": "blueLight2"},
      {"name": "Paid", "color": "greenLight2"},
      {"name": "Overdue", "color": "redLight2"},
      {"name": "Cancelled", "color": "grayLight2"}
    ]}},
    {"name": "Sent Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
    {"name": "Due Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
    {"name": "Paid Date", "type": "date", "options": {"dateFormat": {"name": "local"}}},
    {"name": "Payment Method", "type": "singleSelect", "options": {"choices": [
      {"name": "Stripe", "color": "blueLight2"},
      {"name": "Bank Transfer", "color": "greenLight2"},
      {"name": "Other", "color": "grayLight2"}
    ]}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[Invoices]=$(extract_table_id "$INVOICES_RESP")
ok "Invoices table: ${TABLE_IDS[Invoices]}"

# --- Email Sequences ---
log "Creating table: Email Sequences..."
EMAILS_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
  "name": "Email Sequences",
  "description": "Track email automation sequences and performance",
  "fields": [
    {"name": "Sequence Name", "type": "singleLineText"},
    {"name": "Trigger", "type": "singleSelect", "options": {"choices": [
      {"name": "Lead Magnet Download", "color": "blueLight2"},
      {"name": "Tripwire Purchase", "color": "greenLight2"},
      {"name": "Fit Check Booked", "color": "yellowLight2"},
      {"name": "Sprint Complete", "color": "tealLight2"},
      {"name": "Comment Trigger", "color": "cyanLight2"}
    ]}},
    {"name": "Email Count", "type": "number", "options": {"precision": 0}},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Draft", "color": "yellowLight2"},
      {"name": "Active", "color": "greenLight2"},
      {"name": "Paused", "color": "grayLight2"}
    ]}},
    {"name": "Open Rate", "type": "percent", "options": {"precision": 1}},
    {"name": "Click Rate", "type": "percent", "options": {"precision": 1}},
    {"name": "Conversion Rate", "type": "percent", "options": {"precision": 1}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[EmailSequences]=$(extract_table_id "$EMAILS_RESP")
ok "Email Sequences table: ${TABLE_IDS[EmailSequences]}"

# --- Templates ---
log "Creating table: Templates..."
TEMPLATES_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
  "name": "Templates",
  "description": "Master list of all templates and SOPs",
  "fields": [
    {"name": "Template Name", "type": "singleLineText"},
    {"name": "Category", "type": "singleSelect", "options": {"choices": [
      {"name": "Client-Facing", "color": "blueLight2"},
      {"name": "Internal SOP", "color": "greenLight2"},
      {"name": "Content Template", "color": "yellowLight2"},
      {"name": "Email Template", "color": "cyanLight2"},
      {"name": "Automation", "color": "orangeLight2"}
    ]}},
    {"name": "Version", "type": "number", "options": {"precision": 0}},
    {"name": "Status", "type": "singleSelect", "options": {"choices": [
      {"name": "Draft", "color": "yellowLight2"},
      {"name": "Active", "color": "greenLight2"},
      {"name": "Deprecated", "color": "grayLight2"}
    ]}},
    {"name": "File Link", "type": "url"},
    {"name": "Last Updated", "type": "date", "options": {"dateFormat": {"name": "local"}}},
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[Templates]=$(extract_table_id "$TEMPLATES_RESP")
ok "Templates table: ${TABLE_IDS[Templates]}"

# --- Metrics Dashboard ---
log "Creating table: Metrics Dashboard..."
METRICS_RESP=$(api_post "$API/meta/bases/$BASE_ID/tables" '{
  "name": "Metrics Dashboard",
  "description": "Weekly/monthly KPI tracking",
  "fields": [
    {"name": "Period", "type": "singleLineText", "description": "Format: W01-2026 or Jan-2026"},
    {"name": "Period Type", "type": "singleSelect", "options": {"choices": [
      {"name": "Weekly", "color": "blueLight2"},
      {"name": "Monthly", "color": "greenLight2"}
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
    {"name": "Notes", "type": "multilineText"}
  ]
}')
TABLE_IDS[MetricsDashboard]=$(extract_table_id "$METRICS_RESP")
ok "Metrics Dashboard table: ${TABLE_IDS[MetricsDashboard]}"

echo ""
log "All 12 tables created. Setting up relationships..."

# =============================================================================
# STEP 3: Add linked record fields (relationships between tables)
# =============================================================================

add_link_field() {
  local table_id="$1"
  local field_name="$2"
  local linked_table_id="$3"
  local prefer_single="${4:-false}"

  local options
  if [[ "$prefer_single" == "true" ]]; then
    options="{\"linkedTableId\": \"$linked_table_id\", \"prefersSingleRecordLink\": true}"
  else
    options="{\"linkedTableId\": \"$linked_table_id\"}"
  fi

  api_post "$API/meta/bases/$BASE_ID/tables/$table_id/fields" \
    "{\"name\": \"$field_name\", \"type\": \"multipleRecordLinks\", \"options\": $options}" > /dev/null
  ok "  Link: $field_name"
}

# Accounts → Contacts, Deals, Sprints
log "Linking Accounts..."
add_link_field "${TABLE_IDS[Accounts]}" "Contacts" "${TABLE_IDS[Contacts]}"
add_link_field "${TABLE_IDS[Accounts]}" "Deals" "${TABLE_IDS[Deals]}"
add_link_field "${TABLE_IDS[Accounts]}" "Sprints" "${TABLE_IDS[Sprints]}"

# Contacts → Accounts (already created as reverse of above)
# Contacts → Deals (not yet — Deals.Contact link will create reverse)

# Deals → Account, Contact, Sprint
log "Linking Deals..."
add_link_field "${TABLE_IDS[Deals]}" "Account" "${TABLE_IDS[Accounts]}" "true"
add_link_field "${TABLE_IDS[Deals]}" "Contact" "${TABLE_IDS[Contacts]}" "true"
add_link_field "${TABLE_IDS[Deals]}" "Sprint" "${TABLE_IDS[Sprints]}" "true"

# Sprints → Account, Deal, Deliverables
log "Linking Sprints..."
add_link_field "${TABLE_IDS[Sprints]}" "Account" "${TABLE_IDS[Accounts]}" "true"
add_link_field "${TABLE_IDS[Sprints]}" "Deal" "${TABLE_IDS[Deals]}" "true"
add_link_field "${TABLE_IDS[Sprints]}" "Deliverables" "${TABLE_IDS[Deliverables]}"

# Deliverables → Sprint
log "Linking Deliverables..."
add_link_field "${TABLE_IDS[Deliverables]}" "Sprint" "${TABLE_IDS[Sprints]}" "true"

# Leads → Source Post (Content Calendar), Contact
log "Linking Leads..."
add_link_field "${TABLE_IDS[Leads]}" "Source Post" "${TABLE_IDS[ContentCalendar]}" "true"
add_link_field "${TABLE_IDS[Leads]}" "Contact" "${TABLE_IDS[Contacts]}" "true"

# Proof Objects → Sprint, Account, Used In (Content Calendar)
log "Linking Proof Objects..."
add_link_field "${TABLE_IDS[ProofObjects]}" "Sprint" "${TABLE_IDS[Sprints]}" "true"
add_link_field "${TABLE_IDS[ProofObjects]}" "Account" "${TABLE_IDS[Accounts]}" "true"
add_link_field "${TABLE_IDS[ProofObjects]}" "Used In" "${TABLE_IDS[ContentCalendar]}"

# Invoices → Deal, Account
log "Linking Invoices..."
add_link_field "${TABLE_IDS[Invoices]}" "Deal" "${TABLE_IDS[Deals]}" "true"
add_link_field "${TABLE_IDS[Invoices]}" "Account" "${TABLE_IDS[Accounts]}" "true"

# Content Calendar → Repurposed From (self-link)
log "Linking Content Calendar (self-link)..."
add_link_field "${TABLE_IDS[ContentCalendar]}" "Repurposed From" "${TABLE_IDS[ContentCalendar]}"

echo ""
ok "All relationships created."

# =============================================================================
# STEP 4: Create views
# =============================================================================
log "Creating views..."

create_view() {
  local table_id="$1"
  local view_name="$2"
  local view_type="${3:-grid}"

  api_post "$API/meta/bases/$BASE_ID/tables/$table_id/views" \
    "{\"name\": \"$view_name\", \"type\": \"$view_type\"}" > /dev/null
  ok "  View: $view_name ($view_type)"
}

# Accounts views
log "Accounts views..."
create_view "${TABLE_IDS[Accounts]}" "Active Clients" "grid"
create_view "${TABLE_IDS[Accounts]}" "Pipeline" "grid"

# Deals views
log "Deals views..."
create_view "${TABLE_IDS[Deals]}" "Pipeline Board" "kanban"
create_view "${TABLE_IDS[Deals]}" "Won This Month" "grid"

# Sprints views
log "Sprints views..."
create_view "${TABLE_IDS[Sprints]}" "Active Sprints" "grid"
create_view "${TABLE_IDS[Sprints]}" "Sprint Board" "kanban"

# Content Calendar views
log "Content Calendar views..."
create_view "${TABLE_IDS[ContentCalendar]}" "Publishing Queue" "grid"
create_view "${TABLE_IDS[ContentCalendar]}" "Content Board" "kanban"
create_view "${TABLE_IDS[ContentCalendar]}" "By Pillar" "grid"

# Leads views
log "Leads views..."
create_view "${TABLE_IDS[Leads]}" "New Leads" "grid"
create_view "${TABLE_IDS[Leads]}" "By Trigger" "grid"

# Metrics views
log "Metrics Dashboard views..."
create_view "${TABLE_IDS[MetricsDashboard]}" "Weekly View" "grid"

echo ""
ok "All views created."

# =============================================================================
# STEP 5: Seed initial content data (the 5 cornerstone posts)
# =============================================================================
log "Seeding Content Calendar with Week 1 cornerstone posts..."

seed_post() {
  local title="$1"
  local pillar="$2"
  local stage="$3"
  local cta_type="$4"
  local cta_text="$5"

  api_post "$API/v0/$BASE_ID/Content%20Calendar" \
    "{\"fields\": {
      \"Post Title\": \"$title\",
      \"Platform\": \"LinkedIn\",
      \"Pillar\": \"$pillar\",
      \"Series\": \"From URL to Campaign\",
      \"Journey Stage\": \"$stage\",
      \"Status\": \"Draft\",
      \"CTA Type\": \"$cta_type\",
      \"CTA Text\": \"$cta_text\"
    }}" > /dev/null
  ok "  Post: $title"
}

seed_post "Why Your Hooks All Sound the Same" "Teardown" "Problem-Aware" "Comment Trigger" "Comment TEARDOWN"
seed_post "3 Things I Pull From Any URL" "URL to Brief" "Problem-Aware" "Comment Trigger" "Comment SNAPSHOT + your URL"
seed_post "What a 14-Day Sprint Produces" "Proof Object" "Solution-Aware" "DM Trigger" "DM SPRINT"
seed_post "Why Creative Projects Fail Before Delivery" "Systems" "Solution-Aware" "Comment Trigger" "Comment SCOPE"
seed_post "I Built This Because I Kept Seeing 3 Problems" "Offer/Story" "Solution-Aware" "Comment Trigger" "Comment SPRINT"

echo ""
ok "Content Calendar seeded with 5 cornerstone posts."

# =============================================================================
# STEP 6: Seed Templates table
# =============================================================================
log "Seeding Templates table..."

seed_template() {
  local name="$1"
  local category="$2"

  api_post "$API/v0/$BASE_ID/Templates" \
    "{\"fields\": {
      \"Template Name\": \"$name\",
      \"Category\": \"$category\",
      \"Version\": 1,
      \"Status\": \"Active\"
    }}" > /dev/null
  ok "  Template: $name"
}

seed_template "Sprint Scope Agreement" "Client-Facing"
seed_template "Sprint Intake Checklist" "Client-Facing"
seed_template "Revision Policy" "Client-Facing"
seed_template "QA Checklist" "Internal SOP"
seed_template "Proof Capture Checklist" "Internal SOP"
seed_template "Case Study Skeleton" "Content Template"
seed_template "URL to ICP Snapshot" "Content Template"
seed_template "7 Hooks Guide" "Content Template"
seed_template "Hook Pack ($7)" "Content Template"

echo ""
ok "Templates table seeded."

# =============================================================================
# DONE
# =============================================================================
echo ""
echo "============================================"
echo ""
ok "Get Fractional OS — Airtable base is live!"
echo ""
echo "  Base ID:  $BASE_ID"
echo "  Base URL: https://airtable.com/$BASE_ID"
echo ""
echo "  Tables created: 12"
echo "  Relationships:  17 linked fields"
echo "  Views:          12 custom views"
echo "  Seed data:      5 cornerstone posts + 9 templates"
echo ""
echo "  Next steps:"
echo "    1. Open https://airtable.com/$BASE_ID"
echo "    2. Set view filters (Active Clients, Won This Month, etc.)"
echo "    3. Configure Kanban grouping fields (Stage for Deals, Status for Sprints)"
echo "    4. Build Interface Designer dashboards (see below)"
echo ""
echo "  Manual steps (not available via API):"
echo "    - Set up Automations (Settings → Automations)"
echo "    - Build Interface Designer pages"
echo "    - Configure view filters and sorts"
echo "    - Set Kanban group-by fields"
echo ""
echo "  Base ID saved to: .airtable-base-id"
echo "============================================"
