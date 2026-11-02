# claude-mem：给 AI 编程助手加长期记忆

- 原项目：thedotmack/claude-mem
- 原项目链接：https://github.com/thedotmack/claude-mem
- 榜单：日榜 2026-11-02 第 1 名
- 翻译日期：2026-11-02
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-02 核对）：Star 109,985，Fork 9,601，创建于 2025-08-31

## 一句话介绍

给 Claude Code 这类 AI 编程助手加一个长期记忆：它在每次会话里做了什么都会被记下来、压缩成摘要，下次开新会话时再把相关上下文喂回去，换会话也不丢项目进度。

## 适合谁

- 天天用 Claude Code、Codex、OpenCode、Cursor、Copilot 这类 AI 编程工具写代码的人
- 一个项目要聊很多轮、经常关掉重开会话的人
- 想让 AI 记得以前踩过的坑、定过的方案，不用每轮重新讲一遍的人

## 它解决什么问题

- AI 编程助手换个会话就失忆：以前讨论过的决定、修过的 bug、项目的来龙去脉全没了。
- 靠人手动写文档同步上下文又累又容易漏。
- 记忆塞太多会烧 token，塞太少又想不起来。

claude-mem 的做法是自动记录、AI 压缩、分层取用：只把当下最相关的记忆拿出来，不是一股脑全塞进上下文。

## README 翻译（核心部分）

原文标题是 Persistent memory compression system built for Claude Code，意思是为 Claude Code 打造的持久记忆压缩系统。

原文核心说法翻译如下：

> Claude-Mem 能无缝保留跨会话的上下文。它会自动记录工具使用的观察结果，生成语义摘要，并在以后的会话里提供给 AI 使用。这样即使会话结束或重新连接，Claude 也能保持对项目知识的连续性。

支持的工具包括 Claude Code、OpenClaw、Codex、Gemini、Hermes、Copilot、OpenCode 等。

主要功能（原文 Key Features 翻译）：

- 持久记忆：上下文能跨会话保留。
- 渐进披露：分层取回记忆，能看到 token 花费。
- 智能搜索（默认）：用三步 mem-search 技能查询项目历史。
- 本地 My Work：实时请求、进度、人工交接和已保存的审核队列，在启动时打印的 worker 地址上查看。
- TeamBrain：可选的共享工作区，团队成员各自决定分享什么，个人请求和审核笔记不共享。
- Claude Desktop Skill：可以在 Claude Desktop 对话里搜索记忆。
- 隐私控制：用 `<private>` 标签可以把敏感内容排除在存储之外。
- 截图（可选，默认关闭）：工具截图的转换副本保存在 `~/.claude-mem/media-v1/`，只有开启 Cloud Sync 时才上传到 cmem.ai，只有另外开启图片推理时才发给观察模型。
- 上下文配置：可以精细控制注入什么上下文。
- 自动运行：不需要手动干预。
- 引用：可以通过 worker API 或网页查看器，用 ID 引用过去的观察记录。

工作原理（原文 How It Works 翻译），核心有 6 个部件：

1. 生命周期钩子：SessionStart、UserPromptSubmit、PreToolUse、PostToolUse、Stop、SessionEnd，每个钩子就是一条 `claude-mem hook claude-code <event>` 命令。
2. 智能安装：带缓存的依赖检查器。
3. Worker 服务：本地 HTTP API，带网页查看器和搜索接口，由 Bun 管理。
4. SQLite 数据库：存会话、观察记录和摘要。
5. mem-search 技能：用自然语言查询，渐进披露。
6. Chroma 向量数据库：语义搜索加关键词搜索的混合检索。

MCP 搜索工具（原文 MCP Search Tools 翻译）：提供 4 个 MCP 工具，走省 token 的三层工作流：

1. `search`：先拿紧凑索引和 ID，每条结果约 50-100 token。
2. `timeline`：看感兴趣结果周围的时间线上下文。
3. `get_observations`：只对筛选后的 ID 取完整详情，每条约 500-1000 token。
4. 这样先筛后取，原文说能省约 10 倍 token。

另外 1 个工具没有在正文里单独列出用法，原文只说提供 4 个 MCP 工具，请以官方文档为准。

系统要求（原文 System Requirements）：Node.js 20.0.0 或更高、最新版 Claude Code（支持插件）、Bun（缺了会自动装）、uv（向量搜索用的 Python 包管理器，缺了会自动装）、SQLite 3（已打包）。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。原项目文档站是 docs.claude-mem.ai。

### 方式一：一条命令安装（推荐）

```bash
npx claude-mem install
```

安装器先把东西装好，然后会让你在浏览器里登录 claude-mem（邮箱魔法链接，不用绑卡）。登录后会给你发一个记忆密钥，解锁 claude-mem 观察器，带 30 天免费试用。试用期内记忆不走你的套餐额度，原文说最多能多出 100% 的用量。试用结束后如果不订阅，会自动回落到你的 Anthropic 套餐。登录后你再选记忆提供方：claude-mem 观察器、你自己的 OpenRouter 或 Gemini 密钥，或者你的 Anthropic 套餐。

不想登录也可以跳过，原文给了三种办法：传明确的 `--provider` 参数、设 `CLAUDE_MEM_ONLINE_OPTIN=false`，或者在 CI / 非交互 shell 里运行，安装器会直接装完不做账号交互。

装完重启 Claude Code，之前会话的上下文会自动出现在新会话里。

### 方式二：按工具安装

只用 OpenCode（1.3.4 或更高版本）：

```bash
npx claude-mem install --ide opencode
```

装完重启 OpenCode。

用 T3 Code（Codex 和 Claude Code 提供方）：

```bash
npx claude-mem install --ide t3code
```

安装器会自动发现 T3 Code 已启用的提供方，注册原生插件，支持 T3 管理的 Codex。装完重启 T3 Code，提示信任钩子时点信任，再开新对话。

用 Antigravity CLI、OMP（Oh My Pi）、Pi 原生扩展或 DeepSeek Harness 插件：

```bash
npx claude-mem install --ide antigravity
npx claude-mem install --ide omp
npx claude-mem install --ide pi
npx claude-mem install --ide dsh --dsh-profile tui
```

用 Grok Bot：

```bash
npx claude-mem install --ide grok-bot
```

Grok Bot 没有宿主钩子，所以是监听聊天日志文件。默认是 CMEM Pro 托管记忆，本地观察器是可选的，加 `--provider host` 才用本地。

### 方式三：从 Claude Code 插件市场安装

在 Claude Code 里依次输入：

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

装完重启 Claude Code。

### 方式四：OpenClaw 网关

在 OpenClaw 网关上装成持久记忆插件，一条命令：

```bash
curl -fsSL https://install.cmem.ai/openclaw.sh | bash
```

安装器会处理依赖、插件配置、AI 提供方配置、worker 启动，还能选接 Telegram、Discord、Slack 的实时观察推送。

## 配置说明

- 配置文件在 `~/.claude-mem/settings.json`，第一次运行时自动生成默认值。可以在里面配 AI 模型、worker 端口、数据目录、日志级别和上下文注入设置。
- 模式和语言：用 `CLAUDE_MEM_MODE` 设置，控制工作流行为和生成观察记录用的语言。中文模式是 `code--zh`，已经内置，不用另外装插件。改法是编辑 `~/.claude-mem/settings.json`，写上：

```json
{
  "CLAUDE_MEM_MODE": "code--zh"
}
```

- 改完模式要重启 Claude Code 才生效。
- 想在 Claude Code 和 Codex 的 SessionStart 上下文里包含所有来源的观察记录，把 `"CLAUDE_MEM_SESSION_START_INCLUDE_ALL_SOURCES": "true"` 写进上面那个配置文件，或者在查看器设置里打开 Include all sources at session start。默认是 `false`，只取当前工具的记录。

## 注意事项

- 注意别装错：原文明确提醒，`npm install -g claude-mem` 只装 SDK / 库，不会注册插件钩子，也不会装 worker 服务。一定要用 `npx claude-mem install` 或上面插件市场那两条命令来装。
- Windows 用户注意：如果报错 `npm : The term 'npm' is not recognized`，先装最新版 Node.js 并加进 PATH，重启终端再装。钩子不需要 Git Bash。安装器会把启动器放在 `%LOCALAPPDATA%\claude-mem\bin\claude-mem.exe` 并加进用户 Path，装完重启终端或 IDE。如果钩子报 `Executable not found in $PATH: "claude-mem"`，运行 `npx claude-mem doctor` 排查。
- 隐私：不想被记录的内容用 `<private>` 标签包起来。截图默认关闭，开启前先确认同步和图片推理的开关。
- 费用：30 天免费试用到期后不订阅会自动回落到 Anthropic 套餐，订阅前先确认自己的套餐额度和价格。
- 原项目 README 自带中文版链接，本文是在此基础上按 README 整理的部署步骤，细节以原项目最新文档为准。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/thedotmack/claude-mem
- 原 README：https://github.com/thedotmack/claude-mem#readme
- 官方文档：https://docs.claude-mem.ai

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 Apache-2.0。
