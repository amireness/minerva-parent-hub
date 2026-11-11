// Optional local browser smoke check: Node 22+, Chrome, and the Python venv.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const out = path.join(root, 'build', 'qa', `flask-${Date.now()}`);
fs.mkdirSync(out, { recursive: true });
const python = process.env.PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const chromePath = process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = Number(process.env.FLASK_TEST_PORT || 5087);
const debugPort = Number(process.env.CHROME_TEST_PORT || 9387);
const origin = `http://127.0.0.1:${port}`;
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
for (const url of [origin, `http://127.0.0.1:${debugPort}/json/version`]) {
  let occupied = false;
  try { await fetch(url, { signal: AbortSignal.timeout(500) }); occupied = true; } catch {}
  assert.ok(!occupied, `Port already occupied: ${url}`);
}
const server = spawn(python, ['-c', 'from parenthub import create_app; from parenthub.extensions import db; from parenthub.commands import seed_content; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); seed_content(); app.run(host="127.0.0.1",port=' + port + ',use_reloader=False)'], {
  cwd: root, env: { ...process.env, SECRET_KEY: randomBytes(32).toString('hex'), DATABASE_URL: 'sqlite:///' + path.join(out, 'smoke.sqlite').replaceAll('\\', '/') },
  stdio: 'ignore', windowsHide: true,
});
let chrome, socket;
try {
  let ready = false;
  for (let i = 0; i < 60; i++) {
    try { ready = (await fetch(origin + '/guide')).ok; } catch {}
    if (ready) break;
    await pause(200);
  }
  assert.ok(ready, 'Flask did not start');
  chrome = spawn(chromePath, ['--headless=new', '--no-first-run', '--no-default-browser-check',
    `--remote-debugging-port=${debugPort}`, `--user-data-dir=${path.join(out, 'browser-profile')}`, 'about:blank'],
    { stdio: 'ignore', windowsHide: true });
  let target;
  for (let i = 0; i < 60; i++) {
    try { target = (await fetch(`http://127.0.0.1:${debugPort}/json/list`).then(r => r.json())).find(t => t.type === 'page'); } catch {}
    if (target) break;
    await pause(200);
  }
  assert.ok(target, 'Chrome did not start');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  let sequence = 0;
  const pending = new Map();
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (pending.has(message.id)) {
      const { resolve, reject, timer } = pending.get(message.id);
      clearTimeout(timer);
      pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    }
  };
  const cdp = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => reject(new Error(`Timeout: ${method}`)), 10000);
    pending.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const result = await cdp('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    assert.ok(!result.exceptionDetails, JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  const waitFor = async expression => {
    for (let i = 0; i < 80; i++) {
      if (await evaluate(expression)) return;
      await pause(50);
    }
    assert.fail(`Browser condition timed out: ${expression}`);
  };
  const navigate = async pathname => {
    await cdp('Page.navigate', { url: origin + pathname });
    await waitFor(`location.pathname === ${JSON.stringify(pathname)} && document.readyState === 'complete'`);
  };
  let scriptsEnabled = true;
  const submit = async (values, destination, selector = 'form[method="post"]:not(.inline-form)') => {
    const busy = await evaluate(`(() => { const form = document.querySelector(${JSON.stringify(selector)});
      for (const [name, value] of Object.entries(${JSON.stringify(values)})) {
        const field = form.elements.namedItem(name);
        if (field.type === 'checkbox') field.checked = value; else field.value = value;
      } window.__formSubmitting = true; form.requestSubmit();
      return form.getAttribute('aria-busy') === 'true' && form.querySelector('button[type="submit"]').disabled; })()`);
    if (scriptsEnabled) assert.ok(busy, 'Submission shows busy feedback and prevents repeat clicks');
    await waitFor(`!window.__formSubmitting && location.pathname === ${JSON.stringify(destination)} && document.readyState === 'complete'`);
  };
  await cdp('Page.enable');
  await cdp('Runtime.enable');
  await cdp('Emulation.setDeviceMetricsOverride', { width: 375, height: 900, deviceScaleFactor: 1, mobile: false });
  const responsive = async (page, name = page.slice(1).replaceAll('/', '-') || 'home') => {
    await navigate(page);
    assert.equal(await evaluate(`document.querySelectorAll('h1').length`), 1, `${page} needs one page heading`);
    for (const scheme of ['light', 'dark']) {
      await cdp('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: scheme }] });
      for (const width of [375, 640, 800, 1280, 1600, 900, 768, 480, 320, 375]) {
        await cdp('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
        const overflow = await evaluate(`({width:innerWidth, document:document.documentElement.scrollWidth, main:document.querySelector('main').scrollWidth, client:document.querySelector('main').clientWidth})`);
        assert.ok(overflow.document <= width && overflow.main <= overflow.client, `${page} ${scheme} ${width}: ${JSON.stringify(overflow)}`);
        const menuFits = await evaluate(`(() => { const menu = document.querySelector('.nav-disclosure'); if (!menu) return true; menu.open = true; const rect = menu.querySelector('.nav-dropdown').getBoundingClientRect(); const fits = rect.left >= 0 && rect.right <= innerWidth; menu.open = false; return fits; })()`);
        assert.ok(menuFits, `${page} ${scheme} ${width}: expanded Explore menu leaves viewport`);
        if (page === '/') assert.ok(await evaluate(`Array.from(document.querySelectorAll('.journey-list li > span')).every(span => span.getBoundingClientRect().height <= parseFloat(getComputedStyle(span).lineHeight) + 1)`), 'Journey step numbers stay on one line');
        if (width === 375 || width === 1280) {
          const png = await cdp('Page.captureScreenshot', { format: 'png' });
          fs.writeFileSync(path.join(out, `${name}-${scheme}-${width}.png`), Buffer.from(png.data, 'base64'));
        }
      }
    }
  };
  for (const page of ['/', '/auth/login', '/auth/register']) await responsive(page);
  await navigate('/');
  const key = async (name, code, modifiers = 0) => {
    const keyCode = name === 'Tab' ? 'Tab' : 'Enter';
    await cdp('Input.dispatchKeyEvent', { type: 'keyDown', key: name, code: keyCode, windowsVirtualKeyCode: code, modifiers,
      ...(name === 'Enter' ? { text: '\r', unmodifiedText: '\r' } : {}) });
    await cdp('Input.dispatchKeyEvent', { type: 'keyUp', key: name, code: keyCode, windowsVirtualKeyCode: code, modifiers });
  };
  await key('Tab', 9);
  assert.ok(await evaluate(`document.activeElement.classList.contains('skip-link')`), 'Skip link is first keyboard stop');
  await key('Enter', 13);
  assert.ok(await evaluate(`document.activeElement.id === 'main-content'`), 'Skip link reaches main');
  await navigate('/auth/register');
  const password = randomBytes(18).toString('hex');
  await submit({ email: 'browser@example.com', password, confirm: password }, '/auth/login');
  await submit({ email: 'browser@example.com', password }, '/dashboard');
  await submit({ age_group: 'under18' }, '/dashboard');
  await waitFor(`document.body.innerText.includes('Published requirement')`);
  await navigate('/checklist');
  await submit({ completed: true }, '/checklist');
  await navigate('/reminders/new');
  await submit({ title: 'Browser reminder', due_date: '2027-01-04' }, '/reminders');
  await navigate('/reminders/1/edit');
  await submit({ title: 'Edited browser reminder', due_date: '2027-01-05' }, '/reminders');
  await navigate('/questions/new');
  await submit({ body: 'Which parent steps apply?' }, '/questions');
  await navigate('/questions/1/edit');
  await submit({ body: 'Which parent permissions apply?', resolved: true }, '/questions');
  await evaluate(`document.querySelector('.inline-form').requestSubmit()`);
  await waitFor(`location.pathname === '/guide' && document.readyState === 'complete'`);
  await navigate('/auth/login');
  await submit({ email: 'browser@example.com', password }, '/dashboard');
  await waitFor(`document.body.innerText.includes('Edited browser reminder') && document.body.innerText.includes('1 of 5')`);

  await navigate('/reminders/new');
  await submit({ title: 'Remove this reminder', due_date: '2027-02-01' }, '/reminders');
  await submit({}, '/reminders', 'form[action="/reminders/2/delete"]');
  assert.ok(await evaluate(`!document.body.innerText.includes('Remove this reminder') && document.body.innerText.includes('Reminder deleted.')`));
  await navigate('/questions/new');
  await submit({ body: 'Remove this question' }, '/questions');
  await submit({}, '/questions', 'form[action="/questions/2/delete"]');
  assert.ok(await evaluate(`!document.body.innerText.includes('Remove this question')`));
  await navigate('/resources');
  await evaluate(`(() => { const form = document.querySelector('form[method="get"]'); form.elements.q.value = 'discussion'; form.requestSubmit(); })()`);
  await waitFor(`location.search.includes('q=discussion') && document.readyState === 'complete'`);
  assert.ok(await evaluate(`document.querySelectorAll('.resource-card').length === 1 && document.body.innerText.includes("academic model")`));
  assert.equal(await evaluate(`document.querySelector('.resource-card h2 a').href`), 'https://www.minerva.edu/academics/');
  await navigate('/dashboard');
  for (let i = 0; i < 15; i++) {
    await key('Tab', 9);
    if (await evaluate(`document.activeElement.tagName === 'SUMMARY'`)) break;
  }
  assert.ok(await evaluate(`document.activeElement.tagName === 'SUMMARY' && getComputedStyle(document.activeElement).outlineStyle !== 'none'`), 'Explore has keyboard focus indicator');
  await key('Enter', 13);
  await waitFor(`document.querySelector('.nav-disclosure').open`);
  await key('Tab', 9);
  assert.equal(await evaluate(`document.activeElement.textContent`), 'Parent guidance');
  await key('Tab', 9, 8);
  await key('Enter', 13);
  await waitFor(`!document.querySelector('.nav-disclosure').open`);

  const pages = ['/dashboard', '/guide', '/financial-aid', '/checklist', '/reminders', '/questions', '/resources', '/deadlines', '/reminders/new'];
  for (const page of pages) await responsive(page);
  await navigate('/dashboard');
  await cdp('Network.enable');
  await cdp('Network.emulateNetworkConditions', { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 });
  await waitFor(`!document.getElementById('offline-notice').hidden`);
  assert.ok(await evaluate(`Array.from(document.querySelectorAll('form[method="post"] button')).every(b => b.disabled)`));
  await cdp('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  await cdp('Emulation.setScriptExecutionDisabled', { value: true });
  scriptsEnabled = false;
  await navigate('/checklist');
  assert.ok(await evaluate(`document.querySelectorAll('input[type="checkbox"]').length === 5`));
  await submit({ completed: false }, '/checklist');
  await navigate('/dashboard');
  assert.ok(await evaluate(`document.body.innerText.includes('0 of 5')`));
  console.log(`PASS: browser register/login, saved age/checklist/reminder/question, logout/login persistence; reminder/question deletion, resource search/source link, keyboard skip/menu/focus, busy feedback; ${pages.length + 3} pages × 2 themes × 10 widths; offline notice/disabled writes; no-JavaScript checklist update. Screenshots: ${out}`);
} finally {
  socket?.close();
  chrome?.kill();
  server.kill();
}
