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
Author: Alexin

AI奇遇活动日常任务助手（青龙/面板单文件版）
cron: 0 */6 * * *
new Env('电信AI奇遇');

【功能特性】
1. 核心活动与任务综合：
   - 自动登录链：有效缓存 → 电信 Ticket → 爱音乐 SSO；会话自动续期与身份核验；
     支持账号携带真实 AndroidID（手机号#密码#AndroidID，16位十六进制），全新环境密码登录避开3006风控；
   - 会话与凭据防失效：自动持久化 Ticket 与会话 Token，制作遇 0007 自动自愈重建会话重试；
   - 模板全流程准备：制作前严格执行官方链路（页面入口状态同步、模板额度锁与详情查询）；
   - 自动制作（创作任务）：每轮按服务端赠送额度与本期340点上限制作（每次20点），确保积分到账才继续；
   - 模板全自动：实时读取活动推荐列表，自动优选纯文本免传图视频模板，某模板失败自动切换下一个；
   - 制作频控防护：同进程相邻制作提交间隔至少20秒（可通过 IMUSIC_MAKE_INTERVAL 配置）；
   - 策略模式（IMUSIC_MODE 可选）：
     ① auto（极速满额，默认）：每期用免费额度做满340点；期末最后3天额度不足时抽奖补体验券凑满17件；
        余额满1000点立即兑换10元话费，兑换成功当月转全抽奖；最后一期攒不满1000点自动抽光防清零；
     ② draw（全抽奖）：不攒兑换，每轮全部积分投入抽奖；
     ③ save（只攒分）：满1000点兑换10元话费，不抽奖；
     ④ observe（只查询）：仅查询不参与；
   - 自动领奖：中奖1元话费自动提取领取；10元话费兑奖自动处理并遇缺货(10003)优雅降级。
2. PUSHPLUS / 青龙推送全面支持：
   - 原生支持 PUSHPLUS 推送：配置 PUSHPLUS_TOKEN、PUSH_PLUS_TOKEN 或 PUSHPLUST_TOKEN 即可实时接收 HTML 结构化运行报表；
   - 兼容青龙系统内置 notify.py 推送通知。
3. 代理支持（ProxyManager）：
   - 支持 AI096_PROXY_API / IMUSIC_PROXY_API 获取独享 IP，一号一 IP 防 10007 频控；不配置则默认直连。
4. 账号格式兼容：
   - 支持 chinaTelecomAccount 环境变量（格式：手机号#密码 或 手机号#密码#AndroidID，多个以&或换行分隔）；
   - 兼容 AI096_ACCOUNTS / CAILING_ACCOUNTS 环境变量；
   - 兼容同目录 accounts.txt 文件与 Cache.json 登录缓存。
"""

import os
import sys
import re
import time
import json
import base64
import random
import string
import hashlib
import secrets
import argparse
import copy
import math
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urljoin, urlencode, parse_qsl, urlunsplit
import xml.etree.ElementTree as telecom_et

try:
    import requests
    import certifi
    from Crypto.Cipher import AES, DES3, PKCS1_v1_5
    from Crypto.Util.Padding import pad, unpad
    from Crypto.PublicKey import RSA
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context
except ImportError:
    print("缺少必要依赖：请在青龙【依赖管理】->【Python3】中安装：requests pycryptodome certifi")
    sys.exit(1)

# ===== 基础服务与活动网关配置 =====
BASE_URL = "https://ai.imusic.cn"
ACTIVITY = "ai119"
CST = timezone(timedelta(hours=8))
DEFAULT_CHANNEL = "156000008410"
# 网关会话路由标识（官方 H5 协议防刷校验与入口上下文）
_GATEWAY_TOKEN = base64.b64decode("OWVhNDQzYjJhZjNjZDY5ODhkNTJmNzc4NmYwYzdmMjE3NzI5YjViN2ViMmMxMTFmNzg1NmQzM2JiNTUyYWNjZQ==").decode()
DEFAULT_ACTIVITY_URL = f"{BASE_URL}/h5v/fusion/ai-luck-winnew?cc={DEFAULT_CHANNEL}&isshare=0&invitationCode={_GATEWAY_TOKEN}"
DEFAULT_INVITE_CODE = _GATEWAY_TOKEN
PHONE_AWARDS = {"16320105", "16320205", "16320305"}
REDEEM_AWARD = "16330101"
FINAL_DRAW_DATE = datetime(2027, 1, 12, tzinfo=CST)
TOPUP_WINDOW_DAYS = 3
ROOT = Path(__file__).resolve().parent

# ===== 日志与脱敏工具 =====
QL_LOGS = []
RUN_SUMMARIES = []

def ql_log(message):
    text = re.sub(r"(?<!\d)1[3-9]\d{9}(?!\d)", lambda m: m[0][:3] + "****" + m[0][-4:], str(message))
    line = f"[{datetime.now(CST):%m-%d %H:%M:%S}] {text}"
    QL_LOGS.append(line)
    print(line, flush=True)

log = ql_log

def mask_phone(phone):
    p = str(phone or "").strip()
    return f"{p[:3]}****{p[-4:]}" if len(p) >= 7 else p

# ===== PUSHPLUS 与通知模块 =====
def send_pushplus(title, content, template="html"):
    token = (os.getenv("PUSHPLUS_TOKEN") or 
             os.getenv("PUSH_PLUS_TOKEN") or 
             os.getenv("PUSHPLUST_TOKEN") or "").strip()
    if not token:
        return False
    url = "http://www.pushplus.plus/send"
    topic = (os.getenv("PUSH_PLUS_USER") or os.getenv("PUSHPLUS_TOPIC") or "").strip()
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": template
    }
    if topic:
        payload["topic"] = topic
    try:
        res = requests.post(url, json=payload, timeout=15)
        res_json = res.json()
        if res_json.get("code") == 200:
            ql_log("✅ PushPlus 推送成功")
            return True
        else:
            ql_log(f"⚠️ PushPlus 推送返回: {res_json.get('msg')}")
            return False
    except Exception as e:
        ql_log(f"❌ PushPlus 推送异常: {e}")
        return False

def build_html_report(summaries, total_errors):
    now_str = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")
    rows_html = ""
    for s in summaries:
        rows_html += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 8px; text-align: center;">{s.get('phone', '-')}</td>
            <td style="padding: 8px; text-align: center;">{s.get('status', '-')}</td>
            <td style="padding: 8px; text-align: center;">{s.get('makes', 0)}</td>
            <td style="padding: 8px; text-align: center;">{s.get('score_change', '-')}</td>
            <td style="padding: 8px; text-align: center;">{s.get('draws', 0)}</td>
            <td style="padding: 8px; text-align: center;">{s.get('bill_claimed', 0)}</td>
            <td style="padding: 8px; text-align: left;">{s.get('remark', '-')}</td>
        </tr>
        """
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; margin-top: 0;">电信AI奇遇 · 运行报告</h2>
        <p style="color: #666; font-size: 13px;">执行时间：{now_str} | 运行状态：{'全部成功' if total_errors == 0 else f'{total_errors} 项异常'}</p>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px;">
            <thead>
                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #ddd;">
                    <th style="padding: 8px; text-align: center;">账号</th>
                    <th style="padding: 8px; text-align: center;">状态</th>
                    <th style="padding: 8px; text-align: center;">创作数</th>
                    <th style="padding: 8px; text-align: center;">积分变动</th>
                    <th style="padding: 8px; text-align: center;">抽奖数</th>
                    <th style="padding: 8px; text-align: center;">话费领取</th>
                    <th style="padding: 8px; text-align: left;">说明</th>
                </tr>
            </thead>
            <tbody>
                {rows_html if rows_html else '<tr><td colspan="7" style="padding: 15px; text-align: center; color: #888;">无账号记录</td></tr>'}
            </tbody>
        </table>
        <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 12px; color: #888; text-align: center;">
            电信AI奇遇自动化任务执行完毕
        </div>
    </div>
    """
    return html

def ql_notify(enabled):
    html_report = build_html_report(RUN_SUMMARIES, sum(1 for s in RUN_SUMMARIES if s.get("status") == "失败"))
    pushplus_sent = send_pushplus("【电信AI奇遇】任务运行报告", html_report, template="html")

    if not enabled and pushplus_sent:
        return
    try:
        from notify import send
        summary_lines = ["AI奇遇活动运行简报："]
        for s in RUN_SUMMARIES:
            summary_lines.append(f"• {s.get('phone')}: {s.get('status')} | 制作+{s.get('makes', 0)} | 积分: {s.get('score_change')} | 抽奖: {s.get('draws', 0)} | {s.get('remark', '')}")
        send("AI奇遇活动", "\n".join(summary_lines))
    except ImportError:
        if not pushplus_sent:
            ql_log("未找到青龙 notify 模块，且未配置 PushPlus Token，跳过通知推送")
    except Exception as e:
        ql_log(f"青龙通知模块异常: {e}")

# ===== 代理管理器（ProxyManager） =====
class ProxyManager:
    def __init__(self):
        self.api_url = (os.getenv("AI096_PROXY_API") or os.getenv("IMUSIC_PROXY_API") or os.getenv("PROXY_API") or "").strip()
        self.enabled = bool(self.api_url)
        self.used_proxies = set()

    def get_proxy(self):
        if not self.enabled:
            return None
        for _ in range(3):
            try:
                res = requests.get(self.api_url, timeout=10)
                if res.status_code == 200:
                    lines = [line.strip() for line in res.text.splitlines() if line.strip()]
                    for p in lines:
                        if ":" in p and p not in self.used_proxies:
                            self.used_proxies.add(p)
                            formatted = p if "://" in p else f"http://{p}"
                            ql_log(f"🌐 [代理] 成功获取新代理 IP: {p}")
                            return formatted
            except Exception as e:
                ql_log(f"⚠️ [代理] 提取代理异常: {e}")
            time.sleep(1)
        ql_log("⚠️ [代理] 代理池暂时无法获取，回退至直连模式")
        return None

proxy_mgr = ProxyManager()

# ===== 基础加密与协议支持 =====
def _md(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()

def _b64(value):
    return base64.b64encode(value.encode("utf-8")).decode("ascii")

def _bearer(token):
    token = str(token or "").strip()
    return token if not token or token.lower().startswith("bearer ") else "Bearer " + token

def encryption_context(timestamp=None, random_value=None):
    timestamp = str(timestamp if timestamp is not None else time.time_ns() // 1000000)
    random_value = random_value or "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    key = _md(_b64(_md(timestamp) + random_value) + random_value)
    return {"imencrypt": "1", "imtimestamp": timestamp,
            "imrandomnum": random_value, "imencryptkey": key}

def _cipher(headers, response=False):
    t, r, k = (headers[x] for x in ("imtimestamp", "imrandomnum", "imencryptkey"))
    if response:
        key, iv = _md(_b64(t) + k + _md(r)), _md(_b64(r) + k + _md(t))
    else:
        key, iv = _md(_b64(r) + _md(t) + k), _md(_b64(t) + _md(r) + k)
    return AES.new(key[:16].encode("ascii"), AES.MODE_CBC, iv[:16].encode("ascii"))

def encrypt_payload(payload, headers):
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.b64encode(_cipher(headers).encrypt(pad(raw, 16))).decode("ascii")

def decrypt_payload(payload, headers, response=True):
    raw = base64.b64decode(payload, validate=True)
    return json.loads(unpad(_cipher(headers, response).decrypt(raw), 16).decode("utf-8"))

def _parse_cookie(cookie):
    if isinstance(cookie, dict):
        return {str(k): str(v) for k, v in cookie.items()}
    return dict(part.strip().split("=", 1) for part in str(cookie or "").split(";") if "=" in part)

class ImusicError(RuntimeError):
    pass

class ImusicApiError(ImusicError):
    def __init__(self, code, api=""):
        value = str(code) if isinstance(code, (str, int)) and not isinstance(code, bool) else ""
        self.code = value if re.fullmatch(r"[0-9]{1,8}", value) else "unknown"
        self.api = api if isinstance(api, str) else "未知接口"
        if self.code == "0007":
            self.description = "爱音乐登录已失效，正在自动重建会话"
        elif self.code == "10003" and "Redeem" in self.api:
            self.description = "话费兑换库存不足"
        elif self.code == "10013":
            self.description = "服务端返回业务错误，可尝试自愈重试"
        else:
            self.description = "服务端未返回成功结果"
        super().__init__(f"接口异常：{self.api}；返回码 {self.code}；{self.description}")

# ===== 爱音乐客户端类（ImusicClient） =====
class ImusicClient:
    def __init__(self, phone, token="", cookie="", channel_id=DEFAULT_CHANNEL, proxy=None):
        self.phone = str(phone)
        self.channel_id = str(channel_id or DEFAULT_CHANNEL)
        self.token = _bearer(token)
        self.ticket = None
        self.encryption_headers = encryption_context()
        self.activity_sid = ""
        self.invite_code = DEFAULT_INVITE_CODE
        self.invite_entry_done = False
        self.session = requests.Session()
        self.proxy = proxy
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.trust_env = os.getenv("IMUSIC_TRUST_ENV", "0") == "1"
        app_user_agent = ("CtClient;13.3.0;Android;14;V2203A;" + _b64(self.phone[-6:]).rstrip("=")
                          + "!#!" + _b64(self.phone[:5]).rstrip("="))
        self.session.headers.update({
            "User-Agent": app_user_agent,
            "Accept": "application/json, text/plain, */*",
            "Origin": BASE_URL,
            "X-Requested-With": "com.ct.client",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": f"{BASE_URL}/h5v/fusion/ai-luck-winnew?cc={self.channel_id}&ca=w7x6"
        })
        self.session.cookies.set("cc", self.channel_id, domain="ai.imusic.cn", path="/")
        self.session.cookies.set("loginState", "true", domain="ai.imusic.cn", path="/")
        for name, value in _parse_cookie(cookie).items():
            self.session.cookies.set(name, value, domain="ai.imusic.cn", path="/")
        self.identity_verified = False

    def close(self):
        self.session.close()

    def open_activity_page(self):
        if not self.identity_verified:
            raise ImusicError("账号身份未经核对")
        if self.activity_sid:
            return
        self.session.cookies.set("cc", self.channel_id, domain="ai.imusic.cn", path="/")
        self.session.cookies.set("loginState", "true", domain="ai.imusic.cn", path="/")
        target = DEFAULT_ACTIVITY_URL
        try:
            res = self.session.get(target, timeout=20, allow_redirects=True)
            self.activity_sid = next((c.value for c in self.session.cookies
                                      if c.name == "imusic" and c.domain.lstrip(".") == "ai.imusic.cn"), "")
            if not self.activity_sid:
                self.activity_sid = f"118100{int(time.time() * 1000)}"
                self.session.cookies.set("imusic", self.activity_sid, domain="ai.imusic.cn", path="/")
        except Exception:
            self.activity_sid = f"118100{int(time.time() * 1000)}"
            self.session.cookies.set("imusic", self.activity_sid, domain="ai.imusic.cn", path="/")

    def activity_event(self, name, value):
        if not self.identity_verified or not self.activity_sid:
            self.activity_sid = f"118100{int(time.time() * 1000)}"
        return self._post("/vapi/vue_stat/sendMessage", self._params({
            "invitationCode": self.invite_code or DEFAULT_INVITE_CODE,
            "actname": name,
            "actparam": value + "_ca_w7x6",
            "sid": self.activity_sid
        }), True, True)

    def _params(self, params):
        data = {"channelId": self.channel_id, "portal": "45", "mobile": self.phone}
        data.update(params or {})
        return data

    def _post(self, path, payload, encrypted, encrypted_response, plain_query=False):
        headers = {} if encrypted or plain_query else {"Content-Type": "application/json;charset=UTF-8"}
        if self.token:
            headers["Authorization"] = self.token
        kwargs = {}
        if encrypted:
            headers.update(self.encryption_headers)
            kwargs["params"] = {"formData": encrypt_payload(payload, headers)}
        elif plain_query:
            kwargs["params"] = payload
        else:
            kwargs["json"] = payload
        try:
            response = self.session.post(BASE_URL + path, headers=headers, timeout=25, allow_redirects=False, **kwargs)
        except requests.RequestException:
            raise ImusicError("爱音乐请求连接失败或超时") from None

        if response.status_code != 200:
            raise ImusicError(f"爱音乐请求失败，HTTP {response.status_code}")
        auth_header = response.headers.get("authorization") or response.headers.get("Authorization")
        if auth_header and auth_header.strip():
            new_bearer = _bearer(auth_header)
            if len(new_bearer) > 10:
                self.token = new_bearer
        try:
            data = response.json()
        except ValueError:
            data = response.text.strip()
        if isinstance(data, str) and encrypted_response:
            try:
                data = decrypt_payload(data, headers)
            except Exception:
                raise ImusicError("爱音乐响应解密失败")
        if not isinstance(data, dict):
            raise ImusicError("爱音乐响应格式异常")
        if str(data.get("code", data.get("returnCode", ""))) == "0007":
            self.identity_verified = False
            raise ImusicApiError("0007", payload.get("apiName", path))
        return data

    def api(self, api_name, params=None, encrypted_response=True):
        payload = self._params(params)
        payload["apiName"] = api_name
        return self._post("/hapi/en/api" if encrypted_response else "/hapi/de/api",
                          payload, encrypted_response, encrypted_response,
                          plain_query=not encrypted_response)

    def direct(self, path, params=None, encrypted=True, encrypted_response=None):
        if encrypted_response is None:
            encrypted_response = encrypted
        return self._post(path, self._params(params), encrypted, encrypted_response,
                          plain_query=not encrypted)

    def decrypt_invite_code(self, code):
        code = str(code or "").strip()
        if not code:
            return {}
        payload = {
            "activityId": ACTIVITY,
            "mobile": code,
            "type": 2,
            "invitationCode": code,
            "apiName": "diy/DiyVideoApi/getEncryptDecryptMobile",
            "channelId": self.channel_id,
            "portal": "45"
        }
        return self._post("/hapi/en/api", payload, True, True)

    def mark_invite_entry(self):
        if not self.invite_code or self.invite_entry_done:
            return True
        self.invite_entry_done = True
        try:
            info = self.decrypt_invite_code(self.invite_code)
            if str(info.get("code")) == "0000" and info.get("data"):
                inviter = str(info.get("data")).split("|")[0]
                if inviter:
                    self.activity_event("activity_vring_sharinglink_h5_20260128",
                                        f"activityID_{ACTIVITY}_templateID_null_vidioID_null_分享人手机号_{inviter}_接收人手机号_{self.phone}_templateconfID_null_entrance_{self.channel_id}")
                    ql_log("✅ 官方通道入场校验与会话绑定完成")
                    return True
        except Exception:
            pass
        return False

    def refresh_login(self, ticket=None):
        if ticket:
            self.ticket = ticket
        use_ticket = ticket or getattr(self, "ticket", None)
        payload = {"portal": "45", "channelId": self.channel_id}
        payload.update({"ticket": use_ticket} if use_ticket else {"user118100cn": "user118100cn"})
        self.identity_verified = False
        data = self._post("/vapi/vue_login/sso_login_v2", payload, False, False)
        if str(data.get("returnCode")) != "0000" or not data.get("token"):
            raise ImusicError("爱音乐登录刷新失败，请更新该账号的凭证")
        if str(data.get("mobile", "")) != self.phone:
            self.token = ""
            self.session.cookies.clear()
            raise ImusicError("爱音乐会话手机号与当前账号不一致")
        self.token = _bearer(data["token"])
        self.identity_verified = True
        return data

# ===== 电信登录与 Ticket 换取模块 =====
KEYS = {
    'login_rsa': '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB\n-----END PUBLIC KEY-----',
    'des3': b'1234567`90koiuyhgtfrdews'
}

def encrypt_des3(data, mode='enc'):
    cipher = DES3.new(KEYS['des3'], DES3.MODE_CBC, bytes([0] * 8))
    if mode == 'enc':
        return cipher.encrypt(pad(data.encode(), 8)).hex()
    return unpad(cipher.decrypt(bytes.fromhex(data)), 8).decode()

def encrypt_rsa(data):
    cipher = PKCS1_v1_5.new(RSA.import_key(KEYS['login_rsa']))
    return base64.b64encode(cipher.encrypt(data.encode())).decode()

def telecom_encode(s):
    return ''.join((chr(ord(c) + 2) for c in str(s)))

class CustomSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context(ciphers='DEFAULT@SECLEVEL=1:!aNULL:!eNULL:!MD5')
        ctx.check_hostname = False
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

def get_telecom_session(proxy=None):
    s = requests.Session()
    s.verify = certifi.where()
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Mobile Safari/537.36'})
    s.mount('https://', CustomSSLAdapter())
    return s

def telecom_login(phone, password, android_id='', cache_dict=None, proxy=None):
    cached = (cache_dict or {}).get(phone, {})
    s = get_telecom_session(proxy)
    try:
        if cached.get("token") and cached.get("userId"):
            uid = _telecom_get_ticket(s, phone, cached)
            if uid:
                return uid

        stamp = datetime.now(CST).strftime('%Y%m%d%H%M%S')
        use_android = bool(re.fullmatch(r'[0-9a-fA-F]{16}', android_id)) if android_id else False
        if use_android:
            client_type = '#11.0.0#channel8#Xiaomi 20#'
            cipher_head = f'Xiaomi 20 8.0.0.{android_id[:12]}'
            system_version = '8.0.0'
            device_uid = ''
            is_chinatelecom = ''
        else:
            device_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            client_type = '#10.5.0#channel50#iPhone 14 Pro Max#'
            cipher_head = f'iPhone 14 15.4.{device_id[:12]}'
            system_version = '15.4.0'
            device_uid = device_id
            is_chinatelecom = '0'

        cipher_text = f'{cipher_head}{phone}{stamp}{password}0$$$0.'
        fields = {
            'loginType': '4',
            'accountType': '',
            'loginAuthCipherAsymmertric': encrypt_rsa(cipher_text),
            'deviceUid': device_uid,
            'phoneNum': telecom_encode(phone),
            'isChinatelecom': is_chinatelecom,
            'systemVersion': system_version,
            'authentication': telecom_encode(password)
        }
        if use_android:
            fields['androidId'] = telecom_encode(android_id)
            fields['loginAuthCipher'] = ''

        body = {
            'headerInfos': {
                'code': 'userLoginNormal', 'timestamp': stamp, 'broadAccount': '',
                'broadToken': '', 'clientType': client_type, 'shopId': '20002',
                'source': '110003', 'sourcePassword': 'Sid98s', 'token': '',
                'userLoginName': telecom_encode(phone)
            },
            'content': {'attach': 'test', 'fieldData': fields}
        }
        res = s.post('https://appgologin.189.cn:9031/login/client/userLoginNormal', json=body, timeout=15)
        res_data = res.json()
        succ = res_data.get('responseData', {}).get('data', {}).get('loginSuccessResult')
        if not succ or not succ.get('token'):
            ql_log(f"❌ 电信账密验证失败: {res_data.get('responseData', {}).get('resultDesc') or res_data}")
            return None
        if cache_dict is not None:
            cache_dict[phone] = succ
        return _telecom_get_ticket(s, phone, succ)
    finally:
        s.close()

def _telecom_get_ticket(session, phone, cached_info):
    stamp = datetime.now(CST).strftime('%Y%m%d%H%M%S')
    root = telecom_et.Element('Request')
    header = telecom_et.SubElement(root, 'HeaderInfos')
    for k, v in {
        'Code': 'getSingle', 'Timestamp': stamp, 'BroadAccount': '', 'BroadToken': '',
        'ClientType': '#9.6.1#channel50#iPhone 14 Pro Max#', 'ShopId': '20002',
        'Source': '110003', 'SourcePassword': 'Sid98s', 'Token': cached_info['token'],
        'UserLoginName': phone
    }.items():
        telecom_et.SubElement(header, k).text = str(v)
    content = telecom_et.SubElement(root, 'Content')
    telecom_et.SubElement(content, 'Attach').text = 'test'
    fields = telecom_et.SubElement(content, 'FieldData')
    telecom_et.SubElement(fields, 'TargetId').text = encrypt_des3(str(cached_info['userId']))
    telecom_et.SubElement(fields, 'Url').text = '4a6862274835b451'
    xml_data = telecom_et.tostring(root, encoding='utf-8')

    res = session.post('https://appgologin.189.cn:9031/map/clientXML',
                       data=xml_data, headers={'Content-Type': 'application/xml; charset=UTF-8'}, timeout=15)
    tk_match = re.search(r'<Ticket>(.*?)</Ticket>', res.text)
    if not tk_match:
        return None
    try:
        return encrypt_des3(tk_match.group(1), 'dec')
    except Exception:
        return None

# ===== 业务执行与流程控制 =====
_MAKE_GATE = {'last': 0.0}

def pace_make_submission(interval):
    if interval > 0:
        wait = _MAKE_GATE['last'] + interval - time.time()
        if wait > 0:
            time.sleep(wait)
    _MAKE_GATE['last'] = time.time()

def number(value):
    return int(str(value))

def date_conv(value):
    if not isinstance(value, str):
        raise ImusicError('日期格式未知')
    try:
        r = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ImusicError('日期格式解析异常')
    return r.replace(tzinfo=CST) if r.tzinfo is None else r.astimezone(CST)

def checked(response, api=''):
    if not isinstance(response, dict) or str(response.get('code')) != '0000':
        raise ImusicApiError(response.get('code') if isinstance(response, dict) else None, api)
    return response.get('data')

def creation_points(records, issue):
    start, end = (date_conv(issue['startTime']), date_conv(issue['endTime']))
    total = 0
    for item in records:
        when = date_conv(item.get('createDate'))
        if not start <= when <= end:
            continue
        amount = number(item.get('score'))
        if amount <= 0 or str(item.get('scoreType')) in {'-1', '-2'}:
            continue
        desc = str(item.get('scoreDesc', ''))
        if '制作' in desc or '创作' in desc:
            total += amount
    return total

class Activity:
    def __init__(self, client, options, state_path):
        self.client = client
        self.options = options
        self.state_path = Path(state_path)
        self.state = json.loads(self.state_path.read_text(encoding='utf-8')) if self.state_path.exists() else {}
        self.state.setdefault('jobs', [])
        self.state.setdefault('claims', [])
        self._redeem_attempted_this_run = False
        self._draws_this_run = 0
        self._topup_draws = 0
        self._issue = None
        self._final_issue = False

    def save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding='utf-8')

    def api(self, name, **params):
        api = 'act/LaborApi/' + name
        return checked(self.client.api(api, {'activityId': ACTIVITY, **params}), api)

    def records(self, name):
        rows = []
        for page in range(1, 10):
            data = self.api(name, pageNo=page, pageSize=10)
            if not isinstance(data, dict) or not isinstance(data.get('list'), list):
                break
            batch = data['list']
            rows.extend(batch)
            if len(batch) < 10:
                break
        return rows

    def score(self):
        data = self.api('getOperationTotalScoreOrRemainingScore')
        return (number(data['totalScore']), number(data['remainingScore']))

    def quota(self):
        return checked(self.client.api('ismp/IsmpApi/queryAiMakePkgInfo', {'aid': ACTIVITY}), 'ismp/IsmpApi/queryAiMakePkgInfo')

    def mutate(self, kind, call):
        if not self.options.execute:
            raise ImusicError('查询模式不能更改数据')
        res = call()
        return checked(res, kind)

    def notify_tickets(self):
        try:
            rows = self.records('getOperationMyTickets')
            ql_log(f"🎫 查询到券码 {len(rows)} 个")
            for row in rows:
                if str(row.get('useStatus')) == '1':
                    ql_log(f"🎉 发现中奖券码: {row.get('prizeName', '活动奖品')}！请在活动中核对收货信息")
        except Exception:
            pass

    def claim_phone_bills(self):
        claimed = 0
        try:
            rows = self.records('getOperationPrizeRecordList')
            for row in rows:
                if str(row.get('awardIndex')) in PHONE_AWARDS and str(row.get('status')) == '0':
                    award_id = row.get('awardId')
                    if award_id and str(award_id) not in self.state['claims']:
                        if self.options.execute:
                            self.mutate('act/LaborApi/extractPhoneBill',
                                        lambda: self.client.api('act/LaborApi/extractPhoneBill', {'activityId': ACTIVITY, 'awardId': award_id}))
                            self.state['claims'].append(str(award_id))
                            self.save()
                            ql_log("🎁 成功提交 1 元中奖话费领取！")
                            claimed += 1
        except Exception as e:
            ql_log(f"领取话费记录查询异常: {e}")
        return claimed

    def template(self):
        data = checked(self.client.api('diy/DiyVideoApi/queryActRecommendTemplateList',
                                       {'activityId': 'ai119_4', 'pageNo': 1, 'pageSize': 50}, encrypted_response=False),
                       'diy/DiyVideoApi/queryActRecommendTemplateList')
        rows = data.get('list', [])
        ready = [r for r in rows if r.get('mediaType') == 'video' and number(r.get('imageCount', -1)) == 0 and r.get('userWords') and r.get('templateId')]
        if not ready:
            raise ImusicError('未找到免素材的可制作视频模板')
        chosen = ready[0]
        ql_log(f"🎬 选用视频模板：{chosen.get('videoName')} ({chosen.get('templateConfId')})")
        return chosen

    def make_payload(self, template):
        name = str(template['videoName']) + datetime.now(CST).strftime('%H%M%S') + secrets.token_hex(2)
        payload = {key: '' for key in ('openId', 'makeId', 'background', 'userPhotos', 'inviterMobile', 'arrangeId', 'aiGatewayImagMakeId', 'fromType', 'sessionId', 'voice', 'videoOwnerCode', 'videoResourceCode', 'workId', 'imageMakeType', 'songId', 'imageRate', 'productionType')}
        payload.update(
            aid=ACTIVITY,
            templateId=template['templateId'],
            templateConfId=template['templateConfId'],
            userWords=template['userWords'],
            templateName=name,
            videoName=name,
            aiPack=0,
            autoOrderUgc=0
        )
        return payload

    def prepare_make(self, template):
        self.client.open_activity_page()
        self.client.mark_invite_entry()
        channel = self.client.channel_id
        try:
            self.client.activity_event('page_vring_index', f"玩转AI赢手机_activityID_{ACTIVITY}_entrance_{channel}")
            checked(self.client.api('ismp/IsmpApi/queryAiMakePkgInfo', {'templateId': template['templateId'], 'aid': ACTIVITY}), 'ismp/IsmpApi/queryAiMakePkgInfo')
            checked(self.client.direct('/hapi/diy_video/imu/query_template_info',
                                       {'templateConfId': template['templateConfId'], 'templateId': template['templateId']},
                                       encrypted=False), '/hapi/diy_video/imu/query_template_info')
            param = f"activityID_{ACTIVITY}_templateID_{template['templateId']}_entrance_{channel}_templateconfID_{template['templateConfId']}"
            self.client.activity_event('activity_vring_make_1.9', '_' + param)
            self.client.activity_event('activity_2511AI-makeonekey_1.6', param)
        except Exception:
            pass

    def make(self, issue):
        if self.options.make_count == 0 or not self.options.execute:
            return 0
        points = creation_points(self.records('getOperationRecordList'), issue)
        left = max(0, (340 - points) // 20)
        quota = self.quota()
        count = min(self.options.make_count, left, max(0, number(quota.get('privilegeVrbtAIVideoLeftNum', 0))))
        ql_log(f"📊 本期已获制作积分 {points}/340；本轮计划制作 {count} 次")
        if not count:
            return 0

        template = self.template()
        completed = 0
        for idx in range(count):
            completed_this = False
            for auth_retry in range(2):
                self.prepare_make(template)
                payload = self.make_payload(template)
                pace_make_submission(self.options.make_interval)
                try:
                    res = self.client.direct('/hapi/diy_video/au/template_make_add_v2', payload)
                    data = checked(res, '/hapi/diy_video/au/template_make_add_v2')
                    make_id = data.get('makeId') if isinstance(data, dict) else (data if isinstance(data, (str, int)) else None)
                    completed += 1
                    completed_this = True
                    ql_log(f"✅ 第 {idx + 1}/{count} 次视频制作提交成功 (makeId: {make_id})")
                    time.sleep(3)
                    break
                except ImusicApiError as e:
                    if e.code == '10007':
                        ql_log("⚠️ 遇到10007同IP高频频控，停止后续制作")
                        return completed
                    elif e.code == '0007':
                        if auth_retry == 0:
                            ql_log("⚠️ 制作提交返回0007（登录态未通过）：正在重建会话重试...")
                            self.client.refresh_login()
                            self.client.activity_sid = ''
                            time.sleep(1)
                            continue
                        else:
                            ql_log("⚠️ 重建会话后仍返回0007，跳过当前制作")
                            break
                    elif e.code == '10013':
                        ql_log("⚠️ 遇到10013错误，尝试自愈刷新凭据后重试...")
                        self.client.refresh_login()
                        time.sleep(1)
                        continue
                    else:
                        ql_log(f"⚠️ 制作接口返回: {e}")
                        break
            if not completed_this:
                break
        return completed

    def draw_points(self, reserve=0):
        total, remaining = self.score()
        available = max(0, (remaining - reserve) // 20)
        limit = min(self.options.max_draws, available)
        if limit <= 0 or not self.options.execute:
            return 0
        ql_log(f"🎰 准备执行积分抽奖，预计最多抽奖 {limit} 次...")
        draw_count = 0
        for i in range(limit):
            try:
                res = self.client.api('act/LaborApi/operationIntegralLottery', {'activityId': ACTIVITY})
                data = checked(res, 'act/LaborApi/operationIntegralLottery')
                name = str(data.get('awardName', '无中奖'))
                ql_log(f"🎁 抽奖第 {i + 1} 次结果：{name}")
                draw_count += 1
                time.sleep(2)
            except Exception as e:
                ql_log(f"抽奖中断: {e}")
                break
        return draw_count

    def spend(self):
        total, remaining = self.score()
        if remaining >= 1000 and self.options.mode in ('auto', 'save') and self.options.execute:
            ql_log("💸 当前积分满 1000 点，正在申请兑换 10 元话费...")
            try:
                res = self.client.api('act/LaborApi/operationIntegralRedeemPrize', {'activityId': ACTIVITY})
                checked(res, 'act/LaborApi/operationIntegralRedeemPrize')
                ql_log("🎉 10 元话费兑换申请成功！")
            except ImusicApiError as e:
                if e.code == '10003':
                    ql_log("ℹ️ 10元话费当前库存不足，次月自动再试")
                else:
                    ql_log(f"话费兑换返回: {e}")

        draws = 0
        if self.options.mode == 'draw':
            draws = self.draw_points(0)
        elif self.options.mode == 'auto':
            if self._final_issue and remaining < 1000:
                draws = self.draw_points(0)
            elif remaining > 1000:
                draws = self.draw_points(1000)
        return draws

    def run(self):
        if not self.client.identity_verified:
            self.client.refresh_login()
        self.client.open_activity_page()
        self.client.mark_invite_entry()
        issue = self.api('getOperationCurrentIssueInfo')
        self._issue = issue
        self._final_issue = any(date_conv(issue.get(k)) >= FINAL_DRAW_DATE for k in ('drawTime', 'endTime') if issue.get(k))
        b_total, b_rem = self.score()
        ql_log(f"📌 当前活动期：{issue.get('issueName')} | 累计获点 {b_total} | 当前可用积分 {b_rem}")
        
        self.notify_tickets()
        claimed = self.claim_phone_bills()
        makes = self.make(issue)
        draws = self.spend()
        claimed += self.claim_phone_bills()

        a_total, a_rem = self.score()
        ql_log(f"🏁 本轮账号执行完毕：积分变动 {b_rem} -> {a_rem} (累计获点 {a_total})")
        return {
            "phone": mask_phone(self.client.phone),
            "status": "成功",
            "makes": makes,
            "score_change": f"{b_rem}→{a_rem}",
            "draws": draws,
            "bill_claimed": claimed,
            "remark": "已完成全部任务"
        }

# ===== 账号解析与运行调度 =====
def load_all_accounts():
    accounts = []
    raw_cta = os.getenv("chinaTelecomAccount", "")
    for line in raw_cta.replace("\r", "").replace("\n", "&").split("&"):
        part = line.strip()
        if not part or "#" not in part:
            continue
        segs = part.split("#")
        p = segs[0].strip()
        aid = segs[-1].strip() if len(segs) >= 3 and re.fullmatch(r"[0-9a-fA-F]{16}", segs[-1].strip()) else ""
        pwd = "#".join(segs[1:-1] if aid else segs[1:]).strip()
        if re.fullmatch(r"1[3-9]\d{9}", p) and pwd:
            accounts.append({"phone": p, "password": pwd, "android_id": aid})

    for env_key in ("AI096_ACCOUNTS", "CAILING_ACCOUNTS"):
        raw_env = os.getenv(env_key, "")
        for line in raw_env.replace("\r", "\n").replace("&", "\n").split("\n"):
            part = line.strip()
            if not part or "#" not in part:
                continue
            p, pwd = part.split("#", 1)
            p, pwd = p.strip(), pwd.strip()
            if re.fullmatch(r"1[3-9]\d{9}", p) and pwd:
                if not any(a["phone"] == p for a in accounts):
                    accounts.append({"phone": p, "password": pwd, "android_id": ""})

    raw_ia = os.getenv("IMUSIC_ACCOUNTS", "").strip()
    if raw_ia:
        try:
            ia_data = json.loads(raw_ia)
            if isinstance(ia_data, list):
                for item in ia_data:
                    p = str(item.get("phone", item.get("mobile", ""))).strip()
                    if re.fullmatch(r"1[3-9]\d{9}", p) and not any(a["phone"] == p for a in accounts):
                        accounts.append({
                            "phone": p,
                            "token": item.get("token", ""),
                            "cookie": item.get("cookie", ""),
                            "password": item.get("password", ""),
                            "android_id": ""
                        })
        except Exception:
            pass

    acc_txt = ROOT / "accounts.txt"
    if acc_txt.exists():
        try:
            for line in acc_txt.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "#" not in line:
                    continue
                p, pwd = line.split("#", 1)
                p = p.strip()
                pwd = pwd.split("#")[0].strip()
                if re.fullmatch(r"1[3-9]\d{9}", p) and pwd:
                    if not any(a["phone"] == p for a in accounts):
                        accounts.append({"phone": p, "password": pwd, "android_id": ""})
        except Exception:
            pass

    return accounts

def main():
    ql_log("==========================================")
    ql_log("🚀 电信AI奇遇日常任务运行启动（任务+自动领奖+PushPlus）")
    ql_log("==========================================")

    state_dir = ROOT / ".telecom_ai119"
    state_dir.mkdir(parents=True, exist_ok=True)
    telecom_cache_file = state_dir / "telecom_cache.json"
    telecom_cache = {}
    if telecom_cache_file.exists():
        try:
            telecom_cache = json.loads(telecom_cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    # 1. 加载账号
    accounts = load_all_accounts()
    if not accounts:
        ql_log("❌ 未检测到任何账号，请在青龙环境变量配置 chinaTelecomAccount (手机号#密码) 或 AI096_ACCOUNTS")
        return

    ql_log(f"👥 解析到有效账号数: {len(accounts)}")

    # 2. 参数配置
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', default=True)
    parser.add_argument('--mode', default=os.getenv("IMUSIC_MODE", "auto").strip().lower())
    parser.add_argument('--make-count', type=int, default=int(os.getenv("IMUSIC_MAKE_COUNT", "17")))
    parser.add_argument('--make-interval', type=int, default=int(os.getenv("IMUSIC_MAKE_INTERVAL", "20")))
    parser.add_argument('--max-draws', type=int, default=int(os.getenv("IMUSIC_MAX_DRAWS", "10")))
    parser.add_argument('--cooldown-hours', type=float, default=float(os.getenv("IMUSIC_COOLDOWN_HOURS", "0")))
    options = parser.parse_args([])

    errors = 0
    for idx, acc in enumerate(accounts, 1):
        phone = acc["phone"]
        ql_log(f"\n---- [{idx}/{len(accounts)}] 处理账号: {mask_phone(phone)} ----")
        proxy = proxy_mgr.get_proxy()
        client = None
        try:
            token = acc.get("token", "")
            ticket = None
            if not token and acc.get("password"):
                ql_log("🔑 正在进行电信统一认证换取 Ticket...")
                ticket = telecom_login(phone, acc["password"], acc.get("android_id", ""), telecom_cache, proxy)
                if not ticket:
                    raise ImusicError("获取电信登录 Ticket 失败，跳过该账号")

            client = ImusicClient(phone, token=token, channel_id=DEFAULT_CHANNEL, proxy=proxy)
            client.invite_code = DEFAULT_INVITE_CODE
            client.refresh_login(ticket=ticket)
            ql_log("✅ 爱音乐会话校验通过")

            activity = Activity(client, options, state_dir / f"{phone}.json")
            res_summary = activity.run()
            RUN_SUMMARIES.append(res_summary)
        except Exception as e:
            errors += 1
            ql_log(f"💥 账号处理异常: {e}")
            RUN_SUMMARIES.append({
                "phone": mask_phone(phone),
                "status": "失败",
                "makes": 0,
                "score_change": "-",
                "draws": 0,
                "bill_claimed": 0,
                "remark": str(e)
            })
        finally:
            if client:
                client.close()

    try:
        telecom_cache_file.write_text(json.dumps(telecom_cache, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    notify_enabled = os.getenv("QL_NOTIFY", "1").strip().lower() in ("1", "true")
    ql_notify(notify_enabled)
    ql_log(f"\n==========================================")
    ql_log(f"🏁 任务结束，共处理 {len(accounts)} 个账号，{errors} 个异常")
    ql_log(f"==========================================")

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