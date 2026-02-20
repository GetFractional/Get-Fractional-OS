# Airtable Go-Live Runbook

> Do these steps in order. Total time: ~30 minutes.
> You need: a terminal with curl/jq, your Airtable login, and this doc.

---

## PHASE 1: Run the Build Script (~2 min)

### 1A. Get your workspace ID

Open a terminal and run:

```bash
export AIRTABLE_API_KEY="patXXXXXX"   # your Personal Access Token

curl -s https://api.airtable.com/v0/meta/workspaces \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq '.workspaces'
```

Copy the `id` value (starts with `wsp`). If you have multiple workspaces, pick the one you want the base in.

### 1B. Run the script

```bash
export AIRTABLE_API_KEY="patXXXXXX"
export AIRTABLE_WORKSPACE_ID="wspXXXXXX"

cd Get-Fractional-OS
bash setup/airtable-build.sh
```

Wait for it to finish. You'll see green `[OK]` lines for each table, relationship, and view. At the end it prints the Base ID and URL.

### 1C. Open the base

Go to the URL it prints: `https://airtable.com/appXXXXXX`

Confirm you see 12 tables in the left sidebar. Click through a few to verify fields are there. If anything looks wrong, delete the base and re-run — the script is idempotent on a new base.

---

## PHASE 2: Configure Views (manual — ~15 min)

Omni can't create or configure views. Do these by hand. For each view below:
1. Click the table name
2. Click the view dropdown (top-left, next to the grid icon)
3. Find the view name (the script already created them as empty views)
4. Click the view, then configure filters/sorts/grouping

### Accounts Table

**View: "Active Clients"**
- Filter: `Status` is `Active Client`
- Sort: `Account Name` A→Z

**View: "Pipeline"**
- Filter: `Status` is `Prospect`
- Group by: `Source`
- Sort: `Account Name` A→Z

---

### Deals Table

**View: "Pipeline Board"** (Kanban)
- This is already a Kanban view
- Group by field: `Stage`
- Stack order should be: Lead → Qualified → Fit Check Scheduled → Fit Check Complete → Proposal Sent → Scope Signed → Deposit Paid → In Progress → Delivered → Closed Won → Closed Lost
- Hide fields on cards: `Lost Reason`, `Notes` (keep cards clean)
- Show on cards: `Deal Name`, `Offer`, `Amount`, `Contact`

**View: "Won This Month"**
- Filter: `Stage` is `Closed Won` AND `Close Date` is within the past month
- Sort: `Close Date` newest first

---

### Sprints Table

**View: "Active Sprints"**
- Filter: `Status` is not `Delivered`
- Sort: `Due Date` oldest first (most urgent at top)

**View: "Sprint Board"** (Kanban)
- Group by field: `Status`
- Stack order: Intake Pending → In Progress → Day 3 Review → Day 10 Review → Revision 1 → Revision 2 → Delivered → Paused
- Show on cards: `Sprint Name`, `Account`, `Due Date`, `QA Status`
- Hide on cards: `Pause Reason`, `Notes`, `Client Satisfaction`

---

### Content Calendar Table

**View: "Publishing Queue"**
- Filter: `Status` is `Scheduled`
- Sort: `Publish Date` oldest first (next to publish at top)
- Hide fields: `Post Copy`, `Notes` (too long for grid view)

**View: "Content Board"** (Kanban)
- Group by field: `Status`
- Stack order: Idea → Draft → Review → Scheduled → Published
- Show on cards: `Post Title`, `Platform`, `Pillar`, `Publish Date`

**View: "By Pillar"**
- Group by: `Pillar`
- Sort within groups: `Publish Date` newest first
- This gives you a view of content balance across pillars

---

### Leads Table

**View: "New Leads"**
- Filter: `Status` is `New`
- Sort: Created time newest first (if available) or `Name` A→Z

**View: "By Trigger"**
- Group by: `Trigger Word`
- Sort within groups: `Status`
- This shows you which CTAs are generating leads

---

### Metrics Dashboard Table

**View: "Weekly View"**
- Filter: `Period Type` is `Weekly`
- Sort: `Period` Z→A (newest week at top)

---

## PHASE 3: Create Automations with Omni (~8 min)

Open the base. Click **"Automations"** in the top-right toolbar (or Extensions → Automations). Then click the Omni AI icon (sparkle icon) and paste each prompt below, one at a time. Wait for each to finish before starting the next.

### Automation 1: New Lead Alert

Paste this into Omni:

```
Create an automation called "New Lead Alert". Trigger: when a record is created in the Leads table. Action: send an email to me with subject "New Lead: {Name}" and body that includes the Name, Email, Trigger Word, URL Submitted, and Notes fields from the new record. Format the body so each field is on its own line with a label.
```

### Automation 2: Sprint Status Change Notification

```
Create an automation called "Sprint Status Update". Trigger: when the Status field is updated in the Sprints table. Action: send an email to me with subject "Sprint Update: {Sprint Name} → {Status}" and body that includes Sprint Name, Account, Status, Due Date, and QA Status. Include a line that says "Next step:" followed by guidance based on the status — if Day 3 Review then "Review concept with client", if Day 10 Review then "Send draft for feedback", if Revision 1 or Revision 2 then "Implement consolidated feedback", if Delivered then "Send proof capture checklist".
```

### Automation 3: Overdue Invoice Alert

```
Create an automation called "Overdue Invoice Alert". Trigger: when the Due Date field in the Invoices table is in the past AND the Status field is not "Paid" and not "Cancelled". Run this check daily. Action: send me an email with subject "Overdue Invoice: {Invoice ID}" and body that includes Invoice ID, Account, Amount, Due Date, and how many days overdue it is.
```

### Automation 4: Feedback Deadline Warning

```
Create an automation called "Feedback Deadline Warning". Trigger: when the Status field in the Sprints table changes to "Day 3 Review" or "Day 10 Review". Action: wait 48 hours, then check if the Status field has changed. If the Status is still "Day 3 Review" or "Day 10 Review" (meaning no feedback was received), send me an email with subject "⏸ Sprint may need pause: {Sprint Name}" and body that says the client hasn't responded within 48 hours, includes the Sprint Name and Account, and reminds me to send the pause notification per the scope agreement.
```

### Automation 5: Deal Won → Create Sprint Task

```
Create an automation called "Deal Won — Sprint Setup". Trigger: when the Stage field in the Deals table changes to "Deposit Paid". Action: send me an email with subject "🚀 Sprint ready to kick off: {Deal Name}" and body that includes Deal Name, Account, Contact, Amount, and a checklist of next steps: 1) Create Sprint record, 2) Send Intake Checklist to client, 3) Set milestone dates, 4) Confirm proof permission level.
```

### Automation 6: Weekly Content Reminder

```
Create an automation called "Weekly Content Reminder". Trigger: every Monday at 8am. Action: find records in the Content Calendar table where Status is "Scheduled" and Publish Date is this week. Send me an email with subject "This week's content" and body that lists each post's Title, Platform, Pillar, and Publish Date.
```

After creating each automation, **turn it on** (the toggle in the top-right of each automation).

---

## PHASE 4: Create Interfaces with Omni (~5 min)

Click **"Interfaces"** in the top nav bar (between Data and Automations). Click the Omni AI icon and paste each prompt below.

### Interface 1: Sprint Command Center

```
Create an interface page called "Sprint Command Center". Include these elements:

1. A summary bar at the top showing: count of records in Sprints where Status is "In Progress", count where Status is "Paused", and count where Status is "Delivered".

2. Below that, a Kanban-style board or grid of the Sprints table filtered to Status is not "Delivered", sorted by Due Date, showing Sprint Name, Account, Status, Due Date, and QA Status.

3. At the bottom, a grid of the Deliverables table linked to the currently selected sprint, showing Deliverable Name, Type, Status, and Version.
```

### Interface 2: Deal Pipeline Dashboard

```
Create an interface page called "Deal Pipeline". Include these elements:

1. A summary bar showing: total count of open deals (Stage is not "Closed Won" and not "Closed Lost"), total Amount of deals where Stage is "Closed Won" this month, and count of Fit Checks scheduled this week.

2. A Kanban board of the Deals table grouped by Stage, showing Deal Name, Offer, Amount, and Contact on each card.

3. A chart showing revenue by month (Amount from deals where Stage is "Closed Won", grouped by Close Date month).
```

### Interface 3: Content Hub

```
Create an interface page called "Content Hub". Include these elements:

1. A summary bar showing: count of posts where Status is "Scheduled", count where Status is "Published" this month, and total Engagement from posts published this month.

2. A calendar view of the Content Calendar table using Publish Date, colored by Pillar.

3. Below the calendar, a grid of posts where Status is "Draft" or "Review", sorted by Publish Date, showing Post Title, Platform, Pillar, Status, and CTA Type.
```

### Interface 4: Leads Tracker

```
Create an interface page called "Leads Tracker". Include these elements:

1. A summary bar showing: count of leads where Status is "New", count where Status is "Qualified", and total leads created this week.

2. A grid of the Leads table filtered to Status is "New" or "Contacted", sorted by newest first, showing Name, Email, Trigger Word, Source Post, and Status.

3. A chart showing leads by Trigger Word (count of records grouped by Trigger Word field) as a bar chart.
```

### Interface 5: Weekly Metrics

```
Create an interface page called "Weekly Metrics". Include these elements:

1. Show the most recent record from the Metrics Dashboard table where Period Type is "Weekly", displaying New Leads, Fit Checks Booked, Sprints Sold, Revenue, Content Published, and Tripwire Sales as large number cards.

2. Below that, a line chart of Revenue over time from the Metrics Dashboard table (Period on x-axis, Revenue on y-axis), filtered to the last 12 weeks.

3. A grid of the Metrics Dashboard table sorted by Period newest first, showing all number fields.
```

---

## PHASE 5: Verify (~2 min)

Open each section and confirm:

- [ ] **Tables:** Click through all 12. Each should have fields with colored select options.
- [ ] **Relationships:** Open a record in Accounts. You should see linked fields for Contacts, Deals, and Sprints. Open Deals — you should see Account, Contact, Sprint links.
- [ ] **Views:** Check Deals → "Pipeline Board" shows a kanban. Check Sprints → "Active Sprints" is filtered. Check Content Calendar → "Publishing Queue" is filtered.
- [ ] **Seed data:** Content Calendar should have 5 records (the cornerstone posts). Templates should have 9 records.
- [ ] **Automations:** Go to Automations. You should see 6 automations, all toggled ON. Click "Run test" on "New Lead Alert" to verify email delivery.
- [ ] **Interfaces:** Click Interfaces in the top nav. You should see 5 interface pages. Click each one — the elements should be populated (some may be empty until you have data, but the layout should be correct).

---

## PHASE 6: First Real Data

Once everything checks out, create your first real records to test the system end-to-end:

1. **Create a test lead** in the Leads table: Name = "Test Lead", Trigger Word = "SPRINT", Status = "New". Verify the New Lead Alert automation fires and you get an email.

2. **Create a test deal** in the Deals table: Deal Name = "Test - Creative Sprint", Offer = "Creative Sprint ($3500-$8000)", Stage = "Lead", Amount = $4000. Drag it through the Pipeline Board kanban to verify stages work.

3. **Move a cornerstone post** in Content Calendar: Set one of the 5 seeded posts to Status = "Scheduled" and set a Publish Date to this week. Verify it appears in the Publishing Queue view.

Then delete the test records and you're live.

---

## TROUBLESHOOTING

**Script fails with "Set AIRTABLE_API_KEY":**
You haven't exported the env var. Run `export AIRTABLE_API_KEY="patXXX..."` first.

**Script fails with HTTP 403:**
Your PAT doesn't have the right scopes. Go to airtable.com/create/tokens, edit your token, and add: `data.records:read`, `data.records:write`, `schema.bases:read`, `schema.bases:write`.

**Script fails with HTTP 422 (validation error):**
Usually means a field type or option format is wrong. Check the error message — it'll tell you which field. If you hit this, delete the partially-created base in Airtable and re-run.

**Omni doesn't understand the prompt:**
Try breaking it into two parts. First ask it to create the automation/interface with just the trigger, then edit the actions. Omni works best with one instruction at a time.

**View filters aren't available:**
The script creates views as empty containers. You have to add the filters manually — that's what Phase 2 covers.
