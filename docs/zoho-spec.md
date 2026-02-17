# Zoho CRM Spec — Get Fractional OS

## 1. Modules Overview

| Module | Purpose | SSOT For |
|---|---|---|
| **Leads** | New inbound contacts before qualification | Contact details pre-fit-check |
| **Contacts** | Qualified contacts (converted from Leads) | Contact details post-qualification |
| **Accounts** | Companies / brands (created on conversion) | Company-level data |
| **Deals** | Revenue opportunities through pipeline | Deal stage + revenue |
| **Tasks** | Follow-up actions and SLAs | Activity tracking |
| **Calls** | Fit check calls and sales calls | Call logs |
| **Notes** | Contextual notes on any record | Supplementary info |

---

## 2. Module Field Specs

### Leads Module

| Field Name | Type | Values / Notes |
|---|---|---|
| First Name | Text | |
| Last Name | Text | Required |
| Email | Email | |
| Phone | Phone | |
| Company | Text | |
| **Source Platform** | Picklist | `LinkedIn`, `Facebook`, `Instagram`, `Website`, `Referral`, `Other` |
| **Source Type** | Picklist | `Comment`, `DM`, `Form Submission`, `Opt-in`, `Referral`, `Outbound` |
| **Original Post URL** | URL | The social post that generated this lead |
| **Interest** | Picklist | `Creative Sprint`, `Offer OS Sprint`, `Agency OS Install`, `Iteration Retainer`, `Systems Retainer`, `Tripwire`, `Lead Magnet`, `General` |
| **Fit Check Completed** | Checkbox | |
| **Fit Check Score** | Number | 1–10 |
| **Fit Check Notes** | Multi-line text | |
| **Airtable Record Link** | URL | Deep link to Airtable Leads record |
| **Idempotency Key** | Text | Used by n8n to prevent duplicates |
| Lead Source | Picklist (standard) | Map to: `Social`, `Website`, `Referral`, `Partner`, `Other` |
| Lead Status | Picklist (standard) | `New`, `Contacted`, `Fit Check Scheduled`, `Qualified`, `Unqualified` |

### Contacts Module

> Contacts are created when Leads are converted (post-fit-check qualification).

| Field Name | Type | Values / Notes |
|---|---|---|
| Standard contact fields | — | First Name, Last Name, Email, Phone, Account |
| **Source Platform** | Picklist | Same as Leads |
| **Source Type** | Picklist | Same as Leads |
| **Original Interest** | Picklist | Carried from Lead.Interest |
| **Airtable Record Link** | URL | |
| **Case Study Permission** | Picklist | `Full Public`, `Anonymized`, `Process Only`, `None` |

### Accounts Module

> Company-level records. Created on Lead conversion or manually.

| Field Name | Type | Values / Notes |
|---|---|---|
| Account Name | Text | Required |
| Website | URL | |
| Industry | Picklist | `DTC / Ecommerce`, `Agency`, `B2B Service`, `SaaS`, `Other` |
| **Account Tier** | Picklist | `Sprint Client`, `Retainer Client`, `Install Client`, `Prospect` |
| **Airtable Account Link** | URL | Deep link to Airtable Accounts record |
| Employees | Number | |
| Annual Revenue | Currency | |

### Deals Module

> Tracks revenue opportunities through the sales pipeline.

| Field Name | Type | Values / Notes |
|---|---|---|
| Deal Name | Text | Format: `[Account] - [Offer] - [Date]` |
| Account Name | Lookup | Linked to Accounts |
| Contact Name | Lookup | Linked to Contacts |
| **Offer Type** | Picklist | `Creative Sprint`, `Offer OS Sprint`, `Agency OS Install`, `Iteration Retainer`, `Systems Retainer`, `Tripwire` |
| Amount | Currency | |
| **Deposit Amount** | Currency | |
| **Deposit Paid** | Checkbox | |
| Stage | Picklist | See pipeline stages below |
| Closing Date | Date | |
| **Airtable Sprint Link** | URL | Deep link to Airtable Sprints record |
| **Source Platform** | Picklist | Inherited from Lead/Contact |
| **Proposal Link** | URL | |
| Probability | Percent | Auto-set by stage |
| Description | Multi-line text | |

### Tasks Module

| Field Name | Type | Values / Notes |
|---|---|---|
| Subject | Text | |
| Due Date | Date/Time | |
| Status | Picklist | `Not Started`, `In Progress`, `Completed`, `Waiting`, `Deferred` |
| Priority | Picklist | `High`, `Medium`, `Low` |
| **Task Type** | Picklist | `Follow-up`, `Fit Check`, `Proposal`, `Onboarding`, `Proof Capture`, `SLA Reminder` |
| Related To | Lookup | Deal or Account |
| Assigned To | User | Matt (solo) |

---

## 3. Pipeline Stages (Deals)

| Stage | Probability | Description | SLA |
|---|---|---|---|
| **New** | 10% | Lead expressed interest, not yet contacted | Respond within 24 hours |
| **Fit Check Scheduled** | 20% | Call booked | Call within 72 hours of first contact |
| **Fit Check Completed** | 40% | Call done, evaluating fit | — |
| **Proposal Sent** | 60% | Scope + price sent | Send within 24 hours of fit check |
| **Deposit Paid** | 80% | Commitment received | — |
| **In Fulfillment** | 90% | Sprint/project actively running | Track in Airtable Sprints |
| **Proof Captured** | 95% | Deliverables done, proof objects gathered | Within 48 hours of delivery |
| **Retainer Offered** | 95% | Retention upsell proposed | Within 1 week of delivery |
| **Won** | 100% | Closed-Won | — |
| **Lost** | 0% | Closed-Lost | Record reason |

### Stage Transition Rules

- **New → Fit Check Scheduled:** Only after initial response + booking link sent
- **Fit Check Completed → Proposal Sent:** Only after fit check notes are filled
- **Proposal Sent → Deposit Paid:** Only after deposit is confirmed (manual check)
- **In Fulfillment → Proof Captured:** Only after Sprint is marked "Delivered" in Airtable
- **Any → Lost:** Always require `Lost Reason` field

---

## 4. Lead Routing Rules

> Solo operation — all leads route to Matt. Rules exist for future team scaling.

### Current (Solo)

| Rule | Action |
|---|---|
| All new Leads | Assign to Matt |
| All new Tasks | Assign to Matt |
| High-priority (Interest = Agency OS Install) | Flag for immediate attention |

### Future (Team)

| Rule | Route To |
|---|---|
| Interest = Creative Sprint | Sprint Lead (future hire) |
| Interest = Agency OS Install | Matt (always) |
| Interest = Tripwire/Lead Magnet | Automation (auto-fulfill) |
| Source = Referral | Matt (always) |

---

## 5. Follow-Up Sequences and SLAs

### SLA Definitions

| Event | SLA | Enforcement |
|---|---|---|
| New inbound lead arrives | Respond within 24 hours | Zoho Task auto-created, due in 24h |
| Lead requests fit check | Schedule within 72 hours | Zoho Task auto-created, due in 72h |
| Fit check completed | Send proposal within 24 hours | Zoho Task auto-created |
| Proposal sent, no response | Follow up at Day 3, Day 7, Day 14 | Zoho Tasks auto-created at each interval |
| Sprint delivered | Capture proof within 48 hours | Zoho Task auto-created |
| Sprint complete | Offer retainer within 7 days | Zoho Task auto-created |

### Follow-Up Sequence: Post-Fit-Check (No Deposit Yet)

| Day | Action | Channel |
|---|---|---|
| 0 | Send proposal + scope doc | Email or DM |
| 3 | Soft follow-up: "Any questions on the scope?" | Same channel as initial |
| 7 | Value-add follow-up: share a relevant proof object or teardown | Same channel |
| 14 | Final follow-up: "Want me to hold a slot?" with soft deadline | Same channel |
| 21+ | Move to nurture (no more direct follow-up) | Content-only |

### Follow-Up Sequence: Post-Delivery (Upsell)

| Day | Action | Channel |
|---|---|---|
| 0 | Deliver final kit + proof capture request | Email + Airtable |
| 3 | Ask for feedback + case study permission | Call or DM |
| 7 | Present retainer option | Call |
| 14 | Referral ask | DM or email |

### Workflow Rules (Zoho native)

| Trigger | Action |
|---|---|
| Lead created with Status = "New" | Create Task: "Respond to lead", due in 24h |
| Deal Stage → "Fit Check Scheduled" | Create Task: "Prepare fit check", due 1h before call |
| Deal Stage → "Fit Check Completed" | Create Task: "Send proposal", due in 24h |
| Deal Stage → "Proposal Sent" | Create Tasks: follow-up at Day 3, 7, 14 |
| Deal Stage → "Proof Captured" | Create Task: "Offer retainer", due in 7 days |
| Deal Stage → "Lost" | Create Task: "Record lost reason + learnings" |

---

## 6. Capture Methods: DM / Form / Comment → Zoho

### Method 1: Comment CTA → Manual Capture

**Flow:**
1. Matt posts content with CTA: "Comment 'SPRINT' for the Fit Check checklist"
2. User comments on post
3. Matt (or VA) manually creates Engagement Inbox record in Airtable
4. Matt replies to comment/DM with fit check link or content
5. If lead is qualified → click "Convert to Lead" in Airtable
6. n8n Workflow A fires: creates Zoho Lead + logs

**Why manual:** Platform risk mitigation. No automated scraping of comments.

### Method 2: DM → Manual Capture

**Flow:**
1. User DMs Matt on LinkedIn / Instagram / Facebook
2. Matt creates Engagement Inbox record in Airtable
3. Matt replies manually
4. If qualified → Convert to Lead → n8n syncs to Zoho

### Method 3: Form Submission → Webhook → Auto Capture

**Flow:**
1. User fills form on website (Fit Check request, lead magnet opt-in)
2. Form sends webhook to n8n Workflow A
3. n8n creates Zoho Lead + Airtable Lead automatically
4. n8n logs success/failure to System Logs
5. Matt gets notification to follow up

**Form fields required:**
- Name (required)
- Email (required)
- Company / URL (optional)
- Interest (dropdown: Sprint / Install / Other)
- How did you find us? (optional)

### Method 4: Referral → Manual Entry

**Flow:**
1. Existing client or contact refers someone
2. Matt creates Lead in Airtable with Source = "Referral"
3. n8n syncs to Zoho
4. Matt reaches out directly

---

## 7. Tags and Segmentation

### Lead Tags (Zoho Tag field or custom multi-select)

| Tag | When Applied |
|---|---|
| `hot-lead` | Fit Check Score >= 7 |
| `sprint-interest` | Interest = Creative Sprint |
| `install-interest` | Interest = Agency OS Install |
| `retainer-candidate` | Post-sprint, good fit for retainer |
| `case-study-approved` | Case Study Permission != None |
| `referral-source` | Source = Referral |
| `affiliate-interest` | Expressed interest in Skool / affiliate content |
| `nurture` | Past proposal deadline, no close |

### Account Tags

| Tag | When Applied |
|---|---|
| `dtc-ecommerce` | Industry = DTC / Ecommerce |
| `agency` | Industry = Agency |
| `b2b-service` | Industry = B2B Service |
| `multi-sprint` | More than 1 Deal won |
| `retainer-active` | Active retainer deal |

---

## 8. Lead Magnet Fulfillment (Safe)

### Principles
- No mass unsolicited DMs
- No automated email blasts without opt-in
- Track deliverability and opt-outs

### Delivery Methods

| Lead Magnet | Delivery Method |
|---|---|
| URL → ICP Snapshot | Manual DM with PDF link |
| Ad Fatigue Teardown Checklist | Manual DM or email with link |
| Sprint Scope Map | Gated download (form → webhook → auto-deliver via email) |
| Offer Clarity Scorecard | Manual DM with link |
| Campaign Brief Template | Gated download |
| Approval Workflow Template | Gated download |
| Proof Object Builder | Manual DM with link |

### Tracking

- Airtable Leads table: track which lead magnet was delivered
- Zoho: note on Lead/Contact record
- System Logs: log each delivery for audit

### Opt-Out Handling

- If anyone asks to not be contacted: immediately update Zoho Lead Status = "Unqualified", add note "Opted out"
- Remove from all follow-up sequences
- Do not re-contact

---

## 9. Zoho ↔ Airtable Sync Rules

| Direction | What Syncs | How | Frequency |
|---|---|---|---|
| Airtable → Zoho | New Leads (via n8n) | n8n Workflow A | Real-time (webhook) or polling (5 min) |
| Zoho → Airtable | Zoho Lead/Deal ID | n8n writes ID back to Airtable | On create/update |
| Airtable → Zoho | Sprint stage updates | Manual or future n8n workflow | Manual for MVP |
| Zoho → Airtable | Deal Won/Lost | Manual update in both systems | Manual for MVP |

### Conflict Resolution

- If a record exists in both systems with different data: **Zoho wins for contact/deal data, Airtable wins for operational data (sprint stage, content, engagement)**
- n8n never overwrites Zoho data without checking existing values first (upsert pattern)
- All sync operations are logged to System Logs

---

## 10. Addendum: Zoho One Integration (v2)

> Matt is already on Zoho One with CRM, Billing, and Sign deployed. Changes below are additive only.

### Existing Infrastructure (No Changes Needed)

| Module | Status | Notes |
|---|---|---|
| Zoho CRM | Deployed | Add custom fields + pipeline per sections 2-3 above |
| Zoho Billing | Deployed | Integrate for deposit/invoice automation |
| Zoho Sign | Deployed | Integrate for scope agreement signing |

### Zoho Billing Integration

**Purpose:** Automate deposit collection and invoice generation for sprints.

| Action | Trigger | Zoho Billing Action |
|---|---|---|
| Generate deposit invoice | Deal Stage → "Proposal Sent" | Create Invoice: 50% of Deal Amount, Net Due Immediately |
| Mark deposit paid | Payment received in Zoho Billing | Update Deal: Deposit Paid = true, Stage → "Deposit Paid" |
| Generate final invoice | Sprint delivered in Airtable | Create Invoice: remaining 50%, Net 15 |
| Retainer invoice | Monthly (1st of month) | Recurring Invoice for active retainers |

**Fields to add to Zoho Deals:**

| Field | Type | Notes |
|---|---|---|
| Zoho Billing Invoice ID (Deposit) | Text | Links to deposit invoice |
| Zoho Billing Invoice ID (Final) | Text | Links to final invoice |
| Payment Status | Picklist | `Pending`, `Deposit Paid`, `Fully Paid`, `Overdue` |

**Automation (Zoho Workflow Rule):**
- When Deal.Stage = "Proposal Sent" AND Deposit Amount > 0 → trigger Zoho Billing API to create invoice
- When Invoice.Status = "Paid" → update Deal.Deposit Paid = true

### Zoho Sign Integration

**Purpose:** Get scope agreements signed before sprint kickoff.

| Document | When Sent | Template |
|---|---|---|
| Sprint Scope Agreement | Deal Stage → "Deposit Paid" | Scope, deliverables, timeline, revision policy, case study clause |
| Retainer Agreement | When retainer is offered | Monthly scope, terms, cancellation policy |

**Scope Agreement Template Fields (auto-filled from Zoho Deal):**
- Client Name (from Account)
- Sprint Name
- Deliverables (from Offer)
- Timeline
- Price + Deposit Amount
- Revision Policy (standard text)
- Case Study Permission level (from Account)
- Pause and Requeue clause

**Automation:**
- When Deal.Stage = "Deposit Paid" → auto-send Zoho Sign document for e-signature
- When document signed → update Deal custom field "Agreement Signed" = true
- When signed → trigger Sprint creation in Airtable (via n8n or manual)

### Updated Revision Policy in Zoho

**Pause and Requeue clause** (added to scope agreement):

> "Sprint timelines assume client feedback within 48 hours of each review milestone (Day 3 Concept Review, Day 10 Draft Review). If no consolidated feedback is received within 48 hours, the sprint will be paused. When the client is ready to resume with consolidated feedback, the sprint will be scheduled at the next available production slot. Paused sprints do not expire but are subject to scheduling availability."

### Skool Affiliate Tracking

| Field | Module | Value |
|---|---|---|
| Affiliate Interest | Contact (tag) | `affiliate-interest` tag |
| Affiliate Link Shared | Contact (checkbox) | true when Skool link was shared |
| Affiliate Link | Stored in Zoho CRM notes | `https://www.skool.com/aivideobootcamp/about?ref=747639c593724d49b7618bf8bcb2363c` |

**Rule:** Only share after delivering value (post-sprint or post-retainer). Never in automated sequences.
