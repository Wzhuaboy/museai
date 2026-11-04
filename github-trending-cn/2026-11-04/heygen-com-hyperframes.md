# hyperframes：写 HTML 就能渲染视频

- 原项目：heygen-com/hyperframes
- 原项目链接：https://github.com/heygen-com/hyperframes
- 榜单：月榜 2026-11-04 第 4 名
- 翻译日期：2026-11-04
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-04 核对）：Star 78,354，Fork 7,210，创建于 2026-03-10

## 一句话介绍

一个开源视频框架：把 HTML、CSS、媒体和可定位动画变成确定性的 MP4 视频，写网页就会做视频，AI agent 也能直接按你的要求出片。

## 适合谁

- 想做产品介绍、PR 讲解、数据可视化、社媒短视频，但不想学专业剪辑软件的人
- 让 AI 编程助手帮自己批量做视频、做自动化内容管线的人
- 会写前端、想把网页技术复用到视频制作上的人

## 它解决什么问题

- 做视频的门槛高：要学时间轴、关键帧、剪辑软件，改一处就得重新导出、重新检查。
- AI 生成视频不可控：提示词一句话，出来的画面改不动、细节对不上。
- 视频做完就定死了：想换文案、换配色、换一版风格，得从头再来。

HyperFrames 的做法是：视频就是一份 HTML，用 data 属性写时间和轨道，用 GSAP、CSS、Lottie、Three.js 这些前端动画库做可定位动画，渲染出来的 MP4 是确定性的；改视频就是改网页，agent 也能按同一套流程出片。

## README 翻译（核心部分）

原文标题是 HyperFrames，副标题是 Write HTML. Render video. Built for agents.，意思是写 HTML，渲染视频，为 agent 而建。

原文核心说法翻译如下：

> HyperFrames 是一个开源框架，把 HTML、CSS、媒体和可定位动画变成确定性的 MP4 视频。本地用 CLI，从 AI 编程助手用 skill，或者作为托管创作流程背后的渲染核心。

用 Claude Code、Codex、Cursor 或其他编程助手的话，跑一次 `npx hyperframes skills update`，然后让你的 agent 去做视频。

快速上手（原文 Quick Start 翻译）：

### 跟 AI 编程助手一起用

Claude Code 装版本化插件：

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

想开自动更新，在项目终端里跑 `claude`，在 Claude Code 的终端界面里跑 `/plugin`，选 Marketplaces → hyperframes → Enable auto-update。之后用 `/hyperframes:hyperframes`。Copilot、VS Code、Cursor、Gemini CLI 的插件指南、更新和迁移见插件指南。

独立 skill（包括 OpenCode）这样装：

```bash
npx skills add heygen-com/hyperframes
```

选择器打开时默认什么都没选，Core Skills（核心技能组）就是你需要的全部；`/slideshow`、`/remotion-to-hyperframes`、`/reverse-any-video`、`/style-sampling` 和 `/figma` 按需安装。agent 和非交互运行要用 `npx hyperframes skills update`，它只装核心集；`skills add --all` 会装全部 9 个已发布 skill。仓库内部的 6 个 skill 默认不装。想装完整已发布集，用 `npx hyperframes skills`。

注意：`skills add` 解析的是 skills.sh 注册表文件，可能比 `main` 分支慢几个小时。`npx hyperframes skills update` 从和你的 CLI 版本匹配的发布标签装 skill，所以和运行它们的 CLI 版本一致。

在视频项目的目录里跑项目本地安装；从 HyperFrames 仓库检出里跑 `npx hyperframes skills update` 是全局安装：项目本地安装目标可能和已跟踪的 `skills/` 源码重叠，覆盖掉未提交的编辑。

试试这样的提示词：

> Using `/hyperframes`, create a 10-second product intro with a fade-in title, a background video, and subtle background music.

skill 教 agent 的 HyperFrames 生产循环是：规划视频、写合法的 HTML、接上可定位动画、加媒体、检查、预览、渲染。支持 Claude Code、Codex、Cursor、Gemini CLI、IBM Bob 和其他支持 skill 的编程助手。

## Skills

HyperFrames 带 9 个 skill。想做任何视频，问一声就行；`/hyperframes` 这个 skill 拿着契约和参考资料（影片、字幕、叠加层、动效、外观），先读它。

核心集（原文 Core set 翻译）：

| Skill | 用在什么时候 |
| --- | --- |
| `/hyperframes` | 任何做、改、动画化或渲染视频、动态图形、字幕或叠加层的需求，**先读它**。拿着渲染契约和完整工作流，并指向格式、动效、外观、字幕、整片和分镜的参考资料。 |
| `/hyperframes-cli` | 按任务分的 HyperFrames CLI：脚手架、检查、看帧、改时间轴、预览、本地或云端渲染、发布、项目历史，外加读它的 JSON 和从构建或渲染失败中恢复。 |
| `/hyperframes-registry` | 约 450 个现成的块和组件，以可编辑源码的形式安装：转场、叠加层、标题、动态文字、字幕、图表、地图、3D、镜头移动。手写之前先查有没有现成的；也用于 `hyperframes add` 和目录浏览。 |
| `/media-use` | 为视频找或做任何媒体：音乐、音效、图片、图标、logo、配音、虚拟人和生成视频、字幕、抠图、调色和外观，用 HeyGen 或免费本地工具，并混音。画面发暗、发平、发闷时也用它。 |

按需安装（原文 On demand 翻译）：

| Skill | 用在什么时候 |
| --- | --- |
| `/figma` | 把 Figma 带进视频：渲染好的素材、品牌 token、组件、分镜帧重建成动态、着色器和连接器辅助动效。粘贴 figma.com 链接时用。 |
| `/slideshow` | 演示文稿、路演、交互式 deck：离散幻灯片、片段揭示、分支、热点导航、带讲者备注的演示模式。输出是可导航的 deck，不是渲染好的 MP4。 |
| `/remotion-to-hyperframes` | 把已有的视频代码或素材带进 HyperFrames（先支持 Remotion，也支持 Motion Canvas、Lottie、Three.js、canvas 和其他工具的渲染结果），逐帧验证。 |
| `/reverse-any-video` | 把任何视频文件重建成可编辑的 HyperFrames 项目（动态图形、 talking head、实拍、AI 生成素材），逐帧对照原片检查。HyperFrames Pro。 |
| `/style-sampling` | 用五种已验证风格之一，按你的主题做新一集：拼贴解说、财经解说、动画科学解说、3D 品牌解说、3D 真实犯罪。HyperFrames Pro。 |

视觉设计交接流程见 Claude Design 指南和 Open Design 指南。

手动用 CLI（原文 Manually with the CLI 翻译）：

```bash
npx hyperframes init my-video
cd my-video
npx hyperframes preview      # 浏览器里预览，带实时重载
npx hyperframes render       # 渲染成 MP4
```

**前置要求：Node.js 22+、FFmpeg。**

能做什么（原文 What You Can Build 翻译）：想找灵感去 Showcase 看成品视频，可以看、可以读、可以跑、可以改。

- 产品发布视频和功能公告
- 带动画代码 diff、旁白和字幕的 PR 讲解
- 数据可视化、图表竞赛和地图动画
- 带动态字幕、叠加层和音乐的社媒视频
- 文档转视频、PDF 转视频和网站导览解说
- 自动化内容管线里复用的动态图形

frame.md（原文 Frame.md 翻译）：**frame.md——为视频准备好的设计系统。**

每个品牌都有一份 `design.md`，但没有一份是为镜头写的。`frame.md` 是缺失的翻译层：它拿你的网页上下文设计规范，为画面做一次反转——同样的 token、同样的规则，但重写成 AI agent 能直接用它拼宣传视频的样子，不用猜尺寸、不用碰网页 chrome。

输出是一份 `DESIGN.md` 超集，整个工具链都能读。原子保持神圣，组合保持自由，数字来自脚本。

工作原理（原文 How It Works 翻译）：把视频定义成 HTML。用 data 属性写时间和轨道。用 GSAP、CSS、Lottie、Three.js、Anime.js、WAAPI 或你自己的帧适配器做可定位动画。

```html
<div id="stage" data-composition-id="launch" data-start="0" data-width="1920" data-height="1080">
  <video
    class="clip"
    data-start="0"
    data-duration="6"
    data-track-index="0"
    src="intro.mp4"
    muted
    playsinline
  ></video>
  <h1 id="title" class="clip" data-start="1" data-duration="4" data-track-index="1">Launch day</h1>
  <audio
    data-start="0"
    data-duration="6"
    data-track-index="2"
    data-volume="0.5"
    src="music.wav"
  ></audio>
</div>
```

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。官网是 hyperframes.heygen.com，桌面应用在 hyperframes.studio。

### 方式一：跟 AI 编程助手一起用（推荐）

Claude Code 装插件：

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

其他助手用独立 skill：

```bash
npx skills add heygen-com/hyperframes
```

agent 和非交互运行要用下面这条，它只装核心集，和 CLI 版本一致：

```bash
npx hyperframes skills update
```

装完直接跟 agent 说，比如“用 `/hyperframes` 做一个 10 秒的产品介绍，标题淡入、背景视频、轻音乐”。

### 方式二：手动用 CLI

前置要求：Node.js 22+、FFmpeg。

```bash
npx hyperframes init my-video
cd my-video
npx hyperframes preview      # 浏览器里预览，带实时重载
npx hyperframes render       # 渲染成 MP4
```

### 方式三：桌面应用

从 hyperframes.studio 下载桌面应用：macOS、Windows、Linux（.deb）都有。

## 配置说明

- skill 安装：`npx skills add heygen-com/hyperframes` 打开交互选择器，默认只装 Core Skills（核心技能组）；`/figma`、`/slideshow`、`/remotion-to-hyperframes`、`/reverse-any-video` 按需安装；agent 和非交互运行用 `npx hyperframes skills update` 只装核心集。
- 插件自动更新：Claude Code 里跑 `/plugin`，选 Marketplaces → hyperframes → Enable auto-update。
- 渲染契约：做视频前先读 `/hyperframes` 这个 skill，它拿着渲染契约和完整工作流（规划、写 HTML、接动画、加媒体、检查、预览、渲染）。
- 组件库：`/hyperframes-registry` 里有约 450 个现成块和组件（转场、叠加层、标题、动态文字、字幕、图表、地图、3D、镜头移动），手写之前先查。
- frame.md：品牌的设计规范要先过一遍 `frame.md` 翻译成视频版，输出是 `DESIGN.md` 超集，整个工具链都能读。

## 注意事项

- 前置要求 Node.js 22+ 和 FFmpeg，版本不够先升级再跑。
- `/reverse-any-video` 和 `/style-sampling` 是 HyperFrames Pro 功能，开源版没有。
- `skills add` 解析的注册表可能比 `main` 分支慢几个小时，skill 和 CLI 版本对不上时用 `npx hyperframes skills update` 从发布标签重装。
- 在 HyperFrames 仓库检出里跑项目本地安装可能覆盖 `skills/` 源码里未提交的编辑，那种情况用全局安装。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/heygen-com/hyperframes
- 原 README：https://github.com/heygen-com/hyperframes#readme
- 官网：https://hyperframes.heygen.com
- 桌面应用：https://hyperframes.studio

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 Apache-2.0。
