# Grades page sync (submission status and scores)

CourseCenter and course-manager need to know which assignments the
student has already submitted (to mark them done) and their scores (for
the archive and regrade decisions). Lite gets this from the course's
Canvas **Grades** page — one page per course, every assignment on it.

```bash
opencli browser cm-cs-1331 open https://{institution}.instructure.com/courses/{id}/grades
opencli browser cm-cs-1331 extract
```

Normalize the page into **one** object and store it with the generic
text sync (latest-only, content-hash skip like other text types):

```json
[{
  "canvas_type": "grades", "canvas_id": {course_id}, "course_id": {course_id},
  "title": "Grades", "updated_at_canvas": "{fetch time}",
  "source_url": "https://{institution}.instructure.com/courses/{id}/grades",
  "content": "| 作业 | 截止 | 状态 | 得分 |\n|---|---|---|---|\n| HW 5 | 2026-10-14 23:59 | 已交 | 18/20 |\n…"
}]
```

```bash
python3 skills/canvas-manager-lite/scripts/sync_lite.py \
  --data-dir "{Root}/{Semester}.data/{Course}" \
  --object-type grades --input /tmp/canvas-grades.json
```

This writes `raw/grades/{course_id}/latest.md`. `content` is a Markdown
table with one row per assignment:

- **状态**: 已交 (submitted), 迟交 (late), 缺交 (missing), 未交 (not yet
  submitted, not yet due), 免交 (excused). Use what the page shows —
  Canvas marks these with icons/labels ("Submitted", "Late", "Missing",
  "Excused"); don't guess from scores alone.
- **得分**: `score/points` as shown, empty when ungraded.

Grades are private data: they stay in the local `.data` folder like every
other raw object, never in the Obsidian vault and never sent anywhere.
If the course hides the Grades tab, `extract` redirects to the course
home — treat that as "no grades data," not an error.
