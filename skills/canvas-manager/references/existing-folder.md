# When the chosen folder already has the student's own structure

Shared by both variants. Runs at first-time initialization, right after
the student names the vault root and before anything is created. Many
students point the skill at a folder they already use — an Obsidian vault
with their own course folders, a notes folder, a downloads dump. Creating
the standard skeleton on top of that without asking leaves two parallel
structures and makes the student feel their work was taken over.

## 1. Look before creating anything

List the chosen folder (top level, and one level down for folders that look
like courses or semesters). It counts as **the student's own structure**
when it contains anything this skill didn't create:

- any non-hidden file or folder, other than a previous CanvasManager /
  CourseOS skeleton (recognizable by `courseos.json`, `.courseos/`, a
  `{Semester}.data/` sibling with `raw/_manifest/canvas-objects.json`, or
  `学期总览.md` / `课程总览.md` written from this skill's templates);
- an `.obsidian/` folder only (an empty vault) does **not** count — that's
  just Obsidian's settings; go ahead normally.

A previous CanvasManager skeleton isn't "the student's structure" — that's
a re-initialization; follow the normal rules for existing course
directories instead.

## 2. Show what's there, then offer three choices

Summarize in two or three lines what you found (how many top-level
folders/files, a few names, whether it's an Obsidian vault, anything that
looks like course or semester folders). Then ask one closed question (see
`interaction-style.md`, decision point 2b), with the guarantee stated up
front:

> This folder already has your own structure (12 folders, e.g. `Calculus/`,
> `Notes 2025/`, `Inbox/`; it's an Obsidian vault). Whatever you pick,
> **I won't delete, move, rename, or edit any of your existing files or
> folders** — I only add new ones. How should I set things up?
>
> 1. **Adapt to your structure** — keep your layout; I reuse your existing
>    course/semester folders where they match and add only what's missing.
> 2. **Use a different folder** — start fresh somewhere else (I'll suggest a
>    sibling folder, e.g. `…/2026Fall CourseOS/`) and leave this one alone.
> 3. **Add the standard layout here** — create the standard folders next to
>    yours in this folder; your files stay exactly where they are.

Wait for the answer. Don't pick a default silently, and don't start
creating folders while the question is open.

## 3. What each choice means

The guarantee holds for all three: existing files and folders are never
deleted, moved, renamed, or edited. Only new files and folders are added.
If any step would need to touch an existing file, stop and ask instead.

### 1. Adapt to your structure

- Match the student's folders to the tracked courses (and to the semester
  if there's a semester folder). Show the proposed mapping as a list —
  `Calculus/ → MATH-4317`, `CS stuff/ → CS-1331`, `(new) → HIST-2112` — and
  let them correct it before creating anything.
- Inside each matched course folder, add only the standard subfolders that
  are missing (`wiki/`, `readings/`, `submissions/`, `textbooks/`, and the
  `课程总览.md` note). If one of those names already exists and holds the
  student's own content, don't write into it: use a distinct name
  (`wiki (CourseOS)/`) and record the substitution.
- Record the mapping so every later sync and course-manager use the same
  paths: in the semester's `学期总览.md` course table (folder per course,
  plus a note for any renamed subfolder), and — when the student uses
  CourseOS — tell them to set each course's folder there too (`courseos.json`
  is CourseOS's file; don't write it yourself). The raw store still goes to
  the `{Semester}.data/` sibling outside the vault.
- In the course's `课程总览.md`, link to the student's existing notes for
  that course rather than copying them.

### 2. Use a different folder

- Suggest a sibling folder name, let the student confirm or type another,
  check that it's empty (or new), then initialize there normally. Nothing
  in the original folder is read again or touched.

### 3. Add the standard layout here

- Create the standard skeleton in the chosen folder, next to the student's
  folders. Where a standard name collides with an existing folder or file
  (e.g. they already have a `2026Fall/`), don't merge into it — ask for a
  distinct name or use a suffixed one (`2026Fall (CourseOS)/`) and say so.

## 4. Say what happened

After setup, list in a few lines what was created and where (and, for
choice 1, the final course→folder mapping), and repeat that none of the
student's existing files were changed.
