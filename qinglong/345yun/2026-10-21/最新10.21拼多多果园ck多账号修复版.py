# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cc 脚本库下载！
# 脚本库官方QQ群1群: 429274456
# 脚本库官方QQ群2群: 1077801222
# 脚本库官方QQ群3群: 433030897
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼多多果园 - 自动浇水领水滴

2026-10-21 按最新抓包校准接口（老版有多处已失效）：
  ✗ manor-query/proxy/home/page     → 改 tree/part/get + health/info
  ✗ manor/mission/accept            → 新模型不需要接受任务
  ✗ manor/mission/draw              → 改 mission/complete + complete/gain
  ✗ manor/steal/chance/lack         → 改 friend/home/page 的 rest_chance
  · fun_pl 2 → 7；浇水单次 10 → 30 滴（merge_cost=true）；签到 ui_id 3 → 1

环境变量:
    YYB_GO_URL       - YYB Go 地址，如 http://115.190.216.15:8000
    PDD_OPENID       - YYB Go 账号引用，可填账号 ID、UIN 或 openid；多账号用 & 或换行
    PDD_COOKIE       - (可选) 已有完整 Cookie 字符串，多账号支持 & 或换行
    PDD_WATER_AMOUNT - 单次浇水消耗水滴，默认 30（老版本是 10）
    PDD_FUN_PL       - fun_pl 版本号，默认 7
    PDD_STEAL_RETRY  - 偷水同狗位重试次数，默认 3
    PDD_VERIFY_TOKEN - (可选) 手填 verifyauthtoken，一般不用填，脚本会自己搞：
                       ① 内存里有就用 ② 没有读 pdd_verify_cache.json
                       ③ 还是没有就经 YYB 取 code → /login 第一轮自动取一个
                       （实测 /login 第一轮就算 error_code=54002 也照发这个 39 位 token，
                         拿到后直接能当 verifyauthtoken 用，详见 VERIFY_CACHE 注释）
                       填了就以填的为准，会覆盖上面所有自动来源。
    PDD_ANTI_TTL     - anti-token 缓存秒数，默认 60
    PDD_TOKEN_RELOGIN=1 - 即使已有缓存 token 也强制经 YYB 重取一次
                          （换账号、或怀疑 token 被轮换时用）
    PDD_NO_STEAL=1   - 跳过偷水
    PDD_NO_TASK=1    - 跳过任务
    PDD_NO_WATER_GAIN=1 - 跳过通用领水
依赖:
    pip install requests
    pip install curl_cffi  # 可选
cron: 0 8 * * *
new Env('拼多多果园')
"""
import os, sys, json, time, random, re, subprocess, traceback
from datetime import datetime
from pathlib import Path
import requests as _requests
USE_CFFI = False
try:
    from curl_cffi import requests as _curl_requests
    USE_CFFI = True
except ImportError:
    pass
# ===== 硬编码配置 =====
PDD_MINI_APP_ID = "wx32540bd863b27570"
PDD_XCX_VERSION = "v8.6.21"
PDD_APP_ID = 33
SCRIPT_BUILD = "yyb-go-20261021.2-vtcache"
TOKEN_CACHE = "./pdd_token_cache.json"
COOKIE_CACHE = "./pdd_cookie_cache.json"
VERIFY_CACHE = "./pdd_verify_cache.json"
MANOR_BASE = "https://mobile.yangkeduo.com/proxy/api/api"
LOGIN_BASE = "https://api.pinduoduo.com"
# 2026-10-21 抓包：fun_pl 已从 2 升到 7，全链路都要带
FUN_PL = int(os.environ.get("PDD_FUN_PL", "7"))
# 每次浇水消耗的水滴数：新版默认 30（老版 10），可调
WATER_COST = int(os.environ.get("PDD_WATER_AMOUNT", "30"))
# 偷水狗位重试次数
STEAL_RETRY = int(os.environ.get("PDD_STEAL_RETRY", "3"))
# 是否关掉某个环节（1=跳过）
NO_STEAL = os.environ.get("PDD_NO_STEAL", "0") == "1"
NO_TASK = os.environ.get("PDD_NO_TASK", "0") == "1"
NO_WATER_GAIN = os.environ.get("PDD_NO_WATER_GAIN", "0") == "1"
# ── 风控令牌（2026-10-21 实测定论，之前两版注释都是错的）
# anti-token：每次请求实时生成，有效期几分钟，由 generate_anti_content() 产出。
#             必须用「与本请求头同一个 UA」生成，否则 10018（这是 10018 的头号原因）。
# verifyauthtoken：就是登录链路 /login 返回的 verify_auth_token，39 位
#             （20 位随机 + 16 位 hex），例如 e26QDMowW3RDtWCp2h8OdQ78d064117b1d97cd7
#             —— 跟抓包里请求头那个值完全同源、同长度，不是两个东西。
#             实测：会话级固定值，抓包 16:12 的 token 到 18:02（1.8 小时）照样能用；
#             同一个抓包里 96 次请求复用同一个 token，84 个 anti 各不相同。
#             让它失效的是「PDD 重新登录 / 服务端轮换会话」，不是固定时间到期，
#             所以不存在「每 2 小时必须抓一次」这回事。
#             Code 模式（YYB）第一轮 /login 就会下发它（error_code=54002 也照样给），
#             拿到后落到 VERIFY_CACHE，下次启动直接复用，失效才重新登录。
VERIFY_TOKEN = os.environ.get("PDD_VERIFY_TOKEN", "").strip()
# anti-token 缓存秒数（生成一次要下载 SDK 跑 node，别每次都来）
ANTI_TTL = int(os.environ.get("PDD_ANTI_TTL", "60"))
# ⚠️ 铁律：anti-token 必须用「同一个 UA」生成，且请求头也得是同一个 UA。
# 只要两者不一致，manor 风控接口一律 10018 空列表。实测三组对照：
#   Chrome 生成的 anti + Chrome UA    → 正常，2 个任务
#   Chrome 生成的 anti + 安卓微信 UA  → 10018，0 个任务（串味）
#   安卓微信 UA 自己生成的 anti + 同 UA → 正常，2 个任务
# 所以默认 UA 用真机抓包那台（小米8 / Android 10 / 微信 8.0.76 / 小程序），
# 让 cookie、tubetoken、verifyauthtoken、anti 全在同一环境里，最不容易被判异常。
# 想换环境就设 PDD_UA，anti 会自动跟着换指纹（桌面/移动自动切换）。
ANTI_UA = ("Mozilla/5.0 (Linux; Android 10; MI 8 UD Build/QKQ1.190828.002; wv) "
           "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.173 "
           "Mobile Safari/537.36 XWEB/1420283 MMWEBSDK/20260502 MMWEBID/5337 "
           "MicroMessenger/8.0.76.3141(0x28004C55) WeChat/arm64 Weixin NetType/WIFI "
           "Language/zh_CN ABI/arm64 miniProgram/wx32540bd863b27570")
UA = os.environ.get("PDD_UA", "").strip() or ANTI_UA
# ===== 环境变量 =====
OPENID_RAW = os.environ.get("PDD_OPENID", "").strip()
YYB_GO_URL = os.environ.get("YYB_GO_URL", "").strip().rstrip("/")
COOKIE_STR = os.environ.get("PDD_COOKIE", "").strip()
# ===== 工具函数 =====
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)
def mask(s, h=4, t=4):
    s = str(s)
    if len(s) <= h + t:
        return s[:h] + "***"
    return s[:h] + "***" + s[-t:]
def parse_openids(raw):
    if not raw:
        return []
    result = []
    for line in raw.replace("\r", "\n").split("\n"):
        for part in line.split("&"):
            p = part.strip()
            if p:
                result.append(p)
    return result

def parse_cookies(raw):
    """解析PDD_COOKIE多账号，支持换行 / &分割"""
    if not raw:
        return []
    result = []
    for line in raw.replace("\r", "\n").split("\n"):
        for part in line.split("&"):
            p = part.strip()
            if p:
                result.append(p)
    return result

def cookie_str_to_dict(cookie_str):
    cookies = {}
    for item in cookie_str.split(";"):
        item = item.strip()
        if "=" in item:
            k, v = item.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies
def cookie_dict_to_str(cookies):
    return "; ".join(f"{k}={v}" for k, v in cookies.items())
def extract_uid(cookie_str):
    """从Cookie字符串中提取 pdd_user_id"""
    m = re.search(r'pdd_user_id=(\d+)', cookie_str)
    return m.group(1) if m else ""
# ===== 缓存 =====
def read_cache(path):
    try:
        p = Path(path)
        return json.loads(p.read_text("utf-8")) if p.exists() else {}
    except Exception:
        return {}
def write_cache(path, data):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    except Exception as e:
        log(f"[缓存写入失败] {e}")
def cached_cookie(openid):
    entry = read_cache(COOKIE_CACHE).get(openid, {})
    return entry.get("cookie_str", "")
def save_cookie_cache(openid, cookie_str):
    c = read_cache(COOKIE_CACHE)
    c[openid] = {
        "cookie_str": cookie_str,
        "updatedAt": datetime.now().isoformat()
    }
    write_cache(COOKIE_CACHE, c)
# ===== HTTP 会话 =====
def make_session():
    if USE_CFFI:
        s = _curl_requests.Session(impersonate="chrome")
    else:
        s = _requests.Session()
        s.headers.update({
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        })
    s.headers.update({"User-Agent": UA})
    return s
# ===== Code 登录流程 =====
def get_wx_code(account_ref):
    """通过 YYB Go 获取微信小程序 code。"""
    try:
        r = _requests.post(
            f"{YYB_GO_URL}/wxapp/getCode",
            json={"app_id": PDD_MINI_APP_ID, "ref": account_ref},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if r.status_code != 200:
            body = r.text[:300]
            log(f"[YYB Go] HTTP {r.status_code}: {body}")
            if "session rebuild" in body or "empty code" in body:
                log("[YYB Go] 该微信账号的登录态已被微信踢掉（高频取 code 会触发）")
                log("[YYB Go] 去 YYB 后台重新扫码登录这个账号，再跑脚本")
            return None
        response = r.json()
        if response.get("code") not in (0, "0", None):
            log(
                f"[YYB Go] 获取 code 失败: "
                f"{response.get('msg', json.dumps(response, ensure_ascii=False)[:200])}"
            )
            return None
        data = response.get("data") or {}
        result = data.get("result") or {}
        if isinstance(result, dict):
            code = result.get("code")
        elif isinstance(result, str):
            code = result
        else:
            code = None
        code = code or data.get("code")
        if not code:
            log(
                f"[YYB Go] 未返回小程序 code: "
                f"{json.dumps(response, ensure_ascii=False)[:300]}"
            )
            return None
        return code
    except Exception as e:
        log(f"[YYB Go] 异常: {e}")
        return None
# ===== Anti-Content 生成 (Node.js) =====
# ---- 内嵌 Anti-Content 生成器 (Node.js) ----
_ANTI_TOKEN_JS = r'''
﻿// PDD anti-token 生成器 - Node.js
// 供 Python subprocess 调用: node anti_token.js
const https = require('https');
const util = require('util');
const SDK_URL = 'https://static.pddpic.com/assets/js/risk_control_anti_dac600d707bbff03e560.js';
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36';
async function downloadSDK() {
    return new Promise((resolve, reject) => {
        https.get(SDK_URL, { rejectUnauthorized: false, timeout: 30000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}
async function generateAntiToken() {
    const sdkCode = await downloadSDK();
    // Fake browser environment (minimal)
    const win = {
        webpackChunkmobile_cartoon_activity: [],
        navigator: {
            userAgent: USER_AGENT, platform: 'Win32', language: 'zh-CN',
            languages: ['zh-CN', 'zh'], cookieEnabled: true,
            hardwareConcurrency: 8, maxTouchPoints: 0,
            vendor: 'Google Inc.', appVersion: '5.0',
            appName: 'Netscape', onLine: true,
            plugins: { length: 3 }, mimeTypes: { length: 2 },
            connection: null, getBattery: null, sendBeacon: () => true,
        },
        document: {
            cookie: '', referrer: '', title: 'test', domain: 'mobile.pinduoduo.com',
            readyState: 'complete', visibilityState: 'visible', hidden: false,
            createElement: (tag) => ({ style: {}, setAttribute: () => {}, getAttribute: () => null, addEventListener: () => {}, removeEventListener: () => {}, appendChild: () => {}, removeChild: () => {}, getContext: () => null, tagName: (tag || '').toUpperCase() }),
            getElementById: () => null, querySelector: () => null, querySelectorAll: () => [],
            getElementsByTagName: () => [], addEventListener: () => {}, removeEventListener: () => {},
            createEvent: () => ({ initEvent: () => {} }),
            body: { appendChild: () => {}, removeChild: () => {}, style: {}, scrollTop: 0, scrollLeft: 0, clientWidth: 1920, clientHeight: 1080 },
            head: { appendChild: () => {}, removeChild: () => {} },
            documentElement: { scrollTop: 0, scrollLeft: 0, clientWidth: 1920, clientHeight: 1080, style: {} },
        },
        location: { href: 'https://mobile.pinduoduo.com/garden_index_lz_0.html', hostname: 'mobile.pinduoduo.com', protocol: 'https:', pathname: '/garden_index_lz_0.html', search: '', hash: '', host: 'mobile.pinduoduo.com', origin: 'https://mobile.pinduoduo.com' },
        screen: { width: 1920, height: 1080, colorDepth: 24, availWidth: 1920, availHeight: 1040 },
        performance: { now: () => Date.now() - 1000, timing: { navigationStart: Date.now() - 3000 }, getEntriesByType: () => [], mark: () => {}, measure: () => {} },
        history: { length: 3, state: null, pushState: () => {}, replaceState: () => {} },
        innerWidth: 1920, innerHeight: 1080, outerWidth: 1920, outerHeight: 1080,
        devicePixelRatio: 1, pageXOffset: 0, pageYOffset: 0, scrollX: 0, scrollY: 0,
        localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {}, clear: () => {}, length: 0, key: () => null },
        sessionStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {}, clear: () => {}, length: 0, key: () => null },
        crypto: { getRandomValues: (arr) => { for (let i = 0; i < arr.length; i++) arr[i] = Math.floor(Math.random() * 256); return arr; }, subtle: null },
        addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => true,
        setTimeout, clearTimeout, setInterval, clearInterval,
        Promise, JSON, Math, Date, Array, Object, String, Number, Boolean, RegExp, Error,
        Uint8Array, Uint16Array, Int32Array, ArrayBuffer, DataView, Function,
        Map, Set, WeakMap, WeakSet, Symbol,
        Element: function Element() {}, HTMLElement: function HTMLElement() {}, Node: function Node() {},
        Event: function Event() {}, EventTarget: function EventTarget() {}, HTMLCanvasElement: function HTMLCanvasElement() {},
        TextEncoder: util.TextEncoder, TextDecoder: util.TextDecoder,
        encodeURIComponent, decodeURIComponent, encodeURI, decodeURI,
        parseInt, parseFloat, isNaN, isFinite, console,
        MutationObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
        IntersectionObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
        URL: typeof URL !== 'undefined' ? URL : function (u) { this.href = u; },
        Blob: typeof Blob !== 'undefined' ? Blob : function () {},
        FormData: function () { this.append = () => {}; },
    };
    win.self = win;
    win.window = win;
    win.top = win;
    win.parent = win;
    global.self = win;
    global.window = win;
    global.document = win.document;
    global.location = win.location;
    global.screen = win.screen;
    global.performance = win.performance;
    global.localStorage = win.localStorage;
    global.sessionStorage = win.sessionStorage;
    global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve({}), text: () => Promise.resolve('') });
    global.XMLHttpRequest = function () { this.open = () => {}; this.send = () => {}; };
    global.MutationObserver = win.MutationObserver;
    global.TextEncoder = win.TextEncoder;
    global.TextDecoder = win.TextDecoder;
    global.Element = win.Element;
    global.HTMLElement = win.HTMLElement;
    global.Node = win.Node;
    global.Event = win.Event;
    global.EventTarget = win.EventTarget;
    global.HTMLCanvasElement = win.HTMLCanvasElement;
    // Execute SDK
    eval(sdkCode);
    const chunks = win.webpackChunkmobile_cartoon_activity;
    if (!chunks || !chunks.length) {
        throw new Error('SDK chunks not loaded');
    }
    const [, modules] = chunks[0];
    const cache = {};
    function req(id) {
        if (cache[id]) return cache[id].exports;
        const m = { i: id, l: false, exports: {} };
        cache[id] = m;
        if (modules[id]) { modules[id].call(m.exports, m, m.exports, req); m.l = true; }
        return m.exports;
    }
    req.r = (e) => { Object.defineProperty(e, '__esModule', { value: true }); };
    req.d = (e, n, g) => { if (!Object.prototype.hasOwnProperty.call(e, n)) Object.defineProperty(e, n, { enumerable: true, get: g }); };
    req.o = (o, p) => Object.prototype.hasOwnProperty.call(o, p);
    req.n = (m) => { const g = m && m.__esModule ? () => m.default : () => m; req.d(g, 'a', g); return g; };
    req.p = '';
    const sdk = req(96636);
    const SDKClass = sdk.default;
    const instance = new SDKClass({ serverTime: Date.now(), _2827c887a48a351a: false });
    const token = await instance.messagePackSync({
        touchEventData: true, clickEventData: true, focusblurEventData: true,
        changeEventData: true, locationInfo: true, referrer: true,
        browserSize: true, browserInfo: true, token: true, fingerprint: true
    });
    console.log(token);
}
generateAntiToken().catch(e => { console.error(e.message); process.exit(1); });
'''
def _is_mobile_ua(ua):
    """粗判 UA 是移动端（安卓/iPhone）。用来决定 anti 生成的指纹形态"""
    u = (ua or "").lower()
    return ("android" in u) or ("iphone" in u) or ("ipad" in u) or ("mobile" in u)


def generate_anti_content():
    """调用 Node.js 生成 PDD anti_content token (JS 代码内嵌，无需外部文件)

    UA 与指纹必须成套：桌面 UA 用 Win32/1920x1080，移动 UA 用 armv8l/393x851。
    混搭（桌面 anti 配安卓 UA）服务端直接 10018。
    """
    import tempfile
    try:
        # 写入临时 JS 文件
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False, encoding="utf-8"
        )
        # 把 JS 里的 UA 同步成当前请求 UA，避免 anti 与请求头不一致被风控
        js = _ANTI_TOKEN_JS
        _old_ua = ("const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36';")
        if _old_ua in js:
            js = js.replace(_old_ua, "const USER_AGENT = %r;" % UA)
        if _is_mobile_ua(UA):
            js = (js
                  .replace("platform: 'Win32'", "platform: 'Linux armv8l'")
                  .replace("maxTouchPoints: 0", "maxTouchPoints: 5")
                  .replace("vendor: 'Google Inc.'", "vendor: ''")
                  .replace("screen: { width: 1920, height: 1080, colorDepth: 24, "
                           "availWidth: 1920, availHeight: 1040 }",
                           "screen: { width: 393, height: 851, colorDepth: 24, "
                           "availWidth: 393, availHeight: 851 }")
                  .replace("innerWidth: 1920, innerHeight: 1080, "
                           "outerWidth: 1920, outerHeight: 1080",
                           "innerWidth: 393, innerHeight: 851, "
                           "outerWidth: 393, outerHeight: 851")
                  .replace("clientWidth: 1920, clientHeight: 1080",
                           "clientWidth: 393, clientHeight: 851")
                  .replace("devicePixelRatio: 1", "devicePixelRatio: 2.75"))
        tmp.write(js)
        tmp.close()
        log("  [AntiToken] 正在生成...")
        result = subprocess.run(
            ["node", tmp.name],
            capture_output=True, text=True, timeout=90
        )
        os.unlink(tmp.name)  # 立即删除临时文件
        if result.returncode == 0:
            token = result.stdout.strip()
            if token and len(token) > 50:
                log(f"  [AntiToken] 生成成功: {token[:40]}...")
                return token
            else:
                log(f"  [AntiToken] 输出异常: {result.stdout[:100]}")
                return None
        else:
            log(f"  [AntiToken] Node.js 错误: {result.stderr[:200]}")
            return None
    except FileNotFoundError:
        log("[AntiToken] Node.js 未安装，将尝试无 anti_content 登录")
        return None
    except subprocess.TimeoutExpired:
        log("[AntiToken] 生成超时")
        return None
    except Exception as e:
        log(f"[AntiToken] 异常: {e}")
        return None


def fetch_verify_token_via_yyb(openid, uid_hint=""):
    """只用 YYB 取 code + PDD /login 第一轮，捞到 verify_auth_token 就停

    2026-10-21 实测定论（跟前两版注释说的不一样，那两版是错的）：
      - /login 第一轮返回 error_code=54002（要二次验证）时，响应里
        照样带 39 位的 verify_auth_token
      - 这个值就是 manor 接口要的 verifyauthtoken —— 抓包请求头里那个
        也是 39 位同格式（20 位随机 + 16 位 hex），同一个东西
      - 用真实 cookie 配这个新 token 打 mission/list：HTTP 200 正常返回
      - 后面的 /api/sigerus/verify/login 在 YYB 环境恒 43042，但根本用不上
    所以「token 只能抓包」是错的，这条路能全自动续。
    """
    if not YYB_GO_URL:
        log("  [风控] 没配 YYB_GO_URL，无法自动取 token")
        return "", ""
    code = get_wx_code(openid)
    if not code:
        log("  [风控] YYB 取 code 失败（微信会话可能被打崩，去后台重扫码）")
        return "", ""
    s = make_session()
    try:
        server_time = s.get(f"{LOGIN_BASE}/api/server/_stm", timeout=10).json() \
                       .get("server_time", int(time.time() * 1000))
    except Exception:
        server_time = int(time.time() * 1000)
    rand_str = ''.join(random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=15))
    anti_content = generate_anti_content()
    body = {
        "code": code, "has_auth": False, "app_id": PDD_APP_ID,
        "support_enhance_type": 3, "xcx_version": PDD_XCX_VERSION,
    }
    if anti_content:
        body["anti_content"] = anti_content
    s.headers.update({
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": f"https://servicewechat.com/{PDD_MINI_APP_ID}/1840/page-frame.html",
        "x-xcx-queries": f"mini_program_name=pdd;mp_theme_version={PDD_XCX_VERSION}",
        "rfp": "LqTtkNj4yziKrApKfKKwmWgc2NXA1yXo",
    })
    if anti_content:
        s.headers["anti-content"] = anti_content
    try:
        r = s.post(f"{LOGIN_BASE}/login",
                   params={"xcx": "20161201", "xcx_version": PDD_XCX_VERSION,
                           "xcx_hash": f"{server_time}{rand_str}"},
                   json=body, timeout=20)
        result = r.json() if r.text else {}
    except Exception as e:
        log(f"  [风控] /login 取 token 异常: {e}")
        return "", ""
    tok = result.get("verify_auth_token", "") or pick_verify_token(result)
    if not tok:
        log(f"  [风控] /login 没给 token (error_code={result.get('error_code')})")
        return "", ""
    log(f"  [风控] YYB 链路取到 verifyauthtoken({mask(tok)}, 长度 {len(tok)}, "
        f"login error_code={result.get('error_code')})")
    set_verify_token(tok, uid_hint, "YYB:/login第一轮")
    return tok, uid_hint


def pdd_code_login(openid):
    """
    拼多多 code 登录流程:
    1. wx.login() 获取 code (通过 wx_server)
    2. POST /login 获取 verify_auth_token
    3. POST /api/sigerus/verify/login 获取 uid/uin/access_token
    4. 组装完整 Cookie
    """
    log(f"  --- Code登录 openId={mask(openid)} ---")
    # Step 1: 获取微信 code
    code = get_wx_code(openid)
    if not code:
        return None
    log(f"  [1/4] 获取code: {mask(code, 6, 6)}")
    s = make_session()
    # 获取 server_time
    stm_url = f"{LOGIN_BASE}/api/server/_stm"
    try:
        stm_resp = s.get(stm_url, timeout=10)
        server_time = stm_resp.json().get("server_time", int(time.time() * 1000))
    except Exception:
        server_time = int(time.time() * 1000)
    rand_str = ''.join(random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=15
    ))
    # Step 2: 用 code 换取 verify_auth_token
    login_url = f"{LOGIN_BASE}/login"
    login_params = {
        "xcx": "20161201",
        "xcx_version": PDD_XCX_VERSION,
        "xcx_hash": f"{server_time}{rand_str}"
    }
    # 生成 anti_content
    anti_content = generate_anti_content()
    login_body = {
        "code": code,
        "has_auth": False,
        "app_id": PDD_APP_ID,
        "support_enhance_type": 3,
        "xcx_version": PDD_XCX_VERSION
    }
    if anti_content:
        login_body["anti_content"] = anti_content
    s.headers.update({
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": f"https://servicewechat.com/{PDD_MINI_APP_ID}/1840/page-frame.html",
        "x-xcx-queries": f"mini_program_name=pdd;mp_theme_version={PDD_XCX_VERSION}",
        "rfp": "LqTtkNj4yziKrApKfKKwmWgc2NXA1yXo",
    })
    if anti_content:
        s.headers["anti-content"] = anti_content
    try:
        r = s.post(login_url, params=login_params, json=login_body, timeout=15)
        result = r.json()
    except Exception as e:
        log(f"  [2/6] /login 请求失败: {e}")
        return None
    error_code = result.get("error_code", 0)
    verify_auth_token = result.get("verify_auth_token", "")
    # 第一轮就给 token 的话先抓在手里：后面 verify/login 43042 也不怕，
    # 这个 token 本身就能当 verifyauthtoken 用（39 位，跟抓包同格式）
    if verify_auth_token:
        set_verify_token(verify_auth_token, "", "code登录:/login第一轮")
    if not verify_auth_token:
        log(f"  [2/6] /login 未返回verify_auth_token")
        log(f"       error_code={error_code}, msg={result.get('error_msg', '')}")
        log(f"       完整响应: {json.dumps(result, ensure_ascii=False)[:500]}")
        # 尝试直接提取 uid/access_token (error_code=0 可能表示直接成功)
        direct_uid = result.get("uid") or result.get("user_id") or result.get("data", {}).get("uid")
        direct_token = result.get("access_token") or result.get("data", {}).get("access_token")
        if direct_uid and direct_token:
            uid = direct_uid
            uin = result.get("uin", "") or result.get("data", {}).get("uin", "")
            access_token = direct_token
            acid = result.get("acid", "") or result.get("data", {}).get("acid", "")
            log(f"  [2/4] 直接获取到登录数据! uid={uid}")
            set_verify_token(pick_verify_token(result), uid, "code登录:/login直登")
            # 跳转到 cookie 组装
            pdda = access_token
            response_cookies = {}
            for cookie in s.cookies:
                response_cookies[cookie.name] = cookie.value
            cookie_parts = [f"PDDAccessToken={pdda}", f"pdd_user_id={uid}",
                            f"pdd_user_uin={uin}"]
            if acid:
                cookie_parts.append(f"acid={acid}")
            api_uid = response_cookies.get("api_uid", "")
            if api_uid:
                cookie_parts.append(f"api_uid={api_uid}")
            for k, v in response_cookies.items():
                if k not in ["api_uid"]:
                    cookie_parts.append(f"{k}={v}")
            cookie_str = "; ".join(cookie_parts)
            log(f"  [5/6] Cookie组装完成")
            log(f"  [6/6] 访问果园页面收集额外Cookie...")
            cookies_for_page = cookie_str_to_dict(cookie_str)
            garden_url = f"https://mobile.yangkeduo.com/garden_index_lz_0.html?_pdd_fs=1&_pdd_tc=676666&_pdd_sbs=1&fun_id=wechat_app_home"
            try:
                page_s = make_session()
                page_s.headers.update({
                    "User-Agent": UA,
                    "Referer": "https://servicewechat.com/wx32540bd863b27570/1840/page-frame.html",
                })
                page_r = page_s.get(garden_url, cookies=cookies_for_page, timeout=15, allow_redirects=True)
                # Collect cookies from the page response
                for pc in page_s.cookies:
                    try:
                        cookies_for_page[pc.name] = pc.value
                    except AttributeError:
                        if isinstance(pc, str) and "=" in pc:
                            k, v = pc.split("=", 1)
                            cookies_for_page[k.strip()] = v.strip()
                cookie_str = cookie_dict_to_str(cookies_for_page)
                log(f"  [6/6] Cookie已更新 (共{len(cookies_for_page)}项)")
            except Exception as e:
                log(f"  [6/6] 页面访问异常(可忽略): {e}")
            return cookie_str, str(uid), uin
        return None
    log(f"  [2/6] 获取verify_auth_token: {mask(verify_auth_token)}")
    # Step 3: 第二轮 /login —— 用第一轮的 token 作为 header，获取新的 verify_auth_token
    log(f"  [3/6] 第二轮 /login ...")
    code2 = get_wx_code(openid)
    if not code2:
        log(f"  [3/6] 获取第二个code失败")
        return None
    log(f"        code2={mask(code2, 6, 6)}")
    anti_login2 = generate_anti_content()
    rand_login2 = ''.join(random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=15
    ))
    login2_params = {
        "xcx": "20161201",
        "xcx_version": PDD_XCX_VERSION,
        "xcx_hash": f"{server_time}{rand_login2}"
    }
    login2_body = {
        "code": code2,
        "has_auth": False,
        "app_id": PDD_APP_ID,
        "support_enhance_type": 3,
        "xcx_version": PDD_XCX_VERSION
    }
    if anti_login2:
        login2_body["anti_content"] = anti_login2
    s2_headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": f"https://servicewechat.com/{PDD_MINI_APP_ID}/1840/page-frame.html",
        "x-xcx-queries": f"mini_program_name=pdd;mp_theme_version={PDD_XCX_VERSION}",
        "rfp": "LqTtkNj4yziKrApKfKKwmWgc2NXA1yXo",
        "verifyauthtoken": verify_auth_token,
    }
    if anti_login2:
        s2_headers["anti-content"] = anti_login2
    # 后续验证必须沿用第一轮 /login 的会话，保留 api_uid 等风控 Cookie。
    s2 = s
    s2.headers.update(s2_headers)
    try:
        r2 = s2.post(login_url, params=login2_params, json=login2_body, timeout=15)
        result2 = r2.json()
    except Exception as e:
        log(f"  [3/6] 第二轮 /login 请求失败: {e}")
        return None
    error_code2 = result2.get("error_code", 0)
    verify_auth_token2 = result2.get("verify_auth_token", "")
    if not verify_auth_token2:
        # error_code=0 可能表示直接登录成功，检查是否返回了 uid/access_token
        direct_uid2 = result2.get("uid") or result2.get("data", {}).get("uid")
        direct_token2 = result2.get("access_token") or result2.get("data", {}).get("access_token")
        if direct_uid2 and direct_token2:
            log(f"  [3/6] 第二轮直接登录成功! uid={direct_uid2}")
            set_verify_token(pick_verify_token(result2), direct_uid2, "code登录:第二轮直登")
            uid = direct_uid2
            uin = result2.get("uin", "") or result2.get("data", {}).get("uin", "")
            access_token = direct_token2
            acid = result2.get("acid", "") or result2.get("data", {}).get("acid", "")
            # 组装Cookie后直接返回
            pdda = access_token
            response_cookies = {}
            try:
                for cookie in s2.cookies:
                    response_cookies[cookie.name] = cookie.value
            except AttributeError:
                for cookie in s2.cookies:
                    if hasattr(cookie, 'name'):
                        response_cookies[cookie.name] = cookie.value
                    elif isinstance(cookie, str) and '=' in cookie:
                        k, v = cookie.split('=', 1)
                        response_cookies[k.strip()] = v.strip()
            cookie_parts = [f"PDDAccessToken={pdda}", f"pdd_user_id={uid}",
                            f"pdd_user_uin={uin}"]
            if acid:
                cookie_parts.append(f"acid={acid}")
            api_uid = response_cookies.get("api_uid", "")
            if api_uid:
                cookie_parts.append(f"api_uid={api_uid}")
            for k, v in response_cookies.items():
                if k not in ["api_uid"]:
                    cookie_parts.append(f"{k}={v}")
            cookie_str = "; ".join(cookie_parts)
            log(f"  [5/6] Cookie组装完成")
            log(f"  [6/6] 访问果园页面收集额外Cookie...")
            cookies_for_page = cookie_str_to_dict(cookie_str)
            garden_url = f"https://mobile.yangkeduo.com/garden_index_lz_0.html?_pdd_fs=1&_pdd_tc=676666&_pdd_sbs=1&fun_id=wechat_app_home"
            try:
                page_s = make_session()
                page_s.headers.update({
                    "User-Agent": UA,
                    "Referer": "https://servicewechat.com/wx32540bd863b27570/1840/page-frame.html",
                })
                page_r = page_s.get(garden_url, cookies=cookies_for_page, timeout=15, allow_redirects=True)
                # Collect cookies from the page response
                for pc in page_s.cookies:
                    try:
                        cookies_for_page[pc.name] = pc.value
                    except AttributeError:
                        if isinstance(pc, str) and "=" in pc:
                            k, v = pc.split("=", 1)
                            cookies_for_page[k.strip()] = v.strip()
                cookie_str = cookie_dict_to_str(cookies_for_page)
                log(f"  [6/6] Cookie已更新 (共{len(cookies_for_page)}项)")
            except Exception as e:
                log(f"  [6/6] 页面访问异常(可忽略): {e}")
            return cookie_str, str(uid), uin
        log(f"  [3/6] 第二轮 /login 未返回verify_auth_token 且无直接登录数据")
        log(f"       error_code={error_code2}, msg={result2.get('error_msg', '')}")
        log(f"       完整响应: {json.dumps(result2, ensure_ascii=False)[:300]}")
        return None
    verify_auth_token = verify_auth_token2
    log(f"  [3/6] 第二轮token: {mask(verify_auth_token)}")
    # 这个值就是 manor 接口要的 verifyauthtoken（同一条链路上服务端认它）
    set_verify_token(verify_auth_token, "", "code登录:/login")
    # Step 4: 用第二轮 verify_auth_token 换取正式 token
    rand_str2 = ''.join(random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=15
    ))
    verify_url = f"{LOGIN_BASE}/api/sigerus/verify/login"
    verify_params = {
        "xcx": "20161201",
        "xcx_version": PDD_XCX_VERSION,
        "xcx_hash": f"{server_time}{rand_str2}"
    }
    # 为 verify/login 重新生成 anti_content
    anti_content2 = generate_anti_content()
    verify_body = {
        "has_auth": False,
        "support_enhance_type": 3,
        "verify_auth_token": verify_auth_token,
        "xcx_version": PDD_XCX_VERSION
    }
    if anti_content2:
        verify_body["anti_content"] = anti_content2
    s.headers["verifyauthtoken"] = verify_auth_token
    if anti_content2:
        s.headers["anti-content"] = anti_content2
    try:
        r = s.post(verify_url, params=verify_params, json=verify_body, timeout=15)
        result = r.json()
    except Exception as e:
        log(f"  [4/6] /verify/login 请求失败: {e}")
        return None
    uid = result.get("uid", 0)
    uin = result.get("uin", "")
    access_token = result.get("access_token", "")
    acid = result.get("acid", "")
    if not uid or not access_token:
        log(f"  [4/6] 登录失败: {json.dumps(result, ensure_ascii=False)[:300]}")
        return None
    # 登录成功：把 token 绑定到 uid，并优先用 verify/login 下发的新 token
    set_verify_token(result.get("verify_auth_token") or verify_auth_token,
                     uid, "code登录:verify/login")
    log(f"  [4/6] 登录成功! uid={uid}, uin={mask(uin)}")
    # Step 4: 组装完整 Cookie
    pdda = access_token
    # 收集响应 cookies
    response_cookies = {}
    try:
        for cookie in s.cookies:
            response_cookies[cookie.name] = cookie.value
    except AttributeError:
        for cookie in s.cookies:
            if hasattr(cookie, 'name'):
                response_cookies[cookie.name] = cookie.value
            elif isinstance(cookie, str) and '=' in cookie:
                k, v = cookie.split('=', 1)
                response_cookies[k.strip()] = v.strip()
    cookie_parts = []
    cookie_parts.append(f"PDDAccessToken={pdda}")
    cookie_parts.append(f"pdd_user_id={uid}")
    cookie_parts.append(f"pdd_user_uin={uin}")
    if acid:
        cookie_parts.append(f"acid={acid}")
    # API_UID from response
    api_uid = response_cookies.get("api_uid", "")
    if api_uid:
        cookie_parts.append(f"api_uid={api_uid}")
    # 补充其他 response cookies
    for k, v in response_cookies.items():
        if k not in ["api_uid"]:
            cookie_parts.append(f"{k}={v}")
    cookie_str = "; ".join(cookie_parts)
    log(f"  [5/6] Cookie组装完成")
    return cookie_str, str(uid), uin
# ===== 果园任务 API（2026-10-21 抓包校准）=====
# ┌─ 已下线（老脚本还在用就会一直失败）──────────────────────────────┐
# │ manor-query/proxy/home/page      → 改 manor-query/tree/part/get + health/info │
# │ manor/mission/accept             → 无替代，新模型任务无需接受         │
# │ manor/mission/draw               → 改 manor/mission/complete(+/gain) │
# │ manor/steal/chance/lack          → 改 friend/home/page 的 rest_chance │
# └──────────────────────────────────────────────────────────────┘
# 参数变化：fun_pl 2 → 7；浇水单次 10 → 30 滴且 merge_cost=true；
#           偷水 body 去掉 steal_type / tubetoken；签到 ui_id 3 → 1

# 任务类型白名单（老列表里的 38500-38900 已被服务端废弃）
MISSION_TYPES = [
    38160, 38242, 38090, 38451, 37859,
    38594, 38595, 38624, 38622, 38645, 38639, 38640,
]
MISSION_ACT_IDS = [201036, 201655]

# anti-token 缓存 / 最新 tubetoken（manor_post 会自动回填）
_ANTI_CACHE = {"token": "", "ts": 0.0, "ua": ""}
_TUBE = {"token": ""}

# 登录时拿到的 verify_auth_token（= manor 接口要的 verifyauthtoken）
# 结构：{"token": str, "uid": str, "ts": float, "src": str, "pool": [...],
#        "first_ts": float, "ok_ts": float}
_RT_VERIFY = {"token": "", "uid": "", "ts": 0.0, "src": "", "pool": [],
              "first_ts": 0.0, "ok_ts": 0.0}
VT_SRC_LOG = {"shown": ""}
_FORCE_VT = {"token": ""}


def _vt_cache_load():
    d = read_cache(VERIFY_CACHE)
    return d if isinstance(d, dict) else {}


def _vt_cache_save(uid, token, src, first_ts=None):
    """把 token 落到磁盘：一次登录拿到，后面所有进程直接复用

    实测 verifyauthtoken 是会话级的，不按固定时间过期（抓包 16:12 的
    token 到 18:02 仍能用）。所以没必要每次跑都去 YYB 取 code —— 高频
    getCode 会把微信会话打崩。落盘后只有遇到 10018 才重新取。
    """
    if not token:
        return
    try:
        c = _vt_cache_load()
        key = str(uid or "default")
        old = c.get(key) or {}
        c[key] = {
            "token": token,
            "uid": str(uid or ""),
            "src": src,
            "firstAt": old.get("firstAt") or datetime.now().isoformat(),
            "lastWriteAt": datetime.now().isoformat(),
            "lastOkAt": old.get("lastOkAt", ""),
        }
        write_cache(VERIFY_CACHE, c)
    except Exception:
        pass


def _vt_from_disk(pdduid=""):
    """从磁盘缓存取 token。多账号按 uid 精确匹配，uid 不明时退到 default"""
    c = _vt_cache_load()
    key = str(pdduid or "")
    if key and isinstance(c.get(key), dict):
        return c[key].get("token", ""), c[key]
    if not key and isinstance(c.get("default"), dict):
        return c["default"].get("token", ""), c["default"]
    return "", {}


def mark_verify_ok(token=""):
    """接口通了 → 记一笔成功时间，日志里能看出 token 用了多久"""
    tok = token or _RT_VERIFY.get("token", "")
    if not tok:
        return
    _RT_VERIFY["ok_ts"] = time.time()
    try:
        c = _vt_cache_load()
        for k, v in c.items():
            if isinstance(v, dict) and v.get("token") == tok:
                v["lastOkAt"] = datetime.now().isoformat()
                write_cache(VERIFY_CACHE, c)
                break
    except Exception:
        pass


def harvest_verify_token(data, headers=None):
    """从任意响应里捞新下发的 verify 令牌（有就换掉，没有就啥也不干）

    2026-10-21 抓包统计：1442 条请求的响应体里没有任何接口下发
    verifyauthtoken（只在静态 JS 里出现过字符串）。所以这里基本不会
    命中，但留着 —— 一旦 PDD 哪天改成响应下发，就能自动续期。
    """
    if not isinstance(data, dict):
        return ""
    tok = pick_verify_token(data)
    if not tok:
        return ""
    cur = _RT_VERIFY.get("token", "")
    if tok == cur:
        return ""
    # 长度对不上就不认（正牌是 39 位，防止群里别字段误命中）
    if not (30 <= len(tok) <= 60):
        return ""
    uid = _RT_VERIFY.get("uid", "")
    _RT_VERIFY.update({"token": tok, "ts": time.time(), "src": "响应下发"})
    _vt_cache_save(uid, tok, "响应下发")
    log(f"  [风控] 响应里下发新 verifyauthtoken({mask(tok)})，已自动切换")
    return tok


def set_verify_token(token, uid="", src="login"):
    """记录登录链路里拿到的 verify_auth_token，供 manor 风控接口使用

    同时进候选池：/login 第一轮、第二轮、verify/login 可能各下发一个，
    首选打不通就换下一个试（多账号/多跳登录时很常见）。
    并且落盘缓存 —— 同账号下次启动不用再登录。
    """
    token = (token or "").strip()
    if not token:
        return
    now = time.time()
    first = _RT_VERIFY.get("first_ts") or now
    _RT_VERIFY.update({"token": token, "uid": str(uid or ""), "ts": now,
                       "src": src, "first_ts": first})
    pool = _RT_VERIFY.setdefault("pool", [])
    if all(it.get("token") != token for it in pool):
        pool.append({"token": token, "uid": str(uid or ""), "src": src})
        del pool[:-5]
    _vt_cache_save(uid, token, src)
    log(f"  [风控] 已从{src}拿到 verifyauthtoken({mask(token)}, 长度 {len(token)})")


def pick_verify_token(resp):
    """从登录类响应里捞 verify_auth_token（字段名换过几种写法，都试一遍）"""
    if not isinstance(resp, dict):
        return ""
    data = resp.get("data") if isinstance(resp.get("data"), dict) else {}
    for key in ("verify_auth_token", "verifyAuthToken", "verify_auth", "auth_token"):
        for src in (resp, data):
            v = src.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""


def get_verify_token(pdduid="", refresh=None):
    """取 verifyauthtoken。

    优先级：
      1. 强制指定（任务接口 10018 后逐个候选重试时用）
      2. 环境变量 PDD_VERIFY_TOKEN（手填/CI 注入，最优先，覆盖一切）
      3. 本次进程登录链路自动拿到的（code → /login → verify_auth_token）
      4. 磁盘缓存 pdd_verify_cache.json（上一个进程登录时存下来的）
    同一账号 uid 不匹配时，登录 token 不作数（多账号串号会 10018）。
    """
    if _FORCE_VT["token"]:
        return _FORCE_VT["token"]
    if VERIFY_TOKEN:
        return VERIFY_TOKEN
    tok = _RT_VERIFY["token"]
    if tok:
        owner = _RT_VERIFY["uid"]
        if owner and pdduid and str(pdduid) != owner:
            return ""
        return tok
    # 内存没有 → 看磁盘（换个进程跑也不用重新登录）
    dtok, meta = _vt_from_disk(pdduid)
    if dtok:
        owner = str(meta.get("uid") or "")
        if not (owner and pdduid and str(pdduid) != owner):
            _RT_VERIFY.update({
                "token": dtok, "uid": owner, "ts": time.time(),
                "src": "磁盘缓存", "first_ts": time.time(),
                "pool": [{"token": dtok, "uid": owner, "src": "磁盘缓存"}],
            })
            if VT_SRC_LOG.get("disk") != dtok:
                VT_SRC_LOG["disk"] = dtok
                age = ""
                fa = meta.get("firstAt", "")
                if fa:
                    try:
                        age = f"，首次获取 {fa[:16].replace('T', ' ')}"
                    except Exception:
                        pass
                log(f"  [风控] 复用磁盘缓存的 verifyauthtoken({mask(dtok)}{age})")
            return dtok
    return ""


def iter_verify_tokens(pdduid=""):
    """按优先级产出 (token, 来源)，用于 10018 后自动换 token 重试"""
    seen = set()
    first = get_verify_token(pdduid)
    if first:
        seen.add(first)
        yield first, ("env" if VERIFY_TOKEN else _RT_VERIFY.get("src", "login"))
    for it in reversed(_RT_VERIFY.get("pool") or []):
        tok = it.get("token") or ""
        if not tok or tok in seen:
            continue
        owner = str(it.get("uid") or "")
        if owner and pdduid and str(pdduid) != owner:
            continue
        seen.add(tok)
        yield tok, it.get("src", "login")


def _tube(tubetoken=""):
    """tubetoken 兜底：优先用传进来的，其次用上次响应里回填的"""
    return tubetoken or _TUBE["token"] or ""


def get_anti_token(force=False):
    """取 anti-token（带缓存）。每次实时生成太慢，服务端只认几分钟内的。

    缓存按 UA 隔离：换 UA 必须重生成，否则 anti 指纹和请求头对不上 → 10018。
    """
    now = time.time()
    if (not force and _ANTI_CACHE["token"] and _ANTI_CACHE["ua"] == UA
            and now - _ANTI_CACHE["ts"] < ANTI_TTL):
        return _ANTI_CACHE["token"]
    tok = generate_anti_content()
    if tok:
        _ANTI_CACHE["token"] = tok
        _ANTI_CACHE["ts"] = now
        _ANTI_CACHE["ua"] = UA
        return tok
    return _ANTI_CACHE["token"]


GARDEN_REFERER_TPL = (
    "https://mobile.yangkeduo.com/garden_index_lz_0.html"
    "?_pdd_fs=1&_pdd_tc=676666&_pdd_sbs=1&fun_id=wechat_app_home"
    "&refer_page_el_sn=15079&refer_page_sn=10002&refer_idx=3"
    "&xcx_trace_id={trace}&refer_page_name=index&_m_uin={uin}&xcx_version=v8.6.46"
)


def garden_referer(cookie_str=""):
    """果园页 referer（带查询参数）。

    ⚠️ 写这个函数是因为实测：偷水用裸的 `garden_index_lz_0.html` 会被判
    `10018 当前用户状态异常`，加上 `?_pdd_fs=1&_pdd_tc=...&fun_id=wechat_app_home
    &refer_page_el_sn=15079&...&xcx_trace_id=...` 立刻成功（+17 水滴）。
    服务端在校验 referer 里的页面来源参数，裸 URL 视为非正常入口。
    """
    uin = ""
    try:
        uin = cookie_str_to_dict(cookie_str).get("pdd_user_uin", "")
    except Exception:
        pass
    return GARDEN_REFERER_TPL.format(
        trace=random.randint(10 ** 16, 10 ** 17 - 1), uin=uin)


def make_manor_headers(pdduid, cookie_str, risk=False):
    """果园接口公共头。

    risk=True 时才附加 anti-token / verifyauthtoken —— mission/list、
    mission/complete、steal/water、common/water/gain 这些要，其他接口裸头能过。
    铁律一：anti-token 必须用「与本请求头同一个 UA」生成，混搭必 10018。
            缓存在 get_anti_token 里按 UA 隔离，不要绕过它。
    铁律二：Referer 必须是带查询参数的果园页地址，裸 URL 写操作会被判 10018。
    """
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://mobile.yangkeduo.com",
        "Referer": garden_referer(cookie_str),
    }
    if risk:
        headers["x-requested-with"] = "com.tencent.mm"
        anti = get_anti_token()
        if anti:
            headers["anti-token"] = anti
        vt = get_verify_token(pdduid)
        if vt:
            headers["verifyauthtoken"] = vt
    cookies = cookie_str_to_dict(cookie_str)
    return headers, cookies


def manor_post(pdduid, cookie_str, path, body, timeout=15, tag="", risk=False):
    """统一 POST：自动补 fun_pl、每次重算 cookie，异常返回空 dict 不炸流程"""
    url = f"{MANOR_BASE}{path}"
    headers, cookies = make_manor_headers(pdduid, cookie_str, risk=risk)
    payload = dict(body or {})
    payload.setdefault("fun_pl", FUN_PL)
    s = make_session()
    try:
        r = s.post(f"{url}?pdduid={pdduid}", headers=headers,
                   cookies=cookies, json=payload, timeout=timeout)
        data = r.json()
        if not isinstance(data, dict):
            return {}
        # 顺手回填最新 tubetoken，给后续接口用
        tok = data.get("tubetoken")
        if isinstance(tok, str) and tok:
            _TUBE["token"] = tok
        # 万一哪天 PDD 改成响应下发新 verifyauthtoken，这里自动接住
        harvest_verify_token(data)
        return data
    except Exception as e:
        if tag:
            log(f"  [{tag}] 请求异常: {e}")
        return {}


def query_user_water(pdduid, cookie_str):
    """查水滴，返回 (水量, 是否有效)。error_code 40001 = cookie 失效"""
    data = manor_post(pdduid, cookie_str,
                      "/manor-gateway/manor/query/user/water", {}, tag="水滴")
    if not data:
        return 0, False
    if str(data.get("error_code")) in ("40001", "40003"):
        return 0, False
    try:
        return int(data.get("water_amount") or 0), True
    except (TypeError, ValueError):
        return 0, False


def get_water(pdduid, cookie_str):
    """查询当前水滴数量"""
    water, _ok = query_user_water(pdduid, cookie_str)
    return water


def get_home_page(pdduid, cookie_str, tubetoken):
    """果园首页。

    老接口 manor-query/proxy/home/page 已下线，新版拆成：
      manor-query/tree/part/get  拉果树分片（顺带可能回新 tubetoken）
      manor-query/health/info    健康度 / 营养值 / 背包
    水滴单独用 query/user/water 查。
    """
    water, ok = query_user_water(pdduid, cookie_str)
    if not ok:
        log("  [首页] 验证失败, Cookie可能已过期")
        return None, None

    tree = manor_post(pdduid, cookie_str, "/manor-query/tree/part/get",
                      {"part_id_list": [102], "source": "", "tubetoken": tubetoken},
                      tag="首页")
    if str(tree.get("error_code")) in ("40001", "40003"):
        log("  [首页] 验证失败, Cookie可能已过期")
        return None, None
    new_token = tree.get("tubetoken") or tubetoken
    log(f"  [首页] 水滴: {water}")
    return new_token, water


def get_health_info(pdduid, cookie_str, tubetoken):
    """健康度 / 营养值 / 背包（新接口，老脚本没有）"""
    data = manor_post(pdduid, cookie_str, "/manor-query/health/info",
                      {"tubetoken": tubetoken}, tag="状态")
    if not data:
        return {}
    degree = data.get("health_degree")
    max_degree = data.get("max_health_degree")
    nutrient = data.get("nutrient")
    bag = data.get("backpack_goods_list") or {}
    bag_cnt = len(bag) if isinstance(bag, dict) else len(bag or [])
    log(f"  [状态] 健康度: {degree}/{max_degree}  营养值: {nutrient}  背包: {bag_cnt}项")
    return data


def water_tree(pdduid, cookie_str, tubetoken, max_times=50):
    """浇水：新版每次消耗 WATER_COST 滴（默认30），merge_cost=true"""
    water = get_water(pdduid, cookie_str)
    cost = max(10, WATER_COST)
    log(f"  [浇水] 当前水滴: {water}（每次 {cost} 滴）")
    if water < cost:
        log(f"  [浇水] 水滴不足 {cost} 滴，跳过")
        return 0
    count = min(max_times, water // cost)
    watered = 0
    for i in range(count):
        body = {
            "screen_token": "",
            "atw": False,
            "location_auth": False,
            "last_stay_time": 80 + i * 4,
            "can_trigger_random_mission": False,
            "product_scene": 0,
            "minor": False,
            "mission_type": 0,
            "cost_water_amount": cost,
            "merge_cost": True,
            "fun_id": "wechat_app_home",
            "lower_end_device": False,
            "cost_water_competition_in_scene_icon": False,
            "is_small_screen": True,
            "tubetoken": tubetoken,
        }
        result = manor_post(pdduid, cookie_str, "/manor/water/cost", body, tag="浇水")
        left = result.get("now_water_amount")
        if left is not None and left < water:
            water = left
            watered += 1
            log(f"  [浇水] {watered}/{count}, 剩余: {left}")
            if left < cost:
                break
            time.sleep(0.3)
        else:
            log("  [浇水] 水滴未扣除，停止")
            break
    final = get_water(pdduid, cookie_str)
    log(f"  [浇水] 完成! 浇水{watered}次, 剩余水滴: {final}")
    return watered


def get_mission_list(pdduid, cookie_str, tubetoken):
    """任务列表。

    新版响应把任务放在**顶层 mission_list**（dict，key=mission_type），
    老脚本读的 activity_vo_map[*].mission_list 现在是空的，所以一直显示 0 个任务。

    风控（2026-10-21 重新实测，修正旧说法）：
      真正卡人的是 anti-token 与 UA 错配、Referer 是裸地址 → 10018。
      verifyauthtoken / tubetoken 缺失时多数情况仍能过（实测假 token、
      空 token、无 tubetoken 都是 HTTP 200 正常返回），所以这里不再
      因为缺 token 就直接跳过，先打一次再说。
    """
    log("  [任务] 获取任务列表...")
    vt = get_verify_token(pdduid)
    if not vt:
        log("  [任务] 没有 verifyauthtoken，先裸头试一次")
    elif VT_SRC_LOG.get("shown") != vt:
        VT_SRC_LOG["shown"] = vt
        src = "环境变量 PDD_VERIFY_TOKEN" if VERIFY_TOKEN else _RT_VERIFY.get("src", "登录")
        log(f"  [任务] 使用 verifyauthtoken 来源: {src}")

    tubetoken = _tube(tubetoken)
    if not tubetoken:
        log("  [任务] tubetoken 为空，先跑一次首页/浇水拿到 token 更稳")

    body = {
        "activity_id_list": MISSION_ACT_IDS,
        "mission_types": MISSION_TYPES,
        "request_params": {"act201036EntryInfo": {"4": {"needRefresh": True}}},
        "lower_end_device": False,
    }
    if tubetoken:
        body["tubetoken"] = tubetoken
    result = {}
    last_src = ""
    tokens = list(iter_verify_tokens(pdduid)) or [("", "无token")]
    for vt, src in tokens:
        _FORCE_VT["token"] = vt
        try:
            result = manor_post(pdduid, cookie_str, "/manor/mission/list", body,
                                tag="任务", risk=True)
        finally:
            _FORCE_VT["token"] = ""
        last_src = src
        code = str(result.get("error_code"))
        if result and code != "10018":
            # 只有候选池里的 token 打通才提为首选；环境变量不写进池子
            if src != "env" and not VERIFY_TOKEN and src != _RT_VERIFY.get("src"):
                _RT_VERIFY["token"] = vt
                _RT_VERIFY["src"] = src
                log(f"  [任务] 候选 token({src}) 可用，已设为默认")
            mark_verify_ok(vt)          # 记一笔「这个 token 能用」，写进磁盘
            _vt_cache_save(pdduid, vt, src)
            break
        if code == "10018":
            log(f"  [任务] token 来源({src}) 被风控拒绝，换下一个候选")
        result = {}

    if not result:
        return [], []
    if str(result.get("error_code")) == "10018":
        # 10018 的真正主因通常是 anti-token 与 UA 错配、或 Referer 是裸地址，
        # 不是 verifyauthtoken 过期。所以先别急着怀疑 token。
        log("  [任务] 风控拦截(10018)")
        log("        优先检查：① anti-token 是否用与本请求同一个 UA 生成")
        log("                  ② Referer 是否带 _pdd_fs/_pdd_tc/fun_id 等查询参数")
        if VERIFY_TOKEN:
            log("        若上面都没问题，说明手填的 PDD_VERIFY_TOKEN 已失效：")
            log("        删掉它，或用 YYB 模式让脚本自动取一个新的")
        elif _RT_VERIFY.get("token"):
            log("        token 本身可能已随 PDD 会话轮换失效，清缓存重取：")
            log("        删除 pdd_verify_cache.json，再跑一次（会自动经 YYB 重取）")
        else:
            log("  [任务] 缺 verifyauthtoken，任务环节跳过")
        return [], []

    raw = result.get("mission_list") or {}
    if isinstance(raw, dict):
        items = list(raw.items())
    elif isinstance(raw, list):
        items = [(str(x.get("type")) if isinstance(x, dict) else "?", x) for x in raw]
    else:
        items = []

    tasks = []
    for key, m in items:
        if not isinstance(m, dict):
            continue
        mtype = m.get("type")
        try:
            mtype = int(mtype if mtype is not None else key)
        except (TypeError, ValueError):
            continue

        reward_amount, reward_type = 0, ""
        for ri in (m.get("reward_info") or []):
            if not isinstance(ri, dict):
                continue
            try:
                amt = int(ri.get("min_reward_amount") or 0)
            except (TypeError, ValueError):
                amt = 0
            if ri.get("reward_type") == 1:
                reward_amount, reward_type = amt, "水滴"
                break
            if not reward_amount:
                reward_amount, reward_type = amt, f"T{ri.get('reward_type')}"

        finished = int(m.get("finished_count") or 0)
        max_count = int(m.get("max_count") or 0)
        drawed = int(m.get("drawed_count") or 0)

        tasks.append({
            "mission_id": mtype,
            "activity_id": 0,
            "type": mtype,
            "finished_count": finished,
            "max_count": max_count,
            "drawed_count": drawed,
            "is_draw": drawed >= max_count and max_count > 0,
            "is_open": bool(m.get("is_open")),
            "unified_status": m.get("unified_status"),
            "reward_amount": reward_amount,
            "reward_type": reward_type,
        })

    # 可领：做过（finished>=1）且没领满（drawed < max）
    can_claim = [t for t in tasks
                 if t["finished_count"] >= 1
                 and (t["max_count"] <= 0 or t["drawed_count"] < t["max_count"])]

    if tasks:
        log(f"  [任务] 共{len(tasks)}个, 可领取: {len(can_claim)}")
        for t in tasks:
            flag = " [可领]" if t in can_claim else ""
            log(f"    type={t['mission_id']} done={t['finished_count']}/{t['max_count']} "
                f"drawed={t['drawed_count']} open={t['is_open']} "
                f"status={t['unified_status']} +{t['reward_amount']}{t['reward_type']}{flag}")
    else:
        log("  [任务] 接口返回空任务列表（可能今日任务已全部完成）")
    return can_claim, []


def accept_mission(pdduid, cookie_str, tubetoken, activity_id, mission_id):
    """老接口 /manor/mission/accept 已下线。

    新模型任务由服务端直接下发（is_open=true），不需要"先接受再完成"，
    这个函数保留只为兼容老调用方，直接返回 True。
    """
    return True


def claim_mission(pdduid, cookie_str, tubetoken, activity_id, mission_id):
    """完成任务 / 领任务奖励。

    老接口 /manor/mission/draw 已下线，新版两步：
      POST /manor/mission/complete       {mission_type, tubetoken}  → result:true
      POST /manor/mission/complete/gain  {mission_type, gain_time:1, ...} → 奖励入账
    """
    mtype = int(mission_id)
    data = manor_post(pdduid, cookie_str, "/manor/mission/complete",
                      {"mission_type": mtype, "tubetoken": _tube(tubetoken)},
                      tag="领奖", risk=True)
    if not data.get("result"):
        msg = data.get("error_msg") or data.get("error_code") or "未完成/已领过"
        log(f"  [任务] {mtype} 跳过: {msg}")
        return False

    water = data.get("water_amount")
    reward = data.get("reward_amount")
    log(f"  [任务] {mtype} 完成成功, 当前水滴 {water}, 本次奖励 {reward}")

    # 奖励入账（部分任务不调这一步水滴不涨）
    gain = manor_post(pdduid, cookie_str, "/manor/mission/complete/gain", {
        "mission_type": mtype,
        "gain_time": 1,
        "no_reward": False,
        "store_to_water_bag": False,
        "tubetoken": _tube(tubetoken),
    }, tag="领奖", risk=True)
    if gain.get("water_amount") is not None:
        log(f"  [任务] {mtype} 入账后水滴: {gain.get('water_amount')}"
            f"（+{gain.get('gain_amount') or 0}）")
    return True


def daily_checkin(pdduid, cookie_str, tubetoken):
    """每日签到：ui_id 从 3 改成 1（2026-10 抓包校准）"""
    log("  [签到] 签到中...")
    body = {
        "type": 201811,
        "params": {"ui_id": 1, "type": 2},
        "fun_id": "wechat_app_home",
        "tubetoken": tubetoken,
    }
    result = manor_post(pdduid, cookie_str, "/manor/common/apply/activity", body, tag="签到")
    if result.get("success"):
        log("  [签到] 成功!")
        return True
    log(f"  [签到] 今日已签到或不可签: {result.get('error_msg') or result.get('status')}")
    return False


def common_water_gain(pdduid, cookie_str, tubetoken, gain_type=15):
    """通用领水（新接口）：浏览/看视频类奖励直接加水滴。

    抓包 body: {"fun_id":"wechat_app_home","type":15,"low_end_device":"false",
               "params":{"15":50000},"tubetoken":...}
    """
    body = {
        "fun_id": "wechat_app_home",
        "type": gain_type,
        "low_end_device": "false",
        "params": {str(gain_type): 50000},
        "tubetoken": tubetoken,
    }
    data = manor_post(pdduid, cookie_str, "/manor/common/water/gain", body,
                      tag="领水", risk=True)
    if data.get("success"):
        log(f"  [领水] type={gain_type} 成功, 奖励 {data.get('reward_amount') or '?'} 水滴")
        return True
    if data:
        st = data.get("status")
        if st == 2:
            log(f"  [领水] type={gain_type} 今日已领过，跳过")
        else:
            log(f"  [领水] type={gain_type} 无奖励: {data.get('error_msg') or st}")
    return False


def tag_mission_list(pdduid, cookie_str, tubetoken, tag_name="SCAN_DEGREE_MISSION_CPT"):
    """标签任务查询（新接口）：浏览时长类任务，脚本只读展示不做"""
    data = manor_post(pdduid, cookie_str, "/manor-query/tag/mission/list",
                      {"mission_tag": tag_name, "tubetoken": tubetoken}, tag="标签任务")
    raw = data.get("mission_list") or {}
    if isinstance(raw, dict):
        items = raw.values()
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    out = []
    for v in items:
        if not isinstance(v, dict):
            continue
        out.append((v.get("type"), v.get("finished_count"), v.get("max_count"),
                    v.get("expire_time")))
    if out:
        log("  [标签任务] " + tag_name + ": " + ", ".join(
            f"{t[0]} {t[1]}/{t[2]}" for t in out))
    return out


# ===== 抢水滴 =====
def get_friend_list(pdduid, cookie_str, tubetoken):
    """获取好友列表(含机器人), 用于抢水滴"""
    log("  [偷水] 获取好友列表...")
    result = manor_post(pdduid, cookie_str, "/manor-query/friend/list/page",
                        {"page_num": 1, "tubetoken": tubetoken}, tag="偷水")
    friend_list = result.get("friend_list", []) or []
    can_steal = []
    for f in friend_list:
        if not isinstance(f, dict):
            continue
        steal_status = f.get("steal_water_status", {}) or {}
        if steal_status.get("status") == 2:
            can_steal.append({
                "uid": f.get("uid"),
                "nickname": f.get("nickname", "未知"),
                "amount": f.get("amount", 0),
            })
    log(f"  [偷水] 可偷好友: {len(can_steal)} 人")
    for f in can_steal:
        log(f"    uid={f['uid']} {f['nickname']} 水量={f['amount']}")
    return can_steal


def get_steal_chances(pdduid, cookie_str, tubetoken):
    """剩余偷水次数。

    老接口 /manor/steal/chance/lack 已下线（返回 404/空），
    新版从好友主页 manor-query/proxy/friend/home/page 的
    activity_vo_map["201423"] 里拿 free_chance / daily_free_chance / rest_chance。
    """
    data = manor_post(pdduid, cookie_str, "/manor-query/proxy/friend/home/page",
                      {"tubetoken": tubetoken}, tag="偷水")
    act = ((data.get("activity_vo_map") or {}).get("201423") or {})
    if not isinstance(act, dict):
        act = {}
    free_chance = act.get("free_chance")
    daily = act.get("daily_free_chance")
    rest = act.get("rest_chance")
    robots = [r for r in (act.get("robots") or []) if isinstance(r, dict)]
    robot_uids = [(r.get("uid"), r.get("nickname", "机器人"), r.get("water", 0))
                  for r in robots]
    if rest is None:
        # 接口没给就按每日 5 次兜底，真没次数了 steal/water 会返回 left_can_steal_count=0
        rest = 5
        log("  [偷水] 次数接口没返回，按每日5次兜底")
    try:
        rest = int(rest)
    except (TypeError, ValueError):
        rest = 5
    log(f"  [偷水] 免费次数: {free_chance}, 每日总次数: {daily}, 剩余: {rest}")
    return rest, robot_uids


def steal_water_from_friend(pdduid, cookie_str, tubetoken, friend_uid, dog_status):
    """对单个好友偷水。

    抓包 body: {"friend_uid":..., "dog_status":3, "tubetoken":"...", "fun_pl":7}
    ⚠️ tubetoken 是必填，缺了服务端直接拒（不报错、不扣次数、返回里没有
    steal_amount），表现就是「每次都未偷到」。返回整个响应 dict。
    """
    return manor_post(pdduid, cookie_str, "/manor/steal/water",
                      {"friend_uid": friend_uid, "dog_status": dog_status,
                       "tubetoken": tubetoken}, tag="偷水", risk=True)


def steal_from_friends(pdduid, cookie_str, tubetoken):
    """抢水滴主流程：次数从 steal/water 响应的 left_can_steal_count 实时更新"""
    friends = get_friend_list(pdduid, cookie_str, tubetoken)
    rest_chance, robot_uids = get_steal_chances(pdduid, cookie_str, tubetoken)

    all_targets = [(f["uid"], f["nickname"], f["amount"]) for f in friends]
    all_targets.extend(robot_uids)
    all_targets = [t for t in all_targets if t[0]]
    if not all_targets:
        log("  [偷水] 没有可偷的目标")
        return

    total_stolen = 0
    steal_count = 0
    log(f"  [偷水] 开始偷水, 剩余次数 {rest_chance}, 目标 {len(all_targets)} 个...")

    for target_uid, nickname, water in all_targets:
        if rest_chance <= 0:
            log("  [偷水] 次数用完，停止")
            break
        if isinstance(water, (int, float)) and water <= 0:
            continue
        dog = random.randint(1, 3)
        stolen = 0
        for retry in range(STEAL_RETRY):
            data = steal_water_from_friend(pdduid, cookie_str, tubetoken, target_uid, dog)
            if not data:
                time.sleep(0.2)
                continue
            try:
                left = data.get("left_can_steal_count")
                if left is not None:
                    rest_chance = int(left)
            except (TypeError, ValueError):
                pass
            amount = data.get("steal_amount") or 0
            bitten = data.get("bitten_water") or 0
            if amount > 0:
                stolen = amount
                break
            if rest_chance <= 0:
                break
            # 被狗咬 / miss 都用同一狗位重试（抓包证明同狗位重试能从 miss 变成功）
            time.sleep(0.15)
        if stolen > 0:
            total_stolen += stolen
            steal_count += 1
            log(f"  [偷水] uid={target_uid} {nickname} dog={dog}: +{stolen}滴, 剩余次数 {rest_chance}")
        else:
            log(f"  [偷水] uid={target_uid} {nickname} dog={dog}: 未偷到")
        time.sleep(0.3)

    log(f"  [偷水] 完成! 共偷 {steal_count} 次, 获得 {total_stolen} 水滴")

def run_garden(pdduid, cookie_str, tubetoken):
    """果园主流程（Cookie 模式 / Code 模式共用）

    2026-10 新版顺序：
      首页(水滴+树) → 状态(健康度) → 签到 → 通用领水 → 浇水
        → 任务列表 → 完成任务领奖 → 标签任务 → 偷水 → 汇总
    返回 (最新 tubetoken, 最终水滴)
    """
    new_token, water = get_home_page(pdduid, cookie_str, tubetoken)
    if new_token is None:
        return None, None
    tubetoken = new_token or tubetoken
    log(f"当前水滴: {water}")

    # 1. 健康度 / 营养值 / 背包（新接口）
    get_health_info(pdduid, cookie_str, tubetoken)
    time.sleep(0.3)

    # 2. 签到
    daily_checkin(pdduid, cookie_str, tubetoken)
    time.sleep(0.8)

    # 3. 通用领水（新接口）：先领后浇，能把水滴用足
    if not NO_WATER_GAIN:
        if common_water_gain(pdduid, cookie_str, tubetoken, 15):
            time.sleep(0.5)

    # 4. 浇水
    water_tree(pdduid, cookie_str, tubetoken, max_times=50)
    time.sleep(0.8)

    # 5. 任务：领奖 + 标签任务
    if not NO_TASK:
        can_claim, need_accept = get_mission_list(pdduid, cookie_str, tubetoken)
        if need_accept:
            log(f"\n  [任务] 正在接受 {len(need_accept)} 个任务...")
            for t in need_accept:
                accept_mission(pdduid, cookie_str, tubetoken,
                               t["activity_id"], t["mission_id"])
                time.sleep(0.3)
        if can_claim:
            log(f"\n  [任务] 正在领取 {len(can_claim)} 个任务的奖励...")
            for t in can_claim:
                claim_mission(pdduid, cookie_str, tubetoken,
                              t["activity_id"], t["mission_id"])
                time.sleep(0.5)
        tag_mission_list(pdduid, cookie_str, tubetoken)

    # 6. 偷水
    if not NO_STEAL:
        steal_from_friends(pdduid, cookie_str, tubetoken)

    final = get_water(pdduid, cookie_str)
    return tubetoken, final


def single_cookie_run(cookie_str, idx, total):
    log(f"\n{'='*48}")
    log(f"Cookie账号 [{idx}/{total}]")
    pdduid = extract_uid(cookie_str)
    if not pdduid:
        log("[错误] 当前Cookie缺少 pdd_user_id，跳过")
        return
    log(f"UID: {pdduid}")
    _vt = get_verify_token(pdduid)
    if _vt:
        log(f"  风控 token: 复用缓存({mask(_vt)})，PID 不需要再登录")
    else:
        log("  风控 token: 无 —— Cookie 模式没有 openid 取不了，"
            "先跑一次 Code 模式把缓存养出来，或手填 PDD_VERIFY_TOKEN")
    cookies = cookie_str_to_dict(cookie_str)
    tubetoken = cookies.get("tubetoken", "")
    token, final = run_garden(pdduid, cookie_str, tubetoken)
    if token is None:
        log("[失败] Cookie 无效，跳过该账号")
        return
    if final is None:
        log("[失败] 首页加载失败")
        return
    log(f"\n该账号最终水滴: {final}")

# ===== 单账号处理 =====
def process_account(openid, idx, total):
    """处理单个账号: 登录获取Cookie -> 执行果园任务"""
    log(f"\n{'='*48}")
    log(f"账号 [{idx}/{total}] openId={mask(openid)}")
    cookie_str = cached_cookie(openid)
    pdduid = ""
    if cookie_str:
        pdduid = extract_uid(cookie_str)
        if pdduid:
            cookies = cookie_str_to_dict(cookie_str)
            tubetoken = cookies.get("tubetoken", "")
            new_token, test_water = get_home_page(pdduid, cookie_str, tubetoken)
            if new_token is not None:
                log(f"缓存Cookie有效, uid={pdduid}, 水滴={test_water}")
            else:
                log(f"缓存Cookie失效, 重新登录")
                cookie_str = ""
        else:
            cookie_str = ""
    if not cookie_str:
        result = pdd_code_login(openid)
        if not result:
            log(f"[失败] 登录失败, 跳过此账号")
            return
        cookie_str, pdduid, pdd_uin = result
        save_cookie_cache(openid, cookie_str)
    if not pdduid:
        pdduid = extract_uid(cookie_str)
    if not pdduid:
        log(f"[失败] Cookie中无 pdd_user_id")
        return
    log(f"UID: {pdduid}")
    # verifyauthtoken：内存 → 磁盘缓存 → YYB 现取（三步走，都不用手动抓包）
    # 磁盘缓存在 get_verify_token 里已自动查过，这里只处理「还是没有」的情况。
    need_vt = (not get_verify_token(pdduid)) or \
        os.environ.get("PDD_TOKEN_RELOGIN", "0") == "1"
    if need_vt and YYB_GO_URL and not VERIFY_TOKEN:
        log("  [风控] 没有可用的 verifyauthtoken，走 YYB 现取一个（不覆盖 Cookie）")
        tok, _u = "", ""
        try:
            tok, _u = fetch_verify_token_via_yyb(openid, pdduid)
        except Exception as exc:
            log(f"  [风控] 取 token 异常: {exc}")
        if tok:
            log("  [风控] token 已就绪，Cookie 仍用缓存版本")
        else:
            log("  [风控] 没取到 token，任务环节会跳过（浇水偷水不受影响）")
    elif not get_verify_token(pdduid):
        log("  [风控] 无 verifyauthtoken（没配 YYB，磁盘也没缓存）→ 任务环节跳过")
        log("        手动补：抓任意 manor 请求头里的 verifyauthtoken，"
            "设 PDD_VERIFY_TOKEN 或写进 pdd_verify_cache.json")
    # 走统一主流程（内部已含首页校验 / 状态 / 签到 / 领水 / 浇水 / 任务 / 偷水）
    cookies = cookie_str_to_dict(cookie_str)
    tubetoken = cookies.get("tubetoken", "")
    new_token, final = run_garden(pdduid, cookie_str, tubetoken)
    if new_token is None:
        log(f"[失败] 首页加载失败, Cookie 无效")
        return
    if new_token and new_token != tubetoken:
        cookies["tubetoken"] = new_token
        cookie_str = cookie_dict_to_str(cookies)
        save_cookie_cache(openid, cookie_str)
    log(f"\n最终水滴: {final}")

# ===== 入口 =====
def main():
    log("=" * 48)
    log("拼多多果园 - 自动浇水领水滴")
    log(f"Build: {SCRIPT_BUILD}")
    log(f"HTTP: {'curl_cffi' if USE_CFFI else 'requests'}")
    required_functions = [
        "process_account",
        "single_cookie_run",
        "run_garden",
        "pdd_code_login",
        "get_home_page",
        "water_tree",
        "claim_mission",
        "get_health_info",
        "common_water_gain",
    ]
    missing_functions = [
        name for name in required_functions if not callable(globals().get(name))
    ]
    if missing_functions:
        log("[错误] 当前脚本文件不完整，缺少函数: " + ", ".join(missing_functions))
        log("[错误] 请部署完整脚本文件")
        return
    if COOKIE_STR:
        cookie_list = parse_cookies(COOKIE_STR)
        if not cookie_list:
            log("[错误] PDD_COOKIE解析为空！")
            return
        log(f"PDD_COOKIE模式，共 {len(cookie_list)} 个账号")
        for i, ck in enumerate(cookie_list, 1):
            try:
                single_cookie_run(ck, i, len(cookie_list))
            except Exception as e:
                log(f"[Cookie账号异常] {e}")
                traceback.print_exc()
        return
    if not YYB_GO_URL:
        log("[错误] 未配置环境变量!")
        log("  Code登录模式需要: YYB_GO_URL, PDD_OPENID")
        log("  PDD_OPENID 可填写 YYB Go 账号的 ID、UIN 或 openid")
        log("  Cookie直连模式需要: PDD_COOKIE (多账号支持换行/&分隔)")
        return
    openids = parse_openids(OPENID_RAW)
    if not openids:
        log("[错误] 未配置 PDD_OPENID")
        return
    log(f"共 {len(openids)} 个账号")
    for i, oid in enumerate(openids, 1):
        try:
            process_account(oid, i, len(openids))
        except Exception as e:
            log(f"[账号异常] {e}")
            traceback.print_exc()
    log("\n" + "=" * 48)
    log("全部账号处理完毕")
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"[异常] {e}")
        traceback.print_exc()
        sys.exit(1)
# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cc 脚本库下载！
# 脚本库官方QQ群1群: 429274456
# 脚本库官方QQ群2群: 1077801222
# 脚本库官方QQ群3群: 433030897
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。
