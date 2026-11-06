// 阿华手帐本同步后端：Cloudflare Worker + KV
// 部署：dash.cloudflare.com -> Workers & Pages -> 新建 Worker，粘贴本文件；
// 再建一个 KV 命名空间，绑定变量名 LEDGER_KV，重新部署。
// 数据：KV 键 user:<账号>，值 { passHash, data, updatedAt }。
// 密码不在任何地方存原文：页面先用 SHA-256 算哈希再发过来，云上只存哈希、只比哈希。
// 冲突：以 updatedAt 新的一方为准（最后一次同步胜出）。

function corsHeaders(request) {
  var origin = request.headers.get("Origin") || "";
  var allowed =
    origin === "https://wzhuaboy.github.io" ||
    origin.endsWith(".github.io") ||
    origin.indexOf("http://localhost") === 0 ||
    origin.indexOf("http://127.0.0.1") === 0;
  return {
    "Access-Control-Allow-Origin": allowed ? origin : "https://wzhuaboy.github.io",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function jsonResponse(obj, status, request) {
  return new Response(JSON.stringify(obj), {
    status: status,
    headers: Object.assign({ "Content-Type": "application/json" }, corsHeaders(request)),
  });
}

function validUser(user) {
  return typeof user === "string" && /^[A-Za-z0-9_.\-@]{3,32}$/.test(user);
}

function validHash(hash) {
  return typeof hash === "string" && /^[0-9a-f]{64}$/.test(hash);
}

export default {
  async fetch(request, env) {
    var url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(request) });
    }

    // 上传整份账本（登录不存在的账号时自动注册）
    if (url.pathname === "/api/sync" && request.method === "POST") {
      var body = await request.json().catch(function () { return null; });
      if (!body || !validUser(body.user) || !validHash(body.passHash) || !Array.isArray(body.data)) {
        return jsonResponse({ ok: false, error: "bad request" }, 400, request);
      }
      if (JSON.stringify(body.data).length > 1000000) {
        return jsonResponse({ ok: false, error: "data too large" }, 400, request);
      }
      var key = "user:" + body.user;
      var raw = await env.LEDGER_KV.get(key);
      if (!raw) {
        await env.LEDGER_KV.put(key, JSON.stringify({
          passHash: body.passHash,
          data: body.data,
          updatedAt: body.updatedAt || Date.now(),
        }));
        return jsonResponse({ ok: true, created: true }, 200, request);
      }
      var rec = JSON.parse(raw);
      if (rec.passHash !== body.passHash) {
        return jsonResponse({ ok: false, error: "wrong password" }, 401, request);
      }
      await env.LEDGER_KV.put(key, JSON.stringify({
        passHash: rec.passHash,
        data: body.data,
        updatedAt: body.updatedAt || Date.now(),
      }));
      return jsonResponse({ ok: true }, 200, request);
    }

    // 拉取云端账本
    if (url.pathname === "/api/sync" && request.method === "GET") {
      var user = url.searchParams.get("user") || "";
      var passHash = url.searchParams.get("passHash") || "";
      if (!validUser(user) || !validHash(passHash)) {
        return jsonResponse({ ok: false, error: "bad request" }, 400, request);
      }
      var stored = await env.LEDGER_KV.get("user:" + user);
      if (!stored) {
        return jsonResponse({ ok: false, error: "no such user" }, 404, request);
      }
      var record = JSON.parse(stored);
      if (record.passHash !== passHash) {
        return jsonResponse({ ok: false, error: "wrong password" }, 401, request);
      }
      return jsonResponse({ ok: true, data: record.data, updatedAt: record.updatedAt }, 200, request);
    }

    // 注销账号数据（登录态下可用）
    if (url.pathname === "/api/delete" && request.method === "POST") {
      var delBody = await request.json().catch(function () { return null; });
      if (!delBody || !validUser(delBody.user) || !validHash(delBody.passHash)) {
        return jsonResponse({ ok: false, error: "bad request" }, 400, request);
      }
      var delRaw = await env.LEDGER_KV.get("user:" + delBody.user);
      if (!delRaw) {
        return jsonResponse({ ok: false, error: "no such user" }, 404, request);
      }
      if (JSON.parse(delRaw).passHash !== delBody.passHash) {
        return jsonResponse({ ok: false, error: "wrong password" }, 401, request);
      }
      await env.LEDGER_KV.delete("user:" + delBody.user);
      return jsonResponse({ ok: true }, 200, request);
    }

    return jsonResponse({ ok: false, error: "not found" }, 404, request);
  },
};
