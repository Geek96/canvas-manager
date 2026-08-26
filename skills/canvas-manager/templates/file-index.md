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
> 本页把 `raw/files/` 里按 Canvas 内部 ID 存放的附件，映射成人能看懂的文件名和可点击链接——不用去翻 `canvas-objects.json` 才能找到某个文件。`raw/` 本身是只读证据层，这里只是索引，不改动原文件。

{{生成方式：脚本读 raw/files/*/* 和 ../textbooks/* 的实际目录列表，逐条生成表格行，不要手打——手打的清单会跟实际文件脱节。}}

## 📖 教材

| 文件 | 链接 | 大小 |
|---|---|---|
| {{filename}} | [[../../textbooks/{{filename}}\|打开]] | {{size}} |

{{没有教材文件就删掉这一节}}

## 📄 Canvas 附件

| 文件 | 链接 | 大小 |
|---|---|---|
| {{filename}} | [[raw/files/{{file_id}}/{{filename}}\|打开]] | {{size}} |

{{没有文件附件就写"本课程截至本次同步没有 Canvas 文件附件"}}
