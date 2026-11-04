# worktrunk：给并行跑的 AI agent 一人一个工作区

- 原项目：max-sixty/worktrunk
- 原项目链接：https://github.com/max-sixty/worktrunk
- 榜单：日榜 2026-11-04 第 3 名
- 翻译日期：2026-11-04
- 原项目许可：MIT OR Apache-2.0（README 徽章；仓库页面的 license 栏未标注，以 LICENSE 文件为准）
- 原项目数据（2026-11-04 核对）：Star 10,467，Fork 375，创建于 2025-10-17

## 一句话介绍

一个 Git worktree 管理命令行工具，专门为同时并行跑多个 AI agent 设计：每个 agent 各自一个工作目录，互不踩对方的改动，而操作 worktree 像操作分支一样简单。

## 适合谁

- 同时让好几个 Claude Code、Codex 之类的 agent 在同一个仓库里干活的人
- 被 Git 原生 worktree 的繁琐命令折磨过的人
- 想给每个任务开独立工作区、又不想手动算路径、手动清理的人

## 它解决什么问题

- AI agent 现在能无人监督地干长任务，同时管 5 到 10 个并行 agent 完全可行。Git 原生的 worktree 功能正好能给每个 agent 一个独立工作目录，让它们不互相踩改动。
- 但原生 worktree 的体验很别扭：只是一个新建 worktree 的小任务，就要把分支名敲三遍，`git worktree add -b feat ../repo.feat`，再 `cd ../repo.feat`。
- 并行一多，清理、合并、看状态、共享构建缓存这些活全是手工，agent 越多越乱。

worktrunk 的做法是：三个核心命令让 worktree 像分支一样好用，再加一堆省事的功能（hook、合并流程、共享构建缓存、CI 状态），让并行 agent 的工作区管得住。

## README 翻译（核心部分）

原文标题是 Worktrunk，副标题是 Worktrunk is a CLI for git worktree management, designed for running AI agents in parallel.，意思是 Worktrunk 是一个 Git worktree 管理 CLI，为并行运行 AI agent 而设计。

原文核心说法翻译如下：

> Worktrunk 的三个核心命令让 worktree 像分支一样简单。另外，Worktrunk 还有一堆提高生活质量的功能，帮你简化同时处理多个并行改动，包括自动化本地工作流的 hook 和写时复制（copy-on-write）构建缓存。

背景（原文 Context: git worktrees 翻译）：Claude Code 和 Codex 这样的 AI agent 已经能不监督地处理长任务，所以同时管理 5 到 10 个并行 agent 是可行的。Git 原生的 worktree 功能给每个 agent 一个独立工作目录，让它们不踩对方的改动。但 Git worktree 的用户体验很别扭，哪怕只是新建一个 worktree 这样的小任务，也要把分支名敲三遍。

Worktrunk 让 worktree 像分支一样简单（原文翻译）：worktree 按分支名寻址，路径按可配置的模板算出来。接受分支名的命令也接受该 worktree 检出的路径。

核心命令对照表（原文翻译）：

| 任务 | Worktrunk | 原生 Git |
| --- | --- | --- |
| 切换 worktree | `wt switch feat` | `cd ../repo.feat` |
| 新建并启动 Claude | `wt switch -c -x claude feat` | `git worktree add -b feat ../repo.feat && cd ../repo.feat && claude` |
| 清理 | `wt remove` | `cd ../repo && git worktree remove ../repo.feat && git branch -d feat` |
| 带状态的列表 | `wt list` | `git worktree list`（只有路径） |

进阶功能（原文 Workflow automation 翻译）：

- **Hook**：在创建、合并前、合并后等时机跑命令。
- **LLM 提交信息**：按 diff 生成提交信息。
- **合并流程**：压缩（squash）、变基（rebase）、合并、清理，一条命令做完。
- **交互式选择器**：浏览 worktree，带流式 CI 状态和 diff、日志、PR 和评论预览。
- **共享构建缓存**：十个 worktree 共用 `target/`、`node_modules/` 这些目录，不用重复构建或复制（支持 APFS、btrfs 和 XFS）。
- **`wt list --full`**：每个分支的 CI 状态和 AI 生成的摘要。
- **PR 检出**：`wt switch pr:123` 直接跳到某个 PR 的分支。
- **每个 worktree 一个开发服务器**：`hash_port` 模板过滤器给每个 worktree 一个唯一的端口。
- **别名和按分支变量**：自定义 `wt <名字>` 命令和分支范围的状态，供 hook 模板用。

快速上手（原文 Quick start 翻译）：给一个新功能建 worktree：

```bash
$ wt switch --create feature-auth

✓ Created branch feature-auth from main and worktree @ ~/repo.feature-auth
```

这条命令新建一个分支和 worktree，然后切换过去。干完活，用 `wt list` 看所有 worktree：

```bash
$ wt list

  Branch        Status      HEAD±     main↕    main…±    Remote⇅  Commit    Age  Message
@ feature-auth  +   ↑      +27   -8   ↑1       +31                4bc72dc    2h  Add authenticatio…
^ main              ^⇡                                    ⇡1      0e631ad    1d  Initial commit

○ Showing 2 worktrees, 1 with changes, 1 ahead, hidden: Path
```

`@` 标记当前 worktree。`+` 表示有已暂存的改动，`↑1` 表示比 main 超前 1 个提交，`⇡` 表示有未推送的提交。

做完之后二选一：

**PR 流程**：提交、推送、开 PR、在 GitHub/GitLab 上合并，然后清理：

```bash
wt step commit                    # 提交已暂存的改动
gh pr create                      # 或者 glab mr create
wt remove                         # PR 合并之后清理
```

**本地合并**：压缩、变基到 main、快进合并、清理：

```bash
$ wt merge main

◎ Generating commit message and committing changes... (2 files, +53, no squashing needed)
  Add authentication module
✓ Committed changes @ a1b2c3d
◎ Merging 1 commit to main @ a1b2c3d (no rebase needed)
  * a1b2c3d Add authentication module
   auth.rs | 51 +++++++++++++++++++++++++++++++++++++++++++++++++++
   lib.rs  |  2 ++
   2 files changed, 53 insertions(+)
✓ Merged to main (1 commit, 2 files, +53)
◎ Removing feature-auth worktree & branch in background (same commit as main, _)
○ Switched to worktree for main @ ~/repo
```

并行跑多个 agent 时，每个 worktree 里启动一个 agent：

```bash
wt switch -x claude -c feature-a -- 'Add user authentication'
wt switch -x claude -c feature-b -- 'Fix the pagination bug'
wt switch -x claude -c feature-c -- 'Write tests for the API'
```

`-x` 参数是在切换后运行一条命令，`--` 后面的参数传给它。配好启动后 hook 可以自动化准备工作（装依赖、启动开发服务器）。

## 中文部署操作指南

按原项目 README 整理，未实机跑通，请以原项目最新文档为准。完整文档在 worktrunk.dev。

### 方式一：Homebrew 安装（macOS 和 Linux）

```bash
brew install worktrunk && wt config shell install
```

shell 集成让命令可以切换目录，装完要跑后面那句。

### 方式二：Cargo 安装

```bash
cargo install worktrunk && wt config shell install
```

### 方式三：Windows

`wt` 默认是 Windows Terminal 的命令，所以 Winget 会另外把 Worktrunk 装成 `git-wt`，避免冲突：

```bash
winget install max-sixty.worktrunk
git-wt config shell install
```

也可以关掉 Windows Terminal 的别名（设置 → 应用 → 高级应用设置 → 应用执行别名 → “Terminal”/“Terminal Preview”），直接用 `wt`。

### 方式四：其他系统

Arch Linux：

```bash
sudo pacman -S worktrunk && wt config shell install
```

Conda / Pixi（社区维护的 feedstock）：

```bash
conda install -c conda-forge worktrunk && wt config shell install
```

Pixi：`pixi global install worktrunk && wt config shell install`。

### 方式五：上手跑起来

```bash
wt switch --create feature-auth   # 新建分支 + worktree 并切换过去
wt list                           # 看所有 worktree 的状态
wt switch -x claude -c feature-a -- 'Add user authentication'   # 新建 worktree 并在里面启动 Claude
wt merge main                     # 本地合并：压缩、变基、合并、清理一条龙
wt remove                         # 清理当前 worktree 和分支
```

## 配置说明

- shell 集成：装完必须跑 `wt config shell install`，否则命令没法切换目录。
- 路径模板：worktree 路径按可配置的模板算出来，默认像 `~/repo.feature-auth` 这样按分支名拼。
- hook：创建、合并前、合并后等时机可以跑自定义命令，用来自动化准备工作（装依赖、启动开发服务器）。
- 共享构建缓存：多个 worktree 共用 `target/`、`node_modules/` 这类目录，底层靠写时复制，需要 APFS、btrfs 或 XFS 文件系统。
- 每个 worktree 一个开发服务器：用 `hash_port` 模板过滤器给每个 worktree 分一个唯一端口，避免端口冲突。
- 别名和按分支变量：可以自定义 `wt <名字>` 命令和分支范围的状态，供 hook 模板调用。

## 注意事项

- Windows 上 `wt` 和 Windows Terminal 的命令重名，Winget 默认装成 `git-wt`，想用 `wt` 要先关掉系统那个别名。
- 原文说 Worktrunk 在 2026 年初发布后很快成了最流行的 git worktree 管理器；作者说没有 AI 生成的粗糙内容，遇到任何不顺畅请反馈。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/max-sixty/worktrunk
- 原 README：https://github.com/max-sixty/worktrunk#readme
- 官方文档：https://worktrunk.dev

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 MIT OR Apache-2.0。
