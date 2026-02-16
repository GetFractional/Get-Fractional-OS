# Get Fractional OS — Architecture Blueprint

## 1. System Purpose

The Get Fractional OS is a modular operating system that supports selling, fulfilling, and proving the **Creative Sprint** flagship offer (and future offers) with minimal chaos. It connects four subsystems:

| Subsystem | Tool | Role |
|-----------|------|------|
| **Offer OS** | Airtable + Interfaces | Define, scope, and price offers |
| **Client OS** | Airtable + Zoho CRM | Intake → fulfillment → proof capture |
| **Content OS** | Airtable + manual publish | Draft → QA → approve → publish → engage → capture leads |
| **Automation OS** | n8n + Airtable Automations | Glue layer: lead upsert, URL research, logging |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MATT (Human-in-the-Loop)                     │
│  Approvals · Tone QA · Sales Calls · Final Publish · Proof Review   │
└────────┬──────────────────────┬──────────────────────┬──────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  AIRTABLE BASE  │  │   ZOHO CRM       │  │  SOCIAL PLATFORMS    │
│  "Get Fractional│  │                  │  │  (LinkedIn, FB, IG)  │
│   OS (Core)"    │  │  Leads           │  │                      │
│                 │  │  Contacts        │  │  Manual publish       │
│  11 Tables      │  │  Accounts        │  │  Manual engagement    │
│  5 Interfaces   │  │  Deals pipeline  │  │  Manual DM replies    │
│  4 Automations  │  │  Tasks + SLAs    │  │                      │
└────────┬────────┘  └────────┬─────────┘  └──────────┬───────────┘
         │                    │                        │
         │         ┌──────────┴────────────┐           │
         │         │                       │           │
         ▼         ▼                       ▼           ▼
┌──────────────────────────────────────────────────────────────────┐
│                          n8n (Automation Hub)                     │
│                                                                  │
│  Workflow A: Lead Capture → Zoho Upsert → Airtable Log           │
│  Workflow B: URL Intake → Research → Brief Draft → Approval      │
│  Workflow C: Content Publish Prep → Post URL Capture → Metrics   │
│                                                                  │
│  Every workflow writes to System Logs (success + failure)         │
│  Retries: 3x exponential backoff · Dead-letter: System Logs      │
│  Idempotency keys on all external writes                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model Diagram

```
┌──────────────┐       ┌──────────┐       ┌──────────────┐
│   Accounts   │──1:N──│   ICPs   │──N:M──│  Objections  │
│ (Brands/     │       │          │       │              │
│  Clients)    │       └──────────┘       └──────────────┘
└──────┬───────┘
       │ 1:N
       ▼
┌──────────────┐       ┌──────────────┐
│   Sprints    │──N:1──│   Offers     │
│ (Projects)   │       │              │
└──────┬───────┘       └──────────────┘
       │ 1:N
       ▼
┌──────────────┐
│ Campaign Kits│
└──────┬───────┘
       │ 1:N
       ▼
┌──────────────────┐       ┌─────────────────┐
│ Content Pipeline │       │ Engagement Inbox │
│                  │       │                  │
└──────────────────┘       └────────┬────────┘
                                    │ converts to
                                    ▼
                           ┌──────────────┐       ┌──────────────┐
                           │    Leads     │──────▶│  Zoho CRM    │
                           │ (Airtable)   │ sync  │  (Leads/     │
                           └──────────────┘       │   Deals)     │
                                                  └──────────────┘

┌──────────────────┐       ┌──────────────┐
│ Knowledge Library│       │  System Logs │
│ (RAG-lite)       │       │ (audit trail)│
└──────────────────┘       └──────────────┘
```

### Source-of-Truth (SSOT) Rules

| Data | SSOT | Synced to | Direction |
|------|------|-----------|-----------|
| Brand identity, ICP, objections | Airtable | — | — |
| Offer definitions + scope | Airtable | — | — |
| Sprint fulfillment status | Airtable | — | — |
| Content drafts + approval | Airtable | — | — |
| Lead contact info + deal stage | Zoho CRM | Airtable (Zoho ID field) | Zoho → Airtable (ID only) |
| Lead source + engagement origin | Airtable | Zoho (via n8n upsert) | Airtable → Zoho |
| Automation audit trail | Airtable System Logs | — | — |

---

## 4. Workflow Diagrams

### Workflow A: Lead Capture → Zoho Upsert → Airtable Log

```
[Trigger: Webhook / Form / Manual Button]
        │
        ▼
[Normalize payload]
  - Clean handle, platform, message
  - Generate idempotency key: hash(platform + handle + post_url)
        │
        ▼
[Search Zoho: Lead/Contact by email or handle]
        │
        ├── Found ──▶ [Update existing Zoho record]
        │                     │
        └── Not found ──▶ [Create new Zoho Lead]
                              │
                              ▼
                    [Create/Update Airtable Lead record]
                      - Set Zoho ID
                      - Set source, stage
                              │
                              ▼
                    [Write System Logs: severity=Info]
                              │
                    [On Error: retry 3x exp. backoff]
                    [Dead-letter: System Logs severity=Error]
```

### Workflow B: URL Intake → Brand Research → Brief → Approval

```
[Trigger: New Account with Website URL + Status=Prospect]
        │
        ▼
[Fetch URL content (homepage, product, pricing, about)]
  - Respect robots.txt
  - Light crawl only
        │
        ▼
[Create Knowledge Library records per page]
        │
        ▼
[Airtable AI fields populate:]
  - Brand voice summary
  - ICP draft v1
  - Objections draft
        │
        ▼
[Create Approval Task: "Review Brand + ICP Draft"]
  - Approval needed = true
        │
        ├── Approved ──▶ [Generate Campaign Brief record]
        │                  [Generate initial Angles/Hooks]
        │                  [Log success]
        │
        └── Rejected ──▶ [Log rejection reason]
                          [Return to draft state]
```

### Workflow C: Content Publish Prep → Post URL → Metrics

```
[Trigger: Content Status = "Needs Approval"]
        │
        ▼
[Create QA Checklist record:]
  - Tone check
  - Claims check (no guarantees)
  - Privacy check
  - CTA clarity check
        │
        ▼
[Matt reviews + approves/rejects]
        │
        ├── Approved ──▶ [Status → "Scheduled"]
        │                  [Matt publishes manually]
        │                  [Matt pastes Post URL back]
        │                  [n8n creates "Metrics Capture" task]
        │                  [Log success]
        │
        └── Rejected ──▶ [Status → "Draft"]
                          [Notes added for revision]
```

---

## 5. Safety & Guardrails Summary

### Human-in-the-Loop Gates

| Gate | Where | What Matt Does |
|------|-------|----------------|
| **Content publish** | Content Pipeline → "Needs Approval" | Reviews tone, claims, CTA; approves or sends back to draft |
| **Brand/ICP draft review** | URL Intake workflow | Reviews AI-generated brand voice, ICP, objections before brief generation |
| **Sprint milestone approval** | Sprints → "Approval needed" | Reviews deliverables at Day 3 concept review, Day 10 draft review |
| **Lead reply** | Engagement Inbox | All DM/comment replies are manual |
| **Deal progression** | Zoho Deals | Matt moves deals through pipeline manually |
| **Proof publication** | Content Pipeline | Case studies and proof objects require explicit approval |

### Automation Safety

| Control | Implementation |
|---------|----------------|
| **Idempotency** | Every n8n workflow that writes to Zoho or Airtable uses a deterministic key (hash of unique fields) to prevent duplicate creates |
| **Retry policy** | 3 retries with exponential backoff (2s, 4s, 8s), then dead-letter |
| **Dead-letter handling** | Failed operations write to System Logs with severity=Error, status=New, full payload excerpt |
| **Error alerting** | Daily digest of System Logs where severity ∈ {Error, Critical} sent to email |
| **No auto-publishing** | Social posts are never auto-published. Status must go through "Needs Approval" → manual publish |
| **No auto-replies** | Comments and DMs are captured in Engagement Inbox but replies are always manual |
| **Scope enforcement** | Sprint records enforce revision round limits via counter field |
| **Manual fallback** | Every n8n workflow has a documented "do this by hand" checklist (see runbook.md) |

### Platform Risk Mitigation

- No mass DMs or automated outreach
- No automated comment replies
- No scraping of social platforms beyond light URL fetch for brand research
- Lead magnet delivery is manual DM or single opt-in email, not bulk
- Affiliate links (e.g., Skool) only shared post-value-delivery, never in automated sequences

### Data Governance

- Zoho CRM is SSOT for contact/deal data; Airtable stores the Zoho ID as a reference link
- No PII stored in n8n — it passes through as a processor, logs go to Airtable
- Client portal uses Airtable Interface sharing (read-only), no raw base access
- System Logs retain payload excerpts (not full payloads) to avoid storing sensitive data in logs
