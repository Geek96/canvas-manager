"""Turn a Canvas API dump (fetched through the logged-in browser) into
sync_lite.py inputs, reusing the previous snapshot body when Canvas'
updated_at hasn't changed (so only real changes show up as updates)."""
import json, re, sys, html
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime, timezone

import os

# Canvas base URL, e.g. https://gatech.instructure.com — from --base or $CANVAS_BASE.
BASE = os.environ.get("CANVAS_BASE", "").rstrip("/")


class H2T(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table", "ul", "ol", "blockquote", "hr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.href, self.atext = [], None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n\n#### ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag in ("td", "th"):
            self.out.append(" | ")
        elif tag == "br":
            self.out.append("\n")
        elif tag in self.BLOCK:
            self.out.append("\n\n")
        if tag == "a":
            self.href, self.atext = a.get("href"), []
        if tag == "img" and a.get("src"):
            self.out.append(f"[image: {a.get('alt') or ''}] ")
        if tag == "iframe" and a.get("src"):
            self.out.append(f"\n[embed: {a['src']}]\n")

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            text = "".join(self.atext).strip()
            href = self.href
            if href.startswith("/"):
                href = BASE + href
            self.out.append(f"{text} ({href})" if text and href and not href.startswith("#") else text)
            self.href = None
        elif tag in self.BLOCK:
            self.out.append("\n\n")

    def handle_data(self, data):
        if self.href is not None:
            self.atext.append(data)
        else:
            self.out.append(data)


def h2t(s):
    if not s:
        return ""
    p = H2T()
    p.feed(s)
    t = "".join(p.out).replace("\xa0", " ")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n[ \t]+(?=\S)", lambda m: "\n" if not m.group(0).strip(" \t\n") else m.group(0), t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def old_body(data_dir, key, manifest):
    e = manifest.get(key)
    if not e or not e.get("latest_snapshot"):
        return None
    p = data_dir / e["latest_snapshot"]
    if not p.exists():
        return None
    txt = p.read_text(encoding="utf-8")
    parts = txt.split("\n---\n", 1)
    if len(parts) < 2:
        return None
    body = parts[1]
    return body[1:] if body.startswith("\n") else body


def main():
    global BASE
    args = [a for a in sys.argv[1:] if not a.startswith("--base=")]
    for a in sys.argv[1:]:
        if a.startswith("--base="):
            BASE = a.split("=", 1)[1].rstrip("/")
    if len(args) != 3 or not BASE:
        sys.exit("usage: build_course.py <dump.json> <data-dir> <outdir> --base=https://{institution}.instructure.com  (or set CANVAS_BASE)")
    dump, data_dir, outdir = Path(args[0]), Path(args[1]), Path(args[2])
    outdir.mkdir(parents=True, exist_ok=True)
    d = json.loads(dump.read_text(encoding="utf-8"))
    if isinstance(d, str):
        d = json.loads(d)
    man_p = data_dir / "raw/_manifest/canvas-objects.json"
    manifest = json.loads(man_p.read_text(encoding="utf-8")) if man_p.exists() else {}
    course = d["course"]
    cid = course["id"]
    now = datetime.now().isoformat(timespec="seconds")
    report = {"course": course.get("course_code"), "new": [], "updated": [], "errors": {}}

    def emit(otype, ctype, oid, title, upd, url, content):
        key = f"{otype}/{oid}"
        prev = manifest.get(key)
        def fetched_after_upd():
            p = data_dir / prev.get("latest_snapshot", "")
            if not p.exists():
                return False
            m = re.search(r"^fetched_at: (\S+)$", p.read_text(encoding="utf-8"), re.M)
            if not m:
                return False
            fa = datetime.fromisoformat(m.group(1)).astimezone()
            return datetime.fromisoformat(upd.replace("Z", "+00:00")) <= fa
        if prev and upd and (prev.get("last_canvas_updated_at") == upd or fetched_after_upd()):
            ob = old_body(data_dir, key, manifest)
            if ob is not None:
                content = ob
        elif prev and not upd and otype in ("syllabus", "announcements", "discussions"):
            ob = old_body(data_dir, key, manifest)
            if ob is not None:
                import difflib
                norm = lambda s: re.sub(r"[^0-9A-Za-z]+", "", re.sub(r"\(https?://[^)]*\)", "", s))
                if difflib.SequenceMatcher(None, norm(ob), norm(content), autojunk=False).ratio() > 0.97:
                    content = ob
        elif prev and not upd and otype == "quizzes":
            ob = old_body(data_dir, key, manifest)
            if ob is not None and ob.split("\n")[:4] == content.split("\n")[:4]:
                content = ob
        if not prev:
            report["new"].append(f"{key} {title}")
        elif upd and prev.get("last_canvas_updated_at") != upd and content != old_body(data_dir, key, manifest):
            report["updated"].append(f"{key} {title}")
        return {"canvas_type": ctype, "canvas_id": oid, "course_id": cid, "title": title,
                "updated_at_canvas": upd or now, "source_url": url, "content": content}

    out = {}
    for k in ("assignments", "announcements", "discussions", "modules", "quizzes", "pages", "groups"):
        if isinstance(d.get(k), dict) and "error" in d[k]:
            report["errors"][k] = d[k]["error"]

    # assignments
    A = d["assignments"] if isinstance(d["assignments"], list) else []
    out["assignments"] = [emit("assignments", "assignment", a["id"], a["name"], a.get("updated_at"), a["html_url"],
        "\n".join([f"作业：{a['name']}", f"截止：{a.get('due_at') or '无'}", f"分值：{a.get('points_possible') if a.get('points_possible') is not None else ''}",
                   f"提交方式：{', '.join(a.get('submission_types') or [])}", f"开放：{a.get('unlock_at') or ''}",
                   f"关闭：{a.get('lock_at') or ''}", f"作业组：{a.get('assignment_group_id')}", "", h2t(a.get("description"))]).rstrip())
        for a in A]

    an = d["announcements"] if isinstance(d["announcements"], list) else []
    out["announcements"] = [emit("announcements", "announcement", t["id"], t["title"], t.get("posted_at"), t["html_url"],
        f"公告：{t['title']}\n发布于：{t.get('posted_at')}\n\n{h2t(t.get('message'))}") for t in an]

    ds = d["discussions"] if isinstance(d["discussions"], list) else []
    out["discussions"] = [emit("discussions", "discussion", t["id"], t["title"], t.get("posted_at"), t["html_url"],
        f"讨论：{t['title']}\n发布于：{t.get('posted_at')}\n截止：{(t.get('assignment') or {}).get('due_at') or '无'}\n\n{h2t(t.get('message'))}") for t in ds]

    ms = d["modules"] if isinstance(d["modules"], list) else []
    out["modules"] = []
    for m in ms:
        items = [{"title": i["title"], "type": i["type"], "content_id": i.get("content_id"), "url": i.get("html_url")} for i in m.get("items", [])]
        out["modules"].append(emit("modules", "module", m["id"], m["name"], None, f"{BASE}/courses/{cid}/modules#{m['id']}",
                                   json.dumps(items, ensure_ascii=False)))

    qs = d["quizzes"] if isinstance(d["quizzes"], list) else []
    out["quizzes"] = [emit("quizzes", "quiz", q["id"], q["title"], None, q["html_url"],
        f"测验：{q['title']}\n截止：{q.get('due_at') or '无'}\n分值：{q.get('points_possible')}\n题数：{q.get('question_count')}\n限时：{q.get('time_limit')}\n\n{h2t(q.get('description'))}".rstrip() + "\n")
        for q in qs] if qs else []

    # pages: match previous keys by source_url then title
    prev_pages = {k: v for k, v in manifest.items() if k.startswith("pages/")}
    by_url, by_title = {}, {}
    for k, v in prev_pages.items():
        ob = data_dir / v.get("latest_snapshot", "")
        if ob.exists():
            m = re.search(r"^source_url: (.+)$", ob.read_text(encoding="utf-8"), re.M)
            if m:
                by_url.setdefault(m.group(1).strip(), k.split("/", 1)[1])
        by_title.setdefault(v.get("title", "").strip(), []).append(k.split("/", 1)[1])
    used = set()
    out["pages"] = []
    for p in d.get("pages") or []:
        if not isinstance(p, dict) or "url" not in p:
            continue
        url = p.get("html_url") or f"{BASE}/courses/{cid}/pages/{p['url']}"
        oid = by_url.get(url)
        if not oid and f"pages/{p['page_id']}" in prev_pages:
            oid = str(p["page_id"])
        if not oid:
            cands = [x for x in by_title.get(p["title"].strip(), []) if x not in used]
            oid = cands[0] if cands else str(p["page_id"])
        if oid in used:
            continue
        used.add(oid)
        oid = int(oid)
        mod = p.get("_module")
        out["pages"].append(emit("pages", "page", oid, p["title"], p.get("updated_at"), url,
            f"页面：{p['title']}\n" + (f"所在模块：{mod}\n" if mod else "") + "\n" + h2t(p.get("body"))))
    # keep unmatched previous pages that we did not refetch (e.g. module page hidden) out: they become missing
    report["pages_unmatched_prev"] = [k for k in prev_pages if int(k.split('/')[1]) not in {o['canvas_id'] for o in out['pages']}]

    # syllabus: keep the existing key
    sk = [k for k in manifest if k.startswith("syllabus/")]
    if sk:
        sid = int(sk[0].split("/")[1])
        stitle = manifest[sk[0]].get("title")
        body = course.get("syllabus_body")
        if body:
            out["syllabus"] = [emit("syllabus", "syllabus", sid, stitle, None, f"{BASE}/courses/{cid}/assignments/syllabus",
                                    f"课程大纲（Syllabus 标签页）：{course.get('name')}\n\n{h2t(body)}")]
        elif d.get("front_page") and isinstance(d["front_page"], dict) and d["front_page"].get("body"):
            fp = d["front_page"]
            out["syllabus"] = [emit("syllabus", "syllabus", sid, stitle, fp.get("updated_at"), fp.get("html_url"),
                                    f"{stitle}\n\n{h2t(fp.get('body'))}")]

    # grades from per-assignment submission data (same data the Grades page renders)
    groups = {g["id"]: g["name"] for g in (d["groups"] if isinstance(d["groups"], list) else [])}
    rows = []
    nowdt = datetime.now(timezone.utc)
    for a in sorted(A, key=lambda a: (a.get("due_at") or "9999", a["name"])):
        s = a.get("submission") or {}
        st = s.get("workflow_state")
        due = a.get("due_at")
        if s.get("excused"):
            lab = "免交"
        elif s.get("missing"):
            lab = "缺交"
        elif s.get("late") and st in ("submitted", "graded", "pending_review"):
            lab = "迟交"
        elif s.get("submitted_at") or st in ("submitted", "pending_review"):
            lab = "已交"
        elif st == "graded" and s.get("score") is not None:
            lab = "已交" if s.get("submitted_at") else "已批改"
        else:
            past = due and datetime.fromisoformat(due.replace("Z", "+00:00")) < nowdt
            lab = "未交（已过截止）" if past else "未交"
        sc = s.get("score")
        pts = a.get("points_possible")
        score = f"{sc:g}/{pts:g}" if sc is not None and pts is not None else ""
        dl = ""
        if due:
            dl = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")
        rows.append(f"| {a['name']} | {dl} | {lab} | {score} | {groups.get(a.get('assignment_group_id'), '')} |")
    gcontent = "| 作业 | 截止 | 状态 | 得分 | 作业组 |\n|---|---|---|---|---|\n" + "\n".join(rows)
    gw = "\n".join(f"- {g['name']}：{g.get('group_weight')}%" for g in (d["groups"] if isinstance(d["groups"], list) else []))
    if gw:
        gcontent += "\n\n作业组权重（Canvas）：\n" + gw
    out["grades"] = [{"canvas_type": "grades", "canvas_id": cid, "course_id": cid, "title": "Grades",
                      "updated_at_canvas": now, "source_url": f"{BASE}/courses/{cid}/grades", "content": gcontent}]

    # files referenced by modules that aren't registered yet
    known = {k.split("/")[1] for k in manifest if k.startswith("files/")}
    report["new_files"] = sorted({(i.get("content_id"), i["title"]) for m in ms for i in m.get("items", [])
                                  if i["type"] == "File" and str(i.get("content_id")) not in known}, key=str)

    for k, v in out.items():
        if k in report["errors"] and not v:
            continue  # tab disabled / endpoint failed: don't mark everything missing
        (outdir / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
