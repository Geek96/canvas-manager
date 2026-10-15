# External platform sync (Gradescope, Perusall, Ed, Piazza, …)

Many courses put required work on platforms Canvas only links to (often
as an "external tool" assignment): Gradescope submissions, Perusall
readings, Ed / Piazza announcements. Their deadlines and submission state
never show up in Canvas data, so sync them alongside the course.

**Which platforms to sync**: `.courseos/STATE.md` → "外部平台同步" lists,
per course, the platforms the student switched on in CourseOS. Only
touch those. Platforms not listed: leave alone.

## General rules

- Same browser session as the course (`cm-{course-slug}`) — the student is
  already logged in to Canvas there, and most platforms are reached
  through Canvas or the same school SSO.
- Find the platform course from the Canvas side first: an external-tool
  assignment or a module/page link to the platform (use the link in the
  course's raw data). If a link needs a launch through Canvas (LTI), open
  the Canvas assignment and follow its "Load in a new window" button.
- If a login page, SSO prompt, or 2FA appears: stop for that platform,
  note it in the journal ("Gradescope 需要重新登录"), continue with the
  next one. Never type credentials.
- Read only. Never submit, annotate, post, vote, or change settings.
- Store each result with the generic text sync, same as Canvas text
  objects (latest-only, content-hash skip):

  ```bash
  python3 skills/canvas-manager-lite/scripts/sync_lite.py \
    --data-dir "{Root}/{Semester}.data/{Course}" \
    --object-type gradescope --input /tmp/gradescope.json
  ```

  Object shape: `canvas_type` = the platform id, `canvas_id` = the
  platform's course id (or post id), `course_id` = the Canvas course id,
  `title`, `updated_at_canvas` = fetch time, `source_url` = the platform
  page, `content` = the normalized text below. Files land at
  `raw/{platform}/{id}/latest.md`.

## Per platform

### Gradescope (`gradescope`)
Open `https://www.gradescope.com/courses/{id}`; the table lists every
assignment. Scripts: `scripts/platforms/gradescope_table.js` (eval in the
tab) → `scripts/platforms/gradescope_build.py`. One object per course;
`content`:

```
| 作业 | 发布 | 截止 | 迟交截止 | 状态 | 得分 |
|---|---|---|---|---|---|
| PE 05 | 2026-10-01 | 2026-10-12 23:59 | 2026-10-13 23:59 | 已交 | 98/100 |
```

状态 as shown: 已交 (Submitted), 未交 (No Submission), 已批改 (graded —
write the score). Use the page's own dates (convert to the student's local
time, `YYYY-MM-DD HH:mm`).

**Problem PDFs (handouts).** Some instructors post the problem set only on
Gradescope: an unsubmitted assignment's page
(`/courses/{id}/assignments/{aid}/submissions/new`) then shows
"Download {name} PDF" (a signed S3 link valid for a few hours). Canvas has
no copy, so course-manager has nothing to read for that homework's scope.
For each open assignment, check whether that link exists and **ask the
student before downloading** (filename, source, approximate size). On a
yes, save it to `raw/gradescope/{assignment name}.pdf` (e.g. `H7.pdf`; signed
link: `curl -s -o …` is fine, no credentials involved) and mention it in
the course's `wiki/info/` note for that assignment.

### Perusall (`perusall`)
Open the course on `app.perusall.com`; the assignments list shows each
reading with its deadline and completion. One object per course;
`content`: `| 阅读任务 | 截止 | 状态 | 得分 |` with 已完成 / 未开始 /
进行中 as shown.

### Ed Discussion (`ed`)
Open the course on `edstem.org` (wait until the page has loaded — the Ed
token is read from that tab's localStorage; an empty result usually means
the tab wasn't ready, retry once). Scripts: `scripts/platforms/ed_threads.js`
→ `scripts/platforms/ed_build.py`. Collect **only** posts by staff
(instructor / TA badge) that are announcements or pinned — skip student
questions. One object per post (`canvas_id` = post number); `content`:
title, author role, date, full text. Cap at the 30 most recent.

### Piazza (`piazza`)
Open `piazza.com/class/{id}`. **Only** instructor notes and pinned posts.
One object per post, same shape as Ed. Cap at 30.

### Other platforms (WebAssign, zyBooks, MyLab, Top Hat, Connect, WileyPLUS, Achieve, Codio, MATLAB Grader)
One object per course with `| 作业 | 截止 | 状态 | 得分 |` from the
platform's assignment / due-date list. If the platform has no such list
reachable without extra navigation, note it in the journal and skip.

## Hand-off

course-manager reads `raw/{platform}/` on its next run: platform
assignments join the to-do list (deduplicated against Canvas), staff
posts are scanned for dates like any announcement. See course-manager's
`references/tasks-and-projects.md`.
