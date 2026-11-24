// eleme_ck.js - QX 抓饿了么 CK，点通知复制到剪贴板
// 配合 iOS 快捷指令「复制饿了么CK」使用
// 抓包规则（QX 重写），四条都要加：
// ^https://waimai-guide\.ele\.me/ url script-request-header https://wzhuaboy.github.io/museai/eleme/eleme_ck.js
// ^https://waimai-guide\.ele\.me/ url script-response-header https://wzhuaboy.github.io/museai/eleme/eleme_ck.js
// ^https://acs\.ele\.me/ url script-request-header https://wzhuaboy.github.io/museai/eleme/eleme_ck.js
// ^https://acs\.ele\.me/ url script-response-header https://wzhuaboy.github.io/museai/eleme/eleme_ck.js
//
// 原理：只取登录必需的几个字段拼成精简 CK（cookie2/SID/USERID/_m_h5_tk/munb/UTUSER/sgcookie），
// 完整 Cookie 太长，塞不进快捷指令的 URL；幸运星2.js 跑起来后会从响应 Set-Cookie 里自动补全其余字段。
// 请求头里的 Cookie 是当前登录态；响应 Set-Cookie 里会下发新的 _m_h5_tk，合并时响应优先。

function extract(str) {
  const out = {};
  if (!str) return out;
  const fields = ['cookie2', 'SID', 'USERID', '_m_h5_tk', 'munb', 'UTUSER', 'sgcookie', 'unb'];
  for (const f of fields) {
    const m = str.match(new RegExp('(?:^|;\\s*)' + f + '=([^;]+)'));
    if (m && m[1]) out[f] = m[1];
  }
  return out;
}

let reqFields = {};
let resFields = {};
try {
  if (typeof $request !== 'undefined' && $request && $request.headers) {
    const c = $request.headers['Cookie'] || $request.headers['cookie'] || '';
    reqFields = extract(c);
  }
} catch (e) {}
try {
  if (typeof $response !== 'undefined' && $response && $response.headers) {
    const h = $response.headers;
    let sc = h['Set-Cookie'] || h['set-cookie'] || '';
    if (Array.isArray(sc)) sc = sc.join('; ');
    resFields = extract(sc);
  }
} catch (e) {}

// 合并：响应里的新值优先（主要是 _m_h5_tk 刷新），其余用请求里的
const merged = Object.assign({}, reqFields, resFields);
const order = ['cookie2', 'SID', 'USERID', '_m_h5_tk', 'munb', 'UTUSER', 'sgcookie', 'unb'];
let ck = '';
if (merged.cookie2 && merged.SID && merged.USERID) {
  ck = order.filter((k) => merged[k]).map((k) => k + '=' + merged[k]).join('; ') + ';';
}

if (ck) {
  const now = Date.now();
  const lastTime = parseInt($prefs.valueForKey('elm_ck_last_notify') || '0', 10);
  const lastCk = $prefs.valueForKey('elm_ck_last_value') || '';
  // CK 变了立即通知（不被 30 秒节流挡住）；CK 没变则 30 秒内只通知一次。
  if (ck !== lastCk || now - lastTime > 30000) {
    $prefs.setValueForKey(String(now), 'elm_ck_last_notify');
    $prefs.setValueForKey(ck, 'elm_ck_last_value');
    const url = 'shortcuts://run-shortcut?name=' + encodeURIComponent('复制饿了么CK') + '&input=' + encodeURIComponent(ck);
    $notify('饿了么 CK 已抓到', '点一下复制到剪贴板', ck, { 'open-url': url });
  }
}

$done({});
