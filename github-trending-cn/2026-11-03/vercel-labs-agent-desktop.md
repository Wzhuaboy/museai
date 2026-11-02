# agent-desktop：让 AI agent 直接操作你的桌面应用

- 原项目：vercel-labs/agent-desktop
- 原项目链接：https://github.com/vercel-labs/agent-desktop
- 榜单：日榜 2026-11-03 第 1 名
- 翻译日期：2026-11-03
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-03 核对）：Star 9,502，Fork 644，创建于 2026-02-19

## 一句话介绍

给 AI agent 用的电脑操作命令行工具：它通过操作系统自带的无障碍树读取桌面应用的界面元素，再让 agent 直接点按、输入、操作，不用靠截屏猜像素坐标。

## 适合谁

- 在做 computer-use（电脑操作）类 AI agent 的开发者
- 想让 agent 帮自己操作本地软件的人：点按钮、填表单、切换窗口、收通知
- 需要一套跨 macOS、Windows、Linux 通用的桌面操作接口的团队

## 它解决什么问题

- 过去 agent 操作电脑主要靠截屏加像素坐标：界面一变就点错，又脆又不准。
- 每个平台各有一套无障碍接口，没有统一的调用方式，agent 想跨平台操作桌面得自己挨个适配。
- agent 每次操作完都不知道到底点没点中，缺少“操作完再确认”的闭环。

agent-desktop 的做法是：快照给每个可操作元素一个编号（ref），agent 按编号操作，操作完再快照一次验证，全程用结构化数据，不用像素匹配。

## README 翻译（核心部分）

原文标题是 Computer use for AI agents: read and operate desktop apps through the OS accessibility tree，意思是给 AI agent 的电脑操作能力：通过操作系统无障碍树读取并操作桌面应用。

原文核心说法翻译如下：

> 这是一个面向 macOS、Windows 和 Linux 的 CLI 和 C 语言库。一次快照返回 JSON，里面给每个 agent 可以操作的元素一个 ref。agent 对一个 ref 操作，然后再次快照检查，不用像素匹配，整个循环留在你的 agent 里。

每次 CLI 调用都在自己的进程里跑。无头调用仍然禁止前台激活和合成输入。

隐私提醒（原文）：快照、剪贴板读取、截图、命令输出和调试产物可能包含私人的桌面内容，不要放进公开日志和上传内容。可选的 JEV helper 会把屏幕描述发给配置好的模型提供方，它和原生 CLI 是分开的，详见隐私与数据处理说明。

快速上手（原文 Quick start 翻译）：观察、对 ref 操作、再观察。`agent-desktop list-apps` 列出的任何应用名都可以用，Finder 是 macOS 的例子。每条命令打印一个 JSON 信封，下面是一份裁剪过的快照。

```bash
agent-desktop snapshot --app Finder -i      # 交互元素，每个带一个 ref
agent-desktop click @s8f3k2p9:e8            # 对快照里的 ref 操作
agent-desktop snapshot --app Finder -i      # 再观察一次，验证结果
```

快照返回的 JSON 大致是这样（原文示例裁剪版）：

```json
{
  "version": "2.6",
  "ok": true,
  "command": "snapshot",
  "data": {
    "app": "Finder",
    "window": { "id": "w-204749", "title": "Downloads" },
    "snapshot_id": "s8f3k2p9",
    "ref_count": 59,
    "complete": true,
    "tree": {
      "role": "window",
      "name": "Downloads",
      "children": [
        { "role": "treeitem", "name": "Documents", "ref_id": "@s8f3k2p9:e8", "available_actions": ["Click"] }
      ]
    }
  }
}
```

用 ref 时要注意的几条（原文翻译）：

- ref 只属于它那次快照。只写 `@e8` 会被拒，报错 `INVALID_ARGS`。界面变了之后再操作，会返回 `STALE_REF` 或 `AMBIGUOUS_TARGET`，这时重新快照、用新 ref。
- 多个窗口会报 `AMBIGUOUS_TARGET`，`snapshot` 会在 `error.details` 里列出候选窗口 id，用 `--window-id` 指定一个。
- 界面元素密集的应用：先用 `snapshot --skeleton --app Slack -i --compact` 画骨架，再用 `snapshot --root @s8f3k2p9:e3 -i --compact` 钻进某个区域。
- 默认无头。ref 操作走无障碍 API，不移动鼠标、不抢焦点。全局 `--headed` 参数才允许真实输入。
- PowerShell 里每个 ref 都要加引号（`'@s8f3k2p9:e8'`），因为不加引号的 `@token` 是 splatting 操作符。

给 AI agent 用（原文 For AI agents 翻译）：二进制自带和它版本匹配的文档：

```bash
agent-desktop skills get desktop      # 循环、ref、验证和重试规则
agent-desktop skills get platform     # 当前系统的差异
agent-desktop <command> --help        # 单个命令的参数
```

从 skills.sh 把 skill 装进 agent 框架：

```bash
npx skills add https://github.com/vercel-labs/agent-desktop --skill agent-desktop
```

或者把下面这段写进你的 `AGENTS.md`：

```bash
Use `agent-desktop` to see and operate desktop apps. Before the first use, run
`agent-desktop skills get desktop` and `agent-desktop skills get platform`, and follow them.
```

每条命令打印一个信封，里面有 `ok`，以及 `data` 或 `error`。错误带 `code`、`disposition`，通常还有 `suggestion`；只有 `error.disposition.retry` 是 `safe` 时才重试。契约、错误码和退出码在 `docs/json-output.md` 里。

命令一览（原文 Commands 翻译）：一共 60 个命令名，其中 56 个是可操作命令，另外 4 个（`key-down`、`key-up`、`mouse-down`、`mouse-up`）要等 daemon 能释放按住的按键或按钮后才能运行。

| 分组 | 命令 |
| --- | --- |
| 观察 | `snapshot`、`find`、`get`、`is`、`screenshot`、`list-surfaces` |
| 按 ref 操作 | `click`、`double-click`、`triple-click`、`right-click`、`type`、`set-value`、`clear`、`focus`、`select`、`toggle`、`check`、`uncheck`、`expand`、`collapse`、`scroll`、`scroll-to` |
| 键盘和鼠标 | `press`、`hover`、`drag`、`mouse-move`、`mouse-click`、`mouse-wheel`、`key-down`、`key-up`、`mouse-down`、`mouse-up` |
| 应用和窗口 | `launch`、`close-app`、`list-apps`、`list-windows`、`list-displays`、`focus-window`、`resize-window`、`move-window`、`minimize`、`maximize`、`restore`、`open-system-surface` |
| 通知 | `list-notifications`、`dismiss-notification`、`dismiss-all-notifications`、`notification-action` |
| 剪贴板 | `clipboard-get`、`clipboard-set`、`clipboard-clear` |
| 等待 | `wait` |
| 会话 | `session`、`trace`、`cursor-overlay` |
| 系统 | `status`、`permissions`、`version`、`batch`、`skills` |

平台支持（原文 Platform support 翻译）：

|  | macOS | Windows | Linux |
| --- | --- | --- | --- |
| 无障碍树 | 支持 | 支持 | 支持（AT-SPI） |
| 点击 / 输入 / 键盘 | 支持 | 支持 | AT-SPI；X11 / GNOME 按键 |
| 鼠标输入 | 支持 | 支持 | X11，`--headed` |
| 截图 | 支持 | 支持 | X11 窗口；Wayland 用 portal |
| 剪贴板 | 支持 | 支持 | 支持；Wayland 需要 `wl-clipboard` |
| 应用与窗口管理 | 支持 | 支持 | 启动 / 列出；X11 窗口控制 |
| 通知 | 支持 | 支持 | GNOME Shell |
| 系统界面（`open-system-surface`） | 计划中 | 支持 | GNOME 托盘、操作中心 |

语言绑定（原文 Language bindings 翻译）：每个发布版还带 `libagent_desktop_ffi`，覆盖 macOS、Linux 和 Windows，程序可以在进程内直接调，不用每次启动 CLI。`agent-desktop skills get ffi` 讲入口点、内存归属和线程规则。Python 里用 ctypes 调用的例子原文给了，大意是加载动态库、建 adapter、用完销毁。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。原项目文档在仓库的 `docs/` 目录和 `apps/docs` 里。

### 方式一：npm 安装（推荐）

macOS、Windows、Linux 都可以用 npm 装：

```bash
npm install -g agent-desktop
agent-desktop version
```

Bun、Yarn、pnpm 可以装同一个包。包里带 x64 和 ARM64 的原生二进制和平台 helper。

权限前置要求（按系统）：

```bash
agent-desktop permissions --guide
```

- macOS：需要无障碍（Accessibility）权限，上面这条命令会给指引。
- Windows：操作和终端同完整性级别的应用不需要额外授权。
- Linux：需要在用户的图形会话里跑，并装好 `at-spi2-core`。

官方 Homebrew 和 Scoop 包正在提交，还没进默认源；仓库也不再维护自定义的 Homebrew tap 或 Scoop bucket。不想走 npm 的话，可以从 GitHub Releases 下载对应平台的原生压缩包，把 helper 放在可执行文件旁边直接运行。

### 方式二：从源码构建

按原项目 README，构建要看 `docs/install.md`。各平台的 adapter 只在自己的系统上构建，所以 cargo 测试要按宿主平台限定包。macOS 上的例子：

```bash
HOST_PKGS=(-p agent-desktop-core -p agent-desktop-macos -p agent-desktop -p agent-desktop-ffi)
cargo test "${HOST_PKGS[@]}"
cargo clippy "${HOST_PKGS[@]}" --all-targets -- -D warnings
```

Windows 上把 `agent-desktop-macos` 换成 `agent-desktop-windows`，Linux 上换成 `agent-desktop-linux`。完整的检查门槛在 `CONTRIBUTING.md` 里。

### 方式三：接进 AI agent

装好之后，让 agent 学会用它，二选一：

```bash
npx skills add https://github.com/vercel-labs/agent-desktop --skill agent-desktop
```

或者在项目 `AGENTS.md` 里加一段（见上文 README 翻译里的原文片段），第一次用之前跑 `agent-desktop skills get desktop` 和 `agent-desktop skills get platform`。

## 配置说明

- 无头还是真实输入：默认无头（走无障碍 API，不动鼠标、不抢焦点），需要真实输入时加全局参数 `--headed`。
- 权限：macOS 靠无障碍权限；Linux 靠图形会话加 `at-spi2-core`，Wayland 下剪贴板要 `wl-clipboard`；Windows 一般不用额外授权。
- ref 的有效期：ref 只属于它那次快照，界面一变就失效，失效后重新快照再操作，不要缓存 ref 反复用。
- 输出格式：每条命令只打印一个 JSON 信封，解析时按 `ok`、`data`、`error` 三段处理，错误重试只看 `error.disposition.retry` 是不是 `safe`。

## 注意事项

- 快照、剪贴板、截图、命令输出里可能有私人桌面内容，不要放进公开日志或上传到公开地方。
- 可选的 JEV helper 会把屏幕描述发给配置好的模型提供方，它是独立组件，介意数据外发的不要开。
- PowerShell 里 ref 必须加引号，否则 `@token` 会被当成 splatting 操作符。
- Homebrew、Scoop 官方包还没进默认源，装之前先确认当前状态，不要按旧教程找自定义 tap。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/vercel-labs/agent-desktop
- 原 README：https://github.com/vercel-labs/agent-desktop#readme
- 官方文档：仓库内 `docs/` 目录（安装见 `docs/install.md`，JSON 输出见 `docs/json-output.md`）

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 Apache-2.0。
