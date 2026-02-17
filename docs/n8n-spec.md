# n8n Automation Spec — Get Fractional OS

## 1. Environment Variables

> Store these in n8n Credentials / Environment. **No secrets in workflow JSON.**

| Variable | Description | Used By |
|---|---|---|
| `AIRTABLE_API_KEY` | Airtable Personal Access Token (scoped to Get Fractional OS base) | All workflows |
| `AIRTABLE_BASE_ID` | Base ID for "Get Fractional OS (Core)" | All workflows |
| `ZOHO_CLIENT_ID` | Zoho OAuth2 Client ID | Workflow A, B |
| `ZOHO_CLIENT_SECRET` | Zoho OAuth2 Client Secret | Workflow A, B |
| `ZOHO_REFRESH_TOKEN` | Zoho OAuth2 Refresh Token | Workflow A, B |
| `ZOHO_ORG_ID` | Zoho Organization ID | Workflow A, B |
| `N8N_WEBHOOK_SECRET` | Shared secret for webhook authentication | Workflow A |
| `ALERT_EMAIL` | Email address for error digest alerts | All workflows |

### Airtable Table IDs (configure after base creation)

| Variable | Table |
|---|---|
| `AT_TABLE_ACCOUNTS` | Accounts |
| `AT_TABLE_LEADS` | Leads |
| `AT_TABLE_CONTENT` | Content Pipeline |
| `AT_TABLE_ENGAGEMENT` | Engagement Inbox |
| `AT_TABLE_KNOWLEDGE` | Knowledge Library |
| `AT_TABLE_SPRINTS` | Sprints |
| `AT_TABLE_SYSTEM_LOGS` | System Logs |

---

## 2. Shared Patterns

### Idempotency Key Strategy

Every workflow that creates or updates an external record generates a deterministic key:

```
idempotency_key = SHA256(workflow_name + ":" + unique_field_combination)
```

| Workflow | Key Composition |
|---|---|
| Lead Capture | `lead_capture:{platform}:{handle}:{post_url}` |
| URL Intake | `url_intake:{account_id}:{website_url}` |
| Content Publish | `content_publish:{content_record_id}` |

Before any create operation, the workflow checks: "Does a record with this idempotency key already exist?" If yes, it updates instead of creating.

### Retry Strategy

All external API calls use this pattern:

```
Retry: 3 attempts
Backoff: exponential (2s, 4s, 8s)
On exhaustion: write to System Logs with severity=Error, status=New
```

In n8n, this is implemented via the **Retry on Fail** node setting (set `maxTries=3`, `waitBetweenTries=2000` with multiplier).

### Dead-Letter Handling

When retries are exhausted:

1. Write a System Logs record:
   - Severity: `Error`
   - System: `n8n`
   - Workflow: `{workflow_name}`
   - Message: human-readable error description
   - Payload Excerpt: truncated input (max 500 chars, no full PII)
   - Status: `New`
   - Retry Count: 3
2. Send email notification to `ALERT_EMAIL` (daily digest or immediate for Critical)

### Logging Pattern

Every workflow writes to System Logs on **both success and failure**:

```
Success → Severity: Info, Status: Resolved
Warning → Severity: Warn, Status: Resolved (e.g., partial success)
Error   → Severity: Error, Status: New
Critical → Severity: Critical, Status: New (e.g., Zoho auth failure)
```

---

## 3. Workflow A: Lead Capture → Zoho Upsert → Airtable Log

### Purpose
Capture leads from social engagement (comments, DMs, form submissions) into Zoho CRM and log them in Airtable.

### Trigger Options
- **Primary:** Webhook (POST) with shared secret validation
- **Secondary:** Airtable trigger — when Engagement Inbox record has `Lead Created = true` and no linked Lead record
- **Manual:** "Convert to Lead" button in Airtable Interface triggers webhook

### Input Payload Schema

```json
{
  "handle": "@johndoe",
  "name": "John Doe",
  "email": "john@example.com",
  "platform": "LinkedIn",
  "source_type": "Comment",
  "post_url": "https://linkedin.com/feed/update/urn:li:activity:123",
  "message": "Interested in the sprint!",
  "offer_interest": "Creative Sprint",
  "engagement_record_id": "recABC123"
}
```

### Steps

```
[1. Webhook Trigger]
  ├── Validate: N8N_WEBHOOK_SECRET matches header
  └── Reject with 401 if invalid

[2. Normalize + Clean]
  ├── Trim whitespace from handle, name, email
  ├── Lowercase platform
  ├── Default source_type to "DM" if missing
  └── Generate idempotency_key: SHA256("lead_capture:" + platform + ":" + handle + ":" + post_url)

[3. Check Idempotency]
  ├── Search Airtable Leads: filterByFormula = {Zoho ID} != "" AND {Name / Handle} = handle
  └── If found with matching idempotency → skip to step 6 (log as duplicate, no error)

[4. Zoho Search]
  ├── GET /crm/v2/Leads/search?email={email}
  ├── Also search by handle if email is empty
  ├── If found → capture Zoho Lead ID → go to step 5a
  └── If not found → go to step 5b

[5a. Zoho Update]
  ├── PUT /crm/v2/Leads/{id}
  ├── Update: Source Platform, Source Type, Original Post URL, Interest
  └── Capture response

[5b. Zoho Create]
  ├── POST /crm/v2/Leads
  ├── Fields: Last Name, Email, Source Platform, Source Type, Original Post URL, Interest
  ├── Capture new Zoho Lead ID
  └── On error → retry (3x exp backoff)

[6. Airtable Create/Update Lead]
  ├── Search Airtable Leads by handle
  ├── If exists → update with Zoho ID, refresh source info
  ├── If not → create new Lead record
  │     Fields: Name/Handle, Email, Source, Source Platform, Stage="New", Zoho ID, Notes
  └── If engagement_record_id provided → link Engagement record + set Lead Created = true

[7. Log Success]
  └── Create System Logs record:
        Severity=Info, System=n8n, Workflow="Lead Capture Upsert",
        Message="Lead upserted: {handle} from {platform}",
        Record Link=Airtable Lead URL, Status=Resolved, Retry Count=0

[Error Handler — wraps steps 4-6]
  └── On retry exhaustion:
        Create System Logs record:
        Severity=Error, System=n8n, Workflow="Lead Capture Upsert",
        Message="Failed after 3 retries: {error_message}",
        Payload Excerpt=truncated input, Status=New, Retry Count=3
```

### Manual Fallback

If n8n is down or Zoho API is unreachable:

1. Open Airtable → Leads table
2. Create record manually: Name/Handle, Email, Source, Source Platform, Stage = "New"
3. Open Zoho CRM → Leads module → Create Lead manually
4. Copy Zoho Lead ID back to Airtable record
5. Create System Logs record: Severity=Warn, System=Manual, Workflow="Lead Capture Upsert", Message="Manual fallback used"

---

## 4. Workflow B: URL Intake → Brand Research → Brief → Approval

### Purpose
When a new prospect account is created with a website URL, automatically research the brand, create knowledge records, draft ICP/brand voice, and create an approval task.

### Trigger
- Airtable trigger: when Accounts table record has `Status = "Prospect"` AND `Website URL` is not empty

### Steps

```
[1. Trigger: New/Updated Account]
  ├── Filter: Status = "Prospect" AND Website URL is not empty
  └── Generate idempotency_key: SHA256("url_intake:" + account_id + ":" + website_url)

[2. Check Idempotency]
  ├── Search Knowledge Library: filterByFormula = Related Account = {account_id}
  └── If records exist → skip to step 6 (already processed, log info)

[3. Fetch URL Content]
  ├── HTTP Request: GET {website_url}
  │   - Timeout: 10s
  │   - Respect robots.txt (check /robots.txt first)
  │   - User-Agent: "GetFractionalBot/1.0 (brand research)"
  ├── Parse homepage HTML → extract text content
  ├── Attempt to fetch: /products, /pricing, /about (relative paths)
  │   - Skip any that return 4xx/5xx or are blocked by robots.txt
  └── On complete failure → log warning, proceed with what's available

[4. Create Knowledge Library Records]
  ├── For each successfully fetched page:
  │   Create Airtable record in Knowledge Library:
  │     Title: "{Account Name} - {page_type}"
  │     Type: "Link"
  │     Tags: ["Brand", "Research"]
  │     Source Link: page URL
  │     Related Account: link to Account record
  └── Log: "{n} pages captured for {Account Name}"

[5. Trigger AI Summary Fields]
  ├── Option A (Airtable AI): Let Airtable AI fields auto-populate Summary + Key Excerpts
  ├── Option B (n8n AI node): Use an LLM node to generate:
  │     - Brand voice summary (2-3 sentences)
  │     - ICP draft v1 (who they sell to, what they sell)
  │     - Likely objections (3-5 common objections)
  └── Write AI outputs to Account.Brand Voice Notes or to ICP/Objections draft records

[6. Create ICP Draft Record]
  ├── Create ICP record linked to Account
  │   Fields: ICP Name = "{Account Name} - Primary ICP (Draft)",
  │           JTBD Functional, JTBD Emotional, Trigger Events (from AI)
  └── Create 3-5 Objection records linked to ICP

[7. Create Approval Task]
  ├── Set Account field or create notification:
  │   "Review Brand + ICP Draft for {Account Name}"
  ├── Set a flag/checkbox on Account: "Research Complete - Needs Review"
  └── Send notification to Matt

[8. Wait for Approval] (manual step — Matt reviews in Daily Cockpit)

[9. On Approval → Generate Campaign Brief]
  ├── Trigger: Matt approves (sets flag or moves status)
  ├── Create Sprint record:
  │     Sprint Name: "{Account Name} - Creative Sprint - {date}"
  │     Account: linked
  │     Offer: "Creative Sprint"
  │     Stage: "Intake"
  ├── Create Campaign Kit record linked to Sprint
  ├── Pre-populate: Brand Brief, Objection Map from Knowledge + ICP
  └── Log success

[Error Handler]
  └── On any failure:
        Log to System Logs, severity based on impact
        If URL fetch fails completely → Severity=Warn, "Manual research required"
        If Airtable write fails → Severity=Error, retry then dead-letter
```

### Manual Fallback

1. Visit the prospect's website manually
2. Create Knowledge Library records by hand (copy/paste key content)
3. Write brand voice notes in Account record
4. Create ICP and Objection records manually
5. Log: System=Manual, Workflow="URL Intake Research"

---

## 5. Workflow C: Content Publish Prep → Post URL Capture → Metrics

### Purpose
Guide the QA → approval → publish → metrics capture flow for content. Keeps humans in the loop for all publishing.

### Trigger
- Airtable trigger: when Content Pipeline.Status changes to `"Needs Approval"`

### Steps

```
[1. Trigger: Status → "Needs Approval"]
  ├── Read full Content Pipeline record
  └── Generate idempotency_key: SHA256("content_publish:" + record_id)

[2. Validate QA Completion]
  ├── Check: Tone QA Complete = true
  ├── Check: Claims QA Complete = true
  ├── Check: Privacy QA Complete = true
  ├── If any QA incomplete:
  │     Set Status back to "Needs QA"
  │     Log: Severity=Warn, "Approval requested but QA incomplete for: {Post Title}"
  │     Stop workflow
  └── If all QA complete → continue

[3. Create Approval Notification]
  ├── Send notification to Matt:
  │   "Content ready for final approval: {Post Title}"
  │   Include: Platform, Pillar, CTA Type, Preview of Draft (first 200 chars)
  └── Record appears in Daily Cockpit → Needs Approval section

[4. Wait for Approval] (manual — Matt reviews)

[5a. If Approved]
  ├── Set Status = "Scheduled"
  ├── Set Publish Date (if not already set)
  ├── Log: Severity=Info, "Content approved: {Post Title}"
  └── Matt publishes manually on platform

[5b. If Rejected]
  ├── Set Status = "Draft"
  ├── Matt adds Approval Notes
  └── Log: Severity=Info, "Content rejected: {Post Title}, reason: {Approval Notes}"

[6. Post-Publish: Post URL Capture]
  ├── Trigger: Post URL field is populated (Airtable automation or webhook)
  ├── Validate URL format
  ├── Set Status = "Published" (if not already)
  └── Log: Severity=Info, "Published: {Post Title} at {Post URL}"

[7. Create Metrics Capture Task]
  ├── Create reminder/notification: "Capture 24h metrics for: {Post Title}"
  ├── Schedule for Publish Date + 24 hours
  │   (In MVP: just send a notification. Later: automated metrics pull.)
  └── Log: Severity=Info, "Metrics capture task created for: {Post Title}"

[Error Handler]
  └── On Airtable write failure:
        Retry 3x, then dead-letter to System Logs
        Manual fallback: update Content Pipeline status by hand
```

### Manual Fallback

1. Review content in Airtable Content Pipeline table directly
2. Change Status field manually (Draft → Needs QA → Needs Approval → Scheduled → Published)
3. Paste Post URL after publishing
4. Set a calendar reminder for metrics capture
5. Log: System=Manual, Workflow="Content Publish Prep"

---

## 6. Workflow D: Daily Error Digest (Utility)

### Purpose
Send a daily summary of unresolved errors to Matt.

### Trigger
- Schedule: Daily at 8:00 AM (Matt's timezone)

### Steps

```
[1. Query System Logs]
  ├── Filter: Severity IN ("Error", "Critical") AND Status = "New"
  └── Sort by Timestamp desc

[2. Format Digest]
  ├── If 0 records → skip (no email)
  ├── If 1+ records → format email:
  │     Subject: "Get Fractional OS — {count} unresolved errors"
  │     Body: table of Workflow, Message, Timestamp, Record Link
  └── Cap at 20 entries (add "and {n} more..." if exceeding)

[3. Send Email]
  ├── Send to ALERT_EMAIL
  └── Log: Severity=Info, Workflow="Daily Error Digest", Message="Sent digest with {count} errors"
```

---

## 7. n8n Workflow JSON Exports

> Exported JSON files are in the `/n8n/` directory. These are importable into n8n via **Workflows → Import from File**.

| File | Workflow |
|---|---|
| `n8n/workflow-a-lead-capture.json` | Lead Capture → Zoho Upsert → Airtable Log |
| `n8n/workflow-b-url-intake.json` | URL Intake → Brand Research → Approval |
| `n8n/workflow-c-content-publish.json` | Content Publish Prep → Post URL → Metrics |
| `n8n/workflow-d-error-digest.json` | Daily Error Digest |
| `n8n/workflow-e-social-engagement.json` | Social Engagement Capture (FB + IG + LinkedIn) |
| `n8n/workflow-f-auto-publish.json` | Auto-Publish to Social Platforms |

### Import Instructions

1. Open n8n instance
2. Go to **Workflows** → **Add Workflow** → **Import from File**
3. Select the JSON file
4. Configure credentials:
   - Create Airtable credential with `AIRTABLE_API_KEY`
   - Create Zoho CRM OAuth2 credential with client ID, secret, refresh token
   - Create SMTP / Email credential for error digest
   - Create Meta (Facebook) OAuth2 credential with App ID, App Secret, Page Access Token
   - Create LinkedIn OAuth2 credential with Client ID, Client Secret
5. Update all Airtable nodes with your actual Base ID and Table IDs
6. Activate the workflow
7. Test with a sample record before going live

### Post-Import Checklist

- [ ] All credentials connected (green indicator on each node)
- [ ] Airtable Base ID and Table IDs updated
- [ ] Zoho module and field names match your Zoho setup
- [ ] Meta webhook URL registered in Facebook App dashboard
- [ ] Meta webhook verify token matches n8n environment variable
- [ ] LinkedIn Company Page ID configured
- [ ] Webhook URLs registered where needed
- [ ] Test run completed with sample data
- [ ] System Logs record created for test run
- [ ] Error email received for simulated failure

---

## 8. Addendum: Workflows E, F, G (v2)

> Added per Matt's decisions on social automation and auto-publishing.

### Environment Variables (New)

| Variable | Description | Used By |
|---|---|---|
| `META_APP_ID` | Meta (Facebook) App ID | E, F, G |
| `META_APP_SECRET` | Meta App Secret | E, F, G |
| `META_PAGE_ACCESS_TOKEN` | Long-lived FB Page Access Token | E, F, G |
| `META_PAGE_ID` | Facebook Page ID | F |
| `META_IG_USER_ID` | Instagram Business Account ID | F, G |
| `META_WEBHOOK_VERIFY_TOKEN` | Token for Meta webhook verification | E |
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth2 Client ID | E, F |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth2 Client Secret | E, F |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn Access Token | E, F |
| `LINKEDIN_ORG_ID` | LinkedIn Company Page Organization ID | E, F |

### Workflow E: Social Engagement Capture

**Purpose:** Auto-capture comments from FB, IG, and LinkedIn Company Page posts into Airtable Engagement Inbox. No auto-replies.

**Triggers:**
- Facebook + Instagram: Meta Webhooks (real-time)
- LinkedIn: Polling every 15 minutes

**Key features:**
- CTA keyword detection (SPRINT, TEARDOWN, SNAPSHOT, etc.) — flags high-priority engagement
- Idempotency key per comment to prevent duplicates
- Auto-links to Content Pipeline post record
- All captured engagement appears in Daily Cockpit

**See full spec:** `docs/social-automation.md`

### Workflow F: Auto-Publish

**Purpose:** When Matt approves content (Status = "Approved"), auto-publish to the designated platform via official API.

**Safety gate:** Content MUST pass through `Draft → Needs QA → Needs Approval → Approved` before publishing. Matt's approval is still required.

**Supports:**
- Facebook Page posts (text, with optional link)
- Instagram posts (requires image attachment in Airtable record)
- LinkedIn Company Page posts (text, with optional link)
- "All" platform option — publishes sequentially to all three

**Key features:**
- Captures Post URL back to Airtable automatically
- Sets Publish Date on publish
- Stores Platform Post ID for later metrics capture
- Partial failure handling (if one platform fails, others still publish)

**See full spec:** `docs/social-automation.md`

### Workflow G: Metrics Capture (24h Post-Publish)

**Purpose:** Pull engagement metrics 24h after publishing via platform APIs.

**Trigger:** Daily batch at 9 AM — finds Published content where Metrics Captured At is empty and Publish Date was yesterday or earlier.

**Metrics captured:**
- Impressions, Likes/Reactions, Comments Count, Shares/Reposts
- Link Clicks (where API supports)
- Writes to Content Pipeline record fields

**Manual supplement:** CTR, conversion data, qualitative notes still entered manually.

**See full spec:** `docs/social-automation.md`
