---
title: "文件索引"
type: file-index
course: "{{course_name}}"
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
tags:
  - type/file-index
  - course/{{course-slug}}
---

# 📎 文件索引

> [!abstract] 用途
> 本页把老师上传的可读资料映射成人能看懂的文件名和可点击链接——`readings/` 里是每次同步时从 vault 外的 raw 证据库提取的人类可读副本（`{模块}_{标题}.pdf`），不用去翻 `canvas-objects.json` 才能找到某个文件。这里只是索引，不改动原文件。

{{生成方式：脚本读 readings/* 和 ../textbooks/* 的实际目录列表，逐条生成表格行，不要手打——手打的清单会跟实际文件脱节。}}

## 📖 教材

| 文件 | 链接 | 大小 |
|---|---|---|
| {{filename}} | [[../../textbooks/{{filename}}\|打开]] | {{size}} |

{{没有教材文件就删掉这一节}}

## 📄 课程资料

| 文件 | 链接 | 大小 |
|---|---|---|
| {{filename}} | [[../readings/{{filename}}\|打开]] | {{size}} |

{{没有课程资料就写"本课程截至本次同步没有老师上传的可读资料"}}