(function waitRuntime(){
    var rt = window.xfruntime || window._C2_rt;

    // 双保险：万一 xfruntime 还没有，再等
    if (!rt || !rt.types || !rt.objectsByUid) {
        setTimeout(waitRuntime, 500);
        return;
    }

    window._C2_rt = rt;
    console.log('AI版已就绪');
})();