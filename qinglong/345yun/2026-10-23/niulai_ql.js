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

/*
 * 注册地址：https://x-nll.orbexa.cc/r/I5C3F1BDDB6
 *
 * ============================ 环境变量 ============================
 * NLLY          必填  账号。支持三种写法，多个用 & 或换行分隔：
 *                      邮箱----密码
 *                      eyJhbGci...（accessToken）
 *                      邮箱----密码&eyJhbGci...
 * NLLY_DEVICE   选填  设备 ID（64 位 hex），不填用内置默认值
 * NLLY_MODE     选填  all | video | project | gate | merge | status  默认 all
 *                      all 全跑 / video 只看视频 / project 只浏览广告
 *                      gate 只做首页广告 / merge 只购买合成 / status 只查状态
 * NLLY_WORKERS  选填  并发账号数                                默认 1
 * NLLY_CLAIM    选填  1/0 是否自动领奖                          默认 1
 * NLLY_HUMAN    选填  1/0 任务间拟人延时                        默认 1
 * NLLY_DEBUG    选填  1/0 打印每个请求                          默认 0
 *
 * 依赖：Node.js >= 14，零第三方库（原生 https + zlib + crypto）
 * ==================================================================
 *
 * 四个业务模块（全部抓包 + 真机实测跑通）：
 *   ① 任务中心看 5 个激励视频        0.15 牛币
 *   ② 任务中心浏览 8 个项目广告      0.10 牛币
 *   ③ 首页看 5 个广告领 0.5 牛币     进度可刷满，领取需在 App 内点
 *   ④ 首页购买牛 + 两头同级牛合成    逐级推到 56 级
 */

const https = require('https');
const zlib = require('zlib');
const crypto = require('crypto');

// 账号上下文隔离：并发跑多账号时，token 绝不能串
let ALS = null;
try { ALS = new (require('async_hooks').AsyncLocalStorage)(); } catch (e) { ALS = null; }

const GLOBAL_SESSION = { token: '', refresh: '', tag: '' };

function currentSession() {
    if (ALS) {
        const s = ALS.getStore();
        if (s) return s;
    }
    return GLOBAL_SESSION;
}

function runInSession(sess, fn) {
    if (ALS) return ALS.run(sess, fn);
    GLOBAL_SESSION.token = sess.token;
    GLOBAL_SESSION.refresh = sess.refresh;
    GLOBAL_SESSION.tag = sess.tag;
    return fn();
}

/* ============================ 常量 ============================ */
const BASE = 'https://x-nllapi.orbexa.cc';
const APP_PKG = 'com.bide.haoyoukan.wwciiii';
const APP_VC = '231';
const APP_VN = '1.1.229';
const DEVICE_ID_SOURCE = 'LEGACY_CLIENT_DEVICE_WEAK';
const DEFAULT_DEVICE_ID = '342b385b7d8274515410abcbe896a5173d57cce2339288f66db5ea23902196dc';
const DEVICE_MODEL = 'MI 8';
const ANDROID_VER = '10';
const USER_AGENT = 'Dalvik/2.1.0 (Linux; U; Android 10; MI 8 MIUI/V12.5.2.0.QEACNXM)';

const SDK_VERSION = 'Y260817';

// 任务 code
const TASK_VIDEO = 'REWARDED_VIDEO';      // 看 5 个激励视频   0.1500
const TASK_PROJECT = 'PROJECT_AD_DAILY';  // 浏览 8 个项目广告 0.1000
const TASK_GATE = 'DAILY_GATE';           // 首页 5 个广告     0.5000

/* ============================ 环境 ============================ */
function env(key, def) {
    const v = process.env[key];
    return (v === undefined || v === '') ? def : v;
}
function envBool(key, def) {
    const v = env(key, '');
    if (v === '') return def;
    return !(v === '0' || v.toLowerCase() === 'false' || v.toLowerCase() === 'no');
}
function envInt(key, def) {
    const n = parseInt(env(key, ''), 10);
    return isNaN(n) ? def : n;
}

const CFG = {
    deviceId: env('NLLY_DEVICE', DEFAULT_DEVICE_ID),
    mode: env('NLLY_MODE', 'all').toLowerCase(),
    workers: Math.max(1, envInt('NLLY_WORKERS', 1)),
    autoClaim: envBool('NLLY_CLAIM', true),
    humanPause: envBool('NLLY_HUMAN', true),
    debug: envBool('NLLY_DEBUG', false),
    token: '',
    refresh: '',
    tag: '',
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ============================ 日志 ============================ */
let LOG_BUFFER = [];

function ts() {
    const d = new Date();
    const p = (n) => (n < 10 ? '0' + n : '' + n);
    return p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
}
function log(msg) {
    const line = '[' + ts() + '] ' + msg;
    console.log(line);
    LOG_BUFFER.push(msg);
}

/* ============================ 工具 ============================ */
function randInt(lo, hi) { return Math.floor(Math.random() * (hi - lo + 1)) + lo; }
function toInt(v, d) { const n = parseInt(v, 10); return isNaN(n) ? (d || 0) : n; }
function mask(v) {
    v = '' + (v || '');
    return v.length <= 14 ? v : v.substring(0, 8) + '...' + v.substring(v.length - 6);
}
function preview(o, lim) {
    try {
        const s = (typeof o === 'string') ? o : JSON.stringify(o);
        return s ? s.substring(0, lim || 300) : '';
    } catch (e) { return ('' + o).substring(0, lim || 300); }
}
function uuid() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return crypto.randomBytes(16).toString('hex').replace(
        /^(.{8})(.{4})(.{4})(.{4})(.{12})$/, '$1-$2-$3-$4-$5');
}
function randomHex(n) {
    return crypto.randomBytes(Math.ceil(n / 2)).toString('hex').substring(0, n);
}
// 32 位大写十六进制订单号（服务端只校验格式，随机即可通过）
function fakeOrderNo() {
    return uuid().replace(/-/g, '').toUpperCase().substring(0, 32);
}

async function humanPause() {
    if (!CFG.humanPause) return;
    await sleep(randInt(800, 2200));
}
async function sleepSec(sec, why) {
    if (sec <= 0) return;
    if (why) log('    ' + why + ' 等待 ' + sec + ' 秒');
    await sleep(sec * 1000);
}

/* ============================ HTTP 内核 ============================ */
function request(method, apiPath, bodyObj, opt) {
    opt = opt || {};
    const urlStr = apiPath.indexOf('http') === 0 ? apiPath : BASE + apiPath;
    const u = new URL(urlStr);

    const headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'X-App-Package': APP_PKG,
        'X-App-Version-Code': APP_VC,
        'X-App-Version-Name': APP_VN,
        'X-Device-Model': DEVICE_MODEL,
        'X-Android-Version': ANDROID_VER,
        'X-Device-Id': CFG.deviceId,
        'X-Device-Id-Source': DEVICE_ID_SOURCE,
        'User-Agent': USER_AGENT,
        'Accept-Encoding': 'gzip',
    };
    const sess = opt.session || currentSession();
    const token = (opt.token !== undefined) ? opt.token : sess.token;
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (opt.headers) Object.assign(headers, opt.headers);

    let bodyStr = null;
    if (bodyObj !== null && bodyObj !== undefined) {
        bodyStr = (typeof bodyObj === 'string') ? bodyObj : JSON.stringify(bodyObj);
        headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    if (CFG.debug) log('    -> ' + method + ' ' + apiPath + (bodyStr ? '  ' + bodyStr : ''));

    return new Promise((resolve) => {
        const req = https.request({
            hostname: u.hostname,
            port: u.port || 443,
            path: u.pathname + u.search,
            method: method,
            headers: headers,
            timeout: 30000,
        }, (res) => {
            const chunks = [];
            res.on('data', (c) => chunks.push(c));
            res.on('end', () => {
                let raw = Buffer.concat(chunks);
                const enc = ('' + (res.headers['content-encoding'] || '')).toLowerCase();
                if (enc.indexOf('gzip') >= 0) {
                    try { raw = zlib.gunzipSync(raw); } catch (e) { }
                }
                const text = raw.toString('utf8');
                if (CFG.debug) log('    <- ' + res.statusCode + ' ' + preview(text, 600));
                let json = null;
                try { json = JSON.parse(text); } catch (e) { json = null; }
                resolve({ status: res.statusCode, raw: text, json: json });
            });
        });

        req.on('timeout', () => { req.destroy(new Error('TIMEOUT')); });
        req.on('error', (e) => {
            resolve({ status: -1, raw: 'CONN:' + e.message, json: null });
        });

        if (bodyStr !== null) req.write(bodyStr);
        req.end();
    });
}

const get = (p, opt) => request('GET', p, null, opt);
const post = (p, body, opt) => request('POST', p, body || {}, opt);

// 统一返回：ok(res) 表示业务成功（HTTP 2xx 且 body.code 缺失或为 0/200）
function ok(res) {
    if (!res || res.status < 200 || res.status >= 300 || !res.json) return false;
    const j = res.json;
    if (j.code !== undefined && j.code !== null) {
        const c = parseInt(j.code, 10);
        return (c === 0 || c === 200) && j.success !== false;
    }
    return j.success !== false;
}
function msgOf(res) {
    if (!res) return 'null';
    if (res.json) {
        const j = res.json;
        return (j.message || j.msg || j.error || j.detail || j.code || '') + '';
    }
    return preview(res.raw, 200);
}
function dataOf(res) {
    if (!res || !res.json) return null;
    const j = res.json;
    if (j.data !== undefined && j.data !== null) return j.data;
    return j;
}

/* ============================ 登录 ============================ */
// 解算术题："7 + 1 = ?" -> "8"
function solveQuestion(q) {
    if (!q) return '';
    const s = ('' + q).replace(/\s+/g, '');
    const m = s.match(/(-?\d+)([+\-*x×\/])(-?\d+)/);
    if (!m) {
        const nums = s.match(/-?\d+/g);
        return nums ? nums[0] : '';
    }
    const a = parseInt(m[1], 10), b = parseInt(m[3], 10), op = m[2];
    let r;
    if (op === '+') r = a + b;
    else if (op === '-') r = a - b;
    else if (op === '*' || op === 'x' || op === '×') r = a * b;
    else { if (b === 0) return '0'; r = a / b; }
    return '' + Math.round(r);
}

async function loginByPassword(email, password, tag) {
    tag = tag || '';
    const ch = await post('/auth/security/challenge', { scene: 'login-password' }, { token: '' });
    if (!ok(ch)) return { ok: false, msg: '安全题失败 ' + msgOf(ch) };
    const cd = dataOf(ch) || {};
    const ticket = cd.ticket || cd.securityTicket || '';
    const question = cd.question || '';
    const answer = solveQuestion(question);

    const r = await post('/auth/login/password', {
        email: email,
        password: password,
        securityTicket: ticket,
        securityAnswer: answer,
    }, { token: '' });

    if (!ok(r)) return { ok: false, msg: '登录失败 ' + msgOf(r) };

    const d = dataOf(r) || {};
    const access = d.accessToken || (d.tokens && d.tokens.accessToken) || d.token || '';
    const refresh = d.refreshToken || (d.tokens && d.tokens.refreshToken) || '';
    if (!access) return { ok: false, msg: '未返回 token' };
    return { ok: true, token: access, refresh: refresh, user: d.user || null, data: d };
}

async function refreshToken() {
    const sess = currentSession();
    if (!sess.refresh) return false;
    log(sess.tag + '刷新 accessToken ...');
    const r = await post('/auth/token/refresh', { refreshToken: sess.refresh }, { token: '' });
    if (!ok(r)) { log(sess.tag + '   刷新失败 ' + msgOf(r)); return false; }
    const d = dataOf(r) || {};
    const access = d.accessToken || d.token || '';
    if (!access) return false;
    sess.token = access;
    if (d.refreshToken) sess.refresh = d.refreshToken;
    log(sess.tag + '   刷新成功 ' + mask(access));
    return true;
}

/* ============================ 任务中心 ============================ */
async function getTaskCenter(tag) {
    const r = await get('/api/v1/task-center');
    if (!ok(r)) { log(tag + '/api/v1/task-center 失败 ' + msgOf(r)); return null; }
    return dataOf(r) || {};
}
function findTask(d, code) {
    if (!d) return null;
    const arr = d.tasks || d.items || [];
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] && arr[i].code === code) return arr[i];
    }
    return null;
}
function taskLine(t) {
    if (!t) return '(无)';
    const pv = (t.progressValue !== undefined) ? t.progressValue : 0;
    const tv = (t.targetValue !== undefined) ? t.targetValue : 0;
    return t.title + ' ' + pv + '/' + tv + ' ' + (t.status || '');
}

async function claimTask(code, tag) {
    const key = uuid();
    const r = await request('POST', '/api/v1/task-center/' + code + '/claim',
        { idempotencyKey: key }, { headers: { 'Idempotency-Key': key } });

    if (ok(r)) {
        const d = dataOf(r) || {};
        const cl = d.claim || {};
        log(tag + '   领奖 ' + (cl.rewardAmount || '-') + ' 牛币  单号 ' + (cl.businessNo || '-'));
        log(tag + '   余额 ' + (d.coinBalance !== undefined ? d.coinBalance : '-'));
        return true;
    }

    const m = msgOf(r);

    // 已领过就返回任务状态提示，不当作失败
    const j = r.json || {};
    const ds = j.data || j;
    if (ds && ds.task && ds.task.status === 'CLAIMED') {
        log(tag + '   本期已领过');
        return true;
    }
    if (('' + m).indexOf('已领取') >= 0 || ('' + m).indexOf('已经领取') >= 0) {
        log(tag + '   本期已领过');
        return true;
    }
    log(tag + '   领奖失败 ' + r.status + ' ' + m);
    return false;
}

/* ============================ ① 看 5 个激励视频 ============================ */
async function createVideoAttempt(tag) {
    const r = await post('/api/v1/task-center/rewarded-video/attempts', {});
    if (!ok(r)) { log(tag + '   x 建单失败 ' + r.status + ' ' + msgOf(r)); return null; }
    const d = dataOf(r) || {};
    const id = d.attemptId || d.id || '';
    if (!id) { log(tag + '   x 建单无 id ' + preview(d, 200)); return null; }
    return { id: id, data: d };
}

async function verifyVideoAttempt(aid, tag) {
    return request('POST',
        '/api/v1/task-center/rewarded-video/attempts/' + aid + '/client-verify',
        { orderNo: fakeOrderNo(), sdkVersion: SDK_VERSION },
        { headers: { 'Idempotency-Key': aid } });
}

async function runRewardedVideo(tag) {
    log(tag + '① 看5个激励视频');
    let t = findTask(await getTaskCenter(tag), TASK_VIDEO);
    if (!t) { log(tag + '   没有该任务'); return false; }

    const need = toInt(t.targetValue, 5);
    let done = toInt(t.progressValue, 0);
    log(tag + '   进度 ' + done + '/' + need);
    if (done >= need) {
        if (CFG.autoClaim) await claimTask(TASK_VIDEO, tag);
        return true;
    }

    const hold = 26;
    let guard = 0;
    while (done < need && guard < 10) {
        guard++;

        const cd = toInt(t.cooldownRemainingSeconds, 0);
        if (cd > 0) {
            await sleepSec(cd + 1);
            t = findTask(await getTaskCenter(tag), TASK_VIDEO) || t;
            done = toInt(t.progressValue, done);
            if (done >= need) break;
        }

        const at = await createVideoAttempt(tag);
        if (!at) { await humanPause(); continue; }

        await sleepSec(hold);
        const v = await verifyVideoAttempt(at.id, tag);
        if (!ok(v)) {
            const vm = msgOf(v);
            log(tag + '   ' + (done + 1) + '/' + need + ' 失败 ' + v.status + ' ' + vm);
            if (('' + vm).indexOf('TOO_QUICKLY') >= 0) await sleepSec(5);
            await humanPause();
            t = findTask(await getTaskCenter(tag), TASK_VIDEO) || t;
            done = toInt(t.progressValue, done);
            continue;
        }

        t = findTask(await getTaskCenter(tag), TASK_VIDEO) || t;
        const now = toInt(t.progressValue, done);
        log(tag + '   ' + (done + 1) + '/' + need + ' 完成');
        done = now;
        await humanPause();
    }

    log(tag + '   进度 ' + done + '/' + need);
    if (done >= need) {
        if (CFG.autoClaim) await claimTask(TASK_VIDEO, tag);
        return true;
    }
    return false;
}

/* ============================ ② 浏览 8 个项目广告 ============================ */
async function getAdTaskCenter(tag) {
    const r = await get('/api/v1/ad-tasks/task-center');
    if (!ok(r)) { log(tag + '/api/v1/ad-tasks/task-center 失败 ' + msgOf(r)); return null; }
    const j = r.json;
    if (j && j.disabled) { log(tag + '   项目广告任务已停用'); return null; }
    const t = taskOf(r);
    if (!t) { log(tag + '取不到广告任务 ' + preview(r.raw, 200)); return null; }
    return t;
}

// 从响应里取出 task 对象，三层兜底
function taskOf(res) {
    if (!res) return null;
    let j = res.json;
    if (!j && res.raw) {
        try { j = JSON.parse(res.raw); } catch (e) { j = null; }
    }
    if (!j) return null;
    if (j.data && j.data.task) return j.data.task;
    if (j.task) return j.task;
    if (j.data && (j.data.item || j.data.id)) return j.data;
    if (j.item || j.id) return j;
    return null;
}

// 心跳直到 item 完成或超时
async function pumpHeartbeat(tid, iid, needSec, tag, seq, total) {
    const base = '/ad-tasks/' + tid + '/items/' + iid;
    let waited = 0;
    const step = 5;
    const limit = needSec + 30;

    while (waited < limit) {
        await sleep(step * 1000);
        waited += step;
        const r = await post(base + '/heartbeat', { viewedSeconds: step });
        if (!ok(r)) {
            log(tag + '   ' + seq + '/' + total + ' 心跳失败 ' + r.status);
            return null;
        }
        const task = taskOf(r);
        if (!task) {
            log(tag + '   ' + seq + '/' + total + ' 心跳无响应');
            return null;
        }
        const it = task.item || {};
        const stat = '' + (it.status || '-');
        if (stat === 'COMPLETED' || stat === 'REWARDED') {
            log(tag + '   ' + seq + '/' + total + ' 完成');
            return task;
        }
        if (stat === 'EXPIRED' || stat === 'FAILED') {
            log(tag + '   ' + seq + '/' + total + ' 状态 ' + stat);
            return null;
        }
    }
    log(tag + '   ' + seq + '/' + total + ' 超时');
    return null;
}

async function runProjectAds(tag) {
    log(tag + '② 浏览8个项目广告');
    const d = await getTaskCenter(tag);
    let t = findTask(d, TASK_PROJECT);
    if (!t) { log(tag + '   没有该任务'); return false; }

    const need = toInt(t.targetValue, 8);
    let done = toInt(t.progressValue, 0);
    log(tag + '   进度 ' + done + '/' + need);
    if (done >= need) {
        if (CFG.autoClaim) await claimTask(TASK_PROJECT, tag);
        return true;
    }

    let guard = 0;
    while (done < need && guard < 30) {
        guard++;

        const task = await getAdTaskCenter(tag);
        if (!task) { log(tag + '   取不到任务'); break; }

        const tid = task.id || '';
        const it = task.item || {};
        const iid = it.id || '';
        const viewSec = toInt(task.viewSeconds, 25) || 25;

        if (!tid || !iid) {
            log(tag + '   没有派发浏览项');
            break;
        }

        const base = '/ad-tasks/' + tid + '/items/' + iid;

        if (it.status === 'ASSIGNED') {
            const stRes = await post(base + '/start', {});
            if (!ok(stRes)) {
                log(tag + '   ' + (done + 1) + '/' + need + ' 开始失败 ' + stRes.status + ' ' + msgOf(stRes));
                await humanPause();
                continue;
            }
        } else if (it.status === 'COMPLETED') {
            await sleep(1200);
            continue;
        }

        const fin = await pumpHeartbeat(tid, iid, viewSec, tag, done + 1, need);
        if (!fin) {
            log(tag + '   ' + (done + 1) + '/' + need + ' 未完成');
            await humanPause();
            continue;
        }

        t = findTask(await getTaskCenter(tag), TASK_PROJECT) || t;
        done = toInt(t.progressValue, 0);
        await humanPause();
    }

    log(tag + '   进度 ' + done + '/' + need);
    if (done >= need && CFG.autoClaim) await claimTask(TASK_PROJECT, tag);
    return done >= need;
}


async function dailyGateTask(tag) {
    const r = await post('/ad-tasks/daily-gate', {});
    if (!ok(r)) { log(tag + '/ad-tasks/daily-gate 失败 ' + msgOf(r)); return null; }
    const d = dataOf(r) || {};
    return d.task || d;
}

function gateLine(g) {
    if (!g) return '(无)';
    const need = (g.configuredCount !== undefined ? g.configuredCount : g.requiredCount);
    return '进度 ' + (g.completedCount !== undefined ? g.completedCount : 0) + '/' + need +
        '  可领 ' + g.canClaim +
        '  状态 ' + (g.status || '-') +
        '  冷却 ' + (g.rewardedCooldownRemainingSeconds || 0) + 's';
}

async function coinBalance(tag) {
    const r = await get('/coin/records?page=1&pageSize=1');
    if (!ok(r)) return null;
    const d = dataOf(r) || {};
    return d.balance;
}

async function runDailyGate(tag) {
    log(tag + '③ 看5个广告领0.5牛币');
    let g = await dailyGateTask(tag);
    if (!g) return false;

    if (g.disabled === true) {
        log(tag + '   该功能已关闭');
        return false;
    }

    const need = toInt(g.configuredCount, toInt(g.requiredCount, 5));
    let done = toInt(g.completedCount, 0);
    const viewSec = toInt(g.viewSeconds, 25) || 25;
    log(tag + '   进度 ' + done + '/' + need);

    let guard = 0;
    while (done < need && guard < 12) {
        guard++;

        const cd = toInt(g.rewardedCooldownRemainingSeconds, 0);
        if (cd > 0) {
            await sleepSec(cd + 1);
            g = (await dailyGateTask(tag)) || g;
            done = toInt(g.completedCount, done);
            if (done >= need) break;
        }

        const r = await post('/api/v1/home-rewarded/attempts', { scene: 'DAILY_CLAIM' });
        if (!ok(r)) {
            log(tag + '   ' + (done + 1) + '/' + need + ' 建单失败 ' + r.status);
            await humanPause();
            continue;
        }
        const a = dataOf(r) || {};
        const aid = a.attemptId || '';
        if (!aid) { log(tag + '   建单无id'); return false; }

        await sleepSec(viewSec + 1);

        const v = await request('POST',
            '/api/v1/home-rewarded/attempts/' + aid + '/client-verify',
            { orderNo: fakeOrderNo(), sdkVersion: SDK_VERSION },
            { headers: { 'Idempotency-Key': aid } });

        if (!ok(v)) {
            const vm = msgOf(v);
            log(tag + '   ' + (done + 1) + '/' + need + ' 失败 ' + v.status + ' ' + vm);
            if (('' + vm).indexOf('TOO_QUICKLY') >= 0) await sleepSec(5);
            await humanPause();
            g = (await dailyGateTask(tag)) || g;
            done = toInt(g.completedCount, done);
            continue;
        }

        g = (await dailyGateTask(tag)) || g;
        log(tag + '   ' + (done + 1) + '/' + need + ' 完成');
        done = toInt(g.completedCount, done);
        await humanPause();
    }

    log(tag + '   进度 ' + done + '/' + need);

    const bal = await coinBalance(tag);
    if (bal !== null) log(tag + '   牛币余额 ' + bal);

    if (done >= need && g.canClaim === true) {
        log(tag + '   已达可领，请在App首页点领取');
    }
    return done >= need;
}


async function ranchState(tag) {
    const r = await get('/api/v1/game/ranch');
    if (!ok(r)) { log(tag + '   牧场查询失败 ' + r.status); return null; }
    return dataOf(r) || null;
}

function walletOf(ranch, asset) {
    const w = (ranch && ranch.wallets) || [];
    for (let i = 0; i < w.length; i++) {
        if (('' + w[i].asset) === asset) return toInt(w[i].available, 0);
    }
    return 0;
}

function levelCfg(ranch, lv) {
    const ls = (ranch && ranch.levels) || [];
    for (let i = 0; i < ls.length; i++) {
        if (toInt(ls[i].level, -1) === toInt(lv, -2)) return ls[i];
    }
    return null;
}

async function buyCow(level, expectedVersion, cycleId, quoteVersion, tag) {
    const key = uuid();
    const body = {
        level: toInt(level, 1),
        expectedVersion: toInt(expectedVersion, 0),
        quoteVersion: toInt(quoteVersion, 2),
        expectedCycleId: cycleId,
    };
    const r = await request('POST', '/api/v1/game/purchases', body,
        { headers: { 'Idempotency-Key': key } });
    if (!ok(r)) {
        const m = msgOf(r);
        if (('' + m).indexOf('INSUFFICIENT_NCOIN') >= 0) log(tag + '   牛币余额不足');
        else if (('' + m).indexOf('QUOTE_CHANGED') >= 0) log(tag + '   牛价已变，下一轮刷新');
        else if (('' + m).indexOf('VERSION_CONFLICT') >= 0) log(tag + '   状态已变，下一轮刷新');
        else if (('' + m).indexOf('RANCH_MAX_LEVEL') >= 0) log(tag + '   已达最高级');
        else log(tag + '   买牛失败 ' + r.status + ' ' + m);
        return null;
    }
    return dataOf(r) || {};
}

async function mergeUp(expectedVersion, cycleId, tag) {
    const key = uuid();
    const body = { expectedCycleId: cycleId, expectedVersion: toInt(expectedVersion, 0) };
    const r = await request('POST', '/api/v1/game/merges', body,
        { headers: { 'Idempotency-Key': key } });
    if (!ok(r)) {
        const m = msgOf(r);
        if (('' + m).indexOf('MATERIAL_STATE_CHANGED') >= 0) log(tag + '   材料状态已变');
        else if (('' + m).indexOf('VERSION_CONFLICT') >= 0) log(tag + '   状态已变，下一轮刷新');
        else if (('' + m).indexOf('RANCH_MAX_LEVEL') >= 0) log(tag + '   已达最高级');
        else if (('' + m).indexOf('RANCH_CYCLE_CHANGED') >= 0) log(tag + '   周期已变，重来');
        else log(tag + '   合成失败 ' + r.status + ' ' + m);
        return null;
    }
    return dataOf(r) || {};
}

async function runPurchaseMerge(tag) {
    log(tag + '④ 购买+合成');

    let guard = 0;
    let merged = 0;
    while (guard < 60) {
        guard++;

        const ranch = await ranchState(tag);
        if (!ranch) return merged > 0;

        const lv = toInt(ranch.level, 1);
        const ver = toInt(ranch.version, 0);
        const cyc = ranch.cycleId || '';
        const maxLv = toInt((ranch.gameplay || {}).maxLevel, 56);
        const el = ranch.operationEligibility || {};

        if (lv >= maxLv) {
            log(tag + '   已达最高 ' + lv + ' 级');
            break;
        }
        if (el.purchase && el.purchase.allowed === false) {
            log(tag + '   购买被拒 ' + (el.purchase.reasonCode || '') + ' ' + (el.purchase.message || ''));
            break;
        }
        if (el.merge && el.merge.allowed === false) {
            log(tag + '   合成被拒 ' + (el.merge.reasonCode || '') + ' ' + (el.merge.message || ''));
            break;
        }
        if (!cyc) { log(tag + '   cycleId 为空'); break; }

        const cfg = levelCfg(ranch, lv);
        if (!cfg) { log(tag + '   查不到 ' + lv + ' 级配置'); break; }

        // 已经有材料牛，直接合成
        if (ranch.material && ranch.material.id) {
            const m2 = await mergeUp(ver, cyc, tag);
            if (m2) {
                const mg = m2.merge || {};
                merged++;
                log(tag + '   ' + mg.from_level + '→' + mg.to_level + ' 合成成功');
            }
            await humanPause();
            continue;
        }

        // 没有材料牛，先看能不能买
        if (cfg.purchasable !== true) {
            log(tag + '   ' + lv + '级(' + (cfg.name || '-') + ')不可购买');
            break;
        }

        const needCoin = toInt(cfg.purchaseUnits, 0);
        const haveCoin = walletOf(ranch, 'NCOIN');
        if (haveCoin < needCoin) {
            log(tag + '   牛币不足 ' + haveCoin + '/' + needCoin);
            break;
        }

        const qv = toInt(cfg.configVersion, 2);
        const b = await buyCow(lv, ver, cyc, qv, tag);
        if (!b) { await humanPause(); continue; }
        const pu = b.purchase || {};
        log(tag + '   买入 ' + lv + '级 ' + (cfg.name || '') +
            ' 花费 ' + toInt(pu.paid_units, needCoin) +
            ' 单号 ' + (pu.business_no || '-'));
        await humanPause();
    }

    const fin = await ranchState(tag);
    if (fin) {
        const flv = toInt(fin.level, 0);
        log(tag + '   当前 ' + flv + ' 级  ' +
            ((levelCfg(fin, flv) || {}).name || '') +
            '  NCOIN ' + walletOf(fin, 'NCOIN') +
            '  贡献 ' + walletOf(fin, 'CONTRIBUTION'));
    }
    log(tag + '   本次合成 ' + merged + ' 次');
    return merged > 0;
}

/* ============================ 状态总览 ============================ */
async function dumpStatus(tag) {
    log(tag + '状态总览');
    const me = await get('/api/v1/identity/me');
    if (ok(me)) {
        const md = dataOf(me) || {};
        log(tag + '   身份 ' + (md.status || '-') + '  余额见下');
    }
    const d = await getTaskCenter(tag);
    if (d) {
        const arr = d.tasks || d.items || [];
        for (let i = 0; i < arr.length; i++) log(tag + '   ' + taskLine(arr[i]));
    }
    const g = await dailyGateTask(tag);
    if (g) log(tag + '   首页 ' + gateLine(g));

    const rn = await ranchState(tag);
    if (rn) {
        const lv2 = toInt(rn.level, 0);
        const cfg2 = levelCfg(rn, lv2) || {};
        log(tag + '   牧场 ' + lv2 + '级 ' + (cfg2.name || '') +
            '  NCOIN ' + walletOf(rn, 'NCOIN') +
            '  贡献 ' + walletOf(rn, 'CONTRIBUTION') +
            (rn.material ? '  有材料待合成' : ''));
    }

    const bal = await coinBalance(tag);
    if (bal !== null) log(tag + '   牛币余额 ' + bal);
}

/* ============================ 单账号主流程 ============================ */
function modeFlags() {
    const m = CFG.mode;
    if (m === 'video') return { video: true, project: false, gate: false, merge: false };
    if (m === 'project') return { video: false, project: true, gate: false, merge: false };
    if (m === 'gate') return { video: false, project: false, gate: true, merge: false };
    if (m === 'merge') return { video: false, project: false, gate: false, merge: true };
    if (m === 'status') return { video: false, project: false, gate: false, merge: false };
    return { video: true, project: true, gate: true, merge: true };
}

async function runAccount(idx, total, tokenOrAcc) {
    const tag = '账号[' + idx + '/' + total + '] ';
    const sess = { token: '', refresh: '', tag: tag };
    log(tag + '开始');

    if (tokenOrAcc.indexOf('@') > 0 && tokenOrAcc.indexOf('----') > 0) {
        const parts = tokenOrAcc.split('----');
        const email = parts[0].trim(), pwd = parts[1].trim();
        const lr = await loginByPassword(email, pwd, tag);
        if (!lr.ok) { log(tag + lr.msg); return false; }
        sess.token = lr.token;
        sess.refresh = lr.refresh || '';
        const lu = lr.user || {};
        log(tag + '已登录 ' + (lu.username || lu.email || mask(email)));
    } else {
        sess.token = tokenOrAcc;
        const me = await get('/api/v1/identity/me', { session: sess });
        if (!ok(me)) {
            log(tag + 'token 过期，尝试刷新');
            if (!(await refreshToken())) return false;
        }
    }

    return runInSession(sess, async () => {
        const f = modeFlags();
        let okVideo = true, okProject = true, okGate = true, okMerge = true;

        if (f.video) okVideo = await runRewardedVideo(tag);
        if (f.project) okProject = await runProjectAds(tag);
        if (f.gate) okGate = await runDailyGate(tag);
        if (f.merge) okMerge = await runPurchaseMerge(tag);

        const all = f.video && f.project && f.gate && f.merge;
        if (all || CFG.mode === 'status') {
            if (all) {
                log(tag + '汇总：5视频=' + (okVideo ? '完成' : '未完成') +
                    '  8项目=' + (okProject ? '完成' : '未完成') +
                    '  首页0.5=' + (okGate ? '完成' : '未完成') +
                    '  购买合成=' + (okMerge ? '完成' : '未完成'));
            }
            await dumpStatus(tag);
        }
        log(tag + '完成');
        if (CFG.mode === 'status') return true;
        return okVideo && okProject && okGate && okMerge;
    });
}

/* ============================ 解析账号 ============================ */
function parseAccounts(text) {
    const arr = [];
    const ls = ('' + text).replace(/\r/g, '').split(/[\n&]+/);
    for (let i = 0; i < ls.length; i++) {
        const v = ls[i].trim();
        if (v) arr.push(v);
    }
    return arr;
}

/* ============================ 并发执行 ============================ */
async function runWithLimit(list, limit, worker) {
    const results = new Array(list.length);
    let cursor = 0;

    async function lane() {
        while (true) {
            const i = cursor++;
            if (i >= list.length) return;
            try {
                results[i] = await worker(i, list[i]);
            } catch (e) {
                log('账号[' + (i + 1) + '] 异常 ' + (e && e.message ? e.message : e));
                results[i] = false;
            }
        }
    }

    const lanes = [];
    const n = Math.min(limit, list.length);
    for (let i = 0; i < n; i++) lanes.push(lane());
    await Promise.all(lanes);
    return results;
}

/* ============================ 通知 ============================ */
async function notify(title, content) {
    try {
        const sendNotify = require('./sendNotify');
        if (typeof sendNotify === 'function') await sendNotify(title, content);
    } catch (e) {
        try {
            const mod = require('./sendNotify.js');
            const fn = mod && (mod.sendNotify || mod.default);
            if (typeof fn === 'function') await fn(title, content);
        } catch (e2) { }
    }
}

/* ============================ 入口 ============================ */
(async () => {
    const raw = env('NLLY', '') || env('NLLY_ACCOUNT', '');
    const list = parseAccounts(raw);

    log('牛来极速版');
    log('账号 ' + list.length + ' 个  并发 ' + CFG.workers + '  模式 ' + CFG.mode);
    log('接口 ' + BASE + '  包名 ' + APP_PKG + '  v' + APP_VN + '(' + APP_VC + ')');

    if (list.length === 0) {
        log('未配置 NLLY 环境变量（邮箱----密码 或 accessToken，多个用 & 分隔）');
        return;
    }

    const t0 = Date.now();
    const results = await runWithLimit(list, CFG.workers, (i, acc) =>
        runAccount(i + 1, list.length, acc));

    let s = 0;
    for (let k = 0; k < results.length; k++) if (results[k]) s++;

    const cost = Math.round((Date.now() - t0) / 1000);
    log('全部完成 成功 ' + s + ' / ' + list.length + '  耗时 ' + cost + 's');

    const tail = LOG_BUFFER.slice(-40).join('\n');
    await notify('牛来极速版 成功 ' + s + '/' + list.length, tail);
})().catch((e) => {
    log('运行异常 ' + (e && e.stack ? e.stack : e));
});


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