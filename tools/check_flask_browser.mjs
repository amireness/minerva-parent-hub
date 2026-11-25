// Optional local browser smoke check: Node 22+, Chrome, and the Python venv.
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
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
const env = { ...process.env, SECRET_KEY: randomBytes(32).toString('hex'), DATABASE_URL: 'sqlite:///' + path.join(out, 'smoke.sqlite').replaceAll('\\', '/') };
const server = spawn(python, ['-c', 'from parenthub import create_app; from parenthub.extensions import db; from parenthub.commands import seed_content; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); seed_content(); app.run(host="127.0.0.1",port=' + port + ',use_reloader=False)'], {
  cwd: root, env,
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
    await waitFor(`location.pathname + location.search === ${JSON.stringify(pathname)} && document.readyState === 'complete'`);
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
        assert.ok(await evaluate(`document.querySelector('.help-nav')?.textContent.trim() === 'Help'`), 'Help remains visible and labeled');
        if (page === '/') assert.equal(await evaluate(`document.querySelector('.landing-intro .button').getAttribute('href')`), '/guide');
        if (name === 'aid-step') {
          const active = width >= 850 ? '.workspace-sidebar' : '.workspace-mobile';
          assert.ok(await evaluate(`document.querySelector('${active}').getBoundingClientRect().width > 0`));
        }
        if (name === 'aid-step' && width === 375) {
          assert.ok(await evaluate(`new Set([...document.querySelectorAll('.primary-nav > a')].map(link => link.offsetTop)).size === 1`), 'Parent navigation stays on one row at 375px');
        }
        if (page === '/dashboard' && width === 375 && name !== 'invitation-required') {
          assert.ok(await evaluate(`document.querySelector('#next-action').getBoundingClientRect().bottom <= innerHeight`), 'Home action is visible at 375px');
        }
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
  const admissionsTopics = ['understand', 'student', 'school', 'parent', 'documents', 'next'];
  for (const topic of admissionsTopics) {
    await responsive('/guide?topic=' + topic, 'admissions-' + topic);
  }
  for (const width of [375, 1280]) {
    await cdp('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
    await navigate('/guide');
    for (const [index, topic] of admissionsTopics.entries()) {
      await waitFor(`document.readyState === 'complete' && document.querySelector('#admissions-${topic}')`);
      assert.equal(await evaluate(`document.querySelectorAll('main h1').length`), 1);
      if (index < admissionsTopics.length - 1) {
        await evaluate(`document.querySelector('#admissions-${topic} .button').focus()`);
        await key('Enter', 13);
      }
    }
    await evaluate(`document.querySelector('#admissions-next .actions a').click()`);
    await waitFor(`document.querySelector('#admissions-documents')`);
  }
  const learningTopics = ['understand', 'process', 'role', 'forms', 'offer'];
  for (const topic of learningTopics) {
    await responsive('/financial-aid?view=learn&topic=' + topic, 'aid-learn-' + topic);
  }
  for (const width of [375, 1280]) {
    await cdp('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
    await navigate('/');
    await evaluate(`document.querySelector('.primary-nav a[href="/financial-aid"]').focus()`);
    await key('Enter', 13);
    await waitFor(`location.pathname === '/financial-aid' && !location.search && document.querySelector('#learn-understand')`);
    if (width === 375) {
      await evaluate(`document.querySelector('.workspace-mobile > summary').focus()`);
      await key('Enter', 13);
      await waitFor(`document.querySelector('.workspace-mobile').open`);
      await key('Enter', 13);
      await waitFor(`!document.querySelector('.workspace-mobile').open`);
      assert.ok(await evaluate(`document.querySelector('#learn-understand .button').getBoundingClientRect().bottom <= innerHeight`));
    }
    for (const topic of learningTopics) {
      await waitFor(`document.readyState === 'complete' && document.querySelector('#learn-${topic}')`);
      assert.equal(await evaluate(`document.querySelectorAll('main h1').length`), 1);
      assert.ok(await evaluate(`document.querySelector('[aria-current="step"][href$="topic=${topic}"]')`));
      if (topic === 'process') {
        assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('#learn-process li h2'), h => h.textContent.trim())`),
          ['1. Apply', '2. Review', '3. Assess', '4. Receive a decision']);
        assert.equal(await evaluate(`getComputedStyle(document.querySelector('#learn-process li')).listStyleType`), 'none');
      }
      if (topic === 'forms') {
        assert.ok(await evaluate(`document.querySelector('.aid-resource[target="_blank"][rel="noopener noreferrer"]').href === 'https://www.minerva.edu/undergraduate/financial-aid/'`));
      }
      await evaluate(`document.querySelector('#learn-${topic} .button').click()`);
    }
    await waitFor(`document.querySelector('.aid-tool-list')`);
    const topicNavigator = width === 375 ? '.workspace-mobile' : '.workspace-sidebar';
    if (width === 375) {
      await evaluate(`document.querySelector('.workspace-mobile > summary').focus()`);
      await key('Enter', 13);
      await waitFor(`document.querySelector('.workspace-mobile').open`);
    }
    assert.ok(await evaluate(`document.querySelector('${topicNavigator} [aria-current="step"][href$="view=tools"]').getClientRects().length`));
    await evaluate(`document.querySelector('${topicNavigator} a[href$="topic=understand"]').focus()`);
    await key('Enter', 13);
    await waitFor(`document.querySelector('#learn-understand') && location.search.includes('topic=understand')`);
    await evaluate(`history.back()`);
    await waitFor(`location.search.includes('view=tools') && document.querySelector('.aid-tool-list')`);
    await evaluate(`history.forward()`);
    await waitFor(`location.search.includes('topic=understand') && document.querySelector('#learn-understand')`);
  }
  await navigate('/auth/register');
  const password = randomBytes(18).toString('hex');
  await submit({ email: 'browser@example.com', password, confirm: password }, '/auth/login');
  await submit({ email: 'browser@example.com', password }, '/dashboard');
  await waitFor(`document.querySelector('h1').textContent === 'Invitation required'`);
  await responsive('/dashboard', 'invitation-required');
  const seed = spawnSync(python, ['-m', 'flask', '--app', 'parenthub', '--debug', 'seed-invitations',
    '--email', 'browser@example.com'], { cwd: root, env, encoding: 'utf8', windowsHide: true });
  assert.equal(seed.status, 0, seed.stderr);
  const code = seed.stdout.match(/invitation code: ([\w-]+)/)?.[1];
  assert.ok(code, 'The synthetic seed produced an invitation code');
  await submit({ code }, '/dashboard');
  await waitFor(`document.querySelector('[aria-current="step"]')?.innerText.includes('Application started') && document.body.innerText.includes('Application submitted')`);
  await navigate('/application-progress');
  await evaluate(`document.querySelector('.journey-steps li:nth-child(2) summary').focus()`);
  await key('Enter', 13);
  await waitFor(`document.querySelector('.journey-steps li:nth-child(2) details').open`);
  await navigate('/help');
  assert.ok(await evaluate(`document.querySelector('a[href="mailto:admissions@minerva.edu"]') && document.querySelector('.help-nav[aria-current="page"]')`));
  await navigate('/financial-aid?view=documents');
  await evaluate(`document.querySelector('#income-tax summary').focus()`);
  await key('Enter', 13);
  await waitFor(`document.body.innerText.includes('past two years')`);
  await evaluate(`document.querySelector('#income-tax .aid-file-actions a').click()`);
  await waitFor(`document.readyState === 'complete' && document.querySelector('#income-tax .aid-link-form') !== null`);
  await evaluate(`document.querySelector('#income-tax input[type="radio"]').click()`);
  await submit({}, '/financial-aid', '#income-tax .aid-link-form');
  await waitFor(`document.body.innerText.includes('1 of 4 documents added') && document.body.innerText.includes('Tax-record-example-1.pdf')`);
  await submit({}, '/financial-aid', '#income-tax form[action$="/share"]');
  await waitFor(`document.querySelector('#income-tax').innerText.includes('Shared with student')`);
  await evaluate(`document.querySelector('.primary-nav a[href="/financial-aid"]').click()`);
  await waitFor(`!location.search && document.querySelector('#learn-understand')`);
  await responsive('/financial-aid', 'aid-start');
  assert.ok(await evaluate(`document.querySelector('#learn-understand h1').textContent === 'What is financial aid?' && !document.querySelector('#demo-amount')`));
  await evaluate(`document.querySelector('.workspace-mobile > summary').focus()`);
  await key('Enter', 13);
  await waitFor(`document.querySelector('.workspace-mobile').open`);
  await evaluate(`document.querySelector('.workspace-mobile a[href*="view=tools"]').focus()`);
  await key('Enter', 13);
  await waitFor(`document.querySelector('.aid-tool-list')`);
  assert.equal(await evaluate(`document.querySelectorAll('.aid-tool-list a').length`), 4);
  await evaluate(`document.querySelector('.aid-tool-list a[href*="view=glossary"]').focus()`);
  await key('Enter', 13);
  await waitFor(`document.readyState === 'complete' && document.querySelector('#term-search-controls:not([hidden])')`);
  await evaluate(`(() => { const input = document.querySelector('#term-search'); input.value = 'current account'; input.dispatchEvent(new Event('input')); })()`);
  assert.equal(await evaluate(`document.querySelectorAll('.aid-term:not([hidden])').length`), 1);
  await evaluate(`document.querySelector('.aid-back').click()`);
  await waitFor(`document.querySelector('.aid-tool-list')`);
  await navigate('/financial-aid?view=translations');
  assert.ok(await evaluate(`document.querySelector('#translations').innerText.includes('Illustrative English translation')`));
  await navigate('/financial-aid?view=currency');
  await waitFor(`document.querySelector('#demo-converter:not([hidden])')`);
  await evaluate(`document.querySelector('#demo-amount').value = '90'; document.querySelector('#demo-convert').click()`);
  assert.ok(await evaluate(`document.querySelector('#demo-result').textContent.includes('100.00 USD')`));
  await evaluate(`document.querySelector('#demo-amount').value = '-1'; document.querySelector('#demo-convert').click()`);
  assert.equal(await evaluate(`document.querySelector('#demo-amount').getAttribute('aria-invalid')`), 'true');
  await navigate('/account');
  assert.ok(await evaluate(`document.querySelector('input[name="code"]') !== null`));
  await navigate('/planning');
  await submit({ age_group: 'under18' }, '/planning');
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
  await waitFor(`document.body.innerText.includes('Application started')`);
  assert.ok(await evaluate(`document.body.innerText.includes('Review linked documents')`));
  await navigate('/planning');
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
    if (await evaluate(`document.activeElement.matches('.primary-nav a[href="/planning"]')`)) break;
  }
  assert.ok(await evaluate(`document.activeElement.matches('.primary-nav a[href="/planning"]') && getComputedStyle(document.activeElement).outlineStyle !== 'none'`), 'Planning has a visible keyboard focus indicator');
  await key('Enter', 13);
  await waitFor(`document.querySelector('.primary-nav a[href="/planning"][aria-current="page"]')`);
  await cdp('Emulation.setDeviceMetricsOverride', { width: 375, height: 900, deviceScaleFactor: 1, mobile: false });
  await navigate('/guide');
  await evaluate(`document.querySelector('.workspace-mobile > summary').focus()`);
  await key('Enter', 13);
  await waitFor(`document.querySelector('.workspace-mobile').open`);
  await evaluate(`document.querySelector('.workspace-mobile a[href$="topic=parent"]').focus()`);
  await key('Enter', 13);
  await waitFor(`document.querySelector('#admissions-parent')`);
  await evaluate(`location.href = '/guide?legacy=1#planning'`);
  await waitFor(`location.pathname === '/deadlines' && document.readyState === 'complete'`);

  const pages = ['/dashboard', '/application-progress', '/planning', '/account', '/guide', '/financial-aid', '/checklist', '/reminders', '/questions', '/resources', '/deadlines', '/help', '/reminders/new'];
  for (const page of pages) await responsive(page);
  await responsive('/financial-aid?category=earnings', 'add-document');
  for (const [name, query] of [
    ['aid-useful-tools', 'view=tools'],
    ['aid-glossary', 'view=glossary&term=income'], ['aid-translations', 'view=translations'],
    ['aid-currency', 'view=currency'], ['aid-documents', 'view=documents'],
  ]) await responsive('/financial-aid?' + query, name);
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
  await navigate('/planning');
  assert.ok(await evaluate(`document.body.innerText.includes('0 of 5')`));
  await navigate('/financial-aid?view=documents');
  await evaluate(`document.querySelector('#bank summary').click()`);
  assert.ok(await evaluate(`document.body.innerText.includes('most recent twelve months')`));
  await cdp('Emulation.setScriptExecutionDisabled', { value: false });
  scriptsEnabled = true;
  const number = seed.stdout.match(/(SYN-[A-F0-9]+) invitation code:/)?.[1];
  assert.ok(number);
  const student = spawnSync(python, ['-m', 'flask', '--app', 'parenthub', '--debug', 'seed-student',
    '--email', 'student@example.com', '--application-number', number],
    { cwd: root, env, encoding: 'utf8', windowsHide: true });
  assert.equal(student.status, 0, student.stderr);
  const studentPassword = student.stdout.match(/shown once\): (\S+)/)?.[1];
  assert.ok(studentPassword);
  await evaluate(`document.querySelector('.inline-form').requestSubmit()`);
  await waitFor(`location.pathname === '/guide' && document.readyState === 'complete'`);
  await navigate('/auth/login');
  await submit({ email: 'student@example.com', password: studentPassword }, '/student/preparation');
  assert.ok(await evaluate(`document.body.innerText.includes('Income and tax records') && document.body.innerText.includes('Example document added') && !document.body.innerText.includes('Bank statements')`));
  await evaluate(`document.querySelector('#student-visibility summary').click(); document.querySelector('#student-visibility input').click()`);
  assert.ok(await evaluate(`document.querySelector('#student-visibility output').textContent.includes('application milestones')`));
  await navigate('/student/preparation');
  assert.equal(await evaluate(`document.querySelectorAll('#student-visibility input:checked').length`), 0);
  await responsive('/student/preparation');
  console.log(`PASS: browser registration, invitations, Admissions and aid learning journeys, Useful Tools, demo document sharing, keyboard and offline flows; ${pages.length + 24} page states × 2 themes × 10 widths. Screenshots: ${out}`);
} finally {
  socket?.close();
  chrome?.kill();
  server.kill();
}
