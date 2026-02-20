# Zoho Setup Guide — Get Fractional OS

> Step-by-step instructions for configuring Zoho CRM + Zoho Sign.
> Zoho is the deal pipeline and contract layer. Airtable is the operations layer.
> They sync via n8n (see n8n setup guide).

---

## PART 1: ZOHO CRM SETUP

### Step 1: Create Zoho CRM Account

1. Sign up at [zoho.com/crm](https://www.zoho.com/crm/)
2. Free tier works for initial setup. Upgrade to Standard ($14/mo) when you need workflow rules.
3. Complete the initial setup wizard — select "Services" as business type.

### Step 2: Customize the Deals Module

Go to **Settings → Customization → Modules and Fields → Deals**

**Add these custom fields:**

| Field Name | Field Type | Options/Notes |
|---|---|---|
| Offer Type | Picklist | Fit Check ($97), Creative Sprint, Monthly Retainer, Hook Pack ($7), Custom |
| Deposit Amount | Currency | |
| Deposit Paid | Checkbox | |
| Final Amount | Currency | |
| Final Paid | Checkbox | |
| Sprint Start Date | Date | |
| Sprint Due Date | Date | |
| Intake Status | Picklist | Not Sent, Sent, Partial, Complete |
| Airtable Sprint ID | Single line | For sync reference |

**Customize the Deal pipeline stages:**

| Stage | Probability | Stage Order |
|---|---|---|
| Lead | 10% | 1 |
| Qualified | 20% | 2 |
| Fit Check Scheduled | 40% | 3 |
| Fit Check Complete | 50% | 4 |
| Proposal Sent | 60% | 5 |
| Scope Signed | 75% | 6 |
| Deposit Paid | 90% | 7 |
| In Progress | 95% | 8 |
| Delivered | 100% | 9 |
| Closed Won | 100% | 10 |
| Closed Lost | 0% | 11 |

### Step 3: Customize the Contacts Module

Go to **Settings → Customization → Modules and Fields → Contacts**

**Add these custom fields:**

| Field Name | Field Type | Options/Notes |
|---|---|---|
| LinkedIn URL | URL | |
| Lead Source Detail | Single line | e.g., "LinkedIn comment TEARDOWN on Post #3" |
| Lead Score | Number | 0-100 |
| Trigger Word | Picklist | TEARDOWN, SNAPSHOT, SPRINT, SCOPE, Hook Pack, Fit Check, Email |
| Has Purchased | Checkbox | |
| Airtable Contact ID | Single line | For sync reference |

### Step 4: Create Deal Views

1. **My Pipeline** — Kanban view of all open deals, grouped by Stage
2. **This Month's Revenue** — filter: Close Date = this month, Stage = Closed Won
3. **Fit Checks This Week** — filter: Stage = Fit Check Scheduled, Close Date = this week
4. **Overdue Follow-ups** — filter: Next Follow-up Date < today

### Step 5: Set Up Workflow Rules

Go to **Settings → Automation → Workflow Rules**

1. **Fit Check Booked → Send Prep Email:**
   - Trigger: Deal stage changes to "Fit Check Scheduled"
   - Action: Send email template with prep questions

2. **Deposit Paid → Notify Matt:**
   - Trigger: Deposit Paid checkbox = true
   - Action: Send notification email to Matt

3. **Deal Won → Create Follow-up Task:**
   - Trigger: Stage changes to "Closed Won"
   - Action: Create task "Send Sprint Intake Checklist" due in 1 day

---

## PART 2: ZOHO SIGN SETUP

### Step 1: Activate Zoho Sign

1. Go to [zoho.com/sign](https://www.zoho.com/sign/)
2. Activate with same Zoho account
3. Free tier allows 5 documents/month — sufficient for initial launch

### Step 2: Create the Scope Agreement Template

1. Go to **Templates → Create Template**
2. Upload the scope agreement from `/templates/scope-agreement.md` (convert to PDF first)
3. Map merge fields to Zoho CRM Deal fields:

| Template Field | Zoho CRM Source |
|---|---|
| {{Client Name}} | Contact: Full Name |
| {{Company Name}} | Account: Account Name |
| {{Offer Name}} | Deal: Offer Type |
| {{Start Date}} | Deal: Sprint Start Date |
| {{Due Date}} | Deal: Sprint Due Date |
| {{Deal Amount}} | Deal: Amount |
| {{Deposit Amount}} | Deal: Deposit Amount |
| {{Remaining Amount}} | Deal: Final Amount |
| {{Current Date}} | System: Current Date |
| {{Client Title}} | Contact: Title |

4. Set signature fields:
   - Provider signature (Matt) — pre-filled
   - Client signature — required
   - Client date — auto-fill on sign

5. Set the signing order: Provider first, then Client

### Step 3: Connect Zoho Sign to Zoho CRM

1. Go to **Zoho CRM → Settings → Marketplace → Zoho Sign**
2. Install the Zoho Sign integration
3. This allows sending Sign documents directly from Deal records

### Step 4: Create the Send Flow

When a Deal reaches "Proposal Sent" stage:
1. Open the Deal record
2. Click "Send for Signature" (Zoho Sign integration button)
3. Select the Scope Agreement template
4. Merge fields auto-populate from the Deal
5. Send to client
6. When signed, manually update Deal stage to "Scope Signed"

**Future automation:** n8n can listen for Zoho Sign webhook (document signed) and auto-update the Deal stage.

---

## PART 3: ZOHO + AIRTABLE SYNC STRATEGY

Zoho CRM is the **deal pipeline** layer. Airtable is the **operations** layer.

**What lives in Zoho:**
- Deal pipeline and stages
- Contact management
- Revenue reporting
- Contract/scope agreement sending

**What lives in Airtable:**
- Sprint operations and milestones
- Content calendar
- Lead magnet/tripwire tracking
- Deliverable tracking
- Proof objects

**Sync points (via n8n):**
1. When Deal reaches "Deposit Paid" in Zoho → Create Sprint record in Airtable
2. When Sprint status changes in Airtable → Update Deal custom field in Zoho
3. New Contact in Zoho → Create Contact record in Airtable
4. New Lead in Airtable (from content) → Create Contact in Zoho

See the n8n setup guide for workflow details.
