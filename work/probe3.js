const { spawn } = require('child_process');
const fs = require('fs');

const CHROME = '/root/.cache/puppeteer/chrome/linux-155.0.8059.39/chrome-linux64/chrome';
const URL = process.argv[2] || 'http://127.0.0.1:8099/index.html';
const WAIT = parseInt(process.argv[3] || '45000', 10);
const TAG = process.argv[4] || 'run';

const args = [
  '--headless=new', '--remote-debugging-port=9223', '--no-sandbox',
  '--disable-dev-shm-usage', '--window-size=1400,900', '--mute-audio',
  '--enable-unsafe-swiftshader', '--use-angle=swiftshader',
  '--autoplay-policy=no-user-gesture-required',
  '--user-data-dir=/tmp/chromeprof3'
];
const proc = spawn(CHROME, args, { stdio: ['ignore', 'pipe', 'pipe'] });
proc.stderr.on('data', () => {});
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch('http://127.0.0.1:9223/json/version');
      return (await r.json()).webSocketDebuggerUrl;
    } catch (e) { await sleep(300); }
  }
  throw new Error('chrome not ready');
}

(async () => {
  const browserWs = await getWsUrl();
  const ws = new WebSocket(browserWs);
  let id = 0; const pending = new Map();
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
    const msgId = ++id; pending.set(msgId, { res, rej });
    ws.send(JSON.stringify({ id: msgId, method, params, sessionId }));
  });
  await new Promise(r => ws.addEventListener('open', r));
  const reqUrls = new Map();
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
      return;
    }
    if (m.method === 'Runtime.consoleAPICalled') {
      const txt = (m.params.args || []).map(a => a.value !== undefined ? a.value : a.description).join(' ');
      if (txt) console.log('CONSOLE:', txt.slice(0, 200));
    }
    if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      console.log('!! EXC:', (d.exception && (d.exception.description || d.exception.value)) || d.text);
    }
    if (m.method === 'Network.requestWillBeSent') reqUrls.set(m.params.requestId, m.params.request.url);
    if (m.method === 'Network.loadingFailed') {
      const u = reqUrls.get(m.params.requestId) || '';
      console.log('NETFAIL:', m.params.errorText, u.slice(-90));
    }
    if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) {
      console.log('HTTP', m.params.response.status, m.params.response.url.slice(-90));
    }
  });

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const S = (method, params) => send(method, params, sessionId);
  await S('Runtime.enable'); await S('Page.enable'); await S('Network.enable');

  await S('Page.addScriptToEvaluateOnNewDocument', {
    source: `window.__alerts=[];window.alert=function(m){window.__alerts.push(String(m));};`
  });

  const t0 = Date.now();
  await S('Page.navigate', { url: URL });
  const evals = [];
  while (Date.now() - t0 < WAIT) {
    await sleep(2000);
    const secs = Math.round((Date.now() - t0) / 1000);
    try {
      const r = await S('Runtime.evaluate', {
        expression: `(function(){try{var rt=window.xfruntime;return JSON.stringify({sec:${secs},layout:rt&&rt.running_layout&&rt.running_layout.name,loading:rt&&rt.isXfLoading,progress:rt&&Math.round(rt.progress||0),canvas:!!(rt&&rt.canvas),cw:rt&&rt.canvas&&rt.canvas.width,alerts:(window.__alerts||[]).length});}catch(e){return 'ERR '+e.message}})()`,
        returnByValue: true
      });
      console.log('STATE', r.result.value);
    } catch (e) { console.log('eval err', e.message); }
  }
  try {
    const r = await S('Runtime.evaluate', { expression: `JSON.stringify(window.__alerts||[])`, returnByValue: true });
    console.log('ALERTS:', r.result.value);
    const shot = await S('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`/workspace/work/${TAG}.png`, Buffer.from(shot.data, 'base64'));
  } catch (e) {}
  proc.kill();
  process.exit(0);
})().catch(e => { console.error(e); proc.kill(); process.exit(1); });
