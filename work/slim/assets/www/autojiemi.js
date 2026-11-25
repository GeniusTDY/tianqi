/**
 * autojiemi.js - 资源保护解密器 v6.0 (大文件优化 & 进度控制版)
 * 说明：
 * 1. 解密算法未做任何修改。
 * 2. 增加了图片缓存上限（默认100张），防止大项目内存溢出（OOM）。
 * 3. 增加了全局日志开关，方便调试和正式发布。
 * 4. 增加了进度检测，加载 100% 后自动从内存中卸载拦截器。
 */
(function() {
    'use strict';

    // ============================================================
    // 0. 全局配置
    // ============================================================
    // 控制台日志开关：true = 开启，false = 关闭（发布时改成 false）
    var DEBUG_MODE = false; 
    
    // 图片解密缓存上限：超过这个数量，自动清理最早的缓存，释放内存
    var MAX_CACHE_SIZE = 100; 

    // 当前包内资源均为明文（WebP/JSON），跳过图片 Blob 代理，直接交给原生图片缓存
    var PLAIN_ASSETS = true; 

    // 统一的日志输出函数
    function log() {
        if (DEBUG_MODE) {
            var args = Array.prototype.slice.call(arguments);
            args.unshift('[解密器]');
            console.log.apply(console, args);
        }
    }

    // ============================================================
    // 1. 固定密钥 (21位) —— 【绝对不动的解密算法】
    // ============================================================
    var POOL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

    var FIXED_KEY = 
        POOL.charAt(23) + POOL.charAt(36) + POOL.charAt(61) +
        POOL.charAt(38) + POOL.charAt(15) + POOL.charAt(54) +
        POOL.charAt(48) + POOL.charAt(17) + POOL.charAt(59) +
        POOL.charAt(47) + POOL.charAt(11) + POOL.charAt(57) +
        POOL.charAt(42) + POOL.charAt(13) + POOL.charAt(60) +
        POOL.charAt(42) + POOL.charAt(13) + POOL.charAt(60) +
        POOL.charAt(11) + POOL.charAt(57) + POOL.charAt(42);

    // ============================================================
    // 2. 工具函数 —— 【绝对不动的解密算法】
    // ============================================================
    function getAppId() {
        try {
            if (window.xfConfig && window.xfConfig.appId) {
                return window.xfConfig.appId;
            }
            return null;
        } catch (e) {
            return null;
        }
    }

    function hashString(str, len) {
        var hash = 0;
        for (var i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash = hash & hash;
        }
        return String(Math.abs(hash) % Math.pow(10, len)).padStart(len, '0');
    }

    function getDataJsonPassword() {
        var appId = getAppId();
        if (!appId) return FIXED_KEY + '0000';
        return FIXED_KEY + hashString(appId, 4);
    }

    function getImageKeyFromUrl(url) {
        var filename = url.split('/').pop().split('?')[0];
        return FIXED_KEY + hashString(filename, 4);
    }

    function isZipFile(buffer) {
        try {
            var v = new Uint8Array(buffer);
            return v.length > 4 && v[0] === 0x50 && v[1] === 0x4B && 
                   v[2] === 0x03 && v[3] === 0x04;
        } catch (e) {
            return false;
        }
    }

    function isImageEncrypted(buffer) {
        try {
            var bytes = new Uint8Array(buffer);
            if (bytes.length < 4) return false;
            return bytes[0] === 0x49 && bytes[1] === 0x49 && 
                   bytes[2] === 0x2A && bytes[3] === 0x00;
        } catch (e) {
            return false;
        }
    }

    function decryptImageBuffer(buffer, url) {
        var bytes = new Uint8Array(buffer);
        if (!isImageEncrypted(buffer)) return buffer;

        var originalSize = bytes.length - 4;
        var key = getImageKeyFromUrl(url);

        var data = new Uint8Array(originalSize);
        for (var i = 0; i < originalSize; i++) {
            data[i] = bytes[i + 4];
        }

        var keyBytes = new TextEncoder().encode(key);
        var keyLen = keyBytes.length;
        var encryptLen = Math.min(1024, originalSize);
        for (var i = 0; i < encryptLen; i++) {
            data[i] = data[i] ^ keyBytes[i % keyLen];
        }

        return data;
    }

    // ============================================================
    // 3. 解密 data.json —— 【绝对不动的解密算法】
    // ============================================================
    var decryptedData = null;
    var dataDecryptPromise = null;

    function decryptDataJson() {
        if (dataDecryptPromise) return dataDecryptPromise;
        if (decryptedData) return Promise.resolve(decryptedData);

        dataDecryptPromise = new Promise(function(resolve, reject) {
            fetch('data.json')
                .then(function(res) {
                    if (!res.ok) throw new Error();
                    return res.arrayBuffer();
                })
                .then(function(buffer) {
                    if (isZipFile(buffer)) {
                        var password = getDataJsonPassword();
                        if (typeof JSZip === 'undefined') {
                            try {
                                var jsonStr = new TextDecoder().decode(buffer);
                                decryptedData = JSON.parse(jsonStr);
                                log('data.json 解密成功（无JSZip，按明文解析）');
                                resolve(decryptedData);
                                return;
                            } catch (e) {
                                log('data.json 明文解析失败');
                                reject();
                                return;
                            }
                        }

                        var zip = new JSZip();
                        zip.loadAsync(buffer, { password: password })
                            .then(function(zip) {
                                var file = zip.file('data.json');
                                if (!file) {
                                    var files = zip.files;
                                    var firstFile = null;
                                    for (var name in files) {
                                        if (!files[name].dir) {
                                            firstFile = name;
                                            break;
                                        }
                                    }
                                    if (!firstFile) throw new Error();
                                    return zip.file(firstFile).async('string');
                                }
                                return file.async('string');
                            })
                            .then(function(jsonStr) {
                                decryptedData = JSON.parse(jsonStr);
                                log('data.json 解密成功（ZIP解压）');
                                resolve(decryptedData);
                            })
                            .catch(function() { 
                                log('data.json ZIP解密失败');
                                reject(); 
                            });
                    } else {
                        try {
                            // 明文包：直接把原文交给运行时解析，避免二次 parse + stringify
                            var jsonStr = new TextDecoder().decode(buffer);
                            decryptedData = jsonStr;
                            log('data.json 明文读取成功');
                            resolve(decryptedData);
                        } catch (e) {
                            log('data.json 明文读取失败');
                            reject();
                        }
                    }
                })
                .catch(function() { 
                    log('data.json 请求失败');
                    reject(); 
                });
        });

        return dataDecryptPromise;
    }

    // ============================================================
    // 4. XHR 拦截与响应模拟 —— 【绝对不动的解密算法】
    // ============================================================
    function setXHRResponse(self, data, isJson) {
        try {
            Object.defineProperty(self, 'status', { value: 200, writable: false, configurable: true });
            Object.defineProperty(self, 'statusText', { value: 'OK', writable: false, configurable: true });
            Object.defineProperty(self, 'readyState', { value: 4, writable: false, configurable: true });
            
            if (isJson) {
                var text = (typeof data === 'string') ? data : JSON.stringify(data);
                Object.defineProperty(self, 'response', { value: text, writable: false, configurable: true });
                Object.defineProperty(self, 'responseText', { value: text, writable: false, configurable: true });
            } else {
                Object.defineProperty(self, 'response', { value: data, writable: false, configurable: true });
            }

            if (self.onload) { try { self.onload.call(self); } catch (e) {} }
            if (self.onreadystatechange) { try { self.onreadystatechange.call(self); } catch (e) {} }
        } catch (e) {}
    }

    var _originalOpen = XMLHttpRequest.prototype.open;
    var _originalSend = XMLHttpRequest.prototype.send;
    var _originalImage = window.Image;
    var _originalSrcDescriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
    var _isHooked = false;
    var isActive = true;

    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        this._url = url;
        if (isActive && url && typeof url === 'string') {
            if (url.indexOf('data.json') !== -1 || url.indexOf('data.enc') !== -1) {
                this._requestType = 'datajson';
            } else if (url.indexOf('assets/images/') !== -1 || url.match(/\.(png|jpg|jpeg|gif|webp|bmp)/i)) {
                this._requestType = 'gameimage';
            } else {
                this._requestType = 'other';
            }
        }
        return _originalOpen.call(this, method, url, async !== false, user, password);
    };

    XMLHttpRequest.prototype.send = function(body) {
        var self = this;
        var type = self._requestType;

        if (type === 'datajson' && isActive) {
            decryptDataJson()
                .then(function(data) { setXHRResponse(self, data, true); })
                .catch(function() { _originalSend.call(self, body); });
            return;
        }

        if (type === 'gameimage' && isActive) {
            var originalOnReadyStateChange = self.onreadystatechange;
            self.onreadystatechange = function() {
                if (self.readyState === 4) {
                    if (originalOnReadyStateChange) {
                        try { originalOnReadyStateChange.apply(self, arguments); } catch (e) {}
                    }
                    try {
                        if (self.status === 200 && self.response) {
                            var responseData = self.response;
                            var url = self._url;
                            if (responseData instanceof ArrayBuffer) {
                                if (isImageEncrypted(responseData)) {
                                    var decrypted = decryptImageBuffer(responseData, url);
                                    var blob = new Blob([decrypted], { type: 'image/png' });
                                    Object.defineProperty(self, 'response', { value: blob, writable: false, configurable: true });
                                }
                            } else if (responseData instanceof Blob) {
                                responseData.arrayBuffer().then(function(buffer) {
                                    if (isImageEncrypted(buffer)) {
                                        var decrypted = decryptImageBuffer(buffer, url);
                                        var blob = new Blob([decrypted], { type: 'image/png' });
                                        Object.defineProperty(self, 'response', { value: blob, writable: false, configurable: true });
                                    }
                                });
                            }
                        }
                    } catch (e) {}
                }
            };
        }
        return _originalSend.call(this, body);
    };

    // ============================================================
    // 5. Image 拦截与缓存优化 (重点：LRU 机制防止内存爆炸)
    // ============================================================
    var imageBlobCache = new Map();

    if (_originalSrcDescriptor && !PLAIN_ASSETS) {
        _isHooked = true;

        window.Image = function(width, height) {
            var img = new _originalImage(width, height);
            var _imgOriginalSetter = _originalSrcDescriptor.set;
            
            Object.defineProperty(img, 'src', {
                get: function() { return this._src || ''; },
                set: function(url) {
                    this._src = url;
                    
                    if (isActive && url && typeof url === 'string' && 
                        (url.indexOf('assets/images/') !== -1 || url.match(/\.(png|jpg|jpeg|gif|webp|bmp)/i))) {
                        
                        // 【缓存命中】如果存在缓存，直接使用并更新它在Map中的最新位置（LRU）
                        if (imageBlobCache.has(url)) {
                            var cachedUrl = imageBlobCache.get(url);
                            imageBlobCache.delete(url);
                            imageBlobCache.set(url, cachedUrl); // 重新放回末尾，标记为最新使用
                            _imgOriginalSetter.call(img, cachedUrl);
                            return;
                        }
                        
                        fetch(url)
                            .then(function(res) { 
                                if (!res.ok) throw new Error();
                                return res.arrayBuffer(); 
                            })
                            .then(function(buffer) {
                                var resultBuffer = buffer;
                                var mimeType = 'image/png';
                                
                                if (isImageEncrypted(buffer)) {
                                    resultBuffer = decryptImageBuffer(buffer, url);
                                    mimeType = 'image/png';
                                } else {
                                    var bytes = new Uint8Array(buffer);
                                    if (bytes[0] === 0xFF && bytes[1] === 0xD8) mimeType = 'image/jpeg';
                                    else if (bytes[0] === 0x89 && bytes[1] === 0x50) mimeType = 'image/png';
                                    else if (bytes[0] === 0x47 && bytes[1] === 0x49) mimeType = 'image/gif';
                                    else if (bytes[0] === 0x52 && bytes[1] === 0x49) mimeType = 'image/webp';
                                }
                                
                                var blob = new Blob([resultBuffer], { type: mimeType });
                                var blobUrl = URL.createObjectURL(blob);
                                
                                // 【缓存超限清理】当缓存达到上限，剔除最旧的一个，并释放内存
                                if (imageBlobCache.size >= MAX_CACHE_SIZE) {
                                    var oldestUrl = imageBlobCache.keys().next().value;
                                    var oldBlobUrl = imageBlobCache.get(oldestUrl);
                                    try { URL.revokeObjectURL(oldBlobUrl); } catch (e) {}
                                    imageBlobCache.delete(oldestUrl);
                                    log('缓存已满，自动释放内存：' + oldestUrl);
                                }
                                
                                imageBlobCache.set(url, blobUrl);
                                _imgOriginalSetter.call(img, blobUrl);
                            })
                            .catch(function() {
                                _imgOriginalSetter.call(img, url);
                            });
                    } else {
                        _imgOriginalSetter.call(this, url);
                    }
                },
                configurable: true
            });
            return img;
        };
        window.Image.prototype = _originalImage.prototype;
    }

    // ============================================================
    // 6. 预解密 data.json
    // ============================================================
    decryptDataJson().catch(function() {});

    // ============================================================
    // 7. 自动修复 xfStartLoad 进度（原版逻辑，保留）
    // ============================================================
    function wait(fn) {
        var i = setInterval(function() {
            if (window.xfruntime && window.xfruntime.xfStartLoad) {
                clearInterval(i);
                fn();
            }
        }, 50);
        setTimeout(function() { clearInterval(i); }, 10000);
    }

    function fixXfStartLoad() {
        var r = window.xfruntime;
        if (!r || !r.xfStartLoad) return;

        var originalStartLoad = r.xfStartLoad.bind(r);
        r.xfStartLoad = function() {
            var self = this;
            if (!self.xfPreloadGroup || !self.xfPreloadGroup.startLoad) {
                return originalStartLoad();
            }
            self.isXfLoading = true;
            return self.xfPreloadGroup.startLoad({
                onProgress: function(total, loaded) {
                    self.progress = (loaded / total) * 100;
                    self.completedsize = loaded;
                    self.totalsize = total;
                }
            }).then(function() {
                self.progress = 100;
                self.isXfLoading = false;
            }).catch(function(e) {
                self.isXfLoading = false;
                self.progress = 100;
                return Promise.resolve();
            });
        };
    }
    wait(fixXfStartLoad);

    // ============================================================
    // 8. 加载完成后的自我销毁机制 (内存卸载)
    // ============================================================
    function selfDestruct() {
        if (!isActive) return;
        isActive = false;

        XMLHttpRequest.prototype.open = _originalOpen;
        XMLHttpRequest.prototype.send = _originalSend;

        if (_isHooked && _originalSrcDescriptor) {
            window.Image = _originalImage;
        }

        for (var entry of imageBlobCache.values()) {
            try { URL.revokeObjectURL(entry); } catch (e) {}
        }
        imageBlobCache.clear();

        decryptedData = null;
        dataDecryptPromise = null;
        log('所有资源加载完毕，解密器已从内存中安全卸载。');
    }

    // 监听进度，达到 100% 后自动销毁（兼容不同的进度变量）
    var loadCheck = setInterval(function() {
        var progress = 0;
        if (window.xfruntime && window.xfruntime.progress) {
            progress = window.xfruntime.progress;
        } else if (window.gameLoadProgress) {
            progress = window.gameLoadProgress;
        } else if (window.appProgress) { // 兼容你主 APP 里的进度提示
            progress = window.appProgress;
        }

        if (progress >= 100) {
            clearInterval(loadCheck);
            // 延迟 2 秒再销毁，确保最后一张图片已完成解密渲染
            setTimeout(function() {
                selfDestruct();
            }, 2000);
        }
    }, 1000);

    // 安全兜底：如果一直检测不到进度，改为 10 分钟(600000毫秒)后自动卸载，防止内存一直被占用
    setTimeout(function() {
        if (isActive) {
            clearInterval(loadCheck);
            selfDestruct();
            log('触发安全兜底，解密器已卸载。');
        }
    }, 600000);

    // 最后一道防线：页面关闭/刷新时彻底清理内存
    window.addEventListener('beforeunload', function() {
        if (isActive) selfDestruct();
    });

})();