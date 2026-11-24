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

//!/usr/bin/env node
/**
 * 即融 / 智选宝 小程序「福利中心」每日自动签到
 * 入口地址:#小程序://即融AI/4YiSd6NrDzxq4gk
 微信点击小程序链接，登录，我的--福利中心，就是做任务页面，每天签到就有融豆，下面还有很多小任务，按照要求操作就行，很简单，可以直接兑换现金提现，基本秒到微信。
领到的融豆，在下面兑好礼里，可以兑换成余额，再去我的钱包里提现就行，基本秒到微信，提现的时候会要求下载app，正常去下载就行。

首次提现需要实名认证，填姓名身份证号就行(同名也行)没认证费，审核秒通过

app就是即融AI,应用商店可以下载.
脚本就是每天签到，手动也行。这个脚本就是一个初级脚本，有yyb的自己修改成yyb脚本，能更加自动方便
 * 抓包结论（50_31.har，Reqable，2026-11-21）：
 *   POST /auth/wxmini/login?code=&phoneCode=   -> 拿 token + refreshToken
 *   GET  /users/current                        -> 用户信息（验证 token 有效性）
 *   GET  /welfare/home                         -> 签到状态 checkIn.checkedToday
 *   POST /welfare/check-in   body: {}          -> 执行签到，返回积分
 *
 * 关键点：
 *   1) 唯一凭据是 Authorization: Bearer <JWT>，有效期 2 小时（iat/exp 相差 7200s）。
 *   2) 请求头里的 app-key 是 RSA-2048 动态密文，实测服务端【不校验】：
 *      不传 app-key、传全 A 的伪值，接口依旧 200。故脚本不构造它。
 *   3) 不带 Authorization 访问受保护接口 -> 401 {"code":401,"message":"未授权访问"}。
 *   4) 登录用的 code / phoneCode 来自微信客户端，一次性且无法伪造 —— 所以脚本
 *      只能吃抓包得到的 token，token 过期后需要用 refreshToken 续期（若服务端开放）
 *      或重新抓包。
 *
 * 环境变量：
 *   ZXB_TOKEN          必填。多账号换行分隔。单个账号格式：
 *                        token
 *                        token#refreshToken
 *                        token#refreshToken#备注
 *   ZXB_REFRESH_PATH   续期接口路径，默认 /auth/refresh（若抓包到真实路径请覆盖）
 *   ZXB_APP_VERSION    默认 1.3.1
 *   ZXB_DEVICE_ID      可选，默认使用抓包里的设备 ID
 *   ZXB_QUIET          1 = 不打印用户详情
 *   QL_URL / QL_CLIENT_ID / QL_CLIENT_SECRET  可选，配置后自动把新 token 写回青龙环境变量
 *
 * 用法：node zhixuanbao_welfare.js
 */

'use strict';

const https = require('https');
const zlib = require('zlib');
const { URL } = require('url');

const HOST = 'jirong.zhixuanbao.cn';
const BASE = `https://${HOST}`;
const TIMEOUT = 20000;

const APP_VERSION = process.env.ZXB_APP_VERSION || '1.3.1';
const DEVICE_ID = process.env.ZXB_DEVICE_ID || '66b22125614b4abc90513357651fd35fa';
const CLIENT_TYPE = 'WECHAT_MP';
const REFRESH_PATH = process.env.ZXB_REFRESH_PATH || '/auth/refresh';

// ----------------------------- 基础工具 -----------------------------

function log(...args) {
  console.log('[签到]', ...args);
}

/** 极简 https 请求（无第三方依赖，兼容青龙各版本 Node） */
function http(path, { method = 'GET', headers = {}, body = null } = {}) {
  return new Promise((resolve) => {
    const u = new URL(BASE + path);
    const data = body == null ? null : Buffer.from(typeof body === 'string' ? body : JSON.stringify(body));
    const h = {
      Host: u.host,
      Accept: 'application/json',
      'Accept-Encoding': 'gzip',
      'User-Agent':
        'Mozilla/5.0 (Linux; Android 10; M2007J17C Build/QKQ1.200628.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0 Mobile Safari/537.36 MicroMessenger/8.0.50',
      Referer: 'https://servicewechat.com/wx06e7f75695cf12b1/23/page-frame.html',
      'X-App-Version': APP_VERSION,
      'X-Client-Type': CLIENT_TYPE,
      'X-Device-Id': DEVICE_ID,
      'content-type': 'application/json',
      env: 'prod',
      charset: 'utf-8',
      ...(data ? { 'Content-Length': data.length } : {}),
      ...headers,
    };

    const req = https.request(
      { hostname: u.hostname, port: 443, path: u.pathname + u.search, method, headers: h },
      (res) => {
        const chunks = [];
        res.on('data', (c) => chunks.push(c));
        res.on('end', () => {
          let buf = Buffer.concat(chunks);
          try {
            if (res.headers['content-encoding'] === 'gzip') buf = zlib.gunzipSync(buf);
            else if (res.headers['content-encoding'] === 'deflate') buf = zlib.inflateSync(buf);
            else if (res.headers['content-encoding'] === 'br') buf = zlib.brotliDecompressSync(buf);
          } catch (_) {
            /* 忽略解压异常，按原文处理 */
          }
          const text = buf.toString('utf8');
          let json = null;
          try {
            json = JSON.parse(text);
          } catch (_) {
            /* 非 JSON */
          }
          resolve({ status: res.statusCode, headers: res.headers, text, json });
        });
      }
    );

    req.setTimeout(TIMEOUT, () => req.destroy(new Error('timeout')));
    req.on('error', (e) => resolve({ status: 0, headers: {}, text: '', json: null, error: e.message }));
    if (data) req.write(data);
    req.end();
  });
}

function decodeJwt(token) {
  try {
    const p = token.split('.')[1];
    return JSON.parse(Buffer.from(p.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8'));
  } catch (_) {
    return null;
  }
}

function shortToken(t) {
  return t.length > 18 ? `${t.slice(0, 10)}...${t.slice(-6)}` : t;
}

// ----------------------------- 青龙交互 -----------------------------

let notified = false;
async function notify(title, content) {
  if (notified) return;
  notified = true;
  try {
    // 青龙自带通知模块；不存在则跳过
    const sendNotify = require('./sendNotify');
    if (typeof sendNotify === 'function') await sendNotify(title, content);
  } catch (_) {
    /* 无通知模块属正常情况 */
  }
}

/**
 * 可选：把刷新后的 token 写回青龙环境变量（需要 QL_URL / QL_CLIENT_ID / QL_CLIENT_SECRET）
 * 不配置就只在日志里打印，不影响签到。
 */
async function saveTokenToQL(value) {
  const { QL_URL, QL_CLIENT_ID, QL_CLIENT_SECRET } = process.env;
  if (!QL_URL || !QL_CLIENT_ID || !QL_CLIENT_SECRET) return false;
  const base = QL_URL.replace(/\/$/, '');
  const q = new URLSearchParams({ searchValue: 'ZXB_TOKEN' });
  const tokResp = await new Promise((resolve) => {
    const req = https.request(
      {
        hostname: new URL(base).hostname,
        port: new URL(base).port || 443,
        path: `${new URL(base).pathname.replace(/\/$/, '')}/open/envs?${q}`,
        method: 'GET',
        headers: { Authorization: `Bearer ${QL_CLIENT_ID}${QL_CLIENT_SECRET}` },
      },
      (r) => {
        const c = [];
        r.on('data', (d) => c.push(d));
        r.on('end', () => {
          try {
            resolve(JSON.parse(Buffer.concat(c).toString('utf8')));
          } catch (_) {
            resolve(null);
          }
        });
      }
    );
    req.on('error', () => resolve(null));
    req.setTimeout(TIMEOUT, () => req.destroy());
    req.end();
  });

  const old = Array.isArray(tokResp && tokResp.data) ? tokResp.data.find((e) => e.name === 'ZXB_TOKEN') : null;
  if (!old) return false;

  const payload = JSON.stringify({ ...old, value, name: 'ZXB_TOKEN' });
  const ok = await new Promise((resolve) => {
    const req = https.request(
      {
        hostname: new URL(base).hostname,
        port: new URL(base).port || 443,
        path: `${new URL(base).pathname.replace(/\/$/, '')}/open/envs`,
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${QL_CLIENT_ID}${QL_CLIENT_SECRET}` },
      },
      (r) => {
        r.on('data', () => {});
        r.on('end', () => resolve(r.statusCode === 200));
      }
    );
    req.on('error', () => resolve(false));
    req.setTimeout(TIMEOUT, () => req.destroy());
    req.end(payload);
  });
  return ok;
}

// ----------------------------- 业务逻辑 -----------------------------

function buildHeaders(ctx, { auth = true } = {}) {
  const h = { 'X-Page-Path': 'package-user/pages/welfare-center/welfare-center' };
  if (auth && ctx.token) h.Authorization = `Bearer ${ctx.token}`;
  if (ctx.refreshToken) h['X-Refresh-Token'] = ctx.refreshToken;
  return h;
}

/**
 * token 过期（2h）后尝试用 refreshToken 换新 token。
 * 注意：未授权的路径一律返回 401，所以判断成功只能靠返回体里的 token。
 */
async function tryRefresh(ctx) {
  if (!ctx.refreshToken) return false;
  const paths = [REFRESH_PATH];
  for (const path of paths) {
    for (const method of ['POST', 'GET']) {
      const r = await http(path, { method, headers: buildHeaders(ctx, { auth: false }), body: method === 'POST' ? {} : null });
      const j = r.json || {};
      if (r.status === 200 && j.code === 200 && (j.token || (j.data && j.data.token))) {
        ctx.token = j.token || j.data.token;
        if (j.refreshToken) ctx.refreshToken = j.refreshToken;
        log(`续期成功（${method} ${path}），新 token ${shortToken(ctx.token)}`);
        return true;
      }
      // 只有非 401 且非 200 才值得换个方法再试，避免无意义刷接口
      if (r.status !== 200 && r.status !== 401 && r.status !== 0) break;
      if (r.status === 200) break;
    }
  }
  return false;
}

async function fetchHome(ctx) {
  return http('/welfare/home', { headers: buildHeaders(ctx) });
}

async function runAccount(ctx) {
  const tag = ctx.remark || shortToken(ctx.token);
  let r = await fetchHome(ctx);

  // 401 => token 过期，尝试续期
  if (r.status === 401 || (r.json && (r.json.code === 401 || r.json.code === 403))) {
    log(`[${tag}] token 失效，尝试续期…`);
    if (await tryRefresh(ctx)) {
      r = await fetchHome(ctx);
    }
    if (r.status === 401 || (r.json && r.json.code === 401)) {
      throw new Error('token 已过期且续期失败，需要重新抓包更新 ZXB_TOKEN');
    }
  }

  if (r.status !== 200 || !r.json || r.json.code !== 200) {
    throw new Error(`查询签到状态失败: HTTP ${r.status} ${(r.text || r.error || '').slice(0, 160)}`);
  }

  // 补充用户信息（便于日志排查，可关闭）
  let who = tag;
  if (process.env.ZXB_QUIET !== '1') {
    const u = await http('/users/current', { headers: buildHeaders(ctx) });
    if (u.json && u.json.code === 200 && u.json.data) {
      const d = u.json.data;
      who = `${d.nickName || '用户'}（${d.mobile ? d.mobile.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : d.id}）`;
    }
  }

  const home = r.json.data || {};
  const ci = home.checkIn || {};

  if (ci.checkedToday) {
    log(`[${who}] 今日已签到，跳过。余额 ${home.balance}（≈${home.approxValue} 元）`);
    return { ok: true, skipped: true, balance: home.balance };
  }

  const c = await http('/welfare/check-in', { method: 'POST', headers: buildHeaders(ctx), body: {} });
  if (c.status !== 200 || !c.json || c.json.code !== 200) {
    throw new Error(`签到请求失败: HTTP ${c.status} ${(c.text || c.error || '').slice(0, 160)}`);
  }
  const d = c.json.data || {};
  if (d.duplicated) {
    log(`[${who}] 服务端判定今日已签到（duplicated）`);
    return { ok: true, skipped: true, points: d.points, balance: d.balanceAfter };
  }
  log(`[${who}] 签到成功 +${d.points} 积分，余额 ${d.balanceAfter}，流水号 ${d.recordNo || '-'}`);
  return { ok: true, points: d.points, balance: d.balanceAfter };
}

function parseAccounts() {
  const raw = process.env.ZXB_TOKEN || '';
  const lines = raw
    .split(/[\n&]/)
    .map((s) => s.trim())
    .filter(Boolean);
  const list = [];
  for (const line of lines) {
    const [token, refreshToken = '', remark = ''] = line.split('#').map((s) => s.trim());
    if (!token) continue;
    list.push({ token, refreshToken, remark });
  }
  return list;
}

(async () => {
  const accounts = parseAccounts();
  if (!accounts.length) {
    console.error('未配置环境变量 ZXB_TOKEN（格式：token[#refreshToken[#备注]]，多账号换行）');
    process.exit(1);
  }
  log(`共 ${accounts.length} 个账号`);

  const results = [];
  for (const ctx of accounts) {
    const jwt = decodeJwt(ctx.token);
    if (jwt && jwt.exp) {
      const left = jwt.exp * 1000 - Date.now();
      if (left <= 0) log(`[${ctx.remark || shortToken(ctx.token)}] 本地判断 token 已过期（exp=${new Date(jwt.exp * 1000).toLocaleString()}）`);
      else log(`[${ctx.remark || shortToken(ctx.token)}] token 剩余 ${Math.round(left / 60000)} 分钟`);
    }
    try {
      results.push(await runAccount(ctx));
    } catch (e) {
      results.push({ ok: false, error: e.message });
      log(`[${ctx.remark || shortToken(ctx.token)}] 失败：${e.message}`);
    }
    await new Promise((r) => setTimeout(r, 800)); // 账号间节流
  }

  const okCount = results.filter((x) => x.ok).length;
  const failCount = results.length - okCount;
  log(`执行完成：成功 ${okCount}，失败 ${failCount}`);

  if (failCount) {
    const msgs = results.filter((x) => !x.ok).map((x) => `- ${x.error}`);
    await notify('智选宝签到失败', `${failCount} 个账号失败：\n${msgs.join('\n')}`);
    process.exit(1);
  }

  // 若发生了续期，把最新 token 回写青龙（可选）
  if (process.env.QL_URL && accounts.some((a) => a.token)) {
    const value = accounts.map((a) => [a.token, a.refreshToken, a.remark].filter(Boolean).join('#')).join('\n');
    if (await saveTokenToQL(value)) log('已将最新 token 写回青龙环境变量 ZXB_TOKEN');
  }
})();

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