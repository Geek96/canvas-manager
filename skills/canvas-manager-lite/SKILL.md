---
name: canvas-manager-lite
description: Use when a student wants to sync Canvas LMS content into an Obsidian vault but has no Canvas API token (e.g. their institution disabled self-service token creation) — drives Canvas through opencli's browser bridge instead of the Canvas MCP/API.
---

# CanvasManager Lite

Same goal as `canvas-manager` — semester → course organized Obsidian vault,
Canvas as source of truth, Obsidian as learning surface — but for students
who can't get a Canvas API token. Instead of a Canvas MCP server, this
drives Canvas through `opencli`'s browser bridge, reusing the student's
already-logged-in browser session.

Shared with the full skill, unchanged:
- Vault layout — see `../canvas-manager/references/vault-structure.md`
- Wiki authoring / agent-managed-content boundary — see
  `../canvas-manager/references/obsidian-rules.md`
- Normalized object schema — see
  `../canvas-manager/references/canvas-object-model.md`
- `/schedule`-based recurring sync, and the PlanVault hand-off file

What's different, and why — see `references/opencli-sync-rules.md`:
- Text objects (assignments/announcements/pages/modules/discussions) keep
  only their **latest** version in `raw/` (no history), because browser
  scraping can't see Canvas's real `updated_at` timestamps, so a full
  timestamped history isn't trustworthy anyway.
- File attachments are added automatically when new, but an existing
  filename that might have a new version **requires the user to explicitly
  say to replace it** — never silently overwritten.

## First-time initialization

Before anything else, confirm `opencli doctor` shows the browser extension
connected. Then ask the same three initialization questions as the full
skill (vault root, semester name, courses + directory naming), and check
that the student is actually logged into Canvas by opening their Canvas
dashboard and confirming personalized content renders (e.g. a to-do list
or grades link) — that's the signal the session is authenticated.

## Every sync

Follow `references/opencli-sync-rules.md` step by step: navigate with
`opencli browser`, extract and normalize content, then call
`scripts/sync_lite.py` for each object type. For any file flagged
`needs_confirmation` in the result, tell the user and wait for an explicit
yes before re-running with `--confirm-replace`.
