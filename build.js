'use strict';

/* 把 markdown-it 内联进模板，产出单文件 MD Reader.html */

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const tpl = fs.readFileSync(path.join(ROOT, 'src', 'template.html'), 'utf8');

const candidates = [
  path.join(ROOT, 'node_modules', 'markdown-it', 'dist', 'markdown-it.min.js'),
  path.join(ROOT, '..', 'md-to-desktop', 'node_modules', 'markdown-it', 'dist', 'markdown-it.min.js')
];
const mditPath = candidates.find((p) => fs.existsSync(p));
if (!mditPath) throw new Error('找不到 markdown-it.min.js，先跑 npm install');

const mdit = fs.readFileSync(mditPath, 'utf8');
if (mdit.indexOf('</script') >= 0) throw new Error('markdown-it 里含 </script，不能直接内联');

// favicon：32×32 PNG 内联成 base64
const favPath = path.join(ROOT, 'assets', 'favicon-32.png');
const fav = fs.existsSync(favPath) ? fs.readFileSync(favPath).toString('base64') : '';

const out = tpl
  .replace('/*__MARKDOWN_IT__*/', () => mdit)
  .replace('__FAVICON__', () => fav);

const dist = path.join(ROOT, 'dist');
fs.mkdirSync(dist, { recursive: true });
const outFile = path.join(dist, 'MD Reader.html');
fs.writeFileSync(outFile, out, 'utf8');

const kb = (Buffer.byteLength(out, 'utf8') / 1024).toFixed(1);
console.log('生成 ' + outFile);
console.log('大小 ' + kb + ' KB（其中 markdown-it ' + (Buffer.byteLength(mdit, 'utf8') / 1024).toFixed(1) + ' KB）');
