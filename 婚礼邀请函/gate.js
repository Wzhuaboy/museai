// 婚礼邀请函开门验证：点链接先验证，名字对了才开。
// 名字只在服务器上比对，页面里没有正确答案；验证通过后这台设备不再重复验证。
// 验证前：遮罩不透光、请帖内容藏起来、底下页面锁住滑不动（遮罩自己可以滑）。
(function () {
  var API = "https://wedding-rsvp.wangzhanghua001023.workers.dev";
  var FLAG = "wedding_verified";
  var SIDE = "wedding_side";
  function $(id) { return document.getElementById(id); }
  var side = "";
  var verified = false;
  try { verified = sessionStorage.getItem(FLAG) === "1"; } catch (e) {}

  var wrap = document.querySelector(".wrap");
  function hideContent() { if (wrap) wrap.style.display = "none"; }
  function showContent() { if (wrap) wrap.style.display = ""; }

  // 锁住底下页面的滚动：手指在遮罩里可以滑，落在底下就拦住
  function blockBodyScroll(e) {
    var t = e.target;
    while (t) { if (t.id === "entry") return; t = t.parentElement; }
    e.preventDefault();
  }
  function lockScroll() {
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    document.addEventListener("touchmove", blockBodyScroll, { passive: false });
  }
  function unlockScroll() {
    document.body.style.overflow = "";
    document.documentElement.style.overflow = "";
    document.removeEventListener("touchmove", blockBodyScroll);
  }

  function showOpen() {
    var g = $("gateBox"); if (g) g.style.display = "none";
    var o = $("entryOpen"); if (o) o.style.display = "";
    showContent();
  }
  function showStep1() {
    var g = $("gateBox"); if (g) g.style.display = "";
    var s1 = $("gateStep1"); if (s1) s1.style.display = "";
    var s2 = $("gateStep2"); if (s2) s2.style.display = "none";
    var o = $("entryOpen"); if (o) o.style.display = "none";
  }
  function showStep2() {
    var s1 = $("gateStep1"); if (s1) s1.style.display = "none";
    var s2 = $("gateStep2"); if (s2) s2.style.display = "";
    var t = $("gateSideText");
    if (t) t.textContent = side === "groom" ? "你是新郎的朋友，请填写新郎和新娘的名字" : "你是新娘的朋友，请填写新郎和新娘的名字";
    var m = $("gateMsg"); if (m) m.textContent = "";
  }

  var btns = document.querySelectorAll("#gateStep1 button[data-side]");
  for (var i = 0; i < btns.length; i++) {
    btns[i].addEventListener("click", function () {
      side = this.getAttribute("data-side");
      showStep2();
    });
  }
  var back = $("gateBack");
  if (back) back.addEventListener("click", function (e) { e.preventDefault(); showStep1(); });

  function doVerify() {
    var vb = $("gateVerifyBtn");
    var msg = $("gateMsg");
    var g = $("gateGroom").value;
    var b = $("gateBride").value;
    if (!g.trim() || !b.trim()) { msg.textContent = "两个名字都要填。"; return; }
    vb.disabled = true;
    vb.textContent = "正在验证…";
    msg.textContent = "";
    fetch(API + "/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ side: side, groom: g, bride: b })
    })
      .then(function (r) { return r.json().then(function (d) { return { status: r.status, d: d }; }); })
      .then(function (res) {
        vb.disabled = false;
        vb.textContent = "验证并开启邀请函";
        if (res.status === 429) { msg.textContent = "试太多次了，等 10 分钟再试。"; return; }
        if (res.d && res.d.ok) {
          try { sessionStorage.setItem(FLAG, "1"); sessionStorage.setItem(SIDE, side); } catch (e) {}
          showOpen();
        } else {
          msg.textContent = "名字不对，再想想。";
        }
      })
      .catch(function () {
        vb.disabled = false;
        vb.textContent = "验证并开启邀请函";
        msg.textContent = "验证服务连不上，换个网络再试。";
      });
  }
  var vb2 = $("gateVerifyBtn");
  if (vb2) vb2.addEventListener("click", doVerify);
  ["gateGroom", "gateBride"].forEach(function (id) {
    var el = $(id);
    if (el) el.addEventListener("keydown", function (e) { if (e.key === "Enter") doVerify(); });
  });

  // 开场按钮一点，遮罩消失、请帖出现、滚动恢复
  var entryBtn = $("entryBtn");
  if (entryBtn) entryBtn.addEventListener("click", function () {
    unlockScroll();
    showContent();
  });

  // 初始状态：遮罩一起就锁滚动；没验证过先把请帖内容藏起来
  lockScroll();
  if (verified) showOpen(); else { hideContent(); showStep1(); }
})();
