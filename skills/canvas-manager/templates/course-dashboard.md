---
title: "{{course_name}}"
type: course-dashboard
course: "{{course_name}}"
semester: "{{semester}}"
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
tags:
  - type/course-dashboard
  - course/{{course-slug}}
---

# 📚 {{course_name}}

> [!abstract] 课程概况
> **Canvas**: {{course_url}}
> **学期**: {{semester}}
> {{一两句话说清楚这门课是什么、大概要做什么}}

---

## 📌 近期 Due

<!-- agent-managed:start id="upcoming-due" -->
| 作业 | 类型 | 状态 | Due |
|---|---|---|---|
| {{title}} | {{type}} | {{status}} | {{due_at}} |
<!-- agent-managed:end -->

## 🗂️ 模块

<!-- agent-managed:start id="modules-index" -->
- [[Module - {{module_name}}]]
<!-- agent-managed:end -->

## 🔗 资源索引

- [[作业总览]]
- [[公告时间线]]
- [[考试与截止日期]]
- [[课程复习计划]]

---

> [!tip] Dataview（可选）
> 如果这个 vault 装了 Dataview 插件，可以在这里加自动汇总查询，比如按 due_at 排序的作业列表。
