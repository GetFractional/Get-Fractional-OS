# n8n Setup Guide — Get Fractional OS

> Step-by-step instructions for deploying n8n workflows.
> n8n is the automation glue between Airtable, Zoho, Stripe, and email.
> Start with self-hosted (free) or n8n Cloud ($20/mo for convenience).

---

## STEP 1: Deploy n8n

### Option A: n8n Cloud (Recommended for speed)
1. Sign up at [n8n.io](https://n8n.io)
2. Select Starter plan ($20/mo, 2,500 executions)
3. Your instance is live immediately at `your-name.app.n8n.cloud`

### Option B: Self-Hosted (Free, more setup)
1. Requirements: VPS with Docker (DigitalOcean $6/mo droplet works)
2. Deploy:
```bash
docker run -d --restart unless-stopped \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  --name n8n \
  n8nio/n8n
```
3. Access at `http://your-server-ip:5678`
4. Set up reverse proxy (Caddy or nginx) for HTTPS

---

## STEP 2: Configure Credentials

Go to **Settings → Credentials** and add:

### 2a. Airtable
- Type: Airtable API
- API Key: (from Airtable setup guide, Step 5)
- Test connection

### 2b. Zoho CRM
- Type: Zoho CRM OAuth2
- Client ID + Secret: Create at [api-console.zoho.com](https://api-console.zoho.com)
  - Application type: Server-based
  - Redirect URL: `https://your-n8n-url/rest/oauth2-credential/callback`
  - Scopes: `ZohoCRM.modules.ALL, ZohoCRM.settings.ALL`
- Authorize and test connection

### 2c. Stripe
- Type: Stripe API
- Secret Key: From Stripe Dashboard → Developers → API keys
- Test connection

### 2d. Email (SMTP)
- Type: SMTP
- Host: Your email provider's SMTP server
- Port: 587 (TLS)
- Username + Password
- Test with a send

---

## STEP 3: Build Workflows

### Workflow A: LinkedIn Comment → Lead Capture (Day 0-2 Priority)

**Purpose:** When Matt manually flags a LinkedIn comment lead, create records in Airtable and Zoho.

**Trigger:** Manual trigger (button in n8n) or webhook from a simple form

**Flow:**
```
[Manual Trigger / Webhook]
    → [Set node: parse name, URL, trigger word, source post]
    → [Airtable: Create record in Leads table]
    → [Zoho CRM: Create Contact]
    → [Zoho CRM: Create Deal (stage: Lead)]
    → [Email: Send Matt notification with lead details]
```

**Field mapping:**

| Input | Airtable Leads Field | Zoho Contact Field |
|---|---|---|
| name | Name | Full Name |
| email | Email | Email |
| url | URL Submitted | — |
| trigger_word | Trigger Word | Trigger Word |
| source | Source Post | Lead Source Detail |

**Notes:**
- For Day 0-2, this is semi-manual: Matt copies lead info into a simple form/webhook
- Later, this can be automated with a LinkedIn scraping tool or Phantombuster

---

### Workflow B: Stripe Payment → Tripwire Fulfillment

**Purpose:** When someone buys the $7 Hook Pack, auto-deliver and create lead records.

**Trigger:** Stripe webhook (checkout.session.completed)

**Flow:**
```
[Stripe Webhook: checkout.session.completed]
    → [IF: amount = $7 → Hook Pack flow]
    → [Airtable: Create record in Leads table (Trigger Word: Hook Pack)]
    → [Airtable: Create record in Invoices table (Type: Tripwire, Status: Paid)]
    → [Email: Send Hook Pack delivery email with PDF attachment]
    → [Wait 3 days]
    → [Email: Send follow-up "How'd the hooks work?"]
    → [Wait 3 days]
    → [Email: Send Fit Check CTA]
```

**Stripe setup:**
1. Create a product in Stripe: "Hook Pack" — $7, one-time
2. Create a Payment Link or Checkout Session
3. Add webhook endpoint in Stripe Dashboard → Developers → Webhooks
4. Endpoint URL: `https://your-n8n-url/webhook/stripe-payment`
5. Events to listen for: `checkout.session.completed`

---

### Workflow C: Fit Check Booked → Prep Sequence

**Purpose:** When a Fit Check is booked (Calendly or manual), trigger prep.

**Trigger:** Calendly webhook or manual trigger

**Flow:**
```
[Calendly Webhook / Manual Trigger]
    → [Airtable: Update Lead status to "Qualified"]
    → [Zoho CRM: Update Deal stage to "Fit Check Scheduled"]
    → [Email: Send Fit Check prep email to client]
    → [Email: Send Matt a prep summary with lead info]
```

---

### Workflow D: Deal Won → Sprint Kickoff

**Purpose:** When deposit is paid and scope is signed, kick off the sprint.

**Trigger:** Zoho CRM webhook (Deal stage changes to "Deposit Paid")

**Flow:**
```
[Zoho Webhook: Deal stage = Deposit Paid]
    → [Airtable: Create Sprint record]
    → [Airtable: Create Deliverable records (7 standard deliverables)]
    → [Email: Send Sprint Intake Checklist to client]
    → [Email: Send Matt sprint kickoff notification]
    → [Set: Calculate milestone dates (Day 3, Day 10, Day 14)]
    → [Airtable: Update Sprint with milestone dates]
```

**Standard deliverable records to create:**
1. ICP Brief
2. Objection Map
3. Ad Angles
4. Hooks
5. Ad Concepts
6. LP Copy Kit
7. Testing Plan

---

### Workflow E: Sprint Milestone Alerts

**Purpose:** Alert Matt and client at key milestone dates.

**Trigger:** Schedule (daily at 8am)

**Flow:**
```
[Schedule: Daily 8am]
    → [Airtable: Get all active sprints]
    → [IF: Today = Day 3 milestone → Send Day 3 review reminder]
    → [IF: Today = Day 10 milestone → Send Day 10 draft reminder]
    → [IF: Today = Day 14 milestone → Send delivery day alert]
    → [IF: Feedback overdue (48hr past milestone) → Send pause warning]
```

---

### Workflow F: Weekly Metrics Collection

**Purpose:** Aggregate weekly metrics and store in Airtable.

**Trigger:** Schedule (every Monday at 7am)

**Flow:**
```
[Schedule: Monday 7am]
    → [Airtable: Count new leads this week]
    → [Airtable: Count fit checks this week]
    → [Zoho: Get deals closed this week + revenue]
    → [Airtable: Count content published this week]
    → [Airtable: Create Metrics Dashboard record]
    → [Email: Send Matt weekly dashboard summary]
```

---

## STEP 4: Deployment Priority

| Priority | Workflow | Needed By |
|---|---|---|
| 1 | A: LinkedIn Comment → Lead Capture | Day 0 |
| 2 | B: Stripe → Tripwire Fulfillment | Day 3 (when tripwire goes live) |
| 3 | C: Fit Check → Prep Sequence | Day 3 |
| 4 | D: Deal Won → Sprint Kickoff | Week 2 |
| 5 | E: Sprint Milestone Alerts | Week 2 |
| 6 | F: Weekly Metrics | Week 3 |

---

## STEP 5: Testing

Before going live with any workflow:

1. **Use test data.** Create a test contact, test deal, test lead.
2. **Check every node.** Run workflow manually and inspect each node's output.
3. **Verify Airtable records.** Confirm records are created with correct field values.
4. **Verify emails.** Send to Matt's own email first.
5. **Test error handling.** What happens if Airtable is down? If a field is missing?

Add an **Error Trigger** node to each workflow that sends Matt an email if any workflow fails.
