/* TianQi 热补丁（由 index.html 内的加载器在启动后拉取）
 * 以后所有纯脚本层面的修复都写在这里，改完只需更新本文件，无需重新打 1.1GB 的安装包。
 * 约定：所有改动都要可重复执行（幂等），因为启动时可能多次运行。
 */
(function () {
  try {
    window.__TQ_PATCH__ = { v: '1', at: new Date().toISOString() };
    if (window.console && console.log) console.log('[TQ] hot patch v1 loaded');
  } catch (e) {}
})();
