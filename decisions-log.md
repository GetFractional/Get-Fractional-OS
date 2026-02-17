# Decisions Log — Get Fractional OS Build

> Documenting design decisions, simplest-viable interpretations of ambiguities, and items needing Matt's approval.
>
> **Updated:** Feb 17, 2026 — Matt's responses integrated, expert rulings finalized.

---

## Design Decisions Made

### D-001: Single Airtable Base *(Confirmed)*

**Decision:** All tables stay in one base ("Get Fractional OS (Core)").

**Matt's input:** "If it's not any more complicated to do multi-base, do that. But speed to market and cashflow is most important."

**Expert ruling:** Multi-base adds real complexity — cross-base sync via n8n, no direct linked records between bases, separate API connections per base, and future maintenance burden. Single base is faster to build, simpler to maintain, and has zero scaling issues at this volume (solo, <1,000 records/month). **Keep single base.**

**Risk:** If base exceeds 50,000 records, performance degrades. At current trajectory, that's 12–18+ months away. If/when it happens, split along clean boundaries (e.g., System Logs → separate base).

### D-002: n8n Over Airtable Automations for External APIs *(Confirmed)*

**Decision:** Unchanged. All external API calls go through n8n. Airtable Automations handle internal-only operations.

### D-003: Engagement Capture → Automated via Official APIs *(Changed)*

**Decision:** Automate social engagement capture using **official platform APIs only** (Meta Graph API for FB/IG, LinkedIn Marketing API for Company Page). No scraping, no unofficial tools.

**Matt's input:** "We should automate this if possible, as long as I don't get banned or suspended."

**Expert ruling:** This is safe and achievable using only first-party APIs:
- **Facebook + Instagram:** Meta Graph API v21 provides webhooks for real-time comment notifications on Page posts and IG Business Account posts. Fully ToS-compliant. Read comments, capture author, message, post reference.
- **LinkedIn:** Marketing API allows reading comments on Company Page posts. Personal profile comments require a social management tool (Buffer, Hootsuite, or Agorapulse) that has official LinkedIn API access and can forward engagement data via webhook. Safe and ToS-compliant.
- **DMs:** Facebook/IG DMs accessible via Messenger Platform API (requires app review). LinkedIn DMs have no API access — must remain manual capture.
- **Replies still manual:** We capture engagement automatically, but Matt still replies manually. The automation is inbound capture only.

**New workflow:** n8n Workflow E (Social Engagement Capture). See `social-automation.md`.

### D-004: Auto-Publishing via Official APIs *(Changed)*

**Decision:** Automate content publishing using **official platform APIs** with an approval gate. Matt approves in Airtable → system publishes to platforms automatically.

**Matt's input:** "Automate posting if it increases efficiency and doesn't hurt impressions/engagement/conversions."

**Expert ruling:** Publishing via official APIs does **not** penalize reach or engagement. All major scheduling tools (Buffer, Later, Hootsuite) use the same APIs. Platforms don't distinguish between API posts and manual posts.
- **Facebook Pages:** Meta Graph API — POST to /{page-id}/feed
- **Instagram Business:** Meta Graph API — Content Publishing API (requires image/video upload → publish flow)
- **LinkedIn Company Page:** Marketing API — POST to ugcPosts endpoint
- **LinkedIn Personal Profile:** Share API — POST to shares endpoint (limited formatting)

**Safety gate preserved:** Content must reach Status = "Approved" in Airtable before the auto-publish workflow triggers. Matt's approval is still required — we just eliminate the copy-paste-publish step.

**New workflow:** n8n Workflow F (Auto-Publish). See `social-automation.md`.

### D-005: Zoho SSOT for Contact/Deal Data *(Confirmed)*

**Decision:** Unchanged. Zoho One is already deployed with CRM, Billing, and Sign. Airtable handles operational data.

**Updated context:** Matt is on Zoho One with CRM, Billing, and Sign already set up. No greenfield Zoho setup needed — just custom field additions and pipeline configuration.

### D-006: Idempotency Key Strategy *(Confirmed)*

**Decision:** Unchanged. SHA-256 hash of deterministic field combinations per workflow. Extended to cover new Workflows E and F:
- Social Engagement: `engagement_capture:{platform}:{post_id}:{comment_id}`
- Auto-Publish: `auto_publish:{content_record_id}:{platform}`

### D-007: Retry Policy *(Confirmed)*

**Decision:** Unchanged. 3 retries, exponential backoff (2s/4s/8s), dead-letter to System Logs.

### D-008: Universal System Logs *(Confirmed)*

**Decision:** Unchanged. Single System Logs table for all workflows. Matt confirmed: "These should be captured so we can reference and debug them over time."

### D-009: Campaign Kits as Separate Table *(Confirmed)*

**Decision:** Unchanged. Linked table, not embedded fields.

### D-010: Client Portal → Softr *(Changed)*

**Decision:** Build the client portal using **Softr** connected to Airtable. Not Airtable Interfaces, not a custom-coded portal.

**Matt's input:** "Don't use Airtable — it's expensive and not the best UX. If we can vibe-code a portal, do that. Unless Softr would be cheaper."

**Expert ruling:** Softr is the right call for MVP. Here's why:
- **Softr:** $59/mo (Business plan), connects directly to Airtable, drag-and-drop portal builder, custom domains, client login, looks professional. Build time: 1-2 days.
- **Custom coded (Next.js):** Free hosting (Vercel), but 5-10 days build time, ongoing maintenance, and you're maintaining code. Better long-term flexibility, but wrong for MVP.
- **Airtable Interfaces:** Included in plan, but limited design, no custom domain, clunky UX. Matt's right that it's not great.

**Recommendation:** Start with Softr. If you outgrow it (need custom logic, multi-tenant complexity), migrate to a custom portal later. Softr's monthly cost is negligible vs. the time saved.

See `client-portal-spec.md` for full Softr build spec.

### D-011: Basic HTML Text Extraction *(Confirmed)*

**Decision:** Unchanged. Basic tag stripping for URL intake. Manual fallback for JS-heavy SPAs.

### D-012: Metrics Capture → Automated Where Possible *(Updated)*

**Decision:** Since we're now integrating official social APIs (D-003, D-004), we can pull basic post metrics automatically. Auto-capture: impressions, likes, comments count, shares. Manual supplement: click-throughs, conversions, qualitative notes.

**Rationale:** The social API connections needed for D-003 and D-004 give us read access to post metrics at no additional cost. Adding a metrics pull to the auto-publish workflow is minimal extra work.

### D-013: Daily Error Digest *(Confirmed)*

**Decision:** Unchanged. Workflow D stays as designed.

### D-014: Proof Capture Stage *(Confirmed)*

**Decision:** Unchanged. "Proof Capture" stage between "Delivered" and "Complete."

---

## Approved Items (Formerly Needing Approval)

### A-001: Founders Promo + Value Ladder *(Resolved)*

**Matt's input:** "Bring expert insights on the most effective ways we can profitably build a 50%+ margin offer. I want multiple offers per step in the value ladder to consider for testing."

**Expert ruling:** Full value ladder with margin analysis, multiple testable options per tier, and fulfillment time estimates documented in `docs/value-ladder.md`. Key decisions:
- **Founders promo:** First 5 clients, invitation-only, requires anonymized case study permission. Creates urgency + proof pipeline.
- **$7 tripwires:** AI-assisted production (15-30 min each) using URL + prompt templates. Massive margin. Purpose is qualification, not revenue.
- **Core sprints:** $4k–$8k at 20–25 hrs work = $160–$400/hr effective rate. Above 50% margin after all costs.
- **Retainers:** Highest margin per hour. 8–12 hrs/mo at $3k–$8k = $250–$1,000/hr.

### A-002: Revision Policy — Delay Clause *(Resolved)*

**Matt's input:** "Clients tend to be behind. Forcing forward creates friction. But there should be consequences."

**Expert ruling:** Implement a **"pause and requeue"** policy:
- If no client feedback within 48 hours, the sprint is **paused** (not auto-approved).
- Matt sends a courtesy notification: "I'm pausing your sprint to give you time. When you're ready with consolidated feedback, I'll slot you into my next available window."
- **Consequence:** Matt moves to other work. Client loses their active slot. Resume depends on Matt's availability.
- **Contract language:** "Sprint timelines assume client feedback within 48 hours of each review milestone. Delays beyond 48 hours will pause the sprint. Resumed sprints are scheduled at the next available production slot."
- This is firm but not adversarial. It respects client timing while protecting Matt's schedule.

### A-003: Case Study Permission — At Intake *(Resolved)*

**Matt's input:** "Best to get it in writing early. But I want clients wanting to showcase their results."

**Expert ruling:** **Ask at intake, upgrade after delivery.**
- **At intake (in scope agreement):** Include clause: "Client grants permission for [Full Public / Anonymized / Process Only] use of project outcomes in case studies and marketing materials."
- **Founders promo discount explicitly requires:** "Anonymized" or "Full Public" as condition of the reduced rate. This is framed as: "In exchange for the founders rate, we ask permission to share anonymized results."
- **After delivery:** Ask if they'd like to upgrade from Anonymized → Full Public. Frame it as: "Your results were great — would you be open to us featuring [Brand Name] specifically? We'd link to your site and give you the spotlight."
- This gets legal coverage at day 0 and makes the post-delivery ask about upgrading, not requesting for the first time.

### A-004: Tripwire Design *(Resolved)*

**Matt's input:** "Make sure it's something people will actually need and want and be willing to pay without issue."

**Expert ruling:** Full tripwire catalog with fulfillment specs, margin analysis, and testing priority documented in `docs/value-ladder.md`. Key insight: tripwires at $7–$97 exist to **qualify buyers and demonstrate capability**, not to generate meaningful revenue. The real test: does the tripwire buyer convert to a $4k+ sprint within 30 days?

### A-005: Zoho One Already Deployed *(Resolved)*

**Matt's input:** "Already committed to Zoho One with CRM, Billing, and Sign set up. Just need to implement changes relevant to what we're doing."

**Expert ruling:** Updated `docs/zoho-spec.md` to account for existing infrastructure. Changes are additive only — custom fields, pipeline stages, workflow rules. No module reinstall needed. Zoho Billing integration for deposit/invoice automation and Zoho Sign for scope agreements are now included.

### A-006: AI Video Integration *(Resolved)*

**Matt's input:** Detailed capabilities of Nano Banana Pro (images: up to 14 reference images, prompt, aspect ratio, resolution up to 4K, 1-4 variants, drawing), Kling 3.0 (video: start/end frame, multi-shot, prompt, audio, 3 reference elements, 5-15s, up to 1080p), and Veo 3.1 (video: 4-8s, aspect ratio, resolution up to 1080p).

**Expert ruling:** New table "AI Video Projects" added to Airtable spec. Stores prompts, settings, reference image links, output links, and links to the Sprint/Campaign Kit they serve. UI-first workflow for now (use the tools directly), but Airtable tracks what was generated, with what settings, for which client. This creates a prompt library and makes sprint fulfillment repeatable. See `docs/ai-video-spec.md`.

### A-007: Skool Affiliate *(Resolved)*

**Matt's input:** Affiliate link: `https://www.skool.com/aivideobootcamp/about?ref=747639c593724d49b7618bf8bcb2363c`

**Expert ruling:** Track affiliate referrals via a tag on Lead/Contact records in both Zoho and Airtable. Add "Affiliate Referrals" view in Airtable Leads table. The affiliate link is stored in the Offers table as a "Lead Magnet" tier offer (Offer Name: "AI Video Bootcamp — Skool Affiliate") with the link in the SOP Link field. Recommendation sequence: share only after delivering value (post-sprint or post-retainer), never in cold outreach.

---

## Open Ambiguities Resolved with Simplest Interpretation

| # | Ambiguity | Resolution | Confidence |
|---|---|---|---|
| 1 | "Airtable AI fields" — which AI provider? | Use Airtable's built-in AI field feature (if on a plan that supports it). If not, leave Summary/Key Excerpts as manual long text fields for now. | Medium |
| 2 | Content Pipeline "Metrics capture task" — what metrics? | Auto-capture via API: impressions, likes, comments count, shares. Manual supplement: CTR, conversions, qualitative notes. | High |
| 3 | "Campaign Brief generation" after approval — what format? | Campaign Brief = a Campaign Kit record with pre-populated Brand Brief, Objection Map, and initial Angles/Hooks from the AI research. Not a separate document format. | High |
| 4 | Engagement Inbox "Owner" field — who owns engagement? | Matt (solo). Field exists for future team scaling. Default is Matt. | High |
| 5 | "Approval Workflow Template" lead magnet — what exactly? | A downloadable PDF or Notion template showing a simple content approval flow (Draft → QA → Approve → Publish). Fulfillment TBD by Matt. | Low |
| 6 | KPI Dashboard "Cycle time per sprint stage" | Requires date-tracking per stage transition. At MVP, track Start Date and Due Date only. Full stage-transition timestamps can be added later via Airtable automations that log date changes. | Medium |
| 7 | n8n Workflow B "Create Approval task" — where? | Created as a notification in Airtable (visible in Daily Cockpit) rather than a separate Tasks table. A Tasks table is not in the MVP spec. If needed later, add a lightweight Tasks table. | High |
| 8 | LinkedIn personal profile automation limitations | LinkedIn's API only supports Company Page posts reliably. For personal profile posts: use a social management tool (Buffer/Hootsuite) with official LinkedIn integration, or publish personal posts manually. Company Page auto-publish works natively via API. | High |
| 9 | Instagram content publishing requires image/video first | Meta's Content Publishing API requires a two-step flow: (1) create media container with image/video URL, (2) publish container. n8n workflow handles this. Images must be hosted on a public URL before publishing. | High |
