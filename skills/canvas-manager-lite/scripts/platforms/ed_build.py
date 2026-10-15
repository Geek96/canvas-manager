"""Keep staff announcements / pinned posts (max 30) as `ed` text objects.
usage: ed_build.py <threads.json> <canvas_course_id> <ed_course_id> <out.json>"""
import json,sys
if len(sys.argv)!=5: sys.exit(__doc__)
src,cid,edc,out=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
d=json.load(open(src))
roles={'admin':'教师/管理员','staff':'助教','tutor':'助教','mentor':'助教'}
sel=[t for t in d if t['role'] in roles and (t['type']=='announcement' or t['pinned'])][:30]
objs=[{"canvas_type":"ed","canvas_id":t['number'],"course_id":cid,"title":t['title'],"updated_at_canvas":t['created'],
       "source_url":f"https://edstem.org/us/courses/{edc}/discussion/{t['id']}",
       "content":f"帖子：{t['title']}\n作者：{t['author']}（{roles[t['role']]}）\n类型：{t['type']}{'（置顶）' if t['pinned'] else ''} · {t['cat']}{(' – '+t['sub']) if t['sub'] else ''}\n发布于：{t['created']}\n\n{(t['doc'] or '').strip()}"} for t in sel]
json.dump(objs,open(out,'w'),ensure_ascii=False,indent=1); print(len(objs))
