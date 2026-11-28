/* TianQi 热补丁（由 index.html 内的加载器在启动后拉取）
 * 以后所有纯脚本层面的修复都写在这里，改完只需更新本文件，无需重新打 1.1GB 的安装包。
 * 约定：所有改动都要可重复执行（幂等），因为启动时可能多次运行。
 */
(function () {
  var V = '1';
  try {
    window.__TQ_PATCH__ = { v: V, at: new Date().toISOString() };
    if (window.console && console.log) console.log('[TQ] hot patch v' + V + ' loaded');
  } catch (e) {}

  /* 启动时短暂提示补丁版本，2 秒后自动消失；不需要时把下面整段删掉即可 */
  try {
    var d = document.createElement('div');
    d.textContent = '补丁 v' + V;
    d.style.cssText = 'position:fixed;right:8px;top:8px;z-index:999999;padding:2px 6px;' +
      'font:12px/1.4 sans-serif;color:#fff;background:rgba(0,0,0,.45);border-radius:4px;' +
      'pointer-events:none;opacity:.85;transition:opacity .6s';
    (document.body || document.documentElement).appendChild(d);
    setTimeout(function () {
      d.style.opacity = '0';
      setTimeout(function () { if (d.parentNode) d.parentNode.removeChild(d); }, 700);
    }, 1500);
  } catch (e) {}
})();
