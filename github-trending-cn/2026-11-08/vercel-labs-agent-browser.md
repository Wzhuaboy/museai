# agent-browser：给 AI agent 用的浏览器自动化命令行工具

- 原项目：vercel-labs/agent-browser
- 原项目链接：https://github.com/vercel-labs/agent-browser
- 榜单：日榜 2026-11-08 第 1 名
- 翻译日期：2026-11-08
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-08 核对）：Star 46,520，Fork 3,188，创建于 2026-01-11，提交 816 次，Release 120 个

## 一句话介绍

agent-browser 是 Vercel Labs 出的原生 Rust 命令行工具，给 AI agent 一个能用一条条命令驱动的浏览器：打开页面、读成无障碍树、按元素编号操作，一步一个 shell 命令。

## 适合谁

- 写 AI agent、想让 agent 自己上网查资料、填表单、点按钮的人
- 用 Claude Code、Codex 这类编程 agent，需要浏览器能力的开发者
- 想把浏览器操作写进脚本、CI 里跑的人
- 受够了 Playwright/Puppeteer 那种"写一整段脚本才能跑"的重量级方案，想要轻量命令行的人

## 它解决什么问题

- AI agent 不会"看"网页：它需要的是结构化的文字，而不是像素。agent-browser 把页面读成紧凑的无障碍树文本，每个元素带一个编号（比如 `@e1`），agent 按编号操作，操作完再读一遍页面确认结果，如此循环。
- 浏览器操作不用写长脚本：浏览器在命令之间一直开着，每一步就是一次简短的 shell 调用，agent 一条命令做一步。
- 传统浏览器自动化要自己管浏览器生命周期、等页面加载、处理元素遮挡；agent-browser 把这些收进 CLI：点击目标被挡住、禁用、看不见时直接报错失败，而不是假装成功。

## README 翻译（核心部分）

### 这是什么

给 AI agent 的浏览器自动化：打开页面、读成无障碍树、从 shell 按元素操作。

agent-browser 是一个原生 Rust CLI，给 AI agent 一个可以一次一条命令驱动的浏览器。`snapshot` 把页面以紧凑文本返回，每个元素带一个编号，比如 `@e1`。agent 按编号操作，再读一遍页面检查结果，然后重复。浏览器在命令之间保持打开，所以每一步都是一次简短的 shell 调用。

### 安装

```bash
npm install -g agent-browser

agent-browser install           # 首次运行下载 Chrome for Testing
```

- **Homebrew：** `brew install agent-browser`，然后 `agent-browser install`。
- **Linux：** `agent-browser install --with-deps` 还会装浏览器的系统依赖库。
- **不安装：** `npx agent-browser open example.com`。

项目内安装、从源码构建、`upgrade` 和 `doctor` 在 Installation 文档里。

### 快速上手

```bash
agent-browser open example.com
agent-browser snapshot -i       # 只列可交互元素，每个带编号
agent-browser click @e1         # 对快照里的编号操作
agent-browser get url           # 检查结果
agent-browser close
```

`example.com` 的快照长这样：

```
- link "Learn more" [ref=e1]
```

注意：

- 编号描述的是快照那一刻的页面。导航或 DOM 变化后，用编号之前先重新拍快照。
- CSS 选择器、文本、XPath 和语义定位器也能用，比如 `agent-browser find role button click --name "Submit"`，见 Selectors 文档。
- 目标被隐藏、禁用、在视口外、或被别的元素（比如同意横幅）盖住时，点击会失败，而不是报成功。先把盖住的元素关掉，重新拍快照，再试一次。

完整演示在 quick start 文档里。

### 工作原理

CLI 把每条命令发给一个后台守护进程：第一条命令时启动，通过 Chrome DevTools Protocol 控制浏览器。每个 `--session` 有自己的守护进程和浏览器。默认情况下，守护进程在一小时没有命令后关闭无头浏览器并退出；配置了会话持久化时会先保存状态。

Chrome for Testing 是默认浏览器。也可以用 `--cdp` 或 `--auto-connect`（CDP 模式）连到正在运行的 Chrome，用 `--engine` 选 Lightpanda 或 Obscura 引擎，在 iOS 模拟器里驱动 Mobile Safari，或者用 Browserbase、Browserless、Browser Use、Kernel、AgentCore 这类云浏览器服务。

### 给 AI agent 用

CLI 自带和版本匹配的技能：

```bash
agent-browser skills get core                 # 核心循环、编号、等待和常用工作流
agent-browser skills get core --ref commands  # 单份参考，比如完整命令列表
agent-browser skills get core --full          # 再加完整命令参考和模板
agent-browser skills list                     # 专业技能：electron、slack、dogfood 等
```

从 skills.sh 把发现技能装进 agent 框架：

```bash
npx skills add vercel-labs/agent-browser
```

装好的技能只是一个薄壳，告诉 agent 去加载 `agent-browser skills get core`，所以指令永远和装好的 CLI 版本一致。或者在你的 `AGENTS.md` 里加这段：

```
Use `agent-browser` for browser automation. Before the first use, run
`agent-browser skills get core` and follow it.
```

MCP 客户端用 `agent-browser mcp`，通过 stdio 启动 MCP 服务器，见 MCP server 文档。

### 命令

跑 `agent-browser --help` 看完整列表，或 `agent-browser <命令> --help` 看单个命令。

| 分组 | 命令 | 文档 |
| --- | --- | --- |
| 导航与读取 | `open`、`back`、`forward`、`reload`、`read`、`snapshot`、`get`、`is` | Core、Snapshots |
| 交互 | `click`、`dblclick`、`fill`、`type`、`press`、`keyboard`、`hover`、`focus`、`select`、`check`、`uncheck`、`scroll`、`drag`、`upload`、`mouse`、`find` | Core、Find elements |
| 等待 | `wait` | Wait |
| 截图与保存 | `screenshot`、`pdf`、`record`、`download`、`diff` | Recording、Diffing、Files |
| 页面与网络状态 | `cookies`、`storage`、`network`、`set`、`clipboard`、`eval`、`pushstate` | Network、Settings |
| 标签页、框架与弹窗 | `tab`、`frame`、`dialog` | Tabs and frames |
| 调试与性能 | `console`、`errors`、`highlight`、`inspect`、`trace`、`profiler`、`vitals`、`react`、`a11y` | Debugging、Profiler、React |
| 会话与认证 | `session`、`state`、`auth`、`profiles`、`confirm`、`deny` | Sessions、Security |
| Agent 与集成 | `skills`、`mcp`、`webmcp`、`flow`、`chat`、`batch`、`plugin` | Skills、WebMCP、Plugins |
| 观察 | `stream`、`dashboard` | Streaming、Dashboard |
| 安装设置 | `install`、`upgrade`、`doctor`、`connect`、`close` | Installation |

标志、环境变量和 `agent-browser.json` 在 Configuration 文档里。

### 支持的平台

原生二进制覆盖 macOS（ARM64、x64）、Linux（ARM64、x64，glibc 和 musl）、Windows（x64），npm 包会按主机自动选对二进制。

### 从源码开发

从源码构建需要 Node.js 24 或更高、pnpm 11 或更高，以及 Rust：

```bash
pnpm install
pnpm build:source               # 构建仪表盘和原生 CLI
pnpm link --global
agent-browser install
```

在 `cli/` 里跑 Rust 检查：

```bash
cargo fmt -- --check
cargo clippy
cargo test
cargo test e2e -- --ignored --test-threads=1   # 启动真实的无头 Chrome
```

AGENTS.md 里列了每次改动要更新哪些文件、文档检查和发布流程。

### 文档

- agent-browser.dev：介绍、指南和参考
- Commands 和 Configuration
- Security：认证保险库、域名白名单、操作策略和内容边界
- Next.js、Vercel 和 eve：在 Vercel Sandbox 和 eve agent 里跑 agent-browser
- Changelog

## 中文部署操作指南

### 方式一：npm 全局安装（推荐）

```bash
npm install -g agent-browser
agent-browser install
```

前置要求：Node.js（装 npm 包用）；`agent-browser install` 会下载 Chrome for Testing。

### 方式二：Homebrew（macOS）

```bash
brew install agent-browser
agent-browser install
```

### 方式三：不安装，直接用

```bash
npx agent-browser open example.com
```

### 方式四：从源码构建

```bash
pnpm install
pnpm build:source
pnpm link --global
agent-browser install
```

前置要求：Node.js 24+、pnpm 11+、Rust。

### 装完先跑一遍

```bash
agent-browser open example.com
agent-browser snapshot -i
agent-browser close
```

## 配置说明

- 默认用 Chrome for Testing，不用自己装 Chrome；也可以用 `--cdp` 连已在运行的 Chrome。
- 每个 `--session` 独立一个守护进程和浏览器；默认一小时无命令自动关闭，配了会话持久化会先保存状态。
- 想让 agent 每次都按同一套用法走，在 `AGENTS.md` 里加 README 给的那段话，或跑 `npx skills add vercel-labs/agent-browser` 装发现技能。
- MCP 客户端（比如 Claude Desktop）用 `agent-browser mcp` 起 stdio MCP 服务器。

## 注意事项

- 编号只在快照那一刻有效：页面变了就重新拍快照再操作，别拿旧编号点新页面。
- 点击被挡住、禁用、看不见的目标会直接失败，不是假成功；先处理遮挡再重试。
- 安全相关（认证保险库、域名白名单、操作策略）都在 Security 文档里，跑自动化之前先看一眼，别让 agent 在不该点的站上乱点。
- 注意别和同组织的 vercel-labs/agent-desktop 混淆：那是让 AI agent 直接操作桌面应用的，11 月 3 日已翻译过；这个是浏览器自动化命令行工具。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/vercel-labs/agent-browser
- 原 README：https://github.com/vercel-labs/agent-browser#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
