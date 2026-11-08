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

# -*- coding: utf-8 -*-
"""
草原云（内蒙古日报 iyunxh / cyy.nmgcyy.com.cn）自动签到 + 阅读任务 青龙脚本
由 APK「草原云协议」(com.lcs.cyy) 还原而来

环境变量：
  CAOYUANYUN_ACCOUNTS    必填，格式：手机号#密码&手机号#密码
                         也支持单独指定代理：手机号#密码#http://user:pass@ip:port
  CAOYUANYUN_DO_TASKS    是否做阅读任务，默认 true
  CAOYUANYUN_SIGNIN      是否签到，默认 true
  CAOYUANYUN_MAX_TASKS   每轮最多做多少个任务，0=全部
  CAOYUANYUN_READ_SECONDS 阅读停留秒数，默认 3（与 APK 默认一致）
  CAOYUANYUN_PARALLEL    并发账号数，默认 3（与 APK 默认一致）
  CAOYUANYUN_PROXY_API   代理提取 API，每个号执行前取一个新 IP
  CAOYUANYUN_PROXY       固定代理（没配 PROXY_API 时对所有号生效）
  CAOYUANYUN_DEBUG       默认 false

依赖：requests pycryptodome pillow numpy
      用 socks5 代理还需要：pysocks
定时建议：0 8 * * *（每天 8 点一次）
"""

import base64
import hashlib
import json
import os
import random
import re
import socket
import string
import sys
import threading
import time
import uuid
from urllib.parse import quote

import requests

try:
    from Crypto.Cipher import AES
except ImportError:
    print("缺少依赖 pycryptodome：pip install pycryptodome")
    sys.exit(1)

try:
    from PIL import Image
    import numpy as np
    import io
except ImportError:
    print("缺少依赖 pillow/numpy：pip install pillow numpy")
    sys.exit(1)

# ================= 常量（来自 APK） =================
API = "https://ya.iyunxh.com"
BASE = "https://cyy.nmgcyy.com.cn"
STATIC = "https://static2-ya.iyunxh.com"
H5 = "https://nmgrb.y-h5.iyunxh.com"

APP_ID = "nmgrb"
APP_UA = "TMProject/4.7.0 (iPhone; iOS 17.0; Scale/3.00)"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) TMAppName/caoyuanyun TMAppName/caoyuanyun tm_language/zh-cn")

LOGIN_PHONE = BASE + "/member/login/memberLogin"
TENANT_URL = STATIC + "/api/aosbase/_auth_h5init/nmgrb.json"
DT_URL = API + "/api/aosbase/_auth_dt"
APPUSER_URL = API + "/api/aosbase/_auth_appuserinit"
USER_INFO_URL = API + "/api/aosbase/user_info"
SIGN_URL = API + "/api/aossignin/ac_sub"
SIGN_TIMES_URL = API + "/api/aossignin/user_times?activity_id=10609043"
TASK_LIST_URL = API + "/api/aosbasemodule/_task_list"
TASK_CREATE_URL = API + "/api/aosbasemodule/task_create"
TASK_DONE_URL = API + "/api/aosbasemodule/task_done"
OPTIONP_LIST_URL = API + "/api/aoslearnfoot/_optionp_list?activity_id=11106679"
OPTIONP_DETAIL_URL = API + "/api/aoslearnfoot/optionp_detail"
CAPTCHA_GET_URL = API + "/api/basemodule/_captcha_get"
CAPTCHA_CHECK_URL = API + "/api/basemodule/_captcha_check"
CAPTCHA_VERIFY_URL = API + "/api/aosbasemodule/intelverifcode_check"
FOOTPRINT_URL = BASE + "/fcpublic/Memberfootprint/addfootprint"
READING_URL = BASE + "/fcpublic/yundian/complateReading"
WITHDRAW_PACKAGE_URL = API + "/api/static_3/aosbasemodule/_withdrawal_package_show/13109571.json"

SIGN_ACTIVITY_ID = 10609043
READ_ACTIVITY_ID = 11106679
DEFAULT_MODULE_ID = "41603"

CAPTCHA_KEY = b"7Pf0cfZPHy1L7PS2PfCfP8r2BGi461LG"
CAPTCHA_IV = b"8RsVKSCH8mQ4l7cu"
CAPTCHA_ALPHA = "twxyz2345678"
CAPTCHA_REFERER = H5 + "/module-study/pass-detail/pass-detail"

ALPHABET36 = "abcdefghijklmnopqrstuvwxyz0123456789"
ALPHABET62 = string.digits + string.ascii_lowercase + string.ascii_uppercase


# ================= 基础工具 =================
_TLS = threading.local()
_PRINT_LOCK = threading.Lock()


def log(msg):
    tag = getattr(_TLS, "tag", "")
    line = f"[{time.strftime('%H:%M:%S')}]{tag} {msg}"
    with _PRINT_LOCK:
        print(line, flush=True)


def dbg(msg):
    if os.getenv("CAOYUANYUN_DEBUG", "false").strip().lower() == "true":
        tag = getattr(_TLS, "tag", "")
        with _PRINT_LOCK:
            print(f"[{time.strftime('%H:%M:%S')}]{tag} [debug] {msg}", flush=True)


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def b64(s):
    return base64.b64encode(s.encode("utf-8")).decode()


def b64e(b):
    return base64.b64encode(b).decode()


def b64d(s):
    return base64.b64decode(s)


def rand_str(n, alphabet=ALPHABET36):
    return "".join(random.choice(alphabet) for _ in range(n))


def pkcs_pad(b):
    pad = 16 - len(b) % 16
    return b + bytes([pad]) * pad


def pkcs_unpad(b):
    if not b:
        return b
    n = b[-1]
    if 0 < n <= 16 and b[-n:] == bytes([n]) * n:
        return b[:-n]
    return b


def aes_encrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pkcs_pad(data))


def aes_decrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return pkcs_unpad(cipher.decrypt(data))


def make_keys():
    ts = str(int(time.time() * 1000))
    rnd = rand_str(16)
    key = md5(b64(md5(ts)) + rnd + rnd)
    return ts, rnd, key


def req_key(ts, rnd):
    return md5(b64(ts) + md5(rnd))[:16].encode()


def req_iv(ts, rnd):
    return md5(b64(rnd) + md5(ts))[:16].encode()


def resp_key(ts, rnd):
    return md5(b64(ts) + md5(ts))[:16].encode()


def resp_iv(ts, rnd):
    return md5(rnd)[:16].encode()


def encrypt_body(plain, keys):
    data = base64.b64encode(aes_encrypt(plain.encode("utf-8"), req_key(keys[0], keys[1]), req_iv(keys[0], keys[1]))).decode()
    return json.dumps({"tm_encrypt_data": data}, ensure_ascii=False)


def decrypt_resp(data, ts, rnd):
    if not data:
        return ""
    raw = aes_decrypt(b64d(data), resp_key(ts, rnd), resp_iv(ts, rnd))
    text = raw.decode("utf-8", "ignore")
    return text.rstrip("\x00").rstrip()


def guid32():
    return rand_str(32, ALPHABET62)


def aas_key(appkey):
    if not appkey:
        return ""
    even = "".join(appkey[i] for i in range(0, len(appkey), 2))
    odd = "".join(appkey[i] for i in range(1, len(appkey), 2))
    return md5(even + odd)


def signature(tenant):
    appid = str(tenant.get("appid", ""))
    g = guid32()
    ts = str(int(time.time() * 1000))
    return f"{appid};{g};{ts};{md5(appid + g + ts + aas_key(str(tenant.get('appkey', ''))))}"


def truthy(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    return str(v).strip().lower() in ("true", "1", "yes")


def code_of(js):
    c = js.get("code", "") if isinstance(js, dict) else ""
    try:
        return int(str(c))
    except Exception:
        return -1


def ok(js):
    return code_of(js) in (0, 200)


def data_of(js):
    d = js.get("data") if isinstance(js, dict) else None
    if isinstance(d, dict):
        return d
    return {}


def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        return {"code": -1, "msg": "响应不是JSON"}


def mask(s):
    if not s:
        return ""
    s = str(s)
    return s if len(s) <= 12 else s[:6] + "..." + s[-6:]


def mask_phone(p):
    if p and len(p) == 11:
        return p[:3] + "****" + p[7:]
    return p


def cut(s, n):
    s = str(s or "")
    return s if len(s) <= n else s[:n] + "..."


# ================= 代理（对齐 APK ProxyConfig） =================
class ProxyConfig:
    """等价于 APK 的 ProxyConfig：解析 http/socks5、认证、标签"""

    def __init__(self, raw="", host=None, port=0, socks=False, user=None, password=None, error=None):
        self.raw = raw or ""
        self.host = host
        self.port = port
        self.socks = socks
        self.user = user
        self.password = password
        self.error = error

    @staticmethod
    def direct():
        return ProxyConfig()

    def is_direct(self):
        return not self.host

    def has_auth(self):
        return bool(self.user)

    def label(self):
        if self.is_direct():
            return "直连"
        s = ("socks5://" if self.socks else "") + f"{self.host}:{self.port}"
        if self.has_auth():
            s += " (认证)"
        return s

    def url(self):
        if self.is_direct():
            return ""
        auth = ""
        if self.has_auth():
            auth = f"{self.user}:{self.password}@"
        return ("socks5://" if self.socks else "http://") + auth + f"{self.host}:{self.port}"

    def to_requests(self):
        """requests 用的 proxies 字典"""
        if self.is_direct():
            return None
        u = self.url()
        return {"http": u, "https": u}

    @staticmethod
    def parse(raw):
        s = (raw or "").strip()
        if not s:
            return ProxyConfig.direct()
        scheme = "http"
        idx = s.find("://")
        if idx > 0:
            scheme = s[:idx].lower()
            s = s[idx + 3:]
        socks = scheme.startswith("socks")
        if not socks and not scheme.startswith("http"):
            return ProxyConfig(raw, error=f"不支持的代理类型: {scheme}")

        auth = None
        at = s.rfind("@")
        if at >= 0:
            auth = s[:at]
            s = s[at + 1:]

        s = re.sub(r"/.*$", "", s)
        colon = s.rfind(":")
        if colon <= 0 or colon == len(s) - 1:
            return ProxyConfig(raw, error="代理格式应为 host:port")
        host = s[:colon].strip()
        port_s = s[colon + 1:].strip()
        try:
            port = int(port_s)
        except ValueError:
            return ProxyConfig(raw, error=f"代理端口不是数字: {port_s}")
        if port <= 0 or port > 65535:
            return ProxyConfig(raw, error=f"代理端口越界: {port}")
        if not host:
            return ProxyConfig(raw, error="代理 host 为空")

        user = password = None
        if auth:
            if ":" in auth:
                user, password = auth.split(":", 1)
            else:
                user = auth
            if socks:
                return ProxyConfig(raw, error="SOCKS5 带认证不可靠，请改用 http://user:pass@host:port")
        return ProxyConfig(raw, host, port, socks, user, password)


def api_wants_socks(url):
    """APK：API 地址里带 protocol=3 或 socks 就按 socks5 处理"""
    m = re.search(r"[?&]protocol=([^&]+)", url or "")
    if not m:
        return False
    v = m.group(1).strip().lower()
    return v == "3" or "socks" in v


def extract_proxy(api_url, timeout=15):
    """等价 APK Cyy.extractProxy：支持 JSON/纯文本，返回 ip:port 或 'ERR:xxx' 或 ''"""
    try:
        r = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout, proxies=None)
        text = (r.text or "").strip()
    except Exception as e:
        dbg(f"代理提取请求失败: {e}")
        return ""
    if not text:
        return ""

    if text.startswith("{"):
        try:
            js = json.loads(text)
        except Exception:
            return ""
        arr = None
        data = js.get("data")
        if isinstance(data, list):
            arr = data
        elif isinstance(data, dict):
            arr = data.get("list") or data.get("data")
        if arr is None:
            arr = js.get("list")
        if isinstance(arr, list) and arr:
            first = arr[0]
            if isinstance(first, dict):
                ip, port = str(first.get("ip", "")), str(first.get("port", ""))
                if ip and port:
                    return f"{ip}:{port}"
            elif isinstance(first, str):
                return first.strip()
            return ""
        msg = str(js.get("message") or js.get("msg") or "")
        return ("ERR:" + msg) if msg else ""

    first_line = text.split("\n")[0].strip()
    return first_line if first_line.find(":") > 0 else ""


def resolve_proxy(account_proxy, api_url, use_proxy=True, tag=""):
    """等价 APK resolveProxy：账号自带代理 > 提取 API > 直连"""
    if not use_proxy:
        return ProxyConfig.direct()
    if account_proxy and account_proxy.strip():
        return ProxyConfig.parse(account_proxy)
    if not api_url:
        return ProxyConfig.direct()

    if tag:
        log(f"🌐 为 {tag} 提取代理 IP")
    got = extract_proxy(api_url)
    if got.startswith("ERR:"):
        log(f"❌ 代理提取被拒绝: {got[4:]}")
        return ProxyConfig(raw=got, error=got[4:])
    if not got:
        log("❌ 代理提取失败：接口没有返回可用 IP")
        return ProxyConfig(raw=got, error="代理提取失败")
    if not (got.startswith("http") or got.startswith("socks")):
        got = ("socks5://" if api_wants_socks(api_url) else "http://") + got
    p = ProxyConfig.parse(got)
    if p.error:
        log(f"⚠️ 提取到的代理不可用({got}): {p.error}")
        return ProxyConfig.direct()
    log(f"🌐 分配代理 {p.label()}")
    return p


def verify_ip(proxy=None, timeout=10):
    """等价 APK verifyIp：读取出口 IP"""
    try:
        sess = requests.Session()
        p = proxy.to_requests() if isinstance(proxy, ProxyConfig) else None
        r = sess.get("https://myip.ipip.net", headers={"User-Agent": UA}, timeout=timeout, proxies=p)
        m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", r.text or "")
        return m.group(1) if m else ""
    except Exception as e:
        dbg(f"出口 IP 探测失败: {e}")
        return ""



class Cyy:
    def __init__(self, phone, password, proxy=None):
        self.phone = phone
        self.password = password
        if isinstance(proxy, str):
            proxy = ProxyConfig.parse(proxy)
        self.proxy = proxy if isinstance(proxy, ProxyConfig) else ProxyConfig.direct()
        self.member_token = ""
        self.member_id = 0
        self.tenant = {}
        self.api_dt = ""
        self.access_token = ""
        self.user_id = 0
        self.s = requests.Session()
        self.s.headers.update({"Accept-Encoding": "gzip"})
        if not self.proxy.is_direct():
            if self.proxy.socks:
                try:
                    import socks  # noqa: F401  (requests[socks])
                except ImportError:
                    raise RuntimeError("socks5 代理需要先安装 pysocks：pip install pysocks")
            self.s.proxies = self.proxy.to_requests()
        self.s.headers["User-Agent"] = UA

    # ---------- HTTP ----------
    def http_get(self, url, headers=None, timeout=30):
        try:
            r = self.s.get(url, headers=headers or {}, timeout=timeout)
            dbg(f"GET {url} -> {r.status_code}")
            return r.text
        except Exception as e:
            dbg(f"GET {url} 失败 {e}")
            return ""

    def http_post(self, url, headers=None, body="", timeout=30):
        try:
            r = self.s.post(url, data=body.encode("utf-8"), headers=headers or {}, timeout=timeout)
            dbg(f"POST {url} -> {r.status_code} {r.text[:120]}")
            return r.text
        except Exception as e:
            dbg(f"POST {url} 失败 {e}")
            return ""

    def http_bytes(self, url, headers=None, timeout=30):
        try:
            r = self.s.get(url, headers=headers or {}, timeout=timeout)
            return r.content
        except Exception as e:
            dbg(f"下载 {url} 失败 {e}")
            return b""

    # ---------- 1. 登录 ----------
    def login(self):
        log(f"🔐 手机号登录 {mask_phone(self.phone)}")
        hex16 = uuid.uuid4().hex[:16]
        mac = ":".join("%02X" % random.randint(0, 255) for _ in range(6))
        body = {
            "mobile": self.phone,
            "state": 2,
            "site_code": "00000000000000000000000000000000",
            "code": "",
            "password": self.password,
            "channel_sources": "Default",
            "device_num": hex16,
            "device_no": hex16,
            "imei_no": "",
            "mac_no": mac,
        }
        keys = make_keys()
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "okhttp/3.12.13",
            "tmencrypt": "1",
            "tmtimestamp": keys[0],
            "tmrandomnum": keys[1],
            "tmencryptkey": keys[2],
        }
        resp = parse_json(self.http_post(LOGIN_PHONE, headers, encrypt_body(json.dumps(body, ensure_ascii=False), keys)))
        if str(resp.get("code")) != "200":
            raise RuntimeError(f"登录失败: {resp.get('msg') or resp.get('code')}")
        plain = decrypt_resp(resp.get("data", ""), keys[0], keys[1])
        info = parse_json(plain)
        token = info.get("token", "")
        if not token:
            raise RuntimeError("登录未返回 token")
        mi = info.get("member_info") or {}
        self.member_token = token
        self.member_id = int(mi.get("member_id", 0) or 0)
        log(f"✅ 登录成功 token={mask(token)} member_id={self.member_id}")

    # ---------- 2. 租户 ----------
    def load_tenant(self):
        resp = parse_json(self.http_get(TENANT_URL, {"Access-T-Id": "2433", "Access-T-Id-In": "2433", "User-Agent": UA}))
        if not ok(resp):
            raise RuntimeError(f"租户初始化失败: {resp.get('msg')}")
        self.tenant = parse_json(base64.b64decode(resp.get("data", "")).decode("utf-8"))
        log(f"🏢 租户 appid={self.tenant.get('appid')} t_id={self.tenant.get('t_id', 2433)}")

    def t_id(self):
        return str(self.tenant.get("t_id", 2433))

    def t_id_in(self):
        return str(self.tenant.get("t_id_in", 2433))

    # ---------- 3. 设备令牌 ----------
    def load_device_token(self):
        dt = str(int(time.time() * 1000)) + str(random.randint(100000000, 999999999))
        resp = parse_json(self.http_get(DT_URL, {
            "Access-T-Id": self.t_id(),
            "Access-T-Id-In": self.t_id_in(),
            "Access-Api-Unique-Token": "1",
            "Access-Api-Dt": dt,
            "User-Agent": UA,
        }))
        if not ok(resp):
            raise RuntimeError(f"获取设备令牌失败: {resp.get('msg')}")
        data = str(resp.get("data", ""))
        if len(data) < 68:
            raise RuntimeError(f"设备令牌异常(长度 {len(data)})")
        self.api_dt = data[32:68]
        log(f"📱 设备令牌 {mask(self.api_dt)}")

    # ---------- 4. 头 ----------
    def headers(self, with_user=True):
        h = {
            "Access-T-Id": self.t_id(),
            "Access-T-Id-In": self.t_id_in(),
            "Access-Api-Unique-Token": "1",
            "Access-Wxclient-Type": "wx_app",
            "Access-Api-Signature": signature(self.tenant),
            "Access-Api-Dt": self.api_dt,
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Origin": H5,
            "Referer": H5 + "/",
        }
        if with_user and self.access_token:
            h["Access-Token"] = self.access_token
            h["Access-User-Id"] = str(self.user_id)
        return h

    def api_get(self, url):
        return parse_json(self.http_get(url, self.headers()))

    def api_post(self, url, obj):
        return parse_json(self.http_post(url, self.headers(), json.dumps(obj, ensure_ascii=False)))

    # ---------- 5. appuserinit ----------
    def app_user_init(self):
        items = {
            "app_user_token": self.member_token,
            "appid": str(self.tenant.get("appid", "")),
            "noncestr": guid32(),
            "phone": "",
            "portrait_url": "/images/default/head.jpg",
            "timestamp": str(int(time.time())),
            "user_id": "0",
            "user_name": "微信用户",
            "wx_openid": "",
            "wx_unionid": "",
        }
        qs = "&".join(f"{k}={quote(str(items[k]), safe='')}" for k in sorted(items.keys()))
        sign = md5(qs + "&appkey=" + str(self.tenant.get("appkey", "")))
        body = dict(items)
        body["signature"] = sign
        resp = parse_json(self.http_post(APPUSER_URL, self.headers(False), json.dumps(body, ensure_ascii=False)))
        if not ok(resp):
            raise RuntimeError(f"appuserinit 失败: {resp.get('msg')}")
        d = data_of(resp)
        self.access_token = d.get("access_token", "") or ""
        inner = d.get("data") or {}
        self.user_id = int(inner.get("user_id", 0) or 0)
        if not self.access_token:
            raise RuntimeError("未识别 access_token")
        log(f"✅ access_token {mask(self.access_token)} user_id={self.user_id}")

    # ---------- 6. 签到 ----------
    def do_signin(self):
        try:
            r = self.api_get(SIGN_TIMES_URL)
            if ok(r):
                log(f"📅 签到余量 day_remain={data_of(r).get('day_remain', '-')}")
        except Exception:
            pass
        r = self.api_post(SIGN_URL, {
            "id": SIGN_ACTIVITY_ID,
            "afs_tokenid": "",
            "collect_info": "",
            "longitude": 0,
            "latitude": 0,
        })
        if ok(r):
            gold = data_of(r).get("gold")
            log(f"✅ 签到成功 +{gold} 金币")
            return f"签到+{gold}"
        msg = str(r.get("msg", ""))
        if str(r.get("code")) == "1007" or "已签" in msg:
            log("📅 今日已签到")
            return "今日已签到"
        log(f"⚠️ 签到: {msg or r.get('code')}")
        return "签到失败"

    # ---------- 7. 金币 ----------
    def get_gold(self):
        try:
            r = self.api_get(USER_INFO_URL)
            if ok(r):
                return int(data_of(r).get("gold", 0) or 0)
        except Exception as e:
            log(f"⚠️ 金币查询失败: {e}")
        return -1

    def withdraw_packages(self):
        try:
            r = parse_json(self.http_get(WITHDRAW_PACKAGE_URL, {"User-Agent": UA, "Referer": H5 + "/"}))
            arr = r.get("data")
            out = []
            if isinstance(arr, list):
                for it in arr:
                    out.append((it.get("title", ""), it.get("price", "")))
            return out
        except Exception:
            return []

    # ---------- 8. 任务 ----------
    def do_tasks(self, read_seconds=60, max_tasks=0):
        lr = self.api_get(OPTIONP_LIST_URL)
        if not ok(lr):
            return "任务活动获取失败"
        arr = lr.get("data")
        if not isinstance(arr, list) or not arr:
            return "无任务活动"
        opt = arr[0]
        oid = str(opt.get("id", ""))
        mid = str(opt.get("m_id", DEFAULT_MODULE_ID))
        log(f"🎯 任务活动 {opt.get('title')} option_id={oid} 任务数={opt.get('task_num')}")

        d = self.api_get(OPTIONP_DETAIL_URL + "?id=" + quote(oid))
        if ok(d):
            dd = data_of(d)
            done = int(dd.get("user_done_num", 0) or 0)
            undone = int(dd.get("user_undone_num", 0) or 0)
            log(f"📊 今日已完成 {done}/{done + undone}")

        tl = self.api_get(f"{TASK_LIST_URL}?offset=0&count=30&module_id={mid}&activity_id={oid}")
        if not ok(tl):
            return "任务列表获取失败"
        tasks = tl.get("data")
        if not isinstance(tasks, list):
            return "任务列表为空"
        todo = [t for t in tasks if t and not truthy(t.get("user_done"))]
        log(f"📋 共 {len(tasks)} 个任务，未完成 {len(todo)} 个")
        if not todo:
            return "今日任务已全部完成"

        limit = len(todo) if max_tasks <= 0 else min(max_tasks, len(todo))
        done_cnt = 0
        for i, t in enumerate(todo[:limit]):
            tid = str(t.get("id", ""))
            title = str(t.get("title", ""))
            log(f"[+] 任务 #{tid} {cut(title, 24)}")
            try:
                if self.run_one_task(t, tid, title, read_seconds):
                    done_cnt += 1
            except Exception as e:
                log(f"  ✗ {e}")
            if i < limit - 1:
                time.sleep(random.uniform(1.0, 3.0))
        return f"完成 {done_cnt} 个任务"

    @staticmethod
    def article_id_of(url):
        idx = str(url).find("ArticleDetail")
        if idx < 0:
            return 0
        digits = ""
        i = idx + 13
        while i < len(url) and url[i].isdigit():
            digits += url[i]
            i += 1
        return int(digits) if digits else 0

    def run_one_task(self, task, tid, title, read_seconds):
        rule = task.get("rule") or {}
        if isinstance(rule, str):
            rule = parse_json(rule)
        news_id = str(rule.get("news_id", "")).strip()
        article_id = self.article_id_of(news_id)
        info = rule.get("content_info") or {}
        title2 = str(info.get("title") or "") or title

        rec = data_of(self.api_post(TASK_CREATE_URL, {"task_id": tid})).get("task_record_id", "")
        log(f"  记录 {rec or '-'}")
        if not rec:
            log("  ✓ 无任务记录，跳过")
            return True

        if article_id > 0:
            try:
                fp = self.footprint(article_id, title2, news_id)
                if fp.get("code") == 200:
                    log("  打卡成功")
                else:
                    m = str(fp.get("msg", ""))
                    log("  打卡：今天已打过" if "重复" in m else f"  打卡(忽略): {cut(m, 40)}")
            except Exception as e:
                log(f"  打卡失败(忽略): {cut(e, 40)}")

        self.simulate_read(news_id, read_seconds)

        if article_id > 0:
            try:
                cr = self.complete_reading(article_id)
                if cr.get("code") == 200:
                    log("  阅读完成上报成功")
                else:
                    log(f"  上报(忽略): {cut(cr.get('msg'), 40)}")
            except Exception as e:
                log(f"  上报失败(忽略): {cut(e, 40)}")

        tokenid = ""
        for attempt in (1, 2):
            if attempt == 1:
                log("  刷新 access_token")
            else:
                log("  🔁 重试验证码")
            try:
                self.app_user_init()
                tokenid = Captcha(self).solve()
                if tokenid:
                    break
            except Exception as e:
                log(f"  ⚠️ 滑块失败: {e}")

        if not tokenid:
            log("  ⚠️ 未取得验证 token，跳过该任务")
            return False

        r = self.api_post(TASK_DONE_URL, {
            "task_record_id": rec,
            "collect_info": "",
            "afs_tokenid": tokenid,
            "device_token": "",
        })
        if ok(r):
            opt = data_of(r).get("option") or {}
            log(f"  ✓ 完成！奖励 {opt.get('goods_title') or opt.get('title') or '-'}")
            return True
        log(f"  ✗ 提交失败: {cut(r.get('msg') or r.get('code'), 60)}")
        return False

    def footprint(self, article_id, title, news_id):
        keys = make_keys()
        param = json.dumps({"h5url": news_id, "type": 1}, ensure_ascii=False)
        body = {
            "app_id": "fcinformation",
            "native": 1,
            "src": "NewsI004WKDetailViewController",
            "paramStr": param,
            "title": title,
            "pic": "",
            "member_id": self.member_id,
            "intro": " ",
            "article_id": article_id,
            "article_type": "1",
            "wwwFolder": "wwwFolder",
        }
        h = {
            "token": self.member_token,
            "User-Agent": APP_UA,
            "Content-Type": "application/json",
            "tmencrypt": "1",
            "tmencryptkey": keys[2],
            "tmencryptkeynew": keys[2],
            "tmrandomnum": keys[1],
            "tmrandomnumnew": keys[1],
            "tmtimestamp": keys[0],
            "tmtimestampnew": keys[0],
        }
        return parse_json(self.http_post(FOOTPRINT_URL, h, json.dumps(body, ensure_ascii=False)))

    def complete_reading(self, article_id):
        body = {"content_id": article_id, "member_id": self.member_id}
        h = {
            "token": self.member_token,
            "guid": str(uuid.uuid4()),
            "User-Agent": APP_UA,
            "Content-Type": "application/json",
        }
        return parse_json(self.http_post(READING_URL, h, json.dumps(body, ensure_ascii=False)))

    def simulate_read(self, news_id, read_seconds):
        sec = read_seconds
        if sec <= 0:
            m = re.search(r"second=(\d+)", news_id)
            sec = int(m.group(1)) if m else 60
        if news_id.startswith("http"):
            try:
                link = news_id
                if "#" in news_id:
                    head, tail = news_id.split("#", 1)
                    tail = re.sub(r"(ArticleDetail/\d+)/(undefined|\d+)", r"\1/%d" % self.member_id, tail)
                    if "fc_token=" not in tail:
                        tail += ("&" if "?" in tail else "?") + "fc_token=" + self.member_token
                    link = head + "#" + tail
                self.http_get(link, {"User-Agent": APP_UA, "Accept-Language": "zh-Hans-CN;q=1"})
                log("  已打开文章页")
            except Exception:
                log("  文章页访问失败(忽略)")
        log(f"  开始阅读 {sec} 秒")
        left = sec
        while left > 0:
            time.sleep(min(2, left))
            left -= 2
        log("  阅读结束")

    # ---------- 9. 主流程 ----------
    def run(self, signin=True, do_tasks=True, read_seconds=3, max_tasks=0):
        ip = verify_ip(self.proxy)
        if ip:
            log(f"🌐 出口 IP {ip}（{self.proxy.label()}）")
        else:
            log(f"⚠️ 出口 IP 探测失败（{self.proxy.label()}）")

        self.login()
        self.load_tenant()
        self.load_device_token()
        self.app_user_init()

        parts = []
        if signin:
            parts.append("签到:" + self.do_signin())
        if do_tasks:
            parts.append("任务:" + self.do_tasks(read_seconds, max_tasks))

        gold = self.get_gold()
        if gold >= 0:
            log(f"💰 当前金币 {gold}")
            parts.append(f"金币:{gold}")
            pkgs = self.withdraw_packages()
            if pkgs:
                txt = " ".join(f"{t}({p})" for t, p in pkgs[:12])
                log(f"🏦 兑现档位 {txt}")
        return "  ".join(parts)


# ================= 滑块验证码 =================
class Captcha:
    def __init__(self, cyy):
        self.cyy = cyy

    @staticmethod
    def _rand(n):
        return "".join(random.choice(CAPTCHA_ALPHA) for _ in range(n))

    @staticmethod
    def _enc(obj, urlencode=False):
        raw = aes_encrypt(json.dumps(obj, ensure_ascii=False).encode("utf-8"), CAPTCHA_KEY, CAPTCHA_IV)
        s = base64.b64encode(raw).decode()
        return quote(s, safe="") if urlencode else s

    def solve(self):
        ts = int(time.time())
        once = self._rand(10)
        sign_obj = {"once": once, "referer": CAPTCHA_REFERER, "timestamp": ts, "type": "1"}
        url = (f"{CAPTCHA_GET_URL}?once={quote(once, safe='')}&referer={quote(CAPTCHA_REFERER, safe='')}"
               f"&timestamp={ts}&type=1&signature={self._enc(sign_obj, True)}")
        log("  [验证码] 取图")
        r = parse_json(self.cyy.http_get(url, self.cyy.headers()))
        if not ok(r):
            raise RuntimeError(f"获取验证码失败: {r.get('msg')}")
        d = data_of(r)
        token, bg_url, block_url = d.get("token", ""), d.get("background", ""), d.get("block", "")
        if not (token and bg_url and block_url):
            raise RuntimeError("验证码数据不完整")

        log("  [验证码] 下载拼图")
        hh = {"User-Agent": APP_UA}
        bg_bytes = self.cyy.http_bytes(bg_url, hh)
        blk_bytes = self.cyy.http_bytes(block_url, hh)
        bg = Image.open(io.BytesIO(bg_bytes)).convert("RGB")
        blk = Image.open(io.BytesIO(blk_bytes)).convert("RGBA")
        W, H = bg.size
        w, h = blk.size
        if w > W:
            raise RuntimeError("拼图尺寸异常")
        log(f"  [验证码] 背景 {W}x{H}，拼图 {w}x{h}")

        bg_arr = np.asarray(bg, dtype=np.float64)
        blk_arr = np.asarray(blk, dtype=np.float64)
        cands = self.locate(bg_arr, blk_arr)
        log(f"  [验证码] 缺口候选 " + ", ".join(f"{n}={x}" for n, x in cands))
        for name, x in cands:
            if x + 60 > W - 1:
                log(f"  [*] 跳过 {name} x={x}（过于靠边）")
                continue
            log(f"  [*] 尝试 {name} x={x}")
            track = self._build_track(x)
            payload = {"x": x, "width": W, "track": track}
            body = {"token": token, "data": self._enc(payload), "referer": CAPTCHA_REFERER, "type": "1"}
            r2 = parse_json(self.cyy.http_post(CAPTCHA_CHECK_URL, self.cyy.headers(), json.dumps(body, ensure_ascii=False)))
            d2 = r2.get("data") or {}
            if not ok(r2) or not d2 or not truthy(d2.get("result")):
                log(f"    [x] {cut(r2.get('msg'), 50)}")
                continue
            validate = d2.get("token", "")
            log("    [OK] 滑块通过")
            body3 = {"validate": validate, "verif_type": 3, "afs_uuid": "", "source": "yundian"}
            r3 = parse_json(self.cyy.http_post(CAPTCHA_VERIFY_URL, self.cyy.headers(), json.dumps(body3, ensure_ascii=False)))
            d3 = r3.get("data") or {}
            tokenid = d3.get("tokenid", "") if isinstance(d3, dict) else ""
            if ok(r3) and tokenid:
                log(f"    [OK] afs_tokenid {mask(tokenid)}")
                return tokenid
            log(f"    [warn] 智能验证: {cut(r3.get('msg'), 50)}")
        raise RuntimeError("全部候选位置验证失败")

    @staticmethod
    def locate(bg_arr, blk_arr):
        """缺口横向位置识别，返回 [(名称, x), ...]"""
        W = bg_arr.shape[1]
        H = bg_arr.shape[0]
        w = blk_arr.shape[1]
        alpha = blk_arr[:, :, 3] / 255.0
        mask = alpha > 0.02
        if not mask.any():
            raise RuntimeError("拼图没有有效像素")
        rows = np.where(mask.any(axis=1))[0]
        y0, y1 = int(rows.min()), int(rows.max())
        y1 = min(y1, H - 1)

        t_pix = blk_arr[:, :, :3] * alpha[:, :, None]
        t_norm = float((alpha * (blk_arr[:, :, :3] ** 2).sum(axis=2)).sum())

        region = bg_arr[y0:y1 + 1]
        a = alpha[y0:y1 + 1]
        tp = t_pix[y0:y1 + 1]
        scores = []
        for x in range(0, W - w + 1):
            sub = region[:, x:x + w, :]
            d8 = float((a * (sub ** 2).sum(axis=2)).sum())
            d9 = float((a * (sub * tp).sum(axis=2)).sum())
            scores.append(d9 / np.sqrt(d8 * t_norm) if d8 > 0 and t_norm > 0 else 0.0)
        scores = np.array(scores)
        ncc_max_x = int(np.argmax(scores))

        # 亮度最低列窗口
        col_mean = bg_arr.sum(axis=2).mean(axis=0)
        win = min(w, 20)
        best_x, best_v = 0, float("inf")
        for x in range(0, max(1, W - win + 1)):
            v = float(col_mean[x:x + win].mean())
            if v < best_v:
                best_v, best_x = v, x

        # 背景自身的"空白列"：用 alpha 图在背景上找最像模板的地方（NCC 最小值作为兜底）
        ncc_min_x = int(np.argmin(scores)) if len(scores) else 0

        # 暗块掩膜：缺口通常比周围暗，取"掩膜内亮度显著低于掩膜外"的位置
        bright = bg_arr.sum(axis=2) / 3.0
        dark_x, dark_best = 0, -1e9
        for x in range(0, W - w + 1):
            win_b = bright[y0:y1 + 1, x:x + w]
            inside = float((a * win_b).sum()) / max(1e-6, float(a.sum()))
            outside = float(win_b.mean())
            diff = outside - inside
            if diff > dark_best:
                dark_best, dark_x = diff, x

        return [("ncc_max", ncc_max_x), ("bright_min", best_x), ("dark_max", dark_x), ("ncc_min", ncc_min_x)]

    @staticmethod
    def _build_track(target):
        v = random.uniform(1.4, 1.8)
        total = float(target)
        fast_end = 0.72 * total
        x = 0.0
        track = []
        while x < total - 0.5 and len(track) < 99:
            if x < fast_end:
                x += v + random.uniform(-0.2, 0.2)
            else:
                x += max(0.2, (total - x) * v / (total - fast_end + 1.0)) + random.uniform(-0.15, 0.15)
            track.append({"x": round(x, 1), "y": 0, "time": 100})
        if not track:
            track.append({"x": target, "y": 0, "time": 100})
        else:
            track[-1]["x"] = target
        return track


# ================= 入口 =================
def parse_accounts(raw):
    """手机号#密码 或 手机号#密码#代理"""
    out = []
    for item in re.split(r"[&\n]", raw):
        item = item.strip()
        if not item:
            continue
        if "#" not in item:
            log(f"账号格式错误（应为 手机号#密码）: {cut(item, 20)}")
            continue
        parts = item.split("#", 2)
        phone = parts[0].strip()
        pwd = parts[1].strip() if len(parts) > 1 else ""
        own_proxy = parts[2].strip() if len(parts) > 2 else ""
        if phone and pwd:
            out.append((phone, pwd, own_proxy))
        else:
            log(f"账号密码为空: {cut(phone, 12)}")
    return out


def notify(title, content):
    try:
        if "send" in globals():
            send(title, content)
        else:
            with _PRINT_LOCK:
                print(f"\n📢 {title}\n{content}\n")
    except Exception:
        with _PRINT_LOCK:
            print(f"\n📢 {title}\n{content}\n")


_PROXY_API_LOCK = threading.Lock()


def run_account(idx, total, phone, pwd, own_proxy, cfg):
    _TLS.tag = f" [{mask_phone(phone)}]"
    log(f"▶ 账号 {idx}/{total} 开始")
    pcfg = ProxyConfig.direct()
    try:
        if cfg["use_proxy"]:
            if own_proxy or cfg["proxy_api"]:
                # 同一个提取接口串行取号，避免并发拿到同一个 IP
                with _PROXY_API_LOCK:
                    pcfg = resolve_proxy(own_proxy, cfg["proxy_api"], True, mask_phone(phone))
                if pcfg.error:
                    raise RuntimeError(pcfg.error)
            elif cfg["proxy"]:
                pcfg = ProxyConfig.parse(cfg["proxy"])
                if pcfg.error:
                    raise RuntimeError(pcfg.error)
                log(f"🌐 固定代理 {pcfg.label()}")
        c = Cyy(phone, pwd, pcfg)
        summary = c.run(signin=cfg["signin"], do_tasks=cfg["do_tasks"],
                        read_seconds=cfg["read_seconds"], max_tasks=cfg["max_tasks"])
        log("✅ 账号完成")
        return True, f"✅ {mask_phone(phone)} {summary}"
    except Exception as e:
        log(f"❌ 账号失败: {e}")
        return False, f"❌ {mask_phone(phone)} {e}"
    finally:
        _TLS.tag = ""


def run_all(accounts, cfg):
    """按并发数跑完所有账号，返回 [(ok, 结果文案)]"""
    parallel = max(1, min(cfg["parallel"], len(accounts)))
    results = [None] * len(accounts)

    def worker(i):
        results[i] = run_account(i + 1, len(accounts), accounts[i][0], accounts[i][1], accounts[i][2], cfg)

    if parallel <= 1:
        for i in range(len(accounts)):
            worker(i)
            if i < len(accounts) - 1:
                log("⏳ 2 秒后处理下一个账号")
                time.sleep(2)
        return results

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel, thread_name_prefix="cyy") as pool:
        futures = [pool.submit(worker, i) for i in range(len(accounts))]
        concurrent.futures.wait(futures)
    return results


def main():
    with _PRINT_LOCK:
        print("=" * 56)
        print("🌾 草原云 自动签到/阅读任务（青龙版）")
        print("=" * 56)

    raw = os.getenv("CAOYUANYUN_ACCOUNTS", "").strip()
    if not raw:
        with _PRINT_LOCK:
            print("❌ 未配置账号，请设置环境变量 CAOYUANYUN_ACCOUNTS")
            print("   格式: 手机号#密码&手机号#密码")
        return

    accounts = parse_accounts(raw)
    if not accounts:
        with _PRINT_LOCK:
            print("❌ 没有有效账号")
        return

    def env_int(name, default):
        try:
            return int(os.getenv(name, str(default)).strip())
        except ValueError:
            return default

    cfg = {
        "proxy": os.getenv("CAOYUANYUN_PROXY", "").strip(),
        "proxy_api": os.getenv("CAOYUANYUN_PROXY_API", "").strip(),
        "signin": os.getenv("CAOYUANYUN_SIGNIN", "true").strip().lower() == "true",
        "do_tasks": os.getenv("CAOYUANYUN_DO_TASKS", "true").strip().lower() == "true",
        "read_seconds": env_int("CAOYUANYUN_READ_SECONDS", 3),
        "max_tasks": env_int("CAOYUANYUN_MAX_TASKS", 0),
        "parallel": env_int("CAOYUANYUN_PARALLEL", 3),
    }
    cfg["use_proxy"] = bool(cfg["proxy"] or cfg["proxy_api"])

    with _PRINT_LOCK:
        print(f"📧 共 {len(accounts)} 个账号 | 并发 {cfg['parallel']} | 签到={cfg['signin']} "
              f"任务={cfg['do_tasks']} 阅读={cfg['read_seconds']}s 上限={cfg['max_tasks'] or '全部'}")
        print(f"🌐 代理: {cfg['proxy_api'] and '每号提取API' or (cfg['proxy'] or '直连')}")
        print("=" * 56)

    results = run_all(accounts, cfg)
    results = [r for r in results if r]

    success = sum(1 for r in results if r[0])
    with _PRINT_LOCK:
        print(f"\n{'='*56}\n📊 完成 {success}/{len(accounts)} 个账号\n{'='*56}")
    notify("草原云任务完成", f"成功 {success}/{len(accounts)}\n" + "\n".join(r[1] for r in results))


if __name__ == "__main__":
    main()


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