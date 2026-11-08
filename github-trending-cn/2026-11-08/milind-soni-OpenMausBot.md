# OpenMausBot：开源的 Grok Bot 替代品，每台机器人都有一台电脑

- 原项目：milind-soni/OpenMausBot
- 原项目链接：https://github.com/milind-soni/OpenMausBot
- 榜单：周榜 2026-11-08 第 7 名（顺推；周榜第 1–6 名均已翻译）
- 翻译日期：2026-11-08
- 原项目许可：Apache-2.0（`enterprise/` 目录除外，见注意事项）
- 原项目数据（2026-11-08 核对）：Star 17,232，Fork 2,431，创建于 2026-08-11，提交 8,704 次，Release 105 个

## 一句话介绍

OpenMausBot 是开源的 Grok Bot 替代品：一支属于你自己的 AI 机器人小队，装在一个聊天应用里——每个机器人都是一个真实 agent，有自己的性格、模型、电脑和接好的应用。

## 适合谁

- 想要 Grok Bot、Muse、dots、cue 那种"一队 AI 助手在聊天应用里干活"，但不想被封闭产品和订阅绑住的人
- 已经在用 Claude Code、Codex 或 Grok，想给它们一个聊天式的操作台的人
- 想让多个 agent 分工协作，各自有自己的电脑和权限边界的人
- 愿意自托管、自己管密钥和服务器的人

## 它解决什么问题

- 一个盒子里的单个助手，形状不对。OpenMausBot 保留 Grok Bot 的想法（AI 就是一个消息应用：一排机器人，各有性格、各自线程的记忆、模型、电脑和应用），但按开源、本地优先、跑在你已有的 agent 上重做一遍。
- 封闭产品把模型、电脑和你的数据都留在厂商那边。OpenMausBot 是这个形态的开源版：一支 agent 小队在聊天应用里，每个有自己的模型、自己的电脑、自己接的应用，跑在你的机器上，Apache 2.0 许可。
- 想找"开源版 Muse"、"开源版 dots"、"开源版 Grok Bot"、"开源版 Instinct"或"开源版 Cue"的人，找的就是这个仓库。

## README 翻译（核心部分）

### 为什么有它

一个盒子里的单个助手，形状不对。OpenMausBot 是一个独立开源项目，受 **Grok Bot** 启发——它保留了那个想法（AI 就是一个*消息应用*：一排你能聊天的机器人，每个有自己的性格、各自线程的记忆、模型、电脑和应用），按开源、本地优先、跑在你已有的 agent 上重建：

- **自带 agent。** 机器人跑在你自己机器上装好的 `claude`、`codex` 和 `grok` CLI 上——用你现有的登录和订阅，不用新开账号，中间没有代理。在 **Settings → Engines** 里可以把任意引擎指向自定义 CLI 二进制（指定版本构建或包装器）。
- **本地优先。** `127.0.0.1` 上一个小小的 harness 服务器拥有全部 agent 进程。对话记录、密钥和事件都存在 `~/.openmausbot` 里，不在云端。
- **有手的 agent。** 每个机器人可以用一台云端 Linux 桌面、一台隔离的本地虚拟机，或者——在平台安全边界目前已认证的地方——你自己的电脑，外加通过 Composio 的 500 多个应用。主机控制在 macOS 和 Ubuntu Xorg 上需要明确 opt-in 才能开；Ubuntu Wayland 在 #345 号 issue 解决前保持禁用。

### 与 Grok Bot、Muse、dots、cue 的对照

2026 年七周内出了四款封闭个人 agent 产品，每一款都把模型、电脑和你的数据留在厂商那边。OpenMausBot 是这个形态的开源版。

| 想找的 | 它是什么 | OpenMausBot 的不同 |
| --- | --- | --- |
| **开源版 Grok Bot** | xAI 的机器人名单，在一台共享云电脑上，只用 Grok，来自 SuperGrok 或 Cursor 套餐 | 同样的名单形态；每个机器人任意模型；你自己的机器；审批卡片 |
| **开源版 Muse** | Meta 的单个个人 agent，跑在 Meta 云虚拟机里，只在美国和加拿大 | 一支小队而不是一个 agent；在哪都能跑；数据在 `~/.openmausbot` |
| **开源版 dots** | OpenAI 在 ChatGPT 里的常驻 agent，只用 GPT，Pro 和 Business Premium 套餐 | 多个 agent；用你的 Claude、ChatGPT 或 Grok 登录；不需要套餐 |
| **开源版 Cue** | Manus 的邀请制 agent，有自己的电话、邮箱和钱包 | 不用邀请；用 OAuth 而不是密码；开源 |
| **开源版 Instinct** | Spear Street 的邀请制 agent，在云电脑上保管你的密码 | 想审批时就审批；用 OAuth 登录；你的机器 |

五款并排对照和五个问题的选型指南在原文的链接里。

### 功能

**🧠 每个机器人选一个大脑**

模型选择器加供应商栏——Claude 和 Codex 的模型并排显示，默认的标出来，不可用的供应商变暗并写清原因。可以在对话中途换机器人的模型。

**🖥️ 每个机器人都有一台电脑**

打开 Computer 面板，机器人的云端桌面就自己启动了——它工作时有实时屏幕预览，点 "Open desktop" 可以在浏览器里接管，或者改成指向*这台 Mac*。

**🙋 机器人动手前先问你**

Shell 命令、文件编辑和提问都以行内卡片出现——在聊天里点 Allow / Deny / 回答。权限代理把每一次高风险操作变成一个由你做的决定，云端电脑和本地电脑都一样。

**🔌 接好的应用**

通过 Composio Sessions 的一键市场：Gmail、Slack、GitHub、Notion、Linear 等几百个。OAuth 认证一次，每个机器人都能把它们当工具用。

**🗂 像管理聊天一样管理机器人**

右键点任意机器人：置顶、标未读、改资料、复制、复制会话 ID、隐藏、删除。这就是一个消息应用——你的 agent 表现得像联系人。

**🔑 密钥填一次，全部亮起来**

在 App Settings 里粘贴一次凭证——它们存在本地，供应商舰队会立即热重载。密钥是只写的：界面永远只看到 "configured" 标志，看不到值本身。

**#️⃣ 每个场景一个频道**

工作、个人、每个项目分在不同频道里，不用复制机器人。每个频道有自己的对话记录、共享指令、工作目录、响应规则和可编辑的机器人名单。可以把一个频道和它的机器人归到一个命名的上下文里，团队变了随时改名、改成员。

**⚡ Jev 快速决策**

在 **Settings → Decision model** 里加一个 TypeSafe Jev 密钥，或 OpenRouter 密钥和模型，设为 **Auto** 的房间会在几百毫秒内为每条没指名道姓的消息挑一个合适的机器人；决策模型关掉或不确定时回落到房间的负责人。见 docs/decision-model.md。

**📦 一个 Markdown 文件装一整支队伍**

在 BotMRR 上浏览按结果组织好的队伍，点 **Add to OpenMausBot**，应用会在创建机器人、Chief of Staff、频道、playbook、连接器清单和建议的日常流程之前先打开一个检查界面。也可以从磁盘导入同一个 `.md` 文件，或把它的公开 GitHub 链接粘贴进 **Teams → Import**。

格式保持可移植：OpenMausBot 读结构化的 YAML frontmatter 做可靠的一键安装，而 Grok、Claude、ChatGPT 和人都可以照着普通的 Markdown playbook 走。连接保持关闭直到你批准，日常流程到手就是暂停的，包里永远不带凭证、对话、权限、记忆或电脑访问权限。

**🤝 分享整个部门**

右键点一个部门，选 **Share department…**（或用 **Templates → Share**），把整个部门存成一个文件：机器人和它们的指令、头像、技能、群聊、日常流程、共享指令、Chief of Staff、连接槽位和每个机器人的起始笔记（不勾就留出来）。对话框在保存前会把文件里有什么原样展示给你。聊天记录、密钥密码、模型选择和电脑永远不放进去，看着像密钥的东西会从文本里删掉。导入的人得到的新机器人默认是 Ask 模式，技能关掉、日常流程暂停。

**🎧 会说话的机器人**

点任意回复上的喇叭，或把机器人切换成边出答案边读出来——早上做早饭时可以听它讲昨晚跑了什么。点 **call** 就是一次通话：它听你说话，边干活边告诉你它在做什么，问审批也是出声问。

声音可选 ElevenLabs、Fish Audio、Grok（xAI）、Mac 内置语音，或本地 Chatterbox 服务器，在 agent 资料里设置。给机器人一个自己的声音，一个频道就不会听起来像同一个人。

**还包括：** 带工具运行活动芯片的流式回复 · 编写器麦克风听写（macOS 上是设备端 Apple 语音识别，Windows 和 Linux 桌面应用里是 Fish Audio 语音转文字）· 带角色表情的 SupaMaus 光标吉祥物 · 机器人工作截图折进对话记录里。

### 靠什么实现

| 服务 | 用途 |
| --- | --- |
| **Claude · Codex · Grok** | 每个机器人背后的 agent，通过本地 CLI 运行 |
| **Electron** | macOS、Windows、Ubuntu 的桌面壳 |
| **React + Vite + Tailwind CSS** | 聊天应用界面和构建 |
| **Boat**（boat.dev） | 每个机器人的云电脑 · 赞助商 |
| **Composio** | 接好的应用——Gmail、Slack、GitHub 等 |
| **Cua Driver** | 在你自己机器上的原生电脑操作 |
| **ElevenLabs · Fish Audio** | 会说话的机器人的托管语音 |
| **GitHub Sponsors** | 一次性或每月支持项目 |

### 工作原理

两个进程。应用本身不持有任何传输通道——它通过 HTTP 发类型化命令，再把一条 SSE 事件流折叠成状态。harness 服务器拥有全部 agent 进程，把每个供应商的原生协议归一化成一条规范的运行时事件流（每个线程记成 NDJSON 日志）。

| 层 | 位置 | 做什么 |
| --- | --- | --- |
| Drivers | `server/drivers/` | 每个供应商一个：Claude、Codex、Grok，基于本地 CLI（stream-JSON / JSON-RPC / ACP），再加一个云电脑 agent。未知的驱动只会降级成"不可用"，绝不会拖垮整个舰队。 |
| Harness | `server/harness/` | 注册表（配置 → 实时实例）和每个客户端都折叠的扇入事件总线。 |
| API | `server/index.ts` | 机器人、轮次、审批、模型目录、电脑生命周期、连接器、配置——HTTP + SSE。 |
| Voice | `server/tts/` | ElevenLabs、Fish Audio、Grok（xAI）、Mac 内置语音或本地 Chatterbox。云端密钥留在 harness 上；Markdown 在读出来之前会被改写成值得听的样子。 |
| App | `src/` | 聊天壳。服务器端存储，一个 reducer，零客户端传输。 |
| Desktop | `electron/` | macOS、Windows、Ubuntu 的壳，内嵌 harness 和平台能力；Apple 语音只在 macOS 上，Ubuntu Xorg 有 opt-in 的本地控制，Wayland 保持 fail-closed。 |

**通过 MCP 编排 OpenMausBot**

OpenMausBot 自带一个 stdio MCP 服务器，给 Claude Desktop、Cursor 这类外部客户端用。它暴露一个有意收窄的团队控制面：查看机器人和频道、读/搜压缩过的对话记录页、创建和配置机器人/频道/任务、派活、等完成、换模型、中断轮次。

它**不**暴露审批授权、删除、任意设置、凭证或电脑生命周期。见 MCP 服务器设置和工具参考。

**从脚本和 CI 里跑**

`openmausbot` 命令可以在没有界面的情况下驱动一个正在运行的工作区：从文件搭一支队伍，给一个机器人派一个活，等它和它叫上的每个队友都做完，再把做出来的东西导出来。一份 JSON 文档加 `--json`，退出码可以让脚本分支判断。

```bash
openmausbot team apply team.yaml
openmausbot run "Room Lead" "Rehearse the launch of https://example.com" --export ./out
```

见 Run OpenMausBot from scripts and CI。

### 快速上手

**发布版（最新 Release）：** harness 服务器是内嵌的，不用另外搭服务器。

|  | 下载 | 安装 |
| --- | --- | --- |
| **macOS**（Apple silicon） | OpenMausBot.dmg | 拖进 Applications，打开。已签名和公证。 |
| **macOS**（Intel） | OpenMausBot-intel.dmg | 同一个应用，Intel Mac 版。已签名和公证。 |
| **Windows**（x64） | OpenMausBot-setup.exe | 运行它——一键、按用户安装、不用管理员权限。安装程序还没代码签名，SmartScreen 会显示"未知发布者"：**More info → Run anyway**。 |
| **Ubuntu 24.04**（x64） | OpenMausBot-amd64.deb · OpenMausBot.AppImage | 用 APT 装 `.deb`（推荐），或把 AppImage 设成可执行后运行。Beta 版；支持 GNOME 桌面。 |

任意桌面版也可以通过 Tailscale 和另一台 Windows、macOS 或 Ubuntu 主机配对当客户端，见桌面到桌面 companion 模式。

**从源码：**

```bash
git clone https://github.com/milind-soni/OpenMausBot && cd OpenMausBot

pnpm install

pnpm dev:server    # harness 服务器 → 127.0.0.1:8799
pnpm dev           # 应用 → http://127.0.0.1:5199
pnpm dev:desktop   # Electron 壳；上面两条命令保持运行
```

要求：**macOS、Windows 或 Ubuntu 24.04 x64**，**Node 24+**、**pnpm**，以及至少一个已安装并登录的 agent CLI——`claude`、`codex` 或 `grok`，它们会自动出现在模型选择器里。

打包桌面应用：

```bash
pnpm package:mac      # macOS：DMG + ZIP；需要 Swift/Xcode 工具
pnpm package:win      # Windows：安装程序 + ZIP
pnpm package:linux    # Ubuntu x64：.deb + AppImage + 已验证的 CUA 运行时
```

### 桌面能力状态

| 能力 | macOS | Ubuntu 24.04 Xorg | Ubuntu 24.04 Wayland |
| --- | --- | --- | --- |
| 打包应用、内嵌 harness、本地 agent CLI | 支持 | Beta | Beta |
| Composio 和 Boat/云电脑 | 支持 | Beta | Beta |
| 明确仅预览的本地截屏 | 支持 | Beta | Beta |
| 机器人控制这台电脑 | 支持 | Beta，明确 opt-in | 禁用：Wayland 安全门 |
| 设备端原生听写 | 支持 | 计划中 | 计划中 |
| 通过 Fish Audio 的听写和轮流通话（需要 Fish Audio 密钥） | 不用，设备端代替 | 支持 | 支持 |

Linux 预览版由用户主动发起，永远不会自动开本地机器人控制或 Auto 路由。在 Xorg 上，经过审查的 Cua Driver 0.19.3 运行时只在明确 opt-in 后启动，且不带全屏光标覆盖层。在 Wayland 上，应用永远不会启动它，并在真正的安全门仍未解决时清除旧的 opt-in。

这些凭证都是可选的——本地聊天不用它们也能用。想启用某个集成时，在 **App Settings**（侧边栏底部的齿轮）里粘贴一次密钥：

| 凭证 | 启用什么 | 去哪拿 |
| --- | --- | --- |
| Composio 项目密钥（`ak_…`） | 把 Gmail、GitHub、Slack、Notion 等应用接到你的机器人上 | OpenMausBot Composio 设置 |
| Boat API 密钥 | 给机器人一台带桌面和终端的隔离远程 Linux 电脑 | Boat API 密钥指南 |
| ElevenLabs 密钥 | 大声读回复、和机器人通话 | ElevenLabs API 密钥 |
| Fish Audio 密钥 | 用 Fish Audio 的声音大声读回复、和机器人通话 | Fish Audio API 密钥 |

Composio 和 Boat 是第三方服务，各有自己的账号和条款。Boat 在试用期后是付费服务，用云电脑可能产生费用。

### 触发器：定时和 webhook

触发器就是"某件事发生时，一个机器人做某件事"。跟机器人说"每个工作日早上 9 点，给我发一份收件箱摘要"或"我们的表单一来电话就起草回复"，它就在那一轮里用 `trigger` 工具把触发器搭好（不用确认；聊天里会出现一张带 Edit、Pause、Undo 的实时卡片）。**Triggers** 在侧边栏最前面，列出每个定时和 webhook，带日历和运行历史。

定时（日常流程）可以跑一次、按选定的工作日跑，或每 5–1,440 分钟跑一次，用机器人配置好的模型/电脑或 Cloud VM runner。按间隔的定时会和选定的开始时间对齐；上一轮还在跑就跳过一次，不会让慢活无限排队。

**应用事件**在接好的应用里出事时启动机器人（"一收到 Acme 的邮件就起草回复"）。Composio 把每个事件发到 OpenMausBot 的接好应用服务里排队；应用用长轮询收队，所以桌面端不需要公开地址，关机时事件会等着。Gmail 每 15 分钟查一次；Slack、GitHub 等推送类应用一到就到。

OpenMausBot 默认在 `127.0.0.1:8800` 上启动一个只收 webhook 的接收器（或 `OMB_PORT` 之上一个端口）。用 `OMB_WEBHOOK_PORT` 可以换端口。Webhook 密钥只在触发器创建或轮换时显示一次。

### 当前状态

还早，但是真的能跑——消息 → agent → 流式回复 → 工具 → 审批 → 电脑操作，整个循环端到端是通的：macOS、Windows、Ubuntu 24.04 x64 都有发布版；Ubuntu 仍是 beta，有上面说的能力限制。粗糙的地方：托管/移动端连接还在建，webhook 触发器目前用的是本地接收器而不是常驻的托管中继。

### 隐私

使用分析是可选的、匿名的：产品事件和每天一次"装了什么"的计数，绝不含密钥、姓名、地址或对话。在 Settings → General → Usage analytics 里关掉；`docs/analytics.md` 列了每个事件和属性。

### 支持这个项目

OpenMausBot 免费开源。如果它真帮你干了活，可以通过 GitHub Sponsors 一次性或按月赞助开发。赞助用来资助持续开发和维护；OpenMausBot 保持免费开源。

### 从终端或服务器上跑

Node 24 或更新，装一次就能跑：

```bash
npm install -g openmausbot
openmausbot
```

或不用全局安装，直接 `npx openmausbot`。第一次启动会用方向键选择引导你：选 AI 接入方式、登录或粘贴一个隐藏的 API 密钥、选模型，还可以选接手机。下一次，同一条命令会复用你保存的设置，在这台电脑上打开 OpenMausBot。终端保持开着；Ctrl-C 停的是服务器，不是你保存的工作。用 `--no-open` 可以跳过打开浏览器。

手机接入是可选的，默认跳过。VPS 或常驻电脑上跑服务器，用 `npx openmausbot serve`，入口四选一：`--public-url`（放在你自己的 cloudflared、Caddy 或 nginx 后面）、`--domain`（在你自己的域名上办证书）、`--tailscale`（进你的 tailnet）、`--lan`（只限这个局域网），或 `--tunnel`（`npx openmausbot login` 之后，给一个免费的 MausBot 网址）。

## 中文部署操作指南

### 方式一：下载发布版（推荐）

去最新 Release 下载对应系统的安装包，harness 服务器内嵌，不用另外搭：

- macOS（Apple silicon / Intel）：`.dmg`，拖进 Applications 打开，已签名和公证
- Windows（x64）：`OpenMausBot-setup.exe`，一键安装、不用管理员权限；安装程序还没代码签名，SmartScreen 弹"未知发布者"时点 **More info → Run anyway**
- Ubuntu 24.04（x64）：`.deb`（推荐，用 APT 装）或 AppImage，Beta 版，支持 GNOME 桌面

### 方式二：从源码跑开发版

```bash
git clone https://github.com/milind-soni/OpenMausBot && cd OpenMausBot
pnpm install
pnpm dev:server    # harness 服务器 → 127.0.0.1:8799
pnpm dev           # 应用 → http://127.0.0.1:5199
pnpm dev:desktop   # Electron 壳；上面两条命令保持运行
```

前置要求：macOS / Windows / Ubuntu 24.04 x64，Node 24+、pnpm，至少一个已安装并登录的 agent CLI（`claude`、`codex` 或 `grok`）。

### 方式三：终端 / 服务器版

```bash
npm install -g openmausbot
openmausbot
```

或不装全局包：`npx openmausbot`。第一次启动会引导选 AI 接入方式、登录或粘贴 API 密钥、选模型。服务器上常驻用 `npx openmausbot serve`，入口见上文（`--public-url` / `--domain` / `--tailscale` / `--lan` / `--tunnel`）。

### 方式四：Docker

仓库根目录有 `Dockerfile` 和 `compose.yaml`，按仓库里的部署文档走（本文不转抄，见原项目 docs/deploy-vps.md）。

## 配置说明

- 至少要有一个 agent CLI（`claude`、`codex` 或 `grok`）装好并登录，否则模型选择器里是空的。
- 密钥都是可选的：本地聊天不用它们；想接应用、云电脑、语音时再在 App Settings 里贴：Composio 项目密钥（接 Gmail/GitHub/Slack 等）、Boat API 密钥（云电脑）、ElevenLabs / Fish Audio 密钥（语音）。
- 机器人默认 Ask 模式：高风险操作（Shell 命令、文件编辑）会先弹审批卡片让你点 Allow / Deny。
- 想从脚本或 CI 里驱动，用 `openmausbot` 命令（`team apply`、`run`），或走它自带的 stdio MCP 服务器（给 Claude Desktop、Cursor 用）。

## 注意事项

- 项目还比较早期：核心循环是通的，但 Ubuntu 还是 beta，Wayland 下机器人不能控制本机，托管/移动端连接还在建。
- 许可注意：主体是 Apache 2.0，但 `enterprise/` 目录是另外的 source-available 许可；删掉那个目录，剩下的才是纯开源版。打包的 Cua Driver 组件保留上游 MIT、SIL OFL 1.1、MPL-2.0 等条款。
- 密钥保存方式注意：README 原文写了，API 密钥以明文存在私有的 `config.json` 里（Unix 上权限 `0600`），不是加密存储；介意的话自己留意这台机器的访问权限。
- Boat 云电脑试用期后是付费服务，用云电脑可能产生费用；先看好再开。
- 声明：它和 xAI、Meta、OpenAI、Manus 没有任何隶属关系；"Grok"是 xAI 的商标。作者还特意声明：没有任何加密货币，任何用 OpenMausBot、Maus、SupaMaus 名字的币都和本项目无关。
- Windows 安装程序目前还没代码签名，SmartScreen 会报"未知发布者"，按 README 写的 More info → Run anyway 通过。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/milind-soni/OpenMausBot
- 原 README：https://github.com/milind-soni/OpenMausBot#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
