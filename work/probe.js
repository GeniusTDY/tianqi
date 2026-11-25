const { spawn } = require('child_process');
const fs = require('fs');

const CHROME = '/root/.cache/puppeteer/chrome/linux-155.0.8059.39/chrome-linux64/chrome';
const URL = process.argv[2] || 'http://127.0.0.1:8099/index.html';
const WAIT = parseInt(process.argv[3] || '45000', 10);

const args = [
  '--headless=new', '--remote-debugging-port=9222', '--no-sandbox',
  '--disable-dev-shm-usage', '--window-size=1400,900', '--mute-audio',
  '--enable-unsafe-swiftshader', '--use-angle=swiftshader',
  '--autoplay-policy=no-user-gesture-required','--proxy-server=http://127.0.0.1:18080','--proxy-bypass-list=127.0.0.1;localhost',
  '--user-data-dir=/tmp/chromeprof'
];
const proc = spawn(CHROME, args, { stdio: ['ignore', 'pipe', 'pipe'] });
proc.stderr.on('data', () => {});

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch('http://127.0.0.1:9222/json/version');
      const j = await r.json();
      return j.webSocketDebuggerUrl;
    } catch (e) { await sleep(300); }
  }
  throw new Error('chrome not ready');
}

(async () => {
  const browserWs = await getWsUrl();
  const ws = new WebSocket(browserWs);
  let id = 0;
  const pending = new Map();
  const events = [];
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
    const msgId = ++id;
    pending.set(msgId, { res, rej });
    ws.send(JSON.stringify({ id: msgId, method, params, sessionId }));
  });
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
    } else if (m.method) events.push(m);
  });

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const S = (method, params) => send(method, params, sessionId);

  await S('Runtime.enable');
  await S('Log.enable');
  await S('Page.enable');
  await S('Network.enable');

  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.method === 'Page.javascriptDialogOpening') {
      console.log('!! DIALOG:', m.params.message.replace(/\s+/g, ' '));
      S('Page.handleJavaScriptDialog', { accept: true }).catch(() => {});
    }
    if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      console.log('!! EXC:', (d.exception && (d.exception.description || d.exception.value)) || d.text);
    }
    if (m.method === 'Runtime.consoleAPICalled') {
      const txt = (m.params.args || []).map(a => a.value !== undefined ? a.value : a.description).join(' ');
      if (/(error|fail|失败|Error)/i.test(txt)) console.log('CONSOLE[' + m.params.type + ']:', txt.slice(0, 300));
    }
    if (m.method === 'Log.entryAdded') {
      const e = m.params.entry;
      if (e.level === 'error') console.log('LOG:', e.text.slice(0, 200), e.url || '');
    }
    if (m.method === 'Network.loadingFailed') {
      console.log('NETFAIL:', m.params.errorText, m.params.requestId);
    }
    if (m.method === 'Network.requestWillBeSent') {
      global._reqs = global._reqs || {};
      global._reqs[m.params.requestId] = m.params.request.url;
    }
    if (m.method === 'Network.responseReceived') {
      const r = m.params.response;
      if (r.status >= 400) console.log('HTTP', r.status, r.url.slice(-120));
    }
  });

  await S('Page.navigate', { url: URL });
  const t0 = Date.now();
  const checkpoints = [5, 10, 15, 25, 35, 45];
  let i = 0;
  while (Date.now() - t0 < WAIT) {
    await sleep(1000);
    const secs = Math.round((Date.now() - t0) / 1000);
    if (i < checkpoints.length && secs >= checkpoints[i]) {
      i++;
      try {
        const r = await S('Runtime.evaluate', {
          expression: `(function(){try{var rt=window.xfruntime;return JSON.stringify({t:1,layout:rt&&rt.running_layout&&rt.running_layout.name,isXfLoading:rt&&rt.isXfLoading,progress:rt&&Math.round(rt.progress||0),layoutFlag:rt&&rt.layoutFlag,canvas:!!(rt&&rt.canvas),splash:rt&&rt.isSplashing});}catch(e){return 'ERR '+e.message}})()`,
          returnByValue: true
        });
        console.log(`[${secs}s]`, r.result.value);
        const shot = await S('Page.captureScreenshot', { format: 'png' });
        fs.writeFileSync(`/workspace/work/shot_${secs}.png`, Buffer.from(shot.data, 'base64'));
      } catch (e) { console.log(`[${secs}s] eval err`, e.message); }
    }
  }
  try { await S('Page.captureScreenshot', { format: 'png' }).then(s => fs.writeFileSync('/workspace/work/shot_final.png', Buffer.from(s.data, 'base64'))); } catch (e) {}
  proc.kill();
  process.exit(0);
})().catch(e => { console.error(e); proc.kill(); process.exit(1); });
