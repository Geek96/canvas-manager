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
- **Wiki-links (`[[...]]`)** between `资料摘要`/`概念`/`主题`/`综合` pages
  instead of plain text mentions — this is what makes the vault navigable
  as a graph, not just a folder tree.

Use the emoji section headers already in the templates (📚 📌 🗂️ 🔗 🗓️ 🔥)
consistently — they're navigation aids in the Obsidian outline view, not
decoration.

## Reading actual page content, not just structure

When a Canvas module lists items (pages, external URLs, files), don't stop
at listing the module's item titles — open every page/external-URL item
and extract its actual text content into the normalized object's `content`
field before syncing to `raw/`. A module item entry with no real content
behind it is not useful for `wiki/资料摘要/`.

Video and image content is never transcribed or described from the image
itself — keep only the URL (see the "媒体资源" section in
`source-summary.md`). If a page embeds a video, the raw snapshot's content
should still capture the surrounding text; only the media itself is
link-only.
