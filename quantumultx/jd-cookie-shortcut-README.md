# 取京东Cookie 快捷指令 — 构建说明

用途：先在 QX 网络活动里把整条京东 Cookie 复制到剪贴板，再运行这个快捷指令，
它自动摘出 `pt_key=...;pt_pin=...;` 写回剪贴板，直接粘到青龙 `JD_COOKIE`。
文件里没有任何真实 Cookie，只有下面两条正则。

## 文件

- `jd-cookie.shortcut` — 未签名版（1396 字节，二进制 plist，开头是 `bpli`，iPhone 不能直接导入）
- `signed/jd-cookie.signed.shortcut` — 已签名版（22362 字节，开头是 `AEA1`，可导入）
- `jd-cookie-plan.json` — ShortcutForge 构建计划（动作、UUID、正则、变量接线都在里面，可复查）

推到 Wzhuaboy/museai 后的地址会是：

```
https://raw.githubusercontent.com/Wzhuaboy/museai/main/quantumultx/jd-cookie.shortcut
https://raw.githubusercontent.com/Wzhuaboy/museai/main/quantumultx/signed/jd-cookie.signed.shortcut
```

## 动作（按顺序，共 6 个）

| 序号 | 动作 | 标识符 | 关键参数 |
|---|---|---|---|
| 1 | 获取剪贴板 | `is.workflow.actions.getclipboard` | 无参数，输出命名为 Clipboard |
| 2 | 匹配文本 pt_key | `is.workflow.actions.text.match` | 正则 `pt_key=[^;]+`，大小写敏感，输入明确指向剪贴板 |
| 3 | 匹配文本 pt_pin | `is.workflow.actions.text.match` | 正则 `pt_pin=[^;]+`，大小写敏感，输入明确指向剪贴板 |
| 4 | 文本（拼接） | `is.workflow.actions.gettext` | 内容 = 匹配结果1 + `;` + 匹配结果2 + `;` |
| 5 | 拷贝到剪贴板 | `is.workflow.actions.setclipboard` | 输入为上一步的文本 |
| 6 | 通知 | `is.workflow.actions.notification` | 固定文字 `已提取，粘贴到青龙 JD_COOKIE`，不含 Cookie 值 |

关键接线：第 2、3 步的输入都用 `WFInput` 明确指回第 1 步的剪贴板。
不这样写的话，第 3 步会拿第 2 步的匹配结果当输入，永远找不到 `pt_pin`。

## 验证结果

- `shortcutforge validate jd-cookie.shortcut`：通过（Valid plist structure）
- `shortcutforge inspect`：6 个动作，顺序和标识符与上表一致
- plistlib 独立复核：两个正则在文件里各只出现 1 次（就是正则本身），通知正文是固定文字，
  拼接文本是 U+FFFC 占位符 + `;` + U+FFFC 占位符 + `;`，两个占位符分别指向 pt_key、pt_pin 的输出
- 签名：`shortcutforge sign --via shortcuty` 成功，`signed/` 文件开头 4 字节是 `AEA1`，
  ShortcutForge 签名时内部已核对输入 SHA-256。注意：`shortcutforge validate/inspect`
  读不了 AEA1 签名容器（会报 Invalid file），这是正常的，签名本身以 AEA1 开头为准。
- 未在真机上导入运行过，最终以亲爱的手机上实测为准。

## 哪些写法是核实过的，哪些不是

- 已核实：`getclipboard` / `setclipboard` / `text.match` 三个标识符在 ShortcutForge
  iOS 26 动作目录里存在；`WFMatchTextPattern`、`WFMatchTextCaseSensitive`
  两个参数键在 ScPL 的 Match Text 源码 JSON 里有；`WFInput` 的变量接线写法
  照抄 ShortcutForge 自带示例 `examples/battery-decision-lab.json`；
  文本拼接的 `WFTextTokenString` 单变量写法照抄 ShortcutForge 编译器本身的编码。
- 未单独核实：双变量拼接（两个 U+FFFC 占位符）是单变量写法的扩展，没有真机验证；
  `setclipboard` 的 `WFLocalOnly=false` / `WFExpirationDate={}` 是社区常见导出写法，
  未单独核实；Match Text 返回的是列表，只含一个匹配项时按单条文本处理，未单独核实。
  如果导入后运行结果为空，先走下面的手动版。

## 导入方法

1. 在 iPhone 上打开已签名文件 `signed/jd-cookie.signed.shortcut`（Safari 下载后点它，或从文件 App 里点它）
2. 如果提示不受信任：设置 > 快捷指令 > 打开“允许不受信任的快捷指令”，再重新点文件导入
3. 导入后在快捷指令里能看到“取京东Cookie”，点运行即可

## 用法

1. QX 网络活动里找到京东请求，把整条 Cookie 复制到剪贴板
2. 运行“取京东Cookie”，等通知“已提取，粘贴到青龙 JD_COOKIE”
3. 去青龙新建或修改环境变量 `JD_COOKIE`，粘贴。不要发到聊天里。

## 手动版（5 步，文件导入失败时用）

在快捷指令 App 里新建，改名“取京东Cookie”，按顺序加：

1. 获取剪贴板
2. 匹配文本：正则填 `pt_key=[^;]+`，输入选“剪贴板”
3. 匹配文本：正则填 `pt_pin=[^;]+`，输入同样选“剪贴板”（不要留成上一步的结果）
4. 文本：依次插入第 2 步的匹配结果、`;`、第 3 步的匹配结果、`;`
5. 拷贝到剪贴板，再加一个通知，内容写 `已提取，粘贴到青龙 JD_COOKIE`

## 构建工具

ShortcutForge（nezumi0627/ShortcutForge，从 GitHub 克隆后 `pip install -e .`，
PyPI 上没有 `shortcutforge` 这个包名）。构建命令：

```
python3 -m shortcutforge build jd-cookie-plan.json -o jd-cookie.shortcut
python3 -m shortcutforge validate jd-cookie.shortcut
python3 -m shortcutforge sign jd-cookie.shortcut
```

签名走 Shortcuty 默认服务，不用 API key，只上传了快捷指令逻辑本身，不含任何 Cookie。
