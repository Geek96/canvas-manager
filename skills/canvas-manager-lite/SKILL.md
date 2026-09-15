---
name: canvas-manager-lite
description: Default variant — use when a student wants to sync Canvas LMS content into an Obsidian vault. Most institutions (Georgia Tech included) disable self-service Canvas API tokens for students, so start here unless the student already has a Canvas MCP server connected with a working token, in which case `canvas-manager` (full) is also an option for full version history. Drives Canvas through opencli's browser bridge instead of the Canvas MCP/API — no token needed.
---

# CanvasManager Lite

## Obsidian authoring contract

Before creating or updating any Obsidian artifact, read
`references/obsidian-core.md`. This package-local Core is the portable
baseline; the CanvasManager Lite rules and templates in this Skill take
precedence whenever they are more specific.

Same goal as `canvas-manager` — semester → course organized Obsidian vault,
Canvas as source of truth, Obsidian as learning surface — but reads Canvas
through `opencli`'s browser bridge instead of a Canvas MCP server, reusing
the student's already-logged-in browser session. This is the default
variant: no API token, no MCP server setup, works for every student
regardless of whether their institution allows self-service tokens.

Shared with the full skill, unchanged:
- Vault layout — see `../canvas-manager/references/vault-structure.md`
- Wiki authoring / agent-managed-content boundary, the `course_content/` vs
  `info/` classification standard, and the `textbooks/`/`textbook_breakdown/`
  handling — see `../canvas-manager/references/obsidian-rules.md` and
  `../canvas-manager/SKILL.md`'s "Textbooks" section. Lite doesn't fetch
  textbooks either — same rule, browser-driven or not.
- Normalized object schema — see
  `../canvas-manager/references/canvas-object-model.md`
- `/schedule`-based recurring sync

What's different, and why — see `references/opencli-sync-rules.md`:
- Text objects (assignments/announcements/pages/modules/discussions) keep
  only their **latest** version in `raw/` (no history), because browser
  scraping can't see Canvas's real `updated_at` timestamps, so a full
  timestamped history isn't trustworthy anyway.
- File attachments are added automatically when new, but an existing
  filename that might have a new version **requires the user to explicitly
  say to replace it** — never silently overwritten.

## First-time initialization

See `../canvas-manager/references/interaction-style.md` for how to ask
these — the course question in particular should be a pick-list built from
the student's actual live course list, not a cold open-ended question.

**Before anything else, confirm opencli is installed and connected:**

```bash
opencli doctor
```

If that command isn't found at all: `npm install -g @jackwener/opencli`
(needs Node.js/npm — if the student doesn't have those either, point them
to nodejs.org first). If it's found but reports the browser extension not
connected, see [github.com/jackwener/OpenCLI](https://github.com/jackwener/OpenCLI)
for the extension install/reconnect steps — this varies by browser and is
better walked through from the project's own docs than restated here.

Then ask:

1. What's your Canvas institution's domain? (the part before
   `.instructure.com` in your Canvas URL, e.g. `gatech` for
   `gatech.instructure.com`) — if the student isn't sure, ask them to paste
   the URL they use to reach Canvas and extract it from that instead of
   making them figure out the subdomain themselves.
2. Where should the vault root live? (a folder path)
3. What's the current semester name? (e.g. `2026Fall`; suggest a default
   inferred from today's date and let them just confirm it)
4. Open `https://{institution}.instructure.com/courses` with `opencli
   browser` and extract the student's current-term course list, then
   present it as a numbered pick-list. Which should be tracked this
   semester, and does the default `CourseCode - Course Name` directory
   naming work for each, or do they want to rename any? A course showing
   as not-yet-published (per `vault-structure.md`) gets a placeholder
   entry, not a full directory.

This same first open-and-extract call also doubles as the login check: if
the page redirects to a Canvas login screen instead of showing the course
list, the student isn't logged into Canvas in the browser profile opencli
is bridged to — tell them to log in there first, then retry. If it shows
the real course list, the session is authenticated.

## Every sync

Follow `references/opencli-sync-rules.md` step by step: navigate with
`opencli browser`, extract and normalize content, then call
`scripts/sync_lite.py` for each object type. For any file flagged
`needs_confirmation` in the result, tell the user and wait for an explicit
yes before re-running with `--confirm-replace`.
