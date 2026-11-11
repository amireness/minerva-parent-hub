import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { contrast } from './design_tokens.mjs';

const source = JSON.parse(readFileSync(new URL('../design-tokens.json', import.meta.url), 'utf8'));
const palette = { ...source.color.brand, ...source.color.semantic, ...source.flask.brand };
const kebab = name => name.replace(/[A-Z]/g, letter => '-' + letter.toLowerCase());
const variables = mode => Object.entries(palette).map(([name, value]) => `  --color-${kebab(name)}: ${value[mode]};`);
const dark = variables('dark');
let checked = 0;
const css = [
  '/* Generated from design-tokens.json by tools/flask_design_tokens.mjs. */',
  ':root {', '  color-scheme: light;', ...variables('light'),
  `  --font-display: ${source.flask.displayFont};`,
  `  --type-page-title-size: ${source.flask.pageTitleSize};`,
  `  --type-section-header-size: ${source.flask.sectionHeaderSize};`, '}',
  '@media (prefers-color-scheme: dark) {', '  :root:not([data-theme="light"]) {',
  '  color-scheme: dark;', ...dark, '  }', '}',
  'html[data-theme="dark"] {', '  color-scheme: dark;', ...dark, '}', '',
].join('\n');
for (const mode of ['light', 'dark']) {
  for (const [foreground, background, minimum] of [
    ['text', 'background', 4.5], ['text', 'surface', 4.5], ['textMuted', 'background', 4.5],
    ['textMuted', 'surface', 4.5], ['primary', 'surface', 4.5], ['primary', 'background', 4.5],
    ['onPrimary', 'primary', 4.5], ['gold', 'goldSurface', 4.5], ['gold', 'surface', 4.5],
    ['controlBorder', 'surface', 3], ['success', 'surface', 4.5], ['error', 'surface', 4.5],
    ['text', 'goldSurface', 4.5], ['primary', 'goldSurface', 4.5], ['textMuted', 'surfaceAlt', 4.5],
    ['text', 'surfaceAlt', 4.5], ['textMuted', 'goldSurface', 4.5], ['gold', 'background', 4.5],
    ['warning', 'surfaceAlt', 4.5],
  ]) {
    const ratio = contrast(palette[foreground][mode], palette[background][mode]);
    if (ratio < minimum) throw new Error(`${mode} ${foreground}/${background}: ${ratio.toFixed(2)} below ${minimum}`);
    checked++;
  }
}
const target = fileURLToPath(new URL('../parenthub/static/tokens.css', import.meta.url));
if (process.argv.includes('--check')) {
  if (readFileSync(target, 'utf8').replaceAll('\r\n', '\n') !== css) throw new Error('Flask tokens drifted; run node tools/flask_design_tokens.mjs');
} else {
  writeFileSync(target, css);
}
console.log(`PASS: Flask tokens match; ${checked} text/control contrast pairs meet AA in light and dark.`);
