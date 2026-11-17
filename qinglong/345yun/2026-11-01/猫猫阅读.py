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

import json
import os
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

COOKIE = os.environ.get("MAOMAO_COOKIE", "").strip()
SENDKEY = os.environ.get("SENDKEY", "").strip()

COOKIES = [x.strip() for x in re.split(r"[\n&]+", COOKIE) if x.strip()]
SERVERCHAN_KEY = SENDKEY

MAX_PUSH_PER_DAY = 5
PUSH_ON_START = True
PUSH_WITH_ARTICLE = True
WAIT_AFTER_PUSH = 180

READ_SECONDS = (5, 10)
MAX_READS = 30
ROUND_SIZE = 30
LINK_READS = 1
GAP_SECONDS = (1, 3)
MIN_CYCLE = 12
COOLDOWN_RETRIES = 1
OPEN_ARTICLE = True
REFRESH_EACH_READ = False
WAIT_NEXT_ROUND = False

WD_THRESHOLD = 1.00
WD_PTYPE = 0
ALIPAY_ACCOUNT = ""
ALIPAY_NAME = ""
WD_UA = 2

DUWAY_HOSTS = ["http://baa0c41.vkgows.asia", "http://9caf1e2.osnifk.asia"]
WD_HOSTS = ["http://3721a37.oktwm.asia"]

ENTRY_SITE = "http://maomao520.cn"
ENTRY_API = "http://maomao520.cn/baobaocode.php"
AUTO_ENTER = True

BRAND = "猫猫阅读助手"
FIRST_RUN_WAIT = 15

QR_API = "https://api.pwmqr.com/qrcode/create/?url="
MYSIGN = "168"
VS = "1011"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".maomao_state.json")

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; 23049RAD8C Build/TKQ1.221114.001; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.189 "
    "Mobile Safari/537.36 XWEB/1500205 MMWEBSDK/20260901 MMWEBID/4648 "
    "REV/8bb09e872e59e0fd146f6d993eff881baacade68 MicroMessenger/8.0.78.3180(0x28004E3B) "
    "WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
)


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# 记录"这次运行是否已经静默等过一轮"，避免每个账号都等 3 分钟
_WAITED = [False]
# 「SENDKEY 没配」只提示一次，不要每个账号刷一遍
_NO_KEY_NOTED = [False]
# 服务端 Set-Cookie 下发的 cookie，自动带回下一次请求（原来的 Cookie 头是死的，
# 服务端中途换会话就跟丢了，表现就是读一篇 405 一次）
_COOKIE_JAR = {}
_COOKIE_SEEN = set()


def reset_jar():
    _COOKIE_JAR.clear()
    _COOKIE_SEEN.clear()


class LinkExpired(Exception):
    """入口链接过期（407 已失效），需要重新拿域名，拿不到就只能重抓 Cookie"""


class DailyLimit(Exception):
    """平台把这个号锁到明天（407 已被限制/请明天再来），扫新码也没用，只能等换码"""


class RoundLimit(Exception):
    """本轮 30 篇读满了。服务端原文：
          「请关闭页面，扫二维码查看金币，60分钟后可继续阅读！
            1、每轮上限30篇，每天6轮。」
    这不是链接失效，重取域名、换码、重扫码统统没用，只能等冷却时间过去。
    """

    def __init__(self, msg, minutes=60):
        super().__init__(msg)
        self.minutes = minutes


class Cooldown(Exception):
    """服务端冷却（405/407）：要么该过检测了，要么被限流了"""

    def __init__(self, msg, verify=False):
        super().__init__(msg)
        self.verify = verify


def _round_limit_minutes(msg):
    """从服务端文案里抠出「N分钟后可继续阅读」，抠不到按 60 分钟算"""
    m = re.search(r"(\d+)\s*分钟", msg or "")
    return int(m.group(1)) if m else 60


def is_round_limit(msg):
    """判断这条 msg 是不是「本轮读满了」而不是「链接坏了」"""
    msg = msg or ""
    return any(k in msg for k in ("每轮上限", "关闭页面", "可继续阅读", "60分钟后"))


def log(msg, *args):
    """带时间戳的事件行（启动、异常、重试、轮次边界）"""
    if args:
        msg = msg % args
    print(time.strftime("%H:%M:%S") + "  " + msg, flush=True)


def hr(char="─", width=64):
    print(char * width, flush=True)


def head(title, sub=""):
    """账号分隔块"""
    hr("━")
    print(" " + title + ("   " + sub if sub else ""), flush=True)
    hr("━")


def _dwidth(s):
    """终端显示宽度：中文/全角算 2 列"""
    w = 0
    for ch in str(s):
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def kv(key, val, indent=1, keyw=12):
    """对齐的字段行（按显示宽度补齐，中文不会错位）

    注意：只接受 (key, val) 两个值，需要格式化就自己先 % 好再传进来。
    """
    key, val = str(key), str(val)
    pad = " " * max(1, keyw - _dwidth(key))
    print("%s%s%s%s" % (" " * indent, key, pad, val), flush=True)


def push_log(msg, *args):
    """推送结果，跟账号块其他字段一样对齐，不打断视线"""
    if args:
        msg = msg % args
    kv("推送", msg)


def _pad(s, width, right=True):
    """按显示宽度补空格"""
    s = str(s)
    gap = max(0, width - _dwidth(s))
    return (" " * gap + s) if right else (s + " " * gap)


# 阅读明细表列宽（宽度, 是否右对齐）
_COLS = [(4, True), (6, True), (7, True), (12, True), (9, True), (7, True)]


def read_head():
    titles = ["#", "时长", "金币", "今日", "余额", "剩余"]
    print("│ " + " ".join(_pad(t, w, r) for t, (w, r) in zip(titles, _COLS)), flush=True)
    print("├" + "╌" * 56, flush=True)


def read_row(idx, secs, gold, day_read, day_gold, balance, remain):
    """阅读明细表的一行，按显示宽度对齐（用 │ 开头，避免行首空格被日志系统吃掉）"""
    today = "%s篇/%s" % (day_read if day_read is not None else "-",
                         day_gold if day_gold is not None else "-")
    vals = [
        "%02d" % idx,
        "%ds" % secs,
        ("%+d" % gold) if gold else "+0",
        today,
        balance if balance is not None else "-",
        remain if remain is not None else "-",
    ]
    print("│ " + " ".join(_pad(v, w, r) for v, (w, r) in zip(vals, _COLS)), flush=True)


def _jar_str():
    return "; ".join("%s=%s" % (k, v) for k, v in _COOKIE_JAR.items())


def _absorb_cookies(resp):
    """把响应里的 Set-Cookie 收进 jar，下次请求自动带上"""
    try:
        raw = resp.headers.get_all("Set-Cookie") or []
    except Exception:
        return
    for line in raw:
        head = line.split(";", 1)[0].strip()
        if "=" not in head:
            continue
        name, val = head.split("=", 1)
        name, val = name.strip(), val.strip()
        if not name or name in ("expires", "path", "domain"):
            continue
        if _COOKIE_JAR.get(name) != val:
            _COOKIE_JAR[name] = val
            if name not in _COOKIE_SEEN:
                _COOKIE_SEEN.add(name)
                kv("Cookie", "服务端下发 %s，已自动带上" % name)


def _merge_cookie(cookie):
    """把 jar 里的 cookie 合并进原始 Cookie 头，**同名覆盖，不重复追加**。

    之前是直接 "原始; jar"，服务端下发 bbus 后请求头里就会出现两个 bbus=
    （`bbus=旧; ...; bbus=新`），服务端取哪个不确定，可能直接把号认成别人。
    这里改成先拆成字典再合并，同名只留一份。
    """
    ck = (cookie or "").strip()
    if not _COOKIE_JAR:
        return ck
    parts = {}
    for seg in ck.split(";"):
        seg = seg.strip()
        if "=" in seg:
            k, v = seg.split("=", 1)
            if k.strip():
                parts[k.strip()] = v.strip()
    for k, v in _COOKIE_JAR.items():
        # bbus 是账号身份，只认用户抓包给的那一份。
        # 服务端中途下发的 bbus 可能是匿名会话，覆盖上去等于把号换掉了。
        if k == "bbus" and "bbus" in parts:
            continue
        parts[k] = v
    return "; ".join("%s=%s" % (k, v) for k, v in parts.items())


def build_headers(cookie=None, referer=None):
    h = {
        "User-Agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    ck = _merge_cookie(cookie)
    if ck:
        h["Cookie"] = ck
    if referer:
        h["Referer"] = referer
    return h


def http_get(url, cookie=None, referer=None, timeout=15, retries=1):
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=build_headers(cookie, referer))
            with urllib.request.urlopen(req, timeout=timeout) as r:
                _absorb_cookies(r)
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            _absorb_cookies(e)
            last = e
            if i < retries:
                time.sleep(1)
        except Exception as e:
            last = e
            if i < retries:
                time.sleep(1)
    raise RuntimeError("GET %s 失败: %s" % (url.split("?")[0], last))


def http_post(url, data, cookie=None, referer=None, timeout=15):
    if isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode("utf-8")
    else:
        body = data if data else b""
    h = build_headers(cookie, referer)
    h["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    req = urllib.request.Request(url, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            _absorb_cookies(r)
            return r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        _absorb_cookies(e)
        raise


# ----------------------------------------------------------------------
# 入口：拿阅读域名 + did
# ----------------------------------------------------------------------
def discover(cookie):
    errs = []
    for host in DUWAY_HOSTS:
        try:
            txt = http_post(host + "/haobaobao/duway", b"", cookie=cookie)
            j = json.loads(txt)
            if j.get("errcode") == 0:
                dom = (j.get("data") or {}).get("domain") or ""
                if not dom:
                    errs.append("%s 返回空域名" % host)
                    continue
                u = urllib.parse.urlparse(dom)
                did = urllib.parse.parse_qs(u.query).get("did", [""])[0]
                if not did:
                    errs.append("%s 域名里没有 did" % host)
                    continue
                return "%s://%s" % (u.scheme, u.netloc), did
            errs.append("%s -> %s" % (host, j.get("msg")))
        except Exception as e:
            errs.append("%s -> %s" % (host, e))
    raise RuntimeError("入口域名全部失败: " + " | ".join(errs))


# ----------------------------------------------------------------------
# 进一次阅读页（注册 did，等价于手机上点开链接进页面）
# ----------------------------------------------------------------------
def enter_read_page(host, did, cookie):
    try:
        http_get(read_url_of(host, did), cookie=cookie,
                 referer="https://mp.weixin.qq.com/", retries=0, timeout=12)
        return True
    except Exception:
        return False


# ----------------------------------------------------------------------
# 拉一次文章页（模拟手机打开）
# ----------------------------------------------------------------------
def open_article(url):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            return len(r.read())
    except Exception:
        return 0


# ----------------------------------------------------------------------
# 取文章
# ----------------------------------------------------------------------
def fetch_article(host, did, cookie):
    last = ""
    for _ in range(4):
        url = "%s/mmkkuserf?time=%d&mysign=%s&vs=%s&did=%s" % (
            host, int(time.time() * 1000), MYSIGN, VS, did)
        try:
            j = json.loads(http_get(url, cookie=cookie))
        except Exception as e:
            last = "网络错误: %s" % e
            time.sleep(1)
            continue
        code = j.get("errcode")
        if code == 0:
            link = (j.get("data") or {}).get("link") or ""
            if link:
                return link, None
            last = "返回链接为空"
            time.sleep(1)
            continue
        msg = j.get("msg") or ""
        # 先判「本轮读满」：这条最容易误判成链接失效，重取域名是白费力气
        if is_round_limit(msg):
            raise RoundLimit(msg, _round_limit_minutes(msg))
        if code == 407:
            if "限制" in msg or "明天" in msg:
                raise DailyLimit(msg)      # 号被锁到明天，换码也救不回来
            if "暂时" in msg or "稍候" in msg:
                raise Cooldown(msg)
            raise LinkExpired(msg)
        if code == 405:
            # 405「未能获取到用户信息」= 登录态要重新验，重进 /h/r 一般能救回来
            raise Cooldown(msg, verify=True)
        last = "errcode=%s %s" % (code, msg)
        time.sleep(1)
    return None, last


# ----------------------------------------------------------------------
# 领金币
# ----------------------------------------------------------------------
def claim(host, did, cookie, seconds):
    """返回 (data, err)。data 里 gold=本篇金币, last_gold=总金币, remain_read=今日剩余"""
    secs = seconds
    for _ in range(3):
        url = "%s/rightgetjm?time=%d&psign=%d&did=%s" % (
            host, secs, random.randint(1, 1000), did)
        try:
            j = json.loads(http_get(url, cookie=cookie, retries=0))
        except Exception as e:
            return None, "网络错误: %s" % e
        code = j.get("errcode")
        if code == 0:
            return (j.get("data") or {}), None
        msg = j.get("msg") or ""
        if "时间不足" in msg:
            secs += 3
            time.sleep(3)
            continue
        if is_round_limit(msg):
            raise RoundLimit(msg, _round_limit_minutes(msg))
        return None, "errcode=%s %s" % (code, msg)
    return None, "多次重试仍提示阅读时间不足"


# ----------------------------------------------------------------------
# 提现
# ----------------------------------------------------------------------
def parse_mksmey(html):
    out = {}
    m = re.search(r'var\s+request_id\s*=\s*"([^"]+)"', html)
    if m:
        out["request_id"] = m.group(1)
    m = re.search(r'id="exchange_gold"[^>]*>\s*([\d.]+)', html)
    if m:
        out["gold"] = int(float(m.group(1)))
    m = re.search(r'id="exchange_money"[^>]*>\s*([\d.]+)', html)
    if m:
        out["money"] = float(m.group(1))
    m = re.search(r'var\s+isallowtj\s*=\s*"(\d)"', html)
    if m:
        out["allow"] = m.group(1)
    m = re.search(r"var\s+nickname\s*=\s*'([^']*)'", html)
    if m:
        out["nick"] = m.group(1)
    return out


def try_withdraw(cookie, st):
    """返回 dict：{'ok':bool,'amount':float,'note':str}"""
    res = {"ok": False, "amount": 0.0, "note": ""}
    html, wd_host = None, None
    for h in WD_HOSTS:
        try:
            html = http_get(h + "/mksmey", cookie=cookie)
            wd_host = h
            break
        except Exception as e:
            kv("提现页", "%s 打不开：%s" % (h, e))
    if not html:
        res["note"] = "提现页打不开"
        return res

    info = parse_mksmey(html)
    if "request_id" not in info or "gold" not in info:
        res["note"] = "提现页解析失败（Cookie 可能已失效）"
        return res

    st["balance"] = info["gold"]
    st["money"] = info.get("money", 0.0)
    if info.get("nick"):
        st["uid"] = info["nick"]
    if info.get("allow") == "0":
        res["note"] = "账号被限制提现"
        return res

    usable = (info["gold"] // 1000) * 1000          # 只能整千兑换
    avail = round(info.get("money", 0.0) + usable / 10000.0, 2)
    if st.get("_bal") != (info["gold"], info.get("money")):
        kv("余额", "金币 %d（可兑 %.2f 元）+ 现金 %.2f 元 = %.2f 元" % (
            info["gold"], usable / 10000.0, info.get("money", 0.0), avail))
        st["_bal"] = (info["gold"], info.get("money"))

    if avail < WD_THRESHOLD:
        res["note"] = "余额 %.2f 元，未达提现阈值 %.2f 元" % (avail, WD_THRESHOLD)
        return res

    # 1) 金币兑现金
    money = info.get("money", 0.0)
    if usable >= 1000:
        try:
            txt = http_post(wd_host + "/haobaobao/getgold",
                            {"request_id": info["request_id"], "gold": usable},
                            cookie=cookie, referer=wd_host + "/mksmey")
            j = json.loads(txt)
        except Exception as e:
            res["note"] = "兑换请求失败: %s" % e
            return res
        if j.get("errcode") != 0:
            res["note"] = "兑换失败: %s" % (j.get("msg") or j.get("errcode"))
            return res
        money = round(money + float((j.get("data") or {}).get("money", 0)), 2)
        kv("兑换", "%d 金币 → %.2f 元，现金 %.2f 元" % (usable, usable / 10000.0, money))

    # 2) 提现
    body = {
        "signid": info["request_id"],
        "ua": WD_UA,
        "ptype": WD_PTYPE,
        "paccount": ALIPAY_ACCOUNT if WD_PTYPE == 1 else "",
        "pname": ALIPAY_NAME if WD_PTYPE == 1 else "",
    }
    try:
        txt = http_post(wd_host + "/haobaobao/getwithdraw", body,
                        cookie=cookie, referer=wd_host + "/mksmey", timeout=20)
        j = json.loads(txt)
    except Exception as e:
        res["note"] = "提现请求失败: %s" % e
        return res

    if j.get("errcode") == 0:
        res.update(ok=True, amount=money, note="提现成功")
        st["balance"] = 0
        st["money"] = 0.0
        kv("提现", "成功 %.2f 元" % money)
    else:
        res["note"] = "提现失败: %s" % (j.get("msg") or j.get("errcode"))
    return res


# ----------------------------------------------------------------------
# Server酱
# ----------------------------------------------------------------------
def push_serverchan(title, desp):
    key = (SERVERCHAN_KEY or "").strip()
    if not key:
        return False, "环境变量 SENDKEY 未配置"
    url = ("https://%s.push.ft07.com/send" % key) if key.startswith("sctp") \
        else ("https://sctapi.ftqq.com/%s.send" % key)
    try:
        body = urllib.parse.urlencode({"title": title[:100], "desp": desp}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": USER_AGENT,
        })
        txt = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
        j = json.loads(txt)
        ok = (j.get("code") == 0) or (j.get("data") is not None)
        return ok, txt[:150]
    except Exception as e:
        return False, str(e)


def push(title, desp):
    """带每日额度的推送（Server酱免费版 5 条/天，超了不再发）"""
    if not (SERVERCHAN_KEY or "").strip():
        return False, "环境变量 SENDKEY 未配置"
    st = load_state()
    today = time.strftime("%Y-%m-%d")
    if st.get("push_date") != today:
        st["push_date"] = today
        st["push_count"] = 0
    used = int(st.get("push_count") or 0)
    if used >= MAX_PUSH_PER_DAY:
        push_log("额度已用完（%d/%d），这条不推", used, MAX_PUSH_PER_DAY)
        save_state(st)
        return False, "今日额度用完"
    ok, info = push_serverchan(title, desp)
    if ok:
        st["push_count"] = used + 1
        push_log("成功（今日 %d/%d）", used + 1, MAX_PUSH_PER_DAY)
    else:
        push_log("失败：%s", info)
    save_state(st)
    return ok, info


# ----------------------------------------------------------------------
# 每日入口（maomao520.cn 每天换一次码，did 跟着新链接一起变）
# ----------------------------------------------------------------------
def fetch_daily_entry():
    """取当日落地链接，返回 {'luodi':..., 'token':..., 'daytime':...}"""
    try:
        j = json.loads(http_get(ENTRY_API, retries=1))
    except Exception as e:
        log("取当日入口失败：%s", e)
        return None
    if j.get("code") != 0:
        log("取当日入口异常：%s", j.get("msg") or j)
        return None
    d = j.get("data") or {}
    luo = (d.get("luodi") or "").strip()
    if not luo:
        return None
    return {
        "luodi": luo,
        "token": luo.rstrip("/").split("/")[-1],
        "daytime": d.get("daytime") or "",
    }


def nav_get(url, cookie=None, timeout=15):
    """按浏览器导航的方式请求（不带 XHR 头），返回 (状态码, Location, 正文)"""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    h = {"User-Agent": USER_AGENT,
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language": "zh-CN,zh;q=0.9"}
    ck = (cookie or "").strip()
    extra = _jar_str()
    if extra:
        ck = (ck + "; " + extra) if ck else extra
    if ck:
        h["Cookie"] = ck
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            _absorb_cookies(r)
            return r.status, None, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        _absorb_cookies(e)
        return e.code, e.headers.get("Location"), ""
    except Exception as e:
        return 0, None, str(e)


def enter_daily_entry(entry, cookie):
    """照手机的方式走一遍入口链，等价于点开当天的二维码"""
    luo = (entry or {}).get("luodi")
    if not luo:
        return False
    try:
        _, _, html = nav_get(luo, cookie)
        m = re.search(r"var\s+qrcode\s*=\s*'([^']+)'", html or "")
        if not m:
            return False
        token = m.group(1)
        u = urllib.parse.urlparse(luo)
        base = "%s://%s" % (u.scheme, u.netloc)
        txt = http_get("%s/mcctiaozhan?qrcode=%s" % (base, token), cookie=cookie, retries=0)
        j = json.loads(txt)
        if j.get("errcode") != 0:
            return False
        nxt = (j.get("data") or {}).get("tiao") or ""
        for _ in range(4):
            if not nxt:
                break
            code, loc, _ = nav_get(nxt, cookie)
            nxt = loc if code in (301, 302, 303, 307, 308) else None
        return True
    except Exception as e:
        kv("入口", "走入口链失败：%s" % e)
        return False


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False)
    except Exception as e:
        log("写状态文件失败: %s", e)


def read_url_of(host, did):
    """阅读页链接：把手机绑到脚本这一侧的 did 上。

    点开它才会出现「成功1 获取第二章」；只进平台首页（/haobaobao/home）
    是在手机上新建一个 did，跟脚本用的不是同一个，脚本照样 405。
    """
    return "%s/h/r?did=%s" % (host, did)


def push_entry(entry, article_link=None, force=False):
    """推入口：二维码 + 落地链接 +（可选）阅读页链接，全部在同一条消息里。

    force=True 时跳过「今天已推过」的去重，用于 405 之后补发阅读页链接。
    返回 True 表示这次真的发出去了；False = 关掉了 / 今天已推过 / 没配 key。
    """
    if not PUSH_ON_START and not force:
        return False        # force=405 抢救推送，不受「每轮开始推不推」开关限制
    if not entry and not article_link:
        return False

    if not (SERVERCHAN_KEY or "").strip():
        if not _NO_KEY_NOTED[0]:
            _NO_KEY_NOTED[0] = True
            push_log("环境变量 SENDKEY 未配置，本次不推送")
        return False

    token = (entry or {}).get("token") or ""
    key = token or ("date:" + time.strftime("%Y-%m-%d"))
    st = load_state()
    if not force and st.get("entry_token") == key:
        return False

    parts = ["**今天的新入口**（每天换新码，did 跟着变）\n",
             "①② 是同一个入口的两种打开方式，二选一即可；③ 是阅读页，必须点。\n"]

    if entry:
        qr = QR_API + urllib.parse.quote(entry["luodi"], safe="")
        parts.append("① 扫二维码")
        parts.append("![今日二维码](%s)\n" % qr)
        parts.append("② 点链接（码扫不出/图挂了就点这个）")
        parts.append("%s\n" % entry["luodi"])

    if article_link:
        # 这一条是阅读页 /h/r?did=，不是文章内容链接。
        # 它把手机绑到脚本这一侧的 did 上，点开才会出现「成功1 获取第二章」。
        # 只进平台首页（home）不会激活这个 did，脚本照样 405。
        parts.append("③ 点这个阅读页链接激活（打开后应出现「成功1 获取第二章」）")
        parts.append("%s\n" % article_link)
        parts.append("> 打不开或没出现「成功1」，就先做 ①②，再回来点 ③。\n")

    parts.append("---")
    parts.append("入口页：%s" % ENTRY_SITE)

    title = "%s 今日入口 %s" % (BRAND, time.strftime("%m-%d"))
    ok, _ = push(title, "\n".join(parts))
    if ok:
        st = load_state()          # push() 里已经累加了推送次数，重新读一次
        st["entry_token"] = key
        st["entry_date"] = time.strftime("%Y-%m-%d")
        st["entry_luodi"] = (entry or {}).get("luodi") or ""
        save_state(st)
    return ok


def silent_wait(reason):
    """推送后静默等待，期间一个请求都不发（探测最容易触发风控）"""
    if WAIT_AFTER_PUSH <= 0:
        return
    kv("等待", "%s，静默 %d 秒（期间不发请求）" % (reason, WAIT_AFTER_PUSH))
    time.sleep(WAIT_AFTER_PUSH)
    kv("等待", "结束，继续")


# ----------------------------------------------------------------------
# 单账号跑一轮
# ----------------------------------------------------------------------
def run_account(idx, cookie, entry=None):
    name = "账号%d" % idx
    st = {
        "idx": idx, "name": name, "uid": "", "reads": 0, "gold": 0, "invalid": 0,
        "balance": None, "money": None, "day_read": None, "day_gold": None,
        "remain": None, "wd": None, "abort": "",
    }
    head("%s" % name)
    reset_jar()                     # 每个号独立的会话 cookie，别串号

    # 先按手机的方式进一次今天的入口（did 跟着新链接走）
    if AUTO_ENTER and entry:
        if enter_daily_entry(entry, cookie):
            kv("入口", "已走通")
        else:
            kv("入口", "没走通，用现有会话试")

    try:
        host, did = discover(cookie)
    except Exception as e:
        st["abort"] = str(e)
        kv("域名", "获取失败：%s" % e)
        return st
    kv("域名", "%s   did=%s" % (host, did))
    enter_read_page(host, did, cookie)

    # 先看一眼余额（顺便确认 Cookie 有效、拿到昵称）
    try_withdraw(cookie, st)
    if st["uid"]:
        kv("账号ID", st["uid"])

    reads, refreshes, cool = 0, 0, 0
    attempts = 0                    # 总尝试次数，防止一直拿不到金币死循环
    link = None                     # 取到一次就复用，不每篇都重新取
    link_uses = 0                   # 当前这条链接已经读了几篇
    pushed_first = False
    table_open = False

    def on_round_full(e):
        """本轮 30 篇读满。返回 True = 已等到下一轮可以继续；False = 该退出了。

        服务端原话：「请关闭页面，扫二维码查看金币，60分钟后可继续阅读！
                     1、每轮上限30篇，每天6轮。」
        所以这里既不是链接失效，也不是登录态丢了，唯一解法是等冷却。
        """
        if reads:
            kv("轮次", "本轮 %d 篇已满（每轮上限 30 篇，每天 6 轮）" % reads)
            tail = "本轮 %d 篇已满" % reads
        else:
            # 服务端说满了，但本进程一篇都没读到 —— 说明是别的设备/别的进程先读掉的
            kv("轮次", "服务端判定这一轮已读满（本进程还没开始读）")
            tail = "服务端说这一轮已经读满"
        if not WAIT_NEXT_ROUND:
            st["abort"] = ("%s，要求 %d 分钟后才能继续。"
                           "%d 分钟后再跑就行，Cookie、域名都不用动"
                           % (tail, e.minutes, e.minutes))
            kv("退出", st["abort"])
            return False
        kv("等待", "原地等 %d 分钟进下一轮（期间不发任何请求）" % e.minutes)
        time.sleep(e.minutes * 60 + 20)     # 多给 20 秒，别卡在边界上重来一次
        kv("等待", "结束，开始下一轮")
        return True

    while reads < MAX_READS and attempts < MAX_READS * 3:
        attempts += 1
        cycle_t0 = time.time()

        # ---- 需要链接时才取（一个链接能连读 LINK_READS 篇，重复取反而触发风控）----
        if link is None or link_uses >= LINK_READS:
            link = None
            link_uses = 0
            try:
                link, err = fetch_article(host, did, cookie)
            except RoundLimit as e:
                if not on_round_full(e):
                    break
                reads = attempts = cool = 0
                link, link_uses = None, 0
                continue
            except Cooldown as e:
                # 405「没有登录信息」/ 407「阅读无效」：推送 + 静默等，只给一次机会
                if cool >= COOLDOWN_RETRIES:
                    st["abort"] = ("%s —— 静默等待后还是这样，退出。"
                                   "今天先别跑了，等换码或过几个小时再来" % e)
                    kv("退出", st["abort"])
                    break
                cool += 1
                kv("服务端", str(e))
                if not _WAITED[0]:
                    ru = read_url_of(host, did)
                    kv("激活", ru)          # 推送失败也能手动复制这条
                    if entry:
                        pushed_first = True     # 已经推过入口，后面不再重复尝试
                        push_entry(entry, ru, force=True)
                    silent_wait("请在手机上打开上面这条阅读页链接过检测")
                    _WAITED[0] = True
                else:
                    kv("等待", "已经静默等过一轮，还是不行，退出")
                    kv("激活", read_url_of(host, did))   # 想手动救就点这条再重跑
                    st["abort"] = "%s —— 等过检测后仍然无效，退出" % e
                    break
                enter_read_page(host, did, cookie)
                continue
            except DailyLimit as e:
                st["abort"] = ("%s —— 平台把这个号锁到明天了，今天扫新码也没用。"
                               "等换码（一般次日 0 点后）再跑，Cookie 不用动" % e)
                kv("退出", st["abort"])
                break
            except LinkExpired as e:
                if refreshes >= 2:
                    st["abort"] = "入口链接失效：%s。去 %s 换今天的码，Cookie 不用动" % (e, ENTRY_SITE)
                    kv("退出", st["abort"])
                    break
                refreshes += 1
                kv("重取", "链接失效，重新取域名（第 %d 次）" % refreshes)
                try:
                    host, did = discover(cookie)
                    kv("域名", "%s   did=%s" % (host, did))
                except Exception as e2:
                    st["abort"] = "重新取域名失败: %s" % e2
                    kv("退出", st["abort"])
                    break
                time.sleep(2)
                continue

            if not link:
                st["abort"] = err or "取文章失败"
                kv("失败", "取文章失败：%s" % st["abort"])
                break

            # 注意：这里不重置 cool。cool 只在真正读到金币时才清零，
            # 这样「取链接成功但领金币又报无效」不会再多等一轮

            # 拿到链接后，把「二维码 + 落地链接 + 阅读页链接」合成一条推
            if PUSH_ON_START and PUSH_WITH_ARTICLE and not pushed_first:
                pushed_first = True
                # 注意：推的是阅读页 /h/r?did=，不是 mmkkuserf 返回的文章内容链接。
                # 文章链接点开只会跳到微信文章，不会激活阅读会话；
                # 阅读页链接点开才会出现「成功1 获取第二章」。
                read_url = read_url_of(host, did)
                kv("激活", read_url)
                if push_entry(entry, read_url):
                    silent_wait("入口+阅读页已推送，等你在手机上打开")
                    _WAITED[0] = True

            # 服务端也拉一次文章页（配合检测，失败不影响）
            if OPEN_ARTICLE:
                open_article(link)

            # 推送 + 静默等待都做完了，重新计时，别把等待算成阅读时长
            cycle_t0 = time.time()

        # 一个 did 的会话只认一篇，开读前先重进一次阅读页，把会话续上
        if REFRESH_EACH_READ:
            enter_read_page(host, did, cookie)

        target = random.randint(READ_SECONDS[0], READ_SECONDS[1])
        time.sleep(target)
        secs = max(target, int(round(time.time() - cycle_t0)))

        try:
            data, err = claim(host, did, cookie, secs)
        except RoundLimit as e:
            if not on_round_full(e):
                break
            reads = attempts = cool = 0
            link, link_uses = None, 0
            continue

        # 405：多半是「这条链接对应的那篇已经领过」。重取一篇立刻再领，
        # 比推送 + 等 3 分钟划算得多，也不吃推送额度
        if data is None and "限制" not in (err or "") and "明天" not in (err or "") \
                and any(k in (err or "") for k in ("405", "407", "失效", "无效")):
            try:
                new_link, _e = fetch_article(host, did, cookie)
                if new_link:
                    link = new_link
                    link_uses = 0
                    if OPEN_ARTICLE:
                        open_article(link)
            except Exception:
                pass
            enter_read_page(host, did, cookie)
            time.sleep(random.uniform(0.8, 1.5))
            try:
                d2, e2 = claim(host, did, cookie, secs)
            except RoundLimit as e:
                if not on_round_full(e):
                    break
                reads = attempts = cool = 0
                link, link_uses = None, 0
                continue
            if d2 is not None:
                kv("补救", "重取链接后领到了，不用推送等待")
                data, err = d2, None
            else:
                err = e2 or err

        if data is None:
            kv("失败", "领金币失败（已读 %d 篇）：%s" % (reads, err))
            # 先判「锁到明天」：这种等多久都没用，直接退出
            if any(k in (err or "") for k in ("限制", "明天")):
                st["abort"] = ("%s —— 平台把这个号锁到明天了，今天扫新码也没用。"
                               "等换码（一般次日 0 点后）再跑，Cookie 不用动" % err)
                kv("退出", st["abort"])
                break
            if any(k in (err or "") for k in ("失效", "407", "405", "无效")):
                # 阅读无效 / 登录信息丢了：跟取链接失败走同一套
                # 只给一次「推送 + 静默等待」的机会，再不行就退出
                if cool >= COOLDOWN_RETRIES:
                    st["abort"] = "%s —— 静默等待后仍然无效，退出" % err
                    kv("退出", st["abort"])
                    break
                cool += 1
                link = None
                if not _WAITED[0]:
                    ru = read_url_of(host, did)
                    kv("激活", ru)          # 推送失败也能手动复制这条
                    if entry:
                        push_entry(entry, ru, force=True)
                    silent_wait("阅读无效，请在手机上打开上面这条阅读页链接")
                    _WAITED[0] = True
                else:
                    kv("等待", "已经静默等过一轮，还是无效，退出")
                    kv("激活", read_url_of(host, did))   # 想手动救就点这条再重跑
                    st["abort"] = "%s —— 等过检测后仍然无效，退出" % err
                    break
                enter_read_page(host, did, cookie)
                continue
            time.sleep(2)
            continue

        gold = int(data.get("gold") or 0)
        st["day_read"] = data.get("day_read")
        st["day_gold"] = data.get("day_gold")
        st["balance"] = data.get("last_gold")
        st["remain"] = data.get("remain_read")
        link_uses += 1

        if not table_open:
            print(flush=True)
            read_head()
            table_open = True

        if gold > 0:
            cool = 0                    # 读到金币了才重置失败计数
            reads += 1
            st["reads"] = reads
            st["gold"] += gold
        else:
            st["invalid"] += 1

        read_row(reads or link_uses, secs, gold, st["day_read"], st["day_gold"],
                 st["balance"], st["remain"])

        # 今日上限到了
        try:
            if st["remain"] is not None and int(st["remain"]) <= 0:
                print(flush=True)
                kv("停止", "今日阅读次数已用完（剩余 0）")
                break
        except (TypeError, ValueError):
            pass

        # 每轮结束提现一次
        if reads and reads % ROUND_SIZE == 0:
            r = try_withdraw(cookie, st)
            st["wd"] = r
            kv("提现", r["note"])

        # 控制单篇周期：不足 MIN_CYCLE 就补足，再叠一点随机间隔
        elapsed = time.time() - cycle_t0
        wait = MIN_CYCLE - elapsed + random.randint(GAP_SECONDS[0], GAP_SECONDS[1])
        if wait > 0:
            time.sleep(wait)

    # 收尾：提现
    r = try_withdraw(cookie, st) or {"ok": False, "note": "提现未执行"}
    st["wd"] = r

    print(flush=True)
    kv("小计", "阅读 %d 篇   金币 +%d   无效 %d 次" % (st["reads"], st["gold"], st["invalid"]))
    if r["ok"]:
        kv("提现", "成功 %.2f 元" % r["amount"])
    elif r.get("note"):
        kv("提现", r["note"])
    return st


# ----------------------------------------------------------------------
# 汇总
# ----------------------------------------------------------------------
def build_summary(results):
    out = []
    total_reads = total_gold = 0
    total_cash = 0.0
    for st in results:
        total_reads += st["reads"]
        total_gold += st["gold"]
        out.append(" %s   %s" % (st["name"], st["uid"] or "-"))
        if st["abort"]:
            out.append("  异常    %s" % st["abort"])
        out.append("  本轮    阅读 %d 篇   金币 +%d   无效 %d 次" % (
            st["reads"], st["gold"], st["invalid"]))
        if st["day_read"] is not None:
            out.append("  今日    %s 篇 / %s 金币   剩余 %s" % (
                st["day_read"], st["day_gold"], st["remain"]))
        if st["balance"] is not None:
            out.append("  余额    %s 金币（约 %.2f 元）  现金 %.2f 元" % (
                st["balance"], (st["balance"] or 0) / 10000.0, st["money"] or 0.0))
        if st["wd"]:
            if st["wd"]["ok"]:
                out.append("  提现    成功 %.2f 元" % st["wd"]["amount"])
                total_cash += st["wd"]["amount"]
            else:
                out.append("  提现    %s" % st["wd"]["note"])
        out.append("")
    out.append(" 合计    阅读 %d 篇   金币 +%d   提现 %.2f 元" % (
        total_reads, total_gold, total_cash))
    return "\n".join(out)


def first_run_guide():
    """没有 Cookie 时走这里：只讲环境变量怎么填。

    青龙是无人值守环境，不能用 input() 阻塞（stdin 是 /dev/null，一调就 EOFError），
    所以用「停留 N 秒」曝光。
    """
    hr("═")
    print(" 还没配环境变量，先填这两条", flush=True)
    hr("═")
    print(" 青龙 → 环境变量 → 新建", flush=True)
    kv("MAOMAO_COOKIE", "整条 Cookie，必须含 bbus=")
    kv("SENDKEY", "Server酱 key，可不填")
    hr("═")
    if FIRST_RUN_WAIT > 0:
        time.sleep(FIRST_RUN_WAIT)
    st = load_state()
    st["first_run_shown"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(st)


def main():
    hr("━")
    print(" %s   %s" % (BRAND, time.strftime("%Y-%m-%d %H:%M:%S")))
    kv("账号数", len(COOKIES))
    kv("阅读", "%d-%d 秒/篇   提现阈值 %.2f 元" % (
        READ_SECONDS[0], READ_SECONDS[1], WD_THRESHOLD))
    kv("推送", "已配 SENDKEY，开跑推一条" if (SERVERCHAN_KEY or "").strip()
       else "没配 SENDKEY，本次不推送（不影响阅读）")
    hr("━")

    if not COOKIES:
        first_run_guide()
        return 1

    # 今天的入口（每天换码，did 跟着新链接一起变）
    entry = fetch_daily_entry()
    if entry:
        kv("入口", "token=%s" % entry["token"][:8])
        if PUSH_ON_START and not PUSH_WITH_ARTICLE:
            # 不合并阅读页链接：现在就推（二维码 + 落地链接）
            if push_entry(entry):
                silent_wait("今日入口已推送，等你在手机上打开过检测")
                _WAITED[0] = True
        elif PUSH_ON_START and PUSH_WITH_ARTICLE:
            kv("推送", "等拿到阅读页链接后合并成一条再推")
        else:
            kv("推送", "已关闭（PUSH_ON_START=False）")
    else:
        kv("入口", "没取到，跳过推送")

    results = []
    for i, ck in enumerate(COOKIES, 1):
        ck = (ck or "").strip()
        if not ck:
            log("账号%d Cookie 是空的，跳过", i)
            continue
        try:
            results.append(run_account(i, ck, entry))
        except Exception as e:
            log("账号%d 运行异常：%s", i, e)
            results.append({
                "idx": i, "name": "账号%d" % i, "uid": "", "reads": 0, "gold": 0,
                "invalid": 0, "balance": None, "money": None, "day_read": None,
                "day_gold": None, "remain": None, "wd": None,
                "abort": "运行异常: %s" % e,
            })

    if not results:
        log("没有可运行的账号")
        return 1

    hr("━")
    print(" 汇总", flush=True)
    hr("━")
    print(build_summary(results), flush=True)
    if entry:
        kv("入口页", ENTRY_SITE)
        kv("落地", entry["luodi"])
    st = load_state()
    if st.get("push_date") == time.strftime("%Y-%m-%d"):
        kv("推送", "今日已用 %s/%d 条" % (st.get("push_count", 0), MAX_PUSH_PER_DAY))
    hr("━")
    return 0


if __name__ == "__main__":
    sys.exit(main())


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