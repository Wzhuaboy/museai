# AnyPS5：把 PS5 游戏可执行文件自动移植到 Linux 和 Windows

- 原项目：boykopovar/AnyPS5
- 原项目链接：https://github.com/boykopovar/AnyPS5
- 榜单：月榜 2026-11-05 第 2 名
- 翻译日期：2026-11-05
- 原项目许可：GPL-2.0
- 原项目数据（2026-11-05 核对）：Star 51,297，Fork 4,884，创建于 2026-08-03

## 一句话介绍

自动把 PS5 可执行文件移植到 Linux 和 Windows 的工具：用 relinker 把可执行文件转成目标系统的原生格式，再配上自行实现的系统 prx 库做动态链接，不用模拟器、没有独立的运行时进程。

## 适合谁

- 想在 PC 上跑 PS5 游戏的人（研究、兼容性、保存目的）
- 对游戏移植、逆向工程、图形 API（Vulkan / SPIR-V）感兴趣的开发者
- 关注"不用模拟整机、只移植可执行文件"这条技术路线的人

## 它解决什么问题

- PS5 游戏只能在 PS5 主机上跑，想在 PC 上玩，传统办法是模拟器：整机模拟开销大，兼容性要一个游戏一个游戏啃。
- AnyPS5 换了一条路：不模拟整机，只把可执行文件重链接成 Linux / Windows 原生格式，游戏调用的系统库由项目自己实现的 prx 库承接，跑起来就是原生程序。

## README 翻译（核心部分）

### 它是什么（原文 About 翻译）

自动把可执行文件移植到 Linux 和 Windows 的工具。只有 relinker 的构建能在 macOS 上跑，包括 Apple Silicon。

核心由两部分组成：一个 **relinker**，把可执行文件转换成目标系统的原生格式；以及一套自行实现的 **system prx libraries**（系统动态库），供动态链接用。没有模拟，也没有单独的运行时进程。

还有一个**网页转换器**，在线就能转，文件留在你自己的设备上，不上传。

### 进度（原文 Status 翻译）

项目首页挂了几块进度看板：系统库实现百分比、已解码的着色器形态数、7 天实现进度、进度地图和进度历史。

注意口径：系统库百分比是按"项目目前已声明的函数"（`core/libs/prx` 里声明的）来算的，不是全部 PS5 系统函数；随着声明的函数越来越多，总数还会涨。

**着色器重编译器**已经能成功产出 SPIR-V（用 `ANYPS5_ENABLE_SPIRV_TOOLS` 构建时，可以经 Spirv-Tools 校验）。

### 兼容性（原文 Compatibility 翻译）

每个游戏的状态和测试报告都在 **Game bring-up** 讨论区，一个游戏一个帖子。动手之前先去那里查你要玩的游戏有没有人跑通过。

### 输入映射（原文 Input mapping 翻译）

支持 SDL 映射的手柄，包括摇杆和扳机。键盘鼠标用 `anyps5-input.ini` 文件配置，支持的设备和配置格式见仓库的输入映射文档。

### 免责声明（原文 Disclaimer 翻译）

本项目面向互操作性、研究、保存和兼容性目的。它不包含、不分发、也不需要受版权保护的软件、固件、加密密钥或专有库。用户自己负责确保所用二进制文件的获取和使用符合适用法律和各自的许可条款。

AnyPS5 是独立项目，与索尼互动娱乐无关，未获其授权或背书。"PlayStation" 和 "PS5" 是索尼互动娱乐公司的商标。

## 中文部署操作指南

按原项目 README 整理，未实测，请以原项目最新文档为准。

### 方式一：网页转换器（不用安装）

打开项目 README 里的 **Web converter** 链接，在线转换，文件留在你自己的设备上。页面标题就是 "PS5 apps to Windows/Linux converter"，用法是选一个文件夹或拖入 ZIP 文件：每个应用需要一个可执行 ELF 文件加 `sce_sys/` 和 `sce_module/`，只接受已解密的 ELF 文件；还有一个"把 AMD 专属指令转给 Intel CPU"的选项。注意两点：单个应用限 256 MiB，超过的用原生 relinker；页面自己也写明了，转换不保证应用一定能跑起来。

### 方式二：从源码构建

仓库是 CMake 工程（根目录有 `CMakeLists.txt`），按仓库 `docs` 里的 Build instructions 构建。需要校验着色器输出时，构建加上 `ANYPS5_ENABLE_SPIRV_TOOLS`，产出的 SPIR-V 会经 Spirv-Tools 校验。

### 方式三：用正式 Release

仓库已有 5 个正式 Release，最新为 v0.1.4（注：本项目 10 月登顶月榜时还没有公开版本，现在已经补上了）。

### 方式四：先查兼容性再动手

去仓库 Discussions 里的 **Game bring-up** 区，找到你要玩的游戏那个帖子，看当前状态和别人的测试报告，再决定要不要动手。

## 配置说明

- 手柄：走 SDL 映射，摇杆和扳机都支持。
- 键盘鼠标：用 `anyps5-input.ini` 文件配置，支持的设备和配置格式见仓库的输入映射文档。
- 着色器校验：构建时加 `ANYPS5_ENABLE_SPIRV_TOOLS` 才会经 Spirv-Tools 校验。

## 注意事项

- 遇到不支持或非预期状态，程序会抛 C++ 异常，通常是 `std::runtime_error`；没被捕获的异常会把 `what()` 打印到 stderr 然后退出进程。
- 游戏兼容性逐个游戏不同，动手前先查 Game bring-up 讨论区。
- 版权提醒：项目本身不含任何受版权保护的软件、固件、密钥或专有库；你用的游戏文件来源和用法要自己保证合法合规。
- 是否实测：按文档整理，未实测。

## 原文链接

- 原项目：https://github.com/boykopovar/AnyPS5
- 原 README：https://github.com/boykopovar/AnyPS5#readme
- 网页转换器：https://boykopovar.github.io/AnyPS5/ （见原 README 链接）
- 使用方法 / 构建说明 / 架构：见原 README 里的 Usage、Build instructions、Architecture 链接

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有，原项目许可为 GPL-2.0。
