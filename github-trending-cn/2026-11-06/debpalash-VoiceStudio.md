# VoiceStudio：开源、完全本地的 ElevenLabs 替代品

- 原项目：debpalash/VoiceStudio
- 原项目链接：https://github.com/debpalash/VoiceStudio
- 榜单：月榜 2026-11-06 第 6 名
- 翻译日期：2026-11-06
- 原项目许可：AGPL-3.0
- 原项目数据（2026-11-06 核对）：Star 102,292，Fork 11,339，创建于 2026-04-09

## 一句话介绍

开源 AI 语音工作室，跑在你自己的设备上：声音克隆、声音设计、视频配音、听写、转录、有声书，646 种语言，不用 ElevenLabs 也能做。

## 适合谁

- 要做配音、播客、有声书、视频翻译配音的人
- 不想把声音数据和账单交给云端、想在本地跑的人
- 有显卡能加速、或只有 CPU 也想试试的人
- 想把语音能力接进自己流程（本地 API、MCP）的人

## 它解决什么问题

- ElevenLabs 这类云端语音服务要账号、按量付费，声音数据还得上传到别人服务器。
- VoiceStudio 全部免费、跑在自己硬件上、不用账号，模型按需下载，用哪个下哪个。
- 官网在 voicestudio.sh，下载和文档都在那；README 里还带了简体中文等多语言入口。

## README 翻译（核心部分）

### 能做什么

- **声音克隆（Voice cloning）**：拿一段干净的参考录音，生成用那个熟悉声音说的语音。带自带的演示声音。
- **视频配音（Video dubbing）**：翻译并给视频配音，语音和原片时间对齐。
- **声音设计（Voice design）**：用文字描述一个声音，直接生成。
- **本地模型（Local models）**：自己选引擎，只下载需要的模型。
- **听写与转录（Dictate & transcribe）**：悬浮听写小部件 + 本地转录。
- **旁白与批量（Narrate & batch）**：故事、有声书、排队任务。
- **连接与自动化（Connect & automate）**：本地 API、MCP、可复用的配方、监听文件夹。

默认用 **VoiceStudio**（基于 k2-fsa/OmniVoice 引擎），模型管理器里还有几十个其他引擎可选。功能和引擎目录见原文的 features & engine catalog。

### 免费与付费：上面这些全免费

上面列的全部免费，跑在自己的硬件上，不用账号。Pro 和 Cloud 是可选的：

- **VoiceStudio Pro**：给跨多台机器做付费客户活的人。含商业许可（发到邮箱）、1 个用户同时用 3 台设备、把任务发到别的 GPU 上、项目还留在本地、新功能和修复先拿到。闭源构建、要账号、7 天全额退款。AGPL-3.0 的应用本身一直免费，包括按条款的商业使用。
- **VoiceStudio Cloud**：托管的语音和配音 API，还没上线。语音、声音设计和声音克隆（需征得同意）、配音、转录和有声书，按天或按项目计用量和额度，长任务自己跑。可以加入 early access 拿免费额度。桌面应用一直免费、本地。

### 平台

- **macOS**：Homebrew、DMG、安装器。稳定版，Apple Silicon，macOS 13.3+，本地引擎用 Metal（MPS）。Intel Mac 有限：应用界面能在 Intel 上跑，后端要连到另一台电脑上的 VoiceStudio。
- **Windows**：PowerShell、EXE。稳定版，x64，Windows 10/11，NVIDIA CUDA、AMD ROCm（可选加入）、CPU。Windows on ARM 是实验版：原生应用界面，x64 的 Python 后端在 CPU 上模拟运行。
- **Linux**：AUR、Snap、DEB、AppImage、Nix。稳定版，x64，NVIDIA CUDA、CPU，支持的 GGUF 引擎可用 Vulkan。
- **Docker**：GHCR、Docker Hub。稳定镜像，CPU、NVIDIA CUDA、AMD ROCm。
- **Android**：APK、Obtainium、F-Droid 仓库。Android 10+，预览版，下载模型后离线用。
- **iPhone / iPad**：IPA、侧载。iOS / iPadOS 17+，预览版，下载模型后离线用。

没 GPU 也能用：应用在 CPU 上完全能跑，只是慢一点。原生 GGUF 引擎在 AMD、Intel、NVIDIA 显卡上还能用 Vulkan；OmniVoice GGUF 在 Windows 和 Linux 上会自动选 GPU 和模型大小。

### 上手：装完先干什么

按上面方式装好，打开 **Voice cloning**，选一个声音或加一段干净的参考录音，输入文字、生成。下载任何模型前应用都会先问你。

Agent skills：`npx skills add debpalash/VoiceStudio`（`voicestudio` 做音频活，`voicestudio-maintainer` 管仓库）。

### 许可与负责任使用

- AGPL-3.0 覆盖应用，包括按条款的商业使用。
- 模型权重、声音和生成内容各有自己的许可，模型管理器里每个模型都会显示。
- **克隆声音必须经过声音主人的许可**。细节见 LICENSE-NOTICE.md。

## 中文部署指南

**方式一：macOS（Homebrew，稳定版，Apple Silicon）**

```bash
brew tap debpalash/tap
brew trust --cask debpalash/tap/voicestudio
brew install --cask debpalash/tap/voicestudio
```

或下载 DMG，打开后把 VoiceStudio 拖进 Applications；或一键安装：

```bash
curl -fsSL https://voicestudio.sh/install | sh
```

**方式二：Windows（PowerShell，稳定版，x64）**

```powershell
irm https://voicestudio.sh/install.ps1 | iex
```

或从最新 release 下载 Windows 安装器。

**方式三：Linux（一键安装，稳定版，x64）**

```bash
curl -fsSL https://voicestudio.sh/install | sh
```

Arch / Manjaro / EndeavourOS（AUR）：

```bash
yay -S voicestudio-bin
```

也可以用 `paru -S voicestudio-bin`，或从源码装 `yay -S voicestudio-git`。

Ubuntu / Debian / Linux Mint（DEB）：下载 `.deb` 到当前目录，再装：

```bash
sudo apt install ./VoiceStudio-*-linux-x64.deb
```

Snap（Ubuntu、Fedora、openSUSE 等）：

```bash
sudo snap install voicestudio
```

要开麦克风权限：

```bash
sudo snap connect voicestudio:audio-record
```

AppImage（任何发行版）：下载 AppImage 到当前目录，再跑：

```bash
chmod +x VoiceStudio-*-linux-x64.AppImage
./VoiceStudio-*-linux-x64.AppImage
```

Nix / NixOS（源码环境）：

```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
nix develop .#fhs
bun run dev
```

**方式四：Docker（CPU 上跑）**

```bash
export OMNIVOICE_API_KEY=<redacted>
docker run -d --name omnivoice \
  -p 127.0.0.1:3900:3900 \
  -e OMNIVOICE_API_KEY \
  -e OMNIVOICE_DATA_DIR=/app/omnivoice_data \
  -v omnivoice-data:/app/omnivoice_data \
  ghcr.io/debpalash/voicestudio:stable
printf 'API key: %s\n' "$OMNIVOICE_API_KEY"
```

打开 http://localhost:3900，用打印出来的 API key 登录。NVIDIA、AMD ROCm 和 Compose 的做法见原文；Docker Hub 镜像是 `palashdeb/omnivoice-studio:stable`。

**方式五：从源码跑**

```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun run dev
```

`bun run dev` 会装 JavaScript 依赖，支持的本地后端还会装 Python 依赖，然后启动 Electron。只想重建 Python 环境，直接跑 `bun run setup:api`。

**方式六：手机**

- Android：下载 APK，或在 F-Droid 兼容客户端里加这个仓库：`https://debpalash.github.io/VoiceStudio/fdroid/repo`（按指南核对指纹），或在 Obtainium 里加 GitHub releases 源；也能用 adb 装：`adb install -r VoiceStudio-*-android.apk`
- iPhone / iPad：下载 IPA，按签名和侧载指南装。

**特定版本、卸载**

```bash
curl -fsSL https://voicestudio.sh/install | sh -s -- --version X.Y.Z   # 装指定版本
curl -fsSL https://voicestudio.sh/install | sh -s -- --main            # 编译当前 main
curl -fsSL https://voicestudio.sh/install | sh -s -- --uninstall       # 卸载应用，保留数据
```

如果 `voicestudio.sh` 打不开，直接从仓库跑安装脚本：`curl -fsSL https://raw.githubusercontent.com/debpalash/VoiceStudio/main/scripts/install.sh | sh`。

**用编程 agent 装**（Claude Code、Codex、Cursor 等），直接粘贴：

```
Install the VoiceStudio app on this device and verify it works, following
https://github.com/debpalash/VoiceStudio/blob/main/docs/install/agent.md
```

## 配置说明

- 模型是按需下载的，下载前应用会先问你，不会一上来全下完。
- Docker 方式要先设 `OMNIVOICE_API_KEY`，打开 http://localhost:3900 后用它登录。
- 桌面和手机安装器在最新 release 里；Docker 镜像在 GHCR。
- 0.5.3 或更早（Tauri 应用）升级上来的，要另外单独装新应用。
- Agent skills 有两个：`voicestudio`（做音频活）和 `voicestudio-maintainer`（管仓库），`npx skills add debpalash/VoiceStudio`。

## 注意事项

- macOS 上提示 "VoiceStudio is damaged and can't be opened"，是 Gatekeeper 拦截了应用，不是下载坏了，见仓库里的 Gatekeeper fix。
- 克隆声音必须经过声音主人的许可；模型权重、声音和生成内容各有自己的许可，模型管理器里每个模型都会显示。
- 没 GPU 也能用，CPU 只是慢一点；速度因引擎和硬件而异，见原文 performance。
- Cloud 托管 API 还没上线，别按已上线的去找；Pro 是闭源构建、要账号，免费版 AGPL-3.0 一直能用。
- 是否实测：按原项目 README 文档整理，未实测。
