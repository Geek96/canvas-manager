# Sync Rules

## When to sync

- Light sync: daily, twice a day (defaults: 06:00 and 18:00).
- Deep sync: weekly (default: Sunday 18:00) — produces the Weekly Digest
  (see below).

This skill does not assume any particular automation is running. At the end
of initialization, ask whether to set these three runs up now via Claude
Code's `/schedule` skill, pointed at this skill's sync procedure, or later
— see `interaction-style.md`. Never set them up unasked.

When a first-time sync covers several courses (or one course turns out to
have a lot of modules) and the total effort isn't knowable ahead of time,
ask whether to process everything in one pass or one course at a time with
a pause to look before continuing — see `interaction-style.md`. Don't
silently pick one.

## Sync procedure (per course, per object type)

1. Call the user's Canvas MCP tools to fetch the current objects of one type
   (e.g. all assignments) for the course.
2. Normalize each object into the schema in `canvas-object-model.md`, and
   write the list to a temp JSON file.
3. Run:
   ```bash
   python3 skills/canvas-manager/scripts/sync.py \
     --course-dir "{Root}/{Semester}/{Course}" \
     --object-type assignments \
     --input /tmp/canvas-assignments.json
   ```
4. Read the JSON result (`new`, `updated`, `unchanged`, `missing` object
   keys). For every `new` or `updated` key, read its `latest_snapshot` path
   from `raw/_manifest/canvas-objects.json` and update the relevant `wiki/`
   note (see `obsidian-rules.md`).
5. Repeat for each object type (`assignments`, `announcements`, `pages`,
   `modules`, `discussions`).

For `modules`, don't stop at the module→item structure — that's a table of
contents, not content. For every item that's a page or external URL, fetch
that item too and use its actual text as the `content` field. A module
object whose `content` is just a list of item titles is not useful for
`wiki/course_content/` or `wiki/info/`. Video/image items: keep the URL,
don't transcribe or describe the media (see `obsidian-rules.md`).

Never write to `raw/` directly — always go through `sync.py`, which is the
only thing that knows how to avoid duplicating unchanged snapshots and how
to avoid overwriting same-second writes.

## Weekly Digest (deep sync)

After the normal per-object-type sync above, additionally:

- Update `学期总览.md` and each course's `课程总览.md`.
- Summarize the week's new/updated objects (from that week's
  `raw/sync/*.md` logs).

Deadline-aware prioritization, a plan-candidate export, and anything that
reads like "what should I focus on this week" belong to the separate
[`course-manager`](https://github.com/Geek96/course-manager) skill, not
this one — see `obsidian-rules.md`.

## Attachments

Default sync reads metadata and text content only. Large file attachments
(PDF/PPT/etc.) are not downloaded automatically — that is a separate,
on-demand action the user can trigger per file.

## Failure handling

- If a Canvas MCP call fails or is rate-limited for an object type, skip
  that type for this run — do not partially write its manifest entries.
  Note the failure in that run's sync log. The next scheduled run retries
  automatically.
- `sync.py` itself only ever updates the manifest entries it successfully
  wrote a snapshot for, so a script-level failure mid-run cannot corrupt
  entries it didn't touch.
