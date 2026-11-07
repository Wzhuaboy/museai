// 婚礼邀请函回执后端：Cloudflare Worker + KV
// Worker 名 wedding-rsvp，KV 命名空间 wedding-rsvp，绑定变量名 RSVP_KV
// 公开地址 https://wedding-rsvp.wangzhanghua001023.workers.dev/
// 数据：KV 键 rsvp:list，值是数组 [{name, attend, count, wish, ts}]
// 名单只凭查看口令才能拉取：口令原文不存文件，只存 SHA-256 哈希（ADMIN_KEY_HASH）。
// 客人提交、公开统计不需要口令；查名单、删一条需要口令。
// 部署：python3 ~/workspace/custom-connectors/custom.cloudflare/bin/deploy_wedding_rsvp.py
const ADMIN_KEY_HASH = "adba71f8339da1d8d0a8dc72ba8bf619a3504fa055aea53acfdbbfe24f9e6194";
const LIST_KEY = "rsvp:list";
const ATTENDS = ["一定到场", "可能到场", "遗憾缺席"];
const COUNTS = ["1人", "2人", "3人", "4人及以上"];

function corsHeaders(request) {
  var origin = request.headers.get("Origin") || "";
  var allowed = origin === "https://wzhuaboy.github.io" || origin.endsWith(".github.io") || origin.indexOf("http://localhost") === 0 || origin.indexOf("http://127.0.0.1") === 0;
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
async function sha256Hex(s) {
  var buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
}
function peopleOf(count) {
  if (count === "2人") return 2;
  if (count === "3人") return 3;
  if (count === "4人及以上") return 4;
  return 1;
}
function statsOf(list) {
  var s = { total: list.length, attending: 0, maybe: 0, absent: 0, people: 0, peopleMaybe: 0 };
  list.forEach(function (r) {
    if (r.attend === "一定到场") { s.attending++; s.people += peopleOf(r.count); }
    else if (r.attend === "可能到场") { s.maybe++; s.peopleMaybe += peopleOf(r.count); }
    else if (r.attend === "遗憾缺席") { s.absent++; }
  });
  return s;
}
async function loadList(env) {
  var raw = await env.RSVP_KV.get(LIST_KEY);
  if (!raw) return [];
  try { var v = JSON.parse(raw); return Array.isArray(v) ? v : []; } catch (e) { return []; }
}

export default {
  async fetch(request, env) {
    var url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(request) });
    }
    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "")) {
      return jsonResponse({ ok: true, service: "wedding-rsvp" }, 200, request);
    }
    // 客人提交回执：同名再提交会覆盖上一条，不会重复计数
    if (url.pathname === "/api/rsvp" && request.method === "POST") {
      var body = await request.json().catch(function () { return null; });
      if (!body || typeof body.name !== "string" || body.name.trim().length < 1 || body.name.trim().length > 20) {
        return jsonResponse({ ok: false, error: "bad name" }, 400, request);
      }
      if (ATTENDS.indexOf(body.attend) < 0 || COUNTS.indexOf(body.count) < 0) {
        return jsonResponse({ ok: false, error: "bad attend/count" }, 400, request);
      }
      if (typeof body.wish !== "string" || body.wish.length > 200) {
        return jsonResponse({ ok: false, error: "bad wish" }, 400, request);
      }
      var list = await loadList(env);
      if (list.length >= 500) {
        return jsonResponse({ ok: false, error: "list full" }, 400, request);
      }
      var rec = { name: body.name.trim(), attend: body.attend, count: body.count, wish: body.wish.trim(), ts: Date.now() };
      var idx = -1;
      for (var i = 0; i < list.length; i++) { if (list[i].name === rec.name) { idx = i; break; } }
      if (idx >= 0) list[idx] = rec; else list.push(rec);
      await env.RSVP_KV.put(LIST_KEY, JSON.stringify(list));
      return jsonResponse(Object.assign({ ok: true, updated: idx >= 0 }, statsOf(list)), 200, request);
    }
    // 公开统计：只有数字，没有名单，客人也能看
    if (url.pathname === "/api/stats" && request.method === "GET") {
      var sList = await loadList(env);
      return jsonResponse(Object.assign({ ok: true }, statsOf(sList)), 200, request);
    }
    // 查完整名单：要查看口令
    if (url.pathname === "/api/list" && request.method === "POST") {
      var lb = await request.json().catch(function () { return null; });
      if (!lb || typeof lb.key !== "string" || (await sha256Hex(lb.key)) !== ADMIN_KEY_HASH) {
        return jsonResponse({ ok: false, error: "wrong key" }, 401, request);
      }
      var lList = await loadList(env);
      lList.sort(function (a, b) { return b.ts - a.ts; });
      return jsonResponse(Object.assign({ ok: true, list: lList }, statsOf(lList)), 200, request);
    }
    // 删一条（测试数据、重名清理用）：要查看口令
    if (url.pathname === "/api/delete" && request.method === "POST") {
      var db = await request.json().catch(function () { return null; });
      if (!db || typeof db.key !== "string" || (await sha256Hex(db.key)) !== ADMIN_KEY_HASH || typeof db.name !== "string") {
        return jsonResponse({ ok: false, error: "wrong key" }, 401, request);
      }
      var dList = await loadList(env);
      var kept = dList.filter(function (r) { return r.name !== db.name; });
      await env.RSVP_KV.put(LIST_KEY, JSON.stringify(kept));
      return jsonResponse(Object.assign({ ok: true, removed: dList.length - kept.length }, statsOf(kept)), 200, request);
    }
    return jsonResponse({ ok: false, error: "not found" }, 404, request);
  },
};
