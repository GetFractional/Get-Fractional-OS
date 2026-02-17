# Client Portal Spec — Get Fractional OS

> Built with Softr, connected to Airtable. Professional UX, custom domain, client login.

---

## 1. Why Softr

| Option | Cost | Build Time | UX Quality | Maintenance |
|---|---|---|---|---|
| **Softr (chosen)** | $59/mo Business plan | 1-2 days | Professional, custom domain, branded | Low — drag and drop |
| Airtable Interfaces | Included | 0.5 days | Clunky, no custom domain, no login | Low |
| Custom (Next.js) | $0 hosting | 5-10 days | Full control | High — code maintenance |

Softr wins on the cost-to-quality ratio for MVP. Custom portal is the long-term play if complexity demands it.

---

## 2. Softr Setup

### Account Configuration

| Setting | Value |
|---|---|
| Plan | Business ($59/mo) |
| Custom domain | `portal.getfractional.com` (or similar) |
| Data source | Airtable — "Get Fractional OS (Core)" base |
| Authentication | Email + password login (Softr built-in) |
| User groups | Client, Admin |

### User Group Permissions

| Group | Can See | Cannot See |
|---|---|---|
| **Client** | Their own Account's data only (filtered by email/Account link) | Other clients, internal notes, margin data, System Logs, Engagement Inbox |
| **Admin (Matt)** | Everything | — |

### Data Filtering

Softr supports **logged-in user filtering**: each client's email is matched to their Account record in Airtable. All data displayed is automatically filtered to show only records linked to that Account.

---

## 3. Portal Pages

### Page 1: Dashboard (Home)

```
┌─────────────────────────────────────────────────────────────┐
│  Welcome, [Client Name]                                     │
│  [Account Name]                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ACTIVE SPRINT                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Creative Sprint — Started Mar 1                     │   │
│  │  Stage: ████████░░ Production                        │   │
│  │  Due: Mar 15                                         │   │
│  │  Next milestone: Day 10 Draft Review (Mar 11)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ITEMS NEEDING YOUR FEEDBACK                                │
│  ─ Day 3 Concept Review: 3 angle options to review          │
│  ─ Brand Brief: Please confirm ICP details                  │
│                                                             │
│  RECENT DELIVERABLES                                        │
│  ─ Brand Brief v1.0 [Download]                              │
│  ─ Concept Deck [Available after review]                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Softr components:**
- Heading block: "Welcome, {User Name}"
- List block: Sprints table (filtered by Account, Status != Complete)
- List block: Sprints where Approval Needed = true (client feedback items)
- List block: Campaign Kits (filtered by Sprint linked to Account)

### Page 2: Sprint Timeline

```
┌─────────────────────────────────────────────────────────────┐
│  SPRINT TIMELINE                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Day 0 — Kickoff + Intake (Mar 1)                        │
│     Intake form submitted. Research begins.                 │
│                                                             │
│  ✅ Day 3 — Concept Review (Mar 4)                           │
│     3 angle directions presented. Client selected angle B.  │
│                                                             │
│  ⏳ Day 10 — Draft Review (Mar 11)                           │
│     Full creative kit draft for review.                     │
│     Your feedback due within 48 hours.                      │
│                                                             │
│  ⏳ Day 14 — Final Delivery (Mar 15)                         │
│     Final kit + testing plan delivered.                     │
│                                                             │
│  REVISION ROUNDS REMAINING: 2 of 2                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Softr components:**
- List block: Custom "Timeline Events" (could be Sprint stages with dates)
- Conditional display: show checkmarks for completed stages, clock for upcoming
- Text block: Revision rounds remaining (from Sprint record)

### Page 3: Deliverables

```
┌─────────────────────────────────────────────────────────────┐
│  DELIVERABLES                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────┬──────┬─────────┐  │
│  │ Deliverable                         │Status│ Action  │  │
│  ├─────────────────────────────────────┼──────┼─────────┤  │
│  │ Brand / ICP Brief                   │ ✅   │Download │  │
│  │ Objection Map                       │ ✅   │Download │  │
│  │ Angles + Hooks (Concept Deck)       │ 🔄   │ Review  │  │
│  │ Ad Concepts (10-20 variants)        │ ⏳   │ —       │  │
│  │ Landing Page Copy Kit               │ ⏳   │ —       │  │
│  │ Testing Plan + Naming Conventions   │ ⏳   │ —       │  │
│  └─────────────────────────────────────┴──────┴─────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Softr components:**
- Table block: Campaign Kit deliverables (linked assets with status)
- Download buttons: link to Asset Folder or Airtable attachments
- Status badges: visual indicators for complete/in-progress/pending

### Page 4: Messages / Feedback

```
┌─────────────────────────────────────────────────────────────┐
│  FEEDBACK                                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Submit your consolidated feedback for the current review   │
│  milestone. Remember: one consolidated set per round.       │
│                                                             │
│  Current milestone: Day 10 Draft Review                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [Text area for feedback]                           │   │
│  │                                                     │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Attach Files]  [Submit Feedback]                          │
│                                                             │
│  ─────────────────────────────────────────                  │
│  PREVIOUS FEEDBACK                                          │
│  ─ Day 3 (Mar 4): "Love angle B, adjust tone to be..."     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Softr components:**
- Form block: connected to a "Client Feedback" field on the Sprint record (or a linked Feedback table)
- File upload: for attachments
- List block: previous feedback entries
- Text block: revision policy reminder

---

## 4. Airtable Support for Portal

### Additional Fields Needed

**Sprints table — add:**

| Field Name | Type | Notes |
|---|---|---|
| Client Feedback | Long text | Where client submits feedback via portal form |
| Portal Timeline Notes | Long text | Human-readable timeline text shown in portal |
| Client-Visible Notes | Long text | Only notes meant for client (not Internal Notes) |

**Campaign Kits table — add:**

| Field Name | Type | Notes |
|---|---|---|
| Client Downloadable | Checkbox | Show this asset in the portal |
| Download Link | URL | Direct link to downloadable file |
| Client Status | Single select | Options: `Pending`, `Ready for Review`, `Final` |

### Data Visibility Rules

| Table | Portal Visible | Filtered By |
|---|---|---|
| Sprints | Yes | Account = logged-in user's Account |
| Campaign Kits | Yes (Client Downloadable = true only) | Sprint → Account = user's Account |
| Accounts | Yes (name + basic info only) | User's own Account |
| Content Pipeline | No | — |
| Engagement Inbox | No | — |
| Leads | No | — |
| System Logs | No | — |
| AI Video Projects | No (outputs delivered via Campaign Kit) | — |

---

## 5. Branding

| Element | Value |
|---|---|
| Logo | Get Fractional logo (upload to Softr) |
| Primary color | Match Get Fractional brand |
| Font | Clean sans-serif (Inter, system font) |
| Favicon | Get Fractional icon |
| Login page message | "Welcome to your Get Fractional Sprint Dashboard" |
| Footer | "Powered by Get Fractional — Less chaos, more shipped." |

---

## 6. Build Checklist

- [ ] Create Softr account (Business plan)
- [ ] Connect Airtable base as data source
- [ ] Set up custom domain (portal.getfractional.com)
- [ ] Create user group: Client
- [ ] Create user group: Admin
- [ ] Build Dashboard page with sprint status + feedback items
- [ ] Build Timeline page with milestone display
- [ ] Build Deliverables page with download links
- [ ] Build Feedback page with form submission
- [ ] Configure user filtering (email → Account)
- [ ] Add branding (logo, colors, fonts)
- [ ] Test with a sample client account
- [ ] Set up invite flow (email invitation to client)

---

## 7. Future: Custom Portal Migration

If Softr becomes limiting (complex logic, multi-tenant, advanced features), migrate to:

**Stack:** Next.js + Tailwind CSS + Airtable API + Vercel hosting

**When to migrate:**
- Need custom logic (e.g., real-time notifications, complex permissions)
- Need advanced interactivity (commenting, threaded discussions)
- 10+ active clients and Softr's per-user pricing becomes expensive
- Need white-label capability for Agency OS Install clients

**Migration path:** Softr pages map 1:1 to Next.js routes. Airtable remains the backend. The data model doesn't change — only the presentation layer.
