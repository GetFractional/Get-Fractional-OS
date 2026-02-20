# Softr Setup Guide — Get Fractional OS

> Step-by-step instructions for building the client portal with Softr.
> Softr connects directly to Airtable — no backend code needed.
> This is a Day 7-14 build. Not urgent for Day 0-2.

---

## OVERVIEW

The Softr client portal gives each client a login where they can:
1. See their sprint status and milestones
2. Access deliverables
3. Submit feedback (consolidated per revision round)
4. View their scope agreement details

This replaces email/Slack back-and-forth with a single source of truth.

---

## STEP 1: Create Softr Account

1. Sign up at [softr.io](https://www.softr.io)
2. Free tier works for up to 5 users. Upgrade to Basic ($49/mo) for custom domain and more users.
3. Choose "Start from scratch" (not a template)

---

## STEP 2: Connect Airtable

1. Go to **Settings → Data Sources → Airtable**
2. Paste your Airtable API token (from Airtable setup guide, Step 5)
3. Select the "Get Fractional OS" base
4. Softr will import your table structure

---

## STEP 3: Build Pages

### Page 1: Dashboard (Home)

**Data source:** Sprints table (filtered by logged-in user's Account)

**Layout:** List/card view showing:
- Sprint Name
- Status (with color-coded badge)
- Start Date
- Due Date
- Next milestone

**Access:** Logged-in clients only

**Softr blocks to use:**
- **List with details** block → connected to Sprints table
- **Filter:** Account = logged-in user's linked Account
- **Conditional visibility:** Show "No active sprints" message if no records

---

### Page 2: Sprint Detail

**Data source:** Sprints table (single record view) + Deliverables table

**Layout:**
- Top section: Sprint overview (status, dates, milestones)
- Middle section: Deliverables list with status badges
- Bottom section: Feedback submission form

**Softr blocks to use:**
- **Details** block → Sprint record
- **List** block → Deliverables filtered by this Sprint
- **Form** block → Submit feedback (writes to a Feedback field or linked table)

---

### Page 3: Deliverables

**Data source:** Deliverables table (filtered by client's Sprint)

**Layout:** Table or card view showing:
- Deliverable Name
- Type
- Status
- Version
- File Link (clickable)

**Softr blocks to use:**
- **Table** block → connected to Deliverables table
- **Filter:** Sprint → Account = logged-in user's Account
- File Link column renders as clickable link

---

### Page 4: Scope & Terms

**Data source:** Sprints table (scope-related fields) or static content

**Layout:** Static page showing:
- Scope agreement summary (what's included, what's not)
- Revision policy summary
- Key dates
- Contact information

**Softr blocks to use:**
- **Rich text** block for static content
- **Details** block for dynamic Sprint-specific info

---

## STEP 4: Configure User Authentication

1. Go to **Settings → Users**
2. Choose **Airtable-based users**:
   - User table: Contacts
   - Email field: Email
   - User group field: (create a "Portal Access" single select in Contacts with options: Client, Admin)
3. Set up login page:
   - Magic link login (no passwords to manage)
   - Or email + password if preferred

**Access rules:**
- Dashboard: Client, Admin
- Sprint Detail: Client (own sprint only), Admin (all)
- Deliverables: Client (own sprint only), Admin (all)
- Scope & Terms: Client, Admin

---

## STEP 5: Customize Branding

1. Go to **Settings → Design**
2. Set colors:
   - Primary: (Matt's brand color)
   - Background: White or light gray
   - Text: Dark gray/black
3. Upload logo
4. Set fonts to match brand guidelines
5. Custom domain: Add `portal.getfractional.com` (or similar) in Settings → Domain

---

## STEP 6: Build the Feedback Flow

This is the key operational feature of the portal.

**Option A: Simple (Form block)**
1. Add a Form block to the Sprint Detail page
2. Fields: Long text (feedback), File upload (marked-up PDFs)
3. Form submission creates a record in a new "Feedback" Airtable table
4. n8n workflow triggers on new Feedback record → notifies Matt

**Option B: Structured (Recommended)**
1. Create a "Feedback Rounds" table in Airtable:

| Field | Type |
|---|---|
| Sprint | Link to Sprints |
| Round | Single select (Round 1, Round 2, Additional) |
| Feedback Text | Long text |
| Attachments | Attachment |
| Submitted Date | Date |
| Status | Single select (Submitted, In Review, Implemented) |

2. Softr form writes to this table
3. Client can see their previous feedback submissions and status
4. Matt sees all feedback in Airtable, updates status as he implements

---

## STEP 7: Launch Checklist

Before giving a client access:

- [ ] Test login flow (magic link or password)
- [ ] Verify data filtering (client only sees their own data)
- [ ] Test feedback form submission
- [ ] Verify deliverable links are accessible
- [ ] Check mobile responsiveness
- [ ] Confirm email notifications work (new feedback → Matt notified)
- [ ] Create a welcome email template with portal login instructions

---

## DEPLOYMENT TIMELINE

| Phase | What to Build | When |
|---|---|---|
| Phase 1 | Dashboard + Sprint Detail (read-only) | Day 7-10 |
| Phase 2 | Feedback form + Deliverables page | Day 10-14 |
| Phase 3 | Branding, custom domain, polish | Week 3 |
| Phase 4 | Onboard first client | When first Sprint begins |

The portal is a "nice to have" for Sprint #1. Email delivery works fine initially. Build the portal while the first sprint is running, then onboard the client to it mid-sprint or for Sprint #2.
