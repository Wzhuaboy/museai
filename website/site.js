// 小站公共渲染逻辑：从 projects.json 读数据，首页和分区页都按它生成。
// 项目数是算出来的，改了 projects.json 就自动对上，不用手动改数字。
(function () {
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function projectCard(p, color) {
    var tag = p.tag ? ' <span class="tag">' + esc(p.tag) + "</span>" : "";
    var body = "<h2>" + esc(p.name) + tag + "</h2><p>" + esc(p.desc) + "</p>";
    if (p.url) {
      body += '<div class="go">' + esc(p.action || "访问") + " →</div>";
      return '<a class="proj" href="' + esc(p.url) + '" target="_blank" rel="noopener" style="border-left-color:' + color + '">' + body + "</a>";
    }
    return '<div class="proj" style="border-left-color:' + color + '">' + body + "</div>";
  }

  function renderIndex(data) {
    var grid = document.getElementById("sections");
    if (!grid) return;
    var html = "";
    data.sections.forEach(function (s) {
      var n = data.projects.filter(function (p) { return p.section === s.id && p.visible; }).length;
      html += '<a class="card" style="--ac:' + s.color + '" href="' + s.id + '.html">'
        + "<h2>" + esc(s.name) + '<span class="n">' + n + " 个项目</span></h2>"
        + "<p>" + esc(s.desc) + "</p>"
        + '<div class="go">进入 →</div></a>';
    });
    grid.innerHTML = html;
  }

  function renderSection(data, sectionId) {
    var box = document.getElementById("projects");
    if (!box) return;
    var sec = null;
    data.sections.forEach(function (s) { if (s.id === sectionId) sec = s; });
    if (!sec) { box.innerHTML = "<p>没有这个分区。</p>"; return; }
    var list = data.projects.filter(function (p) { return p.section === sectionId && p.visible; });
    if (!list.length) { box.innerHTML = "<p>这个分区暂时没有同步的项目，去管理页打开几个吧。</p>"; return; }
    var html = "";
    list.forEach(function (p) { html += projectCard(p, sec.color); });
    box.innerHTML = html;
  }

  function fail(msg) {
    var box = document.getElementById("sections") || document.getElementById("projects");
    if (box) box.innerHTML = "<p>" + esc(msg) + "</p>";
  }

  fetch("projects.json")
    .then(function (r) { if (!r.ok) throw new Error("projects.json 打不开"); return r.json(); })
    .then(function (data) {
      var page = document.body.getAttribute("data-page") || "index";
      if (page === "index") renderIndex(data);
      else renderSection(data, page);
    })
    .catch(function () { fail("项目列表打不开，刷新一下试试。"); });
})();
