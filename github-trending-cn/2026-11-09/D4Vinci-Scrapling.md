# Scrapling：从一次请求到整站爬取，一个 Python 网页抓取框架全包

- 原项目：D4Vinci/Scrapling
- 原项目链接：https://github.com/D4Vinci/Scrapling
- 榜单：周榜 2026-11-09 第 10 名（顺推；周榜第 1–8 名已翻过，第 9 名紫微斗数是中文 README、已跳过）
- 翻译日期：2026-11-09
- 原项目许可：BSD-3-Clause
- 原项目数据（2026-11-09 核对）：Star 99,895，Fork 10,443，创建于 2024-10-13，提交 1,824 次，Release 55 个

## 一句话介绍

Scrapling 是一个 Python 网页抓取框架，把快速 HTTP 请求、隐身浏览器、强力解析和并发爬取收进一个库：抓静态页、渲染 JavaScript、跟网站交互、抽它背后 API 的数据，从提几个字段到整站抓成干净的 Markdown 都行。

## 适合谁

- 写爬虫、做数据采集的人，从单页抓取到整站爬取都要
- 被 Cloudflare、反爬、JS 渲染卡住过的人
- 想让 AI agent 自己上网抓数据的人（它有 MCP 服务器和 Agent Skill）
- 用过 Scrapy、BeautifulSoup，想找一个更全、更快、更现代的替代品的人

## 它解决什么问题

- 抓取要用的东西散在好几个库里：requests 发请求、Playwright 渲染 JS、BeautifulSoup 解析、Scrapy 爬整站、代理轮换自己写、反爬自己扛。Scrapling 把这些收进一个库，一套 API 走到底。
- 现代网站越来越难抓：JS 渲染、Cloudflare 验证、指纹检测、限流封 IP。它自带隐身浏览器、TLS 指纹伪装、Cloudflare 处理、代理轮换、自动限速，不用自己拼。
- 给 AI 用的抓取一直是个缺口：agent 要的不是 HTML，是干净的数据。Scrapling 给了 MCP 服务器和 Agent Skill，agent 可以直接调用它浏览和抽数据，还能一句话把整站抓成 RAG 可用的 Markdown 语料。

## README 翻译（核心部分）

### 这是什么

Scrapling 是一个 Python 网页抓取框架，把快速 HTTP 请求、隐身浏览器、强力解析和并发爬取带进一个库。

抓静态页、渲染 JavaScript、跟网站交互、从它背后的 API 调用里抽数据。用可复用的会话、代理轮换、自动重试、暂停/恢复和内置数据导出，搭建爬虫。

可以从 Python、终端，或者通过它的 MCP 服务器和 Agent Skill 让你的 AI agent 用它。从抽几个字段到把整个网站收成干净的 Markdown，Scrapling 覆盖完整的抓取工作流。

### 能用它做什么

- **抓取与交互**：快速 HTTP 请求、隐身浏览器、JavaScript 渲染、Cloudflare Turnstile/Interstitial 处理、持久会话、后台 API 捕获。
- **解析与抽取**：CSS、XPath、文本和正则搜索、自适应元素跟踪、相似元素匹配、干净的 Markdown 输出。
- **爬取与导出**：并发爬虫、代理轮换、重试、AutoThrottle、暂停/恢复、流式输出、现成模板、JSON/JSONL/CSV/XML 导出。
- **用 AI 或从终端抓取**：给 AI agent 浏览和抽数据的 MCP 服务器、Agent Skill、CLI 命令、交互式 shell。

从单个页面开始：

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')

quotes = page.css('.quote .text::text').getall()

print(quotes)
```

或者用爬虫放大规模：

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()

print(len(result.items))

result.items.to_json("quotes.json")
```

这会打印 `10`，并把名言和作者存进 `quotes.json`。

### 关键特性

#### 爬虫：一个完整的爬取框架

- **类似 Scrapy 的 Spider API**：用 `start_urls`、异步 `parse` 回调和 `Request`/`Response` 对象定义爬虫。
- **并发爬取**：可配置的并发上限、按域名的限速和下载延迟。
- **多会话支持**：HTTP 请求和隐身无头浏览器用统一接口放在一个爬虫里——按会话 ID 把请求路由到不同会话。
- **暂停与恢复**：用 `crawldir` 保存待处理请求和已见过的 URL，按 Ctrl+C 优雅停止，用同一个目录重启接着跑。
- **流式模式**：通过 `async for item in spider.stream()` 在数据到达时就流式输出，带实时统计——适合界面、管道和长时间爬取。
- **被封请求检测**：自动检测被封的请求并按自定义逻辑重试。
- **AutoThrottle**：不用再猜延迟。爬虫按网站响应速度自己调每个域名的延迟，网站一开始封或限流就加倍（或按 `Retry-After` 等），停了再加速回来。
- **Robots.txt 合规**：可选的 `robots_txt_obey` 标志，遵守 `Disallow`、`Crawl-delay` 和 `Request-rate` 指令，按域名缓存。
- **开发模式**：第一次运行时把响应缓存到磁盘，之后直接回放——改 `parse()` 逻辑不用反复打目标服务器。
- **现成爬虫模板**：用 `CrawlSpider` 做按规则跟链接、`SitemapSpider` 做 sitemap/robots.txt 驱动的爬取、`XMLFeedSpider`/`CSVFeedSpider` 遍历 XML/RSS 和 CSV、`ShopifySpider` 收集公开 Shopify 商店的商品（每个变体一条），跳过样板代码。
- **链接抽取**：独立的 `LinkExtractor`，支持 allow/deny 模式、域名过滤、CSS/XPath 范围、扩展名过滤和规范化——在模板里用或单独用都行。
- **内置导出**：通过钩子、自己的管道或内置的 JSON/JSONL/CSV/XML 导出器导出结果，用 `result.items.to_json()`、`to_jsonl()`、`to_csv()`、`to_xml()`。

#### 高级网站抓取，带会话支持

- **HTTP 请求**：用 `Fetcher` 类发快速、隐身的 HTTP 请求，可以伪装浏览器的 TLS 指纹、请求头，用 HTTP/3。
- **动态加载**：用 `StealthyFetcher` 类做完整浏览器自动化，支持 Playwright 的 Chromium 和 Google Chrome，抓动态网站。
- **反机器人绕过**：`StealthyFetcher` 和指纹伪装带来高级隐身能力，可以轻松绕过各种 Cloudflare Turnstile/Interstitial。
- **会话管理**：`FetcherSession` 和 `StealthySession` 类提供持久会话，跨请求管理 cookie 和状态。
- **代理轮换**：内置 `ProxyRotator`，在所有会话类型上按循环或自定义策略轮换，另有按请求覆盖代理的选项。
- **域名与广告屏蔽**：屏蔽指定域名（及子域名），或在基于浏览器的抓取器里开内置广告屏蔽（约 3,500 个已知广告/追踪域名）。
- **防 DNS 泄漏**：可选的 DNS-over-HTTPS，把 DNS 查询走 Cloudflare 的 DoH，用代理时不泄漏 DNS。
- **远程浏览器**：不用在本地启动浏览器，通过 CDP 用 `cdp_url` 连到已经在跑的浏览器，不管它在同一台机器、另一台主机还是托管浏览器服务上。也可以用 `executable_path` 把任何浏览器抓取器指向自己的 Chromium 构建。
- **后台 API 捕获**：在浏览器会话上开 `record_requests=True`，再用 `session.network.search(limit=None)` 搜它保存的响应。不用重新发请求，就能读跨页面加载的 API 数据和 HTTP 错误。历史有上限，只保存文本响应体。
- **异步支持**：所有抓取器和专用异步会话类都完整支持异步。

#### 解析与数据抽取

- **智能元素跟踪**：网站变了之后，用智能相似度算法重新定位元素。
- **灵活智能选择**：CSS 选择器、XPath 选择器、按过滤器搜索、文本搜索、正则搜索等。
- **找相似元素**：自动定位和已找到元素相似的元素。

#### AI 功能

- **MCP 服务器**：让 AI 聊天机器人和 agent（Claude/Cursor 等）通过 Scrapling 抓取，用 HTTP 请求、浏览器操作、截图、保存的登录状态和后台 API 响应。用我们的隐身浏览器和合适的工具，让合适的 AI 模型在工作时绕过遇到的任何验证码（更不用说我们的 Cloudflare 求解器）。用了很多方法减少发给模型的内容、屏蔽广告、防止提示词注入。包含通过 CDP 的远程浏览器和带认证选项的 HTTP 传输。
- **Agent Skill**：现成的 Agent Skill，教编程 agent 整个库，这样它们用 Scrapling 写的代码跟当前 API 对得上，而不是靠猜。
- **RAG 就绪的 Markdown**：一行代码（`page.markdown()`）把任何页面转成干净、消毒过、LLM 就绪的 Markdown，或用 `ContentSpider` 模板把整个网站爬成 Markdown 语料，全程不用 LLM。

#### 高性能与久经考验的架构

- **极快**：优化过的性能，超过大多数 Python 抓取库。
- **省内存**：优化过的数据结构和懒加载，内存占用最小。
- **JSON 序列化快**：比标准库快 10 倍。
- **久经考验**：不只有 92% 的测试覆盖率和完整的类型提示覆盖，过去一年里每天都有几百名网页抓取者在用。

#### 对开发者/抓取者友好的体验

- **交互式网页抓取 Shell**：可选的内置 IPython shell，带 Scrapling 集成、快捷键和新工具，加速抓取脚本开发，比如把 curl 请求转成 Scrapling 请求、在浏览器里看请求结果。
- **直接从终端用**：可选，不写一行代码就能用 Scrapling 抓一个 URL。
- **丰富的导航 API**：用父级、兄弟、子级导航方法做高级 DOM 遍历。
- **增强的文本处理**：内置正则、清理方法和优化过的字符串操作。
- **自动选择器生成**：为任意元素生成健壮的 CSS/XPath 选择器。
- **熟悉的 API**：类似 Scrapy/BeautifulSoup，用 Scrapy/Parsel 同样的伪元素。
- **Scrapy 无缝集成**：已经在用 Scrapy？给任意回调加 `scrapling_response` 装饰器，就能用 Scrapling 的解析器解析你已经抓到的响应，不用重写。
- **完整的类型覆盖**：完整的类型提示，IDE 支持和代码补全一流。整个代码库每次改动都自动用 **PyRight** 和 **MyPy** 扫描。
- **现成的 Docker 镜像**：每次发版都会自动构建并推送一个包含所有浏览器的 Docker 镜像。

### 上手

#### 基础用法

带会话支持的 HTTP 请求：

```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # 使用最新版 Chrome 的 TLS 指纹
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# 或者一次性的请求
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```

高级隐身模式：

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # 浏览器一直开着，直到你做完
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# 或者一次性的请求风格，请求时开浏览器，做完就关
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```

完整浏览器自动化：

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # 喜欢 XPath 也可以

# 或者一次性的请求风格
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

#### 爬虫

用并发请求、多种会话类型和暂停/恢复搭建完整爬虫：

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')

        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()

print(f"Scraped {len(result.items)} quotes")

result.items.to_json("quotes.json")
```

在一个爬虫里用多种会话类型：

```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # 受保护的页面走隐身会话
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 显式回调
```

这样跑爬虫可以暂停和恢复长时间爬取：

```python
QuotesSpider(crawldir="./crawl_data").start()
```

设了 `crawldir` 后，按 Ctrl+C 会保存待处理请求和已见过的 URL，用同一个 `crawldir` 重启就接着跑。抓到的条目另外保存。

或者用现成模板直接跳过爬取逻辑，比如拉整个 Shopify 商店的目录：

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # 商店里的每个商品，每个变体一条
```

模板读的是公开 collection 端点暴露的商品，每个变体一条。

#### 高级解析与导航

```python
from scrapling.fetchers import Fetcher

# 丰富的元素选择和导航
page = Fetcher.get('https://quotes.toscrape.com/')

# 用多种选择方法取元素
quotes = page.css('.quote')  # CSS 选择器
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup 风格

# 按文本内容找元素
quotes = page.find_by_text('Albert Einstein', first_match=False)

# 高级导航
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # 链式选择器
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# 元素关系和相似度
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```

不想抓网站、只想用解析器也行：

```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```

用法完全一样！

#### 异步会话管理示例

```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # FetcherSession 支持上下文，也能同步/异步两用
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

### CLI 与交互式 Shell

Scrapling 自带强大的命令行界面。

启动交互式网页抓取 shell：

```bash
pip install "scrapling[shell]"

scrapling shell
```

不用写程序，直接把页面抽到文件里。用 `--css-selector` 选内容，或用 `--ai-targeted` 选取并清理 `body` 内容。`.txt` 出文本，`.md` 出 Markdown，`.html` 出 HTML。

```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

注意：还有很多其他功能，这里想保持页面简洁就没展开，包括 MCP 服务器和交互式网页抓取 Shell，完整文档见原文链接。

### 性能基准

Scrapling 不只强大，还非常快。以下基准把 Scrapling 的解析器和最新版的其他流行库对比。

#### 文本抽取速度测试（5000 个嵌套元素）

| 排名 | 库 | 时间（毫秒） | 对比 Scrapling |
| --- | --- | --- | --- |
| 1 | Scrapling | 1.99 | 1.0x |
| 2 | Parsel/Scrapy | 2.06 | 1.035 |
| 3 | Raw Lxml | 2.56 | 1.286 |
| 4 | PyQuery | 23.98 | 约 12x |
| 5 | Selectolax | 197.02 | 约 99x |
| 6 | MechanicalSoup | 1545.15 | 约 776.5x |
| 7 | BS4 with Lxml | 1562.1 | 约 785.0x |
| 8 | BS4 with html5lib | 3412.73 | 约 1714.9x |

#### 元素相似度与文本搜索性能

Scrapling 的自适应元素查找能力明显超过其他方案：

| 库 | 时间（毫秒） | 对比 Scrapling |
| --- | --- | --- |
| Scrapling | 2.3 | 1.0x |
| AutoScraper | 12.58 | 5.47x |

所有基准都是 100 多次运行的平均值，方法见 `benchmarks.py`。

### 安装

Scrapling 需要 Python 3.10 或更高：

```bash
pip install scrapling
```

重要：这个安装只包含解析引擎和它的依赖，不含抓取器或命令行依赖。所以只装这个就从 `scrapling.fetchers` 或 `scrapling.spiders` 导东西，会报 `ModuleNotFoundError`。要用任何抓取器或爬虫，先按下面装抓取器的依赖。

#### 可选依赖

1. 要用下面任何额外功能、抓取器或它们的类，都要先装抓取器依赖和浏览器依赖：

```bash
pip install "scrapling[fetchers]"

    scrapling install# 正常安装
scrapling install  --force  # 强制重装
```

也可以在代码里装，不用跑命令：

```python
from scrapling.cli import install

install([], standalone_mode=False)          # 正常安装
install(["--force"], standalone_mode=False) # 强制重装
```

2. 额外功能：

- 装 MCP 服务器功能：

```bash
pip install "scrapling[ai]"
```

- 装搭建 RAG 系统的依赖：

```bash
pip install "scrapling[rag]"
```

- 装 shell 功能（网页抓取 shell 和 `extract` 命令）：

```bash
pip install "scrapling[shell]"
```

- 全装：

```bash
pip install "scrapling[all]"
```

需要浏览器抓取器时跑 `scrapling install`，纯 HTTP 请求不用装浏览器。

#### Docker

也可以从 DockerHub 拉一个带所有额外功能和浏览器的 Docker 镜像：

```bash
docker pull pyd4vinci/scrapling
```

或从 GitHub registry 下载：

```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

这个镜像由 GitHub Actions 用仓库 main 分支自动构建推送。

### 免责声明

注意：这个库仅供教育和研究用途。使用这个库即表示你同意遵守本地和国际的数据抓取与隐私法律。作者和贡献者不对软件的任何滥用负责。请始终遵守网站的服务条款和 robots.txt 文件。

### 引用

研究用途引用：

```
@misc{scrapling,
  author = {Karim Shoair},
  title = {Scrapling},
  year = {2024},
  url = {https://github.com/D4Vinci/Scrapling},
  note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
}
```

### 许可

本作品按 BSD-3-Clause 许可授权。

### 致谢

本项目包含改编自以下项目的代码：

- Parsel（BSD 许可）——用于 translator 子模块

作者：Karim Shoair

## 中文部署操作指南

### 方式一：只装解析器

```bash
pip install scrapling
```

注意：这只装解析引擎，不含抓取器；要从 `scrapling.fetchers` 或 `scrapling.spiders` 导东西会报 `ModuleNotFoundError`。

### 方式二：抓取器全套（推荐）

```bash
pip install "scrapling[fetchers]"
scrapling install
```

`scrapling install` 会下载浏览器和系统依赖、指纹伪装依赖；纯 HTTP 请求不用这一步。

### 方式三：按需装额外功能

```bash
pip install "scrapling[ai]"     # MCP 服务器，给 AI agent 用
pip install "scrapling[rag]"    # 搭 RAG 系统的依赖
pip install "scrapling[shell]"  # 交互式 shell 和 extract 命令
pip install "scrapling[all]"    # 全装
```

### 方式四：Docker

```bash
docker pull pyd4vinci/scrapling
```

或：

```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```

### 装完先跑一遍

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

终端里不用写代码也行：

```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
```

## 配置说明

- Python 要求 3.10 或更高。
- `Fetcher` 是快速 HTTP 请求（可伪装 Chrome 的 TLS 指纹、HTTP/3）；`StealthyFetcher`/`StealthySession` 是隐身浏览器（Playwright Chromium 或 Google Chrome），带 `solve_cloudflare=True` 处理 Cloudflare。
- 爬虫用 `Spider` 类：`start_urls` + 异步 `parse`，`concurrent_requests` 控并发；设 `crawldir` 可暂停/恢复；现成模板有 CrawlSpider、SitemapSpider、XMLFeedSpider/CSVFeedSpider、ShopifySpider。
- 给 AI agent 用：装 `scrapling[ai]` 起 MCP 服务器，或装 Agent Skill 让编程 agent 按当前 API 写代码；`page.markdown()` 一行出 RAG 可用的干净 Markdown。
- 代理用内置 `ProxyRotator` 轮换；被封的请求自动检测重试；AutoThrottle 按网站响应自己调延迟。

## 注意事项

- README 里有简体中文版链接，但主 README 是英文，本文翻的是英文主 README。
- 免责声明原文：仅供教育和研究用途，遵守本地和国际数据抓取与隐私法律，遵守网站服务条款和 robots.txt。
- 是否实测：按原项目 README 文档整理，未实测。

## 原文链接

- 原项目：https://github.com/D4Vinci/Scrapling
- 原 README：https://github.com/D4Vinci/Scrapling#readme

## 声明

本文为中文翻译，仅供学习交流，不盈利。原项目版权归原作者所有。
