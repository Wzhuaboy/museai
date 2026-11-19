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
酷狗免费版 (com.kugou.android.elder) 金币任务脚本，青龙零依赖单文件。

接口: gateway.kugou.com/yutc/speeder/v1/*
签名: md5(SALT + 排序参数 + SALT)，SALT = "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
任务: 签到 / 刷视频 / 应用推广 / 兑换 / 抽奖 / 餐补 / 听书 / 听歌 / 登录 / 下载试玩

环境变量 KGFB，多账号换行分隔，每行:
    备注#token#userid#mid#dfid
例:
    账号1#填你的token#填你的userid#填你的mid#填你的dfid
    账号2#填你的token2#填你的userid2#填你的mid2#填你的dfid2
"""

import gzip
import hashlib
import json
import os
import random
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

# ============================================================================
#  可调参数
# ============================================================================
CFG = {
    "skip_taskids": [1162, 2268],      # 1162提现券/2268未开放，跳过
    "task_loop_caps": {},               # 每个任务单轮最多提交几次(0/未配置 = 按服务端剩余次数)
    # ---- 随机延迟 ----
    "delay_min": 4.0, "delay_max": 8.0,     # 请求间隔(秒)
    "pause_prob": 0.12,                      # 每次请求后触发长停顿的概率
    "pause_min": 15, "pause_max": 45,        # 长停顿时长(秒)
    "hesitate_prob": 0.20,                   # 偶发犹豫短停顿的概率
    "hesitate_min": 1.5, "hesitate_max": 5.0,  # 犹豫时长(秒)
    "jitter_max": 2.5,                       # 微抖动(秒)
    "retry_delay_min": 4.0, "retry_delay_max": 12.0,  # 请求失败重试间隔(秒)
    "time_jitter": 3,                        # 时间戳随机偏移(秒)
    # ---- 执行策略 ----
    "shuffle_tasks": True,                   # 打乱任务顺序（只是顺序乱，不跳任何任务）
    "core_taskids": [9, 45, 3001, 1108],     # 核心收益任务（标记用，不跳过）
    "lock": True,                            # 防止青龙两次定时任务重叠执行
    "retry": 2,                              # 单请求失败重试次数
    # ---- 翻倍 ----
    "double_always": True,                   # 有 double_code 就翻倍
    "double_pause_prob": 0.08,               # 翻倍前偶发长停顿概率
    "double_delay_min": 2.5,                 # 翻倍请求前额外延迟下限(秒)
    "try_listen_task": True,                  #  1129听歌时长：尝试领取(成功翻倍，失败50051跳过；需app真实听歌凭证)
    "double_delay_max": 7.0,                 # 翻倍请求前额外延迟上限(秒)
}

ENV_NAME = "KGFB"
ENV_FIELDS = ["remark", "token", "userid", "mid", "dfid", "devid"]

# 默认账号（环境变量 KGFB 优先）
DEFAULT_ACCOUNTS = [{
    "remark": "账号1", "token": "填你的token", "userid": "填你的userid",
    "mid": "填你的mid", "dfid": "填你的dfid",
    "openid": "填你的openid", "nickname": "填你的昵称",
}]
SALT = "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
BASE = "https://gateway.kugou.com"
PREFIX = "/yutc/speeder/v1"   # 免费版(com.kugou.android.elder) 网关模块前缀
UA = ("Android14-1080-24360-46-0-mobileCallProtocol")
TIMEOUT = 25
LOCK_FILE = os.path.join(tempfile.gettempdir(), "kugou_elder.lock")
LOCK_TTL = 3600

REQ_COUNT = 0
ACC = {}          # 当前账号

# ============================================================================
# 固定参数 user_label（所有账号通用）
# ============================================================================
USER_LABEL = {
    "val1": 29904, "val2": 1, "val3": 268435456, "val4": 2147483648,
    "val5": 0, "val6": 0, "val7": 0, "val8": 0, "val9": 0, "val10": 0,
    "val11": 0, "val12": 0, "val13": 0, "val14": 0, "val15": 0,
    "val16": 516, "val17": 32, "val18": 0, "val19": 0, "val20": 8,
    "val21": 0, "val22": 0, "val23": 1024, "val24": 65536, "val25": 1085634,
    "val26": 1073741824, "val27": 0, "val28": 16, "val29": 0, "val30": 16776,
    "val31": 917504, "val32": 16512, "val33": 27279360, "val34": 19136524,
    "val35": 8192, "val36": 131072, "val37": 270536736, "val38": 1024,
    "val39": 196608, "val40": 130, "val41": 0, "val42": 0, "val43": 38010880,
    "val44": 0,
}

# 每日任务清单：(taskid, 名称, 基础奖励, 是否签到)
#   1   签到
#   9   刷创意视频  100/次 ×48
#   45  应用推广奖励 100/次 ×30
#   3001 兑换专区  50/次 ×12
#   1105 定时领取  100/次 ×50
#   1107 抽奖      100/次 ×10
#   23   听书      200 ×1
#   1101 听歌      100 ×1
#   3003 登录      100 ×1
#   1162 提现页(跳过) / 2268 惊喜好礼(未开放) / 1108 餐补(拆餐)
TASK_LIST = [
    # (taskid, name, show_coins, source)
    #   source=来源标记：9/45/3001/23/1101/3003 用1；1108 餐补用5；1107 抽奖用46
    #   1164 下载试玩次留任务走 run_tryplay() 自动识别(每个app 下载+3000/试玩+2000=5000)
    (9,    "刷创意视频",      100,  "1"),
    (45,   "惊喜任务·应用推广", 100,  "1"),
    (3001, "兑换专区任务",    50,   "1"),
    (1105, "定时领取金币",    100,  "1"),
    (1107, "抽奖活动",        100,  "46"),
    (1108, "四餐补贴",        100,  "5"),
    (23,   "听有声读物10分钟", 200,  "1"),
    (1101, "听歌10分钟",      100,  "1"),
    (3003, "登录领金币",      100,  "1"),
]


# ============================================================================
#  账号 / 环境变量解析
# ============================================================================
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def parse_accounts():
    raw = (os.environ.get(ENV_NAME) or "").strip()
    raw = raw.replace("\\r", "").replace("\\n", "\n")     # 兼容字面量 \n
    accounts = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split("#")]
        if len(parts) < 2:
            log(f"! 跳过格式错误的行: {line[:40]}...")
            continue
        parts += [""] * (len(ENV_FIELDS) - len(parts))
        acc = dict(zip(ENV_FIELDS, parts[:len(ENV_FIELDS)]))
        if not acc.get("token") or not acc.get("userid"):
            log(f"! 跳过缺少 token/userid 的行: {line[:40]}...")
            continue
        acc["remark"] = acc.get("remark") or acc["userid"]
        accounts.append(acc)
    if not accounts:
        log(f"! 环境变量 {ENV_NAME} 未配置或为空，使用脚本内置调试账号（仅 1 个）")
        accounts = [dict(a) for a in DEFAULT_ACCOUNTS]
    return accounts


def acquire_lock():
    if not CFG.get("lock", True):
        return True
    try:
        if os.path.exists(LOCK_FILE):
            age = time.time() - os.path.getmtime(LOCK_FILE)
            if age < LOCK_TTL:
                return False
            log(f"发现过期锁({int(age)}秒)，强制接管")
    except OSError:
        pass
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(int(time.time())))
        return True
    except OSError:
        return True


def release_lock():
    if not CFG.get("lock", True):
        return
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


# ============================================================================
#  请求核心
# ============================================================================
def sleep_rand():
    """随机延迟：基础间隔 + 抖动 + 停顿"""
    d = random.uniform(CFG["delay_min"], CFG["delay_max"])
    d += random.uniform(0, CFG.get("jitter_max", 1.2))
    time.sleep(d)
    # 偶发长停顿
    if random.random() < CFG.get("pause_prob", 0.05):
        pause = random.uniform(CFG.get("pause_min", 15), CFG.get("pause_max", 45))
        log(f"    · 停顿 {int(pause)} 秒")
        time.sleep(pause)
    # 偶发短停顿
    elif random.random() < CFG.get("hesitate_prob", 0.15):
        h = random.uniform(CFG.get("hesitate_min", 1.5), CFG.get("hesitate_max", 5.0))
        log(f"    · 短停 {h:.1f} 秒")
        time.sleep(h)


def double_sleep():
    """翻倍请求前的延迟"""
    lo = float(CFG.get("double_delay_min", CFG["delay_min"]))
    hi = float(CFG.get("double_delay_max", CFG["delay_max"]))
    if hi < lo:
        lo, hi = hi, lo
    time.sleep(random.uniform(lo, hi))
    if random.random() < CFG.get("double_pause_prob", 0.08):
        pause = random.uniform(8, 20)
        log(f"      · 翻倍前停顿 {int(pause)} 秒")
        time.sleep(pause)


def _t():
    """时间戳加微小随机偏移"""
    return int(time.time()) + random.randint(-CFG.get("time_jitter", 2), CFG.get("time_jitter", 2))


def make_sign(params, raw_body=None):
    """原生链签名：md5(SALT + 排序后 k=v 串 [+ 原始body] + SALT)"""
    keys = sorted(params.keys())
    joined = "".join(f"{k}={params[k]}" for k in keys)
    if raw_body:
        joined += raw_body
    return hashlib.md5((SALT + joined + SALT).encode("utf-8")).hexdigest()


def api(path, params=None, data=None, method="GET", _retry=None):
    """调用酷狗免费版网关接口，返回解析后的 JSON(dict)；失败抛异常"""
    global REQ_COUNT
    if _retry is None:
        _retry = CFG["retry"]
    p = {
        "appid": "3166",
        "clientver": "24360",
        "clienttime": str(_t()),
        "mid": ACC.get("mid", ""),
        "uuid": "-",
        "dfid": ACC.get("dfid", ""),
        "srcappid": "2919",
        "userid": ACC.get("userid", ""),
        "token": ACC.get("token", ""),
    }
    if params:
        p.update({k: str(v) for k, v in params.items()})

    raw = None
    if data is not None:
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    p["signature"] = make_sign(p, raw)

    url = BASE + PREFIX + path + "?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, data=(raw.encode("utf-8") if raw else None),
                                 method=method)
    req.add_header("User-Agent", UA)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if ACC.get("devid"):
        req.add_header("KG-DEVID", ACC["devid"])
    req.add_header("KG-CLIENTTIMEMS", str(_t() * 1000 + random.randint(0, 999)))
    req.add_header("Accept-Encoding", "gzip")

    last_err = None
    for attempt in range(_retry + 1):
        try:
            REQ_COUNT += 1
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                body = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
            return json.loads(body.decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            b = e.read()
            try:
                if e.headers.get("Content-Encoding") == "gzip":
                    b = gzip.decompress(b)
            except Exception:
                pass
            last_err = f"HTTP {e.code}: {b[:200].decode('utf-8', 'replace')}"
        except Exception as e:            # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
        if attempt < _retry:
            time.sleep(random.uniform(CFG.get("retry_delay_min", 3.0), CFG.get("retry_delay_max", 8.0)))
    raise RuntimeError(f"{method} {path} 失败 -> {last_err}")


# ============================================================================
#  业务接口
# ============================================================================
def get_account():
    return api("/user/info")["data"]


# 各任务查询/提交用的 source 标记（查询必须用对各 source，否则查不到正确状态）
TASK_SOURCE = {1107: "46", 1108: "5", 1129: "5", 1164: "5"}

# 各任务每日可做次数兜底：服务端未返回 max_done_count 时，按清单已知次数跑满
EXPECTED_CAP = {9: 48, 45: 30, 3001: 12, 1105: 50, 1107: 10, 1108: 4,
                23: 1, 1101: 1, 3003: 1, 1129: 9, 1164: 9}


def task_source(tid):
    """返回任务对应的 source：默认 1；抽奖 46；餐补/听歌/试玩 5"""
    return TASK_SOURCE.get(tid, "1")


def get_task_info(tid, source=None):
    """查询单个任务状态，返回 (profile, state)。
    查询时自动使用任务正确的 source（1107=46，1108/1129/1164=5，其余=1）。"""
    r = api("/task/info", params={"taskid": str(tid), "source": source or task_source(tid), "appver": "1001"})
    d = r.get("data") or {}
    return d.get("profile") or {}, d.get("state") or {}


def do_signon():
    """每日签到：直接 signon 带今日 code；已签则返回 (False, 提示)"""
    today = time.strftime("%Y%m%d")
    r = api("/task/signon", params={"source": "1", "appver": "1001"},
            data={"code": today, "source": "1"}, method="POST")
    if r.get("status") == 1:
        d = r.get("data") or {}
        aw = d.get("awards") or {}
        return True, f"签到成功 +{aw.get('coins')} 金币 (code={today})"
    if r.get("errcode") == 30014:
        return False, "今日已签到"
    return False, f"签到失败: {r.get('error') or r.get('errcode')}"


# 1107 抽奖奖品池
LOTTERY_POOL = [
    {"id": "1", "type": "coin", "num": 588},
    {"id": "2", "type": "coin", "num": 228},
    {"id": "3", "type": "coin", "num": 158},
    {"id": "4", "type": "coin", "num": 488},
    {"id": "5", "type": "coin", "num": 388},
    {"id": "6", "type": "coin", "num": 88},
    {"id": "7", "type": "coin", "num": 38},
    {"id": "8", "type": "coin", "num": 5888},
]


def submit_task(tid, show_coins, source="1", meal_id=0):
    """
     提交任务，并按「只要返回 double_code 就翻倍，翻到服务端不再发新 code」的规则循环翻倍。

    返回 (主+翻倍累计到账金币, 主响应, 错误说明)
      - 主请求就 status != 1 时，coins=0，err 为错误信息
      - 主请求成功但 coins=0 时，coins=0，err=""（由调用方决定是否结束该任务）
    """
    body = {"taskid": tid, "show_coins": int(show_coins or 0),
            "user_label": USER_LABEL, "is_vip": 0, "extra": {},
            "appver": 1001,
            "ticket": hashlib.md5(os.urandom(16)).hexdigest()}
    # 按任务类型补参数
    if tid == 1107:
        body["lottery_pool"] = LOTTERY_POOL        # 抽奖：带上奖品池（source=46）
    if tid == 1108 and meal_id:
        body["meal_id"] = int(meal_id)             # 餐补：带上餐序号（source=5）
    if tid == 1129:
        # 1129 听歌需要真实会话凭证，纯脚本大概率失败，自动跳过
        body["extra"] = {"done_count": 1, "seconds": 7200,
                         "ts": int(time.time()),
                         "ticket": hashlib.md5(os.urandom(16)).hexdigest()}
    r = api("/task/submit", params={"source": source, "appver": "1001"},
            data=body, method="POST")
    if r.get("status") != 1:
        return 0, r, r.get("error") or f"errcode={r.get('errcode')}"

    d = r.get("data") or {}
    coins = int((d.get("awards") or {}).get("coins") or 0)

    # 无金币则交给调用方判断
    if coins <= 0:
        return 0, r, ""

    # ---- 循环翻倍（有 double_code 就翻，翻到无新 code 为止）----
    dc = d.get("double_code")
    round_no = 0
    while dc:
        if not CFG.get("double_always", True):
            break
        round_no += 1
        double_sleep()
        try:
            body2 = dict(body)
            body2["double_code"] = dc
            body2["double_award_type"] = 2
            body2["use_uni_award"] = 1
            r2 = api("/task/submit", params={"source": source, "appver": "1001"},
                     data=body2, method="POST")
        except Exception as e:            # noqa: BLE001
            log(f"      ! 翻倍 #{round_no} 请求异常(停止翻倍): {e}")
            break

        if r2.get("status") != 1:
            log(f"      · 翻倍 #{round_no} 失败: {r2.get('error') or r2.get('errcode')}")
            break

        d2 = r2.get("data") or {}
        c2 = int((d2.get("awards") or {}).get("coins") or 0)
        if c2 <= 0:
            log(f"      · 翻倍 #{round_no} 无金币到账，停止翻倍")
            break

        coins += c2
        log(f"       翻倍 #{round_no} +{c2}")

        # 无新 code 则停止翻倍
        new_dc = d2.get("double_code")
        if not new_dc or new_dc == dc:
            break
        dc = new_dc

    return coins, r, ""


def run_lottery():
    """抽奖活动(1107)：机会用完就 exchange(看广告)加机会再抽，直到次数上限。
    实测 exchange {"way":"view"} 纯脚本可用：+1抽奖机会 +金币(约196)，且不加 done_count。"""
    log("  ── 抽奖活动(1107) ──")
    try:
        _, st = get_task_info(1107)
    except Exception as e:                # noqa: BLE001
        log(f"    ! 查询抽奖状态失败: {e}")
        return 0
    done = int(st.get("done_count") or 0)
    cap = int(st.get("max_done_count") or 0)
    chances = int((st.get("lottery") or {}).get("chances") or 0)
    if cap and done >= cap:
        log(f"    · 抽奖次数已达 {done}/{cap}，今日完成")
        return 0
    total = 0
    guard = 0
    while (not cap or done < cap) and guard < 100:
        guard += 1
        if chances <= 0:
            r = api("/lottery/exchange", params={"source": "5", "appver": "1001"},
                    data={"way": "view"}, method="POST")
            if r.get("status") != 1:
                log(f"    · 看广告加机会失败: {r.get('error') or r.get('errcode')}")
                break
            d = r.get("data") or {}
            chances = int((d.get("lottery") or {}).get("chances") or 0)
            c = int(d.get("coins") or 0)
            if c > 0:
                total += c
                log(f"     看广告 +{c} 金币, 抽奖机会 +1")
            if chances <= 0:
                log("    · 看广告后仍无抽奖机会，停止")
                break
            double_sleep()
        coins, r, err = submit_task(1107, 100, "46", 0)
        if r.get("status") != 1:
            log(f"    · 抽奖结束: {err}")
            break
        total += max(coins, 0)
        log(f"     抽奖 +{coins}")
        st = (r.get("data") or {}).get("state") or {}
        done = int(st.get("done_count") or done)
        chances = int((st.get("lottery") or {}).get("chances") or 0)
        if guard < 100:
            sleep_rand()
    log(f"  ── 抽奖累计 +{total} 金币 ──")
    return total


def run_tryplay():
    """下载试玩次留任务(1164)：自动识别 state.extra_state.apps 中可做的 app，
    每个 app = 下载(award_type=1,+3000) + 打开30秒(award_type=2,+2000) = 5000 金币。
    status: 0=未下载(先领下载再领试玩) 1=已下载(直接领试玩) 2=已完成(跳过)。
    每天 app 列表刷新，脚本自动识别新 app。"""
    log("  ── 下载试玩次留(1164) ──")
    try:
        r = api("/task/info", params={"taskid": "1164", "source": "5", "appver": "1001"})
        st = (r.get("data") or {}).get("state") or {}
    except Exception as e:                # noqa: BLE001
        log(f"    ! 查询1164状态失败: {e}")
        return 0
    cap = int(st.get("max_done_count") or 0)
    if cap and int(st.get("done_count") or 0) >= cap:
        log(f"    · 下载试玩已领完 {st.get('done_count')}/{cap}，今日完成")
        return 0
    es = st.get("extra_state") or {}
    apps = es.get("apps") or {}
    if not apps:
        log("    · 暂无下发的试玩 app（每天刷新），跳过")
        return 0
    total = 0
    # 状态: 0=未下载(下载→等待→试玩) / 1=已下载(试玩) / 2=完成(跳过)
    # 下载后需等待 30-60s 再试玩（服务端校验试玩时长）
    try_min = float(CFG.get("tryplay_min_wait", 30))
    try_max = float(CFG.get("tryplay_max_wait", 60))
    for status in ("0", "1"):
        for pkg, info in apps.items():
            if int(info.get("status") or 0) != int(status):
                continue
            if cap and int(st.get("done_count") or 0) >= cap:
                break
            steps = [1, 2] if status == "0" else [2]
            for award_type in steps:
                if cap and int(st.get("done_count") or 0) >= cap:
                    break
                body = {"taskid": 1164, "show_coins": 100, "user_label": USER_LABEL,
                        "is_vip": 0,
                        "extra": {"award_type": award_type, "pkg": pkg,
                                  "app": info.get("app", ""),
                                  "logo": info.get("logo", ""),
                                  "desc": info.get("desc", "")},
                        "appver": 1001,
                        "ticket": hashlib.md5(os.urandom(16)).hexdigest()}
                got_step = False
                for _try in range(CFG.get("tryplay_retry", 3)):
                    try:
                        r = api("/task/submit", params={"source": "5", "appver": "1001"},
                                data=body, method="POST")
                    except Exception as e:    # noqa: BLE001
                        log(f"    ! [{info.get('app','')}] 步骤{award_type} 请求异常: {e}，重试")
                        sleep_rand()
                        continue
                    if r.get("status") != 1:
                        log(f"    · [{info.get('app','')}] 步骤{award_type} 未领取（{r.get('error') or r.get('errcode')}），跳过")
                        got_step = False
                        break
                    d = r.get("data") or {}
                    c = int((d.get("awards") or {}).get("coins") or 0)
                    if c <= 0 and _try < CFG.get("tryplay_retry", 3) - 1:
                        log(f"    · [{info.get('app','')}] 步骤{award_type} 无金币，重试")
                        sleep_rand()
                        continue
                    total += max(c, 0)
                    st = d.get("state") or {}
                    log(f"     [{info.get('app','')}] {'下载' if award_type==1 else '试玩'} +{c}")
                    got_step = True
                    break
                if not got_step:
                    # 接口明确失败/多次无金币：跳过当前 app 的下个步骤
                    if award_type == 1:
                        sleep_rand()
                        continue
                    sleep_rand()
                    continue
                if award_type == 1 and status == "0":
                    # 下载成功（或已尝试）后等待再试玩
                    wait = random.uniform(try_min, try_max)
                    log(f"    · 试玩中 {int(wait)} 秒")
                    time.sleep(wait)
                else:
                    double_sleep()
    log(f"  ── 下载试玩累计 +{total} 金币 ──")
    return total


def run_listen():
    """听歌时长任务(1129)：用户真实听歌后服务端有可领档位时可领取。
    由于提交需要 app 真实听歌会话签发的一次性凭证(extra.ticket)，纯脚本构造
    通常会 50051 失败 -> 静默跳过（不报错、不影响其他任务）。"""
    if not CFG.get("try_listen_task", True):
        return 0
    log("  ── 听歌时长(1129) ──")
    try:
        _, st = get_task_info(1129)
    except Exception as e:                # noqa: BLE001
        log(f"    ! 查询1129状态失败: {e}")
        return 0
    done = int(st.get("done_count") or 0)
    cap = int(st.get("max_done_count") or 0)
    if cap and done >= cap:
        log(f"    · 听歌时长已领完 {done}/{cap}，今日完成")
        return 0
    if not st.get("is_show", 1):
        log("    · 听歌时长任务未开放，跳过")
        return 0
    try:
        coins, r, err = submit_task(1129, 100, "5", 0)
    except Exception as e:                # noqa: BLE001
        log(f"    ! 1129 请求异常: {e}")
        return 0
    if r.get("status") != 1:
        log(f"    · 1129 未能领取（{err}；需 app 真实听歌生成凭证，跳过）")
        return 0
    if coins <= 0:
        log("    · 1129 本次无金币到账（可能需真实听歌时长，不再重复尝试）")
        return 0
    log(f"     听歌时长 +{coins}（含翻倍）")
    return coins


def collect_tasks():
    """先全量查询每个任务完成/剩余次数，再固定把未完成的任务按剩余次数全部跑完。
    规则：查询到剩余 >0 就做，按剩余次数跑满；只有接口明确报错（完成不了/已完成）才智能跳过，
    无金币/请求异常均不中断，继续跑完剩余次数。"""
    total = 0

    # ---- 1. 每日签到 ----
    log("  ── 每日签到 ──")
    try:
        ok, msg = do_signon()
        log(("     " if ok else "    · ") + msg)
    except Exception as e:                # noqa: BLE001
        log(f"    ! 签到异常: {e}")

    # ---- 2. 全量查询：每个任务 完成/剩余 ----
    log("  ── 查询全部任务状态 ──")
    todo = []          # (tid, 名称, show_coins, source, 剩余次数, meal_id)
    for tid, name, show_coins, source in TASK_LIST:
        if tid in CFG["skip_taskids"]:
            continue
        if tid in (1107, 1164):   # 抽奖/下载试玩：独立逻辑，最后统一跑（此处只展示不加入 todo）
            continue
        try:
            prof, st = get_task_info(tid)
        except Exception as e:                # noqa: BLE001
            log(f"    ! 查询任务 [{tid}]{name} 状态失败: {e}")
            continue
        if not st:
            log(f"    · 任务 [{tid}]{name} 无返回状态（可能未开放），跳过")
            continue

        done = int(st.get("done_count") or 0)
        cap = int(st.get("max_done_count") or prof.get("max_done_count") or 0)
        if not cap:
            # 服务端未给上限：按已知每日次数兜底，确保跑满
            cap = EXPECTED_CAP.get(tid, 1)
            if done < cap:
                log(f"    · [{tid}]{name} 服务端未返回上限，按清单每日 {cap} 次兜底")

        # 1108 餐补：拆成未领的餐
        if tid == 1108:
            meals = st.get("meals") or []
            open_meals = [m for m in meals if int(m.get("state") or 0) == 0 and m.get("id")]
            if open_meals:
                log(f"    · [{tid}]四餐补贴 完成 {done}/{cap}，剩余可领 {len(open_meals)} 餐")
            else:
                log(f"    · [{tid}]四餐补贴 完成 {done}/{cap}，当前无未领的餐")
            for m in open_meals:
                todo.append((tid, f"{name}·餐{m['id']}", show_coins, source, 1, int(m["id"])))
            continue

        # 1105 冷却中则跳过（查询即知下次可领时间）
        if tid == 1105 and st.get("next_award_time"):
            left = int(st["next_award_time"]) - int(time.time())
            if left > 0:
                log(f"    · [1105]定时领取金币 已完成 {done}/{cap}，冷却剩 {left // 60}分{left % 60}秒，本轮跳过")
                continue

        if cap and done >= cap:
            log(f"    · [{tid}]{name} 已完成 {done}/{cap}，今日无需再做")
            continue
        rest = (cap - done) if cap else 1
        if rest <= 0:
            rest = 1
        log(f"    · [{tid}]{name} 完成 {done}/{cap}，剩余 {rest} 次，本轮固定完成")
        todo.append((tid, name, show_coins, source, rest, 0))

    # 抽奖 1107：查询展示 + 提示
    try:
        _, st = get_task_info(1107)
        done7 = int(st.get("done_count") or 0)
        cap7 = int(st.get("max_done_count") or 0)
        ch7 = int((st.get("lottery") or {}).get("chances") or 0)
        log(f"    · [1107]抽奖活动 完成 {done7}/{cap7}，剩余机会 {ch7}" + ("" if (not cap7 or done7 < cap7) else "（今日已满）"))
    except Exception as e:                # noqa: BLE001
        log(f"    ! 查询抽奖状态失败: {e}")

    if not todo:
        log("    · 普通任务今日无剩余（均已满/跳过），仍执行抽奖/试玩/听歌")

    # ---- 3. 打乱任务顺序（不随机跳过） ----
    if CFG.get("shuffle_tasks", True):
        random.shuffle(todo)
        log("    · 任务顺序已随机打乱（不跳过任何任务）")

    # ---- 4. 固定完成所有未完成任务 ----
    for tid, name, show_coins, source, rest, meal_id in todo:
        limit = CFG["task_loop_caps"].get(tid, 0)
        if limit:
            rest = min(rest, limit)
        if rest <= 0:
            rest = 1
        got = 0
        for i in range(rest):
            try:
                coins, r, err = submit_task(tid, show_coins, source, meal_id)
            except Exception as e:        # noqa: BLE001
                # 请求异常：不中断本任务，稍后重试下一次；api() 内已有重试
                log(f"    ! [{tid}]{name} #{i + 1} 请求异常: {e}，稍后继续")
                sleep_rand()
                continue

            # 接口明确失败（未完成条件/已完成/次数用尽）→ 该任务智能跳过，继续下一任务
            if r.get("status") != 1:
                log(f"    · [{tid}]{name} 结束（{err}）")
                break

            # 无金币也照常跑满剩余次数（服务端可能异步到账，不因此中断）
            got += max(coins, 0)
            log(f"     [{tid}]{name} #{i + 1} +{coins}")
            if i < rest - 1:
                sleep_rand()
        total += got

    # ---- 5. 独立任务：抽奖 / 试玩 / 听歌 ----
    total += run_lottery()
    total += run_tryplay()
    total += run_listen()

    log(f"  ── 本轮任务累计 +{total} 金币 ──")

    # ---- 6. 结束复查：检查哪些任务没跑满/被智能跳过 ----
    log("  ── 结束复查（检查遗漏） ──")
    unfinished = []
    for tid, name, _, _ in TASK_LIST:
        if tid in CFG["skip_taskids"]:
            continue
        try:
            prof, st = get_task_info(tid)
            if not st:
                continue
            done = int(st.get("done_count") or 0)
            cap = int(st.get("max_done_count") or prof.get("max_done_count") or 0)
            if not cap:
                cap = EXPECTED_CAP.get(tid, 1)
            if tid == 1108:
                # 餐补按未领的餐算
                meals = st.get("meals") or []
                open_meals = [m for m in meals if int(m.get("state") or 0) == 0]
                if open_meals:
                    unfinished.append(f"[{tid}]{name} 还有 {len(open_meals)} 餐未领（可能服务端未开放或冷却中）")
            elif cap and done < cap:
                left = cap - done
                unfinished.append(f"[{tid}]{name} 完成 {done}/{cap}，剩余 {left} 次（可能接口报错智能跳过或冷却中）")
        except Exception:                # noqa: BLE001
            pass

    # 独立任务复查
    try:
        _, st = get_task_info(1107)
        done7 = int(st.get("done_count") or 0)
        cap7 = int(st.get("max_done_count") or 0)
        if cap7 and done7 < cap7:
            unfinished.append(f"[1107]抽奖 完成 {done7}/{cap7}，剩余 {cap7 - done7} 次（可能机会不足智能跳过）")
    except Exception:                    # noqa: BLE001
        pass

    try:
        r = api("/task/info", params={"taskid": "1164", "source": "5", "appver": "1001"})
        st = (r.get("data") or {}).get("state") or {}
        done64 = int(st.get("done_count") or 0)
        cap64 = int(st.get("max_done_count") or 0)
        if cap64 and done64 < cap64:
            unfinished.append(f"[1164]试玩 完成 {done64}/{cap64}，剩余 {cap64 - done64} 次（可能无下发app或接口失败智能跳过）")
    except Exception:                    # noqa: BLE001
        pass

    if unfinished:
        log("    检测到以下任务未跑满（已智能跳过或接口限制）：")
        for u in unfinished:
            log(f"      · {u}")
        log(f"    共 {len(unfinished)} 个任务未完全跑满。原因：①接口报错智能跳过 ②服务端冷却/限制 ③需真实行为（广告/听歌）")
    else:
        log("    ✓ 所有任务已跑满或智能跳过，无遗漏")

    return total


def show_info():
    acc = get_account()
    a = acc.get("account") or {}
    rate = acc.get("coin_rmb_rate") or 10000
    log(f"  余额 : {a.get('balance_coins')} 金币  (≈ {float(a.get('cash') or 0):.2f} 元, 汇率 {rate})")
    log(f"  累计 : {a.get('total_coins')}")
    log("  任务 :")
    for tid, name, show_coins, source in TASK_LIST:
        if tid in CFG["skip_taskids"]:
            continue
        try:
            prof, st = get_task_info(tid)
            done = int(st.get("done_count") or 0)
            cap = int(st.get("max_done_count") or 0)
            flag = "可领" if (not cap or done < cap) else "已满"
            aw = prof.get("award_coins")
            extra = ""
            if tid == 1107:
                extra = f" 机会{(st.get('lottery') or {}).get('chances', 0)}"
            if tid == 1108:
                open_meals = sum(1 for m in (st.get("meals") or [])
                                 if int(m.get("state") or 0) == 0)
                extra = f" 可领{open_meals}餐"
            log(f"        [{tid:>5}] {name[:14]:<14} {done}/{cap} {flag}"
                f"  单次{aw or show_coins}金币{extra}")
        except Exception as e:                # noqa: BLE001
            log(f"        [{tid:>5}] {name[:14]:<14} 查询失败: {e}")


def self_test():
    """校验签名算法（脱敏样本，仅验证拼接+md5 与标准实现一致）"""
    log("── 签名自检 ──")
    p = {"appid": "3166", "clienttime": "1790233296706", "clientver": "24360",
         "dfid": "fakedfid00000000000000000", "from": "client", "h5": "1",
         "mid": "00000000000000000000000000000000", "spec": "15",
         "srcappid": "2919",
         "token": "faketoken000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
         "userid": "0000000000", "uuid": "-"}
    joined = "".join(f"{k}={p[k]}" for k in sorted(p))
    expect = hashlib.md5((SALT + joined + SALT).encode("utf-8")).hexdigest()
    got = make_sign(p)
    if got != expect:
        log(f"   签名实现异常: {got} != {expect}")
        return False
    log(f"   签名算法一致: {got}")
    return True


# ============================================================================
#  入口
# ============================================================================
def run_account(acc, mode):
    global ACC
    ACC = acc
    log(f"━━━ 账号 [{acc['remark']}] userid={acc['userid']} ━━━")
    if mode == "info":
        show_info()
        return
    if not self_test():
        raise RuntimeError("签名自检失败")
    try:
        acc0 = get_account()
        before = int((acc0.get("account") or {}).get("balance_coins") or 0)
        log(f"  起始金币: {before}")
    except Exception as e:                # noqa: BLE001
        log(f"  ! 读取余额失败(账号可能已失效): {e}")
        return

    try:
        collect_tasks()
    except Exception as e:                # noqa: BLE001
        log(f"  ! 任务流程异常: {e}")

    try:
        acc1 = get_account()
        after = int((acc1.get("account") or {}).get("balance_coins") or 0)
        log(f"  结束金币: {after}   本次净增 +{after - before}"
            f"  ({(after - before) / 10000.0:.2f} 元)")
    except Exception as e:                # noqa: BLE001
        log(f"  ! 读取余额失败: {e}")


def main():
    args = set(sys.argv[1:])
    mode = "info" if "--info" in args else "run"
    log("=" * 62)
    log(" 酷狗免费版 · 金币任务脚本 (多账号 · 环境变量 %s)" % ENV_NAME)
    log("=" * 62)

    accounts = parse_accounts()
    log(f"共 {len(accounts)} 个账号")

    if "--test" in args:
        sys.exit(0 if self_test() else 1)

    if mode == "info":
        for acc in accounts:
            try:
                run_account(acc, "info")
            except Exception as e:        # noqa: BLE001
                log(f"! 账号[{acc.get('remark')}] 查询失败: {e}")
        log(f"总请求数: {REQ_COUNT}")
        return

    if not acquire_lock():
        log("已有实例在运行（命中运行锁），本次直接退出")
        sys.exit(0)
    try:
        for acc in accounts:
            try:
                run_account(acc, "run")
            except Exception as e:        # noqa: BLE001
                log(f"! 账号[{acc.get('remark')}] 执行失败: {e}")
            time.sleep(random.uniform(2, 5))
    finally:
        release_lock()

    log(f"总请求数: {REQ_COUNT}")
    log("全部账号完成。")


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