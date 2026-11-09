# Sherlock：拿一个用户名，在 400 多个社交网站上找账号

- 原项目：sherlock-project/sherlock
- 原项目链接：https://github.com/sherlock-project/sherlock
- 榜单：日榜 2026-11-09 第 1 名
- 翻译日期：2026-11-09
- 原项目许可：MIT
- 原项目数据（2026-11-09 核对）：Star 103,605，Fork 12,132，创建于 2018-12-24，提交 2,934 次，Release 3 个

## 一句话介绍

Sherlock 是一个命令行工具：给它一个用户名，它去 400 多个社交网站上一个一个查，这个用户名都在哪些站上注册过账号。

## 适合谁

- 做开源情报（OSINT）、安全测试、渗透测试的人
- 想查自己信息泄露的人：同一个用户名在多少网站上出现过
- 查人、查账号归属，需要快速摸底的人
- 喜欢命令行小工具、想一条命令出结果的人

## 它解决什么问题

- 一个用户名散落在几百个网站上，手动一个个站去搜是不可能的。Sherlock 一次跑完 400 多个站，结果汇总成一个文件。
- 不用注册、不用 API 密钥、不用写爬虫：装好、敲一个用户名就出结果。
- 结果不只打在屏幕上，还能导成 CSV、Excel、txt，方便留档、进报告、做进一步分析。

## README 翻译（核心部分）

### 这是什么

在 400 多个社交网站上，按用户名找账号。

### 安装

| 方法 | 说明 |
| --- | --- |
| `pipx install sherlock-project` | `pip` 或 `uv` 也可以代替 `pipx` |
| `docker run -it --rm sherlock/sherlock` |  |
| `dnf install sherlock-project` |  |

Debian（>= 13）、Ubuntu（>= 22.10）、Homebrew、Kali 和 BlackArch 有社区维护的包，这些包不是 Sherlock Project 直接支持和维护的。

注意：ParrotOS 和 Ubuntu 24.04 上由第三方维护的包疑似**坏了**，这些系统的用户请改用 `uv`/`pipx`/`pip` 或 Docker。

所有其他安装方法见原文链接。

### 一般用法

只查一个用户：

```bash
sherlock user123
```

查多个用户：

```bash
sherlock user1 user2 user3
```

找到的账号会存进以对应用户名命名的单个文本文件里（比如 `user123.txt`）。

```bash
$ sherlock --help
usage: sherlock [-h] [--version] [--verbose] [--folderoutput FOLDEROUTPUT] [--output OUTPUT] [--csv] [--xlsx] [--site SITE_NAME] [--proxy PROXY_URL]
[--dump-response]
                [--json JSON_FILE] [--timeout TIMEOUT] [--print-all] [--print-found] [--no-color] [--browse] [--local] [--nsfw] [--txt] [--ignore-exclusions]
                USERNAMES [USERNAMES ...]

Sherlock: Find Usernames Across Social Networks (Version 0.16.0)

positional arguments:

  USERNAMES             One or more usernames to check with social networks. Check similar usernames using {?} (replace to '_', '-', '.').

options:

  -h, --help            show this help message and exit
  --version             Display version information and dependencies.
  --verbose, -v, -d, --debug
                        Display extra debugging information and metrics.
  --folderoutput FOLDEROUTPUT, -fo FOLDEROUTPUT
                        If using multiple usernames, the output of the results will be saved to this folder.
  --output OUTPUT, -o OUTPUT
                        If using single username, the output of the result will be saved to this file.
  --csv                 Create Comma-Separated Values (CSV) File.
  --xlsx                Create the standard file for the modern Microsoft Excel spreadsheet (xlsx).
  --site SITE_NAME      Limit analysis to just the listed sites. Add multiple options to specify more than one site.
  --proxy PROXY_URL, -p PROXY_URL
                        Make requests over a proxy. e.g. socks5://127.0.0.1:1080
  --dump-response       Dump the HTTP response to stdout for targeted debugging.
  --json JSON_FILE, -j JSON_FILE
                        Load data from a JSON file or an online, valid, JSON file. Upstream PR numbers also accepted.
  --timeout TIMEOUT     Time (in seconds) to wait for response to requests (Default: 60)
  --print-all           Output sites where the username was not found.
  --print-found         Output sites where the username was found (also if exported as file).
  --no-color            Don't color terminal output
  --browse, -b          Browse to all results on default browser.
  --local, -l           Force the use of the local data.json file.
  --nsfw                Include checking of NSFW sites from default list.
  --txt                 Enable creation of a txt file
  --ignore-exclusions   Ignore upstream exclusions (may return more false positives)
```

### 致谢

感谢每一位为 Sherlock 做出贡献的人！

### 许可

MIT © Sherlock Project

作者：Siddharth Dushantha

## 中文部署操作指南

### 方式一：pipx 安装（推荐）

```bash
pipx install sherlock-project
```

`pip` 或 `uv` 也可以代替 `pipx`。

### 方式二：Docker

```bash
docker run -it --rm sherlock/sherlock
```

### 方式三：系统包

```bash
dnf install sherlock-project
```

Debian、Ubuntu、Homebrew、Kali、BlackArch 也有社区包，但不是官方维护的。

### 装完先跑一遍

```bash
sherlock user123
```

结果默认存进 `user123.txt`。

## 配置说明

- 不用配账号、不用 API 密钥、不用填 token，装好就能跑。
- 常用选项：`--csv` 导 CSV，`--xlsx` 导 Excel，`--site` 只查指定站（可多次指定），`--proxy` 走代理（比如 `socks5://127.0.0.1:1080`），`--timeout` 改超时时间（默认 60 秒）。
- 想查相似用户名，用 `{?}` 通配：`{?}` 会替换成 `_`、`-`、`.` 再查一遍。
- `--nsfw` 默认不查 NSFW 站点，加了才查；`--ignore-exclusions` 会忽略上游的排除规则，可能多出误报。

## 注意事项

- ParrotOS 和 Ubuntu 24.04 上第三方维护的包疑似坏了，别用系统包，走 `uv`/`pipx`/`pip` 或 Docker。
- 查出来的"找到"不等于本人注册：同名不同人也会命中，拿结果当线索用，别直接当定论。
- 只用它查公开信息，别拿去骚扰、冒充别人；遵守各站点的使用条款和当地法律。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/sherlock-project/sherlock
- 原 README：https://github.com/sherlock-project/sherlock#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
