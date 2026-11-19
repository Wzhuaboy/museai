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
1KF 会员中心（vip.1kf.com）自动签到脚本 —— 适配青龙面板

注册地址：https://vip.1kf.com/index?t=13392
禁止多号，一个人玩一个号就行，多号必封

环境变量：
  KF_COOKIE        必填。浏览器里 vip.1kf.com 的 Cookie 串，
                   至少含 session_token（PHPSESSID 也带上更稳）
  KF_LOTTERY       可选，默认 0（不抽奖）。设 1 才积分抽奖，每次消耗 10 积分
  KF_LOTTERY_TIMES 可选，默认 1。每轮最多抽几次
  KF_EXCHANGE      可选，默认 1。积分够线自动兑换成余额（1 元 = 20 积分）
  KF_EXCHANGE_MIN  可选，默认 20。兑换门槛（站点写死最低 20 积分，填更小无效）
  KF_EXCHANGE_ALL  可选，默认 0。0=只兑 20 的整数倍，余额留零头；1=全部兑光
  KF_NOTIFY        可选，默认 1。是否推送通知（需青龙已配置通知）

青龙定时：0 8 * * *   （每天 8 点）

作者：Minis
"""

import os
import re
import sys
import json
import time
import random
import logging
import requests

BASE = "https://vip.1kf.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("1kf")

# --------------------------------------------------------------------------
# 通用
# --------------------------------------------------------------------------

def env(key, default=""):
    v = os.environ.get(key)
    return default if v is None or v.strip() == "" else v.strip()


def env_flag(key, default=True):
    v = env(key, "").lower()
    if v == "":
        return default
    return v in ("1", "true", "yes", "on", "y")


def mask(s, keep=4):
    s = str(s)
    if len(s) <= keep * 2:
        return s[:1] + "***"
    return s[:keep] + "***" + s[-keep:]


def parse_cookie(raw):
    """支持 'k=v; k2=v2' 或直接粘贴报头值。返回 dict。"""
    out = {}
    for part in re.split(r"[;\n]", raw):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        if k.lower() in ("path", "domain", "expires", "max-age", "samesite",
                         "secure", "httponly"):
            continue
        out[k] = v.strip()
    return out


class KF:
    def __init__(self, cookie):
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": BASE + "/qiandao",
            "Origin": BASE,
        })
        for k, v in cookie.items():
            self.s.cookies.set(k, v, domain="vip.1kf.com", path="/")
        self.uid = None
        self.csrf = None
        self.points = None
        self.rate = 20.0

    # ---- 基础请求 -------------------------------------------------------
    def get(self, path, **kw):
        kw.setdefault("timeout", 25)
        r = self.s.get(BASE + path, **kw)
        r.encoding = "utf-8"
        return r

    def post(self, path, data, **kw):
        kw.setdefault("timeout", 25)
        r = self.s.post(BASE + path, data=data, **kw)
        r.encoding = "utf-8"
        return r

    def post_json(self, path, data):
        r = self.post(path, data, headers={"Accept": "application/json, text/javascript, */*; q=0.01"})
        try:
            return r.json()
        except Exception:
            snippet = re.sub(r"\s+", " ", r.text)[:200]
            raise RuntimeError(f"{path} 返回非 JSON（HTTP {r.status_code}）：{snippet}")

    # ---- 状态解析 -------------------------------------------------------
    @staticmethod
    def parse_page(html):
        st = {"logged_in": False, "uid": None, "signed": None,
              "streak": None, "csrf": None, "points": None}
        m = re.search(r'VIP-username[^>]*>\s*(?:ID#)?(\d+)', html)
        if m:
            st["logged_in"] = True
            st["uid"] = m.group(1)
        if "退出登录" in html or "logout=1" in html:
            st["logged_in"] = True
        # 签到状态：disabled 按钮 / “今日已签到”
        st["signed"] = bool(
            re.search(r'SIGN-checkin-btn-disabled', html)
            or re.search(r'今日已签到', html)
        )
        m = re.search(r'已连续签到\s*<strong[^>]*>\s*(\d+)\s*</strong>', html)
        if m:
            st["streak"] = int(m.group(1))
        m = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)', html)
        if m:
            st["csrf"] = m.group(1)
        m = re.search(r'id="userPoints"[^>]*>\s*([\d.]+)', html)
        if m:
            st["points"] = float(m.group(1))
        return st

    def fetch_state(self):
        r = self.get("/qiandao")
        if r.status_code != 200:
            raise RuntimeError(f"打开签到页失败 HTTP {r.status_code}")
        st = self.parse_page(r.text)
        if not st["logged_in"]:
            raise RuntimeError("Cookie 已失效或未登录（页面没有用户信息），请重新获取")
        self.uid = st["uid"]
        self.csrf = st["csrf"]
        if st.get("points") is not None:
            self.points = st["points"]
        return st

    # ---- 签到 -----------------------------------------------------------
    def sign(self):
        """返回 (ok, message)"""
        if not self.csrf:
            # 部分版本页面不渲染 csrf hidden input，此时按空值提交
            self.csrf = ""
        try:
            res = self.post_json("/public/sign_ajax.php", {"csrf_token": self.csrf})
        except RuntimeError as e:
            return False, str(e)
        if res.get("success"):
            msg = res.get("message") or "签到成功"
            extra = []
            if res.get("streak_msg"):
                extra.append(res["streak_msg"])
            if res.get("qiyu_msg"):
                extra.append(res["qiyu_msg"])
            if res.get("sign_streak"):
                extra.append(f"连续{res['sign_streak']}天")
            return True, msg + ("（" + "；".join(extra) + "）" if extra else "")
        return False, res.get("message") or json.dumps(res, ensure_ascii=False)[:200]

    # ---- 抽奖 -----------------------------------------------------------
    def lottery(self):
        """抽一次，返回 (ok, text)"""
        try:
            res = self.post_json("/choujiang", {"action": "draw"})
        except RuntimeError as e:
            return False, str(e)
        if res.get("code") != 0:
            return False, res.get("msg") or res.get("message") or json.dumps(res, ensure_ascii=False)[:120]
        prize = res.get("prize") or {}
        pname = {"balance": "元余额", "points": "积分", "growth": "经验值",
                 "shiwubi": "实物币", "quiz_points": "活动点"}
        ptype = prize.get("prize_type") or ""
        pval = prize.get("prize_value") or 0
        if res.get("msg"):
            text = res["msg"]
        elif float(pval or 0) > 0:
            text = f"+{pval}{pname.get(ptype, ptype)}"
        else:
            text = "谢谢参与"
        if res.get("is_time_rule_special"):
            text = "时段必中：" + text
        return True, text

    # ---- 资产 -----------------------------------------------------------
    def assets(self):
        """从 /exchange_logs 读取 积分 / 余额 / 活动点（最可靠的来源，带统计卡片）"""
        out = {}
        try:
            html = self.get("/exchange_logs").text
            st = self.parse_exchange(html)
            out.update({k: v for k, v in st.items() if v is not None})
            if "points" in out:
                self.points = out["points"]
            if st.get("rate"):
                self.rate = st["rate"]
        except Exception as e:
            log.warning("读取资产失败：%s", e)
        return out

    @staticmethod
    def parse_exchange(html):
        """解析兑换页统计卡片：当前积分 / 当前余额 / 当前活动点；顺带拿兑换比例"""
        st = {"points": None, "balance": None, "quiz_points": None, "rate": None}
        cards = re.findall(
            r'<div class="exchange-stat">\s*<div class="label">([^<]+)</div>\s*'
            r'<div class="value[^"]*"[^>]*>([^<]*)</div>', html)
        for label, value in cards:
            v = re.sub(r"[^\d.]", "", value)
            if not v:
                continue
            label = label.strip()
            if "积分" in label and "活动" not in label:
                st["points"] = float(v)
            elif "余额" in label:
                st["balance"] = float(v)
            elif "活动点" in label:
                st["quiz_points"] = float(v)
        m = re.search(r'1\s*元\s*=\s*<strong>([\d.]+)</strong>\s*积分', html)
        if m:
            st["rate"] = float(m.group(1))
        return st

    # ---- 兑换（积分 → 余额现金） -----------------------------------------
    def exchange(self, points):
        """把 points 积分兑换成余额。返回 (ok, message)"""
        points = int(points)
        rate = self.rate or 20.0
        gain = int(points // rate)
        try:
            res = self.post_json("/exchange_logs", {"exchange_submit": 1, "points": points})
        except RuntimeError as e:
            return False, str(e)
        if res.get("success"):
            msg = res.get("message") or "兑换成功"
            return True, f"{points}积分 → {msg}（余额 +{gain}元）"
        return False, res.get("message") or json.dumps(res, ensure_ascii=False)[:160]


# --------------------------------------------------------------------------
# 通知（青龙 notify 命令，不存在则跳过）
# --------------------------------------------------------------------------

def notify(title, content):
    if not env_flag("KF_NOTIFY", True):
        return
    log.info("===== 通知 =====\n%s\n%s", title, content)
    try:
        from notify import send  # 青龙内置
        send(title, content)
        return
    except Exception:
        pass
    # 兜底：直接调用 notify 命令
    import subprocess
    import shutil
    if shutil.which("notify"):
        try:
            subprocess.run(["notify", title, content], timeout=20, check=False)
        except Exception as e:
            log.warning("notify 调用失败：%s", e)


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------

def run_account(name, cookie_raw, lottery_on, lottery_times,
                exchange_on=True, exchange_min=20.0, exchange_keep=True):
    lines = [f"账号：{name}"]
    cookie = parse_cookie(cookie_raw)
    if not cookie:
        lines.append("❌ Cookie 解析失败")
        return False, lines

    kf = KF(cookie)
    try:
        st = kf.fetch_state()
    except Exception as e:
        lines.append(f"❌ {e}")
        return False, lines

    log.info("[%s] uid=%s 已签到=%s 连续=%s", name, st["uid"], st["signed"], st["streak"])
    lines.append(f"用户ID：{kf.uid}")

    # ---- 签到 ----
    if st["signed"]:
        lines.append(f"✅ 今日已签到（连续 {st['streak'] or '?'} 天）")
        signed_ok = True
    else:
        time.sleep(random.uniform(1, 3))
        ok, msg = kf.sign()
        if ok:
            log.info("[%s] 签到成功：%s", name, msg)
            lines.append(f"✅ 签到成功：{msg}")
            signed_ok = True
        else:
            log.warning("[%s] 签到失败：%s", name, msg)
            lines.append(f"❌ 签到失败：{msg}")
            signed_ok = False

    # ---- 抽奖 ----
    if lottery_on and lottery_times > 0:
        results = []
        for i in range(lottery_times):
            # 抽奖前刷新积分：已够兑换线就先保本金，不拿去赌
            kf.points = None
            kf.assets()
            pts = kf.points
            if pts is not None and pts >= 10 and pts >= exchange_min:
                results.append(f"积分 {pts:g} 已达兑换线，不再抽奖")
                break
            if pts is not None and pts < 10:
                results.append(f"积分 {pts:g} 不足 10，跳过抽奖")
                break
            time.sleep(random.uniform(2, 4))
            ok, txt = kf.lottery()
            log.info("[%s] 第%d次抽奖：%s %s", name, i + 1, ok, txt)
            results.append(("✅ " if ok else "⚠️ ") + f"第{i+1}抽：{txt}")
            if not ok:
                break
        if results:
            lines.append("🎰 抽奖：" + " | ".join(results))
    elif lottery_on:
        lines.append("🎰 抽奖：已开启但次数为 0（KF_LOTTERY_TIMES=0）")
    # 抽奖关闭时不输出任何提示，保持通知干净

    # ---- 积分兑换余额（现金） ----
    if exchange_on:
        kf.points = None
        assets = kf.assets()
        pts = kf.points
        rate = kf.rate or 20.0
        log.info("[%s] 兑换前：积分 %s / 余额 %s / 活动点 %s / 比例 1元=%s积分",
                 name, assets.get("points"), assets.get("balance"),
                 assets.get("quiz_points"), rate)
        if pts is None:
            lines.append("💰 兑换：读取积分失败，跳过")
        elif pts < exchange_min:
            lines.append(f"💰 兑换：积分 {pts:g} < {exchange_min:g}，未达兑换线"
                         f"（余额 ¥{assets.get('balance', 0):.2f}）")
        else:
            to_ex = int(pts // rate * rate) if exchange_keep else int(pts)
            gain = int(to_ex // rate)
            time.sleep(random.uniform(1, 3))
            ok, msg = kf.exchange(to_ex)
            if ok:
                log.info("[%s] 兑换成功：%s", name, msg)
                # 兑换后刷新真实余额
                kf.points = None
                after = kf.assets()
                lines.append(f"💰 兑换成功：{msg}；现余额 ¥{after.get('balance', gain):.2f}，"
                             f"剩余积分 {after.get('points', 0):g}")
            else:
                log.warning("[%s] 兑换失败：%s", name, msg)
                lines.append(f"❌ 兑换失败：{msg}")
    return signed_ok, lines


def main():
    raw = env("KF_COOKIE")
    if not raw:
        notify("1KF签到 - 未配置", "缺少环境变量 KF_COOKIE，请在青龙环境变量里添加")
        log.error("缺少环境变量 KF_COOKIE")
        return 1

    # 抽奖默认关闭：积分留着兑换现金更划算。KF_LOTTERY=1 才抽
    lottery_on = env_flag("KF_LOTTERY", False)
    try:
        lottery_times = int(env("KF_LOTTERY_TIMES", "1"))
    except ValueError:
        lottery_times = 1
    lottery_times = max(0, min(lottery_times, 30))

    exchange_on = env_flag("KF_EXCHANGE", True)
    try:
        exchange_min = float(env("KF_EXCHANGE_MIN", "20"))
    except ValueError:
        exchange_min = 20.0
    exchange_min = max(20.0, exchange_min)   # 站点最低 20 积分起兑
    exchange_keep = not env_flag("KF_EXCHANGE_ALL", False)

    # 多账号：多个 cookie 用 & 或换行分隔（也兼容青龙的 # 备注）
    accounts = []
    for idx, block in enumerate(re.split(r"[\n&]+", raw)):
        block = block.strip().rstrip("#").strip()
        if not block or "=" not in block:
            continue
        accounts.append(block)

    if not accounts:
        notify("1KF签到 - 配置错误", "KF_COOKIE 内容为空或格式不正确")
        return 1

    all_lines = []
    success_cnt = 0
    for i, ck in enumerate(accounts, 1):
        name = f"账号{i}"
        log.info("===== 处理 %s =====", name)
        ok, lines = run_account(name, ck, lottery_on, lottery_times,
                                exchange_on, exchange_min, exchange_keep)
        if ok:
            success_cnt += 1
        all_lines.append("\n".join(lines))
        if i < len(accounts):
            time.sleep(random.uniform(3, 6))

    title = f"1KF签到 {success_cnt}/{len(accounts)} 成功"
    full = "\n\n".join(all_lines)
    log.info("===== 汇总 =====\n%s", full)   # 无论是否推送，日志里都留一份
    notify(title, full)

    # 青龙任务状态
    if success_cnt == len(accounts):
        print("【任务完成】全部账号签到成功")
        return 0
    print(f"【任务异常】成功 {success_cnt}/{len(accounts)}")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)


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