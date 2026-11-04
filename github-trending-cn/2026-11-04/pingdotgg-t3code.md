# t3code：Agent 的统一遥控器

- 原项目：pingdotgg/t3code
- 原项目链接：https://github.com/pingdotgg/t3code
- 榜单：周榜 2026-11-04 第 3 名
- 翻译日期：2026-11-04
- 原项目许可：MIT
- 原项目数据（2026-11-04 核对）：Star 44,332，Fork 9,247，创建于 2026-02-08

## 一句话介绍

一个 Agent 操控台：手机、网页、桌面三个入口，统一管你电脑上跑着的 Claude Code、Codex、Cursor、Grok Build、OpenCode 这些编程助手，出门在外也能接着管家里的 agent。

## 适合谁

- 同时用好几个 AI 编程助手的人
- 想在手机上看 agent 跑到哪了、随时插一句话的人
- 电脑上 agent 跑着长任务、自己不在电脑前的人

## 它解决什么问题

- Agent 散在各处：Claude Code 在终端里、Codex 在另一个窗口、Cursor 在编辑器里，换个设备就得重开、重新找。
- 出门在外 agent 还在跑，想看一眼进度、改一句指令，没有统一入口。
- 现有的方案（Codex 桌面应用、Conductor、Claude Desktop、Cursor Glass）作者都试过，觉得没一个达到他的要求：要性能好、能远程用、真正开源。

t3code 的做法是：在电脑上跑一个服务器做中枢，手机 App、网页、桌面应用都是它的遥控器；它不卖你模型，用的是你自己在各家 agent 上已有的订阅。

## README 翻译（核心部分）

原文标题是 T3 Code，副标题是 T3 Code is an "agent harness control surface". It enables control of the agents on your machine with a best-in-class mobile app (iOS, Android), web app and Electron-based desktop app.，意思是 T3 Code 是一个 Agent 操控台。它让你用一流的手机应用（iOS、Android）、网页应用和基于 Electron 的桌面应用，控制你电脑上的 agent。

支持的 agent（原文翻译）：用你在 Claude Code、Codex、Cursor、Grok Build、OpenCode、Google Antigravity 和 fx 上的订阅。如果它们已经在你的电脑上装好了，T3 Code 就能控制它们。

“你们到底在卖我什么？”（原文 "Wait, what are you selling me?" 翻译）：什么都不卖。我们做 T3 Code，是因为我们想要最好的 agent 开发体验。灵感来自已有的方案，比如 Codex 桌面应用、Conductor、Claude Desktop 和 Cursor Glass，但没有一个达到我们的标准。我们想要性能好、能远程用、真正开源的东西。如果哪天我们走错了方向，我们希望你手里有 fork 并做出自己想要的编辑器所需的一切。

安装前置（原文 Installation 翻译）：T3 Code 目前支持 Codex、Claude、Cursor、Grok Build、OpenCode、Antigravity 和 fx。使用之前至少先装好并登录一个提供方：

- Codex：装 Codex CLI，跑 `codex login`
- Claude：装 Claude Code，跑 `claude auth login`
- Cursor：装 Cursor CLI，跑 `agent login`
- Grok Build：装 Grok Build CLI，跑 `grok login`
- OpenCode：装 OpenCode，跑 `opencode auth login`
- Antigravity：在设置里启用，然后用 Install Antigravity 并用 Google 登录，不需要 CLI。
- fx：在跑 T3 Code 服务器的那台机器上装 fx，跑 `fx login`（见安装指南）。

命令行安装（原文 Command line 翻译）：

```bash
curl -fsSL https://t3.codes/install.sh | sh
```

Windows 上用 PowerShell：

```bash
irm https://t3.codes/install.ps1 | iex
```

然后跑 `t3` 启动服务器并打开本地网页应用。`t3 service install` 让它在后台一直跑，`t3 update` 升到新版本，`t3 --help` 有完整参考。

只想试一次、不安装的话，跑 `npx t3@latest`。

桌面应用安装（原文 Desktop app 翻译）：从 GitHub Releases 装最新版桌面应用，或者从你喜欢的包管理器装：

Windows（winget）：

```bash
winget install T3Tools.T3Code
```

Windows（scoop）：

```bash
scoop install extras/t3code
```

macOS（Homebrew）：

```bash
brew install --cask t3-code
```

Debian、Ubuntu（.deb）：从 GitHub Releases 下载 `.deb`，然后：

```bash
sudo apt install ./T3-Code-*.deb
```

Arch Linux（AUR），稳定版：

```bash
yay -S t3code-bin
```

 nightly 版：

```bash
yay -S t3code-nightly-bin
```

AUR 打包由本仓库的 `packaging/aur` 维护。

Nix（nixpkgs）：

```bash
nix profile add github:NixOS/nixpkgs/nixos-unstable#t3code
```

这个包由 nixpkgs 维护，包含桌面应用（`t3code-desktop`）和 `t3` 命令。NixOS 配置和更新见 Nix 安装说明。

注意事项（原文 Some notes 翻译）：项目还非常早期，难免有 bug。目前基本不接受贡献，小修小补可能会考虑，大功能不会接。

文档（原文 Documentation 翻译）：完整文档在仓库的 `docs/` 里，目前还没有文档网站。包括 FAQ、安装和首次运行、权限模式、键盘快捷键、项目设置、外观偏好、从手机或其他机器远程访问、通过 MCP 连接 Claude Code、Codex、ChatGPT 等 agent、保持应用和服务器同步、源代码管理集成、多账号（Codex、Claude）、以后台服务运行 T3 Code。从源码构建从 `docs/internals/overview.md` 开始。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。完整文档在仓库的 `docs/` 目录里。

### 方式一：命令行安装（推荐）

先装好并登录至少一个 agent（见上文安装前置），再装 T3 Code：

```bash
curl -fsSL https://t3.codes/install.sh | sh
```

Windows 上用 PowerShell：

```bash
irm https://t3.codes/install.ps1 | iex
```

装完启动：

```bash
t3
```

这条命令启动服务器并打开本地网页应用。想让它一直在后台跑：

```bash
t3 service install
```

升级：

```bash
t3 update
```

只想试一次、不安装：

```bash
npx t3@latest
```

### 方式二：桌面应用

从 GitHub Releases 下载最新版，或者按系统用包管理器装：

```bash
winget install T3Tools.T3Code        # Windows winget
scoop install extras/t3code          # Windows scoop
brew install --cask t3-code          # macOS Homebrew
yay -S t3code-bin                    # Arch Linux 稳定版
```

Debian、Ubuntu：从 GitHub Releases 下载 `.deb` 后：

```bash
sudo apt install ./T3-Code-*.deb
```

### 方式三：手机 App

iOS 和 Android 都有手机应用（App Store / Google Play），连上电脑上跑着的 T3 Code 服务器就能远程管 agent。远程访问的具体做法见仓库 `docs/` 里的远程访问说明。

## 配置说明

- 先装 agent、再装 T3 Code：至少一个提供方（Codex、Claude、Cursor、Grok Build、OpenCode、Antigravity、fx）要在电脑上装好并登录好，T3 Code 才能控制它。
- 服务器模式：`t3` 启动服务器并打开本地网页应用；`t3 service install` 是以后台服务的方式常驻；`t3 update` 升级；`t3 --help` 看完整命令参考。
- 多账号：Codex 和 Claude 都支持多账号，做法见 `docs/` 里的多账号说明。
- 远程访问：手机或其他机器连服务器的做法见 `docs/` 里的远程访问说明。
- MCP 连接：Claude Code、Codex、ChatGPT 等 agent 通过 MCP 接入的做法见 `docs/` 里的相关说明。

## 注意事项

- 项目还非常早期，原文明确说难免有 bug，遇到问题先看 `docs/` 里的 FAQ。
- 目前基本不接受贡献：小修小补可能会考虑，大功能不会接；想提需求去 Ideas 讨论区，需要支持去 Discord。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/pingdotgg/t3code
- 原 README：https://github.com/pingdotgg/t3code#readme
- 官网：https://t3.codes
- 网页应用：https://app.t3.codes

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 MIT。
