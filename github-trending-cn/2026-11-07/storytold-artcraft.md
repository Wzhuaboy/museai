# ArtCraft：给艺术家的 AI 创作 IDE

- 原项目：storytold/artcraft
- 原项目链接：https://github.com/storytold/artcraft
- 榜单：月榜 2026-11-07 第 2 名（顺推；本月第 1 名 rea 已翻译）
- 翻译日期：2026-11-07
- 原项目许可：MIT 或 Apache-2.0 双许可（任选其一；按 README 原文，GitHub 元数据里显示为 Apache-2.0）
- 原项目数据（2026-11-07 核对）：Star 39,383，Fork 6,204，创建于 2022-03-31，Release 29 个

## 一句话介绍

ArtCraft 是给艺术家的 IDE：做交互式 AI 图片和视频创作，在 2D 里构图、在 3D 里布景、按自己的活儿选模型，把"写提示词"变成可控、可复现的"手艺活"。

## 适合谁

- 用 AI 做图、做视频的艺术家、设计师、电影人
- 觉得纯靠提示词抽卡太随机，想要精确控制构图、角色、机位的人
- 需要在同一个项目里混用多个 AI 模型（图、视频、音乐、3D）的人
- 想把 AI 生成流程做得像传统创作流程一样可控、可复现的人

## 它解决什么问题

- 艺术家需要控制构图、角色一致性和机位，光写提示词做不到。ArtCraft 的思路是：先搭场景、再生成——在生成之前就把场景搭好。
- 模型太多太散：图片、视频、音乐、3D 网格、世界生成各有各的工具。ArtCraft 把 62 个模型收进一个工作台，按需调用。
- 提示词是一次性的、不可复现的；ArtCraft 用可视化工具（分层、摆姿势、布景、抠图）把创作过程变成可精确调整、可重复的操作。

## README 翻译（核心部分）

### 高级创作功能：展示，别只说

艺术家需要控制构图、角色身份和机位。先搭场景，再生成。点击任意预览可全尺寸查看。

| 功能 | 说明 |
| --- | --- |
| **图片到地点（Image to Location）** | 把虚拟演员放进一致的环境里，在同一个房间里规划多个镜头。 |
| **3D 图片合成（3D Image Compositing）** | 在 3D 里分层叠加背景、前景和道具，做出有纵深的构图。 |
| **2D 图片合成（2D Image Compositing）** | 用图层、去背景和绘画工具在平面上构图。 |
| **图片转 3D 网格（Image to 3D Mesh）** | 把一张图片变成可以精确定位、旋转、取景的 3D 物体。 |
| **角色摆姿势（Character Posing）** | 生成最终镜头前，先给角色摆好姿势、定好机位。 |
| **场景调度与套件拼搭（Scene Blocking with Kitbashing）** | 组合 3D 素材套件，控制机位角度、物体摆放和纵深。 |
| **角色身份迁移（Character Identity Transfer）** | 用摆好姿势的人体模型引导角色的摆放和姿态。 |
| **去背景（Background Removal）** | 把主体抠出来，当道具、图层或背景用。 |
| **混合素材创作（Mixed Asset Crafting）** | 在一个场景里组合图片抠图、世界和 3D 网格。 |

更多场景调度、画布编辑、场景重打光的预览还在路上。

### 快速简易提示词

想快速探索想法时，先写提示词起步，再用画布和场景工具细化。

| 功能 | 说明 |
| --- | --- |
| **文生图（Text to Image）** | 用文字提示词，在一众图片模型里探索想法。 |
| **提示词修图（Prompted Image Editing）** | 用文字描述改图，支持 Nano Banana Pro、GPT Image 这类模型。 |
| **画布修图（Canvas Image Editing）** | 用绘画、蒙版和局部重绘，精确指定图片哪里要改。 |
| **图生视频（Image to Video）** | 选视频模型和生成参数，把一张图做成动画。 |

更多图片局部重绘、图片素材（ingredients）功能的预览还在路上。

### ArtCraft 内支持的模型与供应商

| 供应商 | 模型与工作流 |
| --- | --- |
| **ArtCraft** | 图片、视频、音乐和音效、3D 网格、世界。完整模型目录见下。 |
| Grok | Grok Imagine 和 Grok Video。 |
| Midjourney | Midjourney 图片生成。 |
| Sora | Sora 1、Sora 2 和 GPT Image 1。 |
| World Labs | 用高斯泼溅（Gaussian splats）做 Marble 世界生成。 |

**ArtCraft：完整 62 个模型目录**

注：† 表示目前已停用；‡ 表示受限模型，桌面应用里目前不可用。

**图片（16 个）**

| 系列 | 模型 |
| --- | --- |
| Nano Banana | Nano Banana、Nano Banana 2、Nano Banana Pro |
| GPT Image | GPT Image 1.5、GPT Image 2、GPT Image 2.5 Flare、GPT Image 2.5 Sunburst |
| FLUX | FLUX.1 [dev]、FLUX.1 [schnell]、FLUX 1.1 [pro]、FLUX 1.1 [pro] ultra |
| Seedream | Seedream 4、Seedream 4.5、Seedream 5 Lite、Seedream 5.0 Pro、Seedream 5.0 Pro Ultra |

**视频（25 个）**

| 系列 | 模型 |
| --- | --- |
| Seedance | Seedance 1.0 Lite †、Seedance 1.5 Pro、Seedance 2.0 |
| Kling | Kling 1.6 Pro、Kling 2.1 Pro †、Kling 2.1 Master †、Kling 2.5 Turbo Pro、Kling 2.6 Pro、Kling 3.0 Pro †、Kling 3.0 Standard † |
| Veo | Veo 2 †、Veo 3 †、Veo 3 Fast、Veo 3.1、Veo 3.1 Fast、Veo 3.1 Lite |
| Sora | Sora 2 †、Sora 2 Pro † |
| Vidu | Vidu Q3、Vidu Q3 Turbo |
| MiniMax | MiniMax H3、MiniMax H3 Turbo ‡、MiniMax H3 Ultra ‡ |
| Flux | Flux 3、Flux 3 Draft |

**音乐和音效（5 个）**

| 系列 | 模型 |
| --- | --- |
| Suno | Suno Music、Suno Remix、Suno Sounds、Suno Sample |
| Seed Audio | Seed Audio 1.0 |

**3D 网格（11 个）**

| 系列 | 模型 |
| --- | --- |
| Hunyuan 3D | Hunyuan 3D 2.0、Hunyuan 3D 2.1、Hunyuan 3D 3、Hunyuan 3D 3 Sketch、Hunyuan 3D 3.1 Pro、Hunyuan 3D 3.1 Rapid、Hunyuan 3D 3.1 Part、Hunyuan 3D 3.1 Smart Topology |
| Tripo3D | Tripo3D H3.1 |
| Meshy | Meshy 6 |
| Rodin | Rodin 2.5 Fast |

**世界与高斯泼溅（5 个）**

| 系列 | 模型 |
| --- | --- |
| Marble | Marble 1.0、Marble 1.0 Draft、Marble 1.1、Marble 1.1 Plus |
| TripoSplat | TripoSplat |

另外计划接入的供应商：Kling、Google、Runway、Luma；也在考虑支持 OpenArt、Freepik 这类聚合器的现有订阅。

### 下载

- 稳定版：官网 getartcraft.com，提供 Windows、macOS、Linux 版
- GitHub 最新构建：见仓库 Releases（含 AppImage、DEB、RPM、Arch、Flatpak 包）
- Linux 打包说明：见原 README 的 "Linux packaging notes" 链接
- 从源码构建：见原 README 的 "Build from source" 链接（含 Linux）

### 文档

- 开发环境搭建、Linux 打包、开发者文档、桌面构建与开发脚本、路线图：都在原 README 的 Documentation 一节里给了链接。

## 中文部署操作指南

### 方式一：直接下载安装（推荐）

去官网下载对应系统的稳定版安装包：

- 官网：https://getartcraft.com
- Windows、macOS、Linux 都有；Linux 也可在 GitHub Releases 里拿 AppImage、DEB、RPM、Arch、Flatpak 包。

### 方式二：从源码构建

原 README 给了构建文档链接（含 Linux 构建），按文档走：

- 构建文档：见原 README 的 "Build from source" 链接
- 开发环境搭建：见原 README 的 "Development setup" 链接

本文不再转抄构建命令，避免版本变了对不上。

## 配置说明

- README 没有写需要手动填的必填配置（比如 API Key 怎么填、填在哪），模型调用的账号与授权方式以应用内和官网说明为准。
- 桌面应用本身是 Rust 写的（仓库含 `crates`、`frontend`、`artcraft-native` 等目录），从源码构建按开发文档走。

## 注意事项

- 62 个模型里不少是第三方商业模型（Grok、Midjourney、Sora、Kling、Veo 等），README 没有写各模型的计费方式和账号要求，实际用之前先在官网和各供应商处确认价格与授权方式，别按"免费"去理解。
- 目录里标 † 的模型目前已停用、标 ‡ 的是受限模型（桌面应用里目前不可用），选模型时先看标注。
- 演示视频在 YouTube 上有两分钟的官方 demo（原 README 里有链接），上手前可以先看一遍。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/storytold/artcraft
- 原 README：https://github.com/storytold/artcraft#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
