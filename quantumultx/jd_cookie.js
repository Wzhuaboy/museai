// jd_cookie.js - QuantumultX 京东 Cookie 快取
// 用法: QX 里订阅 quantumultx/jd_cookie.conf, 打开 https://bean.m.jd.com 点一次签到,
// 收到通知后点一下通知, pt_key + pt_pin 就写进剪贴板, 直接粘到青龙 JD_COOKIE.
// 原理: Safari 的 document.cookie 读不到 HttpOnly 的 pt_key/pt_pin, 所以书签那条路走不通,
// QX 在请求头里能看到完整 Cookie, 再用 $notify 的 update-pasteboard 点通知复制, 不用翻请求记录手动选.
// 触发: api.m.jd.com signBean / wq.jd.com GetJDUserInfoUnion, 只取 pt_key/pt_pin, 不发到任何地方.

function getCookie(headers) {
  if (!headers) return '';
  var keys = Object.keys(headers);
  for (var i = 0; i < keys.length; i++) {
    if (keys[i].toLowerCase() === 'cookie') return headers[keys[i]] || '';
  }
  return '';
}

var cookie = getCookie($request.headers);
var key = cookie.match(/pt_key=[^;]+/);
var pin = cookie.match(/pt_pin=[^;]+/);

if (key && pin) {
  var jdCookie = key[0] + ';' + pin[0] + ';';
  $prefs.setValueForKey(jdCookie, 'JD_COOKIE_QX');
  console.log('[JD Cookie] ' + jdCookie);
  $notify('京东Cookie已拿到', '点一下这条通知就复制好了', '直接去青龙 JD_COOKIE 粘贴，不用再翻QX请求记录', { 'update-pasteboard': jdCookie });
} else {
  console.log('[JD Cookie] no pt_key/pt_pin in this request');
  $notify('京东Cookie没取到', '', '这次请求里没有 pt_key/pt_pin，刷新一下京东页面再试一次');
}

$done({});
