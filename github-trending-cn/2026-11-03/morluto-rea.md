# rea：用 agent 逆向工程任何东西

- 原项目：morluto/rea
- 原项目链接：https://github.com/morluto/rea
- 榜单：月榜 2026-11-03 第 1 名
- 翻译日期：2026-11-03
- 原项目许可：MIT
- 原项目数据（2026-11-03 核对）：Star 422,753，Fork 105,405，创建于 2026-04-14

## 一句话介绍

一个给逆向工程用的 MCP：让你的 agent 不看源码也能查清一个应用的功能是怎么实现的，从应用行为一直挖到原生二进制，结论还附证据。

## 适合谁

- 看到别人产品里某个功能做得好、想搞懂它怎么实现的人
- 做安全研究、漏洞分析、恶意软件分析的人
- 想把学到的实现搬进自己项目里的开发者
- 想用真实应用的行为数据搭强化学习（RL）环境、做自动化测试的人

## 它解决什么问题

- 想学一个功能的实现，没源码就无从下手；有源码也未必看得懂关键逻辑藏在哪。
- 逆向工具各自为政：Hopper、Ghidra、IDA、JADX 各管一摊，agent 想调用没有统一接口。
- agent 直接给结论不可信：没有证据、不知道结论的边界在哪，错了也没法追查。

REA 的做法是：一个 MCP 服务器把各类逆向工具接进来，agent 调它查目标、追踪相关代码，返回的每条发现都带证据和局限性说明，分析全程在本地跑。

## README 翻译（核心部分）

原文标题是 REA: Reverse Engineer Anything，副标题是 One MCP for reverse engineering across binaries, applications, and runtime behavior.，意思是一个 MCP，覆盖二进制、应用和运行时行为的逆向工程。

原文核心说法翻译如下：

> 看到一个应用里喜欢的功能，想把它做到自己的产品里？让你的 agent 用 REA 调查它。它可以在没有源码的情况下检查这个应用，解释功能怎么工作、给出证据，再为你的项目做出一个版本。

REA 把你的 agent 接到一套工具上，可以检查原生二进制、JavaScript 和 Electron 应用、.NET 程序集和网站。同样的工具也可以在终端里用。分析在本地运行，结果包含每个结论背后的证据和局限性。

安装会把 REA 注册到你的 agent，并装上匹配的工作流指令。原生分析可以用已有的 Hopper、Ghidra、IDA 或 Kuna 安装；安装时也可以在批准后帮你装 Hopper。静态 JavaScript 分析不需要原生分析引擎。

快速上手（原文 Quick start 翻译）：

在 Linux 上，Ghidra、JADX、固件工具启动和静态 JavaScript / Electron 分析要求 REA 的 `PATH` 里有一个 procps 兼容的 `ps`，用来做进程归属检查。恢复步骤在 `docs/installation.md` 的“Linux owned-process prerequisite”一节。

### 给 agent 装上

装好 Node.js 和 npm 之后跑：

```bash
npx rea-agents setup
```

选你的 agent、审一遍它提议的改动、批准。安装会加上 REA 的 MCP 服务器和匹配的工作流指令，并给现有配置做备份。装完重启 agent。安装会把选好的运行时和 REA 入口脚本直接记下来。如果是通过包管理器拿到的，要保留它的缓存条目。从项目外的可信目录里跑包获取命令。安装和恢复的细节在下面的安装指南里。

安装支持 Claude Code、Codex、Cursor、Gemini CLI、Grok Build 和其他 agent。MCP 默认用精简输入 schema 以省上下文；需要完整字段说明和嵌套校验细节时，在 MCP 注册里设 `REA_MCP_INPUT_SCHEMA_PROFILE=full`。两种模式都保留完整的工具集和服务端校验。

### 问你的 agent

```bash
Understand how search works in the Notes app, show me the evidence, and build a
similar feature for my project.
```

把 Notes 换成你的目标应用、把功能换成你想了解的就行。

### 在终端里用

检查一个解压出来的 JavaScript / Electron 应用目录或 ASAR：

```bash
npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json
```

结果包括模块、导入、Electron 边界和证据。Windows 上把路径换成你的目标，比如 `"D:/apps/example"`。

想经常用 `rea` 命令，先装全局包：

```bash
npm install --global rea-agents
rea --help
```

原生分析要先配一个提供方，见 CLI 与证据指南里的原生命令、提供方选择、快照和脚本化。

### 更新 REA

REA 变化很快，新版本经常带 bug 修复，保持更新。

用 `npm install --global` 或 `bun add --global` 装的 CLI：

```bash
rea update
```

`rea --update` 是同一个已验证流程的别名，接受同样的全局输出参数。更新完再跑一次更新时打印的 setup 命令，刷新 agent 注册和 skill。

用 `npx` 的话，更新 agent 安装用：

```bash
npx rea-agents@latest setup
```

审一遍安装的改动、重启 agent。一次性 CLI 命令用 `npx rea-agents@latest` 加命令，Bun 则是 `bunx rea-agents@latest`。

工作原理（原文 How REA works 翻译）：你的 agent 通过 MCP 调用 REA 来检查目标、追踪相关代码。REA 返回带证据的发现，agent 再用它们追问、解释行为，或者写出并测试一个实现。CLI 命令用同样的工作流。

能分析什么（原文 What you can analyze 翻译）：REA 要求 Node.js 22.x（>=22.23.4）、24.x（>=24.22.1）或 26.12.1 以上，外加 npm。不同目标的额外工具和宿主要求如下：

| 目标 | REA 返回什么 | 要求和指南 |
| --- | --- | --- |
| 桌面安装 | 运行时候选、 supporting 文件、组件标记和下一步探测 | 内置的有界目录 / 文件头检查 |
| 原生二进制 | 伪代码、汇编、字符串、符号、调用和引用 | Hopper、Ghidra、IDA 或 Kuna |
| 离线 ELF 布局 | 节、段、原始符号 / 重定位和静态缓解措施候选 | Linux x64 上调用方提供的 pwntools |
| Go 二进制 | 内嵌的编译器版本、模块、替换和构建设置 | 内置静态 ELF / PE / thin Mach-O 检查，不需要装 Go |
| GPU 代码对象 | CUDA / HIP 目标、选中的内核参数和资源、保留的 PTX 文本 | 内置静态 ELF / PE / fatbin / CUBIN / PTX 检查 |
| 模型文件 | GGUF / safetensors 元数据、张量声明和推导出的总量 | 内置文件头检查；可选全文件哈希 |
| IL2CPP 元数据 | Unity 的 global-metadata.dat 程序集映像、类型和方法名及索引范围 | 内置静态解码 24、27、29、31 和 39 版；不需要 Unity |
| Godot PCK | 归档清单和提取、原始文件头 / 目录事实和选中的内容身份 | 内置静态格式 2、3、4；不需要 Godot |
| Rust 二进制 | 内嵌的 cargo-auditable crate 名、版本、来源和依赖边 | 内置静态 ELF / PE / thin Mach-O 检查 |
| PE 证书 | Authenticode WIN_CERTIFICATE 条目和 PKCS#7 签名者 / X.509 身份字段 | 内置静态 PE 检查 |
| PE 导入 | 导入和延迟加载的 DLL 名、序号、IAT RVA 和 pefile 导入哈希 | 内置静态 PE 检查 |
| ELF notes | PT_NOTE / SHT_NOTE 的拥有者、类型、GNU build-id 和 ABI 标签字段 | 内置静态 ELF 检查 |
| Apple IPS 崩溃文件 | .ips 元数据、线程、映像、寄存器和已记录的崩溃分类 | 内置静态 JSON 检查 |
| Linux 内核模块 | .modinfo 键、__versions CRC、this_module 存在性和签 名尾 | 内置静态 ELF 检查 |
| Erlang BEAM | IFF 块、原子、导出、导入、lambda 和 Code 头 | 内置静态 BEAM 检查 |
| WASM 产物 | 校验、节、精确的导入 / 导出 WAT 形式和解码后的 WAT | 调用方提供的 WABT 1.0.42 |
| EVM 字节码 | 分发选择器、字节偏移、推断的参数和可变性 | Linux x64 上的本地原始 / 十六进制载体 |
| SQLite 数据库 | 表、列、索引、视图、触发器和选中的普通表行 | 本地数据库 / WAL 快照；Node.js 24.x >=24.15 或 26+ 的原生 SQLite 限制 |
| 已记录的 Linux 崩溃 | 原始笔记、每个已记录线程的寄存器 / 信号和可选的映射候选 | 调用方提供的 pwntools（Linux x64）；可选 GDB / pwndbg |
| JavaScript / Electron | 模块、导入、source map、路由、IPC 和原生插件关系 | Node.js 和 npm；Linux 上要 procps 兼容的 `ps` |

案例展示（原文 Showcases 翻译）：DX-Ball——重建一个音效声像（sound-pan）计算；Notion——追踪 Electron 的剪贴板桥；TH04——恢复一个 DOS 弹幕环计算；用 REA 搭建 RL 环境。完整案例在 rea.tools 的 Showcases 页。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。原项目官网是 rea.tools，上面有安装指南、图解教程和真实案例。

### 方式一：setup 一条命令装进 agent（推荐）

```bash
npx rea-agents setup
```

装好 Node.js（22.x >=22.23.4、24.x >=24.22.1 或 26.12.1 以上）和 npm 之后跑。安装会让你选 agent、审改动、批准，自动加上 MCP 服务器和工作流指令，并备份现有配置。装完重启 agent。

支持 Claude Code、Codex、Cursor、Gemini CLI、Grok Build 等。装完就可以直接问 agent，比如“搞懂 Notes 应用的搜索是怎么工作的，给出证据，再给我的项目做个类似功能”。

### 方式二：全局安装，终端里用

```bash
npm install --global rea-agents
rea --help
```

检查一个解压出来的 JavaScript / Electron 应用：

```bash
npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json
```

Windows 上路径换成你的目标，比如 `"D:/apps/example"`。原生分析要先配一个提供方（Hopper、Ghidra、IDA 或 Kuna），见 CLI 与证据指南。

### 方式三：更新

```bash
rea update
```

用 `npx` 的话，更新 agent 安装用：

```bash
npx rea-agents@latest setup
```

REA 更新很频繁，新版本经常带 bug 修复，记得及时更新；更新完审一遍改动、重启 agent。

## 配置说明

- MCP 注册：`setup` 命令自动做，注册里直接记下选好的运行时和 REA 入口脚本；通过包管理器拿到的要保留缓存条目。
- 输入 schema 档位：默认精简以省上下文，需要完整字段说明和嵌套校验细节时，在 MCP 注册里设 `REA_MCP_INPUT_SCHEMA_PROFILE=full`。
- 输出 schema 档位：默认广告完整输出 schema；客户端对 `tools/list` 帧大小有限制时，设 `REA_MCP_OUTPUT_SCHEMA_PROFILE=compact` 收紧每个输出 schema，或设 `off` 不广告输出 schema。
- 原生分析提供方：Hopper、Ghidra、IDA 或 Kuna 选一个，`setup` 可以在批准后帮你装 Hopper；静态 JavaScript 分析不需要原生分析引擎。
- Linux 前置：Ghidra、JADX、固件工具和静态 JavaScript / Electron 分析要求 `PATH` 里有 procps 兼容的 `ps`，用来做进程归属检查。

## 注意事项

- 只从官方渠道拿 REA：原仓库 morluto/rea、官网 rea.tools、npm 包 rea-agents。原文明确提醒，名字相似的仓库或复制的 README 不能证明下载是官方的。
- 只分析自己有权分析的目标，遵守相关法律和许可要求。仓库里有单独的 `DISCLAIMER.md`，动手前先读一遍。
- REA 更新频繁，`rea update` 之后记得跑它打印的 setup 命令刷新 agent 注册和 skill。
- Linux 上部分功能需要 procps 兼容的 `ps`，没有会报进程归属检查失败，恢复步骤在 `docs/installation.md`。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/morluto/rea
- 原 README：https://github.com/morluto/rea#readme
- 官网：https://rea.tools

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 MIT。
