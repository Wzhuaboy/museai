// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

#!/usr/bin/env node
'use strict';
/**
 * 
 * 项目地址：https://qingke.junfengkeji.top/s/w_9RFIIVdhc1VLg6NgdENA
 * 
 * ════════════════════════════════════════════════════════════════════════════════
 * 青龙面板（QingLong）纯 Node.js 版  v1.3.1-cli
 * ════════════════════════════════════════════════════════════════════════════════
 * 【依赖】
 *   Node >= 18（用全局 fetch）。Node < 18 需要 `npm i axios`，脚本自动回落。
 *   无其它第三方依赖。
 *   可选：同目录 / 上级目录 / node_modules 里存在 sendNotify.js（青龙经典推送三件套）时自动推送，
 *   找不到就静默跳过 —— 通知失败绝不会影响退出码。
 *
 * 【环境变量】
 *   QK_ACCOUNTS        账号串（最高优先级）。支持逗号 , 分号 ; 换行分隔，
 *                      元素形如 手机号#密码 或 手机号&密码
 *   QK_PHONE           单号手机号（配合 QK_PASSWORD）
 *   QK_PASSWORD        单号密码
 *   QK_MODE            运行模式：全自动 | 仅登录 | 仅签到 | 仅任务中心 | 查进度 | 大厅红包 | 人脉自测
 *   QK_BASE_URL        覆盖 BASE_URL（本地 mock / 抓包代理用，默认 https://qingke.junfengkeji.top）
 *   QK_NOTIFY          =0 关闭推送通知（默认开启）
 *   QK_TASK_INTERVAL   任务间隔 ms（默认 1500，下限 300）
 *   QK_MULTI_DELAY     多号间隔开关 1/0（默认 1 开）
 *   QK_DELAY_A         多号间隔下限秒（默认 3）
 *   QK_DELAY_B         多号间隔上限秒（默认 6）
 *   QK_LOGIN_INTERVAL  登录/刷新最小间隔 ms（默认 3000，下限 500；多号同时登录时防 IP 限流）
 *
 * 【命令行参数】
 *   node 轻客-青龙.js                          无参数 = 全自动，账号从环境变量 / 轻客账号.txt 取
 *   --mode=全自动|仅登录|仅签到|仅任务中心|查进度|大厅红包|人脉自测
 *   --accounts=手机号#密码,手机号#密码
 *   --debug                                    打 RAW（响应体前 800 字符，截断）
 *   --once                                     忽略缓存令牌，强制重新登录
 *   --probe                                    强制跑人脉口径 D1..D8 探测（不信内置 D7 默认）
 *   --help / -h                                帮助
 *
 * 【账号文件】
 *   脚本同目录 轻客账号.txt，每行 `手机号#密码`，`#` 开头为注释行。
 *
 * 【缓存】（不再是 /sdcard/...，全部落在脚本同目录 .cache/）
 *   .cache/qingke_tokens.json   每号 token / refreshToken / expiresAt / deviceId
 *   .cache/qingke_renmai.json   人脉任务口径（D7 contact_popup 命中后写盘，下次直接复用）
 *
 * 【退出码】
 *   0 全部账号成功   1 有账号失败   2 配置缺失 / 运行环境不满足
 *
 * 【青龙定时建议】
 *   0 8 * * *        每天 8:00 跑一次全自动
 *   0 0-23/6 * * *   每 6 小时一次（等价于 0 星号/6 写法；签到/领奖都是幂等的，重复跑不会重复计次）
 *   注意：大厅红包是服务端 30 秒真实计时（每 10 秒心跳、最多 6 轮），单号全自动约 1~3 分钟。
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ═══════════════ 常量 ═══════════════
const SCRIPT_VER = '1.3.1-cli';
const 项目名 = '轻客';
const BASE_URL = process.env.QK_BASE_URL || 'https://qingke.junfengkeji.top';
const APP_CODE = 'root';           // X-Qingke-App-Code：原 App N() 取未定义环境变量 → "root"
const SESSION_VER = '2';           // X-Qingke-Session-Version
const APP_VER = '2.1.3';           // X-App-Version（2026-10-31 按「轻客登录成功包」对齐）
const TOKEN_AHEAD = 600;           // 令牌提前 600 秒刷新
const HTTP_TIMEOUT = 15000;
// UA 固定（Node 里没有 device 对象）：与真机抓包/APK 2.1.3 的 uni-app 串一致
const UA = 'Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 uni-app (Immersed/32.363636) Html5Plus/1.0';

// 服务端没给 dailyLimit 时的回落值（正常情况一律用服务端下发值）
const 默认浏览人脉 = 8, 默认浏览项目 = 8, 默认浏览软件 = 8;
const 默认分享 = 1, 默认点赞 = 5;

// 每日任务真实 code —— 真机确认就这 7 个（精确匹配优先，标题关键字只做兜底）
const 任务码表 = {
    browse_network: 1, share_network: 1,
    browse_project: 1, share_project: 1,
    browse_software: 1, share_software: 1,
    like_software: 1
};
// 这些 status 的每日任务不再发动作
const 跳过状态 = { locked: 1, maxed: 1, claimed: 1, disabled: 1 };

const 错误码中文 = {
    user_login_password_wrong: '密码错误',
    user_login_invalid: '手机号或密码错误 / 登录已失效',
    user_token_app_mismatch: '登录已失效，请重新登录',
    user_request_app_mismatch: '登录已失效，请重新登录',
    user_token_app_code_mismatch: '登录已失效，请重新登录',
    token_refresh_failed: '令牌刷新失败',
    checkin_already_done: '今日已签到',
    user_real_name_verification_required: '需实名认证后才可继续',
    request_failed: '请求失败',
    network_error: '网络错误',
    response_parse_error: '响应解析失败',
    user_login_too_many_attempts: '该账号登录尝试过多，已被临时锁定',
    user_login_ip_rate_limited: '当前网络登录次数过多，已被限流',
    login_cooldown: '登录限流冷却中'
};

const 红包模式 = {
    最多轮: 3,          // 大厅重扫轮数上限（防死循环）
    列表页上限: 8,      // 单个 sortMode 最多翻 8 页
    每页条数: 20,       // App 硬编码 pageSize=20
    无红包页上限: 3,    // 连续 3 页没有 hasRedPacket 就停
    心跳上限: 6,        // 心跳 6 轮 ≈ 60 秒，超时算失败（不发 claim）
    心跳间隔: 10000,    // 与 App 的 setInterval(...,1e4) 一致
    领间隔: 1500,       // claim 必须串行，条与条之间
    重建上限: 1,        // 心跳失败只弃会话重建一次
    原样输出: 800       // RAW 截断长度
};
// 401 族登录失效码（与 App 的 Ye 集合一致）
const 登录失效码 = {
    user_login_invalid: 1,
    user_token_app_mismatch: 1,
    user_request_app_mismatch: 1,
    user_token_app_code_mismatch: 1
};
const 分享场景映射 = {
    hall_project_detail_share: 'share_project',
    network_contact_popup_share: 'share_network',
    software_detail_share: 'share_software'
};

const MODE_LIST = ['全自动', '仅登录', '仅签到', '仅任务中心', '查进度', '大厅红包', '人脉自测'];
const MODE_HINTS = [
    '全自动：登录 → 查任务中心 → 签到 → 浏览人脉/项目/软件 → 分享 → 点赞软件 → 领取全部奖励 → 大厅红包 → 输出今日战绩',
    '仅登录：只验证手机号密码能否登录，拿到并缓存令牌后结束',
    '仅签到：只做每日签到（含首日卡），不发浏览/分享/点赞请求',
    '仅任务中心：只做 7 个每日任务（浏览×8/分享×1/点赞×5 三类）并领奖，不签到',
    '查进度：只读 /api/user/tasks/center，打印全部任务快照与签到状态，不发任何写请求',
    '大厅红包：找大厅里带红包的文章（列表只给 hasRedPacket，逐篇拉详情取 redPacketId），看满服务端 30 秒（每 10 秒心跳，资格只认 eligibleDisplay==1）后领取，直到没有可领的为止（最多 3 轮）',
    '人脉自测：只跑第一个可用账号，对同一张人脉卡依次打 6 个参数变体，每条前后各读一次 browse_network doneCount'
];

// ═══════════════ 路径（不再 /sdcard/...）═══════════════
const CACHE_DIR = path.join(__dirname, '.cache');
const TOKEN_FILE = path.join(CACHE_DIR, 'qingke_tokens.json');
const RENMAI_FILE = path.join(CACHE_DIR, 'qingke_renmai.json');
const ACCOUNT_FILE = path.join(__dirname, '轻客账号.txt');

// ═══════════════ 全局状态 ═══════════════
var 运行参数 = { mode: '', accounts: '', debug: false, once: false, probe: false };
var 运行配置 = { 任务间隔: 1500, 多号延迟: true, 延迟A: 3, 延迟B: 6, 登录间隔: 3000 };
var db = [];                      // 解析后的账号：[{账号, 密码}]
var 开始检测 = true;
var 停止标志 = false;
var 导出原始 = { on: false };      // 原始响应探针
var 本次签到 = { ok: false, already: false, date: '' };
var 上次红包结果 = null;
var 本号统计 = {};
var 汇总 = { 记录: [], 成功: 0, 失败: 0, 开始: Date.now(), 中断: false };
var 人脉口径 = null;
var 人脉按次数 = null;
var 人脉探测上限 = 8;
const 默认人脉口径 = {
    action: 'contact_popup', offset: 0, sortMode: 'all', mode: 'server',
    标签: 'D7 contact_popup', 来源: '内置默认', 按次数: true, 时间: 0
};
var 凭证缓存 = {};

// 登录限流（HTTP 429）：冷却期内不再发登录/刷新；IP 级限流会中止后续账号
var 限流冷却 = 0;
var 限流中止 = false;
var 限流信息 = '';
var 账号冷却 = {};          // 账号级锁定：phone -> 解禁时间戳
var 上次认证时间 = 0;       // 登录/刷新串行最小间隔

function 可继续() { return 开始检测 && !停止标志; }

// ═══════════════ 日志 ═══════════════
function nowStr() {
    const n = new Date();
    return ('0' + n.getHours()).slice(-2) + ':' + ('0' + n.getMinutes()).slice(-2) + ':' + ('0' + n.getSeconds()).slice(-2);
}
function 级别名(类型) {
    const m = { success: 'OK', warn: 'WARN', error: 'ERROR', info: 'INFO', log: 'INFO' };
    return m[String(类型 || 'info')] || 'INFO';
}
function log(内容, 类型, 标记) {
    const 级 = 级别名(类型);
    const 号 = 标记 ? String(标记) : '全局';
    const out = '[' + nowStr() + '] [' + 号 + '] [' + 级 + '] ' + String(内容 == null ? '' : 内容);
    if (级 === 'ERROR') console.error(out);
    else console.log(out);
}
// 原始响应探针（标 RAW）：--debug 或 查进度/探测 模式开启；默认截断 800
function logRaw(tag, 标签, j, 限) {
    if (!导出原始.on && !运行参数.debug) return;
    let raw = '';
    try {
        if (j && j.__raw != null) raw = String(j.__raw);
        else raw = JSON.stringify(j == null ? null : j);
    } catch (e) { raw = ''; }
    const n = Number(限 || 0);
    const lim = (n > 0) ? n : 800;
    if (raw.length > lim) raw = raw.substring(0, lim) + '…（截断）';
    log('RAW[' + 标签 + '] ' + raw, 'info', tag);
}
// 强制打原始报文（不受开关限制）：签到 409 / 口径探测这类「必须留证」的场合
function logRaw强制(tag, 标签, j, 限) {
    const 原 = 导出原始.on;
    导出原始.on = true;
    try { logRaw(tag, 标签, j, 限); } finally { 导出原始.on = 原; }
}
// 响应头取一个值（大小写不敏感）：签到 409 要拿服务端 Date 与本地日期对照
function 取响应头(headers, 名) {
    if (!headers) return '';
    const want = String(名 || '').toLowerCase();
    let hit = '';
    try {
        for (const k in headers) {
            if (String(k).toLowerCase() !== want) continue;
            hit = String(headers[k]);
            break;
        }
    } catch (e) {}
    if (!hit) {
        try { if (headers[want] != null) hit = String(headers[want]); } catch (e2) {}
    }
    return hit;
}

// ═══════════════ 基础工具 ═══════════════
function md5Hex(str) { return crypto.createHash('md5').update(String(str), 'utf8').digest('hex'); }
function maskAcc(s) {
    s = String(s || '');
    if (s.length >= 11) return s.substring(0, 3) + '****' + s.substring(7);
    return s;
}
function isPhone(s) { return /^1[3-9]\d{9}$/.test(String(s || '').trim()); }
// 服务端 idempotencyKey 生成器：原 App ht(e) = `${e}-${Date.now()}-${Math.random().toString(36).slice(2)}`
function ht(prefix) {
    return String(prefix) + '-' + Date.now() + '-' + Math.random().toString(36).slice(2);
}
function 日期补零(n) { return Number(n) < 10 ? '0' + Number(n) : String(n); }
function 今日日期(d) {
    d = d || new Date();
    return d.getFullYear() + '-' + 日期补零(d.getMonth() + 1) + '-' + 日期补零(d.getDate());
}
function 随机整数(a, b) {
    const lo = Math.ceil(Math.min(a, b)), hi = Math.floor(Math.max(a, b));
    return lo + Math.floor(Math.random() * Math.max(1, hi - lo + 1));
}
function 中文错误(e) {
    if (!e) return '未知错误';
    const c = e.code || '';
    if (c && 错误码中文[c]) return 错误码中文[c] + '(' + c + ')';
    return String(e.message || c || e);
}

// ---- 可中断 sleep ----
function sleepRaw(ms) { return new Promise(r => setTimeout(r, Math.max(0, Math.round(ms || 0)))); }
async function safeSleep(ms) {
    let left = Math.max(0, Math.round(ms || 0));
    while (left > 0 && 可继续()) {
        const step = left > 500 ? 500 : left;
        await sleepRaw(step);
        left -= step;
    }
    return 可继续();
}
async function 可停睡(ms) { await safeSleep(ms); }
async function 任务间隔() { await 可停睡(运行配置.任务间隔); }
async function 多号间隔() {
    if (!运行配置.多号延迟) return;
    let a = 运行配置.延迟A, b = 运行配置.延迟B;
    if (a > b) { const t = a; a = b; b = t; }
    await 可停睡(随机整数(a * 1000, b * 1000));
}

// ═══════════════ HTTP 层（fetch 优先，axios 回落）═══════════════
var HTTP_实现 = null;
var HTTP_实现名 = '';

async function 初始化HTTP() {
    if (HTTP_实现) return true;
    if (typeof fetch === 'function') {
        HTTP_实现 = async function (method, url, headers, bodyStr) {
            const ctrl = new AbortController();
            const timer = setTimeout(() => { try { ctrl.abort(); } catch (e) {} }, HTTP_TIMEOUT);
            try {
                const opt = { method: String(method || 'GET').toUpperCase(), headers: headers || {}, redirect: 'follow', signal: ctrl.signal };
                if (bodyStr != null) opt.body = bodyStr;
                const res = await fetch(url, opt);
                const text = await res.text();
                const hs = {};
                try { res.headers.forEach(function (v, k) { hs[String(k).toLowerCase()] = String(v); }); } catch (eh) {}
                return { status: Number(res.status || 0), text: String(text == null ? '' : text), headers: hs };
            } finally { clearTimeout(timer); }
        };
        HTTP_实现名 = '全局 fetch (Node ' + process.version + ')';
        return true;
    }
    let axios = null;
    try { axios = require('axios'); } catch (e) { axios = null; }
    if (!axios) return false;
    HTTP_实现 = async function (method, url, headers, bodyStr) {
        const res = await axios.request({
            method: String(method || 'GET').toUpperCase(),
            url: url,
            headers: headers || {},
            data: (bodyStr == null ? undefined : bodyStr),
            timeout: HTTP_TIMEOUT,
            responseType: 'text',
            validateStatus: function () { return true; },
            transformResponse: [function (d) { return d; }],
            maxRedirects: 5
        });
        const hs = {};
        try {
            const raw = res.headers || {};
            for (const k in raw) {
                const v = raw[k];
                hs[String(k).toLowerCase()] = Array.isArray(v) ? String(v.join(', ')) : String(v);
            }
        } catch (eh) {}
        return { status: Number(res.status || 0), text: String(res.data == null ? '' : res.data), headers: hs };
    };
    HTTP_实现名 = 'axios 回落';
    return true;
}

// 单次 HTTP：非 2xx 也返回 body（由 apiOnce 决定语义）
async function 原始请求(method, url, headers, bodyStr) {
    const res = await HTTP_实现(method, url, headers, bodyStr);
    const text = res && res.text != null ? String(res.text) : '';
    let json = null;
    try { json = JSON.parse(text); } catch (e) { json = null; }
    return { status: (res && res.status) || 0, text: text, json: json, headers: (res && res.headers) || {} };
}

// ═══════════════ 协议层 ═══════════════
// 公共头（原 App tt(e)）：Content-Type / X-Device-Id / X-Qingke-App-Code /
// X-Qingke-Session-Version / X-App-Version / Authorization / idempotencyKey(小写 i)
function makeHeaders(token, dev, extra) {
    const h = {
        'Content-Type': 'application/json',
        'X-Device-Id': String(dev || ''),
        'X-Qingke-App-Code': APP_CODE,
        'X-Qingke-Session-Version': SESSION_VER,
        'X-App-Version': APP_VER,
        'User-Agent': UA
    };
    if (extra && extra.idempotencyKey) h['idempotencyKey'] = String(extra.idempotencyKey);
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
}
// 单次请求：成功 = HTTP 2xx 且 code === "SUCCESS"
// 非 2xx 也必须先解析 body —— 4xx 的业务 code/message 不能被吞成 network_error
//   · body 是 JSON 且有 code/message → 业务错误：e.code / e.status / e.httpStatus / e.__raw / e.headers
//   · body 不是 JSON（网关 HTML / 空体）→ network_error，同样挂 e.status / e.__raw / e.headers
async function apiOnce(sess, method, p, body, opt) {
    opt = opt || {};
    const token = (opt.auth === false) ? '' : ((sess && sess.token) || '');
    const dev = (sess && sess.deviceId) || '';
    const headers = makeHeaders(token, dev, opt.idempotencyKey ? { idempotencyKey: opt.idempotencyKey } : null);
    const bodyStr = (body == null) ? null : JSON.stringify(body);
    let res = null;
    try {
        res = await 原始请求(method, BASE_URL + p, headers, bodyStr);
    } catch (eNet) {
        const eN = new Error('网络异常 @' + p + '：' + ((eNet && eNet.message) ? eNet.message : eNet));
        eN.code = 'network_error';
        eN.httpStatus = 0;
        eN.status = 0;
        eN.path = p;
        eN.__raw = '';
        eN.headers = {};
        throw eN;
    }
    const status = res ? (res.status || 0) : 0;
    const resHeaders = (res && res.headers) ? res.headers : {};
    const rawText = (res && res.text != null) ? String(res.text) : '';
    const jAny = (res && res.json) ? res.json : null;
    if (status < 200 || status >= 300) {
        // 先把 body 当信封看一眼：有 code/message 就是业务错误（409 签到冲突就属于这一类）
        let 有信封 = false, bc = '', bm = '';
        if (jAny && typeof jAny === 'object') {
            const c0 = jAny.code, m0 = jAny.message;
            if ((c0 != null && String(c0).length) || (m0 != null && String(m0).length)) {
                有信封 = true;
                bc = (c0 == null) ? ('http_' + status) : String(c0);
                bm = (m0 == null) ? ('HTTP ' + status + ' @' + p) : String(m0);
            }
        }
        let e0 = null;
        if (有信封) {
            e0 = new Error(String(bm || bc));
            e0.code = bc;
        } else {
            e0 = new Error('HTTP ' + (status || 'fail') + ' @' + p);
            e0.code = 'network_error';
        }
        e0.status = status;
        e0.httpStatus = status;
        e0.path = p;
        e0.__raw = rawText.length ? rawText : (jAny ? JSON.stringify(jAny) : '');
        e0.headers = resHeaders;
        if (jAny && typeof jAny === 'object') { e0.traceId = jAny.traceId; e0.body = jAny; }
        throw e0;
    }
    const j = jAny;
    if (!j) {
        const e1 = new Error('响应解析失败 @' + p);
        e1.code = 'response_parse_error';
        e1.status = status;
        e1.httpStatus = status;
        e1.path = p;
        e1.__raw = rawText;
        e1.headers = resHeaders;
        throw e1;
    }
    if (String(j.code) !== 'SUCCESS') {
        const e2 = new Error(String(j.message || 中文错误({ code: j.code, message: j.message })));
        e2.code = j.code;
        e2.status = status;
        e2.httpStatus = status;
        e2.traceId = j.traceId;
        e2.path = p;
        e2.__raw = rawText.length ? rawText : JSON.stringify(j);
        e2.headers = resHeaders;
        throw e2;
    }
    // 原始响应挂在 __raw 上，供 logRaw() 打探针（不改动业务字段）
    try { if (j && typeof j === 'object') j.__raw = (rawText.length ? rawText : JSON.stringify(j)); } catch (e3) {}
    return j;
}
// 重试判定：4xx 一律不重试（408 例外）；429 是限流，重试只会加重；5xx / 真网络异常（无状态码）重试 2 次
function 可重试(e) {
    if (!e) return false;
    let st = Number((e.httpStatus != null) ? e.httpStatus : ((e.status != null) ? e.status : 0));
    if (!isFinite(st)) st = 0;
    if (st === 408) return true;
    if (st === 429) return false;
    if (st >= 400 && st < 500) return false;
    if (st >= 500) return true;
    if (st === 0) return (String(e.code || '') === 'network_error');
    return false;
}
// 网络错误重试 2 次（1.5s / 3s）；4xx 业务错误不重试；429 直接抛给登录链做冷却
async function api(sess, method, p, body, opt) {
    opt = opt || {};
    const 最大重试 = (opt.retry === false) ? 0 : 2;
    let attempt = 0;
    while (true) {
        try {
            return await apiOnce(sess, method, p, body, opt);
        } catch (e) {
            const 状态码 = Number((e.httpStatus != null) ? e.httpStatus : ((e.status != null) ? e.status : 0));
            if (状态码 === 429) {
                log('服务端限流（HTTP 429 / ' + (e.code || '-') + '），不自动重试：' + p, 'warn', sess && sess.tag);
                throw e;
            }
            if (!可重试(e) || attempt >= 最大重试) throw e;
            attempt++;
            log('请求失败，第 ' + attempt + ' 次重试：' + p + '（HTTP ' + (e.httpStatus || 'fail') + ' / ' + (e.code || '-') + '）', 'warn', sess && sess.tag);
            await 可停睡(attempt === 1 ? 1500 : 3000);
        }
    }
}

// ═══════════════ 凭证缓存（每号一个 deviceId + 令牌）═══════════════
function 加载凭证缓存() {
    try {
        if (!fs.existsSync(TOKEN_FILE)) { 凭证缓存 = {}; return; }
        const raw = fs.readFileSync(TOKEN_FILE, 'utf8');
        凭证缓存 = (raw && raw.length > 1) ? (JSON.parse(raw) || {}) : {};
        if (!凭证缓存 || typeof 凭证缓存 !== 'object') 凭证缓存 = {};
    } catch (e) { 凭证缓存 = {}; }
}
function 保存凭证缓存() {
    try {
        fs.mkdirSync(CACHE_DIR, { recursive: true });
        fs.writeFileSync(TOKEN_FILE, JSON.stringify(凭证缓存, null, 2), 'utf8');
    } catch (e) {}
}
function 读凭证(phone) {
    const k = String(phone || '');
    if (!k) return null;
    return 凭证缓存[k] || null;
}
function 写凭证(phone, obj) {
    const k = String(phone || '');
    if (!k) return;
    const cur = 凭证缓存[k] || {};
    凭证缓存[k] = Object.assign(cur, obj || {});
    保存凭证缓存();
}
// 每号固定 deviceId：platform-<ts>-<rand36>（持久化在缓存文件里，不再每次随机）
function 取设备号(phone, cached) {
    if (cached && cached.deviceId) return String(cached.deviceId);
    const v = 'platform-' + Date.now() + '-' + Math.random().toString(36).slice(2);
    写凭证(phone, { deviceId: v });
    return v;
}

// ---- 人脉口径持久化（.cache/qingke_renmai.json）----
function 读人脉口径() {
    if (人脉口径) return 人脉口径;
    let o = null;
    try {
        if (fs.existsSync(RENMAI_FILE)) {
            const raw = fs.readFileSync(RENMAI_FILE, 'utf8');
            if (raw && String(raw).length > 2) o = JSON.parse(String(raw));
        }
    } catch (e) {}
    if (o && typeof o === 'object' && o.action) {
        人脉口径 = o;
        if (o.按次数 === true) 人脉按次数 = true;
        if (o.按次数 === false) 人脉按次数 = false;
        return o;
    }
    人脉口径 = 默认人脉口径;
    if (默认人脉口径.按次数 === true) 人脉按次数 = true;
    return 默认人脉口径;
}
function 写人脉口径(o) {
    if (!o || typeof o !== 'object') return false;
    人脉口径 = o;
    if (o.按次数 === true) 人脉按次数 = true;
    if (o.按次数 === false) 人脉按次数 = false;
    try {
        fs.mkdirSync(CACHE_DIR, { recursive: true });
        fs.writeFileSync(RENMAI_FILE, JSON.stringify(o, null, 2), 'utf8');
    } catch (e) {}
    return true;
}

// ═══════════════ 登录链 ═══════════════
// 本地读 JWT 的 exp：不发请求就能知道缓存里的 Token 还能不能用（返回剩余秒，解析不了返回 -1）
function 令牌剩余秒(token) {
    try {
        const 段 = String(token || '').split('.');
        if (段.length < 2) return -1;
        const s = 段[1].replace(/-/g, '+').replace(/_/g, '/');
        const o = JSON.parse(Buffer.from(s, 'base64').toString('utf8'));
        const exp = Number(o && o.exp);
        if (!isFinite(exp) || exp <= 0) return -1;
        return Math.floor(exp - Date.now() / 1000);
    } catch (e) { return -1; }
}
function 是限流码(code) {
    const c = String(code || '');
    return c === 'user_login_too_many_attempts' || c === 'user_login_ip_rate_limited' ||
        c === 'request_too_many_attempts' || c === 'rate_limited' || c === 'too_many_requests';
}
function 限流等待秒(e) {
    const ra = Number(取响应头(e && e.headers, 'Retry-After'));
    if (isFinite(ra) && ra > 0) return Math.min(3600, Math.round(ra));
    if (String(e && e.code) === 'user_login_ip_rate_limited') return 300;
    return 600;
}
function 记限流(e, phone, tag) {
    const 秒 = 限流等待秒(e);
    const 码 = String((e && e.code) || '');
    // 账号级锁定：只跳过这个账号，别把整批账号都停了
    if (码 === 'user_login_too_many_attempts' && phone) {
        账号冷却[String(phone)] = Date.now() + 秒 * 1000;
        log('账号被临时锁定：登录尝试次数超限，约需等待 ' + Math.max(1, Math.ceil(秒 / 60)) +
            ' 分钟（HTTP 429 / ' + 码 + '）；本次跳过该账号', 'error', tag);
        log('请确认密码是否正确（密码错也会累计尝试次数）', 'warn', tag);
        return;
    }
    限流冷却 = Date.now() + 秒 * 1000;
    限流中止 = true;
    const 原因 = (码 === 'user_login_ip_rate_limited') ? '当前网络（IP）登录次数超限' : '服务端限流';
    限流信息 = 原因 + '，约需等待 ' + Math.max(1, Math.ceil(秒 / 60)) + ' 分钟';
    log('登录被限流：' + 限流信息 + '（HTTP ' + ((e && (e.httpStatus || e.status)) || 429) + ' / ' + (码 || '-') + '）', 'error', tag);
    log('已停止本轮后续登录：现在继续重试只会加重限流，请等待后再跑', 'error', tag);
}
function 检查登录冷却() {
    const 剩 = 限流冷却 - Date.now();
    if (剩 <= 0) return;
    const e = new Error('登录限流冷却中，还需等待 ' + Math.ceil(剩 / 1000) + ' 秒（' + (限流信息 || '服务端限流') + '）');
    e.code = 'login_cooldown'; e.httpStatus = 429; e.status = 429; e.冷却中 = true;
    throw e;
}
function 检查账号冷却(phone) {
    const 剩 = Number(账号冷却[String(phone || '')] || 0) - Date.now();
    if (剩 <= 0) return;
    const e = new Error('该账号登录限流冷却中，还需等待 ' + Math.ceil(剩 / 1000) + ' 秒');
    e.code = 'user_login_too_many_attempts'; e.httpStatus = 429; e.status = 429; e.账号冷却 = true;
    throw e;
}
function 登录成功清冷却() { 限流冷却 = 0; 限流信息 = ''; }
// 登录/刷新最小间隔：多号连续登录时留出间隔，降低同 IP 触发限流的概率
async function 认证闸门() {
    检查登录冷却();
    const 间隔 = Date.now() - 上次认证时间;
    if (间隔 < 运行配置.登录间隔) await 可停睡(运行配置.登录间隔 - 间隔);
    检查登录冷却();
}

// POST /api/user/login  {phone,password}  —— 不带头 Authorization
// → data.accessToken（回落 data.token）/ data.refreshToken / data.expiresIn(秒) / data.userInfo
async function 密码登录(phone, password, deviceId, tag) {
    检查账号冷却(phone);
    await 认证闸门();
    try { return await 密码登录内(phone, password, deviceId, tag); }
    finally { 上次认证时间 = Date.now(); }
}
async function 密码登录内(phone, password, deviceId, tag) {
    检查登录冷却();
    log('开始密码登录…', 'info', tag);
    const sess = { token: '', refreshToken: '', deviceId: deviceId, phone: phone, tag: tag };
    let j;
    try { j = await api(sess, 'POST', '/api/user/login', { phone: phone, password: password }, { auth: false }); }
    catch (eL) {
        if (是限流码(eL.code) || Number(eL.httpStatus) === 429) 记限流(eL, phone, tag);
        throw eL;
    }
    const d = j.data || {};
    const tk = d.accessToken || d.token || '';
    if (!tk) { log('登录返回里没有 accessToken / token', 'error', tag); return null; }
    sess.token = tk;
    sess.refreshToken = d.refreshToken || '';
    const expSec = Number(d.expiresIn || 0);
    sess.expiresAt = expSec > 0 ? (Math.floor(Date.now() / 1000) + expSec) : 0;
    const ui2 = d.userInfo || {};
    log('登录成功' + (ui2.nickname ? '：' + ui2.nickname : '') + '（令牌有效期 ' + (expSec || '?') + 's）', 'success', tag);
    登录成功清冷却();
    写凭证(phone, {
        token: sess.token, refreshToken: sess.refreshToken,
        expiresAt: sess.expiresAt, deviceId: deviceId, phone: phone, 更新时间: Date.now()
    });
    return sess;
}
// POST /api/user/refresh {refreshToken} —— 只认 data.token
async function 刷新令牌(phone, refreshToken, deviceId, tag) {
    检查账号冷却(phone);
    await 认证闸门();
    try { return await 刷新令牌内(phone, refreshToken, deviceId, tag); }
    finally { 上次认证时间 = Date.now(); }
}
async function 刷新令牌内(phone, refreshToken, deviceId, tag) {
    检查登录冷却();
    log('尝试刷新令牌…', 'info', tag);
    const sess = { token: '', refreshToken: refreshToken, deviceId: deviceId, phone: phone, tag: tag };
    let j;
    try { j = await api(sess, 'POST', '/api/user/refresh', { refreshToken: refreshToken }, { auth: false }); }
    catch (eR) {
        if (是限流码(eR.code) || Number(eR.httpStatus) === 429) 记限流(eR, phone, tag);
        throw eR;
    }
    const d = j.data || {};
    const tk = d.token || '';
    if (!tk) { log('刷新返回里没有 token', 'warn', tag); return null; }
    sess.token = tk;
    // 刷新响应一般不带 expiresIn，按 2 小时保守给；真实过期会让服务端 401，随后会重登
    const expSec = Number(d.expiresIn || 7200);
    sess.expiresAt = Math.floor(Date.now() / 1000) + expSec;
    if (d.refreshToken) sess.refreshToken = d.refreshToken;
    log('令牌刷新成功（有效期 ' + expSec + 's）', 'success', tag);
    登录成功清冷却();
    写凭证(phone, {
        token: sess.token, refreshToken: sess.refreshToken,
        expiresAt: sess.expiresAt, deviceId: deviceId, phone: phone, 更新时间: Date.now()
    });
    return sess;
}
// POST /api/user/logout {refreshToken}
async function 登出(sess) {
    if (!sess || !sess.refreshToken) return false;
    try { await api(sess, 'POST', '/api/user/logout', { refreshToken: sess.refreshToken }); return true; } catch (e) { return false; }
}
async function 获取会话(acc, tag) {
    const phone = acc.账号;
    const cached = 读凭证(phone);
    const dev = 取设备号(phone, cached);
    const nowSec = Math.floor(Date.now() / 1000);
    if (cached && cached.token && !运行参数.once) {
        let exp = Number(cached.expiresAt || 0);
        const 剩c = 令牌剩余秒(cached.token);
        if (剩c >= 0) exp = nowSec + 剩c;   // 以 JWT 的 exp 为准，缓存里的 expiresAt 只作兜底
        if (!exp || exp - nowSec > TOKEN_AHEAD) {
            log('复用缓存令牌' + (exp ? '（剩余 ' + (exp - nowSec) + 's）' : ''), 'info', tag);
            return { token: cached.token, refreshToken: cached.refreshToken || '', deviceId: dev, phone: phone, expiresAt: exp, tag: tag };
        }
        log('缓存令牌即将过期（剩余 ' + (exp - nowSec) + 's），先刷新', 'info', tag);
        if (cached.refreshToken) {
            try {
                const rs = await 刷新令牌(phone, cached.refreshToken, dev, tag);
                if (rs) return rs;
            } catch (e) {
                if (是限流码(e.code) || Number(e.httpStatus) === 429) throw e;
                log('刷新失败：' + 中文错误(e), 'warn', tag);
            }
        }
    } else if (运行参数.once && cached && cached.token) {
        log('--once：忽略缓存令牌，强制重新登录', 'info', tag);
    }
    return await 密码登录(phone, acc.密码, dev, tag);
}

// ═══════════════ 任务中心 ═══════════════
// GET /api/user/tasks/center
// data: profile / signIn / tasks{daily,novice,vip} / summary / rules / lastClaim / lastCardReward
async function 拉任务中心(sess, tag, verbose) {
    const j = await api(sess, 'GET', '/api/user/tasks/center', null);
    logRaw(tag, 'tasks/center', j);
    const center = j.data || {};
    if (verbose) {
        const p = center.profile || {};
        const nick = p.nickname || p.nickName || p.name || '';
        const lv = (p.level != null ? p.level : '-');
        const exp = (p.exp != null ? p.exp : (p.experience != null ? p.experience : '-'));
        log('账号资料：Lv.' + lv + ' 经验 ' + exp + (nick ? ' ' + nick : ''), 'info', tag);
    }
    return center;
}

// ═══════════════ 列表解析（容错版）═══════════════
function 元素含字段(v, 字段) {
    if (!v || Object.prototype.toString.call(v) !== '[object Object]') return false;
    for (let i = 0; i < 字段.length; i++) {
        if (v[字段[i]] !== undefined && v[字段[i]] !== null) return true;
    }
    return false;
}
function 深找数组(data, 字段, 深度) {
    if (data == null || 深度 > 6) return null;
    const isArr = Object.prototype.toString.call(data) === '[object Array]';
    if (isArr) {
        if (data.length && 元素含字段(data[0], 字段)) return data;
        return null;
    }
    if (typeof data !== 'object') return null;
    for (const k in data) {
        if (!Object.prototype.hasOwnProperty.call(data, k)) continue;
        let r = null;
        try { r = 深找数组(data[k], 字段, 深度 + 1); } catch (e0) {}
        if (r) return r;
    }
    return null;
}
function 取列表(data, 元素字段) {
    if (!data) return [];
    if (Object.prototype.toString.call(data) === '[object Array]') return data;
    if (元素字段 && 元素字段.length) {
        const hit = 深找数组(data, 元素字段, 0);
        if (hit) return hit;
        try {
            log('列表里找不到元素含 ' + 元素字段.join('/') + ' 的数组，data 顶层字段 = ' + Object.keys(data).join(','), 'warn');
        } catch (e1) {}
        return [];
    }
    const keys = ['items', 'list', 'records', 'rows', 'data'];
    for (let i = 0; i < keys.length; i++) {
        const v = data[keys[i]];
        if (v && Object.prototype.toString.call(v) === '[object Array]') return v;
    }
    return [];
}
// 数值归一：null/undefined/空串/非数字 → null；其余（含数字字符串）→ Number
// dailyLimit === 0 必须保持 0（不能当缺值回落成 8），只有 null 才回落
function 数字或空(v) {
    if (v === null || v === undefined) return null;
    if (typeof v === 'string' && v.trim().length === 0) return null;
    const n = Number(v);
    return isFinite(n) ? n : null;
}
// 把 tasks{daily,novice,vip} 摊平，并标上来源
function 解析任务列表(center) {
    const out = [];
    if (!center) return out;
    const box = center.tasks || {};
    const groups = ['daily', 'novice', 'vip'];
    for (let g = 0; g < groups.length; g++) {
        const arr = box[groups[g]];
        if (!arr || Object.prototype.toString.call(arr) !== '[object Array]') continue;
        for (let i = 0; i < arr.length; i++) {
            const t = arr[i];
            if (!t) continue;
            out.push({
                code: String(t.code || ''),
                taskId: String(t.taskId || ''),
                rewardKey: String(t.rewardKey || ''),
                rewardType: String(t.rewardType || ''),
                rewardQuantity: Number(t.rewardQuantity || 0),
                title: String(t.title || ''),
                desc: String(t.desc || ''),
                baseExp: Number(t.baseExp || 0),
                dailyLimit: 数字或空(t.dailyLimit),
                doneCount: (function () { const n = 数字或空(t.doneCount); return n == null ? 0 : n; })(),
                claimedCount: Number(t.claimedCount || 0),
                claimableCount: Number(t.claimableCount || 0),
                progressPercent: Number(t.progressPercent || 0),
                rewardText: String(t.rewardText || ''),
                totalRewardText: String(t.totalRewardText || ''),
                gainedExp: Number(t.gainedExp || 0),
                status: String(t.status || ''),
                statusText: String(t.statusText || ''),
                buttonText: String(t.buttonText || ''),
                canClaim: t.canClaim === true,
                actionType: String(t.actionType || ''),
                actionUrl: String(t.actionUrl || ''),
                disabled: t.disabled === true,
                来源: groups[g]
            });
        }
    }
    return out;
}
// 任务类型分流：① code 精确匹配 → ② 分组限制（novice/vip 不参与动作）→ ③ 标题关键字兜底 → ④ code 正则兜底
function 匹配任务类型(title, code, 来源) {
    const c = String(code || '').trim();
    if (任务码表[c]) return c;
    if (来源 && 来源 !== 'daily') return null;
    const t = String(title || '');
    if (t.indexOf('浏览人脉') >= 0 || t.indexOf('查看人脉') >= 0) return 'browse_network';
    if (t.indexOf('分享人脉') >= 0) return 'share_network';
    if (t.indexOf('浏览项目') >= 0 || t.indexOf('查看项目') >= 0) return 'browse_project';
    if (t.indexOf('分享项目') >= 0) return 'share_project';
    if (t.indexOf('浏览软件') >= 0 || t.indexOf('查看软件') >= 0) return 'browse_software';
    if (t.indexOf('分享软件') >= 0) return 'share_software';
    if (t.indexOf('点赞软件') >= 0 || t.indexOf('软件点赞') >= 0) return 'like_software';
    if (/vip|pack|membership|invite|profile|real_?name|payout|publish/i.test(c)) return null;
    if (/software.*like|like.*software/i.test(c)) return 'like_software';
    if (/project/i.test(c) && /share/i.test(c)) return 'share_project';
    if (/network|card/i.test(c) && /share/i.test(c)) return 'share_network';
    if (/software|app/i.test(c) && /share/i.test(c)) return 'share_software';
    if (/project|hall/i.test(c)) return 'browse_project';
    if (/software|app/i.test(c)) return 'browse_software';
    if (/network|card/i.test(c)) return 'browse_network';
    return null;
}
function 默认目标(类型) {
    if (类型 === 'browse_network') return 默认浏览人脉;
    if (类型 === 'browse_project') return 默认浏览项目;
    if (类型 === 'browse_software') return 默认浏览软件;
    if (类型 === 'like_software') return 默认点赞;
    return 默认分享;
}
// 缺口 = dailyLimit - doneCount（dailyLimit 只有 null/undefined 才回落默认）
function 算缺口(task) {
    const 类型 = 匹配任务类型(task && task.title, task && task.code, task && task.来源);
    const lim = 数字或空(task && task.dailyLimit);
    let target = (lim == null) ? 默认目标(类型) : lim;
    if (target < 0) target = 0;
    let done = 数字或空(task && task.doneCount);
    if (done == null || done < 0) done = 0;
    return { target: target, done: done, need: Math.max(0, target - done) };
}
function 任务是否跳过(t) {
    if (!t) return true;
    if (t.disabled === true) return true;
    if (跳过状态[String(t.status || '')]) return true;
    return false;
}
function 类型名(类型) {
    const m = {
        browse_network: '浏览人脉', share_network: '分享人脉',
        browse_project: '浏览项目', share_project: '分享项目',
        browse_software: '浏览软件', share_software: '分享软件',
        like_software: '点赞软件'
    };
    return m[类型] || 类型;
}

// ---- 帖子 / 软件列表（拿 id 用）----
// App 的列表接口一律 auth:false（前端 vt(...,{auth:!1})）；先匿名拉，失败再带令牌兜底
async function 拉列表接口(sess, url, tag, 标签) {
    let j = null;
    try {
        j = await api(sess, 'GET', url, null, { auth: false });
    } catch (e0) {
        log(标签 + ' 匿名拉取失败（' + 中文错误(e0) + '），改带令牌重试', 'warn', tag);
        j = await api(sess, 'GET', url, null);
    }
    logRaw(tag, 标签, j);
    return (j && j.data) || {};
}
// 人脉卡片可透传字段白名单（只用于排查侧，不进 click body）
const 人脉透传白名单 = ['viewToken', 'feedToken', 'exposureToken', 'sessionNo', 'cardPosition',
    'cardType', 'cardNo', 'feedId', 'entryId', 'businessCardId', 'contactId', 'targetNo'];
function 透传字段(item) {
    const out = {};
    if (!item || Object.prototype.toString.call(item) !== '[object Object]') return out;
    for (let i = 0; i < 人脉透传白名单.length; i++) {
        const k = 人脉透传白名单[i];
        const v = item[k];
        if (v === undefined || v === null || v === '') continue;
        out[k] = v;
    }
    return out;
}
// 置顶卡：isPinned===1 / pinned===true / topFlag==="1" / badges 含 pinned → 位置不可信，跳过
function 是否置顶卡(item) {
    if (!item || Object.prototype.toString.call(item) !== '[object Object]') return false;
    if (数字或空(item.isPinned) === 1) return true;
    if (item.pinned === true) return true;
    if (String(item.topFlag || '') === '1') return true;
    const b = item.badges;
    if (Object.prototype.toString.call(b) === '[object Array]') {
        for (let i = 0; i < b.length; i++) {
            const v = b[i];
            if (typeof v === 'string') { if (v === 'pinned') return true; }
            else if (v && typeof v === 'object') {
                if (String(v.type || v.code || v.name || v.key || '') === 'pinned') return true;
            }
        }
    } else if (typeof b === 'string' && b.indexOf('pinned') >= 0) return true;
    return false;
}
// 翻页判定：nextCursor / cursor / nextPage 有值，或 hasMore===true，或 total>已取，或 page<pages
function 人脉可翻页(d, page, 已取) {
    const out = { 继续: false, 原因: '', cursor: null };
    if (!d || typeof d !== 'object') return out;
    const 键 = ['nextCursor', 'cursor', 'nextPage'];
    for (let i = 0; i < 键.length; i++) {
        const v = d[键[i]];
        if (v != null && String(v).length) { out.继续 = true; out.原因 = 键[i]; out.cursor = String(v); return out; }
    }
    if (d.hasMore === true) { out.继续 = true; out.原因 = 'hasMore'; return out; }
    const 总数字段 = ['total', 'totalCount', 'totalElements', 'count'];
    for (let t = 0; t < 总数字段.length; t++) {
        const tn = 数字或空(d[总数字段[t]]);
        if (tn != null) {
            if (tn > Number(已取 || 0)) { out.继续 = true; out.原因 = 'total>' + 已取; }
            return out;
        }
    }
    const 页字段 = ['pages', 'totalPages', 'pageCount'];
    for (let p = 0; p < 页字段.length; p++) {
        const pn = 数字或空(d[页字段[p]]);
        if (pn != null) {
            if (Number(page || 1) < pn) { out.继续 = true; out.原因 = 'page<' + pn; }
            return out;
        }
    }
    return out;
}
// 人脉列表：sortMode（all / latest）+ 翻页 + 置顶剔除 + 服务端 cardPosition 优先
async function 取人脉卡片(sess, 需要数, tag, sortMode) {
    const 模式 = String(sortMode || 'all');
    const out = [], seen = {};
    let 置顶跳过 = 0, 序号 = 0, 已拉 = 0;
    let seed = (模式 === 'all')
        ? ('network-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10))
        : '';
    const 最多页 = 8;
    let 换seed = 0;
    const 最多换seed = (模式 === 'all') ? 3 : 0;
    while (可继续()) {
        let page = 1, cursor = '', 本轮新增 = 0;
        while (page <= 最多页 && out.length < 需要数 && 可继续()) {
            let url = '/api/user/network/business-cards?sortMode=' + encodeURIComponent(模式) +
                '&page=' + page + '&pageSize=50';
            if (cursor) url += '&cursor=' + encodeURIComponent(cursor);
            if (seed) url += '&shuffleSeed=' + encodeURIComponent(seed);
            let d = null;
            try { d = await 拉列表接口(sess, url, tag, '人脉列表(' + 模式 + ') p' + page + ' seed' + (换seed + 1)); }
            catch (e) { log('拉人脉列表失败（' + 模式 + ' 第 ' + page + ' 页）：' + 中文错误(e), 'warn', tag); break; }
            // 服务端回传的 shuffleSeed 优先
            if (seed && d && d.shuffleSeed != null && String(d.shuffleSeed).length) seed = String(d.shuffleSeed);
            const items = 取列表(d, ['cardId']);
            if (!items.length) break;
            for (let i = 0; i < items.length; i++) {
                const it = items[i] || {};
                已拉++;
                const cid = (it.cardId != null) ? String(it.cardId) : ((it.id != null) ? String(it.id) : '');
                if (!cid || seen[cid]) continue;
                seen[cid] = 1;
                if (是否置顶卡(it)) {
                    置顶跳过++;
                    log('人脉列表置顶卡跳过：' + cid + '（客户端随机重排，服务端位置不可信）', 'info', tag);
                    continue;
                }
                const 服务端位置 = 数字或空(it.cardPosition);
                const pos = (服务端位置 == null) ? 序号 : 服务端位置;
                序号++;
                const card = {
                    cardId: cid,
                    cardPosition: pos,
                    位置来源: (服务端位置 == null) ? '过滤后下标' : '服务端下发',
                    列表下标: i,
                    全局下标: out.length,
                    sortMode: 模式,
                    shuffleSeed: seed,
                    contentMode: String(it.contentMode || ''),
                    原始: it
                };
                const 透 = 透传字段(it);
                for (const kk in 透) if (透.hasOwnProperty(kk)) card[kk] = 透[kk];
                out.push(card);
                本轮新增++;
                if (out.length >= 需要数) break;
            }
            const nx = 人脉可翻页(d, page, 已拉);
            if (!nx.继续) break;
            cursor = (nx.cursor == null) ? '' : nx.cursor;
            page++;
            await 可停睡(300);
        }
        log('人脉卡池：page=' + page + ' 新增 ' + 本轮新增 + ' 张，累计 ' + out.length + ' 张（seed 第 ' + (换seed + 1) + ' 轮）', 'info', tag);
        if (out.length >= 需要数) break;
        if (换seed >= 最多换seed) break;
        换seed++;
        seed = 'network-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
        await 可停睡(400);
    }
    if (out.length < 需要数) {
        log('人脉卡池只有 ' + out.length + ' 张（服务端就这么点），需 ' + 需要数 + ' 张才能做满；已做 ' + out.length + ' 张', 'warn', tag);
    }
    log('人脉列表（' + 模式 + '）置顶跳过 ' + 置顶跳过 + ' 张；可用卡 ' + out.length + ' 张（pageSize=50，seed 轮 ' + (换seed + 1) + '，位置来源：服务端 cardPosition 优先）', 'info', tag);
    return out;
}
async function 取人脉ID(sess, 需要数, tag) {
    const cards = await 取人脉卡片(sess, 需要数, tag), out = [];
    for (let i = 0; i < cards.length; i++) out.push(cards[i].cardId);
    return out;
}
async function 取项目ID(sess, 需要数, tag) {
    const out = [], seen = {};
    let page = 1;
    while (out.length < 需要数 && page <= 8 && 可继续()) {
        // GET /api/user/hall/projects?page=1&pageSize=20&sortMode=all（真机实测这条能计数，保持不动）
        const url = '/api/user/hall/projects?page=' + page + '&pageSize=20&sortMode=all';
        let j = null;
        try { j = await api(sess, 'GET', url, null); } catch (e) { log('拉项目列表失败（第 ' + page + ' 页）：' + 中文错误(e), 'warn', tag); break; }
        logRaw(tag, '项目列表 p' + page, j);
        const items = 取列表((j && j.data) || {}, ['projectId']);
        if (!items.length) break;
        for (let i = 0; i < items.length; i++) {
            const k = (items[i].projectId != null) ? String(items[i].projectId) : ((items[i].id != null) ? String(items[i].id) : '');
            if (k && !seen[k]) { seen[k] = 1; out.push(k); }
        }
        page++;
        await 可停睡(300);
    }
    return out;
}
// 软件列表：多来源合并去重（sort: latest/hot；deliveryMode: 空/apk/link）
async function 取软件ID(sess, 需要数, tag, 只要未赞) {
    const out = [], seen = {};
    const 排序列表 = ['latest', 'hot'];
    const 上架列表 = ['', 'apk', 'link'];
    for (let si = 0; si < 排序列表.length && out.length < 需要数 && 可继续(); si++) {
        for (let di = 0; di < 上架列表.length && out.length < 需要数 && 可继续(); di++) {
            for (let page = 1; page <= 5 && out.length < 需要数 && 可继续(); page++) {
                const mode = 上架列表[di];
                let url = '/api/user/software/apps?page=' + page + '&pageSize=50&sort=' + encodeURIComponent(排序列表[si]);
                if (mode) url += '&deliveryMode=' + encodeURIComponent(mode);
                let d = null;
                try { d = await 拉列表接口(sess, url, tag, '软件列表 sort=' + 排序列表[si] + ' mode=' + (mode || '全部') + ' p' + page); }
                catch (e) { log('拉软件列表失败（sort=' + 排序列表[si] + ' mode=' + (mode || '全部') + ' 第 ' + page + ' 页）：' + 中文错误(e), 'warn', tag); break; }
                const items = 取列表(d, ['softwareNo']);
                if (!items.length) break;
                for (let i = 0; i < items.length; i++) {
                    const it = items[i] || {};
                    const no = (it.softwareNo != null) ? String(it.softwareNo) : ((it.id != null) ? String(it.id) : '');
                    if (!no || seen[no]) continue;
                    seen[no] = 1;
                    if (只要未赞 && Number(it.likedToday || 0) === 1) continue;
                    out.push(no);
                    if (out.length >= 需要数) break;
                }
                await 可停睡(300);
            }
        }
    }
    return out;
}
async function 按类型取ID(sess, 类型, 需要数, tag) {
    if (类型 === 'browse_network' || 类型 === 'share_network') return await 取人脉ID(sess, 需要数, tag);
    if (类型 === 'browse_project' || 类型 === 'share_project') return await 取项目ID(sess, 需要数, tag);
    if (类型 === 'browse_software' || 类型 === 'share_software') return await 取软件ID(sess, 需要数, tag, false);
    if (类型 === 'like_software') return await 取软件ID(sess, 需要数, tag, true);
    return [];
}

// ═══════════════ 签到 ═══════════════
// POST /api/user/tasks/checkin  body 依次降级：
//   b1 {clientDate:"YYYY-MM-DD", idempotencyKey}  ← App 原始写法
//   b2 {idempotencyKey}                           ← 不带 clientDate
//   b3 {}                                         ← 空 body
function 签到疑似已签(code, message) {
    const s = (String(code || '') + ' ' + String(message || '')).toLowerCase();
    return /already|已签|重复|duplicate|conflict/.test(s);
}
// 对时：本地日期 vs 服务端响应头 Date
async function 签到对时(sess, tag) {
    const 本地 = 今日日期();
    let 本地串 = '';
    try { 本地串 = String(new Date()); } catch (e0) { 本地串 = '(取本地时间失败)'; }
    let 服务端 = '', 说明 = '';
    try {
        const h = makeHeaders((sess && sess.token) || '', (sess && sess.deviceId) || '', null);
        const res = await 原始请求('GET', BASE_URL + '/api/public/app-config', h, null);
        服务端 = 取响应头(res && res.headers, 'Date');
        if (!服务端) 说明 = 'HTTP ' + ((res && res.status) || '?') + ' 但响应头里没有 Date';
    } catch (e1) {
        说明 = '取 app-config 失败：' + 中文错误(e1);
    }
    log('签到对时：本地日期 ' + 本地 + '（' + 本地串 + '）；服务端 Date=' + (服务端 ? 服务端 : '(未取到)') +
        (说明 ? '（' + 说明 + '）' : ''), 'info', tag);
    return { 本地: 本地, 服务端: 服务端 };
}
async function 提交签到(sess, tag) {
    const clientDate = 今日日期();
    const 尝试表 = [
        { 名: 'b1', body: function () { return { clientDate: clientDate, idempotencyKey: ht('checkin-submit') }; } },
        { 名: 'b2', body: function () { return { idempotencyKey: ht('checkin-submit') }; } },
        { 名: 'b3', body: function () { return {}; } }
    ];
    let 最后错 = null, 见过409 = false, 对时打过 = false;
    for (let i = 0; i < 尝试表.length; i++) {
        const it = 尝试表[i];
        const bd = it.body();
        try {
            const j = await api(sess, 'POST', '/api/user/tasks/checkin', bd);
            const d = j.data || {};
            const 发卡 = d.rewardIssued === true;
            本次签到.ok = true; 本次签到.already = false; 本次签到.date = clientDate;
            log('签到尝试 ' + it.名 + ' → HTTP 200 / code=SUCCESS / msg=ok', 'success', tag);
            logRaw强制(tag, '签到(' + it.名 + ')', j, 1200);
            log('签到成功（' + clientDate + '，' + it.名 + '）' + (发卡 ? '，已发发布卡' : ''), 'success', tag);
            return { ok: true, data: d, 尝试: it.名 };
        } catch (e) {
            最后错 = e;
            let st = Number((e && e.httpStatus != null) ? e.httpStatus : ((e && e.status) || 0));
            if (!isFinite(st)) st = 0;
            const code = String((e && e.code) || '');
            const msg = String((e && e.message) || '');
            if (st === 409) 见过409 = true;
            log('签到尝试 ' + it.名 + ' → HTTP ' + (st || 'fail') + ' / code=' + (code || '-') + ' / msg=' + (msg || '-'), 'warn', tag);
            if (st === 409 && !对时打过) {
                对时打过 = true;
                try { await 签到对时(sess, tag); } catch (eD) {}
            }
            const raw = (e && e.__raw != null) ? String(e.__raw) : '';
            if (raw.length) logRaw强制(tag, '签到', { __raw: raw }, 1200);
            else logRaw强制(tag, '签到', { __raw: '(空响应体，HTTP ' + (st || '?') + ')' }, 1200);
            if (签到疑似已签(code, msg)) {
                本次签到.ok = true; 本次签到.already = true; 本次签到.date = clientDate;
                log('签到判为已签（' + it.名 + ' / ' + (code || msg) + '）：今日已签到（' + clientDate + '）', 'info', tag);
                return { ok: true, already: true, 尝试: it.名, err: e };
            }
        }
    }
    if (见过409) log('签到失败（已打本地/服务端日期对照，见上面的「签到对时」行）', 'error', tag);
    else log('签到失败：' + 中文错误(最后错), 'error', tag);
    return { ok: false, err: 最后错 };
}
// POST /api/user/tasks/signin/first-day-card {idempotencyKey}
async function 领首日卡(sess, tag) {
    try {
        const j = await api(sess, 'POST', '/api/user/tasks/signin/first-day-card', { idempotencyKey: ht('task-first-day-card') });
        const d = j.data || {};
        log('首日卡领取成功' + (d.quantity || d.rewardQuantity ? '：×' + (d.quantity || d.rewardQuantity) : ''), 'success', tag);
        return true;
    } catch (e) {
        log('首日卡领取失败：' + 中文错误(e), 'warn', tag);
        return false;
    }
}
async function 做签到(sess, center, tag) {
    const sign = (center && center.signIn) || {};
    log('签到状态：今日' + (sign.todayCheckedIn ? '已签' : '未签') +
        '，连续 ' + (sign.cumulativeDays != null ? sign.cumulativeDays : 0) + ' 天' +
        '，本周期 ' + (sign.cycleProgress != null ? sign.cycleProgress : '-') + '/' + (sign.cycleDays != null ? sign.cycleDays : '-'), 'info', tag);
    if (sign.todaySignInExp != null) log('今日签到经验：' + sign.todaySignInExp, 'info', tag);
    if (!sign.todayCheckedIn) {
        await 提交签到(sess, tag);
        await 可停睡(800);
    } else {
        log('跳过提交，直接检查首日卡', 'info', tag);
    }
    if (sign.canClaimFirstDayCard === true) {
        await 领首日卡(sess, tag);
        await 可停睡(600);
    }
}

// ═══════════════ 浏览 ═══════════════
// 人脉曝光：body 只 3 个字段 sortMode / cardPosition / exposureToken
async function 曝光人脉一张(sess, cardId, opt) {
    opt = opt || {};
    const sortMode = String(opt.sortMode || 'all');
    const pos = (opt.cardPosition == null) ? 0 : Number(opt.cardPosition);
    const body = {
        sortMode: sortMode,
        cardPosition: (isFinite(pos) ? pos : 0),
        exposureToken: ht('network-card-exposure')
    };
    const j = await api(sess, 'POST', '/api/user/network/business-cards/' + encodeURIComponent(cardId) + '/exposure', body);
    logRaw(sess && sess.tag, '人脉曝光 ' + cardId, j);
    return j;
}
// clickAction 判定：contentMode === "link" → link_jump，否则 image_popup
function 人脉点击动作(contentMode) {
    return (String(contentMode == null ? '' : contentMode) === 'link') ? 'link_jump' : 'image_popup';
}
async function 浏览一条(sess, 类型, id, opt) {
    opt = opt || {};
    if (类型 === 'browse_network') {
        // click body 只有 4 个字段：sortMode / cardPosition / clickAction / idempotencyKey
        const sortMode = String(opt.sortMode || 'all');
        const pos = (opt.cardPosition == null) ? 0 : Number(opt.cardPosition);
        const 动作 = String(opt.clickAction || 人脉点击动作(opt.contentMode));
        const body = {
            sortMode: sortMode,
            cardPosition: (isFinite(pos) ? pos : 0),
            clickAction: 动作,
            idempotencyKey: opt.idempotencyKey || ht('network-card-click')
        };
        const j = await api(sess, 'POST', '/api/user/network/business-cards/' + encodeURIComponent(id) + '/click', body);
        logRaw(sess && sess.tag, '人脉点击 ' + id, j, opt.raw限 || 0);
        const 记了 = !!(j && j.data && j.data.viewRecorded === true);
        return { data: (j && j.data) || null, viewRecorded: 记了, 请求体: body, 响应: j };
    }
    if (类型 === 'browse_project') {
        const j = await api(sess, 'POST', '/api/user/hall/projects/' + encodeURIComponent(id) + '/detail-view',
            { sourceSortMode: 'all', viewToken: ht('hall-detail-view') });
        return j.data;
    }
    // GET /api/user/software/apps/{softwareNo}?viewToken=...
    const j2 = await api(sess, 'GET', '/api/user/software/apps/' + encodeURIComponent(id) +
        '?viewToken=' + encodeURIComponent(ht('software-view')), null);
    return j2.data;
}
// ---- 分享 ----
function buildShareBody(sourceScene, targetNo, idemKey) {
    const actionCode = 分享场景映射[String(sourceScene)];
    if (!actionCode) throw new Error('未知分享场景: ' + sourceScene);
    return {
        actionCode: actionCode,
        sourceScene: String(sourceScene),
        targetNo: String(targetNo == null ? '' : targetNo),
        idempotencyKey: idemKey || ht('task-action-' + actionCode)
    };
}
// ---- 点赞 ----
async function 点赞一条(sess, softwareNo) {
    const j = await api(sess, 'POST', '/api/user/software/apps/' + encodeURIComponent(softwareNo) + '/like',
        { idempotencyKey: ht('software-like') });
    return j.data;
}
// ---- 领奖 ----
// rewardType === "publish_card" → /vip-membership-publish-card/claim {rewardKey}
// 其它 → /experience/claim {taskCode: taskId || code}
async function 领一个(sess, task, tag) {
    if (!task || task.canClaim !== true) return false;
    if (task.rewardType === 'publish_card') {
        if (!task.rewardKey) { log('任务【' + task.title + '】缺 rewardKey，跳过', 'warn', tag); return false; }
        const j1 = await api(sess, 'POST', '/api/user/tasks/vip-membership-publish-card/claim',
            { rewardKey: task.rewardKey, idempotencyKey: ht('vip-membership-publish-card') });
        let q = 0;
        try { q = (j1.data && j1.data.lastCardReward && Number(j1.data.lastCardReward.quantity || 0)) || 0; } catch (e1) {}
        log('领取【' + task.title + '】发布卡 ×' + q, 'success', tag);
        return true;
    }
    const taskCode = task.taskId || task.code;
    if (!taskCode) { log('任务【' + task.title + '】缺 taskId/code，跳过', 'warn', tag); return false; }
    const j2 = await api(sess, 'POST', '/api/user/tasks/experience/claim',
        { taskCode: taskCode, idempotencyKey: ht('task-claim-' + taskCode) });
    let gained = 0;
    try { gained = (j2.data && j2.data.lastClaim && Number(j2.data.lastClaim.gainedExp || 0)) || 0; } catch (e2) {}
    log('领取【' + task.title + '】经验 +' + gained, 'success', tag);
    return true;
}
async function 领全部奖励(sess, tag) {
    const center = await 拉任务中心(sess, tag, false);
    const tasks = 解析任务列表(center);
    let 已领 = 0, 尝试 = 0;
    for (let i = 0; i < tasks.length && 可继续(); i++) {
        if (tasks[i].canClaim !== true) continue;
        尝试++;
        try { if (await 领一个(sess, tasks[i], tag)) 已领++; } catch (e) { log('领取【' + tasks[i].title + '】失败：' + 中文错误(e), 'warn', tag); }
        await 任务间隔();
    }
    if (尝试 === 0) log('当前没有可领取的奖励', 'info', tag);
    else log('领奖完成：成功 ' + 已领 + '/' + 尝试, 已领 ? 'success' : 'warn', tag);
}

// ═══════════════ 打印 ═══════════════
function 限次文案(v) { return (v == null) ? '-' : String(v); }
function 打印任务快照(center, tag) {
    const tasks = 解析任务列表(center);
    if (!tasks.length) { log('任务中心里没有任务列表', 'warn', tag); return; }
    log('任务快照 ' + tasks.length + ' 个（code / 标题 / 进度 / 状态）：', 'info', tag);
    for (let i = 0; i < tasks.length; i++) {
        const t = tasks[i];
        const ty = 匹配任务类型(t.title, t.code, t.来源) || '未识别';
        log('  · [' + t.来源 + '][' + ty + '] ' + t.title + '  ' + t.doneCount + '/' + 限次文案(t.dailyLimit) +
            '  status=' + t.status + (t.canClaim ? ' 可领' : '') +
            '  code=' + (t.code || '-') + (t.rewardText ? '  奖=' + t.rewardText : ''), 'info', tag);
    }
}
// 签到是否已签：本次提交成功也算（signIn.todayCheckedIn 是延迟字段）
function 签到已签(center) {
    const sign = (center && center.signIn) || {};
    return (本次签到.ok === true) || sign.todayCheckedIn === true;
}
function 签到文案(center) {
    const sign = (center && center.signIn) || {};
    let 连续 = 数字或空(sign.cumulativeDays);
    if (连续 == null) 连续 = 0;
    let 周期天 = 数字或空(sign.cycleDays);
    if (周期天 == null) 周期天 = 7;
    let 周期 = 数字或空(sign.cycleProgress);
    if (周期 == null) 周期 = 0;
    const 已签 = 签到已签(center);
    let extra = '';
    if (本次签到.ok === true && sign.todayCheckedIn !== true) extra = ' · 本次已提交';
    if (sign.canClaimFirstDayCard === true) extra += ' · 首日卡可领';
    return '签到：' + (已签 ? '已签' : '未签') + '（连续 ' + 连续 + ' 天，本周期 ' + 周期 + '/' + 周期天 + '）' + extra;
}
// 新手/VIP 不逐个刷屏，各汇总一行
function 输出非每日汇总(novice, vip, tag) {
    if (novice && novice.length) {
        let 未做 = 0;
        for (let i = 0; i < novice.length; i++) {
            const t = novice[i];
            const lim = 数字或空(t.dailyLimit);
            let done = 数字或空(t.doneCount);
            if (done == null) done = 0;
            const 完成 = (String(t.status) === 'claimed') || (String(t.status) === 'claimable') ||
                (lim != null && lim > 0 && done >= lim);
            if (!完成) 未做++;
        }
        log('── 新手任务 ── ' + novice.length + ' 个，其中 ' + 未做 + ' 个未做（需在 App 内完成：完善资料 / 实名 / 绑定收款 / 发帖）', 'info', tag);
    }
    if (vip && vip.length) {
        let 未解锁 = 0;
        for (let k = 0; k < vip.length; k++) {
            const s = String(vip[k].status || '');
            if (s === 'locked' || s === 'disabled' || vip[k].disabled === true) 未解锁++;
        }
        log('── 会员任务 ── ' + vip.length + ' 个，其中 ' + 未解锁 + ' 个未解锁（需 VIP，协议里不做）', 'info', tag);
    }
}
function 分任务组(tasks) {
    const r = { daily: [], novice: [], vip: [] };
    for (let i = 0; i < tasks.length; i++) {
        const s = String(tasks[i].来源 || 'daily');
        if (!r[s]) r[s] = [];
        r[s].push(tasks[i]);
    }
    return r;
}
function 输出进度(center, tag) {
    const tasks = 解析任务列表(center);
    const g = 分任务组(tasks);
    log('── 每日任务（' + g.daily.length + ' 个）──', 'info', tag);
    for (let i = 0; i < g.daily.length; i++) {
        const t = g.daily[i];
        const gap = 算缺口(t);
        log('  ' + (gap.need === 0 ? '✅' : '⬜') + ' ' + t.title + '  ' + gap.done + '/' + gap.target +
            (gap.need > 0 ? '（还差 ' + gap.need + '）' : '') +
            '  ' + (t.statusText || t.status || '') + (t.canClaim ? '  → 可领取' : '') +
            '  code=' + (t.code || '-'), 'info', tag);
    }
    输出非每日汇总(g.novice, g.vip, tag);
    log('── 签到 ── ' + 签到文案(center), 'info', tag);
    const sum = center.summary || {};
    const 摘要 = [];
    for (const k in sum) if (sum.hasOwnProperty(k)) 摘要.push(k + '=' + sum[k]);
    if (摘要.length) log('── 汇总 ── ' + 摘要.join(' '), 'info', tag);
    if (center.lastClaim) log('── 上次领取 ── ' + JSON.stringify(center.lastClaim), 'info', tag);
    return g;
}
// 把 center 的结果记进本号统计（汇总块用）
function 记任务统计(center) {
    try {
        const tasks = 解析任务列表(center);
        const g = 分任务组(tasks);
        let 完成 = 0;
        for (let i = 0; i < g.daily.length; i++) if (算缺口(g.daily[i]).need === 0) 完成++;
        本号统计.任务完成 = 完成;
        本号统计.任务总数 = g.daily.length;
        本号统计.签到 = 签到文案(center);
    } catch (e) {}
}
async function 输出战绩(sess, tag) {
    log('════ 今日战绩 ════', 'success', tag);
    const center = await 拉任务中心(sess, tag, false);
    const tasks = 解析任务列表(center);
    const g = 分任务组(tasks);
    let 完成 = 0, 可领 = 0;
    for (let i = 0; i < g.daily.length; i++) {
        const t = g.daily[i];
        const gap = 算缺口(t);
        if (gap.need === 0) 完成++;
        if (t.canClaim) 可领++;
        log('  ' + (gap.need === 0 ? '✅' : '⬜') + ' ' + t.title + '  ' + gap.done + '/' + gap.target +
            (gap.need > 0 ? '（还差 ' + gap.need + '）' : '') + (t.canClaim ? ' 可领' : '') +
            '  ' + (t.statusText || t.status || ''), 'info', tag);
    }
    输出非每日汇总(g.novice, g.vip, tag);
    log('  · ' + 签到文案(center), 'info', tag);
    log('  · 每日任务完成 ' + 完成 + '/' + g.daily.length + ' 个' +
        (可领 > 0 ? '，仍有 ' + 可领 + ' 个可领（再跑一次或手动领）' : ''), 'success', tag);
    本号统计.任务完成 = 完成;
    本号统计.任务总数 = g.daily.length;
    本号统计.签到 = 签到文案(center);
    // 全自动跑完大厅红包 → 战绩里多打一行红包结果
    const 红包战绩 = 上次红包结果;
    if (红包战绩) {
        const 红包个数 = Number(红包战绩.成功 || 0);
        const 红包失败 = Number(红包战绩.失败 || 0);
        const 红包金额 = Number(红包战绩.合计 || 0);
        if (红包个数 > 0) log('  · 大厅红包：领到 ' + 红包个数 + ' 个，合计 ' + 红包金额 + ' 元', 'success', tag);
        if (红包失败 > 0) log('  · 大厅红包：失败 ' + 红包失败 + ' 个（详情见日志）', 'warn', tag);
        if (红包个数 === 0 && 红包失败 === 0) log('  · 大厅红包：没有可领的红包', 'info', tag);
    }
}

// ═══════════════ 人脉口径（内置默认 contact_popup + 自动探测 + 持久化）═══════════════
function 人脉口径描述(口径) {
    if (!口径) return '默认（clickAction 按 contentMode、位置 = 服务端 cardPosition、sortMode = 卡片自身）';
    return String(口径.标签 || '?') + '（动作=' + String(口径.action || '?') +
        '，位置偏移=' + String(口径.offset == null ? 0 : 口径.offset) +
        '，位置来源=' + (String(口径.mode || 'server') === 'index' ? '列表下标' : '服务端位置') +
        '，sortMode=' + String(口径.sortMode || 'all') + '）';
}
function 是否内置默认口径(口径) {
    return !!口径 && String(口径.来源 || '') === '内置默认';
}
// 位置 / 动作 / 排序 都从口径取；口径为空 → 回落到卡片自身
function 人脉位置(card, 口径) {
    let pos;
    if (口径 && String(口径.mode || '') === 'index') {
        pos = Number((card && card.全局下标 != null) ? card.全局下标 : ((card && card.列表下标 != null) ? card.列表下标 : 0));
    } else {
        pos = Number((card && card.cardPosition != null) ? card.cardPosition : 0) +
            ((口径 && 口径.offset != null) ? Number(口径.offset) : 0);
    }
    if (!isFinite(pos) || pos < 0) pos = 0;
    return pos;
}
function 人脉动作(card, 口径) {
    if (口径 && 口径.action) return String(口径.action);
    return 人脉点击动作(card && card.contentMode);
}
function 人脉排序(card, 口径) {
    if (口径 && 口径.sortMode) return String(口径.sortMode);
    return String((card && card.sortMode) || 'all');
}
// 按口径打一张卡：曝光总是先发（App 顺序：列表渲染曝光 → 点卡片 click）
// 口径 action === "exposure" 时只发曝光不发 click
async function 打人脉一张(sess, tag, card, 口径) {
    const pos = 人脉位置(card, 口径);
    const act = 人脉动作(card, 口径);
    const 排序 = 人脉排序(card, 口径);
    const 只曝光 = (act === 'exposure');
    try { await 曝光人脉一张(sess, card.cardId, { sortMode: 排序, cardPosition: pos }); }
    catch (e1) { log('人脉曝光失败（' + card.cardId + '）：' + 中文错误(e1), 'warn', tag); }
    const 结果 = { cardId: card.cardId, 动作: act, 位置: pos, 排序: 排序, 只曝光: 只曝光, viewRecorded: false, data: null, 响应: null };
    if (只曝光) return 结果;
    const r = await 浏览一条(sess, 'browse_network', card.cardId, {
        sortMode: 排序, cardPosition: pos, contentMode: card.contentMode, clickAction: act, raw限: 1200
    });
    结果.viewRecorded = !!(r && r.viewRecorded === true);
    结果.data = (r && r.data) || null;
    结果.响应 = (r && r.响应) || null;
    return 结果;
}
// 探测一步：打前读 doneCount → 执行 → 睡 1200 → 打后读 doneCount → 一行定格日志
async function 打探测(sess, tag, 号, 描述, fn) {
    let 前 = null, 后 = null, 错 = '', 返 = null;
    try { 前 = await 读人脉进度(sess, tag); }
    catch (e0) { 错 = '读基线失败：' + 中文错误(e0); }
    try { 返 = await fn(); }
    catch (e1) { 错 = (错 ? 错 + '；' : '') + '请求异常：' + 中文错误(e1); }
    await 可停睡(1200);
    try { 后 = await 读人脉进度(sess, tag); }
    catch (e2) { 错 = (错 ? 错 + '；' : '') + '复读失败：' + 中文错误(e2); }
    const x = 前 ? 前.done : null;
    const y = 后 ? 后.done : null;
    const z = (x == null || y == null) ? null : (y - x);
    const 有效 = (z != null && z > 0);
    const vr = (返 && typeof 返 === 'object' && 返.viewRecorded !== undefined) ? (返.viewRecorded === true) : null;
    log('探测 ' + 号 + ' [' + 描述 + '] → 打前 ' + (x == null ? '?' : x) +
        ' / 打后 ' + (y == null ? '?' : y) +
        ' / 增量 ' + (z == null ? '?' : (z >= 0 ? '+' + z : String(z))) +
        ' ← ' + (有效 ? '有效' : '无效') +
        (vr == null ? '' : '（viewRecorded=' + vr + '）') + (错 ? '（' + 错 + '）' : ''),
        有效 ? 'success' : 'warn', tag);
    return { 号: 号, 描述: 描述, 前: x, 后: y, 增量: z, 有效: 有效, viewRecorded: vr, 错: 错 };
}
// 重复同卡验证：判断服务端是按「次数」计数还是按「卡」去重（口径已带标记时只跑 1 次）
async function 重复验证同卡(sess, tag, card, 口径) {
    let 已知 = null;
    if (口径 && 口径.按次数 !== undefined && 口径.按次数 !== null) 已知 = 口径.按次数;
    else if (人脉按次数 !== null && 人脉按次数 !== undefined) 已知 = 人脉按次数;
    const 次数 = (已知 === true || 已知 === false) ? 1 : 3;
    let 增 = 0;
    const 明细 = [];
    if (次数 === 1) {
        log('重复验证：口径已带「按次数=' + 已知 + '」标记（真机已验证），只跑 1 次复核省请求（口径 ' +
            String((口径 && 口径.标签) || '默认') + '）', 'info', tag);
    } else {
        log('重复验证开始：同一张卡 ' + card.cardId + ' 连打 ' + 次数 + ' 次（口径 ' +
            String((口径 && 口径.标签) || '默认') + '，每次全新 idempotencyKey）', 'warn', tag);
    }
    for (let k = 1; k <= 次数 && 可继续(); k++) {
        let 前 = null, 后 = null, 错 = '';
        try { 前 = await 读人脉进度(sess, tag); } catch (e0) { 错 = 中文错误(e0); }
        try { await 打人脉一张(sess, tag, card, 口径); }
        catch (e1) { 错 = (错 ? 错 + '；' : '') + 中文错误(e1); }
        await 可停睡(1200);
        try { 后 = await 读人脉进度(sess, tag); } catch (e2) { 错 = (错 ? 错 + '；' : '') + 中文错误(e2); }
        const x = (前 == null) ? null : 前.done;
        const y = (后 == null) ? null : 后.done;
        const z = (x == null || y == null) ? null : (y - x);
        if (z != null && z > 0) 增 += z;
        明细.push(z);
        log('重复验证 第' + k + '次 → doneCount: ' + (x == null ? '?' : x) + ' → ' + (y == null ? '?' : y) +
            '（' + (z == null ? '?' : (z >= 0 ? '+' + z : String(z))) + '）' + (错 ? '（' + 错 + '）' : ''),
            (z != null && z > 0) ? 'success' : 'warn', tag);
    }
    const 按次数 = (已知 === true || 已知 === false) ? 已知 : (增 > 1);
    人脉按次数 = 按次数;
    if (次数 === 1) {
        log('重复验证结论：沿用口径标记「按次数=' + 已知 + '」，本次 1 次增量 ' +
            (增 > 0 ? '+' + 增 : '0') + '（省 2 次请求，不改标记）', 增 > 0 ? 'success' : 'warn', tag);
    } else if (增 === 0) {
        log('重复验证结论：3 次全不涨 —— 该口径本身不计数（或服务端按卡+每日上限），不能靠重复补满', 'error', tag);
    } else if (按次数) {
        log('重复验证结论：3 次涨 ' + 增 + ' → 服务端按「次数」计数（同卡重复有效），卡池不足时可重复打补满', 'success', tag);
    } else {
        log('重复验证结论：3 次只涨 ' + 增 + ' → 服务端按「卡」去重（同卡重复无效），必须凑够不同 cardId', 'warn', tag);
    }
    return { 增量: 增, 明细: 明细, 按次数: 按次数, 次数: 次数 };
}
// 自动探测 D1..D8（上限 8 条，每条之间 1200ms）；命中即锁定 → 写盘 + 按锁定口径补跑
async function 人脉口径探测(sess, tag, opt) {
    opt = opt || {};
    const 已试 = opt.已试 || {};
    const 需要数 = Number(opt.需要数 || 0);
    let 卡池 = opt.卡池 || [];
    let 成功 = 0, 未记录 = 0, 命中 = null, 锁 = null;
    const 表 = [];
    const 原探针 = 导出原始.on;
    导出原始.on = true;   // 探测必须打 RAW，否则回传的日志没有判据
    try {
        // 探测卡：优先用主轮没打过的卡；全打过了就复用第一张（idempotencyKey 每次全新，不会 replay）
        let 探卡 = null;
        for (let i = 0; i < 卡池.length; i++) {
            if (!已试[卡池[i].cardId]) { 探卡 = 卡池[i]; break; }
        }
        if (!探卡 && 卡池.length) 探卡 = 卡池[0];
        if (!探卡) {
            let 新卡 = [];
            try { 新卡 = await 取人脉卡片(sess, 6, tag, 'all'); }
            catch (e0) { log('人脉口径探测：重拉人脉列表失败（' + 中文错误(e0) + '）', 'warn', tag); }
            for (let j = 0; j < 新卡.length; j++) {
                if (!已试[新卡[j].cardId]) { 探卡 = 新卡[j]; break; }
            }
            if (!探卡 && 新卡.length) 探卡 = 新卡[0];
            卡池 = 卡池.concat(新卡);
        }
        if (!探卡) {
            log('人脉口径探测：一张卡都拿不到，放弃探测', 'warn', tag);
            return { 口径: null, 命中: null, 成功: 0, 未记录: 0, 表: [] };
        }
        let latest卡 = null;   // D6 专用：懒加载
        let P = Number(探卡.cardPosition);
        if (!isFinite(P) || P < 0) P = 0;
        const S = String(探卡.sortMode || 'all');
        log('人脉口径探测开始：探测卡 ' + 探卡.cardId + '（cardPosition=' + P + '，sortMode=' + S +
            '），最多 ' + 人脉探测上限 + ' 条，每条之间 1200ms', 'warn', tag);
        const 发点击 = function (卡, 排序, 位置, 动作) {
            return 浏览一条(sess, 'browse_network', 卡.cardId, {
                sortMode: 排序, cardPosition: 位置, contentMode: 卡.contentMode, clickAction: 动作, raw限: 1200
            });
        };
        // D1 只在「主轮真的打过 image_popup」时才算对照基线跳过
        const 主轮动作 = String((opt.主轮口径 && opt.主轮口径.action) || '');
        const D1跳过 = (主轮动作 === 'image_popup');
        const 步骤 = [
            { 号: 'D1', 描述: 'image_popup, pos=' + P + (D1跳过 ? '（主轮已打）' : '（对照基线）'), 跳过: D1跳过,
                口径: { action: 'image_popup', offset: 0, sortMode: S, mode: 'server' },
                fn: function () { return 发点击(探卡, S, P, 'image_popup'); } },
            { 号: 'D2', 描述: 'image_popup, pos+1=' + (P + 1),
                口径: { action: 'image_popup', offset: 1, sortMode: S, mode: 'server' },
                fn: function () { return 发点击(探卡, S, P + 1, 'image_popup'); } },
            { 号: 'D3', 描述: 'link_jump, pos=' + P,
                口径: { action: 'link_jump', offset: 0, sortMode: S, mode: 'server' },
                fn: function () { return 发点击(探卡, S, P, 'link_jump'); } },
            { 号: 'D4', 描述: 'detail_view, pos=' + P,
                口径: { action: 'detail_view', offset: 0, sortMode: S, mode: 'server' },
                fn: function () { return 发点击(探卡, S, P, 'detail_view'); } },
            { 号: 'D5', 描述: '只发 exposure（不发 click）',
                口径: { action: 'exposure', offset: 0, sortMode: S, mode: 'server' },
                fn: function () { return 曝光人脉一张(sess, 探卡.cardId, { sortMode: S, cardPosition: P }); } },
            { 号: 'D6', 描述: 'image_popup, pos=0, sortMode=latest',
                口径: { action: 'image_popup', offset: 0, sortMode: 'latest', mode: 'index' },
                fn: async function () {
                    if (!latest卡) {
                        try {
                            const ls = await 取人脉卡片(sess, 3, tag, 'latest');
                            if (ls && ls.length) latest卡 = ls[0];
                        } catch (eL) { log('探测 D6 拉 latest 列表失败：' + 中文错误(eL), 'warn', tag); }
                    }
                    if (!latest卡) { log('探测 D6 没有 latest 口径的卡，本条跳过', 'warn', tag); return null; }
                    log('探测 D6 用 latest 卡：' + latest卡.cardId + '（cardPosition=' + latest卡.cardPosition + '）', 'info', tag);
                    return await 发点击(latest卡, 'latest', 0, 'image_popup');
                } },
            { 号: 'D7', 描述: 'contact_popup, pos=' + P,
                口径: { action: 'contact_popup', offset: 0, sortMode: S, mode: 'server' },
                fn: function () { return 发点击(探卡, S, P, 'contact_popup'); } },
            { 号: 'D8', 描述: 'contact, pos=' + P,
                口径: { action: 'contact', offset: 0, sortMode: S, mode: 'server' },
                fn: function () { return 发点击(探卡, S, P, 'contact'); } }
        ];
        let 已探 = 0;
        for (let k2 = 0; k2 < 步骤.length && 已探 < 人脉探测上限 && 可继续(); k2++) {
            const st = 步骤[k2];
            if (st.跳过) {
                log('探测 ' + st.号 + ' [' + st.描述 + '] → 跳过重发（主轮已按这组参数打过，作为对照基线）', 'info', tag);
                continue;
            }
            已探++;
            const one = st;
            const rec = await 打探测(sess, tag, one.号, one.描述, async function () {
                const r = await one.fn();
                try { logRaw强制(tag, '探测 ' + one.号 + ' 响应', (r && r.响应) ? r.响应 : r, 1200); } catch (eR) {}
                return r;
            });
            表.push(rec);
            if (!rec.有效) continue;
            // 命中 → 立即锁定
            命中 = one.号;
            锁 = {
                action: String(one.口径.action), offset: Number(one.口径.offset || 0),
                sortMode: String(one.口径.sortMode || 'all'), mode: String(one.口径.mode || 'server'),
                标签: String(one.号), 来源: '自动探测', 时间: Date.now()
            };
            log('人脉口径锁定：' + 锁.标签 + ' （动作=' + 锁.action + '，位置偏移=' + 锁.offset +
                '，sortMode=' + 锁.sortMode + '）', 'success', tag);
            // 重复同卡验证（决定卡池不足时能不能靠重复补满）
            const 验卡 = (命中 === 'D6' && latest卡) ? latest卡 : 探卡;
            const 验 = await 重复验证同卡(sess, tag, 验卡, 锁);
            锁.按次数 = 验.按次数;
            写人脉口径(锁);
            // 同一轮后续都用锁定口径跑完剩下张数
            const 剩余 = [];
            for (let m2 = 0; m2 < 卡池.length; m2++) {
                const cd = 卡池[m2];
                if (!cd || !cd.cardId) continue;
                if (已试[cd.cardId]) continue;
                if (String(cd.cardId) === String(探卡.cardId)) continue;
                剩余.push(cd);
            }
            for (let n2 = 0; n2 < 剩余.length && 成功 < 需要数 && 可继续(); n2++) {
                const c2 = 剩余[n2];
                已试[c2.cardId] = 1;
                try {
                    const rr = await 打人脉一张(sess, tag, c2, 锁);
                    if (rr.只曝光 || rr.viewRecorded) {
                        成功++;
                        log('浏览人脉（锁定口径 ' + 锁.标签 + '）' + c2.cardId + ' ✓', 'success', tag);
                    } else {
                        未记录++;
                        log('浏览人脉（锁定口径 ' + 锁.标签 + '）' + c2.cardId + ' 未确认（viewRecorded=false）', 'warn', tag);
                    }
                } catch (e4) {
                    未记录++;
                    log('浏览人脉（锁定口径）失败（' + c2.cardId + '）：' + 中文错误(e4), 'warn', tag);
                }
                await 可停睡(1200);
            }
            break;
        }
        if (!命中) {
            log('人脉口径探测：' + 人脉探测上限 + ' 条口径（D1 对照 + D2..D8）全部无效 —— ' +
                '任务次数不是靠 click/exposure 的参数层拿到的，看 RAW 里有没有 taskProgress / browseCount 线索', 'error', tag);
        }
        return { 口径: 锁, 命中: 命中, 成功: 成功, 未记录: 未记录, 表: 表, 卡池: 卡池 };
    } finally {
        导出原始.on = 原探针;
    }
}
// 卡池不足 + 服务端按「次数」计数 → 重复打已用卡补满（账本按 center 的 doneCount）
// 硬上限：最多 4 轮、总请求 ≤ 目标*2
async function 重复打补满(sess, tag, 卡池, 口径, 目标, 起始done) {
    let 补 = 0, 轮 = 0;
    if (!卡池 || !卡池.length) return 0;
    let 目标数 = Number(目标 || 0);
    if (!isFinite(目标数) || 目标数 <= 0) 目标数 = Number(默认浏览人脉 || 8);
    const 请求上限 = Math.max(1, 目标数 * 2);
    let done = (起始done == null) ? null : Number(起始done);
    if (done != null && !isFinite(done)) done = null;
    log('补满前 doneCount=' + (done == null ? '?' : done) + ' / 目标 ' + 目标数 +
        (done == null ? '' : '，还差 ' + Math.max(0, 目标数 - done) + ' 次') +
        ' → 开始补（口径 ' + String((口径 && 口径.标签) || '默认') + '）', 'warn', tag);
    if (done == null) {
        log('补满跳过：读不到 center 的 doneCount（本地 viewRecorded 不能当账本）', 'error', tag);
        return 0;
    }
    while (可继续() && 轮 < 4 && 补 < 请求上限 && done < 目标数) {
        轮++;
        const 轮前 = done;
        let 本轮 = 0;
        for (let i = 0; i < 卡池.length && 可继续() && 补 < 请求上限; i++) {
            if ((done + 本轮) >= 目标数) break;
            try {
                await 打人脉一张(sess, tag, 卡池[i], 口径);
                补++; 本轮++;
            } catch (e) {
                log('补满第' + 轮 + '轮 重复浏览失败（' + 卡池[i].cardId + '）：' + 中文错误(e), 'warn', tag);
            }
            await 可停睡(1200);
        }
        if (本轮 === 0) { log('补满第' + 轮 + '轮：一张卡都没打出去，停止补满', 'warn', tag); break; }
        let 后 = null;
        try { const p2 = await 读人脉进度(sess, tag); 后 = (p2 == null) ? null : p2.done; }
        catch (eR) { log('补满第' + 轮 + '轮 读 doneCount 失败：' + 中文错误(eR), 'warn', tag); }
        if (后 == null) {
            log('补满第' + 轮 + '轮 发 ' + 本轮 + ' 次，但读不到 doneCount → 停止补满（不盲刷）', 'error', tag);
            break;
        }
        const 增 = 后 - 轮前;
        done = 后;
        log('补满第' + 轮 + '轮 ' + (增 >= 0 ? '+' + 增 : String(增)) + ' → doneCount=' + done +
            (done >= 目标数 ? '（已达标）' : '（还差 ' + Math.max(0, 目标数 - done) + '）'),
            (增 > 0) ? 'success' : 'warn', tag);
        if (done >= 目标数) break;
    }
    if (done >= 目标数) {
        log('补满完成：doneCount ' + done + '/' + 目标数 + '（共发 ' + 补 + ' 次请求，跑了 ' + 轮 + ' 轮）', 'success', tag);
    } else {
        log('补满中止：doneCount ' + (done == null ? '?' : done) + '/' + 目标数 +
            '（共发 ' + 补 + ' 次请求，跑了 ' + 轮 + ' 轮；上限 4 轮 / 请求 ' + 请求上限 + '）', 'warn', tag);
    }
    return 补;
}

// ═══════════════ 任务执行 ═══════════════
async function 跑浏览人脉(sess, tag, 任务组) {
    if (!任务组 || !任务组.length) return;
    let need = 0;
    for (let i = 0; i < 任务组.length; i++) need += 算缺口(任务组[i]).need;
    if (need <= 0) { log('浏览人脉任务已完成，跳过', 'info', tag); return; }
    let 前 = null;
    try { 前 = await 读人脉进度(sess, tag); } catch (e0) { log('读浏览人脉基线失败：' + 中文错误(e0), 'warn', tag); }
    const 起始 = (前 == null) ? null : 前.done;
    // actionUrl 是服务端给的"该去哪浏览"的权威答案
    try {
        const it0 = (前 && 前.item) ? 前.item : null;
        const raw0 = (前 && 前.raw) ? 前.raw : null;
        const 路由 = String((it0 && it0.actionUrl) || (raw0 && raw0.actionUrl) || '');
        const 动作类型 = String((it0 && it0.actionType) || (raw0 && raw0.actionType) || '');
        if (路由) {
            const 像人脉页 = /network|business-card|feed|card/i.test(路由);
            log('browse_network.actionUrl = ' + 路由 + '（actionType=' + (动作类型 || '-') + '）',
                像人脉页 ? 'info' : 'error', tag);
            if (!像人脉页) {
                log('⚠ actionUrl 不是人脉页路由（期望 /pages/network/index 这类）—— 服务端可能要我们先去别的位置浏览，' +
                    '只盯 /business-cards/{id}/click 是打不到任务次数的', 'error', tag);
            }
        } else {
            log('browse_network 未下发 actionUrl（前端按 feed 内点击 image_popup / link_jump 处理）', 'info', tag);
        }
    } catch (eAU) {}
    let 成功 = 0, 未记录 = 0, 补次 = 0;
    const 试过 = {};
    let 卡池 = [];
    let 口径 = 读人脉口径();
    if (是否内置默认口径(口径)) {
        log('人脉口径：内置默认 ' + 人脉口径描述(口径) + ' —— 真机已验证（D7 增量 +1），' +
            '主轮直接用它，不再先打 image_popup 一轮', 'info', tag);
    } else if (口径) {
        log('人脉口径：复用上次锁定的 ' + 人脉口径描述(口径) + '（本轮不再探测）', 'info', tag);
    }
    const 轮次 = ['all', 'latest'];
    for (let r = 0; r < 轮次.length && 成功 < need && 可继续(); r++) {
        const 模式 = 轮次[r];
        if (r > 0) log('浏览人脉：all 轮只记到 ' + 成功 + '/' + need + '，改用 sortMode=latest 补一轮', 'warn', tag);
        let cards = [];
        try { cards = await 取人脉卡片(sess, need - 成功 + 2, tag, 模式); }
        catch (eL) { log('拉人脉列表失败（' + 模式 + '）：' + 中文错误(eL), 'warn', tag); continue; }
        if (!cards.length) { log('人脉列表（' + 模式 + '）没拿到可用卡片', 'warn', tag); continue; }
        for (let cz = 0; cz < cards.length; cz++) 卡池.push(cards[cz]);
        for (let k = 0; k < cards.length && 成功 < need && 可继续(); k++) {
            const c = cards[k];
            if (试过[c.cardId]) continue;
            试过[c.cardId] = 1;
            // 曝光 + 点击一次发完（与 App 顺序一致，中间不插第二次列表请求）
            let res = null;
            try { res = await 打人脉一张(sess, tag, c, 口径); }
            catch (e2) {
                log('人脉点击失败（' + c.cardId + '）：' + 中文错误(e2), 'warn', tag);
                await 任务间隔();
                continue;
            }
            const 位置示 = (res && res.位置 != null) ? res.位置 : c.cardPosition;
            const 动作示 = (res && res.动作) ? res.动作 : 人脉点击动作(c.contentMode);
            if (res && (res.viewRecorded === true || res.只曝光)) {
                成功++;
                log('浏览人脉 ' + 成功 + '/' + need + '：' + c.cardId +
                    '（cardPosition=' + 位置示 + ', ' + 动作示 + ', viewRecorded=' + (res.只曝光 ? 'n/a(只曝光)' : 'true') + '）', 'success', tag);
            } else {
                未记录++;
                log('浏览人脉 ' + c.cardId + ' 未记录浏览（viewRecorded=false，position=' + 位置示 + '）', 'warn', tag);
            }
            await 任务间隔();
        }
    }
    // 复检：读一次 center
    let 现在 = null;
    if (可继续()) {
        try { const 后 = await 读人脉进度(sess, tag); 现在 = (后 == null) ? null : 后.done; }
        catch (e3) { log('复检浏览人脉进度失败：' + 中文错误(e3), 'warn', tag); }
    }
    let 涨了 = (起始 != null && 现在 != null && 现在 > 起始);
    if (现在 != null && 起始 != null) {
        log('浏览人脉服务端进度：本轮前 ' + 起始 + ' → 本轮后 ' + 现在 + (涨了 ? '（已计数）' : '（仍未计数）'),
            涨了 ? 'success' : 'warn', tag);
    }
    // --probe 强制探测；否则只在「打完 doneCount 仍不涨」时探测
    let 要探测 = false;
    if (运行参数.probe && 卡池.length && 可继续() && (成功 > 0 || 未记录 > 0)) {
        要探测 = true;
        log('--probe：强制跑人脉口径 D1..D8 探测（不采信内置 D7 默认）', 'warn', tag);
    } else {
        要探测 = (!涨了) && (现在 != null) && 可继续() && (成功 > 0 || 未记录 > 0);
    }
    if (!运行参数.probe && !涨了 && 口径 && !是否内置默认口径(口径) && (成功 > 0 || 未记录 > 0)) {
        log('人脉口径 ' + String(口径.标签 || '?') + ' 本轮没让 doneCount 上涨（可能已过期）→ 重新探测，命中后覆盖 .cache/qingke_renmai.json', 'warn', tag);
    }
    if (!运行参数.probe && !涨了 && 是否内置默认口径(口径) && (成功 > 0 || 未记录 > 0)) {
        log('内置默认口径 contact_popup 本轮没让 doneCount 上涨（服务端可能改了上报点）→ 立刻探测 D1..D' + 人脉探测上限, 'warn', tag);
    }
    if (要探测) {
        const 探 = await 人脉口径探测(sess, tag, { 已试: 试过, 卡池: 卡池, 需要数: need, 起始: 起始, 主轮口径: 口径 });
        if (探.口径) { 口径 = 探.口径; 成功 += 探.成功; 未记录 += 探.未记录; }
        else { 未记录 += 探.未记录; }
        if (探.卡池 && 探.卡池.length > 卡池.length) 卡池 = 探.卡池;
        try {
            const 后2 = await 读人脉进度(sess, tag);
            if (后2 != null) { 现在 = 后2.done; 涨了 = (起始 != null && 现在 > 起始); }
        } catch (e4) { log('探测后复检进度失败：' + 中文错误(e4), 'warn', tag); }
        if (现在 != null) {
            log('浏览人脉服务端进度（探测后）：本轮前 ' + (起始 == null ? '?' : 起始) + ' → 本轮后 ' + 现在 +
                (涨了 ? '（已计数）' : '（仍未计数）'), 涨了 ? 'success' : 'warn', tag);
        }
    }
    // 卡池不足 + 服务端按「次数」计数 → 重复打补满（账本按 center 的 doneCount）
    if (口径 && 人脉按次数 !== false && 卡池.length && 可继续()) {
        let 补前 = null;
        try { 补前 = await 读人脉进度(sess, tag); }
        catch (eB) { log('补满前读 center 失败：' + 中文错误(eB), 'warn', tag); }
        const 目标数 = (补前 && 补前.target) ? Number(补前.target) : Number(默认浏览人脉);
        const 当前 = (补前 != null) ? 补前.done : 现在;
        if (人脉按次数 === null) {
            log('口径里没有「按次数」标记 → 按真机结论视为按次数计数，允许重复打补满', 'info', tag);
        }
        if (当前 == null) {
            log('补满跳过：读不到 center 的 doneCount，本地 viewRecorded 不能当账本', 'warn', tag);
        } else if (当前 >= 目标数) {
            log('补满跳过：doneCount 已 ' + 当前 + '/' + 目标数 + '，无需补', 'success', tag);
        } else {
            const 补 = await 重复打补满(sess, tag, 卡池, 口径, 目标数, 当前);
            补次 += 补;
            try {
                const 后3 = await 读人脉进度(sess, tag);
                if (后3 != null) { 现在 = 后3.done; 涨了 = (起始 != null && 现在 > 起始); }
            } catch (e5) {}
            log('重复浏览补满结果：发 ' + 补 + ' 次请求，服务端 doneCount 现在 ' +
                (现在 == null ? '?' : 现在) + '/' + 目标数,
                (现在 != null && 现在 >= 目标数) ? 'success' : 'warn', tag);
        }
    }
    if (口径) log('人脉口径锁定：已生效 ' + 人脉口径描述(口径), 'success', tag);
    if (!涨了 && 未记录 > 0) {
        log('人脉浏览仍未计数：内置 ' + 人脉探测上限 + ' 条口径（D1..D8）全无效，请回传本次 RAW（探测 D1..D8 响应）', 'error', tag);
    }
    log('浏览人脉本轮小计：viewRecorded=true ' + 成功 + ' 条，未记录 ' + 未记录 + ' 条（目标 ' + need +
        ' 条；补满另发 ' + 补次 + ' 次请求；账本以 center 的 doneCount 为准，现在 ' + (现在 == null ? '?' : 现在) + '）',
        成功 ? 'success' : 'warn', tag);
}
async function 跑浏览类(sess, tag, 任务组, 类型) {
    if (!任务组 || !任务组.length) return;
    let need = 0;
    for (let i = 0; i < 任务组.length; i++) need += 算缺口(任务组[i]).need;
    const 名 = 类型名(类型);
    if (need <= 0) { log(名 + '任务已完成，跳过', 'info', tag); return; }
    const ids = await 按类型取ID(sess, 类型, need, tag);
    if (!ids.length) { log('没拿到可用的' + 名 + ' id，跳过', 'warn', tag); return; }
    if (ids.length < need) log(名 + '可用 id 只有 ' + ids.length + ' 个，目标 ' + need + ' 个', 'warn', tag);
    let ok = 0;
    for (let k = 0; k < ids.length && k < need && 可继续(); k++) {
        try {
            await 浏览一条(sess, 类型, ids[k]);
            ok++;
            log(名 + ' ' + ok + '/' + need + '：' + ids[k], 'success', tag);
        } catch (e) {
            log(名 + ' 失败（' + ids[k] + '）：' + 中文错误(e), 'warn', tag);
        }
        await 任务间隔();
    }
    log(名 + '本轮完成 ' + ok + '/' + need, ok >= need ? 'success' : 'warn', tag);
}
async function 做分享(sess, tag, 分组) {
    const 场景表 = [
        { 类型: 'share_network', scene: 'network_contact_popup_share', 名: '人脉' },
        { 类型: 'share_project', scene: 'hall_project_detail_share', 名: '项目' },
        { 类型: 'share_software', scene: 'software_detail_share', 名: '软件' }
    ];
    for (let i = 0; i < 场景表.length && 可继续(); i++) {
        const item = 场景表[i];
        const 任务组 = 分组[item.类型] || [];
        if (!任务组.length) continue;
        let need = 0;
        for (let j = 0; j < 任务组.length; j++) need += 算缺口(任务组[j]).need;
        if (need <= 0) { log('分享' + item.名 + '已完成，跳过', 'info', tag); continue; }
        const ids = await 按类型取ID(sess, item.类型, need, tag);
        if (!ids.length) { log('没拿到' + item.名 + ' id，分享跳过', 'warn', tag); continue; }
        let ok = 0;
        for (let k = 0; k < ids.length && k < need && 可继续(); k++) {
            try {
                const body = buildShareBody(item.scene, ids[k]);
                await api(sess, 'POST', '/api/user/tasks/actions', body);
                ok++;
                log('分享' + item.名 + ' ' + ok + '/' + need + '：' + ids[k], 'success', tag);
            } catch (e) {
                log('分享' + item.名 + ' 失败（' + ids[k] + '）：' + 中文错误(e), 'warn', tag);
            }
            await 任务间隔();
        }
    }
}
async function 做点赞(sess, tag, 任务组) {
    if (!任务组 || !任务组.length) return;
    let need = 0;
    for (let i = 0; i < 任务组.length; i++) need += 算缺口(任务组[i]).need;
    if (need <= 0) { log('点赞软件已完成，跳过', 'info', tag); return; }
    const ids = await 取软件ID(sess, need, tag, true);
    if (!ids.length) { log('没拿到未点赞的软件（软件池不足），点赞跳过', 'warn', tag); return; }
    if (ids.length < need) log('未点赞软件只有 ' + ids.length + ' 个，不足 ' + need + ' 个（软件池不够）', 'warn', tag);
    let ok = 0;
    for (let k = 0; k < ids.length && k < need && 可继续(); k++) {
        try {
            await 点赞一条(sess, ids[k]);
            ok++;
            log('点赞软件 ' + ok + '/' + need + '：' + ids[k], 'success', tag);
        } catch (e) {
            log('点赞失败（' + ids[k] + '）：' + 中文错误(e), 'warn', tag);
        }
        await 任务间隔();
    }
    log('点赞完成 ' + ok + '/' + need, ok >= need ? 'success' : 'warn', tag);
}
async function 做任务中心(sess, tag, center) {
    const tasks = 解析任务列表(center);
    if (!tasks.length) { log('任务中心未返回任务列表，跳过', 'warn', tag); return; }
    const 分组 = {}, 未识别 = [], 跳过 = [];
    for (let i = 0; i < tasks.length; i++) {
        const t = tasks[i];
        // 只做 daily 分组：novice / vip 是"App 内完成"或"需 VIP"的任务
        if (String(t.来源) !== 'daily') continue;
        if (任务是否跳过(t)) { 跳过.push(t); continue; }
        const ty = 匹配任务类型(t.title, t.code, t.来源);
        if (!ty) { 未识别.push(t); continue; }
        if (!分组[ty]) 分组[ty] = [];
        分组[ty].push(t);
    }
    if (跳过.length) {
        const 略 = [];
        for (let sk = 0; sk < 跳过.length && sk < 8; sk++) 略.push(跳过[sk].code + ':' + 跳过[sk].status);
        log('跳过 ' + 跳过.length + ' 个不可做的每日任务（status=locked/maxed/claimed/disabled）：' + 略.join(' '), 'info', tag);
    }
    if (未识别.length) {
        log('有 ' + 未识别.length + ' 个每日任务没匹配到类型（把下面的 code 回传给我们精确化）：', 'warn', tag);
        for (let u = 0; u < 未识别.length; u++) {
            log('  · ' + 未识别[u].title + '  code=' + (未识别[u].code || '-') + '  taskId=' + (未识别[u].taskId || '-'), 'warn', tag);
        }
    }
    await 跑浏览人脉(sess, tag, 分组['browse_network']);
    await 跑浏览类(sess, tag, 分组['browse_project'], 'browse_project');
    await 跑浏览类(sess, tag, 分组['browse_software'], 'browse_software');
    await 做分享(sess, tag, 分组);
    await 做点赞(sess, tag, 分组['like_software']);
    await 领全部奖励(sess, tag);
}

// ═══════════════ 人脉自测（变体扫射 · 差分定位）═══════════════
async function 读人脉进度(sess, tag) {
    const center = await 拉任务中心(sess, tag, false);
    const tasks = 解析任务列表(center);
    let item = null;
    for (let i = 0; i < tasks.length; i++) {
        if (String(tasks[i].code) === 'browse_network') { item = tasks[i]; break; }
    }
    if (!item) {
        for (let m = 0; m < tasks.length; m++) {
            if (String(tasks[m].来源) !== 'daily') continue;
            if (匹配任务类型(tasks[m].title, tasks[m].code, tasks[m].来源) === 'browse_network') { item = tasks[m]; break; }
        }
    }
    const gap = item ? 算缺口(item) : { done: 0, target: 0, need: 0 };
    // 顺手捞原始对象：解析任务列表会丢掉未映射字段
    let raw = null;
    try {
        const daily = (center && center.tasks && center.tasks.daily) || [];
        for (let r = 0; r < daily.length; r++) {
            if (daily[r] && String(daily[r].code) === 'browse_network') { raw = daily[r]; break; }
        }
    } catch (e0) {}
    return { done: gap.done, target: gap.target, item: item, raw: raw };
}
async function 打变体(sess, tag, 变体号, 描述, fn) {
    let 前 = null, 后 = null, 错 = '', 返 = null;
    try { 前 = await 读人脉进度(sess, tag); }
    catch (e0) { 错 = '读基线失败：' + 中文错误(e0); log('变体 ' + 变体号 + ' ' + 错, 'warn', tag); }
    try { 返 = await fn(); }
    catch (e1) { 错 = 中文错误(e1); log('变体 ' + 变体号 + ' 请求异常：' + 错, 'warn', tag); }
    await 可停睡(1200);
    try { 后 = await 读人脉进度(sess, tag); }
    catch (e2) { log('变体 ' + 变体号 + ' 复读进度失败：' + 中文错误(e2), 'warn', tag); }
    const x = 前 ? 前.done : null;
    const y = 后 ? 后.done : null;
    const z = (x == null || y == null) ? null : (y - x);
    const 有效 = (z != null && z > 0);
    const vr = (返 && typeof 返 === 'object' && 返.viewRecorded !== undefined) ? (返.viewRecorded === true) : null;
    log('变体 ' + 变体号 + ' [' + 描述 + '] → 打前 ' + (x == null ? '?' : x) +
        ' / 打后 ' + (y == null ? '?' : y) +
        ' / 增量 ' + (z == null ? '?' : (z >= 0 ? '+' + z : String(z))) +
        ' ← ' + (有效 ? '有效' : '无效') +
        (vr == null ? '' : '（viewRecorded=' + vr + '）') + (错 ? '（' + 错 + '）' : ''),
        有效 ? 'success' : 'warn', tag);
    return { 号: 变体号, 描述: 描述, 前: x, 后: y, 增量: z, 有效: 有效, 错: 错, viewRecorded: vr };
}
function 人脉自测变体() {
    return [
        { n: 1, 描述: 'click(image_popup, cardPosition=服务端值)', fn: async function (ctx) {
            const b = ctx.选({ contentMode: '', cardPosition: ctx.服务端位置, sortMode: ctx.card.sortMode || 'all' });
            ctx.日志('V1 click 请求体', b);
            const r = await 浏览一条(ctx.sess, 'browse_network', ctx.card.cardId, b);
            if (r && r.请求体) ctx.上次idem = r.请求体.idempotencyKey;
            ctx.日志('V1 click 响应体', r);
            return r;
        } },
        { n: 2, 描述: 'click(link_jump, cardPosition=服务端值)（仅 contentMode=link 的卡）', fn: async function (ctx) {
            const lc = ctx.取link卡();
            if (!lc) { log('V2 列表里没有 contentMode=link 的卡，该变体跳过（不算失败）', 'warn', ctx.tag); return null; }
            log('V2 用 link 卡：' + lc.cardId + '（cardPosition=' + lc.cardPosition + '）', 'info', ctx.tag);
            const b = ctx.选({ contentMode: 'link', cardPosition: lc.cardPosition, sortMode: lc.sortMode || 'all' });
            ctx.日志('V2 click 请求体', b);
            const r = await 浏览一条(ctx.sess, 'browse_network', lc.cardId, b);
            if (r && r.请求体) ctx.上次idem = r.请求体.idempotencyKey;
            ctx.日志('V2 click 响应体', r);
            return r;
        } },
        { n: 3, 描述: 'click(image_popup, cardPosition=数组下标)（旧写法对照）', fn: async function (ctx) {
            const b = ctx.选({ contentMode: '', cardPosition: ctx.idx, sortMode: ctx.card.sortMode || 'all' });
            ctx.日志('V3 click 请求体', b);
            const r = await 浏览一条(ctx.sess, 'browse_network', ctx.card.cardId, b);
            ctx.日志('V3 click 响应体', r);
            return r;
        } },
        { n: 4, 描述: 'exposure + click(image_popup, cardPosition=服务端值)（顺序对照）', fn: async function (ctx) {
            const b0 = ctx.选({ contentMode: '', cardPosition: ctx.服务端位置, sortMode: ctx.card.sortMode || 'all' });
            ctx.日志('V4 exposure 请求体', { sortMode: b0.sortMode, cardPosition: b0.cardPosition });
            ctx.日志('V4 exposure 响应体', await 曝光人脉一张(ctx.sess, ctx.card.cardId, b0));
            const b = ctx.选({ contentMode: '', cardPosition: ctx.服务端位置, sortMode: ctx.card.sortMode || 'all' });
            ctx.日志('V4 click 请求体', b);
            const r = await 浏览一条(ctx.sess, 'browse_network', ctx.card.cardId, b);
            if (r && r.请求体) ctx.上次idem = r.请求体.idempotencyKey;
            ctx.日志('V4 click 响应体', r);
            return r;
        } },
        { n: 5, 描述: 'click(detail_view, cardPosition=服务端值)（旧版写法，预期无效）', fn: async function (ctx) {
            const b = ctx.选({ contentMode: '', clickAction: 'detail_view', cardPosition: ctx.服务端位置, sortMode: ctx.card.sortMode || 'all' });
            ctx.日志('V5 click 请求体', b);
            const r = await 浏览一条(ctx.sess, 'browse_network', ctx.card.cardId, b);
            ctx.日志('V5 click 响应体', r);
            return r;
        } },
        { n: 6, 描述: 'click(image_popup) 但 idempotencyKey 复用上一次（验证幂等去重）', fn: async function (ctx) {
            const key = ctx.上次idem || ht('network-card-click');
            log('V6 复用 idempotencyKey=' + key, 'info', ctx.tag);
            const b = ctx.选({ contentMode: '', cardPosition: ctx.服务端位置, sortMode: ctx.card.sortMode || 'all', idempotencyKey: key });
            ctx.日志('V6 click 请求体', b);
            const r = await 浏览一条(ctx.sess, 'browse_network', ctx.card.cardId, b);
            ctx.日志('V6 click 响应体', r);
            return r;
        } }
    ];
}
async function 人脉自测(acc, tag) {
    log('════ 人脉自测（browse_network 变体扫射）════', 'info', tag);
    const 原探针 = 导出原始.on;
    导出原始.on = true;
    try {
        const sess = await 获取会话(acc, tag);
        if (!sess) { log('登录失败，自测终止', 'error', tag); return false; }

        const 基线 = await 读人脉进度(sess, tag);
        const it = 基线.item;
        if (!it) { log('center 里找不到 code=browse_network 的每日任务，无法判定增量，自测终止', 'error', tag); return false; }
        log('browse_network 当前：' + 基线.done + '/' + 基线.target + '  字段如下（全打）', 'info', tag);
        const 打印字段 = ['code', 'taskId', 'title', 'desc', 'dailyLimit', 'doneCount', 'claimedCount',
            'claimableCount', 'progressPercent', 'status', 'statusText', 'buttonText', 'canClaim',
            'actionType', 'actionUrl', 'disabled', 'rewardKey', 'rewardType', 'rewardQuantity',
            'rewardText', 'totalRewardText', 'baseExp', 'gainedExp', '来源'];
        for (let f = 0; f < 打印字段.length; f++) {
            const fk = 打印字段[f];
            log('  · ' + fk + ' = ' + JSON.stringify(it[fk]), 'info', tag);
        }
        let rawStr = '';
        try { rawStr = JSON.stringify(基线.raw || null); } catch (eR) { rawStr = String(基线.raw); }
        if (rawStr && rawStr.length > 600) rawStr = rawStr.substring(0, 600) + '…（截断）';
        log('  · 原始对象 = ' + rawStr, 'info', tag);
        if (it.actionUrl) log('  ★ actionUrl = ' + it.actionUrl + '（服务端可能已经告诉我们该打哪个路由）', 'warn', tag);

        let cards = [];
        try { cards = await 取人脉卡片(sess, 20, tag, 'all'); }
        catch (eL) { log('拉人脉列表失败：' + 中文错误(eL), 'error', tag); }
        if (!cards.length) { log('人脉列表为空，自测终止', 'error', tag); return false; }
        const card = cards[0];
        log('人脉列表拿到 ' + cards.length + ' 张，首卡 cardId=' + card.cardId + '（整个自测只用这一张）', 'info', tag);
        log('首卡定位：cardPosition=' + card.cardPosition + '（' + card.位置来源 + '）' +
            '，列表下标=' + card.列表下标 + '，contentMode=' + (card.contentMode || '(空)') +
            '，sortMode=' + card.sortMode, 'info', tag);
        let 首卡JSON = '';
        try { 首卡JSON = JSON.stringify(card.原始 || {}); } catch (eJ) { 首卡JSON = String(card.原始); }
        if (首卡JSON.length > 1200) 首卡JSON = 首卡JSON.substring(0, 1200) + '…（截断）';
        log('首卡完整 item：' + 首卡JSON, 'info', tag);
        const 透 = 透传字段(card.原始 || {});
        const 透键 = Object.keys(透);
        log(透键.length
            ? ('原始 item 里的白名单字段（只用于排查，不进 click body）：带了 ' + 透键.join(',') + ' → ' + JSON.stringify(透))
            : '原始 item 里没有白名单字段（viewToken / feedToken / exposureToken / sessionNo / cardType…）',
            透键.length ? 'info' : 'warn', tag);

        let idx = 数字或空(card.列表下标);
        if (idx == null) idx = 0;
        let 位置 = 数字或空(card.cardPosition);
        if (位置 == null || 位置 < 0) 位置 = 0;
        const ctx = {
            sess: sess, tag: tag, card: card, idx: Number(idx),
            服务端位置: Number(位置), seed: String(card.shuffleSeed || ''), 上次idem: null,
            选: function (额外) {
                const e2 = 额外 || {};
                const o = {
                    sortMode: String(e2.sortMode || card.sortMode || 'all'),
                    cardPosition: (e2.cardPosition == null) ? Number(位置) : Number(e2.cardPosition),
                    contentMode: String(e2.contentMode == null ? '' : e2.contentMode)
                };
                if (!isFinite(o.cardPosition)) o.cardPosition = 0;
                if (e2.clickAction) o.clickAction = String(e2.clickAction);
                if (e2.idempotencyKey) o.idempotencyKey = String(e2.idempotencyKey);
                return o;
            },
            取link卡: function () {
                for (let c1 = 0; c1 < cards.length; c1++) {
                    if (String(cards[c1].contentMode || '') === 'link') return cards[c1];
                }
                return null;
            },
            日志: function (标签, 对象) { logRaw(tag, 标签, 对象, 600); }
        };
        const 变体 = 人脉自测变体();
        log('开始扫射 ' + 变体.length + ' 个变体（同一张卡，每条打前/打后各读一次 center，并打 viewRecorded）', 'info', tag);
        const 结果 = [];
        for (let v = 0; v < 变体.length && 可继续(); v++) {
            const one = 变体[v];
            结果.push(await 打变体(sess, tag, one.n, one.描述, function () { return one.fn(ctx); }));
        }

        const 赢 = [], 败 = [];
        let 总增 = 0;
        for (let r2 = 0; r2 < 结果.length; r2++) {
            if (结果[r2].有效) { 赢.push('V' + 结果[r2].号); 总增 += (结果[r2].增量 || 0); }
            else 败.push('V' + 结果[r2].号);
        }
        if (赢.length) {
            log('人脉自测结论：' + 赢.join('/') + ' 有效（增量 +' + 总增 + '）；其余无效', 'success', tag);
            log('下一步：把 ' + 赢.join('/') + ' 的写法固化进「跑浏览人脉」，其余变体可以删掉', 'warn', tag);
        } else {
            log('人脉自测结论：全部变体无效，需要服务端侧原因，请回传本次 RAW', 'error', tag);
            log('排查提示：若服务端按卡片去重（同一张卡一天只认一次），先跑的变体会把这张卡吃掉 —— ' +
                '把 取人脉卡片(sess, 20, tag, "all") 改成取第 2/3 张再跑一轮交叉验证；' +
                '若换了卡还是 0，就是服务端侧另有校验（设备指纹 / 行为序列 / 服务端风控），代码层无解', 'warn', tag);
        }
        return 赢.length > 0;
    } finally {
        导出原始.on = 原探针;
    }
}

// ═══════════════ 大厅红包 ═══════════════
function 是登录失效(e) { return !!(e && 登录失效码[String((e && e.code) || '')]); }
function 是未实名(e) { return !!(e && String((e && e.code) || '') === 'user_real_name_verification_required'); }
// 大厅 item 的 hasRedPacket 可能是 true / 1 / "true" / "1"，一律 truthy 判
function 是否带红包(it) {
    if (!it || typeof it !== 'object') return false;
    const v = it.hasRedPacket;
    if (v === true) return true;
    if (v == null || v === false) return false;
    const s = String(v).trim().toLowerCase();
    return (s === 'true' || s === '1');
}
// 可领判定：status==="active" && claim==null && remainingAmount>0 && !(recipientLimit>0 && claimedCount>=recipientLimit)
function 可领判定(d) {
    if (!d || typeof d !== 'object') return { 可领: false, 原因: '红包详情为空' };
    const st = String(d.status == null ? '' : d.status);
    if (st !== 'active') return { 可领: false, 原因: 'status=' + (st || '?') + '（非 active）' };
    if (d.claim != null) {
        const 已领 = 数字或空(d.claim.amount);
        return { 可领: false, 原因: '本人已领过' + (已领 == null ? '' : ' ' + 已领 + ' 元') };
    }
    let 剩 = 数字或空(d.remainingAmount);
    if (剩 == null) 剩 = 0;
    if (!(剩 > 0)) return { 可领: false, 原因: '剩余 0' };
    const 上限 = 数字或空(d.recipientLimit);
    if (上限 == null || 上限 <= 0) return { 可领: true, 原因: '', 剩余: 剩 };
    let 已领数 = 数字或空(d.claimedCount);
    if (已领数 == null) 已领数 = 0;
    if (已领数 >= 上限) return { 可领: false, 原因: '名额已满 ' + 已领数 + '/' + 上限 };
    return { 可领: true, 原因: '', 剩余: 剩 };
}
// 扫大厅带红包文章：先 sortMode=latest，再 all 补一轮；连续 3 页没红包提前停
async function 扫大厅带红包文章(sess, tag) {
    const out = [], seen = {};
    let 总页数 = 0;
    const 模式表 = ['latest', 'all'];
    for (let m = 0; m < 模式表.length && 可继续(); m++) {
        const sortMode = 模式表[m];
        let page = 1, 空页 = 0, 已取 = 0, 本模式红包 = 0, 本模式页 = 0;
        while (page <= 红包模式.列表页上限 && 可继续()) {
            const url = '/api/user/hall/projects?page=' + page + '&pageSize=' + 红包模式.每页条数 +
                '&sortMode=' + encodeURIComponent(sortMode);
            let d = null;
            try { d = await 拉列表接口(sess, url, tag, '大厅列表(' + sortMode + ') p' + page); }
            catch (e) { log('拉大厅列表失败（' + sortMode + ' 第 ' + page + ' 页）：' + 中文错误(e), 'warn', tag); break; }
            const items = 取列表(d, ['projectId']);
            if (!items.length) break;
            总页数++;
            本模式页++;
            已取 += items.length;
            let 本页红包 = 0;
            for (let i = 0; i < items.length; i++) {
                const it = items[i] || {};
                if (!是否带红包(it)) continue;
                本页红包++;
                const pid = (it.projectId != null) ? String(it.projectId) : ((it.id != null) ? String(it.id) : '');
                if (!pid || seen[pid]) continue;
                seen[pid] = 1;
                out.push({
                    projectId: pid,
                    title: String(it.title || ''),
                    hasRedPacket: true,
                    sortMode: sortMode,
                    页: page
                });
            }
            if (本页红包 > 0) { 空页 = 0; 本模式红包 += 本页红包; }
            else {
                空页++;
                log('大厅列表(' + sortMode + ') 第 ' + page + ' 页 ' + items.length + ' 条里没有带红包的（连续 ' +
                    空页 + '/' + 红包模式.无红包页上限 + ' 页）', 'info', tag);
            }
            if (空页 >= 红包模式.无红包页上限) {
                log('大厅列表(' + sortMode + ') 连续 ' + 空页 + ' 页没有带红包的文章，这一轮扫描提前结束', 'info', tag);
                break;
            }
            const nx = 人脉可翻页(d, page, 已取);
            if (!nx.继续) break;
            page++;
            await 可停睡(300);
        }
        log('大厅扫描(' + sortMode + ')：翻了 ' + 本模式页 + ' 页，' + 本模式红包 + ' 条带红包（累计候选 ' +
            out.length + ' 条）', 'info', tag);
    }
    log('大厅里带红包的文章共 ' + out.length + ' 条（扫描 ' + 总页数 + ' 页，sortMode=latest+all，按 projectId 去重）',
        out.length ? 'success' : 'info', tag);
    return out;
}
// 文章详情 → redPacket.redPacketId
async function 取红包ID(sess, projectId, tag, title) {
    const j = await api(sess, 'GET', '/api/user/hall/projects/' + encodeURIComponent(projectId) + '?sourceSortMode=all', null);
    logRaw(tag, '红包 文章详情 ' + projectId, j, 红包模式.原样输出);
    const data = (j && j.data) || {};
    const rp = data.redPacket || null;
    const id = (rp && rp.redPacketId != null) ? String(rp.redPacketId) : '';
    if (!id) {
        log('《' + (title || projectId) + '》详情里没有 redPacket.redPacketId（列表的 hasRedPacket 可能只是角标）→ 跳过',
            'info', tag);
    }
    return id;
}
// 红包详情：status / remainingAmount / recipientLimit / claimedCount / claim.amount
async function 取红包详情(sess, rpId, tag) {
    const j = await api(sess, 'GET', '/api/user/post-red-packets/' + encodeURIComponent(rpId) + '/detail', null);
    logRaw(tag, '红包 detail', j, 红包模式.原样输出);
    return (j && j.data) || {};
}
// 建领取会话：body 只有 {sessionNo}
async function 建红包会话(sess, rpId, tag) {
    const j = await api(sess, 'POST', '/api/user/post-red-packets/' + encodeURIComponent(rpId) + '/view-sessions',
        { sessionNo: ht('post-red-packet-view') });
    logRaw(tag, '红包 会话', j, 红包模式.原样输出);
    const d = (j && j.data) || {};
    const sn = (d.sessionNo != null) ? String(d.sessionNo) : '';
    if (!sn) throw new Error('view-sessions 回包里没有 sessionNo');
    return {
        sessionNo: sn,
        remainingSeconds: 数字或空(d.remainingSeconds),
        eligibleDisplay: 数字或空(d.eligibleDisplay)
    };
}
// 心跳：body 只有 {sessionNo}；资格 = 回包 eligibleDisplay == 1（数值）
async function 红包心跳(sess, rpId, sessionNo, tag) {
    const j = await api(sess, 'POST', '/api/user/post-red-packets/' + encodeURIComponent(rpId) + '/view-sessions/heartbeat',
        { sessionNo: String(sessionNo) });
    logRaw(tag, '红包 心跳', j, 红包模式.原样输出);
    const d = (j && j.data) || {};
    return { remainingSeconds: 数字或空(d.remainingSeconds), eligibleDisplay: 数字或空(d.eligibleDisplay) };
}
// 领取：body {sessionNo, idempotencyKey}；金额回读 detail.claim.amount
async function 领红包一只(sess, rpId, sessionNo, tag) {
    const body = { sessionNo: String(sessionNo), idempotencyKey: ht('post-red-packet-claim') };
    const j = await api(sess, 'POST', '/api/user/post-red-packets/' + encodeURIComponent(rpId) + '/claim', body);
    logRaw(tag, '红包 claim', j, 红包模式.原样输出);
    let amount = null, 读回失败 = '';
    try {
        const d = await 取红包详情(sess, rpId, tag);
        if (d && d.claim) amount = 数字或空(d.claim.amount);
    } catch (e) { 读回失败 = 中文错误(e); }
    return { amount: amount, 读回失败: 读回失败, 请求体: body };
}
// 登录失效（401 族）→ 用当前账号重新登录一次
async function 红包重登(sess, tag, acc) {
    if (!acc || !acc.账号 || !acc.密码) {
        log('登录失效，但会话里没有可用的账号密码做重登', 'error', tag);
        return false;
    }
    log('登录失效，用当前账号重新登录一次…', 'warn', tag);
    try {
        const s2 = await 密码登录(acc.账号, acc.密码, (sess && sess.deviceId) || '', tag);
        if (!s2 || !s2.token) return false;
        sess.token = s2.token;
        sess.refreshToken = s2.refreshToken || '';
        sess.expiresAt = s2.expiresAt || 0;
        sess.phone = s2.phone || sess.phone;
        log('重新登录成功，继续领红包', 'success', tag);
        return true;
    } catch (e) {
        log('重新登录失败：' + 中文错误(e), 'error', tag);
        return false;
    }
}
// 包一层：未实名 / 其它错误直接抛；登录失效 → 重登一次并重试一次
async function 红包请求(sess, tag, acc, 描述, fn) {
    try {
        return await fn();
    } catch (e) {
        if (是未实名(e) || !是登录失效(e)) throw e;
        if (!(await 红包重登(sess, tag, acc))) {
            const e2 = new Error('登录失效且重新登录失败：' + 中文错误(e));
            e2.code = String(e.code || 'user_login_invalid');
            e2.致命 = true;
            throw e2;
        }
        log(描述 + '：重登后重试一次', 'warn', tag);
        return await fn();
    }
}
function 红包终局(e, tag) {
    if (是未实名(e)) {
        log('需实名认证后才能领红包，整体结束（不再继续刷）', 'error', tag);
        return '实名';
    }
    if (e && e.致命) {
        log('登录失效且重新登录失败，整体结束', 'error', tag);
        return '登录';
    }
    return '';
}
// 顺手发一次文章 detail-view（与红包会话无绑定，零成本）
async function 顺手详情浏览(sess, tag, projectId) {
    if (!projectId) return false;
    try {
        await api(sess, 'POST', '/api/user/hall/projects/' + encodeURIComponent(projectId) + '/detail-view',
            { sourceSortMode: 'all', viewToken: ht('hall-detail-view') });
        return true;
    } catch (e) {
        log('顺手发 detail-view 失败（不影响红包）：' + 中文错误(e), 'info', tag);
        return false;
    }
}
// 探一个候选：文章详情取 redPacketId → 红包 detail → 可领判定
async function 探一个红包(sess, tag, it) {
    const projectId = String((it && it.projectId) || '');
    const title = String((it && it.title) || projectId);
    if (!projectId) return { 可领: false, 原因: '缺 projectId' };
    const rpId = await 取红包ID(sess, projectId, tag, title);
    if (!rpId) return { 可领: false, 原因: '详情里没有 redPacketId' };
    const det = await 取红包详情(sess, rpId, tag);
    const 判 = 可领判定(det);
    if (!判.可领) return { 可领: false, rpId: rpId, 原因: 判.原因 };
    return { 可领: true, rpId: rpId, projectId: projectId, title: title, amount: 数字或空(det.remainingAmount) };
}
// 领红包批量：并行计时（所有会话同时进 30 秒窗口）+ 串行领取
async function 领红包批量(sess, tag, 列表, acc) {
    const 池 = [];
    let 成功 = 0, 合计 = 0, 致命 = '', 致命原因 = '', 上次领取 = 0;
    const 总数 = (列表 && 列表.length) ? 列表.length : 0;
    if (!总数) {
        log('本轮没有可领的红包', 'info', tag);
        return { 成功: 0, 合计: 0, 失败: 0, 致命: '', 致命原因: '' };
    }
    // ① 建会话（并行计时窗口：先全建完，30 秒窗口才重叠得起来）
    for (let i = 0; i < 总数 && 可继续() && !致命; i++) {
        const it = 列表[i] || {};
        const 条 = {
            序号: i + 1, 总数: 总数,
            rpId: String(it.rpId || ''), projectId: String(it.projectId || ''), title: String(it.title || it.rpId || ''),
            sessionNo: '', 已建: false, eligible: false, 重建次数: 0,
            已领: false, 金额: null, 失败: ''
        };
        池.push(条);
        await 顺手详情浏览(sess, tag, 条.projectId);
        try {
            const 会话 = await 红包请求(sess, tag, acc, '建领取会话', (function (x) {
                return function () { return 建红包会话(sess, x.rpId, tag); };
            })(条));
            条.sessionNo = 会话.sessionNo;
            条.已建 = true;
            if (会话.eligibleDisplay == 1) 条.eligible = true;
            log('大厅红包 ' + 条.序号 + '/' + 条.总数 + '：《' + 条.title + '》看满 30 秒中…（会话 ' + 条.sessionNo + '）', 'info', tag);
        } catch (e) {
            const 终1 = 红包终局(e, tag);
            if (终1) { 致命 = 终1; 致命原因 = (终1 === '实名') ? '需实名认证后才能领红包' : 中文错误(e); break; }
            条.失败 = '建会话失败：' + 中文错误(e);
            log('《' + 条.title + '》建会话失败：' + 条.失败, 'warn', tag);
        }
    }
    // ② 心跳轮询：第 1 轮立刻打，之后每 10 秒一轮
    for (let r = 1; r <= 红包模式.心跳上限 && 可继续() && !致命; r++) {
        let 待打 = 0;
        for (let q = 0; q < 池.length; q++) if (池[q].已建 && !池[q].已领 && !池[q].失败) 待打++;
        if (!待打) break;
        if (r > 1) {
            log('等 ' + (红包模式.心跳间隔 / 1000) + ' 秒后打第 ' + r + ' 轮心跳…', 'info', tag);
            await 可停睡(红包模式.心跳间隔);
            if (!可继续()) break;
        }
        for (let k = 0; k < 池.length && 可继续() && !致命; k++) {
            const 条2 = 池[k];
            if (!条2.已建 || 条2.已领 || 条2.失败) continue;
            let hb = null, 错 = null;
            try {
                hb = await 红包请求(sess, tag, acc, '心跳', (function (x) {
                    return function () { return 红包心跳(sess, x.rpId, x.sessionNo, tag); };
                })(条2));
            } catch (e) {
                const 终2 = 红包终局(e, tag);
                if (终2) { 致命 = 终2; 致命原因 = (终2 === '实名') ? '需实名认证后才能领红包' : 中文错误(e); break; }
                错 = e;
            }
            if (错) {
                if (条2.重建次数 < 红包模式.重建上限) {
                    条2.重建次数++;
                    log('《' + 条2.title + '》心跳失败（' + 中文错误(错) + '），弃会话重建第 ' + 条2.重建次数 + ' 次', 'warn', tag);
                    try {
                        const 新会 = await 红包请求(sess, tag, acc, '重建会话', (function (x) {
                            return function () { return 建红包会话(sess, x.rpId, tag); };
                        })(条2));
                        条2.sessionNo = 新会.sessionNo;
                        条2.eligible = false;
                    } catch (e2) {
                        const 终3 = 红包终局(e2, tag);
                        if (终3) { 致命 = 终3; 致命原因 = (终3 === '实名') ? '需实名认证后才能领红包' : 中文错误(e2); break; }
                        条2.失败 = '重建会话失败：' + 中文错误(e2);
                        log('《' + 条2.title + '》重建会话仍失败：' + 条2.失败, 'warn', tag);
                    }
                } else {
                    条2.失败 = '心跳失败：' + 中文错误(错);
                    log('《' + 条2.title + '》心跳连续失败，放弃这个红包：' + 条2.失败, 'warn', tag);
                }
                continue;
            }
            if (hb && hb.eligibleDisplay == 1) {
                条2.eligible = true;
                log('大厅红包 ' + 条2.序号 + '/' + 条2.总数 + '：《' + 条2.title + '》看满 30 秒，领取中…', 'success', tag);
                if (上次领取) await 可停睡(红包模式.领间隔);
                上次领取 = 1;
                try {
                    const 领 = await 红包请求(sess, tag, acc, '领取', (function (x) {
                        return function () { return 领红包一只(sess, x.rpId, x.sessionNo, tag); };
                    })(条2));
                    条2.已领 = true;
                    条2.金额 = 领.amount;
                    成功++;
                    if (领.amount != null) {
                        合计 += Number(领.amount) || 0;
                        log('大厅红包 ' + 条2.序号 + '/' + 条2.总数 + '：领到 ' + 领.amount + ' 元（《' + 条2.title + '》）', 'success', tag);
                    } else {
                        log('《' + 条2.title + '》领取成功，但回读金额失败' + (领.读回失败 ? '：' + 领.读回失败 : ''), 'warn', tag);
                    }
                } catch (e3) {
                    const 终4 = 红包终局(e3, tag);
                    if (终4) { 致命 = 终4; 致命原因 = (终4 === '实名') ? '需实名认证后才能领红包' : 中文错误(e3); break; }
                    条2.失败 = '领取失败：' + 中文错误(e3);
                    log('大厅红包 ' + 条2.序号 + '/' + 条2.总数 + '：领取失败：' + 条2.失败 +
                        (e3 && e3.code ? '（code=' + e3.code + '）' : ''), 'warn', tag);
                }
            }
        }
        if (致命) break;
        let 合格 = 0;
        for (let z = 0; z < 池.length; z++) if (池[z].eligible) 合格++;
        log('第 ' + r + ' 轮心跳：合格 ' + 合格 + ' 个 / 共 ' + 池.length + ' 个' +
            (r < 红包模式.心跳上限 ? '（等待 ' + (红包模式.心跳间隔 / 1000) + 's）' : '（已到心跳上限）'), 'info', tag);
    }
    // ③ 收尾：没领到的都给原因
    let 未领 = 0;
    for (let w = 0; w < 池.length; w++) {
        const 条3 = 池[w];
        if (条3.已领) continue;
        未领++;
        if (!条3.失败) {
            条3.失败 = '心跳 ' + 红包模式.心跳上限 + ' 轮仍未合格（超时）';
            log('《' + 条3.title + '》' + 条3.失败, 'warn', tag);
        }
    }
    const 合计取整 = Math.round(合计 * 100) / 100;
    log('本轮红包结果：成功 ' + 成功 + ' 个 / 合计 ' + 合计取整 + ' 元，超时未领 ' + 未领 + ' 个',
        成功 ? 'success' : 'warn', tag);
    return { 成功: 成功, 合计: 合计取整, 失败: 未领, 致命: 致命, 致命原因: 致命原因 };
}
// 大厅红包主流程：一轮一轮扫大厅 → 判可领 → 批量看满 + 领取 → 再扫，直到没有可领的为止
async function 大厅红包流程(sess, tag, acc) {
    log('════ 大厅红包（自动找带红包的文章 · 看满 30 秒领取）════', 'info', tag);
    log('规则：大厅列表只给 hasRedPacket 布尔 → 逐篇拉详情取 redPacketId → 逐个判可领 → ' +
        '批量建会话并行计时（30 秒服务端判定 + 每 10 秒心跳）→ eligibleDisplay==1 才发 claim；最多 ' +
        红包模式.最多轮 + ' 轮', 'info', tag);
    let 轮 = 0, 成功 = 0, 合计 = 0, 失败 = 0, 致命 = '';
    while (轮 < 红包模式.最多轮 && 可继续()) {
        轮++;
        log('──── 第 ' + 轮 + '/' + 红包模式.最多轮 + ' 轮：扫大厅找带红包的文章 ────', 'info', tag);
        let 候选 = [];
        try {
            候选 = await 扫大厅带红包文章(sess, tag);
        } catch (e) {
            const 终A = 红包终局(e, tag);
            if (终A) { 致命 = 终A; break; }
            log('扫大厅失败：' + 中文错误(e), 'error', tag);
            break;
        }
        if (!候选.length) { log('大厅里没有带红包的文章了，结束', 'success', tag); break; }

        const 可领 = [], 本轮见过 = {};
        for (let i = 0; i < 候选.length && 可继续() && !致命; i++) {
            const it = 候选[i];
            if (本轮见过[it.projectId]) continue;   // 同一轮同一篇只处理一次（跨轮允许重试）
            本轮见过[it.projectId] = 1;
            let 探 = null;
            try {
                探 = await 红包请求(sess, tag, acc, '读文章/红包详情', (function (x) {
                    return function () { return 探一个红包(sess, tag, x); };
                })(it));
            } catch (e) {
                const 终B = 红包终局(e, tag);
                if (终B) { 致命 = 终B; break; }
                log('《' + (it.title || it.projectId) + '》读详情失败：' + 中文错误(e), 'warn', tag);
                continue;
            }
            if (!探 || !探.可领) {
                log('跳过《' + (it.title || it.projectId) + '》：' + ((探 && 探.原因) || '不可领'), 'info', tag);
                continue;
            }
            可领.push({
                projectId: it.projectId,
                rpId: 探.rpId,
                title: it.title || 探.title || it.projectId,
                amount: 探.amount
            });
            await 可停睡(300);
        }
        if (致命) break;
        if (!可领.length) {
            log('第 ' + 轮 + ' 轮：带红包的文章都不可领（已领完/已领过），结束', 'info', tag);
            break;
        }
        log('第 ' + 轮 + ' 轮：可领红包 ' + 可领.length + ' 个，批量建会话并行计时（30 秒窗口重叠）', 'success', tag);
        const 结 = await 领红包批量(sess, tag, 可领, acc);
        成功 += 结.成功;
        合计 += 结.合计;
        失败 += 结.失败;
        if (结.致命) {
            致命 = 结.致命;
            log('第 ' + 轮 + ' 轮中止：' + 结.致命原因, 'error', tag);
            break;
        }
        if (!可继续()) break;
        await 可停睡(1000);
    }
    const 合计取整 = Math.round(合计 * 100) / 100;
    if (致命) {
        log('大厅红包汇总（提前结束：' + (致命 === '实名' ? '未实名认证' : '登录失效') + '）：共领 ' + 成功 +
            ' 个，合计 ' + 合计取整 + ' 元（失败 ' + 失败 + ' 个）', 'error', tag);
    } else {
        log('大厅红包汇总：共领 ' + 成功 + ' 个，合计 ' + 合计取整 + ' 元（失败 ' + 失败 + ' 个）',
            成功 ? 'success' : 'warn', tag);
    }
    const 结果 = { 成功: 成功, 合计: 合计取整, 失败: 失败, 致命: 致命 };
    本号统计.红包 = 结果;
    return 结果;
}

// ═══════════════ 配置 / 账号 ═══════════════
function parseLine(line) {
    line = String(line || '').trim();
    if (!line || line.charAt(0) === '#') return null;
    let idx = line.indexOf('#');
    if (idx < 0) {
        // 兼容 手机号&密码 写法
        idx = line.indexOf('&');
        if (idx < 0) return { err: '格式：手机号#密码 → ' + line };
    }
    const phone = line.substring(0, idx).trim();
    const pwd = line.substring(idx + 1).trim();
    if (!isPhone(phone)) return { err: '手机号无效: ' + phone };
    if (!pwd) return { err: '密码不能为空: ' + phone };
    return { 账号: phone, 密码: pwd };
}
// 账号来源优先级：--accounts > QK_ACCOUNTS > QK_PHONE/QK_PASSWORD > 同目录 轻客账号.txt
function 收集账号() {
    const out = [], bad = [];
    let 来源 = '';
    let rawStr = String(运行参数.accounts || '').trim();
    if (rawStr) 来源 = '命令行 --accounts';
    else if (String(process.env.QK_ACCOUNTS || '').trim()) { rawStr = String(process.env.QK_ACCOUNTS).trim(); 来源 = '环境变量 QK_ACCOUNTS'; }
    if (rawStr) {
        const parts = rawStr.split(/[,;\r\n]+/);
        for (let i = 0; i < parts.length; i++) {
            const p = String(parts[i] || '').trim();
            if (!p) continue;
            const r = parseLine(p);
            if (r === null) continue;
            if (r.err) { bad.push(r.err); continue; }
            out.push(r);
        }
        return { list: out, bad: bad, 来源: 来源 };
    }
    const phone = String(process.env.QK_PHONE || '').trim();
    const pwd = String(process.env.QK_PASSWORD || '').trim();
    if (phone || pwd) {
        来源 = '环境变量 QK_PHONE / QK_PASSWORD';
        if (!isPhone(phone)) bad.push('QK_PHONE 手机号无效: ' + phone);
        else if (!pwd) bad.push('QK_PASSWORD 为空');
        else out.push({ 账号: phone, 密码: pwd });
        return { list: out, bad: bad, 来源: 来源 };
    }
    if (fs.existsSync(ACCOUNT_FILE)) {
        来源 = '账号文件 ' + ACCOUNT_FILE;
        let txt = '';
        try { txt = fs.readFileSync(ACCOUNT_FILE, 'utf8'); } catch (e) { txt = ''; }
        const lines = String(txt).split(/\r?\n/);
        for (let i = 0; i < lines.length; i++) {
            const r = parseLine(lines[i]);
            if (r === null) continue;
            if (r.err) { bad.push('第' + (i + 1) + '行 ' + r.err); continue; }
            out.push(r);
        }
        return { list: out, bad: bad, 来源: 来源 };
    }
    return { list: out, bad: bad, 来源: '(无)' };
}
function 加载账号() {
    const r = 收集账号();
    db = r.list;
    return r;
}

// ═══════════════ 单号执行 / 主流程 ═══════════════
async function 执行单号(acc, mode, tag) {
    log('开始处理 ' + tag + '（模式：' + mode + '）', 'info', tag);
    本次签到 = { ok: false, already: false, date: '' };
    本号统计 = { 签到: '-', 任务完成: null, 任务总数: null, 红包: null };
    const sess = await 获取会话(acc, tag);
    if (!sess) { log('登录失败，跳过该账号', 'error', tag); return false; }

    if (mode === '仅登录') { log('登录成功，结束', 'success', tag); return true; }

    // 大厅红包：独立分支 —— 登录后直接跑红包，跑完就 return
    if (mode === '大厅红包') {
        const 结 = await 大厅红包流程(sess, tag, acc);
        本号统计.红包 = 结;
        上次红包结果 = 结;
        return true;
    }
    // 人脉自测：独立分支
    if (mode === '人脉自测') {
        await 人脉自测(acc, tag);
        return true;
    }

    const center = await 拉任务中心(sess, tag, true);
    打印任务快照(center, tag);
    记任务统计(center);

    if (mode === '查进度') { 输出进度(center, tag); return true; }

    if (mode === '仅签到' || mode === '全自动') {
        if (!可继续()) return true;
        log('── 签到 ──', 'info', tag);
        await 做签到(sess, center, tag);
        if (mode === '仅签到') {
            const c2 = await 拉任务中心(sess, tag, false);
            输出进度(c2, tag);
            记任务统计(c2);
            return true;
        }
    }
    if (mode === '仅任务中心' || mode === '全自动') {
        if (!可继续()) return true;
        log('── 任务中心 ──', 'info', tag);
        await 做任务中心(sess, tag, center);
    }
    let 红包结果 = null;
    if (mode === '全自动') {
        if (!可继续()) return true;
        // 领取全部奖励之后、输出战绩之前补跑大厅红包（异常不中断全自动，战绩照打）
        if (可继续()) {
            log('── 大厅红包 ──', 'info', tag);
            try { 红包结果 = await 大厅红包流程(sess, tag, acc); }
            catch (eRP) { log('大厅红包异常：' + 中文错误(eRP), 'error', tag); }
        }
        上次红包结果 = 红包结果;
        await 输出战绩(sess, tag);
    }
    return true;
}

function 格式化时长(ms) {
    const s = Math.max(0, Math.round(ms / 1000));
    if (s < 60) return s + 's';
    return Math.floor(s / 60) + 'm' + (s % 60) + 's';
}
// 结尾汇总块（同时作为通知正文）
function 生成汇总块() {
    const 行 = [];
    行.push('════ 运行汇总 ════');
    行.push('模式：' + (运行参数.mode || '全自动') + '　脚本：v' + SCRIPT_VER + '　耗时：' + 格式化时长(Date.now() - 汇总.开始));
    行.push('账号：成功 ' + 汇总.成功 + ' / 失败 ' + 汇总.失败 + ' / 共 ' + 汇总.记录.length +
        (汇总.中断 ? '（运行被中断）' : ''));
    if (限流中止) 行.push('登录限流：' + (限流信息 || '服务端限流') + '（已提前结束，别马上重跑）');
    let 签已 = 0, 签未 = 0, 红包个数 = 0, 红包金额 = 0, 红包失败 = 0, 任务完成合计 = 0, 任务项合计 = 0;
    for (let i = 0; i < 汇总.记录.length; i++) {
        const r = 汇总.记录[i];
        if (r.签到 && r.签到.indexOf('已签') >= 0) 签已++;
        else if (r.签到 && r.签到 !== '-') 签未++;
        if (r.红包) { 红包个数 += Number(r.红包.成功 || 0); 红包金额 += Number(r.红包.合计 || 0); 红包失败 += Number(r.红包.失败 || 0); }
        if (r.任务总数 != null) { 任务完成合计 += Number(r.任务完成 || 0); 任务项合计 += Number(r.任务总数 || 0); }
    }
    行.push('今日任务（每日 ' + (任务项合计 || 7) + ' 项）：完成 ' + 任务完成合计 + '/' + (任务项合计 || 7));
    行.push('签到：已签 ' + 签已 + ' 个 / 未签 ' + 签未 + ' 个');
    行.push('大厅红包：领到 ' + 红包个数 + ' 个，合计 ' + (Math.round(红包金额 * 100) / 100) + ' 元' +
        (红包失败 ? '（失败 ' + 红包失败 + ' 个）' : ''));
    行.push('──── 分号明细 ────');
    for (let j = 0; j < 汇总.记录.length; j++) {
        const r = 汇总.记录[j];
        const 段 = [];
        段.push(r.账号);
        段.push(r.成功 ? 'OK' : 'FAIL');
        if (r.任务总数 != null) 段.push('任务 ' + (r.任务完成 == null ? '?' : r.任务完成) + '/' + r.任务总数);
        if (r.签到 && r.签到 !== '-') 段.push(r.签到.replace('签到：', ''));
        if (r.红包) 段.push('红包 ' + (r.红包.成功 || 0) + ' 个/' + (r.红包.合计 || 0) + ' 元');
        if (r.备注) 段.push(r.备注);
        行.push('  · ' + 段.join(' · '));
    }
    return 行.join('\n');
}
function 打印汇总() {
    const block = 生成汇总块();
    log('════════════════════════════════════════', 'info');
    for (const line of block.split('\n')) log(line, 'info');
    log('════════════════════════════════════════', 'info');
    return block;
}
// 通知：三种 require 路径依次尝试，全失败静默跳过；绝不影响退出码
function 找通知模块() {
    const 候选 = [
        path.join(__dirname, 'sendNotify'),
        path.join(__dirname, '..', 'sendNotify'),
        'sendNotify'
    ];
    for (let i = 0; i < 候选.length; i++) {
        try {
            const m = require(候选[i]);
            if (m) return m;
        } catch (e) {}
    }
    return null;
}
async function 发送通知(标题, 内容) {
    if (String(process.env.QK_NOTIFY || '') === '0') { log('QK_NOTIFY=0，跳过通知', 'info'); return false; }
    try {
        const m = 找通知模块();
        if (!m) { log('未找到 sendNotify 模块，跳过通知', 'info'); return false; }
        let fn = null;
        if (typeof m === 'function') fn = m;
        else if (typeof m.sendNotify === 'function') fn = m.sendNotify;
        else if (m.default && typeof m.default === 'function') fn = m.default;
        else if (m.default && typeof m.default.sendNotify === 'function') fn = m.default.sendNotify;
        if (!fn) { log('sendNotify 模块里没有可调用的推送函数，跳过通知', 'info'); return false; }
        const r = fn(标题, 内容);
        if (r && typeof r.then === 'function') await r;
        log('通知已发送', 'success');
        return true;
    } catch (e) {
        log('通知发送失败（忽略）：' + (e && e.message ? e.message : e), 'warn');
        return false;
    }
}
async function 主流程() {
    let 失败数 = 0;
    try {
        log('轻客助手 v' + SCRIPT_VER + ' 开始运行（青龙 CLI）', 'info');
        log('运行模式: ' + 运行参数.mode, 'info');
        log('接口地址: ' + BASE_URL, 'info');
        log('HTTP 实现: ' + HTTP_实现名, 'info');
        log('任务间隔: ' + 运行配置.任务间隔 + 'ms' + (运行参数.debug ? '　--debug 已开' : '') +
            (运行参数.once ? '　--once 已开' : '') + (运行参数.probe ? '　--probe 已开' : ''), 'info');
        log('账号数量: ' + db.length, 'info');
        const mode = 运行参数.mode;
        for (let i = 0; i < db.length && 可继续(); i++) {
            if (限流中止) {
                汇总.中断 = true;
                log('检测到登录限流，停止后续账号，避免继续加重：' + 限流信息, 'error');
                break;
            }
            const tag = maskAcc(db[i].账号);
            log('════ ' + (i + 1) + '/' + db.length + ' ════', 'info', tag);
            let ok = false, 备注 = '';
            try {
                ok = await 执行单号(db[i], mode, tag);
            } catch (e) {
                const 账号级锁定 = String(e && e.code) === 'user_login_too_many_attempts';
                if (账号级锁定) {
                    // 只锁了这一个账号：记失败，继续跑下一个
                    备注 = '账号锁定: ' + 中文错误(e);
                    log(备注, 'error', tag);
                } else if (e && (e.冷却中 || 是限流码(e.code))) {
                    备注 = '登录限流: ' + 中文错误(e);
                    限流中止 = true;
                    汇总.中断 = true;
                    log(备注 + (限流信息 ? '（' + 限流信息 + '）' : ''), 'error', tag);
                } else {
                    备注 = '异常: ' + 中文错误(e);
                    log(备注, 'error', tag);
                }
                ok = false;
            }
            const rec = {
                账号: tag, 成功: ok,
                签到: 本号统计.签到 || '-',
                任务完成: 本号统计.任务完成,
                任务总数: 本号统计.任务总数,
                红包: 本号统计.红包 || null,
                备注: 备注
            };
            汇总.记录.push(rec);
            if (ok) 汇总.成功++; else { 汇总.失败++; 失败数++; }
            if (限流中止) { 汇总.中断 = true; break; }
            if (i < db.length - 1 && 可继续()) await 多号间隔();
        }
        if (停止标志) 汇总.中断 = true;
        log('全部完成：成功 ' + 汇总.成功 + '/' + db.length, 汇总.失败 ? 'warn' : 'success');
    } catch (eMain) {
        log('主流程异常: ' + 中文错误(eMain), 'error');
        失败数++;
        汇总.失败++;
    }
    const block = 打印汇总();
    await 发送通知('轻客助手 结果', block);
    return 失败数;
}

// ═══════════════ CLI 入口 ═══════════════
function 打印帮助() {
    const lines = [];
    lines.push('轻客助手 · 青龙 CLI v' + SCRIPT_VER);
    lines.push('');
    lines.push('用法：node ' + path.basename(__filename) + ' [选项]');
    lines.push('');
    lines.push('选项：');
    lines.push('  --mode=名称        运行模式：' + MODE_LIST.join(' | '));
    lines.push('  --accounts=串      账号串，逗号/分号/换行分隔，元素 手机号#密码 或 手机号&密码');
    lines.push('  --debug            打 RAW（响应体前 800 字符，截断）');
    lines.push('  --once             忽略缓存令牌，强制重新登录');
    lines.push('  --probe            强制跑人脉口径 D1..D8 探测');
    lines.push('  --help, -h         显示本帮助');
    lines.push('');
    lines.push('环境变量：');
    lines.push('  QK_ACCOUNTS / QK_PHONE + QK_PASSWORD / QK_MODE / QK_BASE_URL / QK_NOTIFY=0');
    lines.push('  QK_TASK_INTERVAL / QK_MULTI_DELAY / QK_DELAY_A / QK_DELAY_B / QK_LOGIN_INTERVAL');
    lines.push('');
    lines.push('账号文件：' + ACCOUNT_FILE + '（每行 手机号#密码，# 开头为注释）');
    lines.push('缓存目录：' + CACHE_DIR);
    lines.push('');
    lines.push('模式说明：');
    for (let i = 0; i < MODE_LIST.length; i++) lines.push('  ' + MODE_LIST[i] + '：' + MODE_HINTS[i]);
    lines.push('');
    lines.push('退出码：0 全部成功 / 1 有账号失败 / 2 配置缺失或环境不满足');
    return lines.join('\n');
}
function parseArgs(argv) {
    const o = { mode: '', accounts: '', debug: false, once: false, probe: false, help: false, 错误: '' };
    for (let i = 0; i < argv.length; i++) {
        let a = String(argv[i] || '');
        if (!a) continue;
        if (a === '--help' || a === '-h' || a === '/?') { o.help = true; continue; }
        if (a === '--debug') { o.debug = true; continue; }
        if (a === '--once') { o.once = true; continue; }
        if (a === '--probe') { o.probe = true; continue; }
        if (a.indexOf('--mode=') === 0) { o.mode = a.substring(7).trim(); continue; }
        if (a === '--mode') { o.mode = String(argv[++i] || '').trim(); continue; }
        if (a.indexOf('--accounts=') === 0) { o.accounts = a.substring(11).trim(); continue; }
        if (a === '--accounts') { o.accounts = String(argv[++i] || '').trim(); continue; }
        o.错误 = '未识别的参数: ' + a;
    }
    return o;
}
function 应用运行配置() {
    const 间 = Number(process.env.QK_TASK_INTERVAL || 0);
    if (isFinite(间) && 间 > 0) 运行配置.任务间隔 = Math.max(300, Math.round(间));
    if (process.env.QK_MULTI_DELAY != null && String(process.env.QK_MULTI_DELAY) !== '') {
        运行配置.多号延迟 = String(process.env.QK_MULTI_DELAY) !== '0';
    }
    const a = Number(process.env.QK_DELAY_A || 0), b = Number(process.env.QK_DELAY_B || 0);
    if (isFinite(a) && a > 0) 运行配置.延迟A = Math.round(a);
    if (isFinite(b) && b > 0) 运行配置.延迟B = Math.round(b);
    const 登录间 = Number(process.env.QK_LOGIN_INTERVAL || 0);
    if (isFinite(登录间) && 登录间 > 0) 运行配置.登录间隔 = Math.max(500, Math.round(登录间));
}

async function main() {
    const 参数 = parseArgs(process.argv.slice(2));
    if (参数.help) { console.log(打印帮助()); return 0; }
    if (参数.错误) {
        console.error('[ERROR] ' + 参数.错误);
        console.error(打印帮助());
        return 2;
    }
    运行参数.debug = 参数.debug;
    运行参数.once = 参数.once;
    运行参数.probe = 参数.probe;
    运行参数.accounts = 参数.accounts;
    应用运行配置();

    // 模式：--mode= > QK_MODE > 全自动
    let mode = String(参数.mode || process.env.QK_MODE || '全自动').trim();
    if (MODE_LIST.indexOf(mode) < 0) {
        console.error('[ERROR] 未知模式：' + mode + '（可选：' + MODE_LIST.join(' / ') + '）');
        console.error(打印帮助());
        return 2;
    }
    运行参数.mode = mode;

    // HTTP 实现（必须先确认，缺 fetch + axios 直接退 2）
    const okHttp = await 初始化HTTP();
    if (!okHttp) {
        console.error('[ERROR] 当前 Node 既没有全局 fetch 也没有 axios：' +
            '请升级到 Node 18+ 或执行 npm i axios 后重试');
        return 2;
    }

    // 账号
    加载凭证缓存();
    const 账号结果 = 加载账号();
    if (!db.length) {
        console.error('[ERROR] 配置缺失：没有找到账号。请用下面任一方式提供：');
        console.error('  1) 环境变量 QK_ACCOUNTS=13800000000#密码,13800000001#密码');
        console.error('  2) 环境变量 QK_PHONE=13800000000 且 QK_PASSWORD=密码');
        console.error('  3) 脚本同目录新建 轻客账号.txt，每行 手机号#密码');
        console.error('  4) 命令行 --accounts=13800000000#密码');
        if (账号结果.bad && 账号结果.bad.length) {
            console.error('[ERROR] 解析失败的行：');
            for (let i = 0; i < 账号结果.bad.length && i < 10; i++) console.error('  · ' + 账号结果.bad[i]);
        }
        return 2;
    }
    if (账号结果.bad && 账号结果.bad.length) {
        for (let i = 0; i < 账号结果.bad.length && i < 10; i++) {
            console.error('[WARN] 账号行解析失败（已跳过）：' + 账号结果.bad[i]);
        }
    }
    log('账号来源: ' + 账号结果.来源 + '（' + db.length + ' 个）', 'info');

    // 查进度模式强制开原始响应探针
    if (mode === '查进度') 导出原始.on = true;

    const 失败数 = await 主流程();
    return (失败数 > 0 || 汇总.失败 > 0) ? 1 : 0;
}

// ---- 信号处理：SIGINT / SIGTERM 置停止标志，优雅退出 ----
let 信号已收 = 0;
let 强退定时器 = null;
function 处理信号(sig) {
    信号已收++;
    if (信号已收 === 1) {
        停止标志 = true;
        开始检测 = false;
        log('收到 ' + sig + '：正在优雅退出（当前请求完成后停止，再按一次强制结束）', 'warn');
        // 优雅窗口 20s：超时就地退出（退出码 1，标记中断）
        强退定时器 = setTimeout(function () {
            try { console.error('[' + nowStr() + '] [全局] [WARN] 优雅退出超时，强制结束'); } catch (e) {}
            process.exit(1);
        }, 20000);
        if (强退定时器 && 强退定时器.unref) 强退定时器.unref();
    } else {
        try { console.error('[' + nowStr() + '] [全局] [WARN] 再次收到 ' + sig + '，立即结束'); } catch (e) {}
        process.exit(1);
    }
}
process.on('SIGINT', function () { 处理信号('SIGINT'); });
process.on('SIGTERM', function () { 处理信号('SIGTERM'); });

if (require.main === module) {
    main().then(function (code) {
        process.exitCode = code;
        // 给日志/通知的 socket 留一拍，避免被立刻截断
        setTimeout(function () { process.exit(code); }, 50);
    }).catch(function (e) {
        try { console.error('[ERROR] 未捕获异常：' + (e && e.stack ? e.stack : e)); } catch (e2) {}
        process.exit(2);
    });
}

module.exports = {
    main: main,
    运行参数: 运行参数,
    生成汇总块: 生成汇总块,
    MODE_LIST: MODE_LIST
};


// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。