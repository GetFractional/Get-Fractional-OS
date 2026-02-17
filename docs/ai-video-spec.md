# AI Video Integration Spec — Get Fractional OS

> Tracking prompts, settings, reference assets, and outputs from AI image/video tools.
> UI-first workflow now, API integration later.

---

## 1. Tools Covered

### Nano Banana Pro (Image Generation)

| Capability | Detail |
|---|---|
| Reference images | Up to 14 |
| Prompt | Text input |
| Aspect ratio | Configurable |
| Resolution | 1K, 2K, 4K |
| Variants per run | 1–4 |
| Drawing on images | Supported |
| Primary use | Ad creative images, product shots, lifestyle imagery |

### Kling 3.0 (Video Generation)

| Capability | Detail |
|---|---|
| Start frame | Upload supported |
| End frame | Upload supported |
| Multi-shot | Toggle on/off |
| Prompt | Text input |
| Audio | Toggle on/off |
| Reference elements | Up to 3 (for product placement) |
| Duration | 5–15 seconds |
| Aspect ratio | Configurable |
| Resolution | 720p, 1080p |
| Primary use | Product videos, ad video creative, social reels |

### Veo 3.1 (Video Generation)

| Capability | Detail |
|---|---|
| Duration | 4s, 6s, 8s |
| Aspect ratio | Configurable |
| Resolution | 720p, 1080p |
| Primary use | Short social clips, ad intros, b-roll |

---

## 2. Airtable Table: AI Video Projects

> New table added to "Get Fractional OS (Core)" base.

| Field Name | Type | Notes |
|---|---|---|
| Project Name | Single line text | **Primary field** — format: `[Account] - [Tool] - [Brief Desc] - [Date]` |
| Tool | Single select | Options: `Nano Banana Pro`, `Kling 3.0`, `Veo 3.1`, `Other` |
| Type | Single select | Options: `Image`, `Video` |
| Account | Link to Accounts | Which client this is for |
| Sprint | Link to Sprints | Which sprint this supports |
| Campaign Kit | Link to Campaign Kits | Which kit this belongs to |
| **Prompt** | Long text | The exact prompt used |
| **Negative Prompt** | Long text | If applicable |
| **Settings JSON** | Long text | Structured settings (see below) |
| Reference Images | Attachment | Up to 14 (Nano Banana Pro) or 3 (Kling 3.0) |
| Start Frame | Attachment | For Kling 3.0 video |
| End Frame | Attachment | For Kling 3.0 video |
| Output Files | Attachment | Generated images/videos |
| Output URL | URL | If hosted externally (CDN, Google Drive) |
| Resolution | Single select | Options: `720p`, `1080p`, `1K`, `2K`, `4K` |
| Aspect Ratio | Single select | Options: `1:1`, `4:5`, `9:16`, `16:9`, `Custom` |
| Duration | Single select | Options: `N/A`, `4s`, `5s`, `6s`, `8s`, `10s`, `15s` |
| Variants Generated | Number | 1–4 |
| Multi-Shot | Checkbox | Kling 3.0 only |
| Audio | Checkbox | Kling 3.0 only |
| Status | Single select | Options: `Queued`, `Generating`, `Review`, `Approved`, `Rejected`, `Used` |
| Quality Rating | Single select | Options: `Poor`, `Acceptable`, `Good`, `Excellent` |
| Notes | Long text | What worked, what didn't — builds prompt library knowledge |
| Created | Created time | Auto |

### Settings JSON Format

Store tool-specific settings in a structured format for reproducibility:

**Nano Banana Pro:**
```json
{
  "tool": "nano_banana_pro",
  "resolution": "2K",
  "aspect_ratio": "1:1",
  "variants": 4,
  "reference_count": 3,
  "drawing_used": false,
  "style_notes": "Lifestyle shot, bright natural lighting"
}
```

**Kling 3.0:**
```json
{
  "tool": "kling_3.0",
  "resolution": "1080p",
  "aspect_ratio": "9:16",
  "duration": "10s",
  "multi_shot": true,
  "audio": false,
  "reference_elements": 2,
  "start_frame": true,
  "end_frame": false
}
```

**Veo 3.1:**
```json
{
  "tool": "veo_3.1",
  "resolution": "1080p",
  "aspect_ratio": "9:16",
  "duration": "6s"
}
```

---

## 3. Views

| View Name | Type | Filter/Sort |
|---|---|---|
| All Projects | Grid | Default |
| By Tool | Kanban | Grouped by Tool |
| Needs Review | Grid | Status = "Review" |
| Approved Assets | Gallery | Status = "Approved" or "Used", show Output Files |
| Prompt Library | Grid | Status = "Approved" or "Used", sorted by Quality Rating desc — for reusing winning prompts |
| By Account | Grid | Grouped by Account |
| By Sprint | Grid | Filtered by selected Sprint |

---

## 4. Workflow: UI-First (Current)

```
[1. Matt opens AI video tool (Nano Banana Pro / Kling / Veo)]
        │
[2. Before generating: create AI Video Projects record in Airtable]
     - Set: Tool, Account, Sprint, Prompt, Settings, Reference Images
     - Status = "Generating"
        │
[3. Generate in the tool's UI]
        │
[4. Download outputs → attach to Airtable record as Output Files]
     - Set: Variants Generated, Resolution, etc.
     - Status = "Review"
        │
[5. Review output quality]
     ├── Good → Status = "Approved", Quality Rating, Notes on what worked
     └── Bad → Status = "Rejected", Notes on what to change
        │
[6. Use in sprint deliverables]
     - Link to Campaign Kit
     - Status = "Used"
     - Upload to hosted location → set Output URL for auto-publish
```

### Why UI-First

- These tools are evolving fast — APIs may change or have waitlists
- UI gives Matt full creative control (drawing, tweaking, multi-shot)
- The value of Airtable tracking is the **prompt library** — knowing what prompts + settings produce great results for which client types
- When API access is stable and worth automating, the Airtable records already contain everything needed to make API calls programmatically

---

## 5. Future: API Integration (When Available)

When Nano Banana Pro / Kling / Veo offer stable APIs:

### n8n Workflow (Future)

```
[Trigger: AI Video Projects record with Status = "Queued"]
        │
[Read Settings JSON + Prompt + Reference Images]
        │
[Call tool API with settings]
        │
[Receive output → attach to Airtable record]
        │
[Set Status = "Review"]
        │
[Log to System Logs]
```

### Environment Variables (Future)

| Variable | Description |
|---|---|
| `NANO_BANANA_API_KEY` | When API available |
| `KLING_API_KEY` | When API available |
| `VEO_API_KEY` | When API available |

---

## 6. Prompt Library Best Practices

The AI Video Projects table doubles as a **prompt library**. To maximize value:

1. **Always rate outputs** — Quality Rating field builds a searchable library of what works
2. **Write notes on winning prompts** — "This prompt style works well for [product type] because [reason]"
3. **Tag by account type** — helps find relevant prompts when working with similar clients
4. **Clone winning records** — when starting a new project for a similar client, duplicate an "Excellent" rated record and modify
5. **Track reference image patterns** — note which types of reference images (lifestyle, product-only, in-context) produce best results per tool

### Prompt Template Examples (Starter Library)

**Product Hero Shot (Nano Banana Pro):**
```
[Product name] on a clean white surface, soft studio lighting,
product photography style, sharp focus, high detail, [brand color]
accent lighting, minimalist composition, 4K resolution
```

**Social Ad Video (Kling 3.0):**
```
Close-up of [product] being used by [demographic], natural hand
movements, warm lifestyle lighting, slight camera movement,
shallow depth of field, product clearly visible throughout
```

**Short Hook Clip (Veo 3.1):**
```
Dynamic quick cut of [product/result], attention-grabbing motion,
bold colors, 2-second focus on key benefit, social media vertical format
```
