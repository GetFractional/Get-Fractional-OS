# Lead Magnet: URL → ICP Snapshot

> **Format:** 1-page PDF (delivered via email or DM)
> **Trigger:** Comment "SNAPSHOT" on Tuesday post with URL
> **Funnel position:** Awareness → Email list capture
> **Delivery:** Manual for first 10, then templatize for n8n automation
> **Goal:** Demonstrate the "URL to Campaign" process in miniature

---

## Template: ICP Snapshot for {{Brand Name}}

### Your URL: {{URL}}

---

### 1. WHO YOU'RE ACTUALLY SELLING TO

**Primary ICP (based on your page):**

| Attribute | What Your Page Says |
|---|---|
| **Who** | {{ICP description — demographic + psychographic}} |
| **Pain they feel** | {{Primary pain point implied by benefit copy}} |
| **Outcome they want** | {{Desired state implied by headlines/CTAs}} |
| **Objection they carry** | {{Top objection implied by FAQ/proof/guarantee}} |

**How I identified this:** {{1-2 sentences explaining what page elements revealed this — e.g., "Your hero headline targets [outcome], your testimonials emphasize [proof type], and your FAQ addresses [objection]. This tells me your buyer is [description]."}}

---

### 2. YOUR TOP 3 OBJECTIONS (HIDDEN IN YOUR PAGE)

These are the reasons people visit your page and don't buy. Your own copy reveals them:

1. **{{Objection 1}}** — Found in: {{where on the page — e.g., FAQ, guarantee section, testimonial}}
2. **{{Objection 2}}** — Found in: {{where on the page}}
3. **{{Objection 3}}** — Found in: {{where on the page}}

**Why this matters:** Your ad hooks should address these objections directly. Most brands bury objection handling on the product page. The best ads lead with it.

---

### 3. YOUR UNTAPPED ANGLE

**The angle your page supports but your headline ignores:**

{{1 paragraph describing an angle buried in testimonials, ingredients, comparison, or secondary copy that isn't reflected in the primary headline/hero section}}

**Hook example using this angle:**
> "{{A sample hook using this untapped angle}}"

---

### WHAT THIS TELLS YOU

This snapshot covers ~20% of what a full Creative Sprint produces. The full sprint turns this into:
- 5 ad angles (not just 1)
- 15–25 hooks across all angles
- 10–20 ad concepts with copy and creative direction
- Landing page copy kit
- Testing plan with naming conventions

**Want the full version?** Reply "SPRINT" to this message or book a Fit Check: {{Fit Check link}}

---

## PRODUCTION NOTES

**Time to produce (manual):** 15–20 minutes per snapshot
**Tools needed:** Browser, the URL, this template
**Quality bar:** Must include at least 1 specific, non-obvious insight. If the snapshot only states obvious things, it won't demonstrate value.
**Automation path:** Once Matt has done 10 manually and the pattern is clear, build an n8n workflow:
1. Trigger: Airtable record created in Leads table with URL field populated
2. Action: Scrape URL → extract key elements → fill template → generate PDF → send via email
