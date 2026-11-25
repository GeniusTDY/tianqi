/* 旧地图入口：在合并版中直接切换到 0.8 的十张旧地图 */
(function () {
  'use strict';

  var OLD_MAPS = [
    '冰雕广场', '遗迹区域', '部落林地', '回音海岸', '费尔村落',
    '机械废墟', '天空大陆', '雷鸣海滨', '艺术广场', '发明港口'
  ];
  var RETURN_MAP = '地图界面';

  var opened = false;
  var root, panel, toastEl, toastTimer = null, toggle;
  var shown = null;

  /* 这些不是实际游戏场景：登录、加载、过渡、战斗与测试布局 */
  var HIDDEN_LAYOUTS = {
    '入口': 1,
    '登录界面': 1,
    '数据载入界面': 1,
    '星球选择界面': 1,
    '加载界面': 1,
    '战斗进入前': 1,
    '战斗系统': 1,
    '测试场景': 1,
    '测试1': 1,
    '功能测试场景': 1
  };

  function getRuntime() {
    return window.xfruntime || window.xfgame || null;
  }

  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.style.opacity = '1';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.style.opacity = '0'; }, 2600);
  }

  function changeLayout(name) {
    var r = getRuntime();
    if (!r || !r.layouts) {
      toast('游戏还在加载，请稍候再试');
      return false;
    }
    if (!r.running_layout) {
      toast('请先进入游戏，再切换到旧地图');
      return false;
    }
    var layout = r.layouts[name];
    if (!layout) {
      toast('未找到地图：' + name);
      return false;
    }
    try {
      r.doChangeLayout(layout);
      closePanel();
      return true;
    } catch (e) {
      toast('切换失败：' + (e && e.message ? e.message : e));
      return false;
    }
  }

  function openPanel() {
    opened = true;
    panel.style.display = 'flex';
    toggle.textContent = '收起';
  }

  function closePanel() {
    opened = false;
    panel.style.display = 'none';
    toggle.textContent = '旧地图';
  }

  /*
   * 关键修复：
   * 原实现同时在 pointerdown / touchstart 上调用 preventDefault()，
   * 这会取消浏览器合成的 click 事件，导致按钮“能看见但点不动”。
   * 现在改为：按下只阻止冒泡，不 preventDefault；动作在 touchend / click 上触发，
   * 并用时间戳去重，兼容没有 PointerEvent 的旧 WebView。
   */
  function bindTap(el, fn) {
    var lastFire = 0;
    var startX = 0, startY = 0, moved = false;

    function fire(e) {
      var now = Date.now();
      if (now - lastFire < 350) return;
      lastFire = now;
      if (e) {
        if (e.cancelable) e.preventDefault();
        e.stopPropagation();
      }
      fn();
    }

    el.addEventListener('touchstart', function (e) {
      var t = e.changedTouches && e.changedTouches[0];
      if (t) { startX = t.clientX; startY = t.clientY; }
      moved = false;
      e.stopPropagation();
    }, { passive: true });

    el.addEventListener('touchmove', function (e) {
      var t = e.changedTouches && e.changedTouches[0];
      if (t && (Math.abs(t.clientX - startX) > 10 || Math.abs(t.clientY - startY) > 10)) {
        moved = true;
      }
    }, { passive: true });

    el.addEventListener('touchend', function (e) {
      e.stopPropagation();
      if (!moved) fire(e);
    }, { passive: false });

    /* 不 preventDefault，避免影响鼠标/触控笔产生的 click */
    el.addEventListener('pointerdown', function (e) { e.stopPropagation(); });

    el.addEventListener('click', function (e) { fire(e); });
  }

  function isInGame() {
    var r = getRuntime();
    if (!r || !r.running_layout) return false;
    var name = r.running_layout.name;
    if (!name && r.layouts) {
      for (var k in r.layouts) {
        if (r.layouts[k] === r.running_layout) { name = k; break; }
      }
    }
    if (!name) return false;
    return !HIDDEN_LAYOUTS[name];
  }

  function updateVisibility() {
    if (!root) return;
    var next = isInGame();
    if (next === shown) return;
    shown = next;
    if (next) {
      root.style.display = '';
      setTimeout(placeToggle, 0);
    } else {
      root.style.display = 'none';
      if (opened) closePanel();
    }
  }

  function build() {
    if (document.getElementById('oldmap-root')) return;

    root = document.createElement('div');
    root.id = 'oldmap-root';

    toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.id = 'oldmap-toggle';
    toggle.textContent = '旧地图';

    panel = document.createElement('div');
    panel.id = 'oldmap-panel';

    var title = document.createElement('div');
    title.className = 'oldmap-title';
    var titleText = document.createElement('span');
    titleText.textContent = '旧版地图';
    var titleCount = document.createElement('span');
    titleCount.className = 'oldmap-title-count';
    titleCount.textContent = '0.8 · 共 10 张';
    title.appendChild(titleText);
    title.appendChild(titleCount);
    panel.appendChild(title);

    var grid = document.createElement('div');
    grid.className = 'oldmap-grid';
    OLD_MAPS.forEach(function (name) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'oldmap-map-btn';
      b.textContent = name;
      bindTap(b, function () { changeLayout(name); });
      grid.appendChild(b);
    });
    panel.appendChild(grid);

    var back = document.createElement('button');
    back.type = 'button';
    back.className = 'oldmap-back-btn';
    back.textContent = '返回「地图界面」';
    bindTap(back, function () { changeLayout(RETURN_MAP); });
    panel.appendChild(back);

    var tip = document.createElement('div');
    tip.className = 'oldmap-tip';
    tip.textContent = '提示：先进入游戏再切换；旧地图与新版共用当前存档。';
    panel.appendChild(tip);

    toastEl = document.createElement('div');
    toastEl.className = 'oldmap-toast';
    document.body.appendChild(toastEl);

    bindTap(toggle, function () {
      if (opened) closePanel(); else openPanel();
    });

    root.appendChild(panel);
    root.appendChild(toggle);
    /* 只阻止冒泡，绝不 preventDefault，否则会连带取消内部按钮的 click */
    root.addEventListener('pointerdown', function (e) { e.stopPropagation(); });
    root.addEventListener('touchstart', function (e) { e.stopPropagation(); }, { passive: true });
    root.style.display = 'none';
    document.body.appendChild(root);
    updateVisibility();
    setInterval(updateVisibility, 250);
    setTimeout(placeToggle, 50);
    window.addEventListener('resize', placeToggle);
    setInterval(placeToggle, 1500);
  }

  /* 按钮水平居中于左侧星空留白带（屏幕左边缘到画布左边界之间），垂直保持屏幕中线 */
  function placeToggle() {
    if (!root || !toggle) return;
    var r = getRuntime();
    var c = (r && r.canvas) || document.querySelector('canvas');
    var band = 0;
    if (c && c.getBoundingClientRect) band = Math.max(0, c.getBoundingClientRect().left);
    var w = toggle.offsetWidth || 0;
    var x = band > w + 12 ? Math.round((band - w) / 2) : Math.max(2, Math.round(band - w - 6));
    root.style.left = x + 'px';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
