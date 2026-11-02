# hallmark：让 AI 做的网页不再一眼像 AI 生成的

- 原项目：Nutlope/hallmark
- 原项目链接：https://github.com/Nutlope/hallmark
- 榜单：周榜 2026-11-02 第 1 名
- 翻译日期：2026-11-02
- 原项目许可：MIT
- 原项目数据（2026-11-02 核对）：Star 45,311，Fork 2,406，创建于 2026-04-27

## 一句话介绍

一个给 Claude Code、Codex、Cursor、OpenCode 用的设计 skill：让 AI 做出来的网页不再一眼就是 AI 味，做出像真人设计师做的页面。

## 适合谁

- 用 Claude Code 等 AI 工具做落地页、官网、产品页的人
- 每次 AI 出来的页面都长一个样：紫色渐变、小标题上面一排英文、每段一个 emoji、留白全是空框框，想改掉这种 AI 味的人
- 想让 AI 按真实产品、真实内容、真实图片来做页面，而不是编假数据充数的人

## 它解决什么问题

AI 做网页最常见的毛病，原文叫 AI slop，大概就是一眼假：标题上面总有一行小英文眉题、标签全是大写字母加宽间距、标题里总有一个词被标成彩色、一页全是空框框或者全是照片、首屏大图撑不满一屏、每页结尾都放一个邮箱订阅、表单点了只说谢谢却什么都没发。

hallmark 的做法是先定一条不可突破的底线，再给 AI 发 50 套设计主题让它选，最后用真浏览器检查一遍，还要找一个没看过之前过程的评审再看一遍。

## README 翻译（核心部分）

原文第一句是：A design skill for Claude Code, Codex, Cursor and OpenCode that refuses to look AI-generated，翻译就是：一个拒绝长得像 AI 生成的设计 skill。

原文核心说法翻译如下：

> Hallmark 先守住一条硬底线，然后就让开。它会从 50 种材料的目录里发三套主题，按访客要来干什么来搭建页面，再用真浏览器检查那些一眼就能看出是机器做的痕迹：每个标题上面的眉题、大写加宽的标签、标题里一个变色的词、一页空框框或只有照片、撑不满一屏的首屏、每页结尾的邮箱订阅、点了只说谢谢却什么都没发的表单。最后由一个全新上下文的评审做最后把关。

检查分三档：

- Floor（底线）：永远不能上线，包括对比度、焦点、减弱动效、编造事实、手机布局坏掉。
- Reflex（本能）：AI 默认会掉进去的坑，有理由可以在记录里写明原因后推翻。
- Finish（收尾）：工艺细节，从不因为这个卡住不让上线。

v2 新内容（原文 New in v2 翻译）：

- 50 套主题：每套都是一种材料（纸张、字体、颜色、表面、自己的组件和质感），附一张成品页图片，AI 在这个材料里自己排版。
- 按活来建：预订页就要能预订、商店就要能卖东西、 newsletter 就要能订阅，核心操作放在这个品类该放的位置，页面以这个操作收尾。
- Custom：说 custom 就不用主题了，只留底线、检查规则和一段简短指引，让 AI 找到一个只有这个客户才有的想法，并让这个想法主导整页。
- 真实产品：指给它一个网址、开发服务器或应用，它自己截图。
- 真实照片：755 张公开许可的照片，按主题挑选，页面上会署名。
- Redesign 和 audit：`/hallmark redesign <路径>` 会重建页面并保留内容和接线，`/hallmark audit <路径>` 只出报告不改东西。

主题是什么：原文说主题是一种材料，不是一套方案，它从不规定页面里放什么、按什么顺序放，所以同一个主题、两个不同的提示会做出两张不同的页面。每套主题是一个不超过 8 KB 的文件，在 `references/themes/` 里，旁边配一张图。一次搭建只读其中一套。

搭建流程（原文 How a build runs 翻译）：

1. 预检先读项目（字体、配色、框架、一份锁定的 `design.md`），只问一次要什么材料：照片、截图、真实数字，什么都不编。
2. `scripts/theme.mjs deal` 发三套符合提示又过得了检查的主题，`draw` 按页面的活来定页面结构。
3. 首屏单独先做出来、渲染、冷评审通过后，再做页面其余部分。
4. `scripts/sloplint.mjs --render` 在 8 个宽度下检查页面，再由一个子代理用全新视角复查。
5. 每页都是自包含的 HTML 和 CSS，在第一行 CSS 注释里盖章，写清它做了哪些决定。

Redesign（原文 Redesign 翻译）：

hallmark 不会主动动已有设计，除非你点名。完整重设计保留内容和接线，只换系统和布局；说 keep the layout 就是只换样式，polish 就是只修那些 AI 味。`sloplint --before` 先把每个链接、字段、处理函数和标题记下来，`sloplint --kept` 会在重设计丢了其中任何一个时报错，最后交一份改前改后对照。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。主题预览站是 usehallmark.com。

### 方式一：一条命令安装（推荐）

```bash
npx skills add nutlope/hallmark -g
```

`-g` 是装给所有项目，不加就是只装进当前项目。需要 Node 18 或更高版本。

浏览器检查（`sloplint --render`、截图）还需要另外装：

```bash
npm i -g puppeteer-core
```

同时电脑上要有 Chrome。没有这两样时，静态检查照样能跑。

### 方式二：只装给某一个编程工具

只装给一个工具时，在上面那条命令后面加 `--agent`：

```bash
npx skills add nutlope/hallmark -g --agent claude-code
```

把 `claude-code` 换成 `codex`、`opencode`、`cursor`、`github-copilot` 就是装给对应工具。

各工具的安装位置和调用方式（原文表格翻译）：

| 工具 | 装到哪里 | 怎么叫它 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/hallmark` | `/hallmark <提示>`，或者直接描述要做什么 |
| Codex CLI | `~/.agents/skills/hallmark` | `$hallmark <提示>`，或者直接描述要做什么 |
| Cursor | 会找到上面两处 | `/hallmark <提示>`，或者直接描述要做什么 |
| OpenCode | 会找到上面两处 | `/hallmark <提示>`，或者直接描述要做什么 |

### 方式三：装成 Claude Code 插件

在 Claude Code 里依次输入：

```bash
/plugin marketplace add nutlope/hallmark
/plugin install hallmark@hallmark
```

装完后调用方式是 `/hallmark:hallmark`。

### 方式四：从克隆的仓库安装

```bash
node skills/hallmark/scripts/install.mjs
```

这条命令会在复制前验证所有主题和参考文件。`install-hook.mjs` 会给 Claude Code 加一个编辑时检查底线的钩子。

检查任意页面，不用先搭建：

```bash
node skills/hallmark/scripts/sloplint.mjs <文件或目录> --render
```

## 配置说明

- 没有要填的密钥和账号，装完就能用。
- 做新页面时直接说需求就行，例如：`use hallmark to build ...`。如果它没有自己启动，就点名叫它。
- 想重设计已有页面：`/hallmark redesign ./src/app`，只出报告不改东西：`/hallmark audit ./index.html`。
- 主题在 `references/themes/` 里，每套一个不超过 8 KB 的文件加一张图。想看全部 50 套去 usehallmark.com。

## 注意事项

- 浏览器检查要 Chrome 和 puppeteer-core，没有也能用，但渲染检查和截图这两项跑不了。
- 照片库说明：`skills/hallmark/scripts/photos.json` 列的是 Wikimedia Commons 上托管的照片，库里不存图片文件。每张照片保持自己的许可（CC0、公有领域、CC BY 或 CC BY-SA），hallmark 会在页面上给每张用的照片署名。它不用 Unsplash、Pexels、Pixabay 这类图库，因为那些站的条款不让 AI 工具挑图。
- 它不会编造内容：做页面要用的照片、截图、真实数字，预检时会先问你要，拿不到就不会自己编。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/Nutlope/hallmark
- 原 README：https://github.com/Nutlope/hallmark#readme
- 主题预览：https://www.usehallmark.com

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 MIT。
