# Vault Structure

```text
{user-chosen root}/
└── {Semester}/                          # e.g. 2026Spring
    ├── 学期总览.md
    └── {Course}/                        # default "CourseCode - Course Name"
        ├── raw/
        │   ├── _manifest/canvas-objects.json
        │   ├── sync/
        │   ├── assignments/{id}/{timestamp}.md
        │   ├── announcements/{id}/{timestamp}.md
        │   ├── pages/{id}/{timestamp}.md
        │   ├── modules/{id}/{timestamp}.md
        │   └── files/{id}/...
        ├── wiki/
        │   ├── 资料摘要/
        │   ├── 概念/
        │   ├── 主题/
        │   ├── 综合/
        │   └── assets/
        ├── templates/
        └── 课程总览.md
```

Rules:

- `raw/` is append-only evidence. Nothing already written to `raw/` is ever
  edited or deleted, including by this skill.
- `wiki/` is the learning surface. It can be updated, merged, rewritten, or
  deleted — but only the regions this skill generated (see
  `obsidian-rules.md` for the ownership boundary with user-written content).
- Course directory names default to `CourseCode - Course Name`
  (e.g. `CS101 - Intro to CS`); the user can rename at initialization.
- This skill's own protocol (this file, `sync-rules.md`, etc.) lives only in
  the skill package. Never generate a per-course `AGENTS.md` — that causes
  rule drift between courses and between users.
