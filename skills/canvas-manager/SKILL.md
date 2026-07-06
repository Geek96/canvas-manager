---
name: canvas-manager
description: Use when a student wants to sync Canvas LMS course content (assignments, announcements, pages, modules) into an organized Obsidian vault, or asks to initialize/sync/review a semester or course tracked by CanvasManager.
---

# CanvasManager

Turns a Canvas LMS course into a semester → course organized Obsidian vault.
Canvas is the source of truth; Obsidian is the learning surface.
`raw/` holds unedited Canvas evidence; `wiki/` holds what you've digested
from it. See `references/vault-structure.md` for the full layout.

## First-time initialization

Ask the user:

1. Where should the vault root live? (a folder path)
2. What's the current semester name? (e.g. `2026Spring`)
3. Which Canvas courses to track this semester, and does the default
   `CourseCode - Course Name` directory naming work, or do they want to
   rename any course directory?

Then create the directory skeleton from `references/vault-structure.md` and
the templates in `templates/` for each course, plus the semester dashboard.
If two courses would resolve to the same default directory name (e.g. two
courses both named "Intro Seminar"), stop and ask the user to pick distinct
names for the colliding ones — never silently overwrite an existing course
directory.

## Every sync

Follow `references/sync-rules.md` step by step — it covers calling the
user's Canvas MCP, normalizing objects per
`references/canvas-object-model.md`, invoking `scripts/sync.py`, and
updating `wiki/` per `references/obsidian-rules.md`.

At the end of initialization, tell the user to set up three recurring runs
via Claude Code's `/schedule` skill (daily 06:00 light sync, daily 18:00
light sync, Sunday 18:00 deep sync/Weekly Digest) — this skill does not
assume any automation is already running.

## Hand-off to planning tools

This skill does not do calendars, daily planning, or reminders. Each deep
sync writes plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md` — task title, course, type
(`assignment`/`quiz`/`exam`/`reading`/`project`), `due_at`,
`estimated_workload`, `source_url`, `source_snapshot`, `priority_hint`.
A planning tool (e.g. PlanVault) is expected to read that file; this skill
never schedules or reminds on its own.
