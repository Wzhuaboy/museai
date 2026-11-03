# impeccable：给编程助手的设计词汇表

- 原项目：pbakaus/impeccable
- 原项目链接：https://github.com/pbakaus/impeccable
- 榜单：周榜 2026-11-03 第 3 名
- 翻译日期：2026-11-03
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-03 核对）：Star 100,428，Fork 5,934，创建于 2025-11-16

## 一句话介绍

给编程助手的一套设计品味规范：用 `polish`、`bolder` 这类有名字的命令指挥它改设计，用 `critique`、`audit` 评审它，在 AI 味的粗糙产物上线之前拦下来。

## 适合谁

- 天天让 Claude Code、Cursor、Codex 这类工具写前端界面的人
- 觉得 AI 生成的页面一眼假、千篇一律，想让它做出点品味的人
- 想给团队定一套“设计质检”标准、让 AI 出的活先过一遍审的人

## 它解决什么问题

- AI 做页面有固定套路：什么都用 Inter 字体、紫蓝渐变、卡片套卡片、彩底灰字、每个标题上面一个圆角图标。不给具体指导，问哪个模型、做哪个项目都长这样。
- 人话指挥不动它：“好看一点”“高级一点”太虚，agent 只能靠猜。
- 没人审：粗糙产物直接上线，等用户吐槽才发现。

impeccable 的做法是三件套：给想要的效果起名字（一条命令就是一个具体动作）、配一个评审员（打分加排优先级）、再加一个不用大模型的粗糙产物检测器。

## README 翻译（核心部分）

原文标题是 Impeccable，副标题是 The design vocabulary for your coding agent. Steer with `polish` and `bolder`, review with `critique` and `audit`, and catch AI slop before it ships.，意思是给编程助手的设计词汇表：用 `polish` 和 `bolder` 指挥，用 `critique` 和 `audit` 评审，在 AI 粗糙产物上线前拦住它。

从项目根目录开始：

```bash
npx impeccable install
```

装完重载你的编程工具，然后在 agent 里跑 `/impeccable init`（Codex 上是 `$impeccable init`）。

支持 Claude Code、Cursor、Codex CLI、GitHub Copilot、Devin、Replit Agent、Gemini CLI、Grok Build、OpenCode、Google Antigravity、Kiro、Trae、Rovo Dev、Qoder、Mistral Vibe、Pi、Hermes Agent、DeepSeek Harness 和 Veto。完整文档在 impeccable.style/docs。

原文给了一个同模型、同需求的对比：一个位于利古里亚海岸的 14 间客房家庭旅馆网站。不用 impeccable 时，出来的就是默认的“好看”：米色页面、细衬线标题加斜体点缀、药丸按钮、圆角卡片里的扁平矢量插画。用了之后，页面围绕一张图展开：夜里从海上看过去的房子、悬崖上的别墅，配紧凑的米色加朱红标题，底部还有一条月份条。

为什么需要它（原文 Why 翻译）：

- **给想要的东西起名字。**“让它亮眼一点”只能让 agent 瞎猜。`/impeccable bolder the pricing cards` 会加载一个专为这个动作写的 playbook，并指到一个具体目标上。
- **有个评审员。**`critique` 按可用性启发式给设计打分，并按优先级排出先修什么。`audit` 检查无障碍、性能、主题和响应式表现，问题按 P0（阻塞）到 P3（打磨）分级。
- **有个粗糙产物检测器。**62 条确定性规则，能标出上面那些典型特征，以及拥挤的内边距、跳过的标题这类质量问题。不用大模型，不用 API key。

impeccable 在已有的界面上最强：指着一个页面或组件反复改。新建页面它也能做，但难度更大，原文建议先看“新建页面”那篇文档。入门建议先挑一个组件：

```bash
/impeccable critique the pricing cards
```

工作原理（原文 How it works 翻译）：每个项目跑一次 `/impeccable init`。它读你的代码，只问它推断不出的东西（产品是给谁的、要做什么、有什么约束），然后写出 `PRODUCT.md`，之后每条命令都读它。跑 `/impeccable document` 可以把现有的视觉系统记进 `DESIGN.md`，让改动保持品牌一致。

然后说出命令加目标：

```bash
/impeccable critique the onboarding flow
/impeccable quieter the landing page
/impeccable polish settings
/impeccable harden checkout
```

也可以直接描述想要什么：`/impeccable redo this hero section`。目标越窄效果越好：一个小节认真审一遍，胜过整个页面粗粗扫一眼。常用命令可以用 `/impeccable pin audit` 固定成 `/audit` 快捷方式。

24 条命令（原文翻译）：

|  | 命令 |
| --- | --- |
| 指挥 | `bolder` 放大稳妥的设计 · `quieter` 收敛太吵的设计 · `distill` 删掉页面不需要的东西 · `colorize` 给灰界面上色 · `typeset` 修字体、层级和尺寸 · `layout` 修间距和节奏 · `animate` 加过渡和交互反馈 · `delight` 加个性 · `overdrive` 上着色器、弹簧物理和滚动驱动效果 |
| 评审 | `critique` 是打分制的 UX 评审 · `audit` 是技术质量报告 |
| 收尾 | `polish` 是上线前的最后一遍 · `harden` 覆盖报错、国际化、溢出和边界情况 · `clarify` 重写不清楚的文案 · `adapt` 处理屏幕尺寸和设备 · `optimize` 修加载和渲染性能 · `onboard` 设计首次使用流程和空状态 |
| 实时迭代 | `live` 在浏览器里选一个元素、循环换变体 · `generate` 不用手动选，直接给指定元素生成变体 |
| 规划和搭建 | `shape` 写代码前先规划 UX · `init` 写 `PRODUCT.md` · `document` 写 `DESIGN.md` · `extract` 把重复模式抽进设计系统 |

第 24 条 `craft` 是普通构建请求的旧别名，已废弃。只输 `/impeccable` 可以看到命令列表，每条命令在 impeccable.style/docs 都有自己的页面。Codex 上打开 `/skills` 或输 `$impeccable`。

实时模式（原文 Live mode 翻译）：`/impeccable live` 打开你正在跑的开发服务器并加一个浮层。选一个元素、挑一个方向，impeccable 就地热替换变体。接受一个，改动就写回源码。支持 Vite、Next、SvelteKit、Astro、Nuxt 和纯 HTML。

实时模式只改本地 checkout，不要往已部署的站点里注入，也不要为了让它工作而放宽生产环境的 CSP。用实时模式改文案时，会跑 `package.json` 里可选的 `impeccable:manual-edit-validate` 脚本，用的是你的权限，所以在不熟的仓库里用实时模式之前先审一下这个脚本。

检测器的三种运行方式（原文 Three ways to run the detector 翻译）：

**在你的 agent 里。**设计 hook 会扫描 agent 每次改的 UI 文件，在 agent 说做完之前把发现交回去。这是大部分粗糙产物被拦住的地方：没有 hook 的话，检测器只有在有人想起来时才跑。Claude Code、Cursor、Codex、GitHub Copilot、Grok Build 和 Hermes Agent 都支持，安装器会帮你装上。建议装上。

**在 CI 或终端里。**CLI 不需要 agent：

```bash
npx impeccable detect src/                   # 扫一个目录
npx impeccable detect https://example.com    # 扫一个渲染好的页面（用你装好的 Chrome 或 Edge）
npx impeccable detect --json .               # 机器可读的输出
npx impeccable detect --github src/          # GitHub Actions 标注
npx impeccable detect --list-rules           # 每条规则的 id 和描述
```

JSX、TSX 这类源文件只跑模式类规则。需要渲染后页面才能跑的规则（比如对比度太低、文字太小），要在扫 URL 时才跑，所以也要把 CLI 指到你的开发服务器上：`npx impeccable detect http://localhost:5173`。

退出码 `2` 表示有发现，`1` 表示某个目标扫不了。想让品牌字体处处放行：`npx impeccable ignores add-value overused-font Inter --reason "Brand font"`。想给单个文件关掉一条规则，加注释：`<!-- impeccable-disable overused-font: exported brand doc -->`。

**在浏览器里。**Chrome 扩展可以在任何在线页面上叠加同样的发现，不管是你自己的还是别人的。

安装（原文 Installation 翻译）：

```bash
npx impeccable install
```

安装器会检测你的编程工具，问是装给这个项目还是全局，并在这个工具支持的地方提供设计 hook。建议接受 hook。装完重载工具。`npx impeccable update` 可以刷新已有的安装。脚本化安装可以传 `--providers=claude,codex,cursor` 和 `--scope=project|global`。

有三个工具在 hook 生效前还要多做一步。Codex 里打开 `/hooks` 批准项目 hook（更新改了 hook 之后要再批准一次）。Grok Build 里跑 `/hooks-trust` 或用 `--trust` 启动。Hermes Agent 里 hook 是个插件，跑一次 `hermes plugins enable impeccable-design-hook`。

Node 只在跑 `npx` 时需要。skill 本身跑的是一个自包含的引擎二进制，随 skill 一起发，或者一次下载到 `~/.impeccable/bin/`。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。完整文档在 impeccable.style/docs。

### 方式一：npx 安装（推荐）

```bash
npx impeccable install
```

安装器检测你的编程工具，问装项目级还是全局，并提供设计 hook。建议接受 hook，装完重载编程工具，再跑 `/impeccable init`（Codex 上是 `$impeccable init`），它会读代码、问几个问题、写出 `PRODUCT.md`。

想刷新已有安装：

```bash
npx impeccable update
```

脚本化安装（比如写进团队 setup 脚本）：

```bash
npx impeccable install --providers=claude,codex,cursor --scope=project
```

### 方式二：插件市场安装

Claude Code：

```bash
/plugin marketplace add pbakaus/impeccable
```

然后打开 `/plugin`，安装 Impeccable。

GitHub Copilot（VS Code）：从 Visual Studio Marketplace 安装 Impeccable 扩展，或者：

```bash
code --install-extension renaissance-geek.impeccable
```

需要 VS Code 1.109.3 以上、Copilot Chat、受信任的工作区。这种方式只装 skill，不装 hook。

Grok Build：

```bash
grok plugin install pbakaus/impeccable#plugin --trust
```

会装 skill、agent 和 hook。

### 方式三：团队用 git submodule 固定版本

```bash
git submodule add https://github.com/pbakaus/impeccable vendor/impeccable
npx impeccable link --source=vendor/impeccable --providers=claude,cursor
```

把 `.gitmodules`、submodule 和生成的链接提交上去。同事跑 `git submodule update --init --recursive`。升级时跑 `git submodule update --remote vendor/impeccable`，再跑一遍 `link` 命令并提交。链接只装 skill，不装 hook。已有的 skill 文件夹除非传 `--force` 否则不动。

### 方式四：手动复制，不需要 Node

从 impeccable.style 下载对应工具的 ZIP，或者直接 clone 仓库：每个工具的构建产物都提交在仓库根目录。把 `skills/impeccable` 复制到项目里相同的位置，或全局文件夹。

| 工具 | 仓库里的文件夹 | 全局 skills 文件夹 |
| --- | --- | --- |
| Claude Code | `.claude/` | `~/.claude/skills/` |
| Cursor | `.cursor/` |  |
| Codex CLI、Replit Agent | `.agents/` | `~/.agents/skills/` |
| Devin | `.devin/` | `${XDG_CONFIG_HOME:-$HOME/.config}/devin/skills/` |
| GitHub Copilot | `.github/` |  |
| Gemini CLI | `.gemini/` |  |
| Google Antigravity | `.agent/` | `~/.gemini/config/skills/` |
| OpenCode | `.opencode/` |  |
| Grok Build | `.grok/` | `~/.grok/skills/` |
| Hermes Agent | `.hermes/` | `${HERMES_HOME:-$HOME/.hermes}/skills/` |

### 方式五：不用 agent，终端直接扫

```bash
npx impeccable detect src/
npx impeccable detect https://example.com
npx impeccable detect --json .
```

开发中的页面也可以扫：`npx impeccable detect http://localhost:5173`。退出码 2 表示有发现，1 表示目标扫不了。

## 配置说明

- 项目上下文文件：`PRODUCT.md`（产品是给谁的、要做什么、约束）和 `DESIGN.md`（现有视觉系统），`init` 和 `document` 命令生成，之后每条命令都读它们。
- 忽略规则：品牌字体放行用 `npx impeccable ignores add-value overused-font Inter --reason "Brand font"`；单个文件关一条规则用 HTML 注释 `<!-- impeccable-disable 规则名: 原因 -->`。
- 实时模式的文案回写：默认走聊天 agent；想让它一直在聊天会话里，用环境变量 `IMPECCABLE_LIVE_COPY_AGENT=chat`；想关掉回写，设为 `off`。服务器启动时读一次。
- 常用命令固定快捷方式：`/impeccable pin audit` 可以把 `audit` 固定成 `/audit`。

## 注意事项

- 实时模式只改本地 checkout，不要往已部署的站点注入，也不要为了让它跑起来而放宽生产 CSP。
- 用实时模式改文案前，先审一下 `package.json` 里 `impeccable:manual-edit-validate` 这个可选脚本，它会用你的权限跑。
- Codex 里 hook 装好后要在 `/hooks` 里批准，更新改了 hook 也要再批一次；Grok Build 用 `/hooks-trust` 或 `--trust` 启动。
- 检测器扫源文件（JSX、TSX）时只跑模式类规则，对比度、字号这类要渲染后才能判断的规则，必须扫 URL 或开发服务器地址。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/pbakaus/impeccable
- 原 README：https://github.com/pbakaus/impeccable#readme
- 官方文档：https://impeccable.style/docs

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 Apache-2.0。
