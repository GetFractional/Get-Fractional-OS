# Airtable Setup Guide — Get Fractional OS

> Step-by-step instructions for building the Airtable base.
> Base name: "Get Fractional OS"
> This is the central data layer. Everything else connects to it.

---

## STEP 1: Create the Base

1. Go to [airtable.com](https://airtable.com) → create new base
2. Name it: **Get Fractional OS**
3. Delete the default table

---

## STEP 2: Create All 12 Tables

Create these tables in order (relationships depend on order):

### Table 1: Accounts
**Purpose:** Companies/brands that are clients or prospects.

| Field Name | Field Type | Notes |
|---|---|---|
| Account Name | Single line text | Primary field |
| Website URL | URL | |
| Industry | Single select | Options: DTC Skincare, DTC Supplements, DTC Food & Bev, DTC Apparel, SaaS, Other |
| Status | Single select | Options: Prospect, Active Client, Past Client, Churned |
| Primary Contact | Link to Contacts | |
| Deals | Link to Deals | |
| Sprints | Link to Sprints | |
| Source | Single select | Options: LinkedIn, Referral, Inbound, Cold Outreach, Other |
| Notes | Long text | |
| Created | Created time | |

### Table 2: Contacts
**Purpose:** Individual people at accounts.

| Field Name | Field Type | Notes |
|---|---|---|
| Full Name | Single line text | Primary field |
| Email | Email | |
| Phone | Phone | |
| LinkedIn URL | URL | |
| Account | Link to Accounts | |
| Role/Title | Single line text | |
| Is Decision Maker | Checkbox | |
| Lead Score | Number (integer) | 0-100 |
| Lead Source | Single select | Options: LinkedIn Comment, DM, Lead Magnet, Tripwire, Referral, Fit Check, Other |
| Tags | Multiple select | Options: TEARDOWN, SNAPSHOT, SPRINT, SCOPE, Hook Pack Buyer, Fit Check Booked, Email Subscriber |
| Engagement Notes | Long text | |
| Created | Created time | |
| Last Contacted | Date | |

### Table 3: Deals
**Purpose:** Pipeline tracking for all offers.

| Field Name | Field Type | Notes |
|---|---|---|
| Deal Name | Single line text | Primary field, format: "Account - Offer Type" |
| Account | Link to Accounts | |
| Contact | Link to Contacts | |
| Offer | Single select | Options: Fit Check ($97), Creative Sprint ($3500-$8000), Monthly Retainer, Hook Pack ($7), Custom |
| Stage | Single select | Options: Lead, Qualified, Fit Check Scheduled, Fit Check Complete, Proposal Sent, Scope Signed, Deposit Paid, In Progress, Delivered, Closed Won, Closed Lost |
| Amount | Currency (USD) | |
| Deposit Paid | Checkbox | |
| Final Paid | Checkbox | |
| Close Date | Date | |
| Lost Reason | Single select | Options: Price, Timing, Scope Mismatch, Went with Agency, No Response, Other |
| Sprint | Link to Sprints | |
| Notes | Long text | |
| Created | Created time | |

### Table 4: Sprints
**Purpose:** Active and completed sprint engagements.

| Field Name | Field Type | Notes |
|---|---|---|
| Sprint Name | Single line text | Primary field, format: "Account - Sprint #N" |
| Account | Link to Accounts | |
| Deal | Link to Deals | |
| Status | Single select | Options: Intake Pending, In Progress, Day 3 Review, Day 10 Review, Revision 1, Revision 2, Delivered, Paused |
| Start Date | Date | |
| Day 3 Milestone | Date | Formula or manual |
| Day 10 Milestone | Date | Formula or manual |
| Due Date | Date | 14 days from start |
| Intake Received | Checkbox | |
| Intake Status | Single select | Options: Not Sent, Sent, Partial, Complete |
| QA Status | Single select | Options: Not Started, In Progress, Passed, Failed |
| Deliverables | Link to Deliverables | |
| Proof Permission | Single select | Options: Full Public, Anonymized, Process Only |
| Pause Reason | Long text | |
| Client Satisfaction | Rating (1-5) | |
| Notes | Long text | |

### Table 5: Deliverables
**Purpose:** Individual deliverable items within sprints.

| Field Name | Field Type | Notes |
|---|---|---|
| Deliverable Name | Single line text | Primary field |
| Sprint | Link to Sprints | |
| Type | Single select | Options: ICP Brief, Objection Map, Ad Angles, Hooks, Ad Concepts, LP Copy Kit, Testing Plan, Other |
| Status | Single select | Options: Not Started, In Progress, Draft, QA Review, Delivered, Revised |
| Version | Number (integer) | |
| File Link | URL | Link to Google Doc, Notion, or file |
| Notes | Long text | |

### Table 6: Content Calendar
**Purpose:** Track all content across platforms.

| Field Name | Field Type | Notes |
|---|---|---|
| Post Title | Single line text | Primary field |
| Platform | Single select | Options: LinkedIn, Facebook, Instagram, Email, Blog |
| Pillar | Single select | Options: Teardown, URL to Brief, Proof Object, Systems, Offer/Story |
| Series | Single select | Options: From URL to Campaign, General, Guest/Collab |
| Journey Stage | Single select | Options: Problem-Aware, Solution-Aware, Most-Aware |
| Status | Single select | Options: Idea, Draft, Review, Scheduled, Published |
| Publish Date | Date | |
| Post Copy | Long text | |
| CTA Type | Single select | Options: Comment Trigger, DM Trigger, Link, None |
| CTA Text | Single line text | |
| Engagement | Number (integer) | Likes + comments + shares |
| Leads Generated | Number (integer) | |
| Repurposed From | Link to Content Calendar | Self-link for repurpose tracking |
| Notes | Long text | |

### Table 7: Leads
**Purpose:** All inbound leads before they become contacts/deals.

| Field Name | Field Type | Notes |
|---|---|---|
| Name | Single line text | Primary field |
| Email | Email | |
| URL Submitted | URL | For SNAPSHOT leads |
| Source Post | Link to Content Calendar | Which post generated the lead |
| Trigger Word | Single select | Options: TEARDOWN, SNAPSHOT, SPRINT, SCOPE, Hook Pack, Fit Check, Email Opt-in |
| Status | Single select | Options: New, Contacted, Responded, Qualified, Converted, Dead |
| Contact | Link to Contacts | Linked when converted |
| Response Sent | Checkbox | |
| Response Date | Date | |
| Notes | Long text | |
| Created | Created time | |

### Table 8: Proof Objects
**Purpose:** Track proof/social proof for marketing use.

| Field Name | Field Type | Notes |
|---|---|---|
| Proof Title | Single line text | Primary field |
| Sprint | Link to Sprints | |
| Account | Link to Accounts | |
| Type | Single select | Options: Deliverable Count, Timeline, Client Quote, Result Metric, Process Demo, Before/After |
| Permission Level | Single select | Options: Full Public, Anonymized, Process Only |
| Content | Long text | The actual proof statement or asset |
| Used In | Link to Content Calendar | Posts that reference this proof |
| Status | Single select | Options: Draft, Approved, Published |
| Created | Created time | |

### Table 9: Invoices
**Purpose:** Track all payments and invoicing.

| Field Name | Field Type | Notes |
|---|---|---|
| Invoice ID | Single line text | Primary field, format: "INV-YYYY-NNN" |
| Deal | Link to Deals | |
| Account | Link to Accounts | |
| Type | Single select | Options: Deposit, Final Payment, Add-on, Tripwire, Fit Check |
| Amount | Currency (USD) | |
| Status | Single select | Options: Draft, Sent, Paid, Overdue, Cancelled |
| Sent Date | Date | |
| Due Date | Date | |
| Paid Date | Date | |
| Payment Method | Single select | Options: Stripe, Bank Transfer, Other |
| Notes | Long text | |

### Table 10: Email Sequences
**Purpose:** Track email automation sequences and performance.

| Field Name | Field Type | Notes |
|---|---|---|
| Sequence Name | Single line text | Primary field |
| Trigger | Single select | Options: Lead Magnet Download, Tripwire Purchase, Fit Check Booked, Sprint Complete, Comment Trigger |
| Email Count | Number (integer) | |
| Status | Single select | Options: Draft, Active, Paused |
| Open Rate | Percent | |
| Click Rate | Percent | |
| Conversion Rate | Percent | |
| Notes | Long text | |

### Table 11: Templates
**Purpose:** Master list of all templates and SOPs.

| Field Name | Field Type | Notes |
|---|---|---|
| Template Name | Single line text | Primary field |
| Category | Single select | Options: Client-Facing, Internal SOP, Content Template, Email Template, Automation |
| Version | Number | |
| Status | Single select | Options: Draft, Active, Deprecated |
| File Link | URL | |
| Last Updated | Date | |
| Notes | Long text | |

### Table 12: Metrics Dashboard
**Purpose:** Weekly/monthly KPI tracking.

| Field Name | Field Type | Notes |
|---|---|---|
| Period | Single line text | Primary field, format: "W01-2026" or "Jan-2026" |
| Period Type | Single select | Options: Weekly, Monthly |
| New Leads | Number (integer) | |
| Fit Checks Booked | Number (integer) | |
| Fit Checks Completed | Number (integer) | |
| Sprints Sold | Number (integer) | |
| Revenue | Currency (USD) | |
| Content Published | Number (integer) | |
| Total Engagement | Number (integer) | |
| Email Subscribers | Number (integer) | |
| Tripwire Sales | Number (integer) | |
| Active Sprints | Number (integer) | |
| Notes | Long text | |

---

## STEP 3: Create Core Views

For each table, create these views beyond the default Grid view:

**Accounts:**
- "Active Clients" — filter: Status = Active Client
- "Pipeline" — filter: Status = Prospect, grouped by Source

**Deals:**
- "Pipeline Board" — Kanban view, grouped by Stage
- "Won This Month" — filter: Stage = Closed Won, Close Date = this month

**Sprints:**
- "Active Sprints" — filter: Status ≠ Delivered, sorted by Due Date
- "Sprint Board" — Kanban view, grouped by Status

**Content Calendar:**
- "Publishing Queue" — filter: Status = Scheduled, sorted by Publish Date
- "Content Board" — Kanban view, grouped by Status
- "By Pillar" — grouped by Pillar

**Leads:**
- "New Leads" — filter: Status = New, sorted by Created (newest first)
- "By Trigger" — grouped by Trigger Word

**Metrics Dashboard:**
- "Weekly View" — filter: Period Type = Weekly, sorted by Period (newest first)

---

## STEP 4: Set Up Automations (Native Airtable)

1. **New Lead Alert:** When record created in Leads → send email notification to Matt
2. **Sprint Milestone Reminder:** When Sprint Status changes → send email with next steps
3. **Overdue Invoice Alert:** When Invoice Due Date is past and Status ≠ Paid → send notification

---

## STEP 5: Generate API Key

1. Go to airtable.com/create/tokens
2. Create a personal access token with scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
3. Save the token — you'll need it for n8n integration
4. Note the Base ID (in the URL when viewing the base: `app...`)
