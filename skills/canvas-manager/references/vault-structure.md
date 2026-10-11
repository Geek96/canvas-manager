# Vault Structure

```text
{user-chosen root}/
├── {Semester}/                          # e.g. 2026Spring — the Obsidian vault
│   ├── 学期总览.md
│   ├── courseos.json                    # config surface (CourseOS)
│   ├── _exports/planvault-time-sensitive.md
│   └── {Course}/                        # default "CourseCode - Course Name"
│       ├── wiki/
│       │   ├── course_content/
│       │   ├── info/                    # incl. 文件索引.md → readings/ + textbooks/
│       │   ├── textbook_breakdown/      # only if the course has a real textbook
│       │   ├── 综合/                   # only if the course-manager skill is also installed and run
│       │   └── assets/
│       ├── textbooks/                   # user-sourced textbook/reader files, not Canvas evidence
│       ├── readings/                    # human-readable copies of teacher uploads (this skill)
│       ├── submissions/                 # the student's own work; this skill never writes here
│       ├── templates/
│       └── 课程总览.md
├── {Semester}.data/                     # vault-OUTSIDE: machine surface
│   └── {Course}/
│       └── raw/                         # append-only evidence (moved out in v0.4.0)
│           ├── _manifest/canvas-objects.json
│           ├── sync/
│           ├── assignments/{id}/{timestamp}.md
│           ├── announcements/{id}/{timestamp}.md
│           ├── pages/{id}/{timestamp}.md
│           ├── modules/{id}/{timestamp}.md
│           └── files/{id}/...
└── {Semester}.code/                     # vault-OUTSIDE: code surface (VSCode)
    └── {Course}/                        # one git repo per course
```

Rules:

- `raw/` is append-only evidence and lives **outside** the Obsidian vault
  (`{Semester}.data/{Course}/raw/`). Nothing already written there is ever
  edited or deleted, including by this skill. Obsidian never indexes it —
  no "excluded files" hacks needed. (Moved out in v0.4.0; was
  `{Course}/raw/`.)
- `readings/` holds human-readable **copies** (never symlinks —
  Syncthing/mobile safe) of teacher-uploaded readable files
  (pdf/docx/pptx) extracted from `raw/files/` on each sync. Named from
  the file's own title, prefixed with the module name when known,
  deduplicated (`-2`, `-3`, …). This is the read-in-Obsidian layer —
  Obsidian renders PDFs natively. Regenerated from the actual directory
  listing each sync, never hand-edited.
- `submissions/` is the student's own work product (`{assignment-slug}/`
  per assignment: drafts + the submitted artifact). This skill never
  creates it and never writes into it — course-manager reads it read-only
  for submitted/not-submitted status.
- `wiki/` is the learning surface. It can be updated, merged, rewritten, or
  deleted — but only the regions this skill generated (see
  `obsidian-rules.md` for the ownership boundary with user-written content,
  and for the `course_content/` vs `info/` classification standard).
- `textbooks/` holds textbook/reader files the *user* sourced (bought, or a
  legally free release) — never something this skill downloaded itself, and
  never a pirated copy. This skill only ever links to files already placed
  here; it does not fetch textbooks. Create this folder only once a real
  file exists for the course — don't pre-provision an empty one.
- `wiki/textbook_breakdown/` only exists for a course that actually has a
  textbook in `textbooks/`. Don't create it as an empty placeholder for a
  course with none (e.g. a course whose readings live entirely on an
  external platform like Perusall) — an empty, never-used folder is exactly
  the clutter this structure replaced (see `obsidian-rules.md`).
- `wiki/综合/` is not created or written by this skill at all — it's owned
  entirely by the separate
  [`course-manager`](https://github.com/Geek96/course-manager) skill (an
  assignment overview, announcement timeline, exam/deadline table, and
  review plan built from this skill's evidence). It only exists in a
  course directory if that skill has also been installed and run there.
- Course directory names default to `CourseCode - Course Name`
  (e.g. `CS101 - Intro to CS`); the user can rename at initialization.
- This skill's own protocol (this file, `sync-rules.md`, etc.) lives only in
  the skill package. Never generate a per-course `AGENTS.md` — that causes
  rule drift between courses and between users.
