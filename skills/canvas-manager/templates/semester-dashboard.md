---
title: "{{semester}} 学期总览"
type: semester-dashboard
semester: "{{semester}}"
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
tags:
  - type/semester-dashboard
---

# 🗓️ {{semester}} 学期总览

> [!abstract] Overview
> 本学期共 **{{N}} 门课**。最近一次同步：{{YYYY-MM-DD}}

---

## 📚 本学期课程

| 课程 | 近期 due | 备注 |
|---|---|---|
| [[{{course_name}}/课程总览\|{{course_name}}]] | {{due_count}} | |

## 🔥 本周关注

<!-- agent-managed:start id="weekly-focus" -->
{{Weekly Digest 生成的内容——按 due date 优先级排的重点，不是按"哪些资源被更新"}}
<!-- agent-managed:end -->

---

> [!tip] Dataview（可选）
> 如果装了 Dataview 插件，可以在这里聚合所有课程的 `综合/作业总览.md`，做一个跨课程的 due date 视图。
