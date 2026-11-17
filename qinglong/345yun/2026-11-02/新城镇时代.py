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
"""新城镇时代
下载链接:
https://ntsh.onlinecards.cn/#/
邀请码:
0B1BA4AF

支持的玩法（实测全部跑通）：
     体检：余额 / 任务 / 签到状态 / 会员进度 / 果园牧场
     刷农场会员广告 → 20 条换 2 天会员（买要 5 元）→ 自动领奖
     农场干活：收 / 浇 / 施 / 种（会员托管生效时可以跳过）

──────────────────────── 环境变量 ────────────────────────
必填：
    NTS_TOKEN     主站 Authorization 的 token（32 位 hex）
                  多账号用 & 或换行分隔

可选：
    NTS_MEMBER    1=刷会员广告（默认 1）
    NTS_FARM      1=农场干活（默认 1）
    NTS_SEC       每条广告"播放"秒数（默认 20，真机约 45）
    NTS_MAX       本次最多刷几条（默认 0=不限，刷满为止）
    NTS_FORCE     1=即使会员没过期也继续刷（默认 0，只在剩余天数 <2 时才刷）
    NTS_DC        默认设备码（不写在 token 后面时用这个）

──────────────────────── 定时建议 ────────────────────────
    0 8 * * *       每天早上 8 点刷一轮

──────────────────────── 怎么拿 token ────────────────────
手机上打开 App → 抓包 → 任意 nts.dxiangmu.com 请求头的 Authorization，
去掉 "Bearer " 前缀后的那串就是。
"""
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# ---------------------------------------------------------------- 常量
APP_BASE = "https://nts.dxiangmu.com/app-api"
GAME_BASE = "https://ntegame.dxiangmu.com"
UA = ("Mozilla/5.0 (Linux; Android 15; 2203121C Build/AQ3A.250226.002; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0 Mobile Safari/537.36")
DEF_DC = "B6972F821EF71CB52A4352E7A6169922"
APP_V = "3105"
MEMBER_MODULE = "FARM_MEMBER"

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def md5(s):
    return hashlib.md5(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def fei(seed):
    """服务端要的 fei = md5(md5(x))，两层都是小写 hex。实测逐字命中。"""
    return md5(md5(seed))


def env_int(name, default=0):
    try:
        return int(str(os.environ.get(name, default)).strip() or default)
    except Exception:
        return default


# ---------------------------------------------------------------- HTTP
def _http(url, method="GET", headers=None, body=None, timeout=20):
    data = None
    if body is not None and method != "GET":
        data = json.dumps(body, separators=(",", ":")).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        raise RuntimeError("HTTP %s: %s" % (e.code, txt[:160]))
    except Exception as e:
        raise RuntimeError("%s: %s" % (type(e).__name__, e))


class Nts:
    """主站客户端。"""

    def __init__(self, token, dc=DEF_DC):
        t = (token or "").strip()
        if t.lower().startswith("bearer "):
            t = t[7:].strip()
        self.token = t
        self.dc = dc or DEF_DC
        self._last = 0.0

    def req(self, path, method="GET", params=None, body=None, gap=0.4):
        url = APP_BASE + path
        if params:
            q = "&".join("%s=%s" % (urllib.parse.quote(str(k), safe=""),
                                    urllib.parse.quote(str(v), safe=""))
                         for k, v in params.items())
            url += ("&" if "?" in url else "?") + q
        h = {"Content-Type": "application/json;charset=UTF-8",
             "Authorization": "Bearer " + self.token,
             "Dc": self.dc, "V": APP_V, "user-agent": UA}
        if gap and self._last:
            w = self._last + gap - time.time()
            if w > 0:
                time.sleep(w)
        self._last = time.time()
        return _http(url, method, h, body)

    # ---- 读
    def userinfo(self):
        return (self.req("/user/info").get("data") or {})

    def balance(self):
        d = self.req("/user/wallet/personal").get("data") or {}
        return float(d.get("balance") or 0)

    def member_task(self):
        a = self.req("/user/farmMember/config/task/list").get("data") or []
        return a[0] if a else {}

    def member_status(self):
        return (self.req("/user/farmMember/config/user/get").get("data") or {})

    # ---- 会员广告
    def member_slot(self):
        r = self.req("/user/farmMember/ad/adId")
        if r.get("code") != 0:
            raise RuntimeError("取广告位失败: %s" % r.get("msg"))
        return r.get("data"), r.get("extra") or ""

    def member_start(self, task_id=1):
        _, extra = self.member_slot()
        r = self.req("/user/farmMember/ad/ads/" + MEMBER_MODULE, "PUT",
                     {"fromModule": MEMBER_MODULE, "taskId": task_id,
                      "fei": fei(MEMBER_MODULE + extra)})
        if r.get("code") != 0 or not r.get("data"):
            raise RuntimeError("申请广告失败: %s" % (r.get("msg") or r))
        return str(r["data"]), extra

    def member_beat(self, flow, extra):
        return self.req("/user/farmMember/ad/adh/" + flow, "PUT",
                        {"flowCode": flow, "fei": fei(flow + extra)}, gap=0.2)

    def member_close(self, flow, extra, finished=True):
        f = fei(flow + extra)
        # ★ adCloseFlag 必填，缺了服务端 400 且广告不算完成
        return self.req("/user/farmMember/ad/adc/" + flow, "PUT",
                        {"flowCode": flow, "fei": f,
                         "adCloseFlag": "true" if finished else "false"}, gap=0.2)

    def member_claim(self, task_id=1):
        return self.req("/user/farmMember/reward/%s" % task_id, "PUT", None, {})


def watch_member_ad(api, task_id=1, seconds=20, beat=3):
    """刷一条，返回是否计入。"""
    flow, extra = api.member_start(task_id)
    t0 = time.time()
    while time.time() - t0 < seconds:
        try:
            api.member_beat(flow, extra)
        except RuntimeError:
            pass
        time.sleep(beat)
    try:
        api.member_close(flow, extra, True)
    except RuntimeError as e:
        log("    关闭广告失败：%s" % e)
        return False
    f = fei(flow + extra)
    try:
        r = api.req("/user/farmMember/ad/adg/" + flow, "GET",
                    {"flowCode": flow, "fei": f}, gap=0.2)
    except RuntimeError as e:
        log("    核对失败：%s" % e)
        return False
    ok = bool(r.get("data"))
    log("    flowCode=%s → %s" % (flow, "计入" if ok else "未计入"))
    return ok


# ---------------------------------------------------------------- 游戏
class Game:
    def __init__(self, app_token):
        self.app_token = (app_token or "").strip()
        if self.app_token.lower().startswith("bearer "):
            self.app_token = self.app_token[7:].strip()
        self.access = None
        self.user_id = None

    def _req(self, path, method="GET", body=None, gap=0.4):
        url = GAME_BASE + path
        h = {"Accept": "application/json", "Content-Type": "application/json",
             "user-agent": UA, "X-Requested-With": "uni.CHAOWANPRO",
             "Origin": GAME_BASE,
             "Referer": GAME_BASE + "/games/fantasia/index.html"}
        if self.access:
            h["Authorization"] = "Bearer " + self.access
        data = None
        if body is not None and method != "GET":
            data = json.dumps(body, separators=(",", ":")).encode()
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        if gap:
            time.sleep(gap)
        return _http(url, method, h, body)

    @staticmethod
    def _d(r):
        if r.get("code") != 200 or r.get("success") is False:
            raise RuntimeError("%s（code=%s）" % (r.get("message") or "失败", r.get("code")))
        return r.get("data")

    def login(self):
        d = self._d(self._req("/api/v1/auth/app-token", "POST",
                              {"app_token": self.app_token}, gap=0))
        self.access = d.get("access_token")
        self.user_id = ((d.get("user") or {}).get("id"))
        if not self.access:
            raise RuntimeError("换不到 access_token")
        return self.access

    def get(self, p):
        return self._d(self._req(p))

    def post(self, p, body=None):
        return self._d(self._req(p, "POST", body or {}))

    def auto(self):
        return self.get("/api/v1/fantasia/auto")

    def orchard(self, fruit):
        return self.get("/api/v1/fantasia/orchards/%s" % fruit)

    def harvest(self, f):
        return self.post("/api/v1/fantasia/orchards/%s/harvest" % f)

    def water(self, f):
        return self.post("/api/v1/fantasia/orchards/%s/water" % f)

    def fertilize(self, f):
        return self.post("/api/v1/fantasia/orchards/%s/fertilize" % f)

    def plant(self, f):
        return self.post("/api/v1/fantasia/orchards/%s/plant" % f)

    def fruits(self):
        try:
            st = self.get("/api/v1/fantasia/state")
            fr = ((st.get("catalog") or {}).get("fruits") or [])
            return [x.get("code") for x in fr if x.get("code")]
        except Exception:
            return ["apple", "pear", "orange"]


# ---------------------------------------------------------------- 每个账号
def run_account(tag, token, dc, do_member, do_farm, sec, cap, force):
    log("───── 账号 %s" % tag)
    api = Nts(token, dc)

    u = api.userinfo()
    if not u.get("userId"):
        log("  ✗ token 无效或已失效，跳过")
        return False
    log("  %s（%s）%s" % (u.get("nickname"), u.get("userId"),
                          "已实名" if u.get("realStatus") else "未实名"))
    bal = api.balance()
    log("  余额 %.2f 元" % bal)

    # ---- ① 会员
    if do_member:
        try:
            t = api.member_task()
            st = api.member_status()
            do, had = int(t.get("doCount") or 0), int(t.get("hadDoCount") or 0)
            exp = st.get("expirationTime")
            log("  会员任务 %s：%s/%s，当前 memberType=%s 到期 %s" % (
                t.get("taskName"), had, do, st.get("memberType"), exp))

            # 算剩余天数，判断要不要刷
            left_days = None
            if exp:
                try:
                    dt = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")
                    left_days = (dt - datetime.now()).total_seconds() / 86400
                except Exception:
                    pass
            need = force or left_days is None or left_days < 2

            if t.get("taskStatus") == 2:
                r = api.member_claim(int(t.get("id") or 1))
                log("  ★ 直接领奖：%s" % json.dumps(r, ensure_ascii=False)[:100])
                st2 = api.member_status()
                log("     memberType=%s 到期 %s" % (st2.get("memberType"),
                                                    st2.get("expirationTime")))
            elif need and had < do:
                todo = do - had
                if cap > 0:
                    todo = min(todo, cap)
                log("  刷 %d 条会员广告（每条约 %d 秒）" % (todo, sec))
                okn = 0
                for i in range(todo):
                    try:
                        if watch_member_ad(api, int(t.get("id") or 1), sec):
                            okn += 1
                            log("  ✓ %d/%d" % (okn, todo))
                        else:
                            log("  ✗ 第 %d 条未计入，停止" % (i + 1))
                            break
                    except RuntimeError as e:
                        log("  ✗ 第 %d 条异常：%s" % (i + 1, e))
                        break
                    time.sleep(2)
                t2 = api.member_task()
                log("  进度 %s/%s taskStatus=%s" % (t2.get("hadDoCount"),
                                                    t2.get("doCount"), t2.get("taskStatus")))
                if t2.get("taskStatus") == 2:
                    api.member_claim(int(t2.get("id") or 1))
                    st2 = api.member_status()
                    log("  ★ 已领奖，memberType=%s 到期 %s" % (
                        st2.get("memberType"), st2.get("expirationTime")))
            else:
                log("  会员还有 %.1f 天，本轮不刷" % (left_days or 0))
        except RuntimeError as e:
            log("  ✗ 会员流程失败：%s" % e)

    # ---- ② 农场
    if do_farm:
        try:
            g = Game(token)
            g.login()
            au = g.auto()
            active = ((au.get("member") or {}).get("active"))
            log("  游戏托管：%s" % ("已开启（会员自动驾驶）" if active else "未开启"))
            acts = 0
            for f in g.fruits():
                try:
                    o = g.orchard(f)
                except RuntimeError:
                    continue
                t = o.get("tools") or {}
                nm = (o.get("fruit") or {}).get("name") or f
                for key, fn in (("harvestable", g.harvest), ("waterable", g.water),
                                ("fertilizable", g.fertilize)):
                    if int(t.get(key) or 0) > 0:
                        try:
                            fn(f)
                            acts += 1
                            log("    %s %s %s 块" % (nm, key.replace("able", ""), t.get(key)))
                        except RuntimeError as e:
                            log("    %s %s 失败：%s" % (nm, key, e))
                if int(t.get("plantable") or 0) > 0 and float(t.get("seed_stock") or 0) > 0:
                    try:
                        g.plant(f)
                        acts += 1
                        log("    %s 补种" % nm)
                    except RuntimeError as e:
                        log("    %s 补种失败：%s" % (nm, e))
            log("  农场动作 %d 个%s" % (acts, "（有托管时可能已自动处理）" if active else ""))
        except RuntimeError as e:
            log("  ✗ 农场失败：%s" % e)
    return True


def parse_accounts():
    raw = os.environ.get("NTS_TOKEN", "").strip()
    if not raw:
        return []
    raw = raw.replace("\r", "")
    parts = []
    for chunk in raw.split("&"):
        for line in chunk.split("\n"):
            line = line.strip()
            if line:
                parts.append(line)
    out = []
    default_dc = os.environ.get("NTS_DC", "").strip() or DEF_DC
    for i, p in enumerate(parts, 1):
        if "|" in p:
            tok, dc = p.split("|", 1)
            out.append(("第%d个" % i, tok.strip(), dc.strip() or default_dc))
        else:
            out.append(("第%d个" % i, p, default_dc))
    return out


def main():
    accs = parse_accounts()
    if not accs:
        log("✗ 没配 NTS_TOKEN。在青龙「环境变量」里加一条：")
        log("   NTS_TOKEN = <抓包里 Authorization 去掉 Bearer 后面那串>")
        return 2

    do_member = os.environ.get("NTS_MEMBER", "1").strip() != "0"
    do_farm = os.environ.get("NTS_FARM", "1").strip() != "0"
    sec = env_int("NTS_SEC", 20)
    cap = env_int("NTS_MAX", 0)
    force = os.environ.get("NTS_FORCE", "0").strip() == "1"

    log("共 %d 个账号｜会员=%s 农场=%s 每条%d秒 上限=%s 强制=%s" % (
        len(accs), do_member, do_farm, sec, cap or "不限", force))

    ok = 0
    for tag, tok, dc in accs:
        try:
            if run_account(tag, tok, dc, do_member, do_farm, sec, cap, force):
                ok += 1
        except Exception as e:
            log("  ✗ 账号 %s 异常：%s" % (tag, e))
        time.sleep(2)
    log("完成：%d/%d 个账号" % (ok, len(accs)))
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