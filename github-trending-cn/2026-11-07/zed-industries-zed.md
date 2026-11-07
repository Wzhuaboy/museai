# Zed：Atom 原班人马做的高速多人代码编辑器

- 原项目：zed-industries/zed
- 原项目链接：https://github.com/zed-industries/zed
- 榜单：日榜 2026-11-07 第 1 名
- 翻译日期：2026-11-07
- 原项目许可：GPL-3.0-or-later 为主，Apache-2.0 组件并存（按 README 原文；GitHub 仓库元数据里显示为 Other）
- 原项目数据（2026-11-07 核对）：Star 93,997，Fork 11,532，创建于 2021-02-20，提交 40,745 次，Release 1,322 个

## 一句话介绍

Zed 是一款高性能、多人协作的代码编辑器，由 Atom 和 Tree-sitter 的原班人马打造，口号是"Code at the speed of thought"（以思考的速度写代码）。

## 适合谁

- 每天长时间写代码、觉得编辑器卡顿拖慢思路的开发者
- 需要和队友实时同屏协作写代码的人
- 用过 Atom、怀念它又想要更快更现代替代品的人
- 对编辑器性能和响应速度有执念的人

## 它解决什么问题

- 传统编辑器在打开大文件、处理大项目时容易卡顿，Zed 用 Rust 和自研的 GPUI 框架写成，目标就是快：启动快、输入响应快、滚动快。
- 多人协作不是事后加的插件，而是编辑器内置能力：可以和队友实时共享同一个编辑会话。
- Atom 停更后留下的空白：Zed 的团队就是 Atom 和 Tree-sitter 的原作者，算是一次"原班人马重做编辑器"。

## README 翻译（核心部分）

Zed 的 README 本身很短，核心内容就下面这些（功能细节不在 README 里，更多介绍在官网 zed.dev）：

### 这是什么

欢迎来到 Zed，一款高性能、多人代码编辑器，由 Atom 和 Tree-sitter 的创造者打造。

### 安装

macOS、Linux 和 Windows 上可以直接从官网下载 Zed，或者用本地包管理器安装。

其他平台目前还没有：

- Web 版（有专门的追踪讨论帖，见原 README 里的链接）

### 开发 Zed

想自己编译 Zed 的话，README 给了三份构建文档链接：

- Building Zed for macOS
- Building Zed for Linux
- Building Zed for Windows

### 参与贡献

贡献方式见仓库里的 CONTRIBUTING.md。

另外，Zed 团队在招人，招聘信息在官网的 jobs 页面。

### 许可

Zed 源码主要按 GPL-3.0-or-later 许可，标明的部分组件用 Apache-2.0。

第三方依赖的许可信息必须正确提供，否则 CI 不通过。项目用 `cargo-about` 自动做开源许可合规检查。如果 CI 报错：

- 某个自己新建的 crate 报 `no license specified`：在该 crate 的 `Cargo.toml` 里 `[package]` 下加 `publish = false`。
- 某个依赖报 `failed to satisfy license requirements`：先确认这个项目用的许可、确认当前这套合规机制是否够用，不确定就问律师；确认没问题后，把许可的 SPDX 标识加进 `script/licenses/zed-licenses.toml` 的 `accepted` 数组。
- `cargo-about` 认不出某个依赖的许可：按 cargo-about 手册，在 `script/licenses/zed-licenses.toml` 末尾加 clarification 字段。

### 赞助

Zed 由营利公司 Zed Industries, Inc. 开发。想在经济上支持这个项目，可以通过 GitHub Sponsors 赞助。

赞助款直接归 Zed Industries，作为公司一般收入，不附带任何权益或特权。

## 中文部署操作指南

### 方式一：直接安装（推荐）

去官网下载安装包，或用系统包管理器安装：

- 官网：https://zed.dev
- macOS、Linux、Windows 都有官方版本；Web 版目前没有。

### 方式二：从源码构建

README 没有在正文里贴构建命令，只给了三份构建文档的链接：

- macOS 构建文档：见原 README 的 "Building Zed for macOS" 链接
- Linux 构建文档：见原 README 的 "Building Zed for Linux" 链接
- Windows 构建文档：见原 README 的 "Building Zed for Windows" 链接

按文档走即可，本文不再转抄命令，避免版本变了对不上。

## 配置说明

- 安装后即用，README 里没有需要手动填的必填配置。
- 想自己编译的话，仓库用 Rust 工具链（`rust-toolchain.toml` 已锁定版本），按构建文档操作。

## 注意事项

- Zed 的 README 非常短，编辑器的具体功能（AI、协作、扩展等）都不在 README 里，装好之后看官网文档为准。
- Web 版目前还没有，不要按"网页版 Zed"去找。
- 许可方面注意：源码主体是 GPL-3.0-or-later，不是 MIT/Apache 那种宽松许可，拿源码二次开发、商用前先看清许可条款。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/zed-industries/zed
- 原 README：https://github.com/zed-industries/zed#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
