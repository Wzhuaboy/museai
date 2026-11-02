# security-audit-skill：把编程助手变成安全审计员

- 原项目：cloudflare/security-audit-skill
- 原项目链接：https://github.com/cloudflare/security-audit-skill
- 榜单：月榜 2026-11-02 第 1 名
- 翻译日期：2026-11-02
- 原项目许可：MIT
- 原项目数据（2026-11-02 核对）：Star 56,722，Fork 3,699，本月新增 Star 32,599，创建于 2026-06-18

## 一句话介绍

Cloudflare 官方出的一个编程助手 skill：让你的 AI 编程助手按正规流程给代码做安全审计，分阶段查漏洞、交叉验证、最后出结构化报告。

## 适合谁

- 自己写代码、想在上线前自己先查一轮安全问题的人
- 负责代码评审、安全评审的人，想让 AI 先按套路扫一遍再人工复核
- 用 Claude Code、Cursor、Codex 这类支持并行子代理的编程助手的人

## 它解决什么问题

AI 直接说“帮我找漏洞”常常是想到哪查到哪，查得不全，还容易把没证实的东西说成漏洞，或者把加固建议当成漏洞报上来。

这个 skill 的做法是把审计拆成 6 个阶段：先摸清架构和覆盖面，再分派互不干扰的猎手去查，每个疑似问题都交给一个全新的验证员去证伪，最后只把有完整证据链的写成确认漏洞，没证实的写清楚到底缺哪一个事实。

原文说，这是 Cloudflare 漏洞发现工具链的起点版本，那套工具链后来长成了多阶段、舰队级的大系统，这个 skill 就是它演变前的单仓库起点。

## README 翻译（核心部分）

原文第一句是：A coding-agent skill that turns your agent into a security auditor，翻译就是：一个把编程助手变成安全审计员的 skill。

它按 6 个阶段跑一次结构化审计（原文 What it does 翻译）：

1. 侦察：把架构、信任边界、输入面、已有证据和确定性覆盖情况画出来，写进 `architecture.md` 和 `coverage-ledger.json`。
2. 按覆盖面 hunting：按台账里的单元分派互不干扰的猎手，记录检查结果，再用覆盖面评审员找缺口。
3. 候选验证：每个不重复的候选问题都交给一个全新的验证员，让它想办法证伪。
4. 结构化输出：把 `confirmed`、`needs_validation`、`rejected` 三种记录写进 `findings.json`，再用 `report-schema.json` 校验。
5. 独立记录验证：用全新的代理验证最终的源码引用。重要的替换还要再过一个独立验证员。
6. 目标无关报告：从已验证的记录和覆盖台账派生出 `REPORT.md`、`FINDINGS-DETAIL.md` 和 `NEEDS-VALIDATION.md`。

每轮审计里，父代理在建好台账后和每次更新台账后都要跑 `validate-coverage-ledger.cjs`，在第 4 阶段和每次第 5 阶段替换后都要跑 `validate-findings.cjs`。

三种结论的意思不一样（原文翻译）：

- `confirmed`：有完整源码追溯和有边界的实际观测结果。
- `needs_validation`：有一个明确的、还没解决的事实，没有定严重等级。
- `rejected`：候选问题已经被证伪。

同一仓库多跑几轮，结果是累加的：skill 会用以前的台账和发现去补缺口、重新验证改动过的源码、把当前源码的证据带下去，不会把过时的、没解决的工作当成已覆盖。

主要文件（原文 Files 表格翻译）：

| 文件 | 用途 |
| --- | --- |
| `SKILL.md` | 安装、核心原则、平台术语、工作流总览和审计反模式 |
| `RECONNAISSANCE.md` | 第 1 阶段侦察提示词和综合说明 |
| `HUNTING.md` | 第 2 阶段编排、 hunting 方法和验证规则 |
| `ATTACK-CLASSES.md` | 核心、通配和显而易见类攻击提示词 |
| `MEMORY-SAFETY-AND-BINARY.md` | 针对原生目标的内存安全、二进制和内核 hunting 类别 |
| `AI-AND-LLM.md` | 针对 LLM 应用的提示注入、代理 / 工具和输出处理 hunting 类别 |
| `WEB-PROTOCOL-AND-AUTH.md` | 针对 HTTP 协议和认证目标的请求 framing、缓存和认证协议 hunting 类别 |
| `CLIENT-SIDE.md` | 针对客户端 / 浏览器的 DOM 注入、消息信任、界面伪装和原型污染 hunting 类别 |
| `SUPPLY-CHAIN-AND-RELEASE.md` | 依赖、CI、发布、签名、更新、插件和扩展 hunting 类别 |
| `CLOUD-AND-DEPLOYMENT.md` | IAM、基础设施即代码、容器、Serverless、入口和运行时配置 hunting 类别 |
| `PROTOCOLS-RPC-AND-MESSAGING.md` | RPC、序列化、队列、代理、Webhook 和流协议 hunting 类别 |
| `RESOURCE-EXHAUSTION-AND-AVAILABILITY.md` | 共享资源、配额、队列、Worker 和运营花费 hunting 类别 |
| `DATA-ISOLATION-AND-LIFECYCLE.md` | 租户隔离、缓存、搜索、导出、备份、迁移、删除和恢复 hunting 类别 |
| `DESKTOP-MOBILE-AND-LOCAL-IPC.md` | 原生应用、深链、WebView、导出组件、助手、守护进程和本地 IPC hunting 类别 |
| `VALIDATION-AND-REPORTING.md` | 第 3 到 6 阶段的候选验证、结构化输出、记录验证和报告 |
| `report-schema.json` | 三种 `findings.json` 结论的 JSON Schema |
| `validate-findings.cjs` | 第 4、5 阶段用的零依赖 `findings.json` 校验器 |
| `validate-findings.test.cjs` | 校验器测试和生产者兼容的 fixture 检查 |
| `validate-coverage-ledger.cjs` | 第 1 到 5 阶段用的零依赖 `coverage-ledger.json` 校验器 |
| `validate-coverage-ledger.test.cjs` | 台账校验器测试 |

设计原则（原文 Design principles 翻译）：

- 只确认已证实的边界失效：有源码依据但被卡住的线索，留在 `needs_validation`，写清到底缺哪一个事实。
- 对抗性验证：检查发现的代理，永远不是发现它的那个代理。
- 严重等级要有影响：可能性乘影响，不是照着检查表打勾。
- 纵深防御的缺口不是漏洞：如果 A 层已经挡住了攻击，缺 B 层只是加固建议。
- 多跑几轮能提高覆盖面：原文说在他们的测试里，单轮找到的漏洞大约只有多轮总共找到的一半。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。这是一个 skill，不是能直接跑起来的应用，安装就是把它装进你的编程助手里。

### 方式一：用 Skills CLI 安装（推荐）

```bash
npx skills add https://github.com/cloudflare/security-audit-skill \
  --skill security-audit
```

装给当前用户、所有项目都可用，加 `--global`：

```bash
npx skills add https://github.com/cloudflare/security-audit-skill \
  --skill security-audit \
  --global
```

想看代理选择和非交互选项，运行 `npx skills --help`。

### 方式二：使用

在要审计的代码库里打开你的编程助手，或者让助手指向那个代码库，然后直接说：

```bash
security audit this codebase
```

```bash
find security vulnerabilities in ./src
```

```bash
do a security review, output to ~/audits/my-project
```

skill 会在请求匹配到触发词（安全审计、找漏洞、渗透测试代码等）时自动激活。直接要求审计代码库或做渗透测试时用完整审计模式；问安全问题或做聚焦的漏洞工作时用指导模式，除非你明确要求出报告产物。

完整审计模式下，如果你没指定输出目录，默认输出到 `~/security-audit-skill/<仓库名>/run-<序号>`。只有当你明确选了一个版本控制会忽略的目录时，工作流才会在目标仓库里面写东西。

## 配置说明

- 没有要填的密钥和账号，装完就能在编程助手里用。
- 前置要求（原文 Requirements 翻译）：
  - 一个支持工具调用和并行子代理的编程助手和模型。
  - Node.js：跑那两个零依赖校验器要用。
  - 一个操作系统强制的沙箱：给目标控制的构建、测试、进程、浏览器、模拟器、模糊测试和 fixture 用。沙箱要禁掉外部网络、用净化过的白名单环境、强制资源限制、只允许写到指定的临时路径。没有这些控制时，工作流不会执行目标代码，而是把相关线索留在 `needs_validation`。
- 输出目录可以自己指定，例如上面 `~/audits/my-project` 那个例子。

## 注意事项

- 这不是扫描器一键出报告：它要跑 6 个阶段，中间会派多个子代理并行工作，跑一轮需要时间，多跑几轮覆盖面更好，原文说单轮大约只找到多轮总和的一半。
- 结论要分开看：`confirmed` 才能当漏洞去修，`needs_validation` 是缺一个事实还没证实，不要直接当漏洞报，`rejected` 是已经证伪的。
- 沙箱很重要：没有沙箱就不要让它执行目标代码，工作流本身也会把相关线索留在 `needs_validation` 而不是去执行。
- 联系方式：对 AI 安全工具方面的问题、反馈或交流，原文留的邮箱是 security-ai-research@cloudflare.com。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/cloudflare/security-audit-skill
- 原 README：https://github.com/cloudflare/security-audit-skill#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 MIT。
