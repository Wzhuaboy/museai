# skills：Anthropic 官方的 Agent Skills 仓库

- 原项目：anthropics/skills
- 原项目链接：https://github.com/anthropics/skills
- 榜单：周榜 2026-11-06 第 4 名
- 翻译日期：2026-11-06
- 原项目许可：多数技能 Apache-2.0；docx、pdf、pptx、xlsx 四组文档技能仅源码可见（非开源）
- 原项目数据（2026-11-06 核对）：Star 187,932，Fork 22,163，创建于 2025-09-22

## 一句话介绍

Anthropic 官方公开的 Agent Skills 仓库：技能就是 Claude 按需加载的文件夹（指令 + 脚本 + 资源），让 Claude 在特定任务上按可重复的方式干活。

## 适合谁

- 用 Claude Code、Claude.ai、Claude API 的人
- 想看官方怎么做技能、或想给自己写技能找范本的人
- 要做文档处理（docx、pdf、pptx、xlsx）的人
- 对 Agent Skills 这个标准本身感兴趣的人

## 它解决什么问题

- Agent 默认是通用模型，特定任务没有现成做法：按公司品牌规范做文档、按组织流程分析数据、自动化个人任务，每次都得从头教。
- 技能把做法写成可复用的指令包，Claude 动态加载，遇到专门任务就按包里写的方式做。
- 这个仓库就是官方的示范：从创意应用（艺术、音乐、设计）到技术任务（测试 Web 应用、生成 MCP 服务器）再到企业工作流（沟通、品牌等），都各有一套技能。

## README 翻译（核心部分）

### 什么是技能

技能是**文件夹**：里面是指令、脚本和资源，Claude 按需动态加载，在专门任务上提效。技能教 Claude 如何用可重复的方式完成特定任务，不管是按公司品牌规范做文档、按组织特定流程分析数据，还是自动化个人任务。

想了解更多，原文给了几个入口：什么是技能、如何在 Claude 里用技能、如何创建自定义技能，以及 Anthropic 官方博客《用 Agent Skills 给 agent 装备真实世界的能力》。

### 仓库里有什么

- **`./skills`**：技能示例，分四类：创意与设计、开发与技术、企业与沟通、文档技能
- **`./spec`**：Agent Skills 规范
- **`./template`**：技能模板

每个技能自成一个文件夹，里面有个 `SKILL.md`，是指令和元数据，Claude 靠它工作。可以翻一翻这些技能，找自己写技能的灵感，或理解不同的模式。

### 许可要看清：多数开源，文档技能不是

仓库里很多技能是开源的（Apache 2.0）。但也放了 Claude 文档能力背后那套文档创建和编辑技能，分别在 `skills/docx`、`skills/pdf`、`skills/pptx`、`skills/xlsx` 四个子目录下：**这些是源码可见，不是开源**，官方放出来是想让开发者参考更复杂的、正在生产 AI 应用里跑的技能。

### 免责声明（原文原意）

这些技能**仅供演示和教学**。Claude 里实际给你的实现和行为，可能和仓库里展示的不一样。这些技能是用来说明模式和可能性的。关键任务先在自己的环境里充分测试，再依赖它们。

### 在 Claude Code、Claude.ai、API 里用

**Claude Code**

先把这个仓库注册成 Claude Code 的插件市场，在 Claude Code 里跑：

```bash
/plugin marketplace add anthropics/skills
```

然后装一套具体的技能：

1. 选 `Browse and install plugins`
2. 选 `anthropic-agent-skills`
3. 选 `document-skills` 或 `example-skills`
4. 选 `Install now`

也可以直接装其中一个插件：

```bash
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

装完直接提要求就行。比如装了 `document-skills` 插件，可以对 Claude Code 说："Use the PDF skill to extract the form fields from `path/to/some-file.pdf`"。

**Claude.ai**

这些示例技能在 Claude.ai 的付费计划里已经都有了。要用仓库里的技能或上传自定义技能，按官方帮助文档《在 Claude 里用技能》走。

**Claude API**

可以通过 Claude API 用 Anthropic 的预置技能，也能上传自定义技能，见《Skills API 快速上手》。

### 自己写一个基本技能

技能写起来很简单：一个文件夹，里面一个 `SKILL.md`，带 YAML frontmatter 和指令。可以用仓库里的 **template-skill** 当起点：

```yaml
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples

- Example usage 1
- Example usage 2

## Guidelines

- Guideline 1
- Guideline 2
```

frontmatter 只要两个字段：

- `name`：唯一标识（小写，空格用连字符）
- `description`：完整描述这个技能做什么、什么时候用

Markdown 正文就是 Claude 在技能激活时会照着做的指令、例子和指南。更多细节见官方帮助文档《如何创建自定义技能》。

### 合作伙伴技能

技能也是教 Claude 更好地用特定软件的好办法。官方看到优秀的合作伙伴示例技能，会在这里重点推荐，目前列出的有 **Notion**（Notion 给 Claude 的技能）。

## 中文部署指南

**方式一：Claude Code（插件市场）**

```bash
/plugin marketplace add anthropics/skills
```

然后在插件列表里选 `anthropic-agent-skills`，装 `document-skills` 或 `example-skills`；或直接跑：

```bash
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

**方式二：Claude.ai**

付费计划里示例技能已经内置，直接用；要上传自定义技能，按官方文档《在 Claude 里用技能》操作。

**方式三：Claude API**

用 Anthropic 的预置技能和上传自定义技能，见官方《Skills API 快速上手》。

**方式四：自己写技能**

1. 新建一个文件夹，里面放 `SKILL.md`
2. frontmatter 写 `name` 和 `description` 两个字段
3. 正文写指令、例子和指南
4. 可以直接拿仓库里的 `template` 目录当起点，照着改

## 配置说明

- frontmatter 只需要 `name` 和 `description` 两个字段，其他都是正文里的指令。
- 技能是按文件夹组织的，一个技能一个文件夹，`SKILL.md` 是入口。
- Claude Code 里装完插件后，用技能就是直接提要求，不用记命令。

## 注意事项

- 官方免责声明要当真：这是演示和教学用的仓库，Claude 里实际给你的实现和行为可能和仓库里不一样，关键任务先在自己环境里充分测试。
- 四组文档技能（docx、pdf、pptx、xlsx）仅源码可见、非开源，只能参考，不能当开源代码拿去用。
- Agent Skills 的标准本身在 agentskills.io，仓库里的 `./spec` 是规范，想深入可以对照着看。
- 是否实测：按原项目 README 文档整理，未实测。
