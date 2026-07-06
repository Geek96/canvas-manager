# Obsidian / Wiki Authoring Rules

`wiki/` is organized like this inside each course:

```text
wiki/
├── 资料摘要/   # one summary per raw object (a lecture page, a module, a syllabus)
├── 概念/       # concept cards extracted from course material
├── 主题/       # cross-week, cross-module topic write-ups
├── 综合/       # 作业总览.md, 公告时间线.md, 考试与截止日期.md, 课程复习计划.md
└── assets/
```

## Ownership boundary (read this before editing any wiki file)

A wiki file can contain both agent-generated content and the student's own
handwritten notes in the same file. This skill must never destroy the
student's own writing.

Rule: every agent-generated section starts with an HTML comment marker and
ends with a matching close marker:

```markdown
<!-- agent-managed:start id="资料摘要-page-991" -->
... content this skill generated/updated ...
<!-- agent-managed:end -->
```

When updating a wiki file:

1. Read the whole file.
2. Only replace text between a matching `agent-managed:start`/`:end` pair
   with the same `id`.
3. If no marker with that `id` exists yet, append a new marked section —
   never assume the whole file is safe to overwrite.
4. Anything outside marker pairs (the student's own prose) is left
   byte-for-byte untouched.

## What goes in wiki vs. what stays in raw

- `raw/` keeps the Canvas object as received — never summarized, never
  rewritten.
- `wiki/资料摘要/` holds one digested summary per raw object, referencing its
  `source_snapshot` path so it's traceable back to the evidence it was
  written from.
- `wiki/概念/` and `wiki/主题/` are synthesis the agent builds up over time
  across multiple raw objects — these are the parts most likely to also
  contain the student's own notes, so the marker discipline above matters
  most here.
