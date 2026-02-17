# Social Automation Spec — Get Fractional OS

> Engagement capture + auto-publishing via official platform APIs only.
> No scraping, no unofficial tools, no ToS violations.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOCIAL PLATFORMS                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐                     │
│  │ LinkedIn  │  │ Facebook │  │ Instagram │                     │
│  │ Co. Page  │  │ Page     │  │ Business  │                     │
│  └─────┬────┘  └────┬─────┘  └─────┬─────┘                     │
│        │             │              │                            │
│    Marketing     Graph API      Graph API                        │
│    API v2        v21+           v21+                              │
└────────┼─────────────┼──────────────┼───────────────────────────┘
         │             │              │
         ▼             ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       n8n WORKFLOWS                              │
│                                                                  │
│  Workflow E: ENGAGEMENT CAPTURE (inbound)                        │
│  ┌─────────────┐  ┌──────────┐  ┌────────────┐                 │
│  │ Webhooks /  │→│ Normalize │→│ Airtable   │→ System Logs     │
│  │ Poll APIs   │  │ + Dedup  │  │ Engagement │                  │
│  └─────────────┘  └──────────┘  │ Inbox      │                  │
│                                  └────────────┘                  │
│                                                                  │
│  Workflow F: AUTO-PUBLISH (outbound)                             │
│  ┌──────────────┐  ┌──────────┐  ┌─────────┐                   │
│  │ Airtable     │→│ Format   │→│ Publish  │→ Capture Post URL  │
│  │ Status =     │  │ per      │  │ via API  │→ System Logs      │
│  │ "Approved"   │  │ Platform │  └─────────┘                    │
│  └──────────────┘  └──────────┘                                  │
│                                                                  │
│  Workflow G: METRICS CAPTURE (24h post-publish)                  │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────┐              │
│  │ Schedule:    │→│ Fetch    │→│ Write to     │→ System Logs   │
│  │ 24h after    │  │ Metrics  │  │ Content      │               │
│  │ publish      │  │ from API │  │ Pipeline     │               │
│  └──────────────┘  └──────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. API Credentials Required

### Environment Variables

| Variable | Description | Used By |
|---|---|---|
| `META_APP_ID` | Meta (Facebook) App ID | Workflows E, F, G |
| `META_APP_SECRET` | Meta App Secret | Workflows E, F, G |
| `META_PAGE_ACCESS_TOKEN` | Long-lived Page Access Token (FB) | Workflows E, F, G |
| `META_IG_USER_ID` | Instagram Business Account ID | Workflows E, F, G |
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth2 Client ID | Workflows E, F |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth2 Client Secret | Workflows E, F |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn Access Token (refresh periodically) | Workflows E, F |
| `LINKEDIN_ORG_ID` | LinkedIn Company Page Organization ID | Workflows E, F |
| `META_WEBHOOK_VERIFY_TOKEN` | Token for Meta webhook verification | Workflow E |

### Setup Prerequisites

| Platform | Requirements |
|---|---|
| **Facebook** | Facebook Page created. Meta App created (developers.facebook.com). Page Access Token generated with `pages_read_engagement`, `pages_manage_posts`, `pages_read_user_content` permissions. Webhook subscriptions for Page feed. |
| **Instagram** | IG Business Account linked to Facebook Page. Same Meta App. Permissions: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`. |
| **LinkedIn** | LinkedIn Company Page. App created (developer.linkedin.com). Products: "Share on LinkedIn", "Marketing Developer Platform". Scopes: `r_organization_social`, `w_organization_social`, `rw_organization_admin`. |

---

## 3. Workflow E: Social Engagement Capture

### Purpose
Automatically capture comments on posts across Facebook, Instagram, and LinkedIn. Create Engagement Inbox records in Airtable. No automated replies.

### Trigger Options by Platform

| Platform | Method | Latency |
|---|---|---|
| **Facebook** | Meta Webhooks (real-time) — subscribe to Page `feed` | Real-time (seconds) |
| **Instagram** | Meta Webhooks — subscribe to `comments` on IG media | Real-time (seconds) |
| **LinkedIn** | Polling — GET /organizationalEntityShareStatistics + comments | Every 15 min |

### Steps

```
[FACEBOOK + INSTAGRAM PATH]

[1. Webhook Receiver]
  ├── n8n Webhook node receives Meta webhook POST
  ├── Verify: X-Hub-Signature-256 header matches app secret
  └── Parse: extract comment_id, post_id, from.name, from.id, message, created_time

[2. Fetch Full Comment Details]
  ├── GET /{comment_id}?fields=from,message,created_time,parent
  ├── Determine: is this a top-level comment or reply?
  └── If reply to Matt's comment: flag as potential lead signal

[3. Normalize]
  ├── platform = "Facebook" or "Instagram"
  ├── type = "Comment"
  ├── author_handle = from.name (or from.username for IG)
  ├── content = message
  ├── post_id = post_id
  └── idempotency_key = SHA256("engagement_capture:" + platform + ":" + post_id + ":" + comment_id)

[4. Dedup Check]
  ├── Search Airtable Engagement Inbox by idempotency key
  └── If exists → skip, log Info "Duplicate engagement skipped"

[5. Match to Content Pipeline]
  ├── Search Content Pipeline by Post URL containing post_id
  └── If found → link record. If not → leave Linked Post empty.

[6. Create Engagement Inbox Record]
  ├── Source: platform
  ├── Type: "Comment"
  ├── Author Handle: author_handle
  ├── Author Name: from.name
  ├── Content: message
  ├── Linked Post: matched Content Pipeline record
  ├── Status: "New"
  └── Lead Created: false

[7. Keyword Detection (optional — simple CTA matching)]
  ├── Check if message contains CTA keywords: SPRINT, TEARDOWN, SNAPSHOT, HOOKS, etc.
  ├── If match: set Status = "Queued" (higher priority for Matt to reply)
  └── Add Note: "CTA keyword detected: {keyword}"

[8. Log Success]
  └── System Logs: Info, "Engagement captured: {author} on {platform}"

---

[LINKEDIN PATH]

[1. Scheduled Trigger: Every 15 minutes]

[2. Fetch Recent Company Page Posts]
  ├── GET /organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:{LINKEDIN_ORG_ID}
  └── Get post URNs from last 24 hours

[3. For Each Post: Fetch Comments]
  ├── GET /socialActions/{post_urn}/comments
  └── Extract: comment text, author, timestamp, comment URN

[4. Normalize + Dedup + Create Records]
  ├── Same flow as Facebook/IG steps 3-8
  └── platform = "LinkedIn"

---

[ERROR HANDLING — All Paths]
  ├── Retry: 3x exponential backoff
  ├── Dead-letter: System Logs severity=Error
  └── On webhook verification failure: Log Critical, alert immediately
```

### What This Does NOT Do (Safety)

- Does NOT reply to any comments — Matt replies manually
- Does NOT send DMs — all outreach is manual
- Does NOT scrape — uses only official webhooks and APIs
- Does NOT access personal profile comments (LinkedIn limitation) — only Company Page
- Does NOT store access tokens in workflow JSON — credentials managed in n8n credential store

### LinkedIn Personal Profile Fallback

LinkedIn's API doesn't support reading comments on personal profile posts. For personal profile engagement:

**Option A (Recommended):** Use Buffer or Hootsuite with their LinkedIn integration. These tools aggregate engagement via official API. Set up a webhook from the management tool to n8n.

**Option B:** Continue manual capture for LinkedIn personal profile comments only. Streamlined interface: a quick-entry form in the Daily Cockpit for pasting comment details.

---

## 4. Workflow F: Auto-Publish

### Purpose
When Matt approves content in Airtable (Status = "Approved"), automatically publish to the designated platform via official API. Capture the Post URL back into Airtable.

### Safety Gate

```
Content MUST pass through this sequence:
  Draft → Needs QA → [QA checkboxes checked] → Needs Approval → [Matt approves] → Approved

"Approved" status is ONLY set by Matt manually or via approval button.
The auto-publish workflow ONLY triggers on Status = "Approved".
There is no path from Draft to Published without Matt's explicit approval.
```

### Steps

```
[1. Trigger: Content Pipeline Status → "Approved"]
  ├── Read full record: Platform, Draft, CTA Text, Post Title, Publish Date
  ├── Check: Publish Date = today or past (don't publish future-dated content)
  └── If Publish Date is future → set Status = "Scheduled", stop workflow

[2. Route by Platform]
  ├── Facebook → step 3a
  ├── Instagram → step 3b
  ├── LinkedIn → step 3c
  └── "All" → run 3a + 3b + 3c sequentially

---

[3a. FACEBOOK PUBLISH]
  ├── POST /{page-id}/feed
  │   Body: { message: draft_text, link: (if CTA includes URL) }
  ├── Capture response: post_id
  ├── Construct Post URL: https://facebook.com/{page-id}/posts/{post_id}
  └── On error: retry 3x, then dead-letter

[3b. INSTAGRAM PUBLISH]
  ├── Step 1: Create media container
  │   POST /{ig-user-id}/media
  │   Body: { image_url: hosted_image_url, caption: draft_text }
  │   (Image must be hosted on a public URL — use Airtable attachment URL or CDN)
  ├── Step 2: Publish container
  │   POST /{ig-user-id}/media_publish
  │   Body: { creation_id: container_id }
  ├── Capture response: media_id
  ├── Construct Post URL: https://instagram.com/p/{shortcode}
  └── On error: retry 3x, then dead-letter
  NOTE: If no image attached → skip IG publish, log Warning

[3c. LINKEDIN PUBLISH]
  ├── POST /ugcPosts
  │   Body: {
  │     author: "urn:li:organization:{LINKEDIN_ORG_ID}",
  │     lifecycleState: "PUBLISHED",
  │     specificContent: {
  │       shareContent: {
  │         shareCommentary: { text: draft_text },
  │         shareMediaCategory: "NONE" (or "ARTICLE" if link included)
  │       }
  │     },
  │     visibility: { "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" }
  │   }
  ├── Capture response: post URN
  ├── Construct Post URL from URN
  └── On error: retry 3x, then dead-letter

---

[4. Update Airtable Record]
  ├── Set Status = "Published"
  ├── Set Post URL = captured URL
  ├── Set Publish Date = today (if not already set)
  └── Set Platform Post IDs (store platform-specific IDs for metrics capture later)

[5. Schedule Metrics Capture]
  ├── Create a delayed trigger: 24 hours from now → Workflow G
  └── Pass: content_record_id, platform, post_id

[6. Log Success]
  └── System Logs: Info, "Published: {Post Title} to {Platform} at {Post URL}"

---

[ERROR HANDLING]
  ├── If Facebook API rejects: check token expiry, log Error, alert
  ├── If Instagram rejects (no image): log Warning, skip IG, continue other platforms
  ├── If LinkedIn rejects: check token expiry, log Error, alert
  ├── If ALL platforms fail: set Status back to "Approved" (so Matt can retry or investigate)
  └── Dead-letter all failures to System Logs
```

### Platform-Specific Formatting

| Platform | Max Length | Formatting | Hashtags | Link Preview |
|---|---|---|---|---|
| Facebook | ~63,206 chars | Plain text, line breaks preserved | 1-3 max | Auto-generated from URL |
| Instagram | 2,200 chars | No clickable links in caption | Up to 30 | N/A (link in bio) |
| LinkedIn | 3,000 chars | Supports bold, italic, lists | 3-5 max | Auto-generated from URL |

The workflow includes a **formatting transform** step per platform:
- Truncate to platform limits
- Adjust hashtag count
- For Instagram: move any links to "Link in bio" callout
- For LinkedIn: add simple formatting (line breaks, bullet points)

### LinkedIn Personal Profile Publishing

LinkedIn's Share API supports personal profile posts with limited formatting. If Matt wants to auto-publish from his personal profile (not Company Page):

- Use the `w_member_social` scope
- POST to /ugcPosts with author = `urn:li:person:{MATT_LINKEDIN_ID}`
- Limitations: no rich formatting, no document posts, no polls
- For document/carousel posts: manual publish recommended

**Recommendation:** Auto-publish text posts to Company Page. Cross-share to personal profile manually for posts that warrant it. This preserves the "personal voice" that performs best on LinkedIn personal feeds.

---

## 5. Workflow G: Metrics Capture (24h Post-Publish)

### Purpose
Pull basic engagement metrics 24 hours after publishing. Write to Content Pipeline record.

### Fields to Add to Content Pipeline (Airtable Update)

| Field Name | Type | Notes |
|---|---|---|
| Impressions | Number | Auto-captured |
| Likes / Reactions | Number | Auto-captured |
| Comments Count | Number | Auto-captured |
| Shares / Reposts | Number | Auto-captured |
| Link Clicks | Number | Manual (platform-specific) |
| Platform Post ID | Single line text | For API lookups |
| Metrics Captured At | Date/Time | When metrics were pulled |
| Engagement Rate | Formula | `(Likes + Comments + Shares) / Impressions` |

### Steps

```
[1. Trigger: Scheduled — 24h after publish (or daily batch at 9 AM)]
  ├── Query Content Pipeline: Status = "Published" AND Metrics Captured At is empty
  │   AND Publish Date <= yesterday
  └── For each record with a Platform Post ID:

[2. Route by Platform and Fetch Metrics]

  [Facebook]
  GET /{post_id}?fields=insights.metric(post_impressions,post_engaged_users,post_clicks)
  Also: GET /{post_id}?fields=likes.summary(true),comments.summary(true),shares

  [Instagram]
  GET /{media_id}/insights?metric=impressions,reach,engagement,saved
  Also: GET /{media_id}?fields=like_count,comments_count

  [LinkedIn]
  GET /organizationalEntityShareStatistics?q=organizationalEntity
    &organizationalEntity=urn:li:organization:{ORG_ID}
    &shares=urn:li:share:{post_urn}
  Extract: impressionCount, clickCount, likeCount, commentCount, shareCount

[3. Write Metrics to Airtable]
  ├── Update Content Pipeline record:
  │   Impressions, Likes, Comments Count, Shares, Metrics Captured At = now
  └── Log: Info, "Metrics captured for {Post Title}: {impressions} impressions"

[4. Error Handling]
  ├── If metrics API fails: retry 3x
  ├── If still fails: log Error, Matt can check manually
  └── Some metrics (link clicks) may not be available via API → leave for manual entry
```

---

## 6. DM Handling

### Facebook / Instagram DMs

Meta's Messenger Platform API can receive DMs via webhooks (requires App Review for `pages_messaging` permission). This is a more complex integration.

**MVP approach:** Do NOT automate DM capture at launch. Reason: App Review for messaging permissions takes weeks, and the DM volume at launch is low enough for manual capture.

**Post-MVP:** Once comment capture is stable and volume grows, apply for messaging permissions and add DM webhook handling to Workflow E.

### LinkedIn DMs

No API access for LinkedIn DMs. Must remain manual capture. Use the streamlined Daily Cockpit entry form.

---

## 7. Manual Fallback Procedures

### If Workflow E (Engagement Capture) Fails

1. Check platforms manually for new comments (daily)
2. Create Engagement Inbox records by hand in Airtable
3. Log: System=Manual, Workflow="Engagement Capture"

### If Workflow F (Auto-Publish) Fails

1. Content remains in "Approved" status
2. Copy text from Airtable Draft field
3. Paste directly into platform's native composer
4. After publishing: paste Post URL back into Airtable record, set Status = "Published"
5. Log: System=Manual, Workflow="Auto-Publish"

### If Workflow G (Metrics Capture) Fails

1. Open each platform's native analytics
2. Manually enter: Impressions, Likes, Comments Count, Shares into Content Pipeline record
3. Set Metrics Captured At = now

---

## 8. Token Management

Social API access tokens expire. Here's the maintenance schedule:

| Platform | Token Type | Expiry | Refresh Method |
|---|---|---|---|
| Facebook Page | Long-lived Page Access Token | 60 days (or never if using System User) | Use System User token (never expires) or refresh via API before expiry |
| Instagram | Same as Facebook (linked) | Same | Same |
| LinkedIn | OAuth2 Access Token | 60 days | Refresh token flow via n8n credential refresh |

**Recommendation:** Set up a monthly calendar reminder to verify token health. Add a token expiry check to the Daily Error Digest — if a social API call fails with 401/403, log as Critical.

---

## 9. Rate Limits

| Platform | Limit | Impact |
|---|---|---|
| Facebook Graph API | 200 calls/user/hour | Plenty for our volume |
| Instagram Graph API | 200 calls/user/hour | Plenty |
| LinkedIn Marketing API | 100 calls/day (basic) or higher with partnership | May need batching for metrics. Polling every 15 min = 96 calls/day, just under limit. |

**Mitigation:** Batch API calls where possible. For LinkedIn, if we hit rate limits, reduce polling to every 30 min.
