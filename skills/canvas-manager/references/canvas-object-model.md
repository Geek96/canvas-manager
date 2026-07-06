# Canvas Object Model

`sync.py` never talks to Canvas or an MCP server directly — it only accepts a
JSON list of objects already normalized to this shape:

```json
{
  "canvas_type": "assignment",
  "canvas_id": 12345,
  "course_id": 67890,
  "title": "Homework 4",
  "updated_at_canvas": "2026-07-09T07:55:00",
  "source_url": "https://school.instructure.com/courses/67890/assignments/12345",
  "content": "Markdown/plain-text body of the object"
}
```

Required fields: `canvas_type`, `canvas_id`, `course_id`, `title`,
`updated_at_canvas`, `source_url`, `content`. All are strings except
`canvas_id`/`course_id`, which are integers.

`canvas_type` is always singular (`assignment`, `announcement`, `page`,
`module`, `discussion`, `syllabus`). The `--object-type` flag passed to
`sync.py` is the plural form used for the `raw/` subdirectory
(`assignments`, `announcements`, `pages`, `modules`, `discussions`).

## Turning Canvas MCP output into this shape

Whatever Canvas MCP server the user has connected (e.g. a community
`canvas-mcp` server), its tool responses will have their own field names.
Before calling `sync.py`, the agent must map that output into the schema
above and write it to a temp JSON file, one file per object type per course,
per sync run. This mapping step is the only part of the pipeline that
depends on which MCP server the user has installed — everything downstream
(`sync.py`, the raw/manifest/wiki rules) is server-agnostic.

If a Canvas field doesn't map cleanly (e.g. an MCP server that doesn't
expose `updated_at`), fall back to the fetch time and note the gap in that
run's sync log — never invent a value.
