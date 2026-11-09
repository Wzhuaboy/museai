# DeepTutor：终身个性化 AI 家教，辅导、研究、创作、练习收进一个系统

- 原项目：HKUDS/DeepTutor
- 原项目链接：https://github.com/HKUDS/DeepTutor
- 榜单：月榜 2026-11-09 第 11 名（顺推；月榜前 10 名已翻过）
- 翻译日期：2026-11-09
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-09 核对）：Star 57,022，Fork 6,952，创建于 2025-12-28，提交 3,806 次，Release 90 个

## 一句话介绍

DeepTutor 是一个终身个性化 AI 家教：一个 agent 原生的学习工作台，把辅导、研究、创作和练习连在一个可扩展系统里——聊天、测验、研究、可视化、解题、精通路径、阅读、知识库、记忆，全部共享同一份学习上下文。

## 适合谁

- 想系统学东西的人：学生、自学者、备考、学新技能，都能拿它当长期家教
- 手里有一堆资料（PDF、书、论文、笔记、视频）想学透的人
- 用 Claude Code、Codex、Grok 这类 agent，想让它们参与学习的人
- 想自托管学习系统、数据留在自己机器上的人

## 它解决什么问题

- 学习工具是散的：聊天问问题一个应用、刷题一个应用、看书写笔记一个应用、资料检索又一个应用，进度和记忆互不相通。DeepTutor 把这些收进一个工作台，聊天、书、阅读、练习、任务板、日历、学习笔记共享同一份材料、进度和学习上下文。
- 普通 AI 聊天学东西不接地气：答案没出处、学了就忘、不知道自己掌握到哪。DeepTutor 用带引用的知识库（RAG）接地气，用三层记忆（L1 事件轨迹、L2 事实、L3 综合）记住你学到哪，用精通路径（Mastery Path）按知识点一步步带你过关，掌握了才放行。
- 资料太多不知道从哪学起：它能把选定的资料编成一本可交互的"活书"（living book），带章节、测验、闪卡、时间线、代码、图表、互动组件和页内聊天，边读边练；还能把文档、视频、音频变成带引用的沉浸式阅读。

## README 翻译（核心部分）

### 这是什么

DeepTutor：终身个性化辅导。https://deeptutor.info/

> 我们正在积极招募维护者！看贡献指南了解角色、要求和申请方式。

#### 版本发布

> **[2026.11.6] v1.7.2** — 完整的桌面下载、选中文本朗读、更简单的模型设置、韩语界面预览、NVIDIA NIM 向量嵌入、更可靠的精通度、检索和更新。

> **[2026.11.1] v1.7.1** — 桌面预览、更广的本地化、密码修改、已检查的视频课程、Anki 和日历导出、更多供应商、广泛的可靠性改进。

> **[2026.10.28] v1.7.0** — 模块化安装、焕然一新的学习工作台、带 Dito 的块笔记本、带旁白的视频课程、可恢复的向量嵌入检查点、更可靠的辅导。

> v1.7.2 已发布。`pip install -U "deeptutor[full]"` 装完整 Web 应用和 CLI；只装 `deeptutor` 装核心。老版 CLI 安装的升级步骤见下文。

#### 新闻

- **2026-10-28** DeepTutor v1.7.0 来了！全新的外观、更顺滑的导航、更好配合的学习工具。
- **2026-05-22** 官方文档站上线：deeptutor.info——指南、参考和功能导览都在一处。
- **2026-04-10** 我们的论文上了 arXiv——读预印本了解 DeepTutor 背后的设计和想法。
- **2025-12-29** DeepTutor 正式发布！

### 关键特性

DeepTutor 是一个 agent 原生的学习工作台，把辅导、研究、创作和练习连在一个可扩展系统里。

- **一个运行时，多种学习模式**——聊天、测验、研究、可视化、解题、精通路径、阅读等共享会话上下文，同时保留各自专用的工作流。
- **一个连通的学习工作台**——主页、学习、资源把聊天、书、阅读、练习、任务板、日历和学习笔记连起来，共享材料、进度和学习上下文。
- **有依据的知识与阅读**——用 LlamaIndex、PageIndex、GraphRAG 或 LightRAG 建带版本管理的资料库，接外部知识源，挨着文档、视频和音频学，引用都链到原文。
- **伙伴与子 agent**——实时咨询 Claude Code、Codex、Grok CLI 这类 agent，导入过去的对话，或运行有自己记忆、资源和 IM 频道的持久伙伴（Partner）。
- **可检查的记忆**——L1 轨迹、L2 事实、L3 综合让个性化看得见、可编辑，证据链接可以在记忆图谱（Memory Graph）里审计。
- **生来可扩展**——通过一个 agent 原生运行时加人设、内置或社区技能、MCP 服务、CLI 应用和生成模型。

### 上手

按你想用的方式选安装路径。终端安装共用一个运行时目录：私有设置存在启动目录下的 `data/user/settings/`，或 `DEEPTUTOR_HOME` / `deeptutor start --home` 指定的位置。启动应用后，在 **Settings → Providers** 和 **Language models** 里配置供应商和模型。

**桌面版——macOS 和 Windows（预览版）**

**Open DeepTutor** 把 Python、Node.js 和完整学习工作台打在一起，不用终端、不用另外装运行时。从最新 GitHub Release 下载发布的桌面构建，按你的电脑选安装器。

| 你的电脑 | 下载目标 | 安装器 |
| --- | --- | --- |
| **Mac（Apple Silicon）** | `macos-arm64` | 打开 DMG，把 **Open DeepTutor** 拖进 **Applications**。 |
| **Mac（Intel）** | `macos-x64` | 打开 DMG，把 **Open DeepTutor** 拖进 **Applications**。 |
| **Windows x64** | `windows-x64` | 运行 Setup `.exe`，或解压便携 ZIP、启动 `Open DeepTutor.exe`。 |

Windows 预览构建未签名，可能会弹 SmartScreen 警告。签名、本地数据和源码构建见桌面指南。

**Docker——最快的完整应用试用**

不用装 Python 或 Node.js，直接跑完整 Web 应用：

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

打开 http://127.0.0.1:3782。命名卷保存设置和本地数据；Web 应用只需要 `3782` 一个端口。主机工作区、本地模型服务、反向代理和生产部署见 Docker 指南。

**PyPI——完整 Web 应用和 CLI**

用 **Python 3.11–3.14** 和 **Node.js 20.9+**。在模块化的 1.7.0 版本里，`deeptutor[full]` 装 Web 应用和 CLI；只装 `deeptutor` 装核心聊天和 SDK。

```bash
mkdir -p my-deeptutor && cd my-deeptutor
python -m pip install -U "deeptutor[full]"
deeptutor init     # 端口 + LLM 供应商 + 可选的向量嵌入/搜索
deeptutor start    # 启动后端 + 前端
```

打开终端里打印的 URL，默认 http://127.0.0.1:3782。按 `Ctrl+C` 停掉两个服务。

**从 1.6.15 或更早升级：**停掉 DeepTutor，备份运行时目录，装新版之前先卸载老版 `deeptutor-cli` 包。保持同一个 `DEEPTUTOR_HOME`，然后跑 `python -m pip check` 和 `deeptutor module list`。准确的升级命令见 PyPI 和迁移指南。

**源码——当前开发版和贡献者**

用 **Python 3.11–3.14** 和 **Node.js 22 LTS** 以匹配 CI 和 Docker。

```bash
git clone --branch dev https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/full.txt
python -m pip install -e . --no-deps
( cd web && npm ci --legacy-peer-deps )
deeptutor init
deeptutor start --dev
```

不用 `--dev` 的 `deeptutor start` 是生产构建。可选依赖从仓库根目录装，比如 `python scripts/install_extras.py dev,partners,math-animator`。Conda、额外功能和排障见源码安装指南，或看 Agent Setup 指南让有终端能力的 agent 帮你完成并验证安装。

**CLI——终端和 agent 用**

最精简的终端安装用核心 wheel，不需要 Node.js 或 Web 前端：

```bash
mkdir -p my-deeptutor && cd my-deeptutor
python -m pip install -U deeptutor
deeptutor init --cli
deeptutor chat
```

核心包含聊天、问问题、CLI 和 SDK；其他能力和管​​理命令需要各自对应的功能模块。当前 `dev` 源码安装和可选依赖见 CLI 专属指南，下面的 CLI 参考覆盖单次运行和机器可读输出。

**工作区和高级设置：**见内容工作区、本地数据持久化、容器化与沙箱部署、配置参考和排障。

### 探索 DeepTutor

每个科目或项目开一个**工作区**。主页、学习、资源随当前工作区变化；伙伴和个性化跨工作区可用。

| 区域 | 范围 | 包含什么 |
| --- | --- | --- |
| **主页** | 工作区 | 聊天、任务板、日历、学习笔记 |
| **学习** | 工作区 | 书、精通路径、沉浸式阅读、练习 |
| **资源** | 工作区 | 聊天记录、收藏、学习日志、题库、知识中心 |
| **伙伴** | 账号 | 持久伙伴、伙伴群组、资源访问、IM 频道 |
| **个性化** | 账号 | 我的 agent、人设、技能、MCP 服务、CLI 应用、记忆、设置 |

#### 主页——对话、任务、笔记和日历

主页是每天工作的起点：在当前工作区里和家教聊天、整理下一步行动、写自己的笔记。日历提供账号范围的视图，同时保留学习事件的来源工作区。

#### 聊天——你真正用的 agent 循环

聊天是默认能力，也是大多数工作的起点。一个线程可以正常聊天、调用工具、在选定的知识库里找依据、读附件、生成图片、咨询子 agent、写笔记记录，并在多轮里保持同一份上下文。

家教按需调用工具，必要时停下来问澄清问题。右上角的 **Customize page** 选择可见的模式和技能、MCP、伙伴、偏好设置和语音输入控制。在 **Starting prompts** 下可以添加、编辑或删除 Explain、Solve、Practice、Plan、Research 里的标题和提示词。

用户可开关的工具有 `brainstorm`、`web_search`、`paper_search`、`zotero_search`、`reason`、`geogebra_analysis`——配好对应的生成模型后还有 `imagegen` 和 `videogen`。上下文工具有 `rag`、`kb_files`、`knowledge_frontier`、`read_source`、`read_memory`、`write_memory`、`read_skill`、`load_tools`、`exec`、`web_fetch`、`ask_user`、`list_favorites`、`save_favorite`、`write_note`、`search_notes`、`question_bank`、`github`、`consult_subagent`、`workspace_list`、`workspace_read`、`workspace_search`、`workspace_present`、`workspace_export`，在轮次有合适的上下文时自动挂载。

上下文分两种：**粘性会话上下文**（能力、工作区或课程、工具、知识库、人设、模型、阅读/精通状态）在多轮里持续；**引用**（文件、聊天记录、书、阅读章节、笔记、选定的题库条目、导入的 agent）默认只对本轮生效，从 `+` 菜单加入，置顶后每轮都带上。语音按钮只转录当前消息。

完整配置下，主页把**聊天**、**问问题**、**测验**、**可视化**、**视频课程**放在一键可达的位置；**研究**（带引用的报告）和**解题**（带步骤的推理）放在 *More Capabilities* 下面。在答案里选中文本可以打开 **Little Tutor**，一个嵌在原对话下面的聚焦侧边栏线程。发了至少三条消息后，左边的竖栏会在空间允许时给每个问题打一个勾；悬停预览，点击跳回去，或用 **Alt/Option + ↑/↓** 在问题之间移动。

#### 任务板与日历——安排日常学习

**任务板**用待办、进行中、已完成跟踪学习任务，带笔记、拖拽或键盘移动控制、可恢复的归档。任务留在当前工作区，不需要配置模型。

**日历**把个人学习安排、重复事件和提醒放一起，支持 `.ics` 导出到 Apple 日历、Google 日历、Outlook 和 Thunderbird。任务截止日期和复习这类工作区覆盖层仍连着来源工作区。

#### 学习笔记——页面、来源和 Dito

学习笔记（以前叫 Co-Writer）把你自己的写作按页面、子页面和块组织在当前工作区里。导入 Word 文档、排一个页面树、把收藏里的原始记录当证据插进来。页面保持保存状态可见，导出为 Markdown 或 Word；互动内容在 Word 里变成静态。

**把闪卡导出到 Anki。**笔记页面可以包含闪卡。在有闪卡的页面上，打开页面菜单选 **Export flashcards (Anki)**；在笔记复习队列里选 **Export all for Anki**。在 Anki 里用 **File → Import** 选下载的 `.txt` 文件，卡片进一个叫 `DeepTutor::<笔记标题>` 的牌组，带正反面字段、标签和数学公式，重复导入同一个文件会更新已有卡片而不是复制一份。DeepTutor 自己的复习计划不包含在内。

用 **Dito** 讨论一段话或一个块：要解释、举例、改写或出练习题，对话附在对应的页面和行上。接受修改前先检查提议，或在行下插入答案继续工作。收藏保存原始记录；笔记是你建立自己理解的地方。

#### 学习——书、路径、阅读和练习

学习是当前工作区的学习区。从 **Learning → New learning** 创建一个活动，再从 **All learning** 打开它，进度、对话和来源上下文都在。

| 活动 | 用来做什么 | 保留什么 |
| --- | --- | --- |
| **书** | 从选定来源搭建结构化、可交互的书 | 可编辑的章节、类型化块、阅读进度、页内聊天 |
| **精通路径** | 把学习目标拆成主题和引导学习 | 知识点地图、主题对话、精通证据 |
| **沉浸式阅读** | 挨着文档、网页、视频或音频工作 | 带来源的对话、已验证的引用、高亮、笔记、进度 |
| **练习** | 复习收集或导入的题目 | 答案、错题、回忆评分、下次复习日期 |

#### 书——用你的材料做的活书

书把选定的来源变成一本可交互的**活书**——不是静态 PDF，而是由类型化块搭建的阅读环境。一本书可以从知识库、收藏、题库或聊天记录开始；创建流程在生成内容前先提议章节大纲，你先检查形状，而不是盲目接受一次性的输出。

每个章节编译成可编辑的类型化块——文本、提示框、测验、闪卡、时间线、代码、图表、交互式 HTML、动画、概念图、深度挖掘和用户笔记——每个块自带页内聊天。可以插入、移动、重新生成、改写或切换块类型；选定的段落进入可检查的学习捕获收件箱。即使管理员共享的书是只读或协作编辑，进度、书签、测验尝试、捕获和页内聊天仍按读者私有；共享删除仍只有管理员能做。任何书都能导出 Markdown，长的编译可以暂停和恢复，`deeptutor book health` 标记来源漂移，`deeptutor book refresh-fingerprints` 刷新来源基线。

#### 资源——材料和保存的学习记录

资源是当前工作区的可复用资料库。把原始材料、保存的结果和学习记录放这里，之后可以附到新的对话和活动里，不会把项目混在一起。

#### 知识中心——多引擎 RAG 资料库

知识库是 RAG 背后的文档集合——给聊天轮次、学习笔记编辑、书生成和伙伴对话提供依据。特别的是**检索引擎可选**：**LlamaIndex**（默认，混合向量 + BM25，可选交叉编码器重排，精确 flat 或 HNSW FAISS 索引）、**PageIndex**（带页面级引用的推理检索，可托管或自托管开源版）、**GraphRAG** 和 **LightRAG**（知识图谱检索）、**LightRAG Server**（检索卸载到你用 HTTP 连接的外部 LightRAG 实例）、**WeKnora**（从你自托管部署里的知识库检索，不用本地索引或文档副本）、**腾讯 IMA**（你在 IMA 里整理的资料库——通过它的 OpenAPI 搜索、浏览和写回）、**MarginNote 4**（你的 MN4 学习数据——文档、摘录、思维导图卡片和它们之间的链接——由应用的 Add-on 推送进来，用专用工具导航）、**Kiwix**（通过 HTTP 提供可搜索的 ZIM 存档，不用本地索引）、或一个链接的 **Obsidian** 仓库，家教直接在原地读写。每个知识库绑定一个引擎。

创建知识库时，可以**新建**（上传并索引文档）、**链接已有**（原地复用一个索引）或**连接 Kiwix**（按需搜索一个已提供的 ZIM 存档）。创建时选它的存储工作区；已有的知识库可以在预览后在工作区间移动，分配和保存的引用保留。知识库也可以跟踪 **GitHub 仓库**（仓库、分支、glob）或**文档站 URL**（有限的爬取深度和页数，默认每 24 小时重新同步）；同步用哈希差异比对新增、修改和删除的内容，跟踪的文档不用重新上传就能保持最新；**链接的文件夹**在同步时拾取新增或修改的本地文件。重新索引会写一个新的 flat `version-N` 目录并保留旧的，所以正在工作的索引不会在重建中途被毁掉。单个文档即使在**错误**状态的知识库里也能删掉——不用整个删掉重建。文档解析——纯文本、MinerU、Docling、Tika、markitdown、PyMuPDF4LLM 或 LiteParse——以及可选的图片描述模型，在 **Settings → Knowledge & documents** 里选，本地模型下载默认关闭。

**给知识库打分。**有多个引擎，"哪个在这里检索得最好？"是个经验问题——所以 `deeptutor kb eval` 来回答它。写一份 QA 集（每行一个 JSON 对象：一个 `query` 加理想检索应返回的 `gold` 段落），再用 `deeptutor kb eval <名称> --dataset qa.jsonl --top-k 5 [--mode hybrid] [--save baseline.json]` 给知识库打分。每个用例都走聊天轮次用的同一条检索路径，它的排名引用按精确文本或词法重叠（阈值用 `--min-ratio` 调；不评估语义等价）与 gold 段落匹配，运行报告 **Recall@k / Precision@k / nDCG@k / MRR / MAP / Hit@k**。指标是排名上的纯函数，没有模型评判输出。用 `deeptutor kb eval-diff baseline.json candidate.json` 对比保存的报告，看每个指标和每个用例的变化。

#### 历史、收藏、日志和题库

**聊天记录**按原始学习上下文重新打开对话。**收藏**把有用的原始对话和结果保存在可移动的集合里，支持 Markdown 导出，随时可以插进学习笔记。**学习日志**记录当前任务、会话交接和确认的学习记录。**题库**组织题目、答案、解释和错题；选一组进 **Learning → Practice** 复习薄弱环节并安排重复。

#### 伙伴——跨工作区的持久伙伴

伙伴属于账号而不是某个科目工作区。每个伙伴保持自己的身份、指令、模型策略、关系和频道，同时用私有资料库或已有工作区的资源。

每个入站 Web 或 IM 消息都变成一次普通的 `ChatOrchestrator` 轮次——伙伴就是"一个有性格和电话号码的聊天"。它的 `SOUL.md`、模型选择、工具策略和资料库在创建后仍可编辑。私有伙伴工作区复制分配的知识库、技能和收藏集合；绑定的工作区改为共享它当前的文件和资源。两种模式下，灵魂、对话和关系记忆都各自独立。

**伙伴群组**把两个或更多伙伴放进一个共享对话，各有不同的席位、可选的讨论和共享记忆模式、持久的历史。已认证用户即使在伙伴被共享时也保留私有的伙伴会话和关系记忆。

模式驱动的频道把伙伴接到飞书、Telegram、Slack、Discord、钉钉、QQ/NapCat、微信、WhatsApp、Zulip、Mattermost、Matrix、Mochat 和 Microsoft Teams，具体看装了哪些额外功能和凭证。浏览器端设置支持选定频道的二维码接入。伙伴也可以通过 **Personalization → My Agents** 接入，从一次普通聊天轮次里咨询。

#### 个性化——可复用的行为与连接

个性化跟账号走，跨工作区。选家教该怎么表现，以及它可以复用哪些 agent、技能、服务、应用和记忆；工作区和对话选择可以进一步收窄访问。

**我的 agent——咨询实时 agent、导入历史**

**接一个实时 agent**——Claude Code、Codex、Grok CLI、Antigravity、Kimi、opencode、MiMo Code、Hermes Agent、OpenClaw、DeepSeek Harness 或一个伙伴——从聊天轮次里咨询它。DeepTutor 运行选定的 agent，通过 `consult_subagent` 把它的工作流进 Activity 面板；Agent 芯片或 `@` 让连接附在会话上。本地框架用自己的认证、工作目录和会话存储。

**导入过去的对话**：从 ChatGPT、Claude Code 和 Codex 导入为可搜索、可恢复的引用。ChatGPT 用官方的 `conversations.json` 导出；Claude 历史按项目或工作目录选，Codex 历史按日期选。通过 `+` → My Agents 引用导入的对话，不会把它变成 DeepTutor 自己的声音。

**人设、技能、MCP 服务和 CLI 应用**

**人设**复用一种声音、教学风格或响应策略，也可以给伙伴的灵魂打底。**技能**把可重复的工作流打包成 `SKILL.md` playbook，分账号共享和工作区本地两个库。**从 EduHub 导入**浏览社区技能，通过安全门安装（见生态系统）。

**MCP 服务**授权外部工具，**CLI 应用**通过执行沙箱把已装程序从 CLI-Anything 目录暴露出来。工作区分配和用户授权决定每轮可以用哪些资源。

#### 记忆——可检查的个性化

记忆是一个基于文件、可读、可整理、可审计的三层系统——刻意**不是**一个隐藏的向量库。**L1** 是工作区镜像加只追加的事件轨迹（`trace/<界面>/<日期>.jsonl`）；**L2** 是按界面整理的事实（`L2/<界面>.md`），带指向 L1 实体的引用；**L3** 是跨界面的综合（`L3/<画像|最近|范围|偏好>.md`），记录它来自哪些 L2 界面。

记忆图谱展示整个金字塔——L3 综合在中心、L2 在中间环、L1 轨迹在外圈——带精确的 L2 → L1 证据边和 L3 → 贡献界面的链接。记忆在 `chat`、`notebook`、`quiz`、`kb`、`book`、伙伴和 `cowriter` 界面之间跟踪；整合器的更新/审计/去重预算在 **Settings → Memory** 里调。

#### 设置——一个控制面

设置是运营控制面，打开时在 **General** 上，管界面和模型输出语言。它的可搜索导航链接到独立页面：**Personal** 管工作区、数据迁移、外观和使用统计；**Learning & conversation** 管起点、附件、视频学习、学习者和监护人控制、学习进度和记忆；**Models & services** 管供应商、语言模型、任务模型、向量嵌入、搜索、语音和多模态生成；**Features & integrations** 管工具、能力参数、伙伴与 agent、知识与文档。**System** 放网络、运行时状态和关于；**Archived chats** 可以搜索、恢复或永久删除已归档的对话。运行时状态包含后端健康、常驻内存和 **Readiness** 矩阵，给能力阻断、警告和建议打分。

**OpenAI Codex OAuth（实验性）。**在 Settings → Providers 里添加 **OpenAI Codex** 会打开浏览器登录，用你自己的 ChatGPT 套餐，不需要 `OPENAI_API_KEY`。令牌只存在 `data/system/user-secrets/<所有者>/private/openai-codex/` 里——多容器 Compose 部署里在执行沙箱够不到的每棵树之外——DeepTutor 从不读取或修改你的 `~/.codex` CLI 登录。模型列表来自该账号的实时目录；登录会发布画像，但只有在还没配置 LLM 时才成为当前模型。因为一个令牌授权一个人的套餐，画像不能通过用户授权共享——每个账号自己登录，包括普通用户：他们的登录卡在供应商下面，生成的模型、目录和登出都只对该账号私有。

## 中文部署操作指南

### 方式一：桌面版（最省事）

去最新 GitHub Release 下载对应系统的安装包，**Open DeepTutor** 自带 Python、Node.js 和完整学习工作台，不用终端、不用另外装运行时：

- Mac（Apple Silicon）：`macos-arm64` 的 DMG，拖进 Applications
- Mac（Intel）：`macos-x64` 的 DMG，拖进 Applications
- Windows（x64）：Setup `.exe`，或解压便携 ZIP、启动 `Open DeepTutor.exe`

注意：Windows 预览构建未签名，会弹 SmartScreen 警告。

### 方式二：Docker（最快试用）

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

打开 http://127.0.0.1:3782，命名卷保存设置和本地数据。

### 方式三：PyPI 完整版

```bash
mkdir -p my-deeptutor && cd my-deeptutor
python -m pip install -U "deeptutor[full]"
deeptutor init     # 端口 + LLM 供应商 + 可选的向量嵌入/搜索
deeptutor start    # 启动后端 + 前端
```

前置要求：Python 3.11–3.14、Node.js 20.9+。只装 `deeptutor` 是核心（聊天和 SDK），不含 Web 应用。

### 方式四：PyPI 仅 CLI（终端和 agent 用）

```bash
mkdir -p my-deeptutor && cd my-deeptutor
python -m pip install -U deeptutor
deeptutor init --cli
deeptutor chat
```

不需要 Node.js 或 Web 前端。

### 方式五：从源码

```bash
git clone --branch dev https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/full.txt
python -m pip install -e . --no-deps
( cd web && npm ci --legacy-peer-deps )
deeptutor init
deeptutor start --dev
```

前置要求：Python 3.11–3.14、Node.js 22 LTS。`deeptutor start` 不带 `--dev` 是生产构建。

### 装完先做

启动后在 **Settings → Providers** 和 **Language models** 里配置供应商和模型；不配模型，聊天跑不起来。

## 配置说明

- 每个科目或项目开一个工作区；主页、学习、资源随工作区变，伙伴和个性化跨工作区可用。
- 知识库选检索引擎：LlamaIndex（默认）、PageIndex（带页面级引用的推理检索）、GraphRAG/LightRAG（知识图谱检索）、LightRAG Server、WeKnora、腾讯 IMA、MarginNote 4、Kiwix、Obsidian 仓库；每个知识库绑定一个引擎。
- 记忆三层可检查：L1 事件轨迹、L2 事实、L3 综合，证据链接能在记忆图谱里审计；整合预算在 Settings → Memory 里调。
- 伙伴（Partner）有自己的 `SOUL.md`、模型策略和 IM 频道（飞书、Telegram、Slack、Discord、钉钉、QQ、微信、WhatsApp 等）；我的 agent 可以实时咨询 Claude Code、Codex、Grok CLI 等，也能导入 ChatGPT/Claude/Codex 的历史对话。
- OpenAI Codex OAuth 是实验功能：用自己的 ChatGPT 套餐登录，不用 API 密钥；令牌只存在私有目录，DeepTutor 不碰你的 `~/.codex` 登录。
- 常用 CLI：`deeptutor init`、`deeptutor start`、`deeptutor chat`、`deeptutor book health`、`deeptutor kb eval`（给知识库打分，报 Recall@k / Precision@k / nDCG@k / MRR / MAP / Hit@k）。

## 注意事项

- README 里有简体中文版链接，但主 README 是英文，本文翻的是英文主 README 的核心部分（关键特性、上手、探索）；完整 README 里还有详细的 CLI 参考、生态系统（EduHub 与技能社区）、社区与路线图。
- 最新版是 v1.7.2（2026-11-06）：完整桌面下载、选中文本朗读、更简单的模型设置、韩语界面预览、NVIDIA NIM 向量嵌入。
- 从 1.6.15 或更早升级：先停掉、备份运行时目录、卸载老版 `deeptutor-cli` 包，再装新版；保持同一个 `DEEPTUTOR_HOME`。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/HKUDS/DeepTutor
- 原 README：https://github.com/HKUDS/DeepTutor#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
