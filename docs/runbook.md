# Implementation Runbook — Get Fractional OS

## Roles

| Role | Person/System | Responsibilities |
|---|---|---|
| **Matt** | Human | Offer decisions, tone approval, sales calls, final publish, proof review, all client-facing communication |
| **Codex** | AI/Dev | Airtable base build, n8n workflow implementation, Zoho field setup, documentation |
| **Omni** | AI/Tool | Interface building, Daily Cockpit UX, views, layout |
| **Claude** | AI | Draft SOPs, templates, content drafts, checklists, QA frameworks |

---

## Phase 1: Day 0–2 (Foundation)

### Goal
A lead can comment/DM → become a Zoho lead → be logged in Airtable → you can run a sprint from Airtable.

### Checklist

#### Matt Does

- [ ] **Finalize Creative Sprint offer** — confirm price, scope boundaries, deliverables list
- [ ] **Create deposit link** — Stripe/payment processor, amount = 50% of sprint price
- [ ] **Write offer page copy** — or approve draft from Claude
- [ ] **Record 3–5 "Matt phrases"** for Tone Library (phrases you use, phrases you never use)
- [ ] **Select 10 canonical posts** you've written that capture your voice
- [ ] **Decide:** Founders promo pricing ($3.5k) — yes/no, and conditions

#### Codex Does

- [ ] **Create Airtable base** — "Get Fractional OS (Core)"
- [ ] **Build all 11 tables** per `airtable-spec.md`:
  - Accounts
  - ICPs
  - Objections
  - Offers
  - Sprints
  - Campaign Kits
  - Content Pipeline
  - Engagement Inbox
  - Leads
  - Knowledge Library
  - System Logs
- [ ] **Configure all fields** — types, options, formulas per spec
- [ ] **Set up table relationships** — all linked record fields connected
- [ ] **Create core views:**
  - Sprints: "Sprint In Flight" (Kanban), "Needs Approval"
  - Content Pipeline: "Needs QA", "Needs Approval", "Ready to Publish"
  - Engagement Inbox: "New"
  - Leads: "Needs Follow-up", "By Stage" (Kanban)
  - System Logs: "Errors Last 7 Days", "Unresolved"
- [ ] **Set up Zoho CRM:**
  - Create custom fields per `zoho-spec.md`
  - Configure Deals pipeline stages
  - Set up workflow rules for auto-task creation (SLAs)
- [ ] **Deploy n8n Workflow A** (Lead Capture → Zoho Upsert → Airtable Log):
  - Import `workflow-a-lead-capture.json`
  - Configure Airtable + Zoho credentials
  - Test with sample lead
  - Verify System Logs entry created
- [ ] **Seed initial data:**
  - Create "Get Fractional" Account record
  - Create Creative Sprint offer record with full scope/deliverables
  - Create Offer OS Sprint offer record
  - Create 3 lead magnet offer records

#### Claude Does

- [ ] **Draft offer page copy** for Creative Sprint
- [ ] **Draft 5 cornerstone posts** (1 per weekday pillar):
  - Monday: Teardown post
  - Tuesday: URL → Brief demo concept
  - Wednesday: Proof object / lesson
  - Thursday: Systems post (governance)
  - Friday: Offer / story + CTA
- [ ] **Create Sprint Intake Checklist** template
- [ ] **Create Revision Policy** document
- [ ] **Create QA Checklist** (claims, privacy, tone)

### Day 2 — Definition of Done

| Criteria | How to Verify |
|---|---|
| Lead can be captured via webhook → Zoho + Airtable | Send test webhook, check both systems |
| Sprint record can be created in Airtable | Create test Sprint, verify all fields work |
| Offer page exists with deposit link | Visit URL, test payment link |
| 5 posts drafted in Content Pipeline | Check Airtable: 5 records with Status = "Draft" |
| System Logs has entries | Check: test workflow logged Info records |
| Zoho pipeline has stages | Open Zoho → Deals → verify pipeline |

---

## Phase 2: Day 3–7 (Interfaces + First Client)

### Goal
One paying client moved through intake → delivery → proof capture. Interfaces operational.

### Checklist

#### Matt Does

- [ ] **Publish daily** (5 posts this week from drafted backlog)
- [ ] **Run Fit Checks** — DM leads, book 10-minute calls
- [ ] **Close 1 sprint** — deposit collected, Sprint record created
- [ ] **Run intake** for first client — collect URL, brief, brand voice samples
- [ ] **Approve brand/ICP drafts** in Daily Cockpit
- [ ] **Approve content** daily via Needs Approval view

#### Codex Does

- [ ] **Build Airtable Interfaces:**
  - Daily Cockpit (see `interfaces.md`)
  - Post Builder Wizard
  - Sprint Delivery Cockpit
  - Offer Builder Wizard
- [ ] **Set up Airtable Automations** (4 automations per `airtable-spec.md`):
  - Content Needs QA → notification
  - Content Published → metrics task
  - New Engagement → auto-status
  - Error handler → System Logs
- [ ] **Deploy n8n Workflow D** (Daily Error Digest):
  - Import `workflow-d-error-digest.json`
  - Configure SMTP credentials
  - Test with sample error record

#### Omni Does

- [ ] **Polish Daily Cockpit** — layout, section ordering, mobile-friendly
- [ ] **Polish Sprint Delivery Cockpit** — stage checklists, progress indicators
- [ ] **Create KPI Dashboard** — basic metrics per `interfaces.md`

#### Claude Does

- [ ] **Build Knowledge Library taxonomy** — tag categories, type definitions
- [ ] **Draft 5 more posts** for next week
- [ ] **Create Tone Library records** — Matt's phrases, anti-phrases, canonical examples
- [ ] **Draft Proof Object Capture checklist**
- [ ] **Draft Case Study Skeleton** template

### Day 7 — Definition of Done

| Criteria | How to Verify |
|---|---|
| Daily Cockpit shows real data | Open interface, verify sections populated |
| 1 paying client in Sprint stage | Sprint record with Stage != "Intake" |
| Client intake data in Airtable | Account, ICP, Objections records exist |
| 5+ posts published | Content Pipeline: 5+ records with Status = "Published" |
| Error digest email received | Check inbox for test digest |
| Engagement records being captured | Engagement Inbox has records |

---

## Phase 3: Day 8–14 (Harden + Prove)

### Goal
You can sell, fulfill, capture proof, and repeat without chaos. First case study exists.

### Checklist

#### Matt Does

- [ ] **Complete first sprint delivery** — all deliverables sent
- [ ] **Capture proof objects:**
  - Output count (angles, hooks, concepts produced)
  - Before/after brief comparison
  - One anonymized teardown
- [ ] **Ask for case study permission** from first client
- [ ] **Request referral** from first client
- [ ] **Offer retainer** to first client (if good fit)
- [ ] **Publish daily** — continue 5/week cadence
- [ ] **Close 1–2 more sprints** if pipeline allows

#### Codex Does

- [ ] **Harden revision policy enforcement:**
  - Sprint Delivery Cockpit shows revision count prominently
  - Warning when revision count = 0
  - Scope amendment process documented
- [ ] **Deploy n8n Workflow B** (URL Intake → Brand Research):
  - Import `workflow-b-url-intake.json`
  - Test with sample URL
  - Verify Knowledge Library records created
  - Verify approval notification sent
- [ ] **Deploy n8n Workflow C** (Content Publish Prep):
  - Import `workflow-c-content-publish.json`
  - Test QA validation logic
  - Verify Status transitions work
- [ ] **Build Client Portal** (Interface):
  - Per-client filtered view
  - Read-only sharing configured
  - Test with first client's data
- [ ] **Test error scenarios:**
  - Simulate Zoho API failure → verify dead-letter + System Logs
  - Simulate duplicate lead → verify idempotency skip
  - Simulate URL fetch failure → verify warning log

#### Claude Does

- [ ] **Write first case study** from sprint data
- [ ] **Draft tripwire content** — $7 Hook Pack description + checkout flow
- [ ] **Create Lead Magnet fulfillment SOPs** — step-by-step delivery for each magnet
- [ ] **Draft "From URL to Campaign"** explainer for website

### Day 14 — MVP Definition of Done

| Criteria | How to Verify |
|---|---|
| 1 sprint fully delivered + proof captured | Sprint Stage = "Complete", Proof Captured = true |
| First case study or proof object published | Content Pipeline record with proof content |
| All 4 n8n workflows operational | Each workflow has successful runs in n8n execution log |
| Client Portal shared with first client | Client has received link + confirmed access |
| Tripwire ($7 Hook Pack) ready to sell | Offer record exists, checkout link works |
| Revision policy enforced on first sprint | Sprint Revision Rounds tracked, no scope creep |
| All Airtable automations firing | System Logs has Info records from each automation |
| Error digest running daily | Received at least 1 digest email |
| KPI Dashboard showing real metrics | Dashboard has non-zero values |
| Content published: 10+ posts total | Content Pipeline: 10+ Published records |

---

## Phase 4: Day 15–30 (Scale + Systematize)

> Post-MVP. Execute only after Day 14 Definition of Done is met.

### Checklist

- [ ] Launch tripwire checkout funnel ($7 Hook Pack, $7 Angle Pack)
- [ ] Build lead magnet opt-in forms → webhook → auto-capture
- [ ] Publish 2–3 case studies / proof objects
- [ ] Close 3–5 total sprints ($20k–$30k collected)
- [ ] Convert 1+ sprint clients to Iteration Retainer
- [ ] Polish KPI Dashboard with trend data
- [ ] Add AEO/GEO schema to website (ProfilePage, Organization)
- [ ] Start Reddit engagement (genuine participation, no link spam)
- [ ] Begin pre-selling Agency OS Install interest list
- [ ] Create "About Matt + Get Fractional" page with schema markup

---

## Manual Fallback Procedures

> For every automated workflow, here's how to do it by hand if the system is down.

### Fallback A: Lead Capture (n8n down)

1. Open Airtable → **Leads** table
2. Click "+" to create new record
3. Fill: Name/Handle, Email, Source, Source Platform, Stage = "New"
4. Open Zoho CRM → **Leads** module → "Create Lead"
5. Fill matching fields
6. Copy Zoho Lead ID → paste into Airtable Lead record → "Zoho ID" field
7. Create System Logs record: Severity=Warn, System=Manual, Workflow="Lead Capture Upsert"

### Fallback B: URL Intake (n8n down)

1. Visit the prospect's website manually
2. Take notes on: brand voice, products, pricing, ICP signals
3. Create Knowledge Library records in Airtable (one per page)
4. Write brand voice notes in the Account record
5. Create ICP record manually with JTBD + objections
6. Set Account status or note: "Research complete — needs review"

### Fallback C: Content Publish Prep (n8n down)

1. Open Content Pipeline → change Status manually: Draft → Needs QA → Needs Approval → Scheduled → Published
2. Complete QA checklist checkboxes manually
3. After publishing: paste Post URL into the record
4. Set a calendar reminder: "Capture metrics for [Post Title] in 24 hours"

### Fallback D: Error Digest (n8n down)

1. Open System Logs → "Errors Last 7 Days" view
2. Review manually each morning
3. Resolve or assign as needed

---

## SOP Templates (Copy/Paste Ready)

### SOP 1: Sprint Intake Checklist

```
SPRINT INTAKE — [Client Name] — [Date]

Required from client:
☐ Website URL (primary product/service page)
☐ Product/offer details (what they sell, to whom)
☐ Target audience description (who buys)
☐ Constraints (brand guidelines, restricted claims, compliance)
☐ Past winners (ads/content that worked)
☐ Past losers (what didn't work and why)
☐ Brand voice samples (3-5 examples of content they like)
☐ Competitors (2-3 they respect or fear)

Internal setup:
☐ Account record created in Airtable
☐ Sprint record created with dates
☐ Campaign Kit record linked
☐ Zoho Deal created and moved to "In Fulfillment"
☐ Client Portal link generated and shared

Intake complete when: All required items received + Intake Complete = checked
```

### SOP 2: Revision Policy

```
REVISION POLICY — Get Fractional Creative Sprint

Included: 2 revision rounds per sprint
Round = one consolidated set of changes (not piecemeal)

Rules:
1. All feedback must be submitted in ONE message/document per round
2. Partial feedback does not start a new round — wait until all feedback is collected
3. Matt consolidates and implements in one pass
4. If no feedback within 48 hours of delivery: considered approved
5. Round 0 = initial delivery. Round 1 = first revision. Round 2 = final revision.

Out of scope (requires scope amendment):
- Net new deliverables not in original scope
- Additional ICP or product (original scope = 1 brand, 1 ICP, up to 2 products)
- Fundamental strategy pivot after concepts are approved
- Requests after sprint end date

Scope amendment: +$1,000–$2,000 depending on complexity, with new timeline.
```

### SOP 3: QA Checklist

```
QA CHECKLIST — Content / Creative

TONE
☐ Short paragraphs (no walls of text)
☐ Concrete examples used (not abstract)
☐ Sounds like Matt (warm, direct, grounded)
☐ No buzzwords or hype
☐ "Would a busy founder find this useful in 30 seconds?"

CLAIMS
☐ No revenue/ROAS guarantees
☐ No "10x" or similar multiplier claims
☐ Metrics cited are inputs we control (volume, speed, testing rigor)
☐ No misleading before/after without context
☐ Testimonial quotes have permission

PRIVACY
☐ No client names without permission
☐ No client data (spend, revenue) without permission
☐ Anonymized where Case Study Permission = "Anonymized" or "Process Only"
☐ No screenshots of client dashboards without blur/approval

CTA
☐ CTA is clear and specific
☐ CTA matches journey stage
☐ No high-pressure urgency tactics
☐ Comment/DM CTAs are simple (one word: "SPRINT", "TEARDOWN", etc.)

PLATFORM
☐ Formatting matches platform norms (LI vs FB vs IG)
☐ Character limits respected
☐ Hashtags appropriate for platform (LI: 3-5, IG: up to 30, FB: minimal)
```

### SOP 4: Proof Object Capture

```
PROOF OBJECT CAPTURE — Post-Sprint

After every sprint delivery, capture these:

☐ OUTPUT COUNT
  - Number of angles produced: ___
  - Number of hooks produced: ___
  - Number of ad concepts produced: ___
  - Number of landing page sections: ___
  - Total deliverables: ___

☐ BEFORE/AFTER
  - What the client had before (screenshot or description)
  - What was delivered (screenshot or description)
  - Save both to Knowledge Library

☐ TEARDOWN
  - Write one anonymized teardown of a problem found + fix delivered
  - Add to Content Pipeline as "Proof Objects" pillar post

☐ TIMELINE PROOF
  - Sprint start date: ___
  - Sprint end date: ___
  - Days to deliver: ___

☐ CASE STUDY PERMISSION
  - Permission level: Full Public / Anonymized / Process Only / None
  - Stored in Account record + Zoho Contact record

☐ CLIENT QUOTE (if available)
  - Exact words from client
  - Permission to publish: Yes / No
```

### SOP 5: Case Study Skeleton

```
CASE STUDY — [Client Name or "Anonymized: [Industry]"]

THE SITUATION
- Who they are (industry, size, stage)
- What they were struggling with (1-2 sentences)
- What they had tried before

THE ENGAGEMENT
- What we sold them (offer name + scope)
- Timeline (e.g., "14-day Creative Sprint")
- What we needed from them (URL, brief, samples)

THE PROCESS
- Step 1: [Research/intake — what we found]
- Step 2: [Concept development — how we approached it]
- Step 3: [Production — what we built]
- Step 4: [QA + delivery — how we ensured quality]

THE RESULTS
- Output volume: [X angles, Y hooks, Z concepts]
- Delivery speed: [X days]
- Client feedback: "[quote]"
- Follow-up: [retainer, referral, second sprint]

THE PROOF OBJECTS
- [Link to anonymized teardown]
- [Link to before/after]
- [Link to output count graphic]

PERMISSION LEVEL: [Full Public / Anonymized / Process Only]
```
