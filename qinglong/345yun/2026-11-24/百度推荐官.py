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
"""百度推荐官 · 青龙脚本（单文件 · 支持账号密码登录 ）

==================== 三种登录方式（任选一个，优先级从上到下）====================
  BD_ACCOUNTS      备注#手机号#密码        ← 推荐：脚本自己登录、自己续期
                   多账号换行（或 &）分隔，例：
                       主号#18267596392#mypassword
                       小号#13800000000#otherpwd
                   不写备注也可以：18267596392#mypassword

  BD_CK            完整 cookie            BDUSS=xxx; BAIDUID=yyy; STOKEN=zzz

  BD_BDUSS         只有 BDUSS 的值        UxZGszMWlxLUNWV0tycGhqLW9lZkVOSVNM...

==================== 其他环境变量 ====================
  BD_PROXY         代理（http://user:pass@ip:port 或 socks5://ip:port）
                   多账号换行对应；只写一个则全部共用
  BD_WITHDRAW      做完任务后是否自动兑换提现（1=是，默认 1）
  BD_WITHDRAW_MIN  可提现金额达到多少才提（元，默认 1）
  BD_TASK_LIMIT    每个账号最多做几个任务类型（0=不限，默认 0）
  BD_DEBUG         1=打印详细日志（默认 1）



==================== 部署 ====================

  命令：task 百度推荐官.py

==================== 密码登录的已知限制 ====================
百度对部分账号/设备会要求「短信二次验证」（错误码 400023）。青龙无人值守填不了码，
遇到时日志会提示改用 BD_CK 或 BD_BDUSS。登录成功的 BDUSS 会缓存到
bd_login_cache.json（同目录），之后不再重复登录。
"""

import os
import sys
import json
import time
import random
import traceback

"""百度推荐官 · 任务引擎（安卓版，协议与 Windows 版一致）
纯 requests + 标准库，兼容 Python 3.8（Chaquopy 16）。
"""
import json
import os
import random
import re
import threading
import time
import uuid
from urllib.parse import parse_qs, quote, urlparse

import requests

# ---------------------------------------------------------------- 常量（与桌面版一致）
TPL = 'bs_andr'
APP_ID = '1'
APP_VERSION = '15.84.0.10'
SDK_VERSION = '9.16.2.3'
CAP_AK = '1e3f2dd1c81f2075171a547893391274'
CAP_SCENE = 'login'
CAP_REFER = 'https://wappass.baidu.com/static/activity/pass-machine.html'
CAP_SIG = '13cd337d8f0d0e83d2d391196d728583'
LOGIN_SIG = 'e8f135c027eb40c6db666758de083f5b'
CV = '170601'
UA_LOGIN = 'tpl:bs_andr;android_sapi_v9.16.2.3'
UA_DALVIK = 'Dalvik/2.1.0 (Linux; U; Android 13; 23013RK75C Build/TKQ1.220905.001)'
UA_APP = (
    'Mozilla/5.0 (Linux; Android 13; 23013RK75C Build/TKQ1.220905.001; wv) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.58 '
    'Mobile Safari/537.36 T7/15.84 SP-engine/3.66.0 bd_dvt/0 '
    'baiduboxapp/15.84.0.10 (Baidu; P1 13) NABar/1.0'
)
UA_H5 = (
    'Mozilla/5.0 (Linux; Android 13; 23013RK75C Build/TKQ1.220905.001; wv) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 '
    'Mobile Safari/537.36 Sapi_9.16.2.3_Android'
)
E1024 = 65537
N1024 = int(
    'B3C61EBBA4659C4CE3639287EE871F1F48F7930EA977991C7AFE3CC442FEA496'
    '43212E7D570C853F368065CC57A2014666DA8AE7D493FD47D171C0D894EEE3ED7'
    'F99F6798B7FFD7B5873227038AD23E3197631A8CB642213B9F27D4901AB0D92BF'
    'A27542AE890855396ED92775255C977F5C302F1E7ED4B1E369C12CB6B1822F', 16)
SHOP = 'https://shopping.baidu.com'
KOC_ASYNC = SHOP + '/koc/v2/async'
REGISTER = SHOP + '/api/task/cardclk/register'
FISSION = SHOP + '/api/fission/complete'
JUMP = SHOP + '/koc/v2/complete/jumpTask'
TASK_HINT = SHOP + '/koc/v2/taskHint'
DRESS_BASE = 'https://aishopping.baidu.com'
DRESS_TYPE = 'dress_helper'
WIDGET = 'https://wappass.baidu.com/v3/api/auth/widget'
WIDGET_OK = 110000
ERR_CODE_WRONG = 810003
ERR_SEND_MUCH = 500010


_DEFAULT_INVITER = ('https://mr.baidu.com/r/26FXV7g2hRm?f=cp&rs=876312910'
                    '&ruk=HBLksrD1vr_6sbiENArGTA&u=74dcf07a6031c311&sid_for_share=257311_3')
INVITER_URL = (os.environ.get('BD_INVITER_URL') or _DEFAULT_INVITER)
INVITER_REFER = 'https://shopping.baidu.com/'

INVITER_ACT = ('https://m.baidu.com/s?word=%E7%99%BE%E5%BA%A6%E6%8E%A8%E8%8D%90%E5%AE%98'
               '&sid=1060482')


def _rsa_encrypt(raw, block=128):
    """裸 RSA（无填充）：每 128 字节一块，块内小端拼整数，输出大写十六进制。"""
    b = bytearray(raw)
    while len(b) % block:
        b.append(0)
    out = []
    i = 0
    while i < len(b):
        m, sh = 0, 0
        for k in range(block):
            if i + k < len(b):
                m |= b[i + k] << sh
                sh += 8
        h = format(pow(m, E1024, N1024), 'x').upper()
        if len(h) % 2:
            h = '0' + h
        out.append(h)
        i += block
    return ' '.join(out)


def rsa_username(phone):
    import base64
    return _rsa_encrypt(base64.b64encode(phone.encode('utf-8')))


def rsa_password(pwd):
    return _rsa_encrypt(pwd.encode('utf-8'))


def acc_ua(acc):
    model = (acc or {}).get('model') or '23013RK75C'
    return (
        'Mozilla/5.0 (Linux; Android 13; %s Build/TKQ1.220905.001; wv) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.58 '
        'Mobile Safari/537.36 T7/15.84 SP-engine/3.66.0 bd_dvt/0 '
        'baiduboxapp/15.84.0.10 (Baidu; P1 13) NABar/1.0' % model
    )


# ---------------------------------------------------------------- 登录
class Login(object):
    def __init__(self, proxy=None, timeout=25):
        self.s = requests.Session()
        self.timeout = timeout
        self.s.trust_env = False
        self.cuid = ''
        self.zid = ''
        if proxy:
            self.s.proxies.update({'http': proxy, 'https': proxy})

    def antireplay(self):
        now = int(time.time() * 1000)
        try:
            self.s.get(
                'https://wappass.baidu.com/wp/api/security/antireplaytoken',
                params={'appid': APP_ID, 'clientfrom': 'native', 'tpl': TPL,
                        'time': str(now // 1000), 'tt': str(now)},
                headers={'User-Agent': UA_DALVIK}, timeout=self.timeout)
        except Exception:
            return None

    def cap_init(self, cuid, zid):
        now = int(time.time() * 1000)
        refer = ('%s?clientfrom=native&client=android&ak=%s&type=null&scene=%s&timestamp=%d'
                 % (CAP_REFER, CAP_AK, CAP_SCENE, now))
        r = self.s.post(
            'https://passport.baidu.com/cap/init', timeout=self.timeout,
            headers={'Referer': refer, 'User-Agent': UA_DALVIK},
            data={'ver': '2', 'cuid': cuid, 'clientid': cuid,
                  'app_version': APP_VERSION, 'ak': CAP_AK,
                  'clientfrom': 'native', 'scene': CAP_SCENE, 'sig': CAP_SIG,
                  'tpl': TPL, 'sdkversion': SDK_VERSION, 'zid': zid,
                  'refer': refer, 'appid': APP_ID, 'sdk_version': SDK_VERSION,
                  'client': 'android', '_': str(now)})
        d = (r.json() or {}).get('data') or {}
        return {'ds': d.get('ds', ''), 'tk': d.get('tk', '')}

    def do_login(self, phone, password, cuid=None, zid=None):
        """返回 (ok, data_or_err)"""
        if not cuid:
            cuid = '%032X' % random.getrandbits(128)
        if not zid:
            zid = ''.join(random.choices(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-', k=84))
        self.antireplay()
        cap = self.cap_init(cuid, zid)
        now_s = str(int(time.time()))
        now_ms = int(time.time() * 1000)
        form = {
            'logLoginType': 'sdk_login',
            'isphone': '0',
            'clientid': cuid,
            'app_version': APP_VERSION,
            'clientfrom': 'native',
            'enableExternalWeb': '0',
            'nalogin': '1',
            'sig': LOGIN_SIG,
            'sdkversion': SDK_VERSION,
            'password': rsa_password(password + now_s),
            'zid': zid,
            'isEncrypted': '1',
            'sdk_version': SDK_VERSION,
            'client': 'android',
            'needNaNextUrl': '1',
            'supFaceLogin': '1',
            'alg': 'v3',
            'cuid': cuid,
            'adapter': '3',
            'session_id': uuid.uuid4().hex + now_s,
            'k': cap['tk'],
            'scanface': '1',
            'tpl': TPL,
            's': cap['ds'],
            'cv': CV,
            't': str(now_ms),
            'appid': APP_ID,
            'liveAbility': '1',
            'support_photo': '1',
            'time': now_s,
            'loginmerge': '1',
            'username': rsa_username(phone),
        }
        import hashlib
        form['session_id'] = hashlib.md5(
            (str(uuid.uuid4()) + str(now_ms)).encode('utf-8')).hexdigest()
        r = self.s.post('https://wappass.baidu.com/wp/api/login', data=form,
                        timeout=self.timeout, headers={'User-Agent': UA_LOGIN})
        j = r.json()
        err = j.get('errInfo') or {}
        no = str(err.get('no'))
        d = j.get('data') or {}
        self.cuid, self.zid = cuid, zid
        if no == '0' and d.get('bduss'):
            return (True, {'bduss': d['bduss'], 'cuid': cuid, 'zid': zid,
                           'ptoken': d.get('ptoken', '')})
        msg = err.get('msg') or {'400011': '账号或密码错误',
                                 '400023': '需要短信二次验证',
                                 '230051': '手机号格式有误'}.get(no, '未知错误 ' + no)
        return (False, {'no': no, 'msg': msg, 'goto': d.get('gotoUrl', ''),
                        'phone': d.get('phone', ''),
                        'showType': d.get('showType', ''),
                        'cuid': cuid, 'zid': zid})

    # ---------------- 短信二次验证（400023）
    def _widget(self, action, authid, auth_params, auth_field='',
                auth_type='', auth_scene='', bankcheck=1, extra=None):
        body = {'tpl': TPL, 'client': 'android', 'clientfrom': 'native',
                'authid': authid, 'action': action, 'lang': 'zh_CN'}
        if auth_field:
            body['authField'] = auth_field
        if auth_type:
            body['authType'] = auth_type
        if auth_scene:
            body['authScene'] = auth_scene
        body['authParams'] = auth_params
        if extra:
            body.update(extra)
        url = WIDGET + ('?bankcheck=%d' % bankcheck if action == 'get' else '')
        r = self.s.post(
            url, data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json',
                     'User-Agent': UA_H5,
                     'X-Requested-With': 'com.baiduboxapp',
                     'Referer': 'https://wappass.baidu.com/v6/authwidget'},
            timeout=self.timeout)
        try:
            return r.json()
        except Exception:
            return {'code': -1, 'message': r.text[:200]}

    def begin_verify(self, goto_url, log=None):
        """第一步：解析 gotoUrl → get 取方式 → send 真发短信。返回上下文或 None。"""
        L = log or (lambda tag, msg: None)
        if not goto_url:
            L('verify', '缺少 gotoUrl')
            return None
        gq = parse_qs(urlparse(goto_url).query)
        authid = gq.get('authid', [''])[0]
        u1 = gq.get('u', [''])[0]
        proxy_url = parse_qs(urlparse(u1).query).get('u', [''])[0] or u1
        if not authid:
            L('verify', '缺少 authid')
            return None
        j = self._widget('get', authid,
                         {'supportThirdList': [], 'upsms_tel': '', 'dxmAuth': 0,
                          'clientPasskeysEnable': 0, 'nfczid': self.zid})
        if j.get('code') != WIDGET_OK:
            L('verify', '取验证方式失败 code=%s %s' % (j.get('code'), j.get('message')))
            return None
        d = j.get('data') or {}
        scene = d.get('scene', '')
        dmi = d.get('defaultMethodInfo') or {}
        field, mtype = dmi.get('field', ''), dmi.get('type', '')
        if not field:
            for m in d.get('methodsInfo') or []:
                if 'mobile' in (m.get('fields') or []):
                    field, mtype = 'mobile', 'check'
                    break
        if not field:
            L('verify', '服务端未提供可用验证方式')
            return None
        L('verify', '验证方式 %s/%s scene=%s' % (field, mtype, scene))
        j = self._widget('send', authid,
                         {'banktype': '', 'type': 'vcode', 'secret': ''},
                         auth_field=field, auth_type=mtype, auth_scene=scene,
                         extra={'sup624': 1})
        c = j.get('code')
        pr = (j.get('data') or {}).get('processRes') or {}
        if c == ERR_SEND_MUCH:
            L('verify', '发送过于频繁（500010），请等 1 分钟后再点登录')
            return None
        if c != WIDGET_OK:
            L('verify', '发码失败 code=%s %s' % (c, j.get('message')))
            return None
        L('verify', '★ 短信已发出（%s 位）' % pr.get('smsCodeLength', 6))
        return {'authid': authid, 'field': field, 'mtype': mtype,
                'scene': scene, 'proxy_url': proxy_url}

    def finish_verify(self, ctx, code, log=None):
        """第二步：用验证码 action=check，通过后取 BDUSS。"""
        L = log or (lambda tag, msg: None)
        if not ctx or not code:
            return None
        j = self._widget('check', ctx['authid'],
                         {'vcode': str(code).strip(), 'bankCardType': '',
                          'type': 'vcode', 'secret': ''},
                         auth_field=ctx['field'], auth_type=ctx['mtype'],
                         auth_scene=ctx['scene'])
        c = j.get('code')
        if c == ERR_CODE_WRONG:
            L('verify', '验证码错误，请重新点登录')
            return None
        if c != WIDGET_OK:
            L('verify', '校验失败 code=%s %s' % (c, j.get('message')))
            return None
        pr = (j.get('data') or {}).get('processRes') or {}
        L('verify', '★ 验证通过 status=%s' % pr.get('status'))
        # 有的账号在 check 响应里就直接下发 BDUSS（set-cookie），先拿一手的；
        # 省掉一次跳转，也避免跳转地址过期导致"验证过了却拿不到 BDUSS"。
        for c in self.s.cookies:
            if c.name == 'BDUSS' and c.value:
                L('verify', 'BDUSS 已随校验响应下发 %s...' % c.value[:12])
                return c.value
        return self._fetch_bduss(ctx['proxy_url'], L)

    def _fetch_bduss(self, proxy_url, L):
        if not proxy_url:
            L('verify', '缺少跳转地址，无法取 BDUSS')
            return None
        try:
            r = self.s.get(proxy_url, timeout=self.timeout, allow_redirects=True,
                           headers={'User-Agent': UA_H5})
        except Exception as ex:
            L('verify', '取 BDUSS 失败 %s' % type(ex).__name__)
            return None
        bduss = r.cookies.get('BDUSS')
        if not bduss:
            for c in self.s.cookies:
                if c.name == 'BDUSS':
                    bduss = c.value
                    break
        try:
            j = r.json()
            e = j.get('errInfo') or {}
            L('verify', 'proxy no=%s msg=%s' % (e.get('no'), e.get('msg')))
        except Exception:
            pass
        if bduss:
            L('verify', 'BDUSS 获取成功 %s...' % bduss[:12])
        else:
            L('verify', '未拿到 BDUSS')
        return bduss


def build_cookie(bduss, cuid=None, zid=None):
    S = requests.Session()
    S.trust_env = False
    S.headers.update({'User-Agent': UA_APP,
                      'X-Requested-With': 'com.baidu.searchbox'})
    S.cookies.set('BDUSS', bduss, domain='.baidu.com')
    S.cookies.set('BDUSS_BFESS', bduss, domain='.baidu.com')
    try:
        S.get('https://www.baidu.com/', timeout=20)
    except Exception:
        pass
    jar = {}
    for c in S.cookies:
        jar[c.name] = c.value
    jar['BDUSS'] = bduss
    jar['BDUSS_BFESS'] = bduss
    if cuid:
        jar['BAIDUCUID'] = cuid
        jar['BAIDUCUID_BFESS'] = cuid
    order = ['BAIDUID', 'BAIDUID_BFESS', 'BAIDUCUID', 'BAIDUCUID_BFESS',
             'BDUSS', 'BDUSS_BFESS', 'ST', 'BDORZ']
    parts, seen = [], set()
    for k in order:
        if jar.get(k):
            parts.append('%s=%s' % (k, jar[k]))
            seen.add(k)
    for k, v in jar.items():
        if k not in seen and v:
            parts.append('%s=%s' % (k, v))
    return '; '.join(parts)


# ---------------------------------------------------------------- 任务引擎
class Engine(object):
    """一个账号一个 Engine 实例，互不影响。"""

    def __init__(self, account, proxy=None, log=None,
                 proxy_provider=None, on_proxy_dead=None):
        self.acc = account or {}
        self.proxy = proxy
        self.log = log or (lambda *a, **k: None)
        self.s = requests.Session()
        self.s.trust_env = False
        self.s.headers.update({
            'User-Agent': acc_ua(account),
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'com.baidu.searchbox',
            'X-From-H3-TRNet': 'true',
            'Cookie': (account or {}).get('cookie', ''),
        })
        if proxy:
            self.s.proxies.update({'http': proxy, 'https': proxy})
        self.stop_flag = False
        self._used_words = {}
        self.proxy_provider = proxy_provider
        self.on_proxy_dead = on_proxy_dead
        self._proxy_swaps = 0

    def L(self, tag, msg):
        try:
            self.log(self.acc.get('remark') or self.acc.get('phone', '?'), tag, msg)
        except Exception:
            pass

    def set_proxy(self, px):
        self.proxy = px
        self.s.proxies.clear()
        if px:
            self.s.proxies.update({'http': px, 'https': px})

    def _swap_proxy(self):
        if not self.proxy_provider:
            return False
        if self._proxy_swaps >= 6:
            return False
        old = self.proxy
        if old and self.on_proxy_dead:
            try:
                self.on_proxy_dead(old)
            except Exception:
                pass
        try:
            new = self.proxy_provider()
        except Exception:
            new = None
        if new and new == old:
            self.set_proxy(None)
            self.L('prox', '无可用代理，临时改直连')
            self._proxy_swaps += 1
            return True
        self.set_proxy(new)
        self._proxy_swaps += 1
        self.L('prox', '已换新代理 %s' % (new or '')[:42])
        return True

    def _req(self, method, url, **kw):
        kw.setdefault('timeout', 25)
        last = None
        for attempt in range(3):
            try:
                return self.s.request(method, url, **kw)
            except requests.exceptions.ProxyError as ex:
                last = ex
                self.L('prox', '代理异常（第 %d 次），尝试换新' % (attempt + 1))
                if not self._swap_proxy():
                    raise
            except requests.exceptions.ConnectTimeout as ex:
                last = ex
                if attempt == 0 and self._swap_proxy():
                    continue
                raise
        if last:
            raise last

    def _get(self, url, **kw):
        return self._req('GET', url, **kw)

    def _post(self, url, **kw):
        return self._req('POST', url, **kw)

    @staticmethod
    def _jsonp(t):
        s = (t or '').strip()
        if not s:
            raise ValueError('empty')
        if s[0] in '{[':
            return json.loads(s)
        a, b = s.find('('), s.rfind(')')
        return json.loads(s[a + 1:b])

    def bind_inviter(self):
        """用当前账号的登录态走一遍「拉新链接」，让服务端把它记到邀请人名下。

        平台的两种绑定方式里，「点好友分享的拉新链接」这种可以自动化。
        流程：
          1) 先打开 shopping.baidu.com 种上域内 cookie
          2) 打开拉新短链，跟随全部跳转（最终会落到「百度推荐官」搜索结果页，
             地址里带加密的 refer_id）
          3) 把 refer_id 提出来，再打开一次「活动入口 + refer_id」
             —— 这一步是让活动侧真正看到邀请标识
        INVITER_URL 为空时不做任何事。返回 (ok, msg)。
        """
        if not INVITER_URL:
            return (False, '未配置邀请链接')
        try:
            try:
                self._get(SHOP + '/', headers={'Referer': 'https://m.baidu.com/'})
            except Exception:
                pass

            # 2) 短链 → 跟随全部跳转
            r = self._req('GET', INVITER_URL, allow_redirects=True, timeout=25,
                          headers={'Referer': INVITER_REFER,
                                   'Accept': 'text/html,application/xhtml+xml,'
                                             'application/json;q=0.9,*/*;q=0.8'})
            final = r.url or ''
            txt = r.text or ''
            code = getattr(r, 'status_code', '?')
            self.L('inv', '拉新链接 → HTTP %s，%d 字节' % (code, len(txt)))
            self.L('inv', '落地: %s' % final[:120])

            # 3) 从落地地址里抠 refer_id（保持原始编码，不解码）
            rid = ''
            m = re.search(r'[?&]refer_id=([^&]+)', final)
            if m:
                rid = m.group(1)
                self.L('inv', '取到 refer_id（%d 字符）' % len(rid))
            else:
                self.L('inv', '落地地址里没有 refer_id')

            # 4) 带 refer_id 再访一次活动入口
            if rid:
                act = INVITER_ACT + '&refer_id=' + rid
                try:
                    r2 = self._req('GET', act, allow_redirects=True, timeout=25,
                                   headers={'Referer': final,
                                            'Accept': 'text/html,*/*'})
                    self.L('inv', '活动入口 → HTTP %s，%d 字节'
                           % (getattr(r2, 'status_code', '?'), len(r2.text or '')))
                except Exception as ex:
                    self.L('inv', '活动入口访问失败 %s' % type(ex).__name__)

            # 5) 判断结果（能认出来的话术）
            joined = txt
            for kw in ('已绑定', '绑定成功', '绑定关系已建立', '已是好友', '邀请成功'):
                if kw in joined:
                    return (True, '绑定完成（命中「%s」）' % kw)
            for kw in ('已绑定其他', '已有邀请人', '不能重复绑定', '无法绑定'):
                if kw in joined:
                    return (False, '该账号已有邀请人，不能改绑')
            if len(joined) < 600 and ('登录' in joined or 'login' in joined.lower()):
                return (False, '链接要求登录，可能 cookie 失效')
            return (True, '已走完邀请链接（HTTP %s，refer_id %s）'
                    % (code, ('已带上' if rid else '未取到')))
        except Exception as ex:
            return (False, '绑定异常 %s: %s' % (type(ex).__name__, str(ex)[:60]))

    def panel(self):
        r = self._get(KOC_ASYNC,
                      params={'word': '优选推荐官', 'srcid': '60482',
                              'uid': self.acc.get('uid', '0')},
                      headers={'Referer': 'https://m.baidu.com/'})
        j = self._jsonp(r.text)
        if j.get('status') != 0:
            raise RuntimeError('面板失败 %s' % j.get('msg'))
        return j.get('data') or {}

    def tasks(self):
        panel = self.panel()
        out = []
        for blk in panel.get('blocks', []):
            if blk.get('component') != 'sp-referrals-task':
                continue
            d = blk.get('data') or {}
            for t in d.get('taskList', []):
                pool, srcids = [], []
                for h in t.get('hintConfig') or []:
                    sid = h.get('srcid')
                    if sid and str(sid) not in srcids:
                        srcids.append(str(sid))
                    for tu in h.get('tutorial') or []:
                        v = (tu.get('hintText') or '').strip()
                        if v and v not in pool:
                            pool.append(v)
                lc = t.get('logData') or {}
                total = t.get('totalNum') or 0
                done = t.get('finishesNum') or 0
                out.append({
                    'title': t.get('title'),
                    'type': t.get('type'),
                    'gold': t.get('gold'),
                    'double_gold': t.get('doubleGold'),
                    'total': total,
                    'done': done,
                    'left': max(0, total - done),
                    'register_url': t.get('registerUrl') or '',
                    'complete_url': t.get('completeUrl') or '',
                    'task_id': t.get('taskId') or lc.get('taskid'),
                    'srcids': srcids,
                    'hint_pool': pool,
                    'tutorial_done': t.get('taskTutorialDoneUrl') or '',
                })
        return panel, out

    def quota(self):
        panel, ts = self.tasks()
        info = {}
        for blk in panel.get('blocks', []):
            c = blk.get('component')
            if c == 'sp-referrals-task':
                d = blk.get('data') or {}
                info.update({'今日已用': d.get('todayUsage'),
                             '每日上限': d.get('todayUsageCount'),
                             '任务完成': d.get('taskCompleteCount'),
                             '任务总数': d.get('taskTotalCount')})
            elif c == 'sp-referrals-info':
                d = blk.get('data') or {}
                info.update({'用户名': d.get('username'),
                             '金币': (d.get('goldInfo') or {}).get('value'),
                             '可提现': (d.get('depositInfo') or {}).get('value'),
                             '等级': d.get('userLevel')})
        info['uid'] = panel.get('uid')
        info['tasks'] = ts
        return info

    @staticmethod
    def ftask_of(url):
        q = parse_qs(urlparse(url).query)
        raw = q.get('ftask_info', [None])[0]
        return raw, (json.loads(raw) if raw else None)

    @staticmethod
    def ftask_from_search(url):
        q = parse_qs(urlparse(url).query)
        ext = q.get('ext', [None])[0]
        if not ext:
            return ''
        o = json.loads(ext).get('ftask_info')
        if isinstance(o, dict):
            return json.dumps(o, ensure_ascii=False, separators=(',', ':'))
        return o or ''

    def _fresh_task(self, task_id, title=None):
        try:
            _panel, ts = self.tasks()
        except Exception as ex:
            self.L('pan', '刷新面板失败 %s' % type(ex).__name__)
            time.sleep(random.uniform(1.2, 2.4))
            return None
        for x in ts:
            if task_id and str(x.get('task_id')) == str(task_id):
                return x
        if title:
            for x in ts:
                if title in (x.get('title') or ''):
                    return x
        return None

    def do_cardclk(self, t, max_refresh=6, max_try=60):
        """服务端每次拉面板只下发 2 个词，用完必须重拉面板换新词。"""
        tid_key = str(t.get('task_id') or t.get('title'))
        tried = self._used_words.setdefault(tid_key, set())
        pool = [w for w in (t.get('hint_pool') or []) if w and w not in tried]
        random.shuffle(pool)
        refresh = 0
        while True:
            if self.stop_flag:
                return (0, '已停止')
            if len(tried) >= max_try:
                return (0, '已试 %d 个词仍未成功' % len(tried))
            if not pool:
                if refresh >= max_refresh:
                    return (0, '刷新多次仍无可用新词')
                refresh += 1
                nt = self._fresh_task(t.get('task_id'), t.get('title'))
                if nt and nt.get('register_url'):
                    t = nt
                pool = [w for w in ((nt or {}).get('hint_pool') or [])
                        if w and w not in tried]
                if not pool:
                    time.sleep(random.uniform(2.0, 4.0))
                    continue
                random.shuffle(pool)
                self.L('reg', '词池已换新（%d 个词）' % len(pool))
            q = pool.pop()
            if q in tried:
                continue
            tried.add(q)
            ft_raw, _obj = self.ftask_of(t.get('register_url') or '')
            cb0 = 'jsonp_%d_%d' % (int(time.time() * 1000), random.randint(1000, 9999))
            params = {'ftask_info': ft_raw, 'query': q, 'activeTab': 'tabTask',
                      'ip': '127.0.0.1', 'zid': self.acc.get('zid', ''),
                      'oncetoken': '', 'brand': 'Xiaomi', 'model': '23013RK75C',
                      'cua': '411_730_android_15.84.0.10_2.625', 'app': 'android',
                      'callback': cb0}
            r = self._get(REGISTER, params=params,
                          headers={'Referer': 'https://m.baidu.com/'})
            try:
                j = self._jsonp(r.text)
            except Exception:
                continue
            if j.get('status') != 0:
                msg = str(j.get('msg') or '')
                if 'duplicate' in msg or 'invalid' in msg:
                    self.L('reg', "词 '%s' 不可用，换下一个" % q)
                    continue
                return (0, 'register 失败 %s' % msg[:40])
            url = (j.get('data') or {}).get('url', '')
            if not url:
                return (0, '服务端未返回搜索链接')
            ft2 = self.ftask_from_search(url)
            try:
                self._get(url, headers={'Referer': 'https://shopping.baidu.com/'})
            except Exception:
                pass
            cb = 'jsonpCallback%d' % int(time.time() * 1000)
            rr = self._get(FISSION, params={'ftask_info': ft2, 'callback': cb},
                           headers={'Referer': 'https://shopping.baidu.com/spu/item'})
            cj = self._jsonp(rr.text)
            if cj.get('status') == 0:
                bonus = (cj.get('data') or {}).get('bonus', '') or ''
                m = re.search(r'(\d+)', str(bonus))
                return (int(m.group(1)) if m else 0, '词=%s' % q)
            return (0, '领奖失败 %s' % cj.get('status'))

    def do_randomsearch(self, t):
        nt = self._fresh_task(t.get('task_id'), t.get('title'))
        if nt and 'ftask_info' in (nt.get('register_url') or ''):
            t = nt
        ft_raw, obj = self.ftask_of(t.get('register_url') or '')
        ext = json.dumps({'ftask_info': obj}, ensure_ascii=False,
                         separators=(',', ':'))
        url = ('https://m.baidu.com/s?ext=%s&sa=re_activity_input_reco&word=%s'
               % (quote(ext), quote('苹果手机价格')))
        try:
            self._get(url, headers={'Referer': 'https://shopping.baidu.com/'})
        except Exception:
            pass
        cb = 'jsonpCallback%d' % int(time.time() * 1000)
        rr = self._get(FISSION, params={'ftask_info': ft_raw, 'callback': cb},
                       headers={'Referer': 'https://shopping.baidu.com/spu/item'})
        cj = self._jsonp(rr.text)
        if cj.get('status') == 0:
            bonus = (cj.get('data') or {}).get('bonus', '') or ''
            m = re.search(r'(\d+)', str(bonus))
            return ((int(m.group(1)) if m else 0), '随机搜索')
        return (0, '领奖失败 %s' % cj.get('status'))

    def do_jump(self, t):
        cu = t.get('complete_url') or ''
        if not cu or 'ftask_info' not in cu:
            return (0, '无 completeUrl')
        ft_raw, _obj = self.ftask_of(cu)
        ru = t.get('register_url') or ''
        if ru.startswith('http'):
            try:
                self._get(ru)
            except Exception:
                pass
        cb = 'jsonpCallback%d' % int(time.time() * 1000)
        rr = self._get(JUMP, params={'ftask_info': ft_raw, 'callback': cb},
                       headers={'Referer': 'https://shopping.baidu.com/'})
        cj = self._jsonp(rr.text)
        if cj.get('status') == 0:
            return (0, '已领（券本身不发金币）')
        return (0, '失败 %s' % cj.get('status'))

    def dress_progress(self, task_id):
        r = self._get(DRESS_BASE + '/api/v1/task/progress',
                      params={'taskId': task_id, 'taskType': DRESS_TYPE},
                      headers={'Referer': DRESS_BASE + '/',
                               'Origin': DRESS_BASE})
        if r.status_code != 200:
            return {}
        try:
            return r.json() or {}
        except Exception:
            return {}

    def do_dress(self, t, notice=None):
        """每 3 次 query 记 1 轮，循环由服务端 completedRounds 驱动。"""
        q = parse_qs(urlparse(t.get('register_url') or '').query)
        task_id = q.get('task_id', [''])[0]
        if not task_id:
            return (0, '无 task_id')
        try:
            self._get(t.get('register_url'))
        except Exception:
            pass
        p = self.dress_progress(task_id)
        if not p:
            return (0, '查不到进度')
        if p.get('allCompleted'):
            return (0, '已全部完成')
        total = t.get('total') or 0
        done = p.get('completedRounds') or 0
        in_round = p.get('currentRoundDone') or 0
        PER = 3
        need = max(0, total - done)
        if need <= 0:
            return (0, '已达总轮数')
        max_submit = PER - in_round + (need - 1) * PER + 6
        self.L('dress', '进度 %s/%s 轮，本轮 %s/%s，预计提交 ≤%s 次'
                % (done, total, in_round, PER, max_submit))
        pool = []
        try:
            r = self._post(DRESS_BASE + '/api/v1/chat/suggestions',
                           data=b'{"scene":"home","source":"home"}',
                           headers={'Content-Type': 'application/json',
                                    'Referer': DRESS_BASE + '/',
                                    'Origin': DRESS_BASE})
            pool = (r.json() or {}).get('suggestions') or []
        except Exception:
            pool = []
        if not pool:
            pool = ['今天穿什么合适', '上班穿搭推荐', '约会怎么搭配',
                    '显高显瘦技巧', '冬季保暖穿搭', '面试着装建议']
        won = 0
        sub = 0
        while sub < max_submit:
            if self.stop_flag:
                break
            cur = self.dress_progress(task_id)
            if cur.get('allCompleted') or (cur.get('completedRounds') or 0) >= total:
                break
            query = random.choice(pool)
            sub += 1
            j = {}
            try:
                r = self._post(DRESS_BASE + '/api/v1/task/record-dialogue',
                               data=json.dumps({'taskId': task_id,
                                                'taskType': DRESS_TYPE,
                                                'query': query},
                                               ensure_ascii=False).encode('utf-8'),
                               headers={'Content-Type': 'application/json',
                                        'Referer': DRESS_BASE + '/',
                                        'Origin': DRESS_BASE})
                j = r.json() or {}
            except Exception:
                j = {}
            if j.get('justCompleted'):
                won += 1
                c = j.get('coinsAwarded') or 0
                self.L('win', '★ 完成第 %s 轮 +%s 金币' % (j.get('completedRounds'), c))
                if notice:
                    notice(c)
                if j.get('allCompleted'):
                    break
            time.sleep(random.randint(3, 7))
        return (won * (t.get('gold') or 0), '完成 %d 轮 / 提交 %d 次' % (won, sub))

    def revenue(self):
        r = self._get(SHOP + '/koc/revenue_center',
                      params={'pn': '1', 'rn': '10', 'type': '0'},
                      headers={'Referer': SHOP + '/'})
        h = r.text
        # 诊断：先确认拿到的到底是什么（登录页 / 空页 / 正常页）
        self.L('rev', '收益页 HTTP %s 共 %d 字节' % (getattr(r, 'status_code', '?'), len(h)))
        if not h or len(h) < 500:
            self.L('bad', '收益页内容过短，可能登录态失效：%s'
                   % (h[:160].replace('\n', ' ') if h else '(空)'))

        # 兼容几种可能的排版（有无空格），别因为一个空格就整条提现链全废
        cands = [
            '"component":"sp-income-overview","data":',
            '"component": "sp-income-overview", "data":',
            '"sp-income-overview","data":',
            '"sp-income-overview":',
        ]
        i, hit = -1, ''
        for k in cands:
            i = h.find(k)
            if i >= 0:
                hit = k
                break
        if i < 0:
            self.L('bad', '收益页里找不到 sp-income-overview（页面可能改版或登录失效）')
            self.L('bad', '页面开头 200 字：%s' % h[:200].replace('\n', ' '))
            raise RuntimeError('页面里找不到 sp-income-overview')
        self.L('rev', '命中结构: %s' % hit)

        dec = json.JSONDecoder()
        try:
            obj, _end = dec.raw_decode(h[i + len(hit):])
        except Exception as ex:
            self.L('bad', '收益 JSON 解析失败 %s，片段：%s'
                   % (type(ex).__name__, h[i:i + 200].replace('\n', ' ')))
            raise
        out = dict(obj)
        self.L('rev', '解析到字段: %s' % ','.join(sorted(out.keys()))[:180])
        try:
            panel, _t = self.tasks()
            for b in panel.get('blocks', []):
                if b.get('component') == 'sp-referrals-info':
                    d = b.get('data') or {}
                    out['gold'] = (d.get('goldInfo') or {}).get('value')
                    out['deposit'] = (d.get('depositInfo') or {}).get('value')
        except Exception:
            pass
        rate = 14000
        try:
            rm = json.loads(out.get('convertRateMap') or '{}')
            rate = rm.get(str(out.get('userlevel') or 1), 14000)
        except Exception:
            pass
        out['rate'] = rate
        return out

    def _anti(self, rev):
        a = [('ip', rev.get('cip', '') or ''),
             ('zid', self.acc.get('zid', '') or ''),
             ('oncetoken', ''),
             ('brand', 'Xiaomi'),
             ('model', '23013RK75C'),
             ('cua', '411_730_android_142.0.7444.58_2.625'),
             ('app', 'android')]
        return ''.join('&%s=%s' % (k, v) for k, v in a)

    def convert_all(self):
        rev = self.revenue()
        gold = int(float(rev.get('gold') or 0))
        rate = int(rev.get('rate') or 14000)
        min_coin = rate // 100
        self.L('conv', '金币 %s 兑换率 %s:1 最少 %s 金币 可提现 %s'
                % (gold, rate, min_coin, rev.get('cashableIncom')))
        if gold < min_coin:
            return (False, '金币 %s 不足最低兑换额 %s' % (gold, min_coin))
        commission = '%.2f' % (int(gold * 100 // rate) / 100.0)
        url = ('%s/koc/v2/convert?coin=%s&commission=%s%s'
               % (SHOP, gold, commission, self._anti(rev)))
        r = self._get(url, headers={'Referer': SHOP + '/koc/revenue_center'})
        try:
            j = r.json()
        except Exception:
            return (False, '非 JSON: %s' % r.text[:120])
        d = j.get('data') or {}
        if d.get('errText'):
            return (False, d['errText'])
        if d.get('finalCommission'):
            self.L('conv', '★ 兑换成功 金币→%s 现金→%s'
                    % (d.get('finalCoin'), d.get('finalCommission')))
            return (True, '兑换 %s 金币 → %s 元' % (gold, d.get('finalCommission')))
        return (False, '兑换未成功: %s' % json.dumps(j, ensure_ascii=False)[:160])

    def withdraw_max(self):
        rev = self.revenue()
        cash = float(rev.get('cashableIncom') or 0)
        items = rev.get('topCashItems') or []
        tiers = []
        for it in items:
            try:
                tiers.append(float(it.get('topCashAmount')))
            except Exception:
                pass
        if not tiers:
            tiers = [float(x) for x in (rev.get('topCashs') or []) if x]
        tiers.sort()
        usable = [t for t in tiers if t <= cash + 1e-09]
        self.L('wd', '可提现 %s 元，档位 %s，可用 %s' % (cash, tiers, usable))
        if not usable:
            low = tiers[0] if tiers else '?'
            return (False, '可提现 %s 元，不足最低档 %s 元' % (cash, low))
        amt = max(usable)
        url = ('%s/koc/v2/withdraw?changeValue=%s%s'
               % (SHOP, ('%g' % amt), self._anti(rev)))
        r = self._get(url, headers={'Referer': SHOP + '/koc/revenue_center'})
        try:
            j = r.json()
        except Exception:
            return (False, '非 JSON: %s' % r.text[:120])
        d = j.get('data') or {}
        if d.get('errText'):
            return (False, d['errText'])
        if d.get('finalCommission'):
            self.L('wd', '★ 提现成功 %g 元，余额剩 %s'
                    % (amt, d.get('finalCommission')))
            return (True, '提现 %g 元成功' % amt)
        return (False, '提现 %g 元失败（余额充足），通常是未绑定支付宝或未实名，请到百付宝绑定后再试' % amt)

    def cash_out(self):
        ok1, m1 = self.convert_all()
        self.L('cash', '兑换：%s' % m1)
        ok2, m2 = self.withdraw_max()
        self.L('cash', '提现：%s' % m2)
        return (ok1 or ok2, '%s；%s' % (m1, m2))

    def run(self, which=None, notice=None):
        """which: None=全部可做；或 {'cardClk','randomSearch','jump','dress'} 子集。"""
        which = which or {'cardClk', 'randomSearch', 'dress', 'jump'}
        panel, ts = self.tasks()
        gold = 0
        ok = 0
        fail = 0
        for t in ts:
            if self.stop_flag:
                break
            if t['left'] <= 0:
                continue
            ty = t['type']
            try:
                if ty == 'cardClk' and 'cardClk' in which and t['hint_pool']:
                    done = 0
                    miss = 0
                    while done < t['left'] and miss < 4:
                        if self.stop_flag:
                            break
                        g, note = self.do_cardclk(t)
                        if g > 0:
                            gold += g
                            ok += 1
                            done += 1
                            miss = 0
                            self.L('ok', '%s %s +%s  累计%s'
                                   % (t['title'], note, g, gold))
                        else:
                            miss += 1
                            fail += 1
                            self.L('bad', '%s %s（连续失败 %d/4）'
                                   % (t['title'], note, miss))
                            if miss >= 4:
                                break
                            time.sleep(random.uniform(3, 6))
                            continue
                        if notice:
                            notice(g)
                        time.sleep(max(6, min(28, int(random.gauss(12, 4)))))

                elif ty == 'randomSearch' and 'randomSearch' in which:
                    done = 0
                    miss = 0
                    while done < t['left'] and miss < 4:
                        if self.stop_flag:
                            break
                        g, note = self.do_randomsearch(t)
                        if g > 0:
                            gold += g
                            ok += 1
                            done += 1
                            miss = 0
                            self.L('ok', '%s +%s  累计%s' % (t['title'], g, gold))
                        else:
                            miss += 1
                            fail += 1
                            self.L('bad', '%s %s（连续失败 %d/4）'
                                   % (t['title'], note, miss))
                            if miss >= 4:
                                break
                            time.sleep(random.uniform(3, 6))
                            continue
                        if notice:
                            notice(g)
                        time.sleep(max(5, min(20, int(random.gauss(9, 3)))))

                elif ty == 'jump' and 'jump' in which:
                    g, note = self.do_jump(t)
                    ok += 1
                    self.L('ok', '%s %s' % (t['title'], note))

                elif (ty == 'callback' and 'dress' in which
                      and '穿搭' in (t['title'] or '')):
                    g, note = self.do_dress(t, notice)
                    if g > 0 or '完成' in note:
                        ok += 1
                        gold += g
                        self.L('ok', '%s %s +%s' % (t['title'], note, g))
                    else:
                        fail += 1
                        self.L('bad', '%s %s' % (t['title'], note))

                elif ty == 'callback':
                    self.L('skip', '%s 需 App 内完成，跳过' % t['title'])
            except Exception as ex:
                fail += 1
                self.L('err', '%s 异常 %s: %s'
                       % (t['title'], type(ex).__name__, str(ex)[:60]))
                continue
        return {'gold': gold, 'ok': ok, 'fail': fail}


# ============================================================ 青龙主逻辑
def _env(name, default=''):
    v = os.environ.get(name)
    return default if v is None or str(v).strip() == '' else str(v).strip()


def _env_list(name):
    raw = _env(name)
    if not raw:
        return []
    parts = []
    for sep in ('\n', '&', '|'):
        if sep in raw:
            raw = raw.replace(sep, '\n')
    for line in raw.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            parts.append(line)
    return parts


def _log(msg):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), msg), flush=True)


def _parse_accounts():
    """从 BD_ACCOUNTS / BD_CK / BD_BDUSS 组装账号列表

    BD_ACCOUNTS 格式（手机号密码登录）：
        备注#手机号#密码          或      手机号#密码
    多账号用换行或 & 分隔。

    BD_CK 格式：完整 cookie（BDUSS=xxx; BAIDUID=yyy; ...）
    BD_BDUSS 格式：只有 BDUSS 值
    """
    accs = []
    idx = 0
    # ① BD_ACCOUNTS：手机号#密码（优先，因为能自己续期）
    for part in _env_list('BD_ACCOUNTS'):
        bits = [x.strip() for x in part.split('#')]
        bits = [x for x in bits if x != '']
        if len(bits) < 2:
            _log('BD_ACCOUNTS 第 %d 条格式不对（要 备注#手机号#密码）：%s'
                 % (idx + 1, part[:40]))
            continue
        idx += 1
        remark = bits[0] if len(bits) >= 3 else ''
        phone = bits[-2]
        pwd = bits[-1]
        accs.append({'phone': phone, 'password': pwd,
                     'remark': remark or phone, 'cookie': '', 'bduss': '',
                     'uid': '', 'zid': '', 'cuid': ''})
    # ② BD_CK：完整 cookie
    for ck in _env_list('BD_CK'):
        idx += 1
        ck = ck.replace(', ', '; ')
        bduss = ''
        m = re.search(r'BDUSS=([^;]+)', ck)
        if m:
            bduss = m.group(1).strip()
        if not bduss:
            _log('第 %d 个 BD_CK 里没有 BDUSS，跳过' % idx)
            continue
        accs.append({'phone': 'ql%d' % idx, 'remark': '号%d' % idx,
                     'cookie': ck, 'bduss': bduss, 'uid': '', 'zid': '', 'cuid': ''})
    # ③ BD_BDUSS：只给 BDUSS
    for b in _env_list('BD_BDUSS'):
        idx += 1
        b = b.strip()
        if not b or len(b) < 60:
            continue
        accs.append({'phone': 'ql%d' % idx, 'remark': '号%d' % idx,
                     'cookie': '', 'bduss': b, 'uid': '', 'zid': '', 'cuid': ''})
    return accs


# ---------------------------------------------------------- 手机号密码登录
_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'bd_login_cache.json')


def _cache_read():
    try:
        with open(_CACHE_PATH, encoding='utf-8') as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _cache_write(d):
    try:
        with open(_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def _login_by_password(acc, use_cache=True):
    """用手机号+密码登录拿 BDUSS。返回 (ok, cookie 或 错误说明)

    登录成功的 BDUSS/cuid/zid 会缓存到 bd_login_cache.json，
    下次优先用缓存（BDUSS 一般能撑很久，不用每次登录，减少触发二次验证）。
    """
    phone = acc.get('phone') or ''
    pwd = acc.get('password') or ''
    if not phone or not pwd:
        return False, '缺手机号或密码'

    cache = _cache_read()
    if use_cache and cache.get(phone, {}).get('bduss'):
        c = cache[phone]
        _log('  用缓存的登录态（%s 保存）' % c.get('at', '?'))
        return True, {'bduss': c['bduss'], 'cuid': c.get('cuid', ''),
                      'zid': c.get('zid', '')}

    _log('  手机号密码登录：%s' % phone)
    try:
        lg = Login(proxy=acc.get('proxy'), timeout=30)
        ok, data = lg.do_login(phone, pwd)
    except Exception as ex:
        return False, '登录异常 %s: %s' % (type(ex).__name__, str(ex)[:100])

    if ok:
        _log('  登录成功  cuid=%s... zid=%s...' % (str(data.get('cuid'))[:8],
                                                 str(data.get('zid'))[:8]))
        cache[phone] = {'bduss': data['bduss'], 'cuid': data.get('cuid', ''),
                        'zid': data.get('zid', ''),
                        'at': time.strftime('%Y-%m-%d %H:%M')}
        _cache_write(cache)
        return True, data

    no = str(data.get('no') or '')
    msg = data.get('msg') or ''
    if no == '400023':
        return False, ('需要短信二次验证（400023）—— 青龙跑不了手工验证码。'
                       '请改用 BD_CK 或 BD_BDUSS（浏览器里拿一次 cookie 即可）')
    if no == '400011':
        return False, '账号或密码错误（400011）'
    if no == '230051':
        return False, '手机号格式有误（230051）'
    return False, '登录失败 %s %s' % (no, msg)



def main():
    accts = _env_list('BD_ACCOUNTS')
    cks = _env_list('BD_CK')
    bduss = _env_list('BD_BDUSS')
    if not accts and not cks and not bduss:
        _log('请先设置环境变量（任选一个）：')
        _log('  BD_ACCOUNTS = 备注#手机号#密码     （推荐，脚本自己登录）')
        _log('  BD_CK       = 完整 cookie         （BDUSS=xxx; BAIDUID=yyy; ...）')
        _log('  BD_BDUSS    = 只有 BDUSS 的值')
        return 1

    withdraw = _env('BD_WITHDRAW', '1') == '1'
    wd_min = float(_env('BD_WITHDRAW_MIN', '1') or 1)
    task_limit = int(_env('BD_TASK_LIMIT', '0') or 0)
    gap_min = float(_env('BD_GAP_MIN', '6') or 6)
    gap_max = float(_env('BD_GAP_MAX', '12') or 12)
    # 邀请链接写死内置，不能关（这是分发给别人用时的核心）
    inv_url = _DEFAULT_INVITER
    globals()['INVITER_URL'] = inv_url

    proxys = _env_list('BD_PROXY')
    accs = _parse_accounts()
    _log('共 %d 个账号' % len(accs))
    _log('配置：提现=%s（门槛 %s 元） 单号任务上限=%s 间隔=%s~%s 秒 邀请=%s'
         % (withdraw, wd_min, task_limit or '不限', gap_min, gap_max,
            '有' if inv_url else '无'))
    print('-' * 60, flush=True)

    summary = []
    for i, acc in enumerate(accs, 1):
        tag = acc.get('remark') or acc.get('phone')
        _log('===== [%d/%d] %s =====' % (i, len(accs), tag))
        px = proxys[i - 1] if i - 1 < len(proxys) else (proxys[0] if len(proxys) == 1 else None)
        line = {'tag': tag, 'ok': 0, 'fail': 0, 'gold': 0, 'msg': ''}
        try:
            # ① 手机号+密码 → 先登录拿 BDUSS（成功会缓存，下次优先用缓存）
            if not acc.get('cookie') and not acc.get('bduss') and acc.get('password'):
                okL, dataL = _login_by_password(acc)
                if not okL:
                    _log('  登录失败：%s' % dataL)
                    line['msg'] = '登录失败: %s' % str(dataL)[:40]
                    summary.append(line)
                    continue
                acc['bduss'] = dataL['bduss']
                if dataL.get('cuid'):
                    acc['cuid'] = dataL['cuid']
                if dataL.get('zid'):
                    acc['zid'] = dataL['zid']
                _log('  BDUSS 已拿到（%d 字符）' % len(acc['bduss']))

            # ② 有 BDUSS 没 cookie → 换完整 cookie
            if not acc.get('cookie') and acc.get('bduss'):
                ck = build_cookie(acc['bduss'], acc.get('cuid'), acc.get('zid'))
                if not ck:
                    _log('  cookie 构建失败（BDUSS 可能失效）')
                    line['msg'] = 'cookie 构建失败'
                    summary.append(line)
                    continue
                acc['cookie'] = ck
            _log('  cookie %d 字符' % len(acc.get('cookie') or ''))

            eng = Engine(acc, px, log=lambda t, lv, m: _log('  [%s] %s' % (t, m)))
            info = eng.quota()
            _log('  昵称=%s 金币=%s 可提现=%s 今日已用=%s/%s'
                 % (info.get('用户名'), info.get('金币'), info.get('可提现'),
                    info.get('今日已用'), info.get('每日上限')))

            # 绑邀请（如果配了）
            if inv_url:
                try:
                    okb, msgb = eng.bind_inviter()
                    _log('  邀请绑定: %s' % msgb)
                except Exception as ex:
                    _log('  邀请绑定异常 %s' % type(ex).__name__)

            # 做任务
            tasks = info.get('tasks') or []
            available = [t for t in tasks if (t.get('left') or 0) > 0]
            _log('  可做任务 %d 个：%s' % (len(available),
                 ', '.join('%s×%s' % (t.get('type'), t.get('left')) for t in available[:6])))
            if task_limit and len(available) > task_limit:
                available = available[:task_limit]

            # 注意：Engine.run 内部自己带了拟人节奏
            #   time.sleep(max(6, min(28, int(random.gauss(12, 4)))))
            # 也就是每个任务之间 6~28 秒（均值 12），不需要外部再控速。
            res = eng.run(notice=lambda g: _log('  ★ +%s 金币' % g))
            line['ok'] = res.get('ok', 0)
            line['fail'] = res.get('fail', 0)
            line['gold'] = res.get('gold', 0)
            _log('  任务完成：成功 %s 失败 %s 金币 +%s'
                 % (line['ok'], line['fail'], line['gold']))

            # 复查余额
            try:
                info2 = eng.quota()
                _log('  现在：金币=%s 可提现=%s' % (info2.get('金币'), info2.get('可提现')))
                line['msg'] = '金币%s 可提%s' % (info2.get('金币'), info2.get('可提现'))
            except Exception:
                pass

            # 提现
            if withdraw:
                cash = 0
                try:
                    cash = float(info2.get('可提现') or 0)
                except Exception:
                    cash = 0
                if cash >= wd_min:
                    okw, msgw = eng.cash_out()
                    _log('  兑换提现：%s' % msgw)
                    line['msg'] += ' | 提现:%s' % ('成功' if okw else '待观察')
                else:
                    _log('  可提现 %s 元 < 门槛 %s 元，今天先不提' % (cash, wd_min))
        except Exception as ex:
            _log('  账号异常 %s: %s' % (type(ex).__name__, str(ex)[:120]))
            if _env('BD_DEBUG', '1') == '1':
                traceback.print_exc()
            line['msg'] = '异常 %s' % type(ex).__name__
        summary.append(line)
        if i < len(accs):
            time.sleep(random.uniform(3, 8))

    print('-' * 60, flush=True)
    _log('===== 汇总 =====')
    for s in summary:
        _log('  %-8s 成功%-3s 失败%-3s 金币+%-6s %s'
             % (s['tag'], s['ok'], s['fail'], s['gold'], s['msg']))

    # 通知（青龙自带 sendNotify 就调用）
    try:
        body = '\n'.join('%s: 成功%s 失败%s 金币+%s %s'
                         % (s['tag'], s['ok'], s['fail'], s['gold'], s['msg'])
                         for s in summary)
        if 'notify' in sys.modules or os.path.exists('/ql/data/scripts/notify.py'):
            sys.path.insert(0, '/ql/data/scripts')
        import notify
        notify.send('百度推荐官', '今日结果\n' + body)
        _log('  通知已发送')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _log('用户中断')
        sys.exit(130)
    except Exception as ex:
        _log('脚本异常 %s: %s' % (type(ex).__name__, str(ex)[:200]))
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