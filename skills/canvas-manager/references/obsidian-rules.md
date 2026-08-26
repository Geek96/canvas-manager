# Obsidian / Wiki Authoring Rules

`wiki/` is organized like this inside each course:

```text
wiki/
├── course_content/    # digested per-object content — see classification standard below
├── info/               # operational/administrative info — see classification standard below
├── textbook_breakdown/ # only if the course has a real textbook in ../textbooks/
└── assets/
```

## Classification standard: `course_content/` vs `info/`

**The test: does this note teach you something, or does it tell you how the
course operates?**

- **`course_content/`** — the actual academic substance: what you're
  supposed to learn, read, or produce. Lecture/module content, practice
  problems, project descriptions, skill-building material (e.g. a
  debugging-technique video), and an assignment's actual prompt/task.
- **`info/`** — logistics: syllabus/policies, deadlines, submission
  mechanics, exam procedure/format, tooling setup, support resources,
  onboarding, compliance-flavored assignments (a "read the syllabus" quiz, a
  usage-tracking form). Answers "how do I operate inside this course," not
  "what am I learning."

This is **not** decided by how many raw objects a note maps to — a syllabus
page is a single object but is still `info`, not `course_content`. Judge by
content nature, not object count.

| Kind of note | Example | Bucket |
|---|---|---|
| Syllabus / course policy / course home page | any course's syllabus | `info` |
| Exam rules/format (not exam coverage) | "Exam Instructions", exam date/weight records | `info` |
| Support/tutoring resources | PLUS sessions, disability services | `info` |
| Environment/tooling setup | IDE install, linter config docs | `info` |
| Onboarding / welcome | "Start Here", Week 1 checklist | `info` |
| Compliance-flavored assignment | a syllabus quiz, a usage-tracking form | `info` |
| Lecture/module actual content | a week's lecture notes | `course_content` |
| Practice material / skill-teaching content | weekly practice problems, a technique video | `course_content` |
| An assignment/project's real prompt | the actual task description | `course_content` |

`info/` also holds the fixed cross-cutting synthesis notes below (these
aggregate across many raw objects for a specific operational purpose — same
underlying logic, don't split them into a separate folder):

- `作业总览.md` — every assignment, due date, status
- `公告时间线.md` — announcements in reverse chronological order
- `考试与截止日期.md` — exam/deadline table
- `课程复习计划.md` — review plan (only build this from real captured
  structure — a syllabus schedule, a chapter list actually stated by the
  course; never invent a week-by-week plan for a course that hasn't
  published one)
- `文件索引.md` — every file under `raw/files/` and `../textbooks/`, real
  filename, a working link, file size. Canvas file IDs make opaque folder
  names (`raw/files/75719989/`) — this is what makes them findable without
  opening `canvas-objects.json`. Regenerate from the actual directory
  listing (script it, don't hand-type) so it can't drift from reality.

## Ownership boundary (read this before editing any wiki file)

A wiki file can contain both agent-generated content and the student's own
handwritten notes in the same file. This skill must never destroy the
student's own writing.

Rule: every agent-generated section starts with an HTML comment marker and
ends with a matching close marker:

```markdown
<!-- agent-managed:start id="course_content-page-991" -->
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
- `wiki/course_content/` and `wiki/info/` each hold one digested note per
  raw object (sorted between them per the classification standard above),
  referencing the object's `source_snapshot` path so it's traceable back to
  the evidence it was written from.
- `wiki/textbook_breakdown/` is synthesis the agent builds up over time as
  the student actually works through the textbook in `../textbooks/` —
  chapter/section notes, not a summary of a raw Canvas object. Seed a
  `目录.md` index page from whatever coverage/chapter structure the course
  itself has actually stated (a syllabus content list, a schedule table) —
  never fabricate a textbook's table of contents from general knowledge.
  If nothing was stated, say so honestly rather than guessing. This folder
  and the marker discipline above matter most here, since it's the part
  most likely to also contain the student's own notes over time.

## Visual conventions

Every wiki file uses the templates in `../templates/`. Two things make them
worth using instead of writing prose from scratch:

- **YAML frontmatter with a `tags` hierarchy** — `type/<template-type>`,
  `course/<course-slug>`. This is what makes the vault filterable/queryable
  in Obsidian (e.g. with the Dataview plugin), not just a pile of files.
- **Obsidian callouts** (`> [!abstract]`, `> [!tip]`, `> [!warning]`,
  `> [!info]`, `> [!question]`) instead of plain paragraphs for anything
  that's a summary, an action item, a risk, or an open question. A callout
  renders as a colored, iconed box in Obsidian — this is what actually
  fixes "the wiki looks like plain text with no visual hierarchy." Don't
  overuse them: one callout per idea, not one per sentence.
- **Wiki-links (`[[...]]`)** between `course_content`/`info`/
  `textbook_breakdown` pages instead of plain text mentions — this is what
  makes the vault navigable as a graph, not just a folder tree. A filename
  like `文件索引.md` or `目录.md` repeats across every course, so a
  cross-course link needs the full path (`[[CourseName/wiki/info/文件索引|文件索引]]`)
  to avoid Obsidian resolving it to the wrong course.

Use the emoji section headers already in the templates (📚 📌 🗂️ 🔗 🗓️ 🔥)
consistently — they're navigation aids in the Obsidian outline view, not
decoration.

## Reading actual page content, not just structure

When a Canvas module lists items (pages, external URLs, files), don't stop
at listing the module's item titles — open every page/external-URL item
and extract its actual text content into the normalized object's `content`
field before syncing to `raw/`. A module item entry with no real content
behind it is not useful for `wiki/course_content/` or `wiki/info/`.

Video and image content is never transcribed or described from the image
itself — keep only the URL (see the "媒体资源" section in
`source-summary.md`). If a page embeds a video, the raw snapshot's content
should still capture the surrounding text; only the media itself is
link-only.
