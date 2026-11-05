# Superpowers：给编程 agent 配一套真正的软件开发方法论

- 原项目：obra/superpowers
- 原项目链接：https://github.com/obra/superpowers
- 榜单：周榜 2026-11-05 第 5 名
- 翻译日期：2026-11-05
- 原项目许可：MIT
- 原项目数据（2026-11-05 核对）：Star 312,662，Fork 27,813，创建于 2025-10-09

## 一句话介绍

一套完整的 agent 软件开发方法论加可组合的技能库：装上之后，你的编程 agent 不再接到任务就直接写代码，而是先问清你要什么、给你看设计、做实现计划、按 TDD 让子 agent 分工实现，全程自带评审。

## 适合谁

- 每天用 Claude Code、Cursor、Codex、Gemini CLI 这类编程 agent 写代码的人
- 觉得 agent 经常"自作主张写一堆、跑偏了才发现"的人
- 想让 agent 按正规流程（需求 → 设计 → 计划 → 实现 → 评审）干活的个人和团队

## 它解决什么问题

- Agent 的默认行为是接到任务直接写代码：不问你要什么、设计不给你看、没有实现计划、测试靠后，返工全靠你人肉发现。
- 不同 agent 各有一套习惯，没有统一、经过验证的开发方法论。
- Agent 一次自主干几个小时很常见，没有流程兜底，跑偏了就是几小时白干。

Superpowers 的做法是：把一套方法论做成一组技能，再加一点启动指令确保 agent 真用它们。技能自动触发，你不用特别做什么，你的 agent 就"有了超能力"。

## README 翻译（核心部分）

### 它怎么工作（原文 How it works 翻译）

从你启动编程 agent 那一刻开始。它看到你在构建东西时，**不会**直接跳进去写代码，而是先退一步，问你到底想做什么。

等它从对话里把需求抠出来，会分段展示给你看，短到你真的能读完、能消化。设计你点头之后，agent 再做一份实现计划，细到"一个热情但品味差、不懂项目上下文、还讨厌写测试的初级工程师也能照着做"，强调真正的红绿 TDD、YAGNI（You Aren't Gonna Need It：不需要的别做）和 DRY。

你说"开始"之后，它启动**子 agent 驱动开发**流程：派 agent 一个任务一个任务做，每步检查、评审，再继续往前。Agent 连续自主工作几个小时不跑偏，是常有的事。

### 基本工作流（原文 The Basic Workflow 翻译）

1. **brainstorming（头脑风暴）**：开工前激活。通过提问把你真正想要什么、为什么要，抠出来，再把它的理解复述给你纠正。小改动在聊天里定；大项目写成一份设计文档，细到 builder 能直接拿去做计划。
2. **using-git-worktrees（用 git worktree）**：设计通过后激活。开隔离工作区、新分支，跑项目初始化，验证测试基线是干净的。
3. **writing-plans（写计划）**：设计通过后激活。把活拆成 2–5 分钟一个的小任务，每个任务写清准确的文件路径、完整代码、验证步骤。
4. **subagent-driven-development（子 agent 驱动开发）或 executing-plans（执行计划）**：有计划后激活。二选一：前者每个任务派一个全新的子 agent，做完评审一次，最彻底；后者同一会话内全部做完、最后统一评审一次整个分支，最省。
5. **test-driven-development（测试驱动开发）**：实现过程中激活。强制 RED-GREEN-REFACTOR：先写失败的测试、看它失败、写最少代码、看它通过、提交。测试之前写的代码删掉。
6. **requesting-code-review（请求代码评审）**：任务之间激活。对照计划评审，按严重程度报告问题，严重问题会阻塞进度。
7. **finishing-a-development-branch（收尾开发分支）**：任务完成时激活。验证测试，给出选项（合并 / 提 PR / 保留 / 丢弃），清理 worktree。

**Agent 在做任何任务之前都会先检查有没有相关的技能。这是强制流程，不是建议。**

### 技能库（原文 What's Inside 翻译）

**测试**

- **test-driven-development**：红绿重构循环（附测试反模式参考）

**调试**

- **systematic-debugging**：四阶段根因定位流程（附根因追踪、纵深防御、按条件等待等技术）
- **verification-before-completion**：确认真的修好了再收尾
- **diagnosing-superpowers**：查清一次会话里哪里出了问题，拿证据说话；可以导出一份脱敏材料或直接提 issue

**协作**

- **brainstorming**：开工前把意图抠出来
- **writing-plans**：详细的实现计划
- **executing-plans**：同一会话内执行计划，最后统一评审一次
- **dispatching-parallel-agents**：并行派子 agent 的工作流
- **requesting-code-review**：评审前的检查清单
- **receiving-code-review**：回应评审意见
- **using-git-worktrees**：并行开发分支
- **finishing-a-development-branch**：合并 / PR 的决策流程
- **subagent-driven-development**：两段式评审的快速迭代（先合规、再代码质量）

**元技能**

- **writing-skills**：按最佳实践创建新技能（附测试方法）
- **using-superpowers**：技能系统的入门介绍

### 理念（原文 Philosophy 翻译）

- **测试驱动开发**：永远先写测试
- **系统化胜过随手猜**：流程胜过猜测
- **降低复杂度**：简单是首要目标
- **证据胜过断言**：宣布成功之前先验证

### 出问题时怎么办（原文 When Something Goes Wrong 翻译）

有时候一次会话会失控：技能该触发时没触发、不该触发时触发了，或者 agent 不按计划走、重复劳动、烧掉比预期多的 token。这时让你的编程 agent"查一下这次会话里 superpowers 哪里出了问题"，它会调用 **diagnosing-superpowers** 技能，读会话记录、按行给证据；如果你愿意，它还会打包一份脱敏材料用来提 bug 报告。查更早的会话时，直接报会话 id 就行。

### 作者与商业支持

Superpowers 由 Jesse Vincent 和 Prime Radiant 团队开发。企业用户需要商业支持、额外工具或托管服务，可以联系 sales@primeradiant.com。

### 遥测说明

因为技能和插件不给作者任何反馈，作者不知道有多少人在用 Superpowers。默认情况下，brainstorming 的可选可视化小伙伴功能会从官网加载 Prime Radiant 的 logo，其中包含你用的 Superpowers 版本号，不包含你的项目、提示词或编程 agent 的任何细节，看不到你的点击和你在构建什么。这只是为了大致了解用的人数和版本。完全可选：把环境变量 `SUPERPOWERS_DISABLE_TELEMETRY` 设为任意 true 值即可关掉。Superpowers 也认 Claude Code 的 `DISABLE_TELEMETRY` 和 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`。

## 中文部署操作指南

按原项目 README 整理，未实测，请以原项目最新文档为准。不同 harness 安装方式不同，用几个就各装一次。

### 方式一：Claude Code（官方市场）

在 Claude Code 里执行：

```
/plugin install superpowers@claude-plugins-official
```

或用 Superpowers 自己的市场（还附带几个相关插件）：

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### 方式二：Cursor

在 Cursor Agent 聊天里执行：

```
/add-plugin superpowers
```

或在插件市场里搜 "superpowers" 安装。

### 方式三：Gemini CLI

```bash
gemini extensions install https://github.com/obra/superpowers
```

更新：

```bash
gemini extensions update superpowers
```

### 方式四：OpenCode

直接告诉 OpenCode：

```
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
```

详细文档见仓库 `docs/README.opencode.md`。

### 方式五：Kimi Code

打开 Kimi Code 的插件管理（`/plugins`），进 Marketplace 找 Superpowers 安装；或直接执行：

```
/plugins install https://github.com/obra/superpowers
```

### 方式六：其他 harness

- **Codex App / Codex CLI**：官方 Codex 插件市场里有，App 里点侧栏 Plugins 找 Superpowers，CLI 里用 `/plugins` 搜索安装。
- **Qwen Code**：`qwen extensions install obra/superpowers`。
- **Pi**：`pi install git:github.com/obra/superpowers`。
- **Devin CLI**：`devin plugins install obra/superpowers`。
- **GitHub Copilot CLI**：先 `copilot plugin marketplace add obra/superpowers-marketplace`，再 `copilot plugin install superpowers@superpowers-marketplace`。
- **Factory Droid**：先 `droid plugin marketplace add https://github.com/obra/superpowers`，再 `droid plugin install superpowers@superpowers`。
- **Antigravity**：`agy plugin install https://github.com/obra/superpowers`。
- **Grok Build CLI**：`grok plugin install superpowers@xai-official --trust`。
- **Hermes Agent**：`hermes plugins install obra/superpowers --enable`，装完重启会话。
- **Muse**：`muse plugins install ./`（本地 checkout）或克隆后安装，再 `muse plugins approve superpowers`，装完重启会话。

### 验证装好了没有

开一个新会话，发一句 `Let's make a react todo list`：装好了的话，写代码之前会自动先触发 `brainstorming`，而不是直接开写。

## 配置说明

- 装完重启一次会话，让 SessionStart hook 生效；技能本身装完立刻可用，hook 需要首次安装时批准。
- 更新方式因 harness 而异，多为自动更新。
- 遥测可选关闭：设 `SUPERPOWERS_DISABLE_TELEMETRY` 为 true。

## 注意事项

- 贡献规则：一般不接受新技能投稿；技能改动必须在所有支持的编程 agent 上都能用；不接受 agent 代写的 PR（哪怕你遇到了同一个 issue，也请把报告追加到已有的 issue 里，而不是让 agent 替别人修）。
- 技能行为测试用 `superpowers-evals` 的 drill 评估框架，见仓库 `evals/README.md`。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/obra/superpowers
- 原 README：https://github.com/obra/superpowers#readme
- 发布公告原文：https://blog.fsck.com （见原 README Philosophy 一节的链接）

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 MIT。
