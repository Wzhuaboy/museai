# GitHub 热门中文翻译

不盈利的公益翻译项目，为英文不好的人把 GitHub 热门项目讲清楚、能上手用。

## 每天做 3 篇

每天翻译 3 个项目，各取 1 个：

- 当天最热门：第 1 名
- 本周最热门：第 1 名
- 当月最热门：第 1 名

榜单来源为 GitHub Trending 的 daily / weekly / monthly，不分编程语言。

## 去重规则

以 `已翻译清单.md` 为准，同一个项目只翻译一次。

- 如果某榜单第 1 名已经翻译过，顺推到该榜单第 2 名、第 3 名，取还没翻译过的最高名次。
- 例如今天做了当月第 1 名，明天就做当月还没做过的最高名次，一般就是第 2 名。
- 周榜和月榜排名每天会变，按当天榜单里还没做过的最高名次来取，不按固定数字硬套。

## 目录结构

```text
github-trending-cn/
  README.md            本文件，项目说明和索引
  TEMPLATE.md          每篇文章的固定模板，写新文章先复制它
  已翻译清单.md        已翻译项目总表，去重依据
  2026-11-02/          按日期分文件夹，一天一个
    作者-仓库名.md     一篇一个项目
```

## 每篇文章包括什么

- 原项目链接和榜单来源（日榜 / 周榜 / 月榜、日期、排名）
- 一句话介绍：它是干嘛的，适合谁
- README 核心部分翻译
- 中文部署操作指南：本地运行、Docker、一键部署（有哪种写哪种）
- 配置说明和注意事项

## 声明

- 翻译仅供学习交流，不盈利。
- 原项目版权和许可归原作者所有，每篇文章都会附原项目链接和许可信息。
- 部署指南按原项目 README 和仓库结构整理，未逐一实机跑通的会在文中注明，请以原项目最新文档为准。

## 索引

### 2026-11-08

- 日榜第 1 名：[agent-browser：给 AI agent 用的浏览器自动化命令行工具](2026-11-08/vercel-labs-agent-browser.md)（vercel-labs/agent-browser）
- 周榜第 7 名：[OpenMausBot：开源的 Grok Bot 替代品，每台机器人都有一台电脑](2026-11-08/milind-soni-OpenMausBot.md)（milind-soni/OpenMausBot）

### 2026-11-07

- 日榜第 1 名：[Zed：Atom 原班人马做的高速多人代码编辑器](2026-11-07/zed-industries-zed.md)（zed-industries/zed）
- 周榜第 2 名：[Claude Code Game Studios：把 Claude Code 变成一间完整游戏工作室](2026-11-07/Donchitos-Claude-Code-Game-Studios.md)（Donchitos/Claude-Code-Game-Studios）
- 月榜第 2 名：[ArtCraft：给艺术家的 AI 创作 IDE](2026-11-07/storytold-artcraft.md)（storytold/artcraft）

### 2026-11-06

- 日榜第 2 名：[skills：给真正干工程的人准备的 agent 技能合集](2026-11-06/mattpocock-skills.md)（mattpocock/skills）
- 周榜第 4 名：[skills：Anthropic 官方的 Agent Skills 仓库](2026-11-06/anthropics-skills.md)（anthropics/skills）
- 月榜第 6 名：[VoiceStudio：开源、完全本地的 ElevenLabs 替代品](2026-11-06/debpalash-VoiceStudio.md)（debpalash/VoiceStudio）

### 2026-11-05

- 日榜第 1 名：[Auto Ontology：给数据加一层语义图谱，让 agent 查数不再瞎编](2026-11-05/NVIDIA-auto-ontology.md)（NVIDIA/auto-ontology）
- 周榜第 5 名：[Superpowers：给编程 agent 配一套真正的软件开发方法论](2026-11-05/obra-superpowers.md)（obra/superpowers）
- 月榜第 2 名：[AnyPS5：把 PS5 游戏可执行文件自动移植到 Linux 和 Windows](2026-11-05/boykopovar-AnyPS5.md)（boykopovar/AnyPS5）

### 2026-11-04

- 日榜第 3 名：[worktrunk：给并行跑的 AI agent 一人一个工作区](2026-11-04/max-sixty-worktrunk.md)（max-sixty/worktrunk）
- 周榜第 3 名：[t3code：Agent 的统一遥控器](2026-11-04/pingdotgg-t3code.md)（pingdotgg/t3code）
- 月榜第 4 名：[hyperframes：写 HTML 就能渲染视频](2026-11-04/heygen-com-hyperframes.md)（heygen-com/hyperframes）

### 2026-11-03

- 日榜第 1 名：[agent-desktop：让 AI agent 直接操作你的桌面应用](2026-11-03/vercel-labs-agent-desktop.md)（vercel-labs/agent-desktop）
- 周榜第 3 名：[impeccable：给编程助手的设计词汇表](2026-11-03/pbakaus-impeccable.md)（pbakaus/impeccable）
- 月榜第 1 名：[rea：用 agent 逆向工程任何东西](2026-11-03/morluto-rea.md)（morluto/rea）

### 2026-11-02

- 日榜第 1 名：[claude-mem：给 AI 编程助手加长期记忆](2026-11-02/thedotmack-claude-mem.md)（thedotmack/claude-mem）
- 周榜第 1 名：[hallmark：让 AI 做的网页不再一眼像 AI 生成的](2026-11-02/Nutlope-hallmark.md)（Nutlope/hallmark）
- 月榜第 1 名：[security-audit-skill：把编程助手变成安全审计员](2026-11-02/cloudflare-security-audit-skill.md)（cloudflare/security-audit-skill）
