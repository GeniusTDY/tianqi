// ============================================================
// Spine 速度控制修复补丁 - 正式版
// 修复 set-rate 动作调用 SetRate 但函数为空的问题
// ============================================================

(function() {
    'use strict';
    
    // ============================================================
    // 查找所有 Spine 实例（只保留有效的方法）
    // ============================================================
    function findAllSpineInstances() {
        var instances = [];
        var found = {};
        
        // ★ 实际生效的方法：通过 drama.plugins_.xfSpine.instances
        if (window.drama && window.drama.plugins_ && window.drama.plugins_.xfSpine) {
            var plugin = window.drama.plugins_.xfSpine;
            if (plugin.instances) {
                for (var k = 0; k < plugin.instances.length; k++) {
                    var inst = plugin.instances[k];
                    if (inst && inst.skeletonInfo && !found[inst.uid]) {
                        instances.push(inst);
                        found[inst.uid] = true;
                    }
                }
            }
        }
        
        // 备用：通过 window.aa（如果存在）
        if (window.aa && window.aa.skeletonInfo && !found[window.aa.uid]) {
            instances.push(window.aa);
            found[window.aa.uid] = true;
        }
        
        return instances;
    }
    
    // ============================================================
    // 等待 drama 和 xfSpine 插件加载完成
    // ============================================================
    function waitForDrama(attempts) {
        attempts = attempts || 0;
        
        if (attempts > 50) {
            return;
        }
        
        if (typeof window.drama === 'undefined') {
            setTimeout(function() { waitForDrama(attempts + 1); }, 200);
            return;
        }
        
        var spinePlugin = window.drama.plugins_ && window.drama.plugins_.xfSpine;
        if (!spinePlugin) {
            setTimeout(function() { waitForDrama(attempts + 1); }, 200);
            return;
        }
        
        applyFix(spinePlugin);
    }
    
    // ============================================================
    // 应用补丁
    // ============================================================
    function applyFix(spinePlugin) {
        var proto = spinePlugin.prototype;
        var acts = proto.acts || {};
        
        // ============================================================
        // SetRate 函数 - 接收事件传递的参数
        // ============================================================
        acts.SetRate = function(rate) {
            var speed = parseFloat(rate);
            if (isNaN(speed)) {
                speed = 1.0;
            }
            
            if (this.skeletonInfo && this.skeletonInfo.state) {
                this.skeletonInfo.state.timeScale = speed;
                return true;
            }
            return false;
        };
        
        proto.SetRate = acts.SetRate;
        
        // 添加到 actions（如果存在）
        if (spinePlugin.actions) {
            spinePlugin.actions.SetRate = acts.SetRate;
        }
        
        // 为现有实例添加 SetRate 方法
        var instances = findAllSpineInstances();
        instances.forEach(function(inst) {
            if (inst && !inst.SetRate) {
                inst.SetRate = acts.SetRate;
            }
        });
        
        // 全局快捷函数
        window.SetRate = function(rate) {
            var speed = parseFloat(rate);
            if (isNaN(speed)) {
                speed = 1.0;
            }
            
            var allInstances = findAllSpineInstances();
            var success = false;
            
            allInstances.forEach(function(inst) {
                if (inst && inst.SetRate) {
                    success = inst.SetRate(speed) || success;
                } else if (inst && inst.skeletonInfo && inst.skeletonInfo.state) {
                    inst.skeletonInfo.state.timeScale = speed;
                    success = true;
                }
            });
            
            return success;
        };
        
        // 劫持 onCreate，确保新实例也有 SetRate
        var originalOnCreate = proto.onCreate;
        proto.onCreate = function() {
            if (originalOnCreate) {
                originalOnCreate.call(this);
            }
            if (!this.SetRate) {
                this.SetRate = acts.SetRate;
            }
        };
    }
    
    // 启动
    waitForDrama();
    
})();