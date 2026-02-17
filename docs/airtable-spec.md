# Airtable OS Spec — Get Fractional OS (Core)

## 1. Base Configuration

- **Base name:** `Get Fractional OS (Core)`
- **One base, no fragmentation.** All tables live in a single base for simplicity and cross-table linking.
- **Naming convention:** PascalCase for table names, Title Case for field names.

---

## 2. Tables, Fields, Types & Formulas

### Table 1: Accounts

> SSOT for brand identity. One record per brand/client.

| Field Name | Type | Notes |
|---|---|---|
| Account Name | Single line text | **Primary field** |
| Website URL | URL | Used as trigger for URL Intake workflow |
| Primary ICP | Link to ICPs | Single link |
| Brand Voice Notes | Long text | Rich text enabled |
| Offer Stack | Link to Offers | Multiple links |
| Status | Single select | Options: `Prospect`, `Active`, `Paused`, `Churned` |
| Case Study Permission | Single select | Options: `Full Public`, `Anonymized`, `Process Only`, `None` |
| Asset Folder Link | URL | Google Drive / Dropbox link |
| Zoho Account ID | Single line text | Populated by n8n sync |
| Created | Created time | Auto |
| Last Modified | Last modified time | Auto |

---

### Table 2: ICPs

> ICP profiles linked to Accounts.

| Field Name | Type | Notes |
|---|---|---|
| ICP Name | Single line text | **Primary field** |
| Account | Link to Accounts | |
| JTBD - Functional | Long text | |
| JTBD - Emotional | Long text | |
| JTBD - Social | Long text | |
| Objections | Link to Objections | Multiple links |
| Trigger Events | Long text | |
| Proof Needed | Long text | What proof resolves their objections |
| Platform Notes | Long text | LI / FB / IG behavioral notes |
| Demographics | Long text | Firmographics + psychographics |

---

### Table 3: Objections

> Reusable objection library linked to ICPs.

| Field Name | Type | Notes |
|---|---|---|
| Objection | Single line text | **Primary field** |
| ICP | Link to ICPs | Multiple links (objection can apply to multiple ICPs) |
| Rebuttal Angles | Long text | |
| Proof Type | Single select | Options: `Screenshot`, `Metric`, `Story`, `Before/After`, `Testimonial` |
| Proof Asset Link | URL | Link to proof object |

---

### Table 4: Offers

> Offer catalog — internal and client-specific.

| Field Name | Type | Notes |
|---|---|---|
| Offer Name | Single line text | **Primary field** |
| Account | Link to Accounts | Use "Get Fractional" for internal offers |
| Tier | Single select | Options: `Lead Magnet`, `Tripwire`, `Core`, `Retainer`, `Install` |
| Price | Currency | |
| Price Notes | Single line text | e.g., "Founders promo $3.5k" |
| Promise | Long text | One-sentence promise |
| Scope Boundaries | Long text | What is explicitly excluded |
| Deliverables | Link to Campaign Kits | Or long text list if no kit yet |
| Deliverables Description | Long text | Bulleted list of what client gets |
| Timeline | Single line text | e.g., "14 days" |
| SOP Link | URL | Link to fulfillment SOP |
| Active | Checkbox | Is this offer currently being sold? |

---

### Table 5: Sprints

> Project records for active fulfillment.

| Field Name | Type | Notes |
|---|---|---|
| Sprint Name | Single line text | **Primary field** — format: `[Account] - [Offer] - [Date]` |
| Account | Link to Accounts | |
| Offer | Link to Offers | |
| Stage | Single select | Options: `Intake`, `Research`, `Concepts`, `Production`, `QA`, `Review`, `Delivered`, `Proof Capture`, `Complete` |
| Start Date | Date | |
| Due Date | Date | |
| Day 3 Review Date | Formula | `DATEADD({Start Date}, 3, 'days')` |
| Day 10 Review Date | Formula | `DATEADD({Start Date}, 10, 'days')` |
| Revision Rounds Remaining | Number | Default: 2 |
| Approval Needed | Checkbox | Set true at review milestones |
| Intake Complete | Checkbox | All required inputs received |
| URL Provided | URL | Client's website/product URL |
| Client Brief | Long text | |
| Internal Notes | Long text | |
| Proof Captured | Checkbox | |
| Proof Objects | Link to Content Pipeline | Links to proof-type content |
| Campaign Kit | Link to Campaign Kits | |

---

### Table 6: Campaign Kits

> Deliverable packages tied to Sprints.

| Field Name | Type | Notes |
|---|---|---|
| Kit Name | Single line text | **Primary field** |
| Sprint | Link to Sprints | |
| Angles Count | Count | Count of linked records (or manual number) |
| Hooks Count | Number | Manual entry |
| Assets | Long text | Or link to asset table if needed later |
| Testing Plan | Long text | Naming conventions, test matrix |
| Testing Plan Link | URL | External doc link |
| Brand Brief | Long text | 1–2 page brand/ICP brief |
| Objection Map | Long text | |
| Landing Page Copy | Long text | Or link to doc |
| Status | Single select | Options: `In Progress`, `Review`, `Final`, `Delivered` |

---

### Table 7: Content Pipeline

> All content across all platforms — single pipeline.

| Field Name | Type | Notes |
|---|---|---|
| Post Title | Single line text | **Primary field** |
| Platform | Single select | Options: `LinkedIn`, `Facebook`, `Instagram`, `All` |
| Pillar | Single select | Options: `Teardowns`, `URL to Campaign`, `Proof Objects`, `Systems & Governance`, `Offer Craft`, `Experiment Design`, `Operator Moments`, `Tooling Reality` |
| Journey Stage | Single select | Options: `Unaware`, `Problem-Aware`, `Solution-Aware`, `Product-Aware`, `Most-Aware` |
| Draft | Long text | Rich text enabled |
| Status | Single select | Options: `Idea`, `Draft`, `Needs QA`, `Needs Approval`, `Scheduled`, `Published`, `Rejected` |
| Publish Date | Date | Target or actual publish date |
| Post URL | URL | Filled after publishing |
| CTA Type | Single select | Options: `Comment CTA`, `DM CTA`, `Link CTA`, `No CTA` |
| CTA Text | Single line text | e.g., "Comment SPRINT" |
| Account | Link to Accounts | Optional — for client-specific content |
| Sprint | Link to Sprints | Optional — for proof objects |
| Content Type | Single select | Options: `Teardown Post`, `Demo/Walkthrough`, `Case Study`, `Framework`, `Build-in-Public`, `Relatable`, `Carousel`, `Reel Script`, `Lead Magnet Promo` |
| Tone QA Complete | Checkbox | |
| Claims QA Complete | Checkbox | |
| Privacy QA Complete | Checkbox | |
| Approval Notes | Long text | Reviewer feedback |
| Repurposed From | Link to Content Pipeline | Self-link for tracking repurposing chain |

---

### Table 8: Engagement Inbox

> Captures social interactions for lead qualification.

| Field Name | Type | Notes |
|---|---|---|
| Engagement ID | Autonumber | **Primary field** |
| Source | Single select | Options: `LinkedIn`, `Facebook`, `Instagram`, `Other` |
| Type | Single select | Options: `Comment`, `DM`, `Form Submission`, `Email` |
| Author Handle | Single line text | |
| Author Name | Single line text | |
| Content | Long text | The actual message/comment |
| Linked Post | Link to Content Pipeline | Which post triggered this |
| Lead Created | Checkbox | |
| Lead Record | Link to Leads | |
| Status | Single select | Options: `New`, `Queued`, `Replied`, `Converted`, `Closed`, `Spam` |
| Owner | Collaborator | |
| Notes | Long text | |
| Created | Created time | Auto |

---

### Table 9: Leads

> Pre-CRM lead tracking in Airtable, synced to Zoho.

| Field Name | Type | Notes |
|---|---|---|
| Name / Handle | Single line text | **Primary field** |
| Email | Email | |
| Source | Single select | Options: `DM`, `Comment`, `Form`, `Referral`, `Inbound`, `Outbound` |
| Source Platform | Single select | Options: `LinkedIn`, `Facebook`, `Instagram`, `Website`, `Other` |
| Source Post | Link to Content Pipeline | Which content drove this lead |
| Account Interest | Link to Offers | Which offer they're interested in |
| Stage | Single select | Options: `New`, `Fit Check Scheduled`, `Fit Check Done`, `Proposal Sent`, `Won`, `Lost` |
| Zoho ID | Single line text | Populated by n8n — links to Zoho Lead/Contact |
| Notes | Long text | |
| Next Step | Single line text | |
| Next Step Date | Date | |
| Engagement Records | Link to Engagement Inbox | |
| Fit Check Score | Number | Optional — 1-10 rating |
| Lost Reason | Single select | Options: `Budget`, `Timing`, `Scope Mismatch`, `No Response`, `Competitor`, `Other` |
| Created | Created time | Auto |

---

### Table 10: Knowledge Library

> Lightweight RAG-like reference store — no vector DB needed at MVP.

| Field Name | Type | Notes |
|---|---|---|
| Title | Single line text | **Primary field** |
| Type | Single select | Options: `Doc`, `Transcript`, `Link`, `Screenshot`, `Template`, `SOP` |
| Tags | Multiple select | Options: `Brand`, `ICP`, `Offer`, `Creative`, `Systems`, `Governance`, `Case Study`, `Competitor`, `Research` |
| Summary | Long text | AI field: auto-summarize if using Airtable AI |
| Key Excerpts | Long text | AI field: extract key points |
| Source Link | URL | |
| Source File | Attachment | |
| Related Account | Link to Accounts | |
| Related Offer | Link to Offers | |
| Related Sprint | Link to Sprints | |
| Created | Created time | Auto |

---

### Table 11: System Logs

> Audit trail for all automations. Every n8n workflow and Airtable automation writes here.

| Field Name | Type | Notes |
|---|---|---|
| Log ID | Autonumber | **Primary field** |
| Severity | Single select | Options: `Info`, `Warn`, `Error`, `Critical` |
| System | Single select | Options: `Airtable`, `n8n`, `Zoho`, `Manual`, `Other` |
| Workflow | Single line text | e.g., "Lead Capture Upsert", "URL Intake Research" |
| Message | Long text | Human-readable description |
| Record Link | URL | Deep link to the relevant Airtable/Zoho record |
| Payload Excerpt | Long text | Truncated payload for debugging (no full PII) |
| Status | Single select | Options: `New`, `Investigating`, `Resolved`, `Won't Fix` |
| Retry Count | Number | How many retries were attempted |
| Owner | Collaborator | Who is investigating |
| Resolution Notes | Long text | |
| Timestamp | Created time | Auto |

---

## 3. Relationships Map

```
Accounts ──1:N──▶ ICPs ──N:M──▶ Objections
    │
    ├──1:N──▶ Sprints ──N:1──▶ Offers
    │             │
    │             └──1:N──▶ Campaign Kits
    │
    ├──1:N──▶ Content Pipeline
    │
    ├──1:N──▶ Leads ──────────▶ Zoho CRM (via Zoho ID)
    │
    └──1:N──▶ Knowledge Library

Engagement Inbox ──N:1──▶ Content Pipeline
                 ──N:1──▶ Leads

System Logs ── standalone (linked via URL field to any record)
```

### SSOT Rules (Recap)

1. **Brand/ICP/Objection data** → Airtable is SSOT
2. **Offer definitions** → Airtable is SSOT
3. **Sprint fulfillment tracking** → Airtable is SSOT
4. **Content drafts and status** → Airtable is SSOT
5. **Lead contact details and deal stage** → Zoho is SSOT; Airtable stores `Zoho ID` as reference
6. **Lead origin/source** → Airtable captures first, n8n syncs to Zoho
7. **Audit trail** → System Logs table in Airtable is SSOT

---

## 4. Views

### Accounts Table
| View Name | Type | Filter/Sort |
|---|---|---|
| All Accounts | Grid | Default |
| Active Clients | Grid | Status = "Active" |
| Prospects | Grid | Status = "Prospect", sorted by Created desc |

### Sprints Table
| View Name | Type | Filter/Sort |
|---|---|---|
| Sprint In Flight | Kanban | Grouped by Stage |
| Needs Approval | Grid | Approval Needed = checked |
| My Active Sprints | Grid | Stage NOT IN ("Complete", "Proof Capture"), sorted by Due Date |
| Overdue | Grid | Due Date < TODAY() AND Stage NOT IN ("Delivered", "Complete") |

### Content Pipeline Table
| View Name | Type | Filter/Sort |
|---|---|---|
| All Content | Grid | Default |
| Needs QA | Grid | Status = "Needs QA" |
| Needs Approval | Grid | Status = "Needs Approval" |
| Ready to Publish | Grid | Status = "Scheduled", sorted by Publish Date |
| Published | Grid | Status = "Published", sorted by Publish Date desc |
| Ideas Backlog | Grid | Status = "Idea" |
| By Platform | Kanban | Grouped by Platform |
| By Pillar | Kanban | Grouped by Pillar |
| This Week | Calendar | Publish Date, filtered to current week |

### Engagement Inbox
| View Name | Type | Filter/Sort |
|---|---|---|
| New | Grid | Status = "New", sorted by Created desc |
| Queued | Grid | Status = "Queued" |
| All Engagement | Grid | Default |

### Leads Table
| View Name | Type | Filter/Sort |
|---|---|---|
| All Leads | Grid | Default |
| Needs Follow-up | Grid | Stage NOT IN ("Won", "Lost") AND Next Step Date <= TODAY() |
| By Stage | Kanban | Grouped by Stage |
| New This Week | Grid | Created within last 7 days |
| Won | Grid | Stage = "Won" |
| Lost | Grid | Stage = "Lost" |

### System Logs Table
| View Name | Type | Filter/Sort |
|---|---|---|
| Errors Last 7 Days | Grid | Severity IN ("Error", "Critical") AND Timestamp within last 7 days |
| All Logs | Grid | Sorted by Timestamp desc |
| Unresolved | Grid | Status IN ("New", "Investigating") |
| By Workflow | Kanban | Grouped by Workflow |

---

## 5. Interfaces Plan (Omni-Ready)

### Interface 1: Daily Cockpit

> Matt's home screen. Everything that needs attention today.

| Section | Source | Display |
|---|---|---|
| Today's Approvals | Content Pipeline (Status = "Needs Approval") + Sprints (Approval Needed = true) | List with quick-action buttons |
| Engagement Queue | Engagement Inbox (Status = "New") | List, sorted by Created desc, 10 most recent |
| Leads Needing Follow-up | Leads (Next Step Date <= TODAY()) | List with stage + next step |
| Error Log | System Logs (Severity IN Error/Critical, Status = New) | Compact list with severity badge |
| Sprints In Flight | Sprints (Stage NOT IN Complete) | Summary cards with stage + due date |
| Content Calendar | Content Pipeline (Status = Scheduled, next 7 days) | Timeline or list |

### Interface 2: Post Builder Wizard

> Guided content creation flow.

| Step | Component | Source |
|---|---|---|
| 1. Select Pillar | Button group / dropdown | Content Pipeline.Pillar options |
| 2. Select Journey Stage | Button group / dropdown | Content Pipeline.Journey Stage options |
| 3. Select CTA Type | Dropdown | Content Pipeline.CTA Type options |
| 4. Write Draft | Long text editor | Content Pipeline.Draft |
| 5. Tone QA Checklist | Checkbox group | Tone QA, Claims QA, Privacy QA fields |
| 6. Submit for Approval | Button | Sets Status = "Needs QA" |

### Interface 3: Offer Builder Wizard

> Define and document offers.

| Step | Component | Source |
|---|---|---|
| 1. Select Tier | Dropdown | Offers.Tier options |
| 2. Define Promise | Text input | Offers.Promise |
| 3. Set Scope Boundaries | Long text | Offers.Scope Boundaries |
| 4. List Deliverables | Long text | Offers.Deliverables Description |
| 5. Set Price + Timeline | Number + text | Offers.Price, Offers.Timeline |
| 6. Link SOP | URL input | Offers.SOP Link |

### Interface 4: Sprint Delivery Cockpit

> Per-sprint operational view.

| Section | Component | Source |
|---|---|---|
| Sprint Header | Record summary | Sprint Name, Account, Offer, Stage, Dates |
| Intake Completeness | Progress bar / checklist | URL Provided, Client Brief filled, Intake Complete |
| Stage Checklist | Linked checklist | Stage-specific tasks (see Runbook) |
| Revision Counter | Number display | Revision Rounds Remaining (highlighted if 0) |
| Deliverables | Linked Campaign Kit | Kit status, assets, testing plan |
| Proof Capture Prompts | Checklist | Output count, before/after, teardown logged, case study permission |
| Approval Actions | Button | Set Approval Needed, advance Stage |

### Interface 5: Client Portal

> Shared read-only view per client.

| Section | What Client Sees | What Client Does NOT See |
|---|---|---|
| Sprint Status | Current stage, due date, next milestone | Internal notes, margin data |
| Deliverables | Final deliverable files/links | Draft iterations |
| Timeline | Key dates (concept review, draft review, delivery) | Exact hours logged |
| Approvals | Items awaiting their feedback | QA checklists |
| **Access method:** Shared Airtable Interface link, filtered by Account | | |

### Interface 6: KPI Dashboard

> Basic operational metrics.

| Metric | Source | Display |
|---|---|---|
| Posts Published This Week | Content Pipeline (Status = Published, last 7 days) | Count |
| Posts Published This Month | Content Pipeline (Status = Published, last 30 days) | Count |
| Fit Checks Booked | Leads (Stage = "Fit Check Scheduled") | Count |
| Sprints Sold This Month | Sprints (Created this month) | Count |
| Lead Sources | Leads grouped by Source Platform | Bar chart |
| Sprint Stage Distribution | Sprints grouped by Stage | Pie chart |
| Avg Cycle Time by Stage | Sprints (computed from date diffs) | Table or bar chart |
| Engagement Volume | Engagement Inbox (last 7 days) | Count by Source |

---

## 6. Airtable Automations (Native)

> Keep Airtable-native automations simple. Complex logic goes to n8n.

### Automation 1: Content Needs QA → Create QA Task

| Property | Value |
|---|---|
| **Trigger** | When Content Pipeline.Status changes to "Needs QA" |
| **Condition** | Tone QA Complete = false OR Claims QA Complete = false OR Privacy QA Complete = false |
| **Action 1** | Send notification to Matt: "Post '{Post Title}' needs QA review" |
| **Action 2** | (Optional) Create a linked record in a Tasks table, or use the notification as the task |
| **Logging** | Create System Logs record: Severity=Info, System=Airtable, Workflow="Content QA Trigger", Message="QA triggered for: {Post Title}" |

### Automation 2: Content Published + Post URL Filled → Create Metrics Task

| Property | Value |
|---|---|
| **Trigger** | When Content Pipeline.Status changes to "Published" AND Post URL is not empty |
| **Action** | Send notification: "Capture metrics for '{Post Title}' — {Post URL}" |
| **Logging** | Create System Logs record: Severity=Info, System=Airtable, Workflow="Metrics Capture Trigger" |

### Automation 3: New Engagement Record → Set Status New

| Property | Value |
|---|---|
| **Trigger** | When record is created in Engagement Inbox |
| **Action** | Set Status = "New" (if not already set) |
| **Logging** | Create System Logs record: Severity=Info, System=Airtable, Workflow="Engagement Auto-Status" |

### Automation 4: Any Automation Error → Log to System Logs

| Property | Value |
|---|---|
| **Trigger** | When any of the above automations encounters an error (use Airtable automation error handling) |
| **Action** | Create System Logs record: Severity=Error, System=Airtable, Workflow="{automation name}", Message="{error details}" |

---

## 7. System Logs — Exact Schema (Reference)

This is the canonical schema for System Logs, referenced by all automation and workflow specs:

```
Table: System Logs
├── Log ID (Autonumber) — Primary field
├── Severity (Single select) — Info | Warn | Error | Critical
├── System (Single select) — Airtable | n8n | Zoho | Manual | Other
├── Workflow (Single line text) — name of the workflow/automation
├── Message (Long text) — human-readable description
├── Record Link (URL) — deep link to relevant record
├── Payload Excerpt (Long text) — truncated debug info
├── Status (Single select) — New | Investigating | Resolved | Won't Fix
├── Retry Count (Number) — attempts made
├── Owner (Collaborator) — assigned investigator
├── Resolution Notes (Long text)
└── Timestamp (Created time) — auto
```

### Log Entry Examples

**Success (Info):**
```json
{
  "Severity": "Info",
  "System": "n8n",
  "Workflow": "Lead Capture Upsert",
  "Message": "Lead created in Zoho and Airtable: @johndoe from LinkedIn comment on post 'Teardown: Why Your Hooks Fail'",
  "Record Link": "https://airtable.com/appXXX/tblLeads/recXXX",
  "Status": "Resolved",
  "Retry Count": 0
}
```

**Error (needs attention):**
```json
{
  "Severity": "Error",
  "System": "n8n",
  "Workflow": "Lead Capture Upsert",
  "Message": "Zoho API returned 429 (rate limit) after 3 retries. Lead not created. Manual action required.",
  "Payload Excerpt": "{\"handle\": \"@janedoe\", \"platform\": \"LinkedIn\", \"post_url\": \"...\"}",
  "Status": "New",
  "Retry Count": 3
}
```

**Warning:**
```json
{
  "Severity": "Warn",
  "System": "n8n",
  "Workflow": "URL Intake Research",
  "Message": "robots.txt blocked /pricing page. Skipped. Other pages crawled successfully.",
  "Record Link": "https://airtable.com/appXXX/tblAccounts/recXXX",
  "Status": "Resolved",
  "Retry Count": 0
}
```

---

## 8. Addendum: New Tables & Field Updates (v2)

> Added per Matt's decisions on social automation, AI video, client portal, and metrics capture.

### NEW Table 12: AI Video Projects

> Tracks prompts, settings, and outputs from AI image/video generation tools. Doubles as a prompt library.

| Field Name | Type | Notes |
|---|---|---|
| Project Name | Single line text | **Primary field** — `[Account] - [Tool] - [Desc] - [Date]` |
| Tool | Single select | Options: `Nano Banana Pro`, `Kling 3.0`, `Veo 3.1`, `Other` |
| Type | Single select | Options: `Image`, `Video` |
| Account | Link to Accounts | |
| Sprint | Link to Sprints | |
| Campaign Kit | Link to Campaign Kits | |
| Prompt | Long text | Exact prompt used |
| Negative Prompt | Long text | If applicable |
| Settings JSON | Long text | Tool-specific settings (see ai-video-spec.md) |
| Reference Images | Attachment | Up to 14 |
| Start Frame | Attachment | Kling 3.0 only |
| End Frame | Attachment | Kling 3.0 only |
| Output Files | Attachment | Generated images/videos |
| Output URL | URL | Hosted location for auto-publish |
| Resolution | Single select | Options: `720p`, `1080p`, `1K`, `2K`, `4K` |
| Aspect Ratio | Single select | Options: `1:1`, `4:5`, `9:16`, `16:9`, `Custom` |
| Duration | Single select | Options: `N/A`, `4s`, `5s`, `6s`, `8s`, `10s`, `15s` |
| Variants Generated | Number | 1–4 |
| Multi-Shot | Checkbox | Kling 3.0 only |
| Audio | Checkbox | Kling 3.0 only |
| Status | Single select | Options: `Queued`, `Generating`, `Review`, `Approved`, `Rejected`, `Used` |
| Quality Rating | Single select | Options: `Poor`, `Acceptable`, `Good`, `Excellent` |
| Notes | Long text | What worked/didn't — builds prompt library |
| Created | Created time | Auto |

### UPDATED: Content Pipeline — New Fields for Metrics + Auto-Publish

| Field Name | Type | Notes |
|---|---|---|
| Platform Post ID | Single line text | Platform-specific post ID for API lookups |
| Impressions | Number | Auto-captured via Workflow G |
| Likes / Reactions | Number | Auto-captured |
| Comments Count | Number | Auto-captured |
| Shares / Reposts | Number | Auto-captured |
| Link Clicks | Number | Manual entry |
| Metrics Captured At | Date | When metrics were pulled |
| Engagement Rate | Formula | `IF(Impressions > 0, (({Likes / Reactions} + {Comments Count} + {Shares / Reposts}) / Impressions) * 100, 0)` |
| Image / Media | Attachment | For IG auto-publish (requires image) |
| Scheduled Publish Time | Date/Time | When to auto-publish (if future-dated) |

**Updated Status options:** `Idea`, `Draft`, `Needs QA`, `Needs Approval`, `Approved`, `Scheduled`, `Published`, `Rejected`

> Note: "Approved" is new — it means Matt approved but auto-publish hasn't fired yet. "Scheduled" means it's queued for a future publish time.

### UPDATED: Content Pipeline — Updated Status Flow

```
Idea → Draft → Needs QA → Needs Approval → Approved → Published
                                              ↓
                                          Scheduled (if future Publish Date)
                                              ↓
                                          Published (auto-publish fires)

Rejected can occur from Needs Approval → back to Draft
```

### UPDATED: Sprints — New Fields for Client Portal

| Field Name | Type | Notes |
|---|---|---|
| Client Feedback | Long text | Submitted via Softr portal |
| Portal Timeline Notes | Long text | Human-readable timeline for portal display |
| Client-Visible Notes | Long text | Notes visible to client (not Internal Notes) |
| Sprint Paused | Checkbox | Set when client misses 48h feedback window |
| Pause Reason | Long text | Why sprint was paused |
| Original Due Date | Date | Preserved when sprint is paused/rescheduled |

### UPDATED: Campaign Kits — New Fields for Client Portal

| Field Name | Type | Notes |
|---|---|---|
| Client Downloadable | Checkbox | Show this asset in the Softr portal |
| Download Link | URL | Direct link to downloadable file |
| Client Status | Single select | Options: `Pending`, `Ready for Review`, `Final` |

### UPDATED: Engagement Inbox — New Fields for Auto-Capture

| Field Name | Type | Notes |
|---|---|---|
| Platform Post ID | Single line text | Platform-specific post ID |
| Platform Comment ID | Single line text | Platform-specific comment ID |
| Idempotency Key | Single line text | SHA256 hash for dedup |
| CTA Keyword Detected | Single line text | If comment matches a CTA keyword |
| Auto-Captured | Checkbox | true = captured by Workflow E, false = manual |

### UPDATED: Leads — New View

**Affiliate Referrals view:**
- Filter: Notes CONTAINS "affiliate" OR Account Interest = "AI Video Bootcamp — Skool Affiliate"
- Purpose: Track Skool affiliate referral pipeline

### NEW Views for New Table

**AI Video Projects:**
| View Name | Type | Filter/Sort |
|---|---|---|
| All Projects | Grid | Default |
| By Tool | Kanban | Grouped by Tool |
| Needs Review | Grid | Status = "Review" |
| Approved Assets | Gallery | Status IN ("Approved", "Used"), show Output Files |
| Prompt Library | Grid | Status IN ("Approved", "Used"), sorted by Quality Rating desc |
| By Account | Grid | Grouped by Account |

### Updated Table Count

**Total tables: 12** (was 11, added AI Video Projects)
