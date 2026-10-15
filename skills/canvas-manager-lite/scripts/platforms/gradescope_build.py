"""Turn gradescope_table.js output into one `gradescope` text object.
usage: gradescope_build.py <table.json> <canvas_course_id> <gradescope_course_id> <out.json>"""
import json,sys
if len(sys.argv)!=5: sys.exit(__doc__),re
from datetime import datetime
src,cid,gid,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
d=json.load(open(src))
def fmt(dt): return datetime.strptime(dt,"%Y-%m-%d %H:%M:%S %z").astimezone().strftime("%Y-%m-%d %H:%M")
rows=["| 作业 | 发布 | 截止 | 迟交截止 | 状态 | 得分 |","|---|---|---|---|---|---|"]
for r in d["rows"]:
    rel=[t for t in r["times"] if "release" in t["cls"]]
    due=[t for t in r["times"] if "dueDate" in t["cls"] and not t["txt"].startswith("Late")]
    late=[t for t in r["times"] if t["txt"].startswith("Late")]
    st=r["status"]; score=""
    m=re.match(r"^([\d.]+)\s*/\s*([\d.]+)$",st)
    if m: score=f"{float(m.group(1)):g}/{float(m.group(2)):g}"; lab="已批改"
    elif st.startswith("Submitted"): lab="已交"
    elif st.startswith("No Submission"): lab="未交"
    else: lab=st
    rows.append(f"| {r['name']} | {fmt(rel[0]['dt'])[:10] if rel else ''} | {fmt(due[0]['dt']) if due else ''} | {fmt(late[0]['dt']) if late else ''} | {lab} | {score} |")
obj=[{"canvas_type":"gradescope","canvas_id":gid,"course_id":cid,"title":"Gradescope assignments",
      "updated_at_canvas":datetime.now().isoformat(timespec="seconds"),"source_url":f"https://www.gradescope.com/courses/{gid}",
      "content":"\n".join(rows)}]
json.dump(obj,open(out,"w"),ensure_ascii=False,indent=1); print(obj[0]["content"])
