# Decisions Log — Get Fractional OS Build

> Documenting design decisions, simplest-viable interpretations of ambiguities, and items needing Matt's approval.

---

## Design Decisions Made

### D-001: Single Airtable Base

**Decision:** All 11 tables live in one base ("Get Fractional OS (Core)").

**Rationale:** The spec explicitly says "single base MVP" and flags multi-base fragmentation as a "WON'T." One base keeps linked records simple and avoids cross-base sync complexity.

**Risk:** If the base exceeds 50,000 records total, performance may degrade. At current scale (solo, 4 sprints/mo), this is not a concern for 12+ months.

### D-002: n8n Over Airtable Automations for External APIs

**Decision:** All external API calls (Zoho, URL fetching) go through n8n. Airtable Automations handle only internal record operations (status changes, notifications, log writes).

**Rationale:** Spec Section 9 explicitly defines this split. n8n provides retry logic, idempotency, dead-letter handling, and credential management that Airtable Automations lack.

### D-003: Engagement Inbox is Manual-Entry at MVP

**Decision:** Social engagement (comments, DMs) is captured manually by Matt or a future VA creating Airtable records. No automated social scraping.

**Rationale:** Spec Section 1 (Assumptions Register) states "Human-in-loop for publishing and replies is required to avoid platform risk" with High confidence. Automated comment scraping would violate platform ToS.

**Trade-off:** More manual work, but zero platform risk. A VA can handle this once volume grows.

### D-004: Content Publishing is Always Manual

**Decision:** No auto-publishing to any social platform. The workflow moves content to "Scheduled" status, but Matt manually publishes.

**Rationale:** Spec hard constraint: "publishing + comment replies stay manual/approval-gated." This appears in multiple places and is a core safety principle.

### D-005: Zoho is SSOT for Contact/Deal Data, Airtable for Everything Else

**Decision:** Contact details and deal pipeline live in Zoho as the authoritative source. Airtable stores a `Zoho ID` reference field. Operational data (sprints, content, engagement) lives in Airtable as SSOT.

**Rationale:** Spec Section 8 defines this SSOT split. Zoho handles CRM-specific concerns (pipeline stages, SLAs, follow-up sequences). Airtable handles operational delivery.

### D-006: Idempotency Key Strategy

**Decision:** Using SHA-256 hash of deterministic field combinations per workflow:
- Lead Capture: `platform + handle + post_url`
- URL Intake: `account_id + website_url`
- Content Publish: `content_record_id`

**Rationale:** Spec requires idempotency keys. SHA-256 is deterministic, collision-resistant, and the field combinations ensure uniqueness within each workflow context.

### D-007: Retry Policy = 3 Attempts, Exponential Backoff

**Decision:** All n8n workflows retry external API calls 3 times with 2s/4s/8s backoff before dead-lettering to System Logs.

**Rationale:** Spec Section 9 requires "exponential backoff, capped at 3" and "dead-letter queue." Three retries balances persistence with avoiding rate-limit escalation.

### D-008: System Logs Table as Universal Audit Trail

**Decision:** One System Logs table serves all workflows and automations. No separate log tables per system.

**Rationale:** Spec defines a single System Logs table with a `System` field to differentiate sources. This keeps the audit trail centralized and queryable.

### D-009: Campaign Kits as Separate Table (Not Embedded in Sprints)

**Decision:** Campaign Kits are a linked table, not fields embedded in the Sprints table.

**Rationale:** Spec Section 8 defines Campaign Kits as a separate table with rollup fields (Angles Count, Hooks Count). This allows one Sprint to have one Kit record, keeping the Sprint record clean and the Kit extensible.

### D-010: Client Portal via Airtable Interface Sharing

**Decision:** Client portals are shared Airtable Interface pages filtered by Account, not a custom-built portal.

**Rationale:** Spec Section 8 says "Share Interface pages read-only. No raw base access, no automations exposed." Airtable Interface sharing is the simplest implementation that meets this requirement.

**Limitation:** Limited design control. If a more polished client experience is needed later, consider Softr or a custom portal.

### D-011: Workflow B (URL Intake) Uses Basic HTML Text Extraction

**Decision:** URL content is fetched via HTTP request and parsed with basic HTML tag stripping. No headless browser rendering.

**Rationale:** Spec says "light crawl" and "respect robots." Basic text extraction covers most marketing sites. JavaScript-rendered SPAs may not extract fully, but this is acceptable for MVP. The manual fallback covers edge cases.

### D-012: Metrics Capture is Manual at MVP

**Decision:** After content is published and Post URL is captured, a notification/reminder is created but metrics are entered manually. No automated social API metrics pull.

**Rationale:** Spec Section 12 (MoSCoW) lists "Metrics capture automation" as COULD (nice-to-have). Social platform APIs require approval processes and add complexity. Manual entry works for 5 posts/week.

### D-013: Added Workflow D (Daily Error Digest)

**Decision:** Created a fourth n8n workflow not explicitly spec'd but required by the error handling design: Daily Error Digest email.

**Rationale:** Spec Section 9 says "Alerting: daily digest of errors to your email/Slack." The digest workflow operationalizes this requirement. Without it, the System Logs table would accumulate unreviewed errors.

### D-014: Sprint Stage Includes "Proof Capture" Between Delivered and Complete

**Decision:** Added "Proof Capture" as a stage between "Delivered" and "Complete."

**Rationale:** Spec Section 5 and the implementation runbook emphasize proof capture as a critical step. Without a dedicated stage, proof capture could be skipped. The stage makes it visible in the Kanban view and the Sprint Delivery Cockpit.

---

## Items Needing Matt's Approval

### A-001: Founders Promo Pricing

**Question:** The spec mentions $3,500 founders promo "with tight scope." Should this be available to the first N clients, first N days, or by invitation only?

**Current implementation:** Offer record created with Price Notes = "Founders promo $3.5k." No automated discount logic. Matt applies at his discretion.

### A-002: Revision Policy — 48-Hour Silence = Approval

**Question:** The runbook SOP states "If no feedback within 48 hours of delivery: considered approved." Does Matt want this to be a soft reminder or a hard policy communicated to clients?

**Current implementation:** Documented in the Revision Policy SOP. Not auto-enforced by any automation.

### A-003: Case Study Permission — When to Ask

**Question:** Should case study permission be asked at intake (before work starts) or after delivery (when proof exists)?

**Current implementation:** Field exists on both Account (Airtable) and Contact (Zoho). The runbook places the ask in the post-delivery sequence (Day 3 after delivery). The founders promo already conditions on "case study permission."

### A-004: Tripwire Fulfillment Method

**Question:** The $7 Hook Pack and $7 Angle Pack — are these pre-built templates customized per client URL, or fully custom builds per purchaser?

**Current implementation:** Offer records created with generic descriptions. Fulfillment SOP needs Matt's input on production method (template vs. custom).

### A-005: Zoho vs. Simpler CRM

**Question:** The spec assumes Zoho CRM. If Matt hasn't already committed to Zoho, a lighter option (e.g., Airtable-only with pipeline views) could reduce setup complexity for MVP.

**Current implementation:** Full Zoho spec built per spec requirements. If Zoho is deferred, the Leads table in Airtable can serve as a temporary pipeline with the Kanban view by Stage.

### A-006: Higgsfield Integration Timing

**Question:** Spec mentions "Higgsfield UI-first now, API later." What Higgsfield outputs should be stored in Airtable, and in which table?

**Current implementation:** No Higgsfield integration built. Prompts/settings/outputs can be stored as attachments or links in Knowledge Library or Campaign Kits when ready.

### A-007: Skool Affiliate Tracking

**Question:** Should affiliate referrals be tracked as their own lead source in Zoho, or just as a tag on existing contacts?

**Current implementation:** Zoho tag `affiliate-interest` defined. Airtable doesn't have a dedicated Affiliate table. The simplest approach: tag on existing Lead/Contact records.

---

## Open Ambiguities Resolved with Simplest Interpretation

| # | Ambiguity | Resolution | Confidence |
|---|---|---|---|
| 1 | "Airtable AI fields" — which AI provider? | Use Airtable's built-in AI field feature (if on a plan that supports it). If not, leave Summary/Key Excerpts as manual long text fields for now. | Medium |
| 2 | Content Pipeline "Metrics capture task" — what metrics? | At MVP: impressions, comments, DMs, link clicks. Entered manually. Specific fields not added to avoid premature structure. | Medium |
| 3 | "Campaign Brief generation" after approval — what format? | Campaign Brief = a Campaign Kit record with pre-populated Brand Brief, Objection Map, and initial Angles/Hooks from the AI research. Not a separate document format. | High |
| 4 | Engagement Inbox "Owner" field — who owns engagement? | Matt (solo). Field exists for future team scaling. Default is Matt. | High |
| 5 | "Approval Workflow Template" lead magnet — what exactly? | A downloadable PDF or Notion template showing a simple content approval flow (Draft → QA → Approve → Publish). Fulfillment TBD by Matt. | Low |
| 6 | KPI Dashboard "Cycle time per sprint stage" | Requires date-tracking per stage transition. At MVP, track Start Date and Due Date only. Full stage-transition timestamps can be added later via Airtable automations that log date changes. | Medium |
| 7 | n8n Workflow B "Create Approval task" — where? | Created as a notification in Airtable (visible in Daily Cockpit) rather than a separate Tasks table. A Tasks table is not in the MVP spec. If needed later, add a lightweight Tasks table. | High |
