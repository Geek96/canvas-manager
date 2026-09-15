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

## 🗂️ 模块

<!-- agent-managed:start id="modules-index" -->
- [[Module - {{module_name}}]]
<!-- agent-managed:end -->

## 🔗 资源索引

- [[文件索引]]

{{如果装了 course-manager skill 并且已经跑过，取消下面的注释：
- [[综合/作业总览|作业总览]]
- [[综合/公告时间线|公告时间线]]
- [[综合/考试与截止日期|考试与截止日期]]
- [[综合/课程复习计划|课程复习计划]]
这些不是 canvas-manager 自己生成的，见 references/vault-structure.md 里
wiki/综合/ 的说明。}}

---

> [!tip] Dataview（可选）
> 如果这个 vault 装了 Dataview 插件，可以在这里加自动汇总查询；没装完全不影响这份 dashboard 本身的可用性。
