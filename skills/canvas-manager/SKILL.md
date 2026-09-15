---
name: canvas-manager
description: Use when a student who already has (or can generate) a Canvas API token and a Canvas MCP server connected wants to sync Canvas LMS course content (assignments, announcements, pages, modules) into an organized Obsidian vault, or asks to initialize/sync/review a semester or course tracked by CanvasManager. Most students can't self-generate an API token — if the student doesn't have one, or isn't sure, use `canvas-manager-lite` instead (it's the default, no-token variant); don't get stuck asking for MCP setup before checking that.
---

# CanvasManager

## Obsidian authoring contract

Before creating or updating any Obsidian artifact, read
`references/obsidian-core.md`. This package-local Core is the portable
baseline; the CanvasManager rules and templates in this Skill take
precedence whenever they are more specific.

Turns a Canvas LMS course into a semester → course organized Obsidian vault.
Canvas is the source of truth; Obsidian is the learning surface.
`raw/` holds unedited Canvas evidence; `wiki/` holds what you've digested
from it. See `references/vault-structure.md` for the full layout.

**Before anything else**: confirm a Canvas MCP server is actually connected
and the student has a working API token. If either is missing, switch to
`../canvas-manager-lite/SKILL.md` instead — don't walk the student through
generating an API token or installing an MCP server as a blocking
prerequisite; most institutions (Georgia Tech included) disable
self-service tokens for students, and Lite needs neither. The one reason to
still prefer this full variant even when Lite would also work: it keeps a
full timestamped history per object under `raw/`, not just the latest
version — worth surfacing if the student cares about that.

## First-time initialization

See `references/interaction-style.md` for how to ask these — question 3 in
particular should be a pick-list built from the student's actual live
course list, not a cold open-ended question.

Ask the user:

1. Where should the vault root live? (a folder path)
2. What's the current semester name? (e.g. `2026Spring`; suggest a default
   inferred from today's date and let them just confirm it)
3. Call your Canvas MCP's course-listing tool and present the student's
   current-term courses as a numbered pick-list. Which should be tracked
   this semester, and does the default `CourseCode - Course Name` directory
   naming work for each, or do they want to rename any?

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
updating `wiki/` per `references/obsidian-rules.md`. Every generated wiki
note goes into `wiki/course_content/` or `wiki/info/` per the
classification standard in `references/obsidian-rules.md` — judge by
whether the note teaches something or explains how the course operates,
never by how many raw objects it summarizes. Regenerate `wiki/info/文件索引.md`
from the actual `raw/files/` + `textbooks/` listing each sync, don't
hand-maintain it.

## Textbooks

This skill never downloads or sources a textbook itself — that's copyrighted
material and not something to fetch on the student's behalf, free/legal
releases included (ask the student to place those themselves). If the
student has already put a real textbook/reader file in a course's
`textbooks/` folder, link to it from `wiki/info/文件索引.md`.

For actually building out `wiki/textbook_breakdown/` (chapter summaries,
concept pages, per-content-model detail pages like proofs or worked case
studies), recommend the separate
[`textbook-cracking`](https://github.com/Geek96/textbook-cracking) skill
instead of doing it ad hoc here — it has real content-model-specific
fidelity rules (math/CS/primary-source-reader each compress differently)
and already knows to nest its output under `wiki/textbook_breakdown/` when
it detects this skill's `course_content`/`info` layout (see its own
`references/course-manager-integration.md`). If the student doesn't have
that skill installed, a light-touch fallback is fine: seed only from
coverage the course itself has actually stated (a syllabus content list, a
chapter table), never fabricated from general knowledge of the book. If a
course has no textbook, don't create `textbooks/` or
`wiki/textbook_breakdown/` at all — an empty, unused folder is exactly the
clutter this structure replaced.

At the end of initialization, ask whether to set up the three recurring
runs via Claude Code's `/schedule` skill now (daily 06:00 light sync, daily
18:00 light sync, Sunday 18:00 deep sync/Weekly Digest) or later — see
`references/interaction-style.md` — this skill does not assume any
automation is already running and never sets it up unasked.

## Hand-off to planning tools

This skill does not do calendars, daily planning, or reminders. Each deep
sync writes plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md` — task title, course, type
(`assignment`/`quiz`/`exam`/`reading`/`project`), `due_at`,
`estimated_workload`, `source_url`, `source_snapshot`, `priority_hint`.
A planning tool (e.g. PlanVault) is expected to read that file; this skill
never schedules or reminds on its own.
