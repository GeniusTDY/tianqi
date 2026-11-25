const { spawn } = require('child_process');
const fs = require('fs');
const CHROME = '/root/.cache/puppeteer/chrome/linux-155.0.8059.39/chrome-linux64/chrome';
const URL = process.argv[2] || 'http://127.0.0.1:8099/index.html';
const WAIT = parseInt(process.argv[3] || '30000', 10);
const proc = spawn(CHROME, ['--headless=new','--remote-debugging-port=9223','--no-sandbox','--disable-dev-shm-usage','--window-size=1300,760','--mute-audio','--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-proxy-server','--proxy-bypass-list=*','--user-data-dir=/tmp/chromeprof2'], { stdio: ['ignore','pipe','pipe'] });
proc.stderr.on('data', () => {});
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  let wsUrl;
  for (let i=0;i<40;i++){ try{ const r=await fetch('http://127.0.0.1:9223/json/version'); wsUrl=(await r.json()).webSocketDebuggerUrl; break;}catch(e){await sleep(300);} }
  const ws = new WebSocket(wsUrl); let id=0; const pending=new Map();
  const send=(m,p={},s)=>new Promise((res,rej)=>{const i=++id;pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method:m,params:p,sessionId:s}));});
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data);
    if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}
    else if(m.method==='Page.javascriptDialogOpening'){console.log('DIALOG:',JSON.stringify(m.params.message).slice(0,300));send('Page.handleJavaScriptDialog',{accept:true},m.sessionId).catch(()=>{});}
    else if(m.method==='Runtime.exceptionThrown'){const d=m.params.exceptionDetails;console.log('EXC:',((d.exception&&(d.exception.description||d.exception.value))||d.text||'').split('\n').slice(0,4).join(' | '));}
    else if(m.method==='Runtime.consoleAPICalled'){const t=(m.params.args||[]).map(a=>a.value!==undefined?a.value:a.description).join(' ');console.log('C['+m.params.type+']:',t.slice(0,400));}
    else if(m.method==='Log.entryAdded'){console.log('LOG['+m.params.entry.level+']:',m.params.entry.text.slice(0,300), m.params.entry.url||'');}
  });
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const S=(m,p)=>send(m,p,sessionId);
  await S('Runtime.enable'); await S('Page.enable'); await S('Log.enable'); await S('Network.enable');
  await S('Page.navigate',{url:URL});
  const t0=Date.now(); let shot=0;
  while(Date.now()-t0<WAIT){
    await sleep(2000); const s=Math.round((Date.now()-t0)/1000);
    const r=await S('Runtime.evaluate',{expression:`JSON.stringify({rs:document.readyState,rt:typeof window.xfruntime,rtv:window.xfruntime?{layout:window.xfruntime.running_layout&&window.xfruntime.running_layout.name,prog:Math.round(window.xfruntime.progress||0),loading:window.xfruntime.isloading,canvas:!!window.xfruntime.canvas}:null,cordova:typeof window.cordova,dev:!!window.cordova&&!!window.cordova.platformId,scripts:document.scripts.length,bodyChildren:document.body.children.length})`,returnByValue:true}).catch(e=>({result:{value:'EVALERR '+e.message}}));
    console.log(`[${s}s]`, r.result.value);
    if(shot<3){ const sh=await S('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(`/workspace/work/p2_${s}.png`, Buffer.from(sh.data,'base64')); shot++; }
  }
  proc.kill(); process.exit(0);
})().catch(e=>{console.error(e);proc.kill();process.exit(1);});
