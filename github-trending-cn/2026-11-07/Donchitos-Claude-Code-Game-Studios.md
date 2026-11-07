# Claude Code Game Studios：把 Claude Code 变成一间完整游戏工作室

- 原项目：Donchitos/Claude-Code-Game-Studios
- 原项目链接：https://github.com/Donchitos/Claude-Code-Game-Studios
- 榜单：周榜 2026-11-07 第 2 名（顺推；本周第 1 名 claude-mem 已翻译）
- 翻译日期：2026-11-07
- 原项目许可：MIT
- 原项目数据（2026-11-07 核对）：Star 36,282，Fork 4,778，创建于 2026-02-12，Release 10 个

## 一句话介绍

把一个 Claude Code 会话变成一间完整游戏开发工作室：49 个 AI agent、74 个工作流技能、一套照着真实工作室层级搭的协作系统。

## 适合谁

- 想一个人用 AI 做游戏的独立开发者
- 用 Claude Code 写游戏、但觉得单个会话没结构、越写越乱的人
- Godot、Unity 或 Unreal 引擎的游戏开发者
- 想给 AI 开发流程加上设计评审、QA、版本管理这些"工作室规矩"的人

## 它解决什么问题

- 一个人跟 AI 做游戏很强，但单个聊天会话没有结构：没人拦着你写死魔法数字、跳过设计文档、写面条代码；没有 QA、没有设计评审、没人问"这真的符合游戏愿景吗？"
- 这个项目给 AI 会话套上真实工作室的结构：49 个专业 agent 按工作室层级组织——总监把控愿景、部门负责人管各自领域、专员干具体活。每个 agent 有明确职责、升级路径和质量关卡。
- 结果是：决策还是你做，但现在有一支团队会问对的问题、早发现错误、从第一次头脑风暴到上线全程保持项目有序。

## README 翻译（核心部分）

### 包含什么

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| **Agents** | 49 | 横跨设计、编程、美术、音频、叙事、QA、制作的专业子 agent |
| **Skills** | 74 | 每个工作流阶段的斜杠命令（`/start`、`/design-system`、`/create-epics`、`/create-stories`、`/dev-story`、`/story-done` 等） |
| **Hooks** | 15 | 提交、推送、资源变更、设计文档读写、注册表、会话生命周期、agent 审计轨迹、缺口检测时的自动校验 |
| **Rules** | 14 | 编辑玩法、引擎、AI、UI、网络代码、场景和资源文件时强制执行的路径级编码标准 |
| **Templates** | 62 | GDD（游戏设计文档）、UX 规范、ADR（架构决策记录）、冲刺计划、HUD 设计、无障碍等文档模板 |

注：仓库简介里写的是"72 个工作流技能"，README 正文和徽章写的是 74 个，以 README 正文为准（74 个）。

### 工作室层级

Agent 按三层组织，和真实工作室的运作方式一致：

```
Tier 1 — 总监（Directors）
  creative-director    technical-director    producer
Tier 2 — 部门负责人（Department Leads）
  game-designer        lead-programmer       art-director
  audio-director       narrative-director    qa-lead
  release-manager      localization-lead
Tier 3 — 专员（Specialists）
  gameplay-programmer  engine-programmer     ai-programmer
  network-programmer   tools-programmer      ui-programmer
  systems-designer     level-designer        economy-designer
  technical-artist     sound-designer        writer
  world-builder        ux-designer           prototyper
  performance-analyst  devops-engineer       analytics-engineer
  security-engineer    qa-tester             accessibility-specialist
  live-ops-designer    community-manager
```

每个 agent 在自己的 frontmatter 里声明用什么模型：三位总监要求 Opus，`lead-programmer` 和 15 位专员指定 Sonnet，剩下 30 位继承你当前会话的模型。层级代表的是角色资历，不是账单方案——工作室大部分成员跑的就是你本来在用的模型。

### 引擎专员

模板为三大主流引擎都准备了 agent 组合，用哪个引擎就用哪套：

| 引擎 | 负责人 Agent | 下属专员 |
| --- | --- | --- |
| **Godot 4** | `godot-specialist` | GDScript、Shaders、GDExtension |
| **Unity** | `unity-specialist` | DOTS/ECS、Shaders/VFX、Addressables、UI Toolkit |
| **Unreal Engine 5** | `unreal-specialist` | GAS、蓝图、Replication、UMG/CommonUI |

### 斜杠命令

在 Claude Code 里输入 `/` 就能调用全部 74 个技能：

- **上手与导航**：`/start`、`/help`、`/project-stage-detect`、`/setup-engine`、`/adopt`、`/settings`
- **游戏设计**：`/brainstorm`、`/map-systems`、`/design-system`、`/quick-design`、`/review-all-gdds`、`/propagate-design-change`
- **美术与资源**：`/art-bible`、`/asset-spec`、`/asset-audit`
- **UX 与界面设计**：`/ux-design`、`/ux-review`
- **架构**：`/create-architecture`、`/architecture-decision`、`/architecture-review`、`/create-control-manifest`
- **故事与冲刺**：`/create-epics`、`/create-stories`、`/dev-story`、`/sprint-plan`、`/sprint-status`、`/story-readiness`、`/story-done`、`/estimate`
- **评审与分析**：`/design-review`、`/code-review`、`/balance-check`、`/content-audit`、`/scope-check`、`/perf-profile`、`/tech-debt`、`/gate-check`、`/consistency-check`、`/security-audit`
- **QA 与测试**：`/qa-plan`、`/smoke-check`、`/soak-test`、`/regression-suite`、`/test-setup`、`/test-helpers`、`/test-evidence-review`、`/test-flakiness`、`/skill-test`、`/skill-improve`
- **制作**：`/milestone-review`、`/retrospective`、`/bug-report`、`/bug-triage`、`/reverse-document`、`/playtest-report`
- **发布**：`/release-checklist`、`/launch-checklist`、`/changelog`、`/patch-notes`、`/hotfix`、`/day-one-patch`
- **创意与内容**：`/prototype`、`/vertical-slice`、`/onboard`、`/localize`
- **团队编排**（多个 agent 协作做一个功能）：`/team-combat`、`/team-narrative`、`/team-ui`、`/team-release`、`/team-polish`、`/team-audio`、`/team-level`、`/team-live-ops`、`/team-qa`

### 它产出的是游戏，还是文档？

这是个好问题，答案是一次测量，而不是一个示例项目。

作者用同一个简报、在不同的 `modes.rigor` 级别下各做了一款游戏，数了每款游戏在写下第一行游戏代码之前写了多少文档：

| `modes.rigor` | 写第一行代码前的文档数 | 耗时 |
| --- | --- | --- |
| `minimal` | **1**（一页简报） | 0 分钟 |
| `standard` | 30 | 58 分钟 |

四款游戏都做出来了、能跑、测过。两位盲审评审加一位真人试玩之后，把 `standard` 那款排在了**最后**——多写的 29 份文档换来的是可追溯性，不是一款更好的游戏。

### 它会运行游戏并亲眼看一看

上面那组数字说的是成本。另一半是东西到底能不能用，对游戏来说就意味着得有人**看一眼**——测试通过说明不了菜单是不是画出屏幕外了。所以，任何一个改动了玩家能看到的东西的故事，在游戏被启动、被观察、截图留存在 `production/qa/evidence/` 之前，都不算完成。只做解析检查不算运行。

这条在所有 rigor 级别都成立，包括 `minimal`——`minimal` 下自动化测试可以免掉，但"看一眼"不能免。

游戏本身特意**不随仓库发货**：这是你用来开自己项目的模板，别人的游戏放在你的仓库里是杂物，不是证据。

## 中文部署操作指南

### 前置要求

- Git
- Claude Code：推荐用原生安装器（`npm install -g @anthropic-ai/claude-code` 也行，需要 Node.js 22+）
- Python 3：用来读每个技能和 hook 的 `project.yaml`，没有它所有设置都会静默回落到默认值
- Bash：跑所有 hook；macOS 和 Linux 自带，Windows 随 Git for Windows 提供
- 推荐装 `jq`（做 hook 校验用）

Hook 在可选工具缺失时会优雅降级——只是丢掉校验——只有一个例外：如果提交里暂存了数据 JSON、而没有 Python 来校验它，提交会被拦截。

### 方式一：本地运行

```bash
git clone https://github.com/Donchitos/Claude-Code-Game-Studios.git my-game
cd my-game
```

然后在项目根目录（放着 `CLAUDE.md` 和 `project.yaml` 的那一级）打开 Claude Code，开始会话：

```bash
claude
```

注意：在 `src/` 这样的子目录里启动会跳过项目的 hook、拒绝规则和"先问再做"的权限模式。

进去后跑 `/start`，系统会问你现在处在哪个阶段（完全没想法、概念模糊、设计清晰、已有成果），再把你带到对的工作流，不做假设。

也可以直接跳到某个技能：

- `/brainstorm`：从零探索游戏点子
- `/setup-engine godot 4.7`：已经知道用什么引擎就直接配好
- `/project-stage-detect`：分析已有项目

## 配置说明

项目根目录的 `project.yaml` 是工作室行为的唯一事实来源：引擎、命名约定，以及一个 `modes` 块，控制每个技能执行多少流程。`/start` 会帮你写好它，一般不用手改。

最关键的问题是 **`modes.rigor`**，三个档：`minimal`、`standard`、`full`。它是一扇前门，背后是六个独立旋钮（`workflow`：要求哪些 GDD 章节；`docs.density`；`qa.level`；`story_granularity`；`review_mode`：多少位总监 agent 评审你的工作；`team.size`），所以 `/start` 只问一次，不问六次：

- **`minimal`**（默认）：游戏 jam 速度。不要求 GDD，文档简洁，QA 证据最少，单人评审。流程：`/start` → `/setup-engine` → `/brainstorm`（一页简报）→ `/create-stories` → `/dev-story` ↔ `/story-done`。
- **`standard`**：要求 5 个 GDD 章节，文档深度适中，标准 QA 证据，精简评审。
- **`full`**：全部 8 个 GDD 章节，文档详尽，每个故事类型都有完整 QA 证据，总监全面评审。

`minimal` 是默认，因为更重的档位要花更多成本才能写出能跑的代码，却没产出更好的结果，新人接手项目时也得不到回报。项目长大后用一次 `/settings` 就能调高——`/help` 和 `/gate-check` 看到苗头时会建议你调。

两个逃生口让单个设置不至于一刀切：**`system_overrides`** 可以让单个系统享受比项目其他部分更高的标准——战斗系统走 full 流程，其他部分保持轻量；**`testing.strict`** 按测试类型（逻辑、集成、可视化、UI、配置）分别设定，缺证据是拦截故事还是只警告。

六个底层旋钮也可以单独设，混搭也行（比如 `workflow: full` 配 `docs.density: terse`：全面但紧凑）。

其中两个——`review_mode`（`full` / `lean` / `solo`）和 `team.size`——还是**个人级**的：rigor 设定团队默认值，但你可以在 git 忽略的 `project.local.yaml` 里按人覆盖，不动共享配置。`modes.automation`（AI 动手前多久停下来问你一次）不在 rigor 里，同样可以按人覆盖。

查看或改任何设置都用 `/settings` 技能：

```
/settings                              # 查看当前生效的配置
/settings modes.review_mode            # 查看单个设置
/settings modes.rigor=full             # 写进 project.yaml（全团队生效）
/settings --local modes.review_mode=solo   # 写进 project.local.yaml（只对你生效）
```

## 注意事项

- 这是一个模板仓库，不是游戏本体：克隆下来是用来开你自己的游戏项目的，里面没有现成的游戏。
- 作者的实测结论值得先看一眼：`standard` 档位多花的 58 分钟、30 份文档，换来的是可追溯性而不是更好的游戏；默认 `minimal` 不是偷懒，是作者有意为之。
- 模型用量注意：三位总监默认要 Opus，`lead-programmer` 和 15 位专员默认要 Sonnet，剩下 30 位继承你会话的模型——跑之前先看一眼自己的 Claude Code 套餐/用量。
- 没有 Python 3 的话，`project.yaml` 里的设置会静默回落到默认值，而且带数据 JSON 的提交会被拦截；先装 Python 3 再开始。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/Donchitos/Claude-Code-Game-Studios
- 原 README：https://github.com/Donchitos/Claude-Code-Game-Studios#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
