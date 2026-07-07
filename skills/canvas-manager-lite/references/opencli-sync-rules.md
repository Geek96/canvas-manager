# opencli Sync Rules (CanvasManager Lite)

Lite has no Canvas API token and no Canvas MCP server. It reads Canvas the
same way the student would in a browser: through `opencli`'s browser bridge,
reusing the student's already-logged-in session. Everything downstream
(vault structure, `wiki/` authoring rules) is shared with the full
CanvasManager skill — only how raw data is captured and stored differs.
This assumes `opencli doctor` reports the browser extension connected; if
not, tell the user to install/connect it first.

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

## Scheduling and PlanVault hand-off

Same as the full skill: guide the user to set up recurring `/schedule`
runs, and export plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md`. Lite does not change
either of these.
