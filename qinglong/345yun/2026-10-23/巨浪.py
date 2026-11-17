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
# 脚本名称: 巨浪大游
# 功能描述: 每日自动下注游戏(0.5 BGC)完成游戏任务后签到领 BGC, 净赚签到奖励
# 作者: 晓阅
# 版本: v1.0.0
# 日期: 2026-10-22
#
# 环境变量:
#   JL_ACCOUNTS  - 必填, 多账号列表, 格式 '邮箱#密码&邮箱2#密码2', 不配则退出
#   JL_CFG       - 可选, JSON 配置覆盖, 如 {"bet_num": 1, "wait_rounds": 6}
#
# 说明:
#   - 每账号: 若今日已签到则跳过; 否则下注 0.5 BGC 完成游戏任务后签到领 BGC
#   - 下注 num=1 即 0.5 BGC(接口 num 为整数注数, 每注固定 0.5 BGC)
#   - 下注后等待当局开奖(无论输赢, 有结果即可解锁签到), 签到成功 +0.5~3.5 BGC
#项目地址：https://hwbgame.com/NDMVJA
# ============================================================

import requests
import json
import time
import os
import sys
import random

# ============================================================
# 配置(可改)
# ============================================================
BASE = "https://hwbgame.com"

# 账号(环境变量 JL_ACCOUNTS, '邮箱#密码&邮箱2#密码2', 不配则退出)
ACCOUNTS_ENV = os.environ.get("JL_ACCOUNTS", "").strip()
if not ACCOUNTS_ENV:
    print("❌ 未配置 JL_ACCOUNTS 环境变量, 格式: '邮箱#密码&邮箱2#密码2'")
    sys.exit(1)
ACCOUNTS = [a for a in ACCOUNTS_ENV.split("&") if a.strip()]

# 设备指纹(固定, 同一账号每次请求一致, 降低关联风控)
DEVICE = {
    "user-agent": "Dart/3.9 (dart:io)",
    "system": "1",
    "abi": "arm64-v8a",
    "mobile-model": "25053RT47C",
    "lang": "zh_CN",
    "version": "1.0.1",
    "equipment": "4fe80013ae58602b",
}

BET_NUM = 1          # 下注注数(整数), 1 注 = 0.5 BGC
WAIT_ROUNDS = 6      # 等待下注窗口的最大轮询轮数(每轮 5 秒)
RESULT_ROUNDS = 14   # 下注后等待开奖结果的最大轮询轮数(每轮 5 秒)
TIME_OUT = 15
RETRY = 3

try:
    _env_cfg = json.loads(os.environ.get("JL_CFG", "{}"))
    BET_NUM = _env_cfg.get("bet_num", BET_NUM)
    WAIT_ROUNDS = _env_cfg.get("wait_rounds", WAIT_ROUNDS)
    RESULT_ROUNDS = _env_cfg.get("result_rounds", RESULT_ROUNDS)
except Exception:
    pass

# 请求体加密(固定 AES-256-CBC, 密钥/IV 来自客户端)
AES_KEY = b"7A3F9C1D5E8B24A6F0D7C3B91E5A8D42"
AES_IV = b"3B7E1A9C4D2F8056"

# ============================================================
# Logger
# ============================================================
class Logger:
    R = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

    def _ts(self):
        return time.strftime("%H:%M:%S")

    def _c(self, text, color):
        return f"{color}{text}{self.R}"

    def banner(self, name, desc, version):
        print(self._c("=" * 60, self.CYAN))
        print(self._c(f" {name} {version}", self.BOLD + self.CYAN))
        print(self._c(f" {desc}", self.CYAN))
        print(self._c(f" 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}", self.CYAN))
        print(self._c("=" * 60, self.CYAN))

    def info(self, msg, indent=0):
        print(" " * indent + self._c(f"ℹ️ {self._ts()} {msg}", self.BLUE))

    def ok(self, msg, indent=0):
        print(" " * indent + self._c(f"✅ {self._ts()} {msg}", self.GREEN))

    def warn(self, msg, indent=0):
        print(" " * indent + self._c(f"⚠️ {self._ts()} {msg}", self.YELLOW))

    def err(self, msg, indent=0):
        print(" " * indent + self._c(f"❌ {self._ts()} {msg}", self.RED))

    def skip(self, msg, indent=0):
        print(" " * indent + self._c(f"⏭️ {self._ts()} {msg}", self.YELLOW))

    def step(self, msg, indent=0):
        print(" " * indent + self._c(f"▶️ {self._ts()} {msg}", self.CYAN))


log = Logger()

# ============================================================
# 服务端下注记录判断(防重复下注: 当天每账号只下注一次)
# 通过 prizeDetailed(投注记录)接口查今天是否有 created_at 为今日的记录
# ============================================================

def _today_bet_done(session, token):
    """查服务端投注记录, 判断今天是否已下注过"""
    p = _safe_request(session, "/api/mark3/thunder/prizeDetailed",
                      {"limit": 20, "search_start_id": 0, "max_date": "", "timestamp": int(time.time())}, token)
    if not p or p.get("code") != 0:
        log.warn("投注记录查询失败, 保守起见按未下注处理")
        return False
    today = time.strftime("%Y-%m-%d")
    records = ((p.get("data") or {}).get("data") or [])
    for rec in records:
        created = (rec or {}).get("created_at", "")
        if created.startswith(today):
            return True
    return False

# ============================================================
# notify 双路径(存在则发, 不存在静默跳过)
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
# 请求封装
# ============================================================
def _aes_encrypt(obj):
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
    except ImportError:
        log.err("缺少 pycryptodome, 请先 pip install pycryptodome")
        sys.exit(1)
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode()
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return __import__("base64").b64encode(c.encrypt(pad(raw, 16))).decode()


def _safe_request(session, path, payload, token=""):
    for i in range(RETRY):
        try:
            headers = {
                "user-agent": DEVICE["user-agent"],
                "system": DEVICE["system"],
                "abi": DEVICE["abi"],
                "content-type": "application/json",
                "timestamp": str(int(time.time() * 1000)),
                "token": token,
                "mobile-model": DEVICE["mobile-model"],
                "lang": DEVICE["lang"],
                "version": DEVICE["version"],
                "equipment": DEVICE["equipment"],
            }
            r = session.post(
                BASE + path,
                json={"body": _aes_encrypt(payload)},
                headers=headers,
                timeout=TIME_OUT,
            )
            return r.json()
        except Exception as e:
            if i < RETRY - 1:
                time.sleep(2)
            else:
                log.warn(f"{path} 请求失败: {e}")
    return None


# ============================================================
# 核心流程
# ============================================================
def run_account(email, password):
    log.step(f"开始处理账号 {_mask(email)}")
    session = requests.Session()
    ts = int(time.time())

    # 1. 登录
    rj = _safe_request(session, "/api/mark1/login",
                       {"email": email, "password": password, "timestamp": ts})
    if not rj or rj.get("code") != 0:
        log.err(f"登录失败: {rj}")
        send_notify("巨浪大游", f"登录失败: {rj}")
        return
    token = rj["data"]["token"]
    log.ok("登录成功")

    # 2. 余额
    rj = _safe_request(session, "/api/mark1/funds/balance", {"timestamp": int(time.time())}, token)
    balance = (rj or {}).get("data", {}).get("bgc", 0)
    log.ok(f"当前余额: {balance} BGC")

    # 3. 签到状态
    rj = _safe_request(session, "/api/mark1/sign/info", {"timestamp": int(time.time())}, token)
    d = (rj or {}).get("data", {})
    if d.get("today_is_sign"):
        log.skip("今日已签到, 无需操作")
        return
    log.info(f"今日未签到(连续第 {d.get('continuous_day', 0)} 天)")

    # 4. 若已完成游戏任务直接签到
    if d.get("is_finish_task"):
        log.ok("今日游戏任务已完成(is_finish_task=true), 直接签到")
        rj = _safe_request(session, "/api/mark1/sign/checkIn", {"timestamp": int(time.time())}, token)
        if rj and rj.get("code") == 0:
            gain = (rj.get("data") or {}).get("bgc", 0)
            log.ok(f"签到成功, 获得 {gain} BGC")
            send_notify("巨浪大游", f"签到成功 +{gain} BGC(余额 {balance} → 稍后刷新)")
            _print_balance(session, token)
            return
        log.warn(f"签到失败: {rj}")
        return

    # 4.1 本地记录防重复下注: 今天该账号已下注过则不再下注, 直接签到
    if _today_bet_done(session, token):
        log.skip("今天已下注过(服务端记录), 不再下注, 直接签到")
        rj = _safe_request(session, "/api/mark1/sign/checkIn", {"timestamp": int(time.time())}, token)
        if rj and rj.get("code") == 0:
            gain = (rj.get("data") or {}).get("bgc", 0)
            log.ok(f"签到成功, 获得 {gain} BGC")
            send_notify("巨浪大游", f"签到成功 +{gain} BGC")
        else:
            log.err(f"签到失败: {rj}")
        _print_balance(session, token)
        return

    # 5. 余额不足 0.5 则无法下注, 直接尝试签到
    if balance < 0.5:
        log.warn("余额不足 0.5 BGC, 跳过下注直接尝试签到")
        rj = _safe_request(session, "/api/mark1/sign/checkIn", {"timestamp": int(time.time())}, token)
        log.info(f"签到结果: {rj}")
        return

    # 6. 等下注窗口(progress=1 且至少一条线赔率>0)
    log.step("等待下注窗口...")
    bet_ok = False
    for i in range(WAIT_ROUNDS):
        ts = int(time.time())
        p = _safe_request(session, "/api/mark3/thunder/getProgress", {"timestamp": ts}, token)
        s = _safe_request(session, "/api/mark3/thunder/getBetShares", {"timestamp": ts}, token)
        pdata = (p or {}).get("data", {})
        shares = (s or {}).get("data", [])
        pr = pdata.get("progress")
        sec = pdata.get("second", 0)
        if pr != 1:
            log.info(f"[轮询{i+1}] prog={pr} 开奖/结算中, 等待下一期投注")
            time.sleep(5)
            continue
        open_lines = [j + 1 for j, v in enumerate(shares) if v and float(v) > 0]
        if not open_lines or sec <= 10:
            log.info(f"[轮询{i+1}] prog=1 sec={sec} 窗口刚开/快关, 可投线尚未开放")
            time.sleep(5)
            continue
        # 显示当前可投线及赔率
        line_desc = " ".join(f"{j}({shares[j-1]})" for j in open_lines)
        log.info(f"[轮询{i+1}] prog=1 sec={sec} 窗口已开, 可投线: {line_desc}")
        # 从 5 条线中随机选一条可投的(输赢无所谓, 只为完成当局)
        best = random.choice(open_lines)
        log.info(f"随机选中线{best}(赔率{shares[best-1]})")
        rj = _safe_request(session, "/api/mark3/thunder/thunderBet",
                           {"model_id": best, "num": BET_NUM, "timestamp": ts}, token)
        if rj and rj.get("code") == 0:
            log.ok(f"下注成功: 线{best} x{BET_NUM} 注(0.5 BGC), 赔率 {shares[best-1]}")
            bet_ok = True
            break
        else:
            log.warn(f"下注被拒: {rj}")
            time.sleep(5)
    if not bet_ok:
        log.err("未能成功下注(可能是投注窗口太短), 直接尝试签到")
        rj = _safe_request(session, "/api/mark1/sign/checkIn", {"timestamp": int(time.time())}, token)
        log.info(f"签到结果: {rj}")
        return

    # 7. 等待当局开奖(无论输赢, 有结果即可签到)
    log.step("等待当局开奖...")
    saw2 = False
    settled = False
    for i in range(RESULT_ROUNDS):
        time.sleep(5)
        p = _safe_request(session, "/api/mark3/thunder/getProgress", {"timestamp": int(time.time())}, token)
        pdata = (p or {}).get("data", {})
        pr = pdata.get("progress")
        sec = pdata.get("second", 0)
        if pr == 2:
            saw2 = True
        if saw2 and pr == 1:
            # 查最新一期开奖, 判断压的线是否中
            tp = _safe_request(session, "/api/mark3/thunder/tenPeriod", {"timestamp": int(time.time())}, token)
            ten = ((tp or {}).get("data") or {}).get("ten", [])
            win_lines = ten[0].get("win", []) if ten else []
            if best in win_lines:
                log.ok(f"当局已开奖(线{best} 中了! 赔率{shares[best-1]})")
            else:
                log.info(f"当局已开奖(线{best} 未中, 输 0.5 BGC)")
            log.ok("游戏任务已完成, 可以签到")
            settled = True
            break
        if saw2 and pr == 3:
            log.info(f"当局结算中(prog=3, sec={sec})")
            time.sleep(6)
            tp = _safe_request(session, "/api/mark3/thunder/tenPeriod", {"timestamp": int(time.time())}, token)
            ten = ((tp or {}).get("data") or {}).get("ten", [])
            win_lines = ten[0].get("win", []) if ten else []
            if best in win_lines:
                log.ok(f"当局已开奖(线{best} 中了! 赔率{shares[best-1]})")
            else:
                log.info(f"当局已开奖(线{best} 未中, 输 0.5 BGC)")
            log.ok("游戏任务已完成, 可以签到")
            settled = True
            break
        log.info(f"[轮询{i+1}] prog={pr} sec={sec}")
    if not settled:
        log.warn("等待超时未确认开奖, 仍尝试签到")

    # 8. 签到
    rj = _safe_request(session, "/api/mark1/sign/checkIn", {"timestamp": int(time.time())}, token)
    if rj and rj.get("code") == 0:
        gain = (rj.get("data") or {}).get("bgc", 0)
        log.ok(f"签到成功, 获得 {gain} BGC")
        send_notify("巨浪大游", f"签到成功 +{gain} BGC")
    else:
        log.err(f"签到失败: {rj}")
        send_notify("巨浪大游", f"签到失败: {rj}")

    _print_balance(session, token)


def _mask(email):
    """账号脱敏: 保留前3后2, 中间打码"""
    if len(email) <= 6:
        return email[:1] + "***"
    return email[:3] + "***" + email[-2:]


def _print_balance(session, token):
    rj = _safe_request(session, "/api/mark1/funds/balance", {"timestamp": int(time.time())}, token)
    balance = (rj or {}).get("data", {})
    log.info(f"当前余额: {balance}")


if __name__ == "__main__":
    log.banner("巨浪大游", "下注完成游戏任务后签到领 BGC", "v1.0.0")
    try:
        summary = []
        for acct in ACCOUNTS:
            email, password = acct.split("#", 1)
            try:
                run_account(email, password)
                summary.append(f"{_mask(email)}: 完成")
            except Exception as e:
                log.err(f"账号 {_mask(email)} 异常: {e}")
                summary.append(f"{_mask(email)}: 异常")
                send_notify("巨浪大游", f"账号 {_mask(email)} 异常: {e}")
        if len(ACCOUNTS) > 1:
            log.step("===== 汇总 =====")
            for s in summary:
                log.info(s)
            send_notify("巨浪大游", "\n".join(summary))
    except KeyboardInterrupt:
        log.warn("用户中断")
    except Exception as e:
        log.err(f"异常: {e}")
        send_notify("巨浪大游", f"脚本异常: {e}")

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