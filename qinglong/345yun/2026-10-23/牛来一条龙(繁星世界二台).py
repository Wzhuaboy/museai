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
# ============================================================
# 脚本名称: 牛来牧场多账户一条龙脚本
# 功能描述: 自动登录 → 激励视频 → 浏览任务 → 买牛 → 合成升级 → 每日领取
# 作者: 柏油马路
# 版本: v1.3.0
# 日期: 2026-10-23
# 定时任务: cron: 0 9 * * *
#
# 环境变量:
#   NL_ACCOUNTS      - 必填, 邮箱#密码&邮箱#密码 多账号用 & 分隔
#   NL_VIDEO_ENABLE  - 可选, 激励视频开关  默认 true
#   NL_BROWSE_ENABLE - 可选, 浏览任务开关  默认 true
#   NL_BUY_ENABLE    - 可选, 买牛开关  默认 true
#   NL_MERGE_ENABLE  - 可选, 合成升级开关  默认 true
#   NL_CLAIM_ENABLE  - 可选, 每日产出领取开关  默认 true
# 项目地址: https://x-nll.orbexa.cc/r/I525C7C3E2C
# ============================================================

import requests
import json
import time
import sys
import os
import re
import uuid
import random
from datetime import datetime

# ============================================================
# 接口配置（抓包自 牛来1.har，后端 x-nllapi.orbexa.cc）
# ============================================================
BASE_URL = "https://x-nllapi.orbexa.cc"
CAPTCHA_URL = f"{BASE_URL}/auth/security/challenge"
LOGIN_URL = f"{BASE_URL}/auth/login/password"
HOME_REWARDED_ATTEMPTS_URL = f"{BASE_URL}/api/v1/home-rewarded/attempts"
TASK_CENTER_ATTEMPTS_URL = f"{BASE_URL}/api/v1/task-center/rewarded-video/attempts"
TASK_CENTER_URL = f"{BASE_URL}/api/v1/task-center"
AD_TASKS_CENTER_URL = f"{BASE_URL}/api/v1/ad-tasks/task-center"
RANCH_URL = f"{BASE_URL}/api/v1/game/ranch"
DAILY_ELIGIBILITY_URL = f"{BASE_URL}/api/v1/game/daily-eligibility"
PURCHASES_URL = f"{BASE_URL}/api/v1/game/purchases"
MERGES_URL = f"{BASE_URL}/api/v1/game/merges"
DAILY_GATE_URL = f"{BASE_URL}/ad-tasks/daily-gate"
LOTTERY_HOME_URL = f"{BASE_URL}/lottery/home?wheelType=COIN"
ME_URL = f"{BASE_URL}/me"

# 每日产出领取接口（实测确认）
DAILY_CLAIMS_URL = f"{BASE_URL}/api/v1/game/daily-claims"
# 任务中心奖励领取（实测确认: POST /api/v1/task-center/{CODE}/claim）
TASK_CLAIM_URL = f"{BASE_URL}/api/v1/task-center"
# 抽奖 / 提现 接口路径（未实测，暂留备查）
LOTTERY_DRAW_CANDIDATES = [
    "/lottery/draw",
    "/api/v1/lottery/draw",
    "/lottery/claims",
]
WITHDRAWAL_CONFIG_URL = f"{BASE_URL}/withdrawal/config"
WITHDRAWAL_APPLY_URL = f"{BASE_URL}/withdrawals"

# 设备指纹：消融实验已实测（16:14, 新token）——牛来全部设备字段可随机化
# - 只读接口(/me/ranch/task-center) + attempts 创建: 全随机指纹均通过
# - client-verify 409 与指纹无关, 是观看时长 <6s 被拒 (TOSIN_REWARD_COMPLETED_TOO_QUICKLY)
# - 所以每个账号生成独立随机指纹, 账号内所有请求保持一致, 多账号互不关联
import random as _random

def generate_device_profile():
    """生成一个随机设备指纹, 格式对齐抓包原值"""
    model = f"25053RT{_random.randint(10,99)}C"
    android_ver = str(_random.randint(12, 15))
    build = f"AQ3A.{_random.randint(100000, 999999)}"
    return {
        "X-Device-Id": uuid.uuid4().hex * 2,  # 128位随机hex, 格式同抓包
        "X-Device-Id-Source": "LEGACY_CLIENT_DEVICE_WEAK",
        "X-Device-Model": model,
        "X-Android-Version": android_ver,
        "X-App-Package": "com.bide.haoyoukan.wwciiii",
        "X-App-Version-Code": "231",
        "X-App-Version-Name": "1.1.229",
        "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android {android_ver}; {model} Build/{build})",
    }

# ============================================================
# 日志系统
# ============================================================
class Logger:
    R = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'

    def __init__(self, color=True):
        self.color = color
        self.start_time = datetime.now()
        self.success_count = 0
        self.fail_count = 0
        self.results = []

    def _c(self, text, color):
        if not self.color:
            return text
        return f"{color}{text}{self.R}"

    def _now(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _elapsed(self):
        s = int((datetime.now() - self.start_time).total_seconds())
        h, rem = divmod(s, 3600)
        m, s = divmod(rem, 60)
        if h > 0:
            return f"{h}h{m:02d}m{s:02d}s"
        elif m > 0:
            return f"{m}m{s:02d}s"
        return f"{s}s"

    def banner(self, name="牛来牧场", version="1.0.0", desc=""):
        print(self._c("=" * 60, self.CYAN))
        print(self._c(f"  {name} 多账户自动化脚本 v{version}", self.BOLD + self.CYAN))
        if desc:
            print(self._c(f"  {desc}", self.CYAN))
        print(self._c(f"  时间: {self._now()}", self.CYAN))
        print(self._c("=" * 60, self.CYAN))

    def footer(self, exit_code=0):
        print(self._c("=" * 60, self.CYAN))
        print(self._c(f"📊 完成: ✅ {self.success_count} 成功, ❌ {self.fail_count} 失败",
                      self.BOLD + (self.GREEN if self.fail_count == 0 else self.YELLOW)))
        print(self._c("=" * 60, self.CYAN))
        print(self._c(f"=== 执行结束 [{self._now()}] 耗时 {self._elapsed()} 退出码 {exit_code} ===", self.GRAY))

    def account_header(self, email, idx, total):
        print("")
        print(self._c("=" * 50, self.BLUE))
        print(self._c(f"📱 [{idx}/{total}] {email}", self.BOLD + self.BLUE))
        print(self._c("=" * 50, self.BLUE))

    def info(self, msg, indent=1):
        sp = "  " * indent
        print(f"{sp}{self._c('ℹ️', self.CYAN)} {msg}")

    def ok(self, msg, indent=1):
        sp = "  " * indent
        print(f"{sp}{self._c('✅', self.GREEN)} {self._c(msg, self.GREEN)}")

    def err(self, msg, indent=1):
        sp = "  " * indent
        print(f"{sp}{self._c('❌', self.RED)} {self._c(msg, self.RED)}")

    def warn(self, msg, indent=1):
        sp = "  " * indent
        print(f"{sp}{self._c('⚠️', self.YELLOW)} {self._c(msg, self.YELLOW)}")

    def skip(self, msg, indent=1):
        sp = "  " * indent
        print(f"{sp}{self._c('⏭️', self.YELLOW)} {msg}")

    def step(self, msg, indent=1):
        sp = "  " * indent
        print(f"{sp}{self._c('▶', self.MAGENTA)} {msg}")

    def result_item(self, email, status, msg):
        self.results.append((email, status, msg))
        if status == 'success':
            self.success_count += 1
        else:
            self.fail_count += 1

    def show_results(self):
        print("")
        print(self._c("📢 执行结果:", self.BOLD + self.CYAN))
        print(self._c(f"总账户: {len(self.results)}  ✅成功: {self.success_count}  ❌失败: {self.fail_count}", self.GRAY))
        for idx, (email, status, msg) in enumerate(self.results, 1):
            icon = "✅" if status == 'success' else "❌"
            color = self.GREEN if status == 'success' else self.RED
            print(f"  {self._c(f'{idx}.', self.GRAY)} {self._c(icon, color)} {self._c(email, self.BLUE)} - {self._c(msg, color)}")

logger = Logger()

# ============================================================
# 通知（青龙 notify 双路径，未配置则静默跳过）
# ============================================================
def send_notify(title, content):
    try:
        sys.path.insert(0, "/ql/data/scripts")
        from notify import send
        send(title, content)
        return True
    except Exception:
        pass
    try:
        sys.path.insert(0, os.path.expanduser("~/scripts"))
        from notify import send
        send(title, content)
        return True
    except Exception:
        return False

# ============================================================
# 工具函数
# ============================================================
def random_order_no():
    """TOSIN 广告 orderNo：32位大写 hex（uuid4 hex 大写截取）"""
    return uuid.uuid4().hex.upper()[:32]

def safe_json_parse(text, default=None):
    try:
        return json.loads(text)
    except Exception:
        return default or {"raw": text}

def mask_email(email):
    if '@' in email:
        name, domain = email.split('@', 1)
        if len(name) > 3:
            return name[:3] + '***' + '@' + domain
        return name + '@' + domain
    return email

def build_headers(extra=None):
    p = DEVICE_PROFILE
    h = {
        "User-Agent": p["User-Agent"],
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "X-App-Package": p["X-App-Package"],
        "X-App-Version-Code": p["X-App-Version-Code"],
        "X-App-Version-Name": p["X-App-Version-Name"],
        "X-Device-Model": p["X-Device-Model"],
        "X-Android-Version": p["X-Android-Version"],
        "X-Device-Id": p["X-Device-Id"],
        "X-Device-Id-Source": p["X-Device-Id-Source"],
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    if extra:
        h.update(extra)
    return h

# 模块级设备指纹：每账号登录时重新生成（独立指纹，避免多账号关联风控）
DEVICE_PROFILE = generate_device_profile()
SDK_VERSION = "Y260817"

def safe_request(session, method, url, **kwargs):
    """统一请求封装：异常返回 None"""
    try:
        return session.request(method, url, timeout=kwargs.pop('timeout', 15), **kwargs)
    except Exception as e:
        logger.warn(f"请求异常 {url}: {e}", 2)
        return None

def retry_loop(fn, retries=3, base_sleep=2, max_sleep=12):
    """指数退避重试"""
    for i in range(retries):
        r = fn()
        if r is not None:
            return r
        if i < retries - 1:
            time.sleep(min(base_sleep * (2 ** i), max_sleep))
    return None

# ============================================================
# 登录（安全题验证码 + 邮箱密码）
# ============================================================
def get_captcha(session, scene="login-password"):
    try:
        resp = session.post(CAPTCHA_URL, headers=build_headers(), json={"scene": scene}, timeout=10)
        if resp.status_code != 200:
            logger.warn(f"获取验证码失败 HTTP {resp.status_code}", 2)
            return None, None
        data = resp.json()
        ticket = data.get("ticket", "")
        question = data.get("question", "")
        if not ticket or not question:
            logger.err("验证码数据异常", 2)
            return None, None
        logger.info(f"验证码: {question}", 2)
        expr = re.sub(r"[=?？\s]", "", question)
        if re.fullmatch(r"[\d+\-*/]+", expr):
            answer = str(int(eval(expr)))
            logger.info(f"验证码答案: {answer}", 3)
            return ticket, answer
        logger.err(f"无法解析: {question}", 2)
        return None, None
    except Exception as e:
        logger.err(f"获取验证码异常: {e}", 2)
        return None, None

def login(email, password):
    global DEVICE_PROFILE
    # 每账号独立设备指纹（消融实测: 牛来不校验指纹, 全部可随机）
    DEVICE_PROFILE = generate_device_profile()
    session = requests.Session()
    session.headers.update(build_headers())

    logger.info("获取登录验证码...")
    ticket, answer = get_captcha(session, "login-password")
    if not ticket:
        return None, "获取验证码失败"

    logger.info("登录中...")
    login_data = {
        "email": email,
        "password": password,
        "securityTicket": ticket,
        "securityAnswer": answer,
    }
    try:
        resp = session.post(LOGIN_URL, json=login_data, timeout=15)
        result = safe_json_parse(resp.text, {})
        if resp.status_code == 200 and "accessToken" in result:
            token = result["accessToken"]
            user_info = result.get("user", {})
            username = user_info.get("username", "未知")
            uid = user_info.get("uid", "?")
            logger.ok(f"登录成功 ({username} uid={uid})", 2)
            session.headers["Authorization"] = f"Bearer {token}"
            return session, token
        msg = result.get("msg", result.get("message", "登录失败"))
        logger.err(f"登录失败: {msg}", 2)
        return None, msg
    except Exception as e:
        logger.err(f"登录异常: {e}", 2)
        return None, f"登录异常: {e}"

# ============================================================
# 激励视频（任务中心 REWARDED_VIDEO，App里那个 3/5 的，0.15牛币/次）
# ============================================================
def run_video_reward_task(session, target_times=5):
    """任务中心激励视频：POST /task-center/rewarded-video/attempts (空body)
    → 等待（实测阈值 6s）→ client-verify 随机 orderNo
    冷却: cooldownSeconds 15s（抓包规则）
    完成后调 task_claim_reward 领牛币
    先查状态：CLAIMED/已完成直接跳过或直接领, 只刷缺的次数"""
    logger.step(f"激励视频 (任务中心, 目标: {target_times}次)")

    # 先查任务中心状态
    tasks = get_task_center(session)
    if tasks and tasks.get("REWARDED_VIDEO"):
        t = tasks["REWARDED_VIDEO"]
        status = t.get("status", "")
        progress = t.get("progressValue", 0)
        target = t.get("targetValue", target_times)
        if status == "CLAIMED":
            logger.ok(f"REWARDED_VIDEO 今日已领取, 跳过", 2)
            return True
        if status == "CLAIMABLE" or progress >= target:
            logger.ok(f"REWARDED_VIDEO 已完成 ({progress}/{target}), 直接领取", 2)
            task_claim_reward(session, "REWARDED_VIDEO")
            return True
        if 0 < progress < target:
            logger.info(f"REWARDED_VIDEO 已进行 {progress}/{target}, 只刷缺的 {target-progress} 次", 2)
            target_times = target - progress

    completed_total = 0

    for idx in range(1, target_times + 1):
        logger.info(f"第 {idx}/{target_times} 次", 2)
        attempt_id = None

        for retry in range(1, 4):
            resp = safe_request(session, "POST", TASK_CENTER_ATTEMPTS_URL, json={})
            if resp is None:
                time.sleep(random.uniform(3, 6))
                continue
            if resp.status_code == 429:
                try:
                    wait = float(resp.json().get("cooldownRemainingSeconds", 15)) + 2
                except Exception:
                    wait = 17
                logger.warn(f"冷却中, 等待 {round(wait,1)}s (重试{retry}/3)", 2)
                time.sleep(wait)
                continue
            data = safe_json_parse(resp.text, {})
            attempt_id = data.get("attemptId")
            if attempt_id:
                break
            time.sleep(random.uniform(3, 6))

        if not attempt_id:
            logger.warn("未获取 attemptId, 跳过本次", 2)
            time.sleep(random.uniform(8, 12))
            continue

        # 观看时长：必须 ≥6s（实测阈值），拟人取 8~12s
        watch_sec = random.uniform(8, 12)
        logger.info(f"观看广告 {round(watch_sec,1)}s", 2)
        time.sleep(watch_sec)

        verify_url = f"{BASE_URL}/api/v1/task-center/rewarded-video/attempts/{attempt_id}/client-verify"
        payload = {"orderNo": random_order_no(), "sdkVersion": SDK_VERSION}
        req_headers = {"Idempotency-Key": str(uuid.uuid4())}

        resp_verify = safe_request(session, "POST", verify_url, json=payload, headers=req_headers)
        if resp_verify is None:
            time.sleep(random.uniform(5, 10))
            continue
        res_json = safe_json_parse(resp_verify.text, {})

        if res_json.get("verified"):
            completed_total = res_json.get("progressValue", completed_total + 1)
            logger.ok(f"验证通过 进度: {completed_total}/{target_times}", 2)
        else:
            logger.warn(f"验证未通过: {resp_verify.text[:120]}", 2)

        if completed_total >= target_times:
            logger.ok("激励视频已满, 提前完成!", 2)
            break

        # 冷却 15s（任务规则 cooldownSeconds）+ 拟人余量
        sleep_sec = random.uniform(16, 22)
        logger.info(f"冷却 {round(sleep_sec,1)}s", 2)
        time.sleep(sleep_sec)

    logger.ok(f"激励视频完成 {completed_total}/{target_times}次")

    # 完成后尝试领取牛币
    if completed_total >= target_times:
        task_claim_reward(session, "REWARDED_VIDEO")

    time.sleep(3)
    return completed_total >= target_times

# ============================================================
# 任务中心查询（用于检测各任务完成状态）
# ============================================================
def get_task_center(session):
    """查询任务中心, 返回 {code: task_dict}。失败返回 None"""
    resp = safe_request(session, "GET", TASK_CENTER_URL)
    if resp is None:
        return None
    try:
        data = resp.json()
        return {t.get("code"): t for t in data.get("tasks", []) if t.get("code")}
    except Exception:
        return None

def task_done_or_claimable(session, task_code):
    """检测任务状态: 返回 (是否完成/可领, 可直接领取)
    已领(CLAIMED)或可领(CLAIMABLE)都算完成; 完成未领的直接领取"""
    tasks = get_task_center(session)
    if not tasks:
        return False, False
    task = tasks.get(task_code)
    if not task:
        return False, False
    status = task.get("status", "")
    if status == "CLAIMED":
        logger.ok(f"{task_code} 今日已完成并领取, 跳过", 2)
        return True, False
    if status == "CLAIMABLE":
        logger.ok(f"{task_code} 已完成待领取, 直接领取", 2)
        task_claim_reward(session, task_code)
        return True, False
    return False, False

# ============================================================
# 任务中心奖励领取（抓包 牛来2.har 实测确认）
# POST /api/v1/task-center/{CODE}/claim  body: {"idempotencyKey":"<uuid>"}
# 响应: claim.rewardAmount / claim.businessNo, 需 Idempotency-Key 头同值
# ============================================================
def task_claim_reward(session, task_code):
    """任务完成后领取牛币奖励。task_code: REWARDED_VIDEO / PROJECT_AD_DAILY"""
    logger.step(f"领取任务奖励 ({task_code})")
    idem_key = str(uuid.uuid4())
    resp = safe_request(session, "POST", f"{BASE_URL}/api/v1/task-center/{task_code}/claim",
                        json={"idempotencyKey": idem_key},
                        headers={"Idempotency-Key": idem_key})
    if resp is None:
        logger.warn(f"领取请求失败 ({task_code})", 2)
        return False
    data = safe_json_parse(resp.text, {})
    if resp.status_code in (200, 201) and data.get("claim"):
        claim = data["claim"]
        amount = claim.get("rewardAmount", "?")
        business_no = claim.get("businessNo", "?")
        logger.ok(f"领取成功! {task_code} 奖励 {amount} 牛币 单号: {business_no}", 2)
        return True
    logger.warn(f"领取失败: {resp.status_code} {resp.text[:150]}", 2)
    return False

# ============================================================
# 每日产出（解锁广告 + 领取，同一个状态机：
# ADS_REQUIRED → 刷 home-rewarded 广告到 5/5 → CLAIMABLE → daily-claims 领取 → CLAIMED）
# ============================================================
def get_daily_eligibility(session):
    resp = safe_request(session, "GET", DAILY_ELIGIBILITY_URL)
    if resp is None:
        return None
    try:
        return resp.json()
    except Exception:
        return None

def _run_unlock_ads(session, target_times):
    """刷每日解锁广告（home-rewarded DAILY_CLAIM），返回完成次数"""
    completed_total = 0
    for idx in range(1, target_times + 1):
        logger.info(f"第 {idx}/{target_times} 次", 2)
        attempt_id = None

        for retry in range(1, 4):
            resp = safe_request(session, "POST", HOME_REWARDED_ATTEMPTS_URL, json={"scene": "DAILY_CLAIM"})
            if resp is None:
                time.sleep(random.uniform(3, 6))
                continue
            if resp.status_code == 429:
                try:
                    wait = float(resp.json().get("cooldownRemainingSeconds", 6)) + 2
                except Exception:
                    wait = 8
                logger.warn(f"冷却中, 等待 {round(wait,1)}s (重试{retry}/3)", 2)
                time.sleep(wait)
                continue
            data = safe_json_parse(resp.text, {})
            attempt_id = data.get("attemptId")
            if attempt_id:
                break
            time.sleep(random.uniform(3, 6))

        if not attempt_id:
            logger.warn("未获取 attemptId, 跳过本次", 2)
            time.sleep(random.uniform(8, 12))
            continue

        watch_sec = random.uniform(6, 10)
        logger.info(f"观看广告 {round(watch_sec,1)}s", 2)
        time.sleep(watch_sec)

        verify_url = f"{BASE_URL}/api/v1/home-rewarded/attempts/{attempt_id}/client-verify"
        payload = {"orderNo": random_order_no(), "sdkVersion": SDK_VERSION}
        req_headers = {"Idempotency-Key": str(uuid.uuid4())}

        resp_verify = safe_request(session, "POST", verify_url, json=payload, headers=req_headers)
        if resp_verify is None:
            time.sleep(random.uniform(5, 10))
            continue
        res_json = safe_json_parse(resp_verify.text, {})

        if res_json.get("verified"):
            completed_total += 1
            logger.ok(f"验证通过 进度: {completed_total}/{target_times}", 2)
        else:
            logger.warn(f"验证未通过: {resp_verify.text[:120]}", 2)

        if completed_total >= target_times:
            logger.ok("解锁广告已满, 提前完成!", 2)
            break

        sleep_sec = random.uniform(7, 12)
        logger.info(f"冷却 {round(sleep_sec,1)}s", 2)
        time.sleep(sleep_sec)

    return completed_total

def claim_daily_produce(session):
    """每日产出一条龙：查资格 → 未解锁刷广告 → 解锁后 daily-claims 领取。
    CLAIMED 视为已领过（正常完成）。
    实测: daily-claims 需 expectedCycleId+expectedVersion+Idempotency-Key
    成功返回 HTTP 201, claim.business_no, NCOIN + dailyUnits"""
    logger.step("每日产出 (解锁广告 + 领取)")
    elig = get_daily_eligibility(session)
    if not elig:
        logger.warn("获取每日资格失败, 尝试直接领取", 2)
        cycle_id = ""
        version = 0
        daily_units = "?"
        claimable = True
    else:
        claim_status = elig.get("claimStatus", "")
        claimable = elig.get("claimable", False)
        verified = elig.get("verifiedAds", 0)
        required = elig.get("requiredAds", 5)
        cycle_id = elig.get("cycleId", "")
        version = elig.get("version", 0)
        daily_units = elig.get("dailyUnits", "?")
        logger.info(f"每日资格: 状态={claim_status} 广告={verified}/{required} 可领={claimable}", 2)

        # 已领取过 = 正常完成
        if claim_status == "CLAIMED":
            logger.ok(f"今日产出已领取过, 跳过", 2)
            return True, {"status": "CLAIMED"}

        # 未解锁 → 刷缺的广告
        if not claimable:
            need = max(0, required - verified)
            if need > 0:
                logger.info(f"未解锁, 需刷 {need} 个解锁广告", 2)
                _run_unlock_ads(session, need)
                time.sleep(2)
                # 重查资格
                elig = get_daily_eligibility(session)
                if not elig:
                    logger.warn("重查资格失败", 2)
                    return False, "重查失败"
                claim_status = elig.get("claimStatus", "")
                claimable = elig.get("claimable", False)
                cycle_id = elig.get("cycleId", cycle_id)
                version = elig.get("version", version)
                daily_units = elig.get("dailyUnits", daily_units)
                if claim_status == "CLAIMED":
                    logger.ok(f"解锁广告刷完, 但状态已变为 CLAIMED (可能已自动到账?)", 2)
                    return True, {"status": "CLAIMED"}
            else:
                logger.info(f"广告已达标 ({verified}/{required}), 尝试直接领取", 2)

    if not claimable:
        logger.warn(f"仍不可领取 ({claim_status}), 跳过", 2)
        return False, claim_status

    if not cycle_id:
        # 从 ranch 补 cycleId
        ranch = get_ranch(session)
        if ranch:
            cycle_id = ranch.get("cycleId", "")
            version = ranch.get("version", 0)

    if not cycle_id:
        logger.err("未获取到 cycleId, 无法领取", 2)
        return False, "无 cycleId"

    payload = {"expectedCycleId": cycle_id, "expectedVersion": version}
    resp = safe_request(session, "POST", f"{BASE_URL}/api/v1/game/daily-claims",
                        json=payload, headers={"Idempotency-Key": str(uuid.uuid4())})
    if resp is None:
        return False, "请求失败"
    data = safe_json_parse(resp.text, {})
    if resp.status_code in (200, 201):
        claim = data.get("claim", {})
        business_no = claim.get("business_no", "?")
        amount = claim.get("amount", daily_units)
        logger.ok(f"每日产出领取成功! 单号: {business_no} 产出: {amount} 微牛币", 2)
        return True, data
    code = data.get("code", "")
    logger.warn(f"领取失败: {code} {resp.text[:100]}", 2)
    return False, code

# ============================================================
# 买牛（买当前等级的伙伴，用于合成升级）
# ============================================================
def get_ranch(session):
    resp = safe_request(session, "GET", RANCH_URL)
    if resp is None:
        return None
    return safe_json_parse(resp.text, None)

def buy_cow(session):
    """买当前等级伙伴。返回 (purchase_id) 或 None"""
    logger.step("买牛")
    ranch = get_ranch(session)
    if not ranch:
        logger.err("获取牧场状态失败", 2)
        return None

    # 先查今日是否还可购买（操作资格）
    elig = ranch.get("operationEligibility", {}).get("purchase", {})
    if not elig.get("allowed", True):
        reason = elig.get("reasonCode", "")
        msg = elig.get("message", "") or reason
        logger.warn(f"今日不可买牛: {msg}", 2)
        return None

    level = ranch.get("level", 1)
    version = ranch.get("version", 0)
    cycle_id = ranch.get("cycleId", "")
    wallets = {w.get("asset"): w.get("available", "0") for w in ranch.get("wallets", [])}
    coin = wallets.get("NCOIN", "0")
    try:
        coin_f = float(coin)  # 微单位 (10^-6 牛币)
    except Exception:
        coin_f = 0.0
    levels = {l.get("level"): l for l in ranch.get("levels", [])}

    cur = levels.get(level)
    if not cur:
        logger.warn(f"等级 {level} 配置缺失, 无法买牛", 2)
        return None
    purchase_units = int(cur.get("purchaseUnits", "0"))
    name = cur.get("name", f"L{level}")

    logger.info(f"当前等级: {level} 牛币余额: {coin_f/1e6:.6f} 版本: {version}", 2)

    # 判断是否买得起（NCOIN 与 purchaseUnits 同为微单位, 直接比较）
    if coin_f < purchase_units:
        logger.info(f"{name} 伙伴价 {purchase_units/1e6:.6f} 牛币, 余额不足, 跳过买牛", 2)
        return None

    quote_version = int(cur.get("configVersion", 2))
    purchase_payload = {
        "level": level,
        "expectedVersion": version,
        "quoteVersion": quote_version,
        "expectedCycleId": cycle_id,
    }
    logger.info(f"购买 {name}(L{level}) 伙伴 花费 {purchase_units/1e6:.6f} 牛币", 2)
    resp = safe_request(session, "POST", PURCHASES_URL, json=purchase_payload,
                        headers={"Idempotency-Key": str(uuid.uuid4())})
    if resp is None:
        return None
    pdata = safe_json_parse(resp.text, {})
    if resp.status_code not in (200, 201) or not pdata.get("purchase"):
        logger.warn(f"买牛失败: {resp.text[:150]}", 2)
        return None
    purchase_id = pdata["purchase"]["id"]
    logger.ok(f"买牛成功 {pdata['purchase'].get('business_no', '')} purchaseId={purchase_id[:8]}...", 2)
    return purchase_id

# ============================================================
# 合成升级（用已购买的伙伴合成，牛升级）
# ============================================================
def merge_upgrade(session, purchase_id):
    """用 purchase_id 合成升级。成功返回 True"""
    if not purchase_id:
        logger.warn("无 purchaseId, 跳过合成升级", 2)
        return False
    logger.step("合成升级")

    # 重新读取 ranch 拿最新版本号和 cycleId（买完后版本已+1）
    ranch = get_ranch(session)
    if not ranch:
        logger.err("获取牧场状态失败", 2)
        return False

    # 先查今日是否还可合成（操作资格）
    elig = ranch.get("operationEligibility", {}).get("merge", {})
    if not elig.get("allowed", True):
        msg = elig.get("message", "") or elig.get("reasonCode", "")
        logger.warn(f"今日不可合成: {msg}", 2)
        return False

    level = ranch.get("level", 1)
    version = ranch.get("version", 0)
    cycle_id = ranch.get("cycleId", "")

    merge_payload = {
        "purchaseId": purchase_id,
        "expectedVersion": version,
        "expectedCycleId": cycle_id,
    }
    logger.info(f"合成升级 L{level} → L{level+1}", 2)
    resp = safe_request(session, "POST", MERGES_URL, json=merge_payload,
                        headers={"Idempotency-Key": str(uuid.uuid4())})
    if resp is None:
        return False
    mdata = safe_json_parse(resp.text, {})
    if resp.status_code not in (200, 201) or not mdata.get("merge"):
        logger.warn(f"合成失败: {resp.text[:150]}", 2)
        return False
    merge = mdata["merge"]
    new_ranch = mdata.get("ranch", {})
    new_level = int(new_ranch.get("level", level + 1))
    contrib = int(merge.get("contribution_units", "0"))
    logger.ok(f"合成成功 → L{new_level} 贡献 +{contrib} 牛币", 2)
    time.sleep(random.uniform(2, 4))
    return True

# ============================================================
# 浏览任务（任务中心 PROJECT_AD_DAILY，App里那个 3/8 的，0.1牛币/次）
# 链路: GET /api/v1/ad-tasks/task-center 拿任务 → start → 循环 heartbeat(25s) ×8
# ============================================================
def run_browse_task(session, target_count=8, task_name="浏览任务"):
    logger.step(f"{task_name} (目标: {target_count}次)")

    # 先查任务中心状态：已领/已完成直接跳过或直接领
    done, _ = task_done_or_claimable(session, "PROJECT_AD_DAILY")
    if done:
        return True

    def query_task(retry=3):
        for i in range(retry):
            try:
                resp = session.get(AD_TASKS_CENTER_URL, timeout=10)
                data = resp.json()
                task = data.get("task")
                if task:
                    return task
            except Exception as e:
                logger.warn(f"查询失败: {e} ({i+1}/{retry})", 2)
            time.sleep(1)
        return None

    task = query_task()
    if not task:
        logger.err("获取浏览任务失败", 2)
        return False

    task_id = task.get("id")
    required = task.get("requiredCount", target_count)
    view_seconds = task.get("viewSeconds", 25)
    completed = task.get("completedCount", 0)

    logger.info(f"任务ID: {task_id} | 需要 {required}次 | 每次 {view_seconds}s | 已完成 {completed}", 2)
    if completed >= required:
        logger.ok(f"{task_name}: 已完成 {completed}/{required}", 2)
        task_claim_reward(session, "PROJECT_AD_DAILY")
        return True

    empty_retries = 0
    while completed < required:
        task = query_task()
        if not task:
            empty_retries += 1
            if empty_retries >= 15:
                logger.err("连续查询失败, 任务终止", 2)
                break
            time.sleep(2)
            continue
        empty_retries = 0

        task_id = task.get("id", task_id)
        item = task.get("item") or {}
        item_id = item.get("id")
        status = item.get("status")
        completed = task.get("completedCount", 0)

        if completed >= required:
            break
        if not item_id:
            logger.info("等待分配任务...", 2)
            time.sleep(3)
            continue

        logger.info(f"第 {completed+1}/{required} 次 | 状态: {status}", 2)

        if status == "ASSIGNED":
            start_url = f"{BASE_URL}/ad-tasks/{task_id}/items/{item_id}/start"
            safe_request(session, "POST", start_url, json={})
            time.sleep(1)

        if status in ("VIEWING", "ASSIGNED"):
            heartbeat_url = f"{BASE_URL}/ad-tasks/{task_id}/items/{item_id}/heartbeat"
            interval = 5
            max_retry = 12
            for _ in range(max_retry):
                resp = safe_request(session, "POST", heartbeat_url, json={})
                if resp is not None:
                    data = safe_json_parse(resp.text, {})
                    task = data.get("task", {})
                    item = task.get("item", {})
                    viewed = item.get("viewedSeconds", 0)
                    remain = item.get("remainingSeconds", 0)
                    status = item.get("status")
                    if status == "COMPLETED" or remain <= 0 or viewed >= view_seconds:
                        logger.ok(f"第 {completed+1} 次完成", 2)
                        completed = task.get("completedCount", completed)
                        break
                time.sleep(interval)
        elif status == "COMPLETED":
            completed = task.get("completedCount", completed)
            time.sleep(1)

        time.sleep(1.5)

    final_task = query_task()
    final_count = final_task.get("completedCount", 0) if final_task else completed
    logger.ok(f"{task_name}: {final_count}/{required}")

    # 完成后尝试领取牛币
    if final_count >= required:
        task_claim_reward(session, "PROJECT_AD_DAILY")

    return final_count >= required

# ============================================================
# 抽奖（COIN 转盘，6 次机会）
# ============================================================
def run_lottery(session):
    logger.step("牛币幸运抽奖")
    resp = safe_request(session, "GET", LOTTERY_HOME_URL)
    if resp is None:
        return False
    data = safe_json_parse(resp.text, {})
    chances = int(data.get("chances", 0) or 0)
    if chances <= 0:
        logger.info("今日抽奖次数已用完", 2)
        return True
    logger.info(f"抽奖机会: {chances} 次", 2)

    drawn = 0
    for _ in range(chances):
        for path in LOTTERY_DRAW_CANDIDATES:
            resp = safe_request(session, "POST", f"{BASE_URL}{path}",
                                json={"wheelType": "COIN"},
                                headers={"Idempotency-Key": str(uuid.uuid4())})
            if resp is None:
                continue
            if resp.status_code in (200, 201):
                data = safe_json_parse(resp.text, {})
                prize = data.get("prize", data.get("result", {}))
                if isinstance(prize, dict):
                    name = prize.get("name", "?")
                    amount = prize.get("rewardAmount", "?")
                else:
                    name, amount = "?", "?"
                logger.ok(f"抽奖获得: {name} {amount}", 2)
                drawn += 1
                break
        time.sleep(random.uniform(3, 6))

    logger.ok(f"抽奖完成 {drawn}/{chances} 次")
    return True

# ============================================================
# 自动提现（接口与繁星同底座候选，未实测）
# ============================================================
def auto_withdraw(session, amount=0.3):
    logger.step(f"自动提现 {amount}元")
    tier_id = None
    resp = safe_request(session, "GET", WITHDRAWAL_CONFIG_URL)
    if resp is None or resp.status_code != 200:
        logger.warn("获取提现配置失败 (接口可能不存在, 跳过)", 2)
        return False
    config = safe_json_parse(resp.text, {})
    for tier in config.get("tiers", []):
        if float(tier.get("amount", 0)) == float(amount):
            tier_id = tier.get("id")
            break
    if not tier_id:
        logger.warn(f"未找到 {amount}元 档位", 2)
        return False

    logger.info("获取提现验证码...", 2)
    ticket, answer = get_captcha(session, "withdrawal-submit")
    if not ticket:
        logger.err("获取验证码失败", 2)
        return False

    withdraw_data = {
        "tierId": tier_id,
        "amount": f"{amount:.2f}",
        "accountType": "BALANCE",
        "provider": "ALIPAY",
        "securityTicket": ticket,
        "securityAnswer": answer,
    }
    resp = safe_request(session, "POST", WITHDRAWAL_APPLY_URL, json=withdraw_data,
                        headers={"Idempotency-Key": str(uuid.uuid4())})
    if resp is None:
        return False
    if resp.status_code in (200, 201):
        result = safe_json_parse(resp.text, {})
        order_no = result.get("requestNo", result.get("businessNo", "未知"))
        logger.ok(f"提现成功! 单号: {order_no}", 2)
        return True
    text = resp.text[:150]
    logger.warn(f"提现失败: {text}", 2)
    return False

# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    env_accounts = os.getenv("NL_ACCOUNTS", "")
    video_enable = os.getenv("NL_VIDEO_ENABLE", "true").strip().lower() == "true"
    browse_enable = os.getenv("NL_BROWSE_ENABLE", "true").strip().lower() == "true"
    buy_enable = os.getenv("NL_BUY_ENABLE", "true").strip().lower() == "true"
    merge_enable = os.getenv("NL_MERGE_ENABLE", "true").strip().lower() == "true"
    claim_enable = os.getenv("NL_CLAIM_ENABLE", "true").strip().lower() == "true"

    logger.banner("牛来牧场", "1.3.0", "自动登录 + 激励视频 + 浏览任务 + 买牛 + 合成升级 + 每日领取")

    if not env_accounts:
        logger.err("未检测到环境变量 NL_ACCOUNTS")
        logger.info("配置: 邮箱#密码，多账号用 & 分隔")
        sys.exit(1)

    accounts = []
    for line in env_accounts.replace("&", "\n").split("\n"):
        line = line.strip()
        if line and "#" in line:
            email, pwd = line.split("#", 1)
            accounts.append((email.strip(), pwd.strip()))

    if not accounts:
        logger.err("环境变量格式错误")
        logger.info("正确格式: 邮箱#密码，多账号用 & 分隔")
        sys.exit(1)

    print("")
    print(logger._c(f"✅ 成功加载 {len(accounts)} 个账户", logger.GREEN))
    for idx, (email, _) in enumerate(accounts, 1):
        print(f"   {idx}. {mask_email(email)}")
    print("")

    notify_lines = [f"牛来牧场脚本启动 | 账号数: {len(accounts)}"]

    for idx, (email, pwd) in enumerate(accounts):
        result_msgs = []
        logger.account_header(mask_email(email), idx + 1, len(accounts))

        session, info = login(email, pwd)
        if not session:
            logger.err(f"登录失败: {info}")
            logger.result_item(email, 'fail', "登录失败")
            continue

        # 1. 激励视频（每日产出前置条件）
        if video_enable:
            if run_video_reward_task(session, target_times=5):
                result_msgs.append("激励视频✓")
            else:
                result_msgs.append("激励视频未满")
            time.sleep(2)

        # 2. 浏览任务（8 个项目广告）
        if browse_enable:
            if run_browse_task(session, target_count=8):
                result_msgs.append("浏览✓")
            time.sleep(2)

        # 3. 买牛（买当前等级伙伴）
        purchase_id = None
        if buy_enable:
            purchase_id = buy_cow(session)
            if purchase_id:
                result_msgs.append("买牛✓")
            time.sleep(2)

        # 4. 合成升级（用买到的伙伴合成，牛升级）
        if merge_enable:
            if merge_upgrade(session, purchase_id):
                result_msgs.append("合成升级✓")
            time.sleep(2)

        # 5. 每日产出（解锁广告 + 领取，一个状态机，放最后领升级后的最大产出）
        if claim_enable:
            claim_ok, _ = claim_daily_produce(session)
            result_msgs.append("领取✓" if claim_ok else "领取未确认")
            time.sleep(2)

        summary = " | ".join(result_msgs) if result_msgs else "全部完成"
        logger.result_item(email, 'success', summary)
        time.sleep(3)

    logger.show_results()
    logger.footer(0)

    # 汇总通知（未配置 notify 则静默跳过）
    ok_count = logger.success_count
    fail_count = logger.fail_count
    notify_lines.append(f"完成: 成功 {ok_count} / 失败 {fail_count}")
    for email, status, msg in logger.results:
        icon = "✅" if status == 'success' else "❌"
        notify_lines.append(f"{icon} {mask_email(email)} - {msg}")
    send_notify("牛来牧场脚本执行完成", "\n".join(notify_lines))


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