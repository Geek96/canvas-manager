<p align="center">
  <img src="https://img.shields.io/badge/AI_Agent-Skill-7C3AED?style=for-the-badge" alt="AI Agent Skill"/>
  <img src="https://img.shields.io/badge/version-0.3.1-10B981?style=for-the-badge" alt="Version 0.3.1"/>
  <img src="https://img.shields.io/github/license/Geek96/canvas-manager?style=for-the-badge&color=6B7280" alt="MIT License"/>
</p>

<h1 align="center">🎓 canvas-manager</h1>

<p align="center">
  <strong>一个 Claude Code skill，把 Canvas LMS 课程同步进按"学期 → 课程"组织的 Obsidian vault</strong>
  <br/>
  <code>Canvas → 原始证据 → 消化后的 wiki 笔记</code>
  <br/><br/>
  默认使用 <strong>CanvasManager Lite</strong>——不需要 Canvas API token
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>简体中文</strong>
</p>

---

## ✨ 特性

- **两种读取 Canvas 的方式** —— `canvas-manager-lite` 通过 `opencli` 驱动你自己已登录的浏览器（默认，不需要 API token）；`canvas-manager` 在你学校允许学生申请 API token 的情况下对接 Canvas MCP server
- **证据优先的 vault** —— `raw/` 保存每个对象未经编辑的 Canvas 快照；`wiki/` 保存基于这些快照消化出来的笔记，绝不反过来
- **幂等、按内容哈希去重的同步** —— Canvas 上没有变化的情况下重新跑一次同步是空操作；一个 Python 引擎（仅用标准库，带单元测试）负责 diff/manifest 状态管理，这一步不留给 agent 自己判断
- **绝不静默覆盖** —— 一个可能是你已有文件新版本的文件会被标记为 `needs_confirmation`，不会自动替换
- **Agent 管理区域标记规则** —— 本 skill 只会触碰它自己生成的那部分 wiki 文件内容；同一文件里你自己手写的笔记永远不会被碰
- **原生 Obsidian 输出** —— YAML frontmatter、`> [!callouts]`、`[[wiki-links]]`——不需要任何 Obsidian 插件，本 skill 直接把普通文件写进你的 vault 文件夹
- **只管证据，不管综合汇总** —— 每个原始对象对应一份消化后的摘要，仅此而已；如果需要有截止日期意识的作业总览、公告时间线，或者给 PlanVault 用的交接文件（基于本 skill 的证据构建），见另一个独立的 [`course-manager`](https://github.com/Geek96/course-manager) skill

---

## 📦 安装

这是一个 Claude Code 插件/skill。克隆或安装它，然后让 Claude Code 指向和你的 Canvas 访问方式匹配的那个变体（下面的[依赖](#-依赖与前置条件)部分说明每个变体真正跑起来之前分别需要什么）。

```bash
npx skills add Geek96/canvas-manager
```

或者直接克隆：

```bash
git clone https://github.com/Geek96/canvas-manager.git
```

装好之后两个 skill 都会通过 `.claude-plugin/plugin.json` 自动注册。插件里两个变体都有——你只需要为你实际要用的那一个配好依赖。

---

## 🔧 依赖与前置条件

> **两个变体都需要**——Python 3（仅用标准库，不用 `pip install` 任何东西）和一个 Obsidian vault 文件夹（Obsidian 这个 App 本身是可选的——本 skill 直接把普通 Markdown 文件写到磁盘上，消费这些文件不需要任何 Obsidian 插件或 API）。

### CanvasManager Lite（默认——如果你学校屏蔽了学生自助申请 API token，用这个）

```
☐ opencli            ← 浏览器桥接，复用你已登录的 Canvas 会话
☐ 已登录 Canvas        ← 在 opencli 桥接的同一个浏览器 profile 里
```

**1. 安装 `opencli`**

> 提供的能力：驱动一个真实的、已登录的浏览器标签页，让本 skill 能像你自己一样读取 Canvas 页面，完全不需要任何 API 访问权限。

```bash
npm install -g @jackwener/opencli
```

如果光装 npm 包在你的平台上还不够用，完整安装指南（它需要的浏览器扩展、支持的浏览器等）见 [github.com/jackwener/OpenCLI](https://github.com/jackwener/OpenCLI)。

**2. 确认桥接已连接**

```bash
opencli doctor
```

应该显示 daemon 正在运行、浏览器扩展已连接。如果没有，在让 agent 同步任何东西之前，按上面 `opencli` 的文档（重新）安装/重连扩展。

**3. 确认你已登录 Canvas**

在 opencli 桥接的那同一个浏览器 profile 里打开你学校的 Canvas 主页（`https://{你的学校}.instructure.com/`），确认显示的是真实的个人化内容（待办列表、成绩链接之类）——而不是登录页。`opencli` 复用的是这个会话，它不会替你登录。

不需要 Canvas API token，不需要 MCP server，不需要 Obsidian 插件——这是依赖最少的路径，也是默认应该走的那条。

### 完整版 CanvasManager（仅当你学校允许自助申请 API token 时）

```
☐ Canvas API token   ← 从你学校的 Canvas 账户设置里生成
☐ Canvas MCP server   ← 连接到 Claude Code，用这个 token 配置好
```

**1. 获取 Canvas API token**——Canvas → Account → Settings → **New Access Token**。很多学校（包括 Georgia Tech）对学生禁用了这个功能；如果你学校也是，改用上面的 CanvasManager Lite。

**2. 连接一个 Canvas MCP server**——任何能把 Canvas 的课程/作业/公告/模块/页面接口暴露给 Claude Code 的 MCP server 都行，比如 [vishalsachdev/canvas-mcp](https://github.com/vishalsachdev/canvas-mcp)。按那个 server 自己的配置说明，用你的 token 配置它。

多花这份配置力气换来的：`raw/` 下每个对象保留完整的带时间戳历史，而不是 Lite 那种只保留最新版本的存储方式。

---

## 🧩 Skill 总览

```
┌───────────────────────────────────────────────────────────────┐
│                       canvas-manager (插件)                     │
│                                                                 │
│   canvas-manager-lite（默认）         canvas-manager（完整版）    │
│   opencli 浏览器桥接                   Canvas MCP server         │
│   不需要 API token                    需要学生 API token         │
│           │                                   │                │
│           └───────────────┬───────────────────┘                │
│                            ▼                                   │
│                 共享的 vault 结构                                │
│         raw/（证据）→ wiki/（消化后的笔记）                        │
│                            │                                   │
│                            ▼                                   │
│      可选：course-manager（独立 skill）→ wiki/综合/               │
│                     → PlanVault（独立 skill）                    │
└───────────────────────────────────────────────────────────────┘
```

| Skill | 做什么 | 需要什么 |
|-------|-------------|-------|
| **`canvas-manager-lite`** | 通过浏览器桥接同步——从这个开始 | `opencli`、一个已登录的浏览器 |
| `canvas-manager` | 通过 Canvas API/MCP 同步——保留完整历史 | Canvas API token、一个 Canvas MCP server |

---

## 📖 示例工作流

### 首次设置

```
> 帮我给 2026 秋季学期设置 CanvasManager
```

Agent 会问你 vault 根目录、学期名称，以及要追踪哪些课程（默认按"课程代码 - 课程名"命名目录，可改）。

### 日常同步

```
> 同步一下我的 Canvas 课程
```

读取每门被追踪课程的作业/公告/页面/模块，和 `raw/` 里已有的内容做 diff，只为真正变化的部分更新 `wiki/` 笔记。

### 定期同步（可选）

首次设置完成后，可以让 agent 通过 Claude Code 的 `/schedule` skill 设置轻量（每天两次）和深度（每周一次）同步——CanvasManager 自己不会安排定期任务。

---

## 📁 项目结构

```text
canvas-manager/
├── skills/
│   ├── canvas-manager-lite/          # 默认：opencli 浏览器桥接
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/sync_lite.py, files.py
│   └── canvas-manager/                # 完整版：Canvas API/MCP
│       ├── SKILL.md
│       ├── references/                # vault 结构、对象模型、
│       │                              # wiki 创作规则（两个变体共用）
│       ├── templates/                 # 共用的 wiki 模板
│       └── scripts/sync.py, manifest.py, snapshot.py
├── tests/                             # 29 个单元测试，用标准库 unittest
├── .claude-plugin/plugin.json
└── README.md
```

---

## 可选的 course-manager 集成

本 skill 有意止步于原始证据和按对象的摘要——没有作业总览、没有公告时间线、没有考试/截止日期表、没有 PlanVault 交接文件。如果需要这些，把 [`course-manager`](https://github.com/Geek96/course-manager) 和本 skill 一起装上：它只读 `raw/`、`wiki/course_content/`、`wiki/info/`，在 `wiki/综合/` 里构建那些有截止日期意识的视图，外加一份合并安全的暂存文件供 PlanVault 这类每日规划工具使用。不是必需的——没有它 CanvasManager 本身完全能正常工作，只是没有任何跨对象的综合汇总。

## 可选的 textbook-cracking 集成

如果某门课在 `textbooks/` 文件夹里放了真实的教材/读本，[`textbook-cracking`](https://github.com/Geek96/textbook-cracking)（一个独立的 skill，安装方式和这个一样）会构建出 `wiki/textbook_breakdown/`——章节摘要、概念页，以及内容模型专属的详情页（数学的证明、CS 的实操案例研究、原始文献读本的文献条目）——用的是真正的保真度规则，而不是临时拼凑的摘要。它已经知道，检测到是由 CanvasManager 管理的课程时，要把输出嵌套到这个仓库的 `wiki/textbook_breakdown/` 文件夹下，所以两者组合使用不会冲突。不是必需的——没有它 CanvasManager 也能正常工作，只是教材处理会更轻量一些。

## CourseOS

本 skill 在 [CourseOS](https://github.com/Geek96/course-manager) 里承担**证据驱动（Evidence Driver）**角色（见该仓库的 `FRAMEWORK.md`）——这是把 Canvas 转换成 `course-manager` 和 `textbook-cracking` 所依赖的 `raw/`+`wiki/course_content/`+`wiki/info/` 结构的必需组件。任何能产出同样结构的工具（定义见 `course-manager` 的 `references/canvas-manager-integration.md`）都可以顶替这个角色——`canvas-manager` 和 `canvas-manager-lite` 本身就已经是这个角色的两种可互换实现。这里的一切都不依赖于身处 CourseOS 之中；另外两个 skill 是可选的附加组件，不是必需项。

---

## Development

```bash
python3 -m unittest discover -s tests -v
```

零外部依赖——只用 Python 3 标准库。

---

## 📄 License

MIT © [Geek96](https://github.com/Geek96)
