# opencli Sync Rules (CanvasManager Lite)

Lite has no Canvas API token and no Canvas MCP server. It reads Canvas the
same way the student would in a browser: through `opencli`'s browser bridge,
reusing the student's already-logged-in session. Everything downstream
(vault structure, `wiki/` authoring rules) is shared with the full
CanvasManager skill — only how raw data is captured and stored differs.
This assumes `opencli doctor` reports the browser extension connected; if
not, see `SKILL.md`'s initialization section for how to install it — don't
restate install steps here, they live in one place.

When a first-time sync covers several courses (or one course turns out to
have a lot of modules) and the total effort isn't knowable ahead of time,
ask whether to process everything in one pass or one course at a time with
a pause to look before continuing — see
`../../canvas-manager/references/interaction-style.md`. Don't silently pick
one.

## Navigating Canvas

Pick one session name per sync run (e.g. `cm`) and reuse it across calls so
the tab stays alive:

```bash
opencli browser cm open https://{institution}.instructure.com/courses
opencli browser cm extract          # course list
opencli browser cm open https://{institution}.instructure.com/courses/{id}/assignments
opencli browser cm extract          # assignment list for one course
opencli browser cm open https://{institution}.instructure.com/courses/{id}/modules
opencli browser cm extract          # full module -> item tree
opencli browser cm open https://{institution}.instructure.com/courses/{id}/modules/items/{item_id}
opencli browser cm extract          # one page's full rich-text content
```

Some courses disable a tab (assignments, announcements, pages, files) —
`extract` silently redirects back to the course home page when that
happens. Treat that as "this course has none of this object type," not as
an error.

**Don't stop at the module list.** `opencli browser cm extract` on a
`/modules` page only returns the module→item table of contents (item
titles and their `/modules/items/{item_id}` links) — not the actual page
content. For every item that's a page or external URL, open its
`/modules/items/{item_id}` link (it redirects to the real content page)
and extract *that* page's full text — that's what goes into the object's
`content` field, not the module list entry. A `wiki/course_content/` or
`wiki/info/` note written from a module's table of contents instead of the
real page text is not useful to the student.

Video/image module items: keep the item's URL only, don't transcribe or
describe the media itself (see
`../../canvas-manager/references/obsidian-rules.md`).

## Normalizing into the shared object schema

Map extracted content into the same shape used by the full skill (see
`../../canvas-manager/references/canvas-object-model.md`): `canvas_type`,
`canvas_id`, `course_id`, `title`, `updated_at_canvas`, `source_url`,
`content`.

Browser scraping cannot see Canvas's internal `updated_at` timestamp, so
`updated_at_canvas` always falls back to the fetch time — this is expected
and already accounted for by only keeping the latest version (below), not
a full timestamped history.

## Text objects: latest-only, no history

Call `sync_lite.py` with `--object-type` set to `assignments`,
`announcements`, `pages`, `modules`, or `discussions`:

```bash
python3 skills/canvas-manager-lite/scripts/sync_lite.py \
  --course-dir "{Root}/{Semester}/{Course}" \
  --object-type pages \
  --input /tmp/canvas-pages.json
```

Unlike the full skill's `raw/{type}/{id}/{timestamp}.md` history, Lite
writes only `raw/{type}/{id}/latest.md` and overwrites it in place when
content changes. A content-hash check still skips the write entirely when
nothing changed, so re-running sync with no Canvas-side changes is a no-op.

## Files: additive by default, replacement needs confirmation

Download real attachments by navigating to their Canvas download URL —
this triggers a real browser file download (verified: it lands in the
OS Downloads folder, not just rendered as a page). Move it into place via
`sync_lite.py --object-type files`, passing each entry's `file_id`,
`filename`, and the local downloaded path.

- A `file_id` never seen before in this course → added automatically.
- A `file_id` already registered → skipped, nothing to do.
- A **new** `file_id` with a **filename that already exists** under a
  different `file_id` in this course → flagged as `needs_confirmation` and
  **not** written to disk or the manifest. Report this to the user (e.g.
  "`syllabus.pdf` may have a new version on Canvas — replace the one we
  have?"). Only re-run with `--confirm-replace {file_id}` after the user
  explicitly says yes. The previous version is never deleted, even after a
  confirmed replacement — both live under their own `raw/files/{file_id}/`.

## Scheduling

Same as the full skill: at the end of initialization, ask whether to set up
the three recurring `/schedule` runs now or later (see
`../../canvas-manager/references/interaction-style.md`) — never set them up
unasked. Lite does not change this.

For deadline-aware synthesis and a PlanVault hand-off file, see the
separate [`course-manager`](https://github.com/Geek96/course-manager)
skill — same as the full variant, this skill only ever writes one summary
per raw object.
