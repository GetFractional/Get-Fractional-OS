# Interfaces Spec — Get Fractional OS

> All interfaces are built using Airtable Interfaces (Omni-compatible). Each interface is a separate page within the "Get Fractional OS (Core)" base.

---

## 1. Daily Cockpit

### Purpose
Matt's operational home screen. Shows everything that needs attention right now. Open this first every morning.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  DAILY COCKPIT                                    [Today]   │
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│  🔴 APPROVALS NEEDED         │  📥 ENGAGEMENT QUEUE          │
│  ─────────────────────       │  ─────────────────────       │
│  Content awaiting approval   │  New comments/DMs             │
│  Sprint milestones due       │  Sorted by recency           │
│                              │  Quick status buttons         │
│  [List: max 10 items]        │  [List: max 10 items]        │
│                              │                              │
├──────────────────────────────┼──────────────────────────────┤
│                              │                              │
│  👤 LEADS NEEDING ACTION     │  ⚠️ ERROR LOG                 │
│  ─────────────────────       │  ─────────────────────       │
│  Follow-ups due today        │  Unresolved errors/criticals │
│  New leads not yet contacted │  From System Logs            │
│                              │                              │
│  [List: max 10 items]        │  [List: max 5 items]         │
│                              │                              │
├──────────────────────────────┴──────────────────────────────┤
│                                                             │
│  📋 SPRINTS IN FLIGHT                                       │
│  ─────────────────────                                      │
│  Active sprints with stage, due date, approval status       │
│  [Horizontal cards or compact list]                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📅 CONTENT CALENDAR (Next 7 Days)                          │
│  ─────────────────────                                      │
│  Scheduled posts with platform, pillar, publish date        │
│  [Timeline or list view]                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Components

| Section | Data Source | Filter | Sort | Display |
|---|---|---|---|---|
| Approvals Needed | Content Pipeline | Status = "Needs Approval" | Publish Date asc | Record list: Post Title, Platform, CTA Type |
| Approvals Needed (Sprints) | Sprints | Approval Needed = true | Due Date asc | Record list: Sprint Name, Stage, Due Date |
| Engagement Queue | Engagement Inbox | Status = "New" | Created desc | Record list: Source, Author, Content preview (50 chars), Linked Post |
| Leads Needing Action | Leads | Next Step Date <= TODAY() OR (Stage = "New" AND Created > 24h ago) | Next Step Date asc | Record list: Name, Stage, Next Step, Source Platform |
| Error Log | System Logs | Severity IN (Error, Critical) AND Status = "New" | Timestamp desc | Record list: Severity badge, Workflow, Message (truncated) |
| Sprints In Flight | Sprints | Stage NOT IN (Complete, Proof Capture) | Due Date asc | Cards: Sprint Name, Account, Stage, Due Date, Revision Rounds |
| Content Calendar | Content Pipeline | Status = "Scheduled" AND Publish Date within next 7 days | Publish Date asc | List: Post Title, Platform, Pillar, Publish Date |

### Actions Available

| Action | What It Does |
|---|---|
| Click approval item → opens record detail | Review + approve/reject |
| Click engagement item → opens record | Reply notes, convert to lead |
| Click lead → opens record | Update stage, add next step |
| Click error → opens System Logs record | Investigate, mark resolved |
| Click sprint → navigates to Sprint Delivery Cockpit | Full sprint view |

---

## 2. Post Builder Wizard

### Purpose
Guided workflow for creating content. Ensures every post follows the pillar + journey stage + CTA framework and passes QA before requesting approval.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  POST BUILDER                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Select Pillar                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Teardowns   │ │ URL→Campaign│ │ Proof Objects│ ...      │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│  STEP 2: Select Journey Stage                               │
│  ┌──────────┐ ┌──────────────┐ ┌───────────────┐          │
│  │ Unaware  │ │Problem-Aware │ │Solution-Aware │ ...      │
│  └──────────┘ └──────────────┘ └───────────────┘          │
│                                                             │
│  STEP 3: Platform                                           │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐                  │
│  │ LinkedIn │ │ Facebook │ │ Instagram │                   │
│  └──────────┘ └──────────┘ └───────────┘                  │
│                                                             │
│  STEP 4: Content Type                                       │
│  [Dropdown: Teardown Post, Demo, Case Study, ...]           │
│                                                             │
│  STEP 5: CTA                                                │
│  Type: [Dropdown]    Text: [________________]               │
│                                                             │
│  STEP 6: Write Draft                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  [Rich text editor - Draft field]                   │   │
│  │                                                     │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 7: QA Checklist                                       │
│  ☐ Tone QA: Voice matches Matt's style guide               │
│  ☐ Claims QA: No guarantees, no misleading metrics          │
│  ☐ Privacy QA: No client data without permission            │
│                                                             │
│  [Submit for Approval]                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

| Step | Component Type | Source | Required |
|---|---|---|---|
| Pillar | Button group | Content Pipeline.Pillar options (8 pillars) | Yes |
| Journey Stage | Button group | Content Pipeline.Journey Stage options (5 stages) | Yes |
| Platform | Button group | Content Pipeline.Platform options | Yes |
| Content Type | Dropdown | Content Pipeline.Content Type options | Yes |
| CTA Type | Dropdown | Content Pipeline.CTA Type options | Yes |
| CTA Text | Text input | Content Pipeline.CTA Text | If CTA Type != "No CTA" |
| Draft | Long text (rich text) | Content Pipeline.Draft | Yes |
| Tone QA | Checkbox | Content Pipeline.Tone QA Complete | Before submit |
| Claims QA | Checkbox | Content Pipeline.Claims QA Complete | Before submit |
| Privacy QA | Checkbox | Content Pipeline.Privacy QA Complete | Before submit |

### Submit Logic

1. On "Submit for Approval" click:
   - Validate: all 3 QA checkboxes checked
   - If incomplete: show warning "Complete QA checklist before submitting"
   - If complete: set Status = "Needs Approval"
2. Record appears in Daily Cockpit → Approvals section
3. n8n Workflow C triggers validation

### Tone QA Reference (Displayed as Helper Text)

```
MATT'S VOICE: Warm, direct, grounded.
DO: Short paragraphs. Concrete examples. "Here's exactly what I did."
DON'T: Hype. Guarantees. "10x your ROAS." Buzzwords.
CHECK: Would a busy founder find this useful in 30 seconds?
```

---

## 3. Offer Builder Wizard

### Purpose
Define new offers or refine existing ones with structured scope boundaries and clear deliverables.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  OFFER BUILDER                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Offer Tier                                         │
│  ┌────────────┐ ┌──────────┐ ┌──────┐ ┌─────────┐         │
│  │Lead Magnet │ │ Tripwire │ │ Core │ │Retainer │ ...     │
│  └────────────┘ └──────────┘ └──────┘ └─────────┘         │
│                                                             │
│  STEP 2: Offer Name                                         │
│  [_____________________________________________]            │
│                                                             │
│  STEP 3: Promise (one sentence)                             │
│  [_____________________________________________]            │
│                                                             │
│  STEP 4: Scope Boundaries (what's EXCLUDED)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [Long text — explicit exclusions]                  │   │
│  │  e.g., "No paid media management. No pixel debug.   │   │
│  │  No guarantee claims. 2 revision rounds max."       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 5: Deliverables                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [Long text — bulleted list of what client gets]    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 6: Price + Timeline                                   │
│  Price: [$________]  Timeline: [________]                   │
│  Price Notes: [_____________________]                       │
│                                                             │
│  STEP 7: SOP Link (optional)                                │
│  [URL: ________________________________________]            │
│                                                             │
│  STEP 8: Link to Account                                    │
│  [Dropdown: Account record or "Get Fractional"]             │
│                                                             │
│  [Save Offer]                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Offer Templates (Pre-Fill Options)

When creating a new offer, show a "Start from template" option:

| Template | Pre-fills |
|---|---|
| Creative Sprint (14-day) | Tier=Core, Promise, Scope, Deliverables, Price=$4k-$8k, Timeline=14 days |
| Offer OS Sprint (7-day) | Tier=Core, Promise, Scope, Deliverables, Price=$2k-$4k, Timeline=7 days |
| Agency OS Install | Tier=Install, Promise, Scope, Deliverables, Price=$12k-$25k, Timeline=21-30 days |
| Iteration Retainer | Tier=Retainer, Promise, Scope, Deliverables, Price=$3k-$8k/mo |
| Systems Retainer | Tier=Retainer, Promise, Scope, Deliverables, Price=$2k-$6k/mo |
| Tripwire (generic) | Tier=Tripwire, Template for price/deliverables |
| Lead Magnet (generic) | Tier=Lead Magnet, Template for deliverables |

---

## 4. Sprint Delivery Cockpit

### Purpose
Per-sprint operational view. Everything needed to fulfill a sprint from intake to proof capture. One cockpit per active sprint.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  SPRINT: [Account] - Creative Sprint - [Date]               │
│  Stage: [██████░░░░] Production          Due: Mar 15, 2026  │
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│  INTAKE COMPLETENESS         │  STAGE CHECKLIST             │
│  ─────────────────────       │  ─────────────────────       │
│  ✅ URL Provided              │                              │
│  ✅ Client Brief filled       │  For current stage:          │
│  ☐ Brand voice samples       │  ☐ Review research notes     │
│  ✅ Past winners shared       │  ☐ Draft 3-5 angles          │
│  ☐ Intake Complete flag      │  ☐ Draft 15-25 hooks         │
│                              │  ☐ Batch ad concepts         │
│  Progress: 3/5               │  ☐ Internal QA pass          │
│                              │                              │
├──────────────────────────────┼──────────────────────────────┤
│                              │                              │
│  REVISION TRACKER            │  KEY DATES                   │
│  ─────────────────────       │  ─────────────────────       │
│                              │                              │
│  Rounds remaining: 2         │  Start: Mar 1                │
│  ██████████ (2 of 2)         │  Day 3 Review: Mar 4         │
│                              │  Day 10 Review: Mar 11       │
│  If 0: "No revisions left.  │  Due: Mar 15                 │
│  Additional rounds require   │                              │
│  scope amendment."           │  ⚠️ Day 10 review is in      │
│                              │    2 days                    │
│                              │                              │
├──────────────────────────────┴──────────────────────────────┤
│                                                             │
│  DELIVERABLES (Campaign Kit)                                │
│  ─────────────────────                                      │
│  Kit: [Kit Name]    Status: [In Progress]                   │
│  Angles: 5    Hooks: 20    Assets: 15                       │
│  Testing Plan: [Link]                                       │
│  Brand Brief: [View]                                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PROOF CAPTURE CHECKLIST                                    │
│  ─────────────────────                                      │
│  ☐ Output count logged (angles, hooks, concepts)            │
│  ☐ Before/after brief comparison saved                      │
│  ☐ Anonymized teardown written                              │
│  ☐ Case study permission confirmed                          │
│  ☐ Proof object linked in Content Pipeline                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ACTIONS                                                    │
│  [Advance Stage ▶]  [Request Approval]  [Mark Delivered]    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Stage Checklists (Per-Stage)

| Stage | Checklist Items |
|---|---|
| **Intake** | URL received, Client brief complete, Brand voice samples, Past winners/losers, Intake Complete flag set |
| **Research** | Knowledge Library records created, Brand voice notes drafted, ICP draft reviewed, Objections mapped |
| **Concepts** | 3-5 angles drafted, 15-25 hooks drafted, Landing page structure outlined, Day 3 concept review scheduled |
| **Production** | Ad concepts batched (10-20 variants), Landing page copy drafted, Testing plan written, Naming conventions set |
| **QA** | Tone QA pass, Claims QA pass (no guarantees), Visual QA pass, Testing plan complete |
| **Review** | Day 10 draft review done, Client feedback collected, Revisions consolidated (one round) |
| **Delivered** | Final kit sent, Client confirmed receipt, Revision round completed (if used) |
| **Proof Capture** | Output count logged, Before/after saved, Teardown written, Case study permission confirmed |

### Revision Policy Display

Always visible in the cockpit:

```
REVISION POLICY
- 2 revision rounds included
- Revision requests must be consolidated (no piecemeal feedback)
- Each round = one consolidated set of changes
- Additional rounds: requires scope amendment + additional fee
- No revision = no delay. Silence after 48h = approval.
```

---

## 5. Client Portal

### Purpose
Read-only view shared with active clients. Shows sprint progress, deliverables, and approval requests. No access to internal operations.

### Access Method
- Shared Airtable Interface link, filtered by the client's Account record
- Each client gets a unique shared link
- No raw base access
- No automations or internal views exposed

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [Client Logo/Name] — Sprint Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SPRINT STATUS                                              │
│  ─────────────────────                                      │
│  Sprint: Creative Sprint                                    │
│  Stage: [██████████░░░░] Production                         │
│  Start: Mar 1     Due: Mar 15                               │
│  Next milestone: Day 10 Draft Review (Mar 11)               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  KEY DATES                                                  │
│  ─────────────────────                                      │
│  ✅ Kickoff: Mar 1                                           │
│  ✅ Day 3 Concept Review: Mar 4                              │
│  ⏳ Day 10 Draft Review: Mar 11                              │
│  ⏳ Final Delivery: Mar 15                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DELIVERABLES                                               │
│  ─────────────────────                                      │
│  [Only shows final/approved deliverables]                   │
│  - Brand Brief: [Download]                                  │
│  - Creative Kit: [Available after delivery]                 │
│  - Testing Plan: [Available after delivery]                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  YOUR FEEDBACK NEEDED                                       │
│  ─────────────────────                                      │
│  [Items where client approval/feedback is requested]        │
│  - Day 3 Concepts: [Review + comment]                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### What Clients See vs. Don't See

| Visible | Hidden |
|---|---|
| Sprint stage (simplified) | Internal notes |
| Key milestone dates | Margin / pricing internals |
| Final deliverables (links) | Draft iterations |
| Items awaiting their feedback | QA checklists |
| Revision rounds remaining | System Logs |
| | Engagement Inbox |
| | Other client data |
| | Content Pipeline |
| | Lead data |

### Security Rules

1. Each client portal link is scoped to a single Account record
2. No cross-client data visible
3. Read-only — clients cannot edit records
4. No export capability (Airtable Interface default)
5. Revoke access by disabling the shared link

---

## 6. KPI Dashboard

### Purpose
Operational metrics at a glance. Track output, pipeline health, and system reliability.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  KPI DASHBOARD                        Period: [This Month]  │
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│  CONTENT                     │  PIPELINE                    │
│  ─────────────────────       │  ─────────────────────       │
│                              │                              │
│  Posts this week:  [5]       │  Fit checks booked:  [3]     │
│  Posts this month: [18]      │  Proposals sent:     [2]     │
│  By platform:                │  Sprints sold:       [1]     │
│    LI: 12  FB: 8  IG: 6     │  Revenue this month: [$5k]   │
│                              │                              │
│  [Bar chart: by platform]    │  [Funnel: leads→checks→won] │
│                              │                              │
├──────────────────────────────┼──────────────────────────────┤
│                              │                              │
│  LEAD SOURCES                │  SPRINT HEALTH               │
│  ─────────────────────       │  ─────────────────────       │
│                              │                              │
│  LinkedIn:    [8]            │  Active sprints:     [2]     │
│  Facebook:    [3]            │  On schedule:        [2]     │
│  Instagram:   [2]            │  Overdue:            [0]     │
│  Form:        [1]            │  Avg days/sprint:    [12]    │
│  Referral:    [1]            │                              │
│                              │  [Pie: by stage]             │
│  [Bar chart: by source]      │                              │
│                              │                              │
├──────────────────────────────┼──────────────────────────────┤
│                              │                              │
│  ENGAGEMENT                  │  SYSTEM HEALTH               │
│  ─────────────────────       │  ─────────────────────       │
│                              │                              │
│  New this week:    [15]      │  Errors (7 days):    [2]     │
│  Converted to lead: [4]     │  Criticals:          [0]     │
│  Conversion rate:  [27%]     │  Unresolved:         [1]     │
│                              │                              │
│  [Trend: weekly engagement]  │  [Status: green/yellow/red]  │
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
```

### Metrics Definitions

| Metric | Source | Calculation |
|---|---|---|
| Posts this week | Content Pipeline | COUNT where Status = "Published" AND Publish Date within last 7 days |
| Posts this month | Content Pipeline | COUNT where Status = "Published" AND Publish Date within last 30 days |
| Posts by platform | Content Pipeline | GROUP BY Platform, COUNT |
| Fit checks booked | Leads | COUNT where Stage = "Fit Check Scheduled" this month |
| Proposals sent | Leads | COUNT where Stage = "Proposal Sent" this month |
| Sprints sold | Sprints | COUNT where Created this month |
| Lead sources | Leads | GROUP BY Source Platform, COUNT |
| Active sprints | Sprints | COUNT where Stage NOT IN (Complete) |
| Overdue sprints | Sprints | COUNT where Due Date < TODAY() AND Stage NOT IN (Delivered, Complete) |
| Engagement volume | Engagement Inbox | COUNT created in last 7 days |
| Engagement conversion | Engagement Inbox | COUNT where Lead Created = true / total COUNT |
| System errors | System Logs | COUNT where Severity IN (Error, Critical) in last 7 days |

### Refresh
- All metrics auto-refresh when the Interface page loads (Airtable standard behavior)
- No manual refresh needed
- For historical trends: use Airtable chart blocks or export to Google Sheets
