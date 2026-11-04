import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const html = readFileSync(new URL('index.html', root), 'utf8');
const manifest = JSON.parse(readFileSync(new URL('manifest.json', root), 'utf8'));
const prefix = new URL('https://amireness.github.io/minerva-parent-hub/');
function checkLocal(value) {
  const resolved = new URL(value, prefix);
  assert.equal(resolved.origin, prefix.origin);
  assert.ok(resolved.pathname.startsWith(prefix.pathname), `${value} escapes the project path`);
  const relative = resolved.pathname.slice(prefix.pathname.length);
  assert.ok(existsSync(fileURLToPath(new URL(relative, root))), `${value} is missing`);
}
let resources = 0;
for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
  const value = match[1];
  if (value.startsWith('#') || value.startsWith('mailto:')) continue;
  if (value.startsWith('https:')) {
    assert.equal(new URL(value).hostname, 'www.minerva.edu');
    continue;
  }
  checkLocal(value);
  resources++;
}
assert.ok(resources >= 5);
assert.equal(new URL(manifest.start_url, prefix).href, prefix.href);
assert.equal(new URL(manifest.scope, prefix).href, prefix.href);
assert.throws(() => checkLocal('/css/styles.css'), /escapes the project path/);
console.log(`PASS: ${resources} local resources, official links and manifest stay within /minerva-parent-hub/; root-path negative control fails as expected`);
