# skills：给真正干工程的人准备的 agent 技能合集

- 原项目：mattpocock/skills
- 原项目链接：https://github.com/mattpocock/skills
- 榜单：日榜 2026-11-06 第 2 名
- 翻译日期：2026-11-06
- 原项目许可：MIT
- 原项目数据（2026-11-06 核对）：Star 315,970，Fork 26,440，创建于 2026-02-03

## 一句话介绍

Matt Pocock 每天真刀真枪写工程用的 agent 技能合集，直接从他的 `.agents` 目录里拿出来的：小、可改、可组合，目标不是 vibe coding，是正经做应用。

## 适合谁

- 每天用 Claude Code、Codex、Copilot、Gemini CLI 这类编程 agent 写代码的人
- 觉得 agent 经常答非所问、话太多、代码跑不起来、越写越乱的人
- 不想被重流程框架绑住、想自己掌控开发过程的人

## 它解决什么问题

- 做真正的应用很难。GSD、BMAD、Spec-Kit 这类流程框架想帮忙，但它们接管了整个过程，也拿走了你的控制权，流程本身出 bug 还很难修。
- 这些技能反其道而行之：小、容易改、可组合，适用于任何模型，浓缩了几十年的工程经验。作者的意思是：拿去折腾，改成你自己的。
- 它针对的是 agent 最常见的四个翻车点，一个一个给解法。

## README 翻译（核心部分）

### 为什么有这些技能：四个翻车点

**#1：Agent 没按你要的做**

原文引《程序员修炼之道》："没有人确切知道自己想要什么。"软件开发里最常见的失败就是错位：你以为开发懂你要什么，看到做出来的东西才发现完全没理解。AI 时代也一样，你和 agent 之间有个沟通鸿沟。

解法是**烤问（grilling session）**：动手前让 agent 详细追问你要做什么。对应两个技能：

- **`/grill-me`**：非代码场景也用，追问到底
- **`/grill-with-docs`**：同上，再加共享语言和 ADR（见 #2）

作者说这是他最受欢迎的技能，每次想改东西都用一次，先对齐、再深想。

**#2：Agent 话太多**

原文引《领域驱动设计》：有了通用语言，开发人员之间的对话和代码表达都源自同一个领域模型。项目一开始，开发和业务方往往说着不同的语言；agent 也一样，被丢进项目里自己摸索行话，1 个词能说清的要用 20 个词。

解法是**共享语言**：一份文档，帮 agent 破解项目里的行话。原文例子（作者 course-video-manager 仓库里的 glossary）：

- **改前**："There's a problem when a lesson inside a section of a course is made 'real' (i.e. given a spot in the file system)"
- **改后**："There's a problem with the materialization cascade"

好处不只是话少：变量、函数、文件命名一致，代码库对 agent 更好导航，agent 思考还省 token。作者说这可能是仓库里最酷的一个技巧，内建在 `/grill-with-docs` 里，烤问的同时帮你建共享语言、把难解释的决策写进 ADR。

**#3：代码跑不起来**

原文引《程序员修炼之道》："永远迈小而审慎的步子，反馈的速度就是你的速度上限，别接超出能力的大任务。"就算对齐了，agent 还是可能产出烂代码，问题出在反馈回路上：没有代码实际跑起来的反馈，agent 就是盲飞。

解法是常规的反馈回路：静态类型、浏览器访问、自动化测试。测试要红绿重构：先写失败的测试，再修测试。对应技能：

- **`/tdd`**：红绿重构循环，指导什么是好测试、什么是坏测试
- **`/diagnosing-bugs`**：调试的纪律循环，分阶段设卡：先让 bug 复现变红 → 缩小范围 → 假设 → 埋点 → 修 → 回归测试

**#4：写出一团泥**

原文引 Kent Beck："每天都在乎系统的设计。"和 John Ousterhout："最好的模块都很深，大量功能通过简单接口访问。"agent 让写代码变快，也让软件熵加速，代码库以前所未有的速度变复杂、难改。

解法是：从根本上在乎代码设计，内建在每一层技能里：

- **`/to-spec`**：写 spec 前先问你动了哪些模块
- **`/improve-codebase-architecture`**：扫描代码库找"加深模块"的机会，给一份可视化 HTML 报告，再烤问你选中的那一个。作者建议几天跑一次；注意它只是调查，不是救援，老代码库能找出真问题，但不会替你解开。

### 技能怎么分：用户调用 vs 模型调用

按谁能触发分两类：**用户调用**的技能只有你打字才能触发，负责编排；**模型调用**的技能你或 agent 都能用，任务合适时 agent 会自动取用，装的是可复用的纪律。用户调用的技能可以调模型调用的，但不能调另一个用户调用的。

**Engineering（写代码用的）——用户调用**

- **ask-matt**：问哪个技能或流程适合你当前的情况，相当于路由
- **grill-with-docs**：烤问，同时建项目领域模型、打磨术语，同步更新 `GLOSSARY.md` 和 ADR
- **triage**：把 issue 按分流角色的状态机往前推
- **improve-codebase-architecture**：扫描代码库找加深机会，给可视化 HTML 报告，再烤问你选中的项
- **setup-matt-pocock-skills**：给工程技能做配置（issue tracker、分流标签、文档放哪），每个仓库跑一次再用其他工程技能
- **to-spec**：把当前对话变成 spec，发到 issue tracker 上，不访谈，只综合已讨论的内容
- **to-tickets**：把计划、spec 或对话拆成一组 tracer-bullet 票，每张声明阻塞关系，可写本地文件或发到真实 tracker 上当原生阻塞链接
- **implement**：按 spec 或票实现，在约好的接缝处跑 `/tdd`，收尾跑 `/code-review` 再提交
- **implement-spec**：整份 spec 一个集成分支，把票当任务图，多路实现子 agent 并行跑，收尾跑 `/code-review`
- **wayfinder**：超大任务（一个 agent 会话装不下）先画成 issue tracker 上的决策票地图，一张一张解决，直到去目的地的路清晰
- **retro**：一次会话后给编程 agent 的环境提改进建议（导航、自动检查、编码标准、 steering 文件、工具），最严重的先说

**Engineering（写代码用的）——模型调用**

- **prototype**：为回答设计问题做抛弃式原型，单个可分享 HTML 文件（状态/逻辑问题），或同一路由下可切换的多个完全不同的 UI 方案
- **diagnosing-bugs**：疑难 bug 和性能回归的纪律诊断循环：先让 bug 复现变红 → 缩小范围 → 假设 → 埋点 → 修 → 回归测试
- **research**：对照高可信一手来源调查问题，写成带引用的 Markdown 文件存仓库里，后台 agent 跑
- **tdd**：红绿重构的测试驱动开发，一次做一个垂直切片
- **domain-modeling**：主动建设和打磨项目领域模型：拿术语对照 glossary 较真、用边界场景做压力测试，同步更新 `GLOSSARY.md` 和 ADR
- **codebase-design**：设计深模块的共享纪律和词汇：大量行为藏在小接口后面，放在干净的接缝处，能通过接口测试
- **code-review**：双轴评审：标准（是否遵守仓库编码标准，外加 Fowler 坏味道基线）和 Spec（是否忠实实现原始 issue/spec），两个并行子 agent 跑，互不干扰
- **pr**：PR 正文该有的样子：最小可视摘要、改动前后的证据、合并风险（一扇门还是两扇门、影响面多大）
- **wizard**：生成交互式 bash 向导，带人一步步走只有人能做的事：配基础设施、设凭证或 CI 密钥、走不熟的第三方后台、做一次性迁移或切换

**Productivity（通用工作流，不针对代码）——用户调用**

- **grill-me**：对一个计划或设计 relentless 追问，直到设计树的每个分支都解决
- **handoff**：把当前对话压成一份移交文档，让另一个 agent 接着干
- **teach**：多会话教用户新技能或新概念，拿当前目录当有状态的教学工作区
- **to-questionnaire**：把你一个人答不上来的决策变成 Markdown 问卷，发给能答的那个人，异步填或开会一起填；问的是发送的事（发给谁、要拿回什么），不是主题本身
- **wait-what**：消息没说明白时立刻触发，agent 用 `GLOSSARY.md` 里的词、plain English 把缺的那部分上下文重新讲一遍

**Productivity——模型调用**

- **grilling**： relentless 追问的原语，`grill-me`、`grill-with-docs`、`triage`、`wayfinder`、`improve-codebase-architecture` 背后共用的访谈机制
- **writing-for-agents**：给 agent 写文档：技能、AGENTS.md/CLAUDE.md，以及 agent 顺着指针能找到的任何文档

## 中文部署指南

**安装方式：二选一，别两个都装**

- 插件方式：插件会自己更新。`skills.sh` 方式：把可编辑的文件复制进你的项目，手动更新。两个都装会让每个技能出现两次。

**方式一：Claude Code（插件，默认自动更新）**

```bash
claude plugin install mattpocock-skills@claude-plugins-official
```

**方式二：Codex（启动时自动更新）**

```bash
codex plugin marketplace add mattpocock/skills
codex plugin add mattpocock-skills@mattpocock
```

**方式三：GitHub Copilot CLI 和 VS Code（每天更新）**

```bash
copilot plugin marketplace add mattpocock/skills
copilot plugin install mattpocock-skills@mattpocock
```

再在 `~/.copilot/settings.json` 里加一次：

```json
{
  "extraKnownMarketplaces": {
    "mattpocock": { "source": { "source": "github", "repo": "mattpocock/skills" }, "autoUpdate": true }
  }
}
```

VS Code 里跑 **Chat: Install Plugin From Source**，填 `https://github.com/mattpocock/skills`。

**方式四：Gemini CLI（手动更新）**

```bash
gemini skills install https://github.com/mattpocock/skills.git --path skills/engineering
gemini skills install https://github.com/mattpocock/skills.git --path skills/productivity
```

更新时把两条命令重跑一遍。

**方式五：其他 agent，或要可编辑的文件（手动更新）**

```bash
npx skills@latest add mattpocock/skills -a <agent>  # cursor, opencode, devin, windsurf, amp, pi；不加 -a 会让选
```

安装时问你要哪些技能，记得选上 `setup-matt-pocock-skills`。更新时跑 `npx skills@latest update`，再重跑 `add` 拿新技能。

**装完第一步：每个仓库跑一次**

在 agent 里跑 `/setup-matt-pocock-skills`，它会问你三件事：issue tracker 用哪个（GitHub、GitLab、本地文件，或你自己描述的）、triage 时给票打什么标签、建出来的文档放哪。

## 配置说明

- 插件方式默认自动更新（Codex 是启动时更新，Copilot 是每天更新）；`skills.sh` / `npx skills` 方式是把文件复制进项目，手动更新。
- 每个仓库用之前先跑一次 `/setup-matt-pocock-skills` 做配置，否则工程技能不知道 issue 和文档放哪。
- 技能本身是作者日常实战的沉淀，鼓励按自己项目改：小、可改、可组合是设计初衷。

## 注意事项

- 作者明确说：这些技能是他把软件工程基本功浓缩成可重复做法的尝试，基本功在 AI 时代比以前更重要，不是更不重要。
- `/improve-codebase-architecture` 只是调查，不是救援：老代码库能找出真问题，但不会替你解开。
- 技能分用户调用和模型调用两类，用户调用的技能不能调另一个用户调用的技能，别指望一个命令串起整条用户流程。
- 是否实测：按原项目 README 文档整理，未实测。
