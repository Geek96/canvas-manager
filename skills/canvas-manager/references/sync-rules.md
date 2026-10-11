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

## Paths (v0.4.0)

The raw evidence store lives **outside** the Obsidian vault:

- Course dir (vault): `{Root}/{Semester}/{Course}`
- Data dir (machine surface): `{Root}/{Semester}.data/{Course}`
- Raw store: `{Root}/{Semester}.data/{Course}/raw/`

`latest_snapshot` values in `raw/_manifest/canvas-objects.json` are
relative to the **data dir** (e.g. `raw/assignments/123/2026-10-07-180000.md`).

## Sync procedure (per course, per object type)

1. Call the user's Canvas MCP tools to fetch the current objects of one type
   (e.g. all assignments) for the course.
2. Normalize each object into the schema in `canvas-object-model.md`, and
   write the list to a temp JSON file.
3. Run:
   ```bash
   python3 skills/canvas-manager/scripts/sync.py \
     --data-dir "{Root}/{Semester}.data/{Course}" \
     --object-type assignments \
     --input /tmp/canvas-assignments.json
   ```
4. Read the JSON result (`new`, `updated`, `unchanged`, `missing` object
   keys). For every `new` or `updated` key, read its `latest_snapshot` path
   from `{Root}/{Semester}.data/{Course}/raw/_manifest/canvas-objects.json`
   (resolve relative to the data dir) and update the relevant `wiki/`
   note (see `obsidian-rules.md`).
5. Repeat for each object type (`assignments`, `announcements`, `pages`,
   `modules`, `discussions`).
6. Extract readable documents into `readings/`:
   ```bash
   python3 skills/canvas-manager/scripts/extract_readings.py \
     --data-dir "{Root}/{Semester}.data/{Course}" \
     --course-dir "{Root}/{Semester}/{Course}"
   ```
   This copies new teacher-uploaded pdf/docx/pptx files from the raw store
   into `{Course}/readings/` with human-readable names (copies, never
   symlinks; deduplicated; identical files skipped).
7. Regenerate `wiki/info/文件索引.md` from the actual `readings/` +
   `textbooks/` directory listing (script it, don't hand-type) so it
   can't drift from reality.

For `modules`, don't stop at the module→item structure — that's a table of
contents, not content. For every item that's a page or external URL, fetch
that item too and use its actual text as the `content` field. A module
object whose `content` is just a list of item titles is not useful for
`wiki/course_content/` or `wiki/info/`. Video/image items: keep the URL,
don't transcribe or describe the media (see `obsidian-rules.md`).

Never write to the raw store directly — always go through `sync.py`, which
is the only thing that knows how to avoid duplicating unchanged snapshots
and how to avoid overwriting same-second writes.

## Weekly Digest (deep sync)

After the normal per-object-type sync above, additionally:

- Update `学期总览.md` and each course's `课程总览.md`.
- Summarize the week's new/updated objects (from that week's
  `{Root}/{Semester}.data/{Course}/raw/sync/*.md` logs).

Deadline-aware prioritization, a plan-candidate export, and anything that
reads like "what should I focus on this week" belong to the separate
[`course-manager`](https://github.com/Geek96/course-manager) skill, not
this one — see `obsidian-rules.md`.

## Attachments & readings

Teacher-uploaded readable documents (pdf/docx/pptx) **are** downloaded
during sync into `raw/files/{id}/` — they're the course's actual reading
material and the student wants them readable in Obsidian (that's what
`readings/` is for). Large media (video/audio/big datasets, or anything
well over ~100MB) stays on-demand per file, as before — keep only the URL
in the snapshot.

## Failure handling

- If a Canvas MCP call fails or is rate-limited for an object type, skip
  that type for this run — do not partially write its manifest entries.
  Note the failure in that run's sync log. The next scheduled run retries
  automatically.
- `sync.py` itself only ever updates the manifest entries it successfully
  wrote a snapshot for, so a script-level failure mid-run cannot corrupt
  entries it didn't touch.
