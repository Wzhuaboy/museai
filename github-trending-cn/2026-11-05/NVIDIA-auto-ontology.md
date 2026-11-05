# Auto Ontology：给数据加一层语义图谱，让 agent 查数不再瞎编

- 原项目：NVIDIA/auto-ontology
- 原项目链接：https://github.com/NVIDIA/auto-ontology
- 榜单：日榜 2026-11-05 第 1 名
- 翻译日期：2026-11-05
- 原项目许可：Apache-2.0
- 原项目数据（2026-11-05 核对）：Star 6,115，Fork 482，创建于 2026-04-27

## 一句话介绍

NVIDIA 的开源库，从企业元数据自动生成一层"本体"（ontology）——语义图谱推理层，告诉 agent 数据在哪里、是什么意思、该不该用、该怎么用，让自然语言查库的结果可验证、可解释。

## 适合谁

- 做企业数据问答、Text-to-SQL、让 agent 查数据库的人
- 被"同一个指标各系统口径不一致""agent 生成的 SQL 看着对、结果是错的"折磨过的人
- 有 Postgres 环境、能接 NVIDIA NIM 推理接口的团队

## 它解决什么问题

- Agent 能查文档、能连数据库，但可靠性是瓶颈：营收指标答得再快，数字错了等于零。
- 各系统对同一个业务概念的定义不一致，agent 不知道该信哪一个。
- Agent 生成的 SQL 没法验证对错，答案没有出处，错了也不知道错在哪。

Auto Ontology 的做法是：在数据和 agent 之间加一层语义上下文——从企业元数据自动生成本体，统一各系统的定义，再把这层上下文通过 MCP、CLI、API 交给任何 agent 框架用。

## README 翻译（核心部分）

原文开篇的意思是：Agent 能检索文档、能查询数据库，但可靠性决定了 agent 数据分析能不能用。Agent 需要一层上下文，告诉它数据在哪里、是什么意思、该不该用、该怎么用、从哪来、和什么相似。NVIDIA Auto Ontology 就是开源实现这一层的库：从企业元数据构建它，调和跨系统的定义，再通过 MCP、CLI、API 暴露给任何 agent 框架。它补充而不是替代你已有的语义模型。

它让开发者能做到五件事（原文翻译）：

- **发现（Discover）**：从元数据生成企业本体；接上已有的本体和语义模型；构建 AI 就绪的知识图谱。
- **扎根（Ground）**：给 agent 关于指标、实体、关系的可信业务含义；调和跨系统不一致的定义。
- **校验（Validate）**：按认证过的定义和血缘校验生成的查询；每个答案都带出处。
- **暴露（Expose）**：通过 MCP、CLI、API 把上下文交给任何 agent 框架。
- **学习（Learn）**：把认证过的修正和使用反馈折回本体，共享上下文越用越好。

### 本体里装了三种定义

- **术语（Terms）**：业务概念，比如 Customer（客户）、Invoice Line（发票行），每个带描述和同义词，映射到实际存放它的列。
- **SQL 属性（SQL attributes）**：审核过的 SQL 表达式，比如毛利、滚动合计，挂在某个术语下面。Agent 复用它们，同一个指标每次算法都一致。
- **关系（Relationships）**：表之间怎么 join，包括桥接表，从键和数据里推断出来。

### 三个阶段：生成、认证、回答

**生成（Generate）**：摄入服务从源数据库起草第一版本体：

1. 读源库：抽取 schema、给列做画像、采样值，写进目录。
2. 命名实体：逐表抽术语，映射到列。
3. 解析关系：推断表间 join 和桥接表，从查询历史建议 SQL 属性。
4. 写本体：术语、关系、SQL 属性存进 Postgres，embedding 存进 pgvector 做检索。

结果是一张可以在 UI 里探索的语义图。原文例子：一次编译 Wide World Importers（微软的示例销售库）产出了 31 个术语，点开 Order 能看到它的描述、相关术语、映射的列和 SQL 属性。

**认证（Certify）**：人让草稿变得可信：

1. 在 Chat 里用真问题测试，或走 MCP 的 `check_answerable` 和 `ask_question`。
2. 在 UI 或 API 里修正术语、描述和 SQL 属性。
3. 确认无误后认证名称、描述和 SQL 属性。

**回答（Answer）**：每个问题 agent 按五步走：

1. 分类意图，抽出问题里提到的实体。
2. 用 embedding 检索候选术语、列和 SQL 属性。
3. 根据候选写 SQL。
4. 校验过滤值和查询本身，校验失败就修复 SQL。
5. 执行查询，返回答案时附上 SQL 和推导步骤。

候选撑不起这个问题时，agent 会直接报告这个问题用现有数据答不了。预测类问题在配好 KumoRFM 时会交给它。

### 核心功能（原文 Key Features 翻译）

- **自然语言查询结构化数据**：问题翻译成 SQL 再到连接的数据库上执行，由 NVIDIA NIM 驱动。
- **语义目录 / 本体层**：覆盖关系型数据源，和它描述的目录一起存在 Postgres 里。
- **认证与 RBAC**：用 Better Auth 实现。
- **Web UI**：聊天、分析、数据目录、分析和设置。
- **灵活部署**：Kubernetes 用 Helm chart，本地用 Docker Compose。

### 软件组件（原文 Software Components 翻译）

| 组件 | 技术 | 作用 | 默认端口 |
| --- | --- | --- | --- |
| 前端 | Next.js 16（React 19、TypeScript、Tailwind CSS 4）、Better Auth、Prisma | Web UI、认证、API 网关 | 3000 |
| 后端 | FastAPI（Python 3.12+）、LangChain | 聊天 / 自然语言转 SQL、目录、数据源 API | 3001 |
| 摄入 worker | FastAPI（Python 3.12+） | 摄入表格数据、写 embedding | 3002 |
| Postgres + pgvector | 关系型数据库 | 应用元数据、目录和本体、向量存储 | 5432 |
| HashiCorp Vault | 可选 | 连接凭证的安全存储 | — |

### 模型配置：NVIDIA NIM 与三元组

Auto Ontology 用 NVIDIA NIM 推理接口，可以是托管的 NVIDIA API 目录（`integrate.api.nvidia.com`），也可以自托管 NIM。`.env.example` 里的默认值：

- **大模型（LLM）**：`nvidia/nemotron-3.5-lightning-30b-a3b`
- **Embedding**：`nvidia/nemotron-3-embed-1b`
- **重排序（Reranking）**：`nvidia/llama-nemotron-rerank-vl-1b-v2`

每个模型角色由一组三个环境变量配置（原文叫"三元组"）：`<PREFIX>_ENDPOINT`（地址）、`<PREFIX>_API_KEY`、`<PREFIX>_MODEL`：

| 前缀 | 角色 |
| --- | --- |
| `DEFAULT_MODELS` | 共享默认；下面每个字段都回落到它 |
| `REASONING` | 主聊天 / 自然语言转 SQL 的模型 |
| `NON_REASONING` | 实体抽取用的轻量模型 |
| `EMBED` | 文本 embedding 模型（摄入和查询必须一致） |
| `RERANK` | 检索流程用的重排序模型 |

只填 `DEFAULT_MODELS_*` 是最简单的配置方式，有区别的字段再单独覆盖。`*_API_KEY` 也兼容旧的 `NVIDIA_API_KEY`。

### 基准与贡献状态

- 基准：跑 BIRD 这类 Text-to-SQL 基准，去 ontology SQL evaluation 仓库（原文 Benchmarks 一节）。
- 项目按 Apache License 2.0 分发，**目前不接受外部贡献**（原文原话）。

## 中文部署操作指南

按原项目 README 整理，未实测，请以原项目最新文档为准。

### 方式一：Docker Compose 快速上手（官方 Quickstart）

前置要求：Docker + Compose v2、`uv`、一个 NVIDIA API key（`nvapi-...`，去 build.nvidia.com 领取）。

1. 克隆仓库并建 `.env`：

```bash
git clone https://github.com/NVIDIA/auto-ontology.git && cd auto-ontology
cp .env.example .env
```

然后在 `.env` 里填这些值（把每个默认密码都换掉再启动）：

```
DEFAULT_MODELS_API_KEY=nvapi-你的key
AUTH_SECRET=你的密钥
APP_URL=http://localhost:3000
POSTGRES_PASSWORD=你的密码
CONNECTION_STRINGS=postgresql://postgres:同一个密码@postgres:5432/wideworldimporters
AUTO_ONTOLOGY_ADMIN_PASSWORD=你的密码
PGADMIN_PASSWORD=你的密码
```

`.env.example` 还给每个模型角色单独配了一个 key：把每个 `nvapi-your-api-key-here` 换成自己的 key，或者删掉这些行、让它们回落到 `DEFAULT_MODELS_API_KEY`。

2. 启动 Postgres 并灌入示例库 Wide World Importers（种子脚本在 auto-ontology-eval 仓库里）：

```bash
docker compose up -d --wait postgres
git clone https://github.com/NVIDIA/auto-ontology-eval.git ../auto-ontology-eval
(cd ../auto-ontology-eval && uv sync && cp .env.example .env && \
  POSTGRES_PASSWORD=你的密码 \
  uv run python scripts/seed/seed_wwi.py --database-name wideworldimporters --drop)
```

3. 构建并启动其余服务：

```bash
docker compose up -d --build
```

4. 打开 http://localhost:3000 ，用 `.env` 里的 `AUTO_ONTOLOGY_ADMIN_EMAIL` 和 `AUTO_ONTOLOGY_ADMIN_PASSWORD` 登录。去 **Settings → Semantic Compilation** 打开它。摄入在启动时就跑，编译会立刻开始，完成后报告 **Semantic compilation is ready**。

5. 在 **Chat** 里提问，比如原文的例子：

> What was revenue for the USB food flash drive - sushi roll in Pennsylvania in June 2015?

Agent 会把 revenue、product、state 解析到本体里的术语，顺着关系找到需要的 join，跑查询。答案连同 SQL 和推导步骤一起返回，可以对照源头核对。原文例子里答案是 $588.80，来自 3 行发票明细。

6. 问一个数据答不了的问题试试：Wide World Importers 没有广告数据，问广告投入回报率时，通过 MCP 接入的 agent 会先调 `check_answerable` 检查可答性，发现没有术语覆盖 "ad spend"，然后直接告诉你算不了，并问你要不要改问 2015 年 6 月的营收，或者有没有别的记录广告花费的数据源该接进来。

### 方式二：接自己的 agent

本体建好后，除了 Web UI，还可以通过 MCP server、Agent skills、REST API 接自己的 agent 框架。仓库根目录有 `mcp/` 和 `skills/`，部署文档见仓库里的 `DEPLOYMENT.md`。

### 方式三：Kubernetes 部署

仓库自带 `helm/auto-ontology` Helm chart，见原 README 的灵活部署一节。

## 配置说明

- 模型三元组：`DEFAULT_MODELS_*` 是共享默认，`REASONING` / `NON_REASONING` / `EMBED` / `RERANK` 各自可覆盖；API key 统一用 `DEFAULT_MODELS_API_KEY` 最省事。
- 数据源：`CONNECTION_STRINGS` 里填自己的数据库连接串，示例库 Wide World Importers 只是演示。
- 管理员账号：`AUTO_ONTOLOGY_ADMIN_EMAIL` / `AUTO_ONTOLOGY_ADMIN_PASSWORD`，首次登录用。
- Embedding 模型摄入和查询必须用同一个，否则检索对不上。

## 注意事项

- 需要 NVIDIA API key（`nvapi-...`），额度和费用按 NVIDIA 的政策。
- 仓库目前没有正式 Release，安装走 git clone。
- 重启后 UI 左侧导航加载不出来，通常是浏览器留了旧的 session cookie：清除 `localhost:3000` 的站点数据再重新登录。其他安装失败见仓库 setup skill 的排障指南。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/NVIDIA/auto-ontology
- 原 README：https://github.com/NVIDIA/auto-ontology#readme
- Text-to-SQL 基准仓库：https://github.com/NVIDIA/auto-ontology-eval

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 Apache-2.0。
